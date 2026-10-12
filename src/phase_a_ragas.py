from __future__ import annotations

"""Phase A: RAGAS Production Evaluation — 50q, 3 distributions, cluster analysis."""

import json
import math
import os
import re
import sys
from dataclasses import asdict, dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TEST_SET_PATH, ANSWERS_PATH, ARTIFACTS_DIR
from src.experiment_support import write_json

Distribution = str  # "factual" | "multi_hop" | "adversarial"
METRICS = ("faithfulness", "answer_relevancy", "context_precision", "context_recall")

DIAGNOSTIC_TREE = {
    "faithfulness":      ("LLM hallucinating", "Tighten system prompt, lower temperature"),
    "context_recall":    ("Missing relevant chunks", "Improve chunking or add BM25"),
    "context_precision": ("Too many irrelevant chunks", "Add reranking or metadata filter"),
    "answer_relevancy":  ("Answer doesn't match question", "Improve prompt template"),
}


@dataclass
class RagasResult:
    question_id: int
    distribution: Distribution
    question: str
    answer: str
    contexts: list[str]
    ground_truth: str
    faithfulness: float
    answer_relevancy: float
    context_precision: float
    context_recall: float

    @property
    def avg_score(self) -> float:
        return (self.faithfulness + self.answer_relevancy +
                self.context_precision + self.context_recall) / 4

    @property
    def worst_metric(self) -> str:
        scores = {
            "faithfulness":      self.faithfulness,
            "answer_relevancy":  self.answer_relevancy,
            "context_precision": self.context_precision,
            "context_recall":    self.context_recall,
        }
        return min(scores, key=scores.get)


# ─── Đã implement sẵn ────────────────────────────────────────────────────────

@dataclass
class RagasEvaluation:
    """Task 2 output: measured rows plus model identifiers reported by m4."""
    results: list[RagasResult]
    evaluator_models: list[str]

def load_test_set_50q(path: str = TEST_SET_PATH) -> list[dict]:
    """Load 50q test set với 3 distributions."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_answers(path: str = ANSWERS_PATH) -> list[dict]:
    """Load pre-generated answers từ setup_answers.py."""
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"answers_50q.json không tìm thấy tại {path}\n"
            "→ Chạy trước: python scripts/setup_answers.py --live"
        )
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_phase_a_report(results: list[RagasResult], clusters: dict, bottom: list[dict]) -> dict:
    """Provided exporter: preserve the student-produced Task 3 rows verbatim."""
    per_dist: dict[str, dict] = {}
    for dist in ["factual", "multi_hop", "adversarial"]:
        subset = [r for r in results if r.distribution == dist]
        if subset:
            per_dist[dist] = {
                "count": len(subset),
                "faithfulness":      sum(r.faithfulness for r in subset) / len(subset),
                "answer_relevancy":  sum(r.answer_relevancy for r in subset) / len(subset),
                "context_precision": sum(r.context_precision for r in subset) / len(subset),
                "context_recall":    sum(r.context_recall for r in subset) / len(subset),
                "avg_score":         sum(r.avg_score for r in subset) / len(subset),
            }

    report = {
        "total_questions": len(results),
        "per_question": [asdict(r) for r in results],
        "per_distribution": per_dist,
        "failure_clusters": clusters,
        "bottom_10": bottom,
    }
    return report


def save_phase_a_report(results: list[RagasResult], clusters: dict, bottom: list[dict],
                        path: str = os.path.join(ARTIFACTS_DIR, "ragas_50q.json")) -> None:
    write_json(path, build_phase_a_report(results, clusters, bottom))



# ─── Tasks 1-4: Sinh viên implement ──────────────────────────────────────────

def group_by_distribution(test_set: list[dict]) -> dict[str, list[dict]]:
    """Task 1: Nhóm 50 câu hỏi theo 3 distributions.

    Returns:
        {"factual": [...], "multi_hop": [...], "adversarial": [...]}
    """
    groups = {"factual": [], "multi_hop": [], "adversarial": []}
    for item in test_set:
        distribution = item["distribution"]
        if distribution not in groups:
            raise ValueError(f"Question {item.get('id')}: unknown distribution {distribution!r}")
        groups[distribution].append(item)
    return groups


def run_ragas_50q(answers: list[dict]) -> RagasEvaluation:
    """Task 2: Chạy RAGAS 4 metrics trên toàn bộ 50 câu hỏi.

    Gợi ý — import từ Day 18 của bạn:
        from src.m4_eval import evaluate_ragas

    Steps:
        1. Extract questions, answers, contexts, ground_truths từ answers list
        2. Gọi evaluate_ragas() từ m4_eval.py
        3. Kết hợp kết quả với distribution info từ answers list
        4. Return RagasEvaluation(results, raw["metadata"]["evaluator_models"])
           m4 must report its actual LLM/embedding models; never guess JUDGE_MODEL.
    """
    # Import trong hàm để dùng đúng m4 hiện tại (tests thay sys.modules["src.m4_eval"]).
    try:
        from src.m4_eval import evaluate_ragas
    except ImportError as error:
        raise ValueError("Missing src/m4_eval.py; cannot run RAGAS or declare evaluator models") from error

    raw = evaluate_ragas(
        [a["question"] for a in answers],
        [a["answer"] for a in answers],
        [a["contexts"] for a in answers],
        [a["ground_truth"] for a in answers],
    )
    per_question = raw.get("per_question", [])
    if len(per_question) != len(answers):
        raise ValueError(f"m4 returned {len(per_question)} rows for {len(answers)} answers; "
                         "RAGAS did not evaluate every question.")
    evaluator_models = raw.get("metadata", {}).get("evaluator_models")
    if not evaluator_models:
        raise ValueError("m4 must report metadata.evaluator_models; never substitute JUDGE_MODEL.")

    results = []
    for a, pq in zip(answers, per_question):
        reported_question = getattr(pq, "question", None)
        if reported_question is not None and reported_question != a["question"]:
            raise ValueError(f"Question {a['id']}: m4 rows are not aligned with answers.")
        scores = {}
        for metric in METRICS:
            value = float(getattr(pq, metric))
            if not math.isfinite(value) or not 0 <= value <= 1:
                raise ValueError(f"Question {a['id']}: {metric}={value} is not a finite score in [0, 1].")
            scores[metric] = value
        results.append(RagasResult(
            question_id=a["id"], distribution=a["distribution"],
            question=a["question"], answer=a["answer"],
            contexts=a["contexts"], ground_truth=a["ground_truth"],
            **scores,
        ))
    return RagasEvaluation(results, list(evaluator_models))


def bottom_10(results: list[RagasResult]) -> list[dict]:
    """Task 3: Lấy 10 câu hỏi có avg_score thấp nhất.

    Returns:
        [{"rank": 1, "question_id": ..., "distribution": ...,
          "question": ..., "avg_score": ..., "worst_metric": ...,
          "diagnosis": ..., "suggested_fix": ...}, ...]
    """
    output = []
    for rank, r in enumerate(sorted(results, key=lambda r: r.avg_score)[:10], 1):
        diagnosis, suggested_fix = _diagnose(r)
        output.append({
            "rank": rank,
            "question_id": r.question_id,
            "distribution": r.distribution,
            "question": r.question,
            "avg_score": round(r.avg_score, 4),
            "worst_metric": r.worst_metric,
            "diagnosis": diagnosis,
            "suggested_fix": suggested_fix,
        })
    return output


VERSION_PATTERN = re.compile(r"\bv\d+(\.\d+)?\b|hiện hành|hết hiệu lực|thay thế|phiên bản", re.IGNORECASE)
NEGATION_PATTERN = re.compile(r"^\s*không\b|không được|tuyệt đối không|\bcấm\b", re.IGNORECASE)
ANSWER_NEGATION_PATTERN = re.compile(r"\bkhông\b|\bchưa\b|\bcấm\b", re.IGNORECASE)
NOT_FOUND_PATTERN = re.compile(r"không tìm thấy", re.IGNORECASE)


def _diagnose(r: RagasResult) -> tuple[str, str]:
    """Diagnosis cụ thể cho một câu, suy ra từ điểm, answer và reference của chính câu đó."""
    diagnosis, fix = DIAGNOSTIC_TREE[r.worst_metric]
    worst_value = getattr(r, r.worst_metric)
    signals = [f"{diagnosis} ({r.worst_metric}={worst_value:.2f})"]
    fixes = [fix]
    if NOT_FOUND_PATTERN.search(r.answer):
        signals.append("answer trả 'không tìm thấy' — context lấy về không chứa thông tin cần")
        fixes.append("kiểm tra retrieval cho từ khóa của câu hỏi (BM25/dense, tăng top_k) trước khi sửa prompt")
    if VERSION_PATTERN.search(r.ground_truth):
        signals.append("reference phân biệt phiên bản chính sách — rủi ro dùng bản cũ đã bị thay thế")
        fixes.append("gắn metadata phiên bản/ngày hiệu lực khi chunking, ưu tiên bản hiện hành khi rerank "
                     "và yêu cầu answer nêu phiên bản áp dụng (không xóa tài liệu cũ)")
    if NEGATION_PATTERN.search(r.ground_truth):
        if ANSWER_NEGATION_PATTERN.search(r.answer):
            signals.append("reference có phủ định/điều kiện cấm — cần đối chiếu answer có giữ đúng phủ định")
        else:
            signals.append("reference là phủ định nhưng answer không chứa phủ định nào")
        fixes.append("prompt yêu cầu trả lời rõ Có/Không trước, rồi trích điều kiện từ context")
    if r.distribution == "multi_hop" and r.worst_metric in ("context_recall", "context_precision"):
        signals.append("câu multi-hop cần kết hợp nhiều tài liệu; top-k sau rerank có thể thiếu một nguồn")
        fixes.append("tăng RERANK_TOP_K hoặc trả parent chunk cho câu cần nhiều nguồn")
    return "; ".join(signals), "; ".join(fixes)


def cluster_analysis(results: list[RagasResult]) -> dict:
    """Task 4: Phân tích failure clusters theo (worst_metric × distribution).

    Matrix thống kê worst_metric của mọi câu, không coi mọi câu là một failure.
    Nhóm yếu nhất = distribution có avg_score trung bình thấp nhất (bỏ nhóm rỗng).
    Tổng matrix theo cột chỉ là kích thước nhóm 20/20/10, không đo chất lượng.

    Returns:
        {
          "matrix": {
            "faithfulness":      {"factual": 3, "multi_hop": 5, "adversarial": 2},
            "answer_relevancy":  {...},
            "context_precision": {...},
            "context_recall":    {...},
          },
          "dominant_failure_distribution": "multi_hop",
          "dominant_failure_metric": "context_recall",
          "insight": "..."
        }
    """
    if not results:
        raise ValueError("cluster_analysis needs at least one RAGAS result.")
    distributions = ("factual", "multi_hop", "adversarial")
    matrix = {metric: {d: 0 for d in distributions} for metric in METRICS}
    for r in results:
        matrix[r.worst_metric][r.distribution] += 1

    # Nhóm rỗng bị bỏ khỏi phép chia, không gán 0 chất lượng.
    means = {}
    for d in distributions:
        scores = [r.avg_score for r in results if r.distribution == d]
        if scores:
            means[d] = sum(scores) / len(scores)
    dominant_dist = min(means, key=means.get)  # chất lượng thấp nhất, không phải nhóm đông nhất
    metric_totals = {m: sum(matrix[m].values()) for m in METRICS}
    dominant_metric = max(metric_totals, key=metric_totals.get)

    means_text = ", ".join(f"{d}={value:.4f}" for d, value in means.items())
    insight = (f"Nhóm yếu nhất theo avg_score trung bình là '{dominant_dist}' "
               f"({means[dominant_dist]:.4f}; các nhóm: {means_text}). "
               f"Worst metric phổ biến nhất là '{dominant_metric}' ở "
               f"{metric_totals[dominant_metric]}/{len(results)} câu, trong đó "
               f"{matrix[dominant_metric][dominant_dist]} câu thuộc '{dominant_dist}'. "
               f"Gợi ý: {DIAGNOSTIC_TREE[dominant_metric][1]}.")

    return {"matrix": matrix, "distribution_avg_scores": means,
            "dominant_failure_distribution": dominant_dist,
            "dominant_failure_metric": dominant_metric, "insight": insight}


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from scripts.run_experiments import main
    raise SystemExit(main(["--phase", "a", *sys.argv[1:]]))

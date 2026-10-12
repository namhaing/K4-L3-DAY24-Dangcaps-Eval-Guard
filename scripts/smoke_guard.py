"""Small real-engine checks for Tam; does not write official batch artifacts."""
from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone
import hashlib
from importlib.metadata import PackageNotFoundError, version
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import ADVERSARIAL_SET_PATH, CLEAN_SET_PATH, OPENAI_API_KEY
from src.phase_c_guard import check_input_rail, pii_scan, setup_nemo_rails, setup_presidio


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true', help='Also call NeMo/OpenAI; one input by default')
    parser.add_argument('--nemo-limit', type=int, default=1, help='Maximum input checks (1-15); not an API-call count')
    parser.add_argument('--nemo-start', type=int, default=0, help='Resume at input index to avoid repeating checks')
    parser.add_argument('--output', type=Path, help='Save UTF-8 JSON evidence, including completed checks on failure')
    args = parser.parse_args(argv)
    if not 1 <= args.nemo_limit <= 15 or not 0 <= args.nemo_start < 15:
        parser.error('Need nemo-limit in 1..15 and nemo-start in 0..14')
    if args.live and not OPENAI_API_KEY:
        parser.error('Set OPENAI_API_KEY in .env before --live; never paste the key into logs.')

    attacks = json.loads(Path(ADVERSARIAL_SET_PATH).read_text(encoding='utf-8'))
    clean = json.loads(Path(CLEAN_SET_PATH).read_text(encoding='utf-8'))
    checks = []
    root = Path(__file__).resolve().parents[1]
    packages = {}
    for name in ('presidio-analyzer', 'presidio-anonymizer', 'spacy', 'en-core-web-lg',
                 'nemoguardrails', 'openai', 'annoy', 'fastembed', 'onnxruntime'):
        try:
            packages[name] = version(name)
        except PackageNotFoundError:
            packages[name] = None
    report = {'created_at': datetime.now(timezone.utc).isoformat(),
              'scope': 'smoke_only_not_official_phase_c',
              'nemo_live': args.live, 'status': 'running', 'packages': packages,
              'source_sha256': {
                  name: hashlib.sha256((root / name).read_bytes()).hexdigest()
                  for name in ('src/phase_c_guard.py', 'guardrails/config.yml',
                               'guardrails/rails.co', 'fixtures/adversarial_set_20.json',
                               'fixtures/clean_set_8.json')},
              'checks': checks}

    def save_report():
        report['passed'] = sum(row['passed'] for row in checks)
        report['total'] = len(checks)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')

    save_report()
    try:
        analyzer, anonymizer = setup_presidio()
        run_checks(analyzer, anonymizer, attacks, clean, args, checks, save_report)
    except Exception as error:
        # Never serialize provider messages: some include credential fragments.
        report['status'] = 'runtime_error'
        report['error_type'] = type(error).__name__
        status_code = getattr(error, 'status_code', None)
        if isinstance(status_code, int):
            report['error_status_code'] = status_code
        save_report()
        print(json.dumps(report, indent=2))
        return 1
    report['status'] = 'passed' if all(row['passed'] for row in checks) else 'failed_checks'
    save_report()
    print(json.dumps(report, indent=2))
    return 0 if report['status'] == 'passed' else 1


def run_checks(analyzer, anonymizer, attacks, clean, args, checks, save_report):
    # Real Presidio, including default NER: verify clean controls and four PII cases.
    for item in clean + [row for row in attacks if row['id'] in (1, 2, 3, 4)]:
        result = pii_scan(item['input'], analyzer, anonymizer)
        expected_pii = item['expected'] == 'blocked'
        passed = result['has_pii'] == expected_pii
        if result['has_pii']:
            passed = passed and result['anonymized'] != item['input']
        checks.append({'id': item['id'], 'layer': 'presidio', 'passed': passed,
                       'has_pii': result['has_pii'],
                       'entity_types': sorted({row['type'] for row in result['entities']})})
        save_report()

    if args.live:
        # Fail before NeMo starts a background indexing thread if its native
        # dependency is absent; the saved Presidio evidence remains available.
        import annoy  # noqa: F401

        async def check_nemo():
            rails = setup_nemo_rails()
            selected = [row for row in attacks if row['id'] in (5, 7, 16, 17, 18, 19, 20)] + clean
            selected = selected[args.nemo_start:args.nemo_start + args.nemo_limit]
            for item in selected:
                result = await check_input_rail(item['input'], rails)
                actual = 'allowed' if result['allowed'] else 'blocked'
                checks.append({'id': item['id'], 'layer': 'nemo_input',
                             'actual': actual, 'passed': actual == item['expected']})
                save_report()
        asyncio.run(check_nemo())


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as error:
        # Provider error strings can contain credential fragments; do not log them.
        print(f'Smoke check stopped: {type(error).__name__}. No further inputs scheduled.', file=sys.stderr)
        raise SystemExit(1)

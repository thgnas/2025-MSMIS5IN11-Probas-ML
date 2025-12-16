import subprocess
import sys
import json
from statistics import mean
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'etape 2'
PY = sys.executable

def run_once(max_cycle, no_browser=True):
    args = [PY, str(SCRIPT), '--max-cycle', str(max_cycle)]
    if no_browser:
        args.append('--no-browser')
    proc = subprocess.run(args, capture_output=True, text=True)
    out = proc.stdout.strip().splitlines()
    # chercher la dernière ligne JSON
    summary = None
    for line in reversed(out):
        line = line.strip()
        if line.startswith('{') and line.endswith('}'):
            try:
                summary = json.loads(line)
                break
            except Exception:
                continue
    if summary is None:
        # essayer stderr
        err = proc.stderr.strip().splitlines()
        for line in reversed(err):
            line = line.strip()
            if line.startswith('{') and line.endswith('}'):
                try:
                    summary = json.loads(line)
                    break
                except Exception:
                    continue
    return summary


def benchmark(trials=5):
    results = {'2-only': [], 'mix': []}
    for t in range(trials):
        print(f"Run {t+1}/{trials} — mode 2-only")
        s2 = run_once(2)
        print('  ->', s2)
        if s2:
            results['2-only'].append(s2['n_saved'])

        print(f"Run {t+1}/{trials} — mode mix (max_cycle=3)")
        sm = run_once(3)
        print('  ->', sm)
        if sm:
            results['mix'].append(sm['n_saved'])

    summary = {}
    for k, vals in results.items():
        summary[k] = {
            'trials': len(vals),
            'mean_saved': mean(vals) if vals else 0,
            'all': vals
        }
    print('\n=== BENCHMARK RESULT ===')
    print(json.dumps(summary, indent=2))

if __name__ == '__main__':
    benchmark(trials=5)

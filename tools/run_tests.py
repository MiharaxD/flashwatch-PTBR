"""Run the project's standalone test scripts and retain their full logs."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def main() -> int:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    cli.add_argument("--out", type=Path, default=Path("build/test-results"))
    args = cli.parse_args()
    root = args.root.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, QT_QPA_PLATFORM="offscreen", PYTHONIOENCODING="utf-8")
    results = []
    for test in sorted((root / "tests").glob("test_*.py")):
        start = time.perf_counter()
        with (out / f"{test.stem}.log").open("w", encoding="utf-8") as log:
            result = subprocess.run([sys.executable, str(test)], cwd=root,
                                    env=env, stdout=log, stderr=subprocess.STDOUT)
        results.append(dict(suite=test.name, code=result.returncode,
                            seconds=round(time.perf_counter() - start, 2)))
        print(f"{'PASS' if result.returncode == 0 else 'FAIL'} {test.name}", flush=True)
        (out / "results.json").write_text(json.dumps(results, indent=2), "utf-8")
    return int(any(row["code"] for row in results))


if __name__ == "__main__":
    sys.exit(main())

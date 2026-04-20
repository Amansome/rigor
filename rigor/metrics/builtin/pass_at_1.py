"""pass@1 metric: executes generated code in sandboxed subprocess."""

import resource
import subprocess
import sys
import tempfile
import os

from rigor.metrics import registry


def _extract_code(output: str, entry_point: str) -> str:
    if "```python" in output:
        start = output.index("```python") + len("```python")
        end = output.index("```", start)
        return output[start:end].strip()
    if "```" in output:
        start = output.index("```") + 3
        end = output.index("```", start)
        return output[start:end].strip()
    # No fences — return as-is, only stripping surrounding blank lines.
    # Preserve internal indentation (function body lines start with spaces).
    return output.strip("\n")


def _run_sandboxed(script: str, timeout_s: float = 10.0) -> tuple[int, str]:
    """Run script in a subprocess with resource limits. Returns (returncode, stderr)."""
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            script_path = os.path.join(tmpdir, "solution.py")
            with open(script_path, "w") as f:
                f.write(script)

            def _set_limits():
                resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
                # RLIMIT_AS is unreliable on macOS (BSD); skip it there.
                if sys.platform != "darwin":
                    resource.setrlimit(
                        resource.RLIMIT_AS,
                        (512 * 1024 * 1024, 512 * 1024 * 1024),
                    )

            result = subprocess.run(
                [sys.executable, script_path],
                cwd=tmpdir,
                timeout=timeout_s,
                stderr=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                text=True,
                preexec_fn=_set_limits,
            )
            return result.returncode, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "TIMEOUT"
    except Exception as e:
        return -1, str(e)


class PassAt1:
    name = "pass_at_1"

    def compute(self, output: str, reference: dict, input: dict) -> float:
        entry_point = input["entry_point"]
        extracted = _extract_code(output, entry_point)
        script = (
            input["prompt"]
            + "\n"
            + extracted
            + "\n"
            + reference["test"]
            + "\n"
            + f"check({entry_point})"
        )
        returncode, _ = _run_sandboxed(script)
        return 1.0 if returncode == 0 else 0.0


registry.register(PassAt1())

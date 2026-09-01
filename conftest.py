import sys


def pytest_configure(config):
    """Reset stdout/stderr encoding to avoid UnicodeEncodeError on Windows (cp1252)."""
    stdout_reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(stdout_reconfigure):
        stdout_reconfigure(encoding="utf-8")
    stderr_reconfigure = getattr(sys.stderr, "reconfigure", None)
    if callable(stderr_reconfigure):
        stderr_reconfigure(encoding="utf-8")

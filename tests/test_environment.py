"""
Smoke test to ensure environment inspection module works properly.
"""
import pytest
from scripts.inspect_environment import inspect_environment

def test_environment_inspection():
    report = inspect_environment()
    assert "os" in report
    assert "python" in report
    assert "disk_space" in report
    assert report["os"]["system"] == "Windows"

import importlib.util
import os
from pathlib import Path


def test_port_env(monkeypatch):
    monkeypatch.setenv('PORT', '8080')
    module_path = Path(__file__).resolve().parents[1] / 'aws-cost-exporter.py'
    spec = importlib.util.spec_from_file_location('aws_cost_exporter', module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.port == 8080


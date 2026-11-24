"""Offline tests for EconHarnessToolkit folder walls, domain tools, and synthetic benchmark data."""

import json

import pytest

from econ_agent_harness.benchmark.synthetic_data import SyntheticDataBuilder
from econ_agent_harness.tools import EconHarnessToolkit


def test_folder_walls_block_raw_and_root_writes(tmp_path):
    toolkit = EconHarnessToolkit(tmp_path)
    (tmp_path / "data/raw").mkdir(parents=True)
    (tmp_path / "data/raw/input.csv").write_text("x\n1\n")

    with pytest.raises(PermissionError, match="read-only"):
        toolkit.write_file("data/raw/input.csv", "overwrite")

    with pytest.raises(PermissionError, match="outside allowed"):
        toolkit.write_file("loose_script.py", "print(1)")

    with pytest.raises(PermissionError, match="escapes workspace"):
        toolkit.write_file("../escape.txt", "bad")

    msg = toolkit.write_file("references/configs/ok.yaml", "seed: 42\n")
    assert "references/configs/ok.yaml" in msg
    assert (tmp_path / "data/raw/input.csv").read_text() == "x\n1\n"


def test_synthetic_data_and_domain_tools_run_offline(tmp_path):
    hashes = SyntheticDataBuilder({}, seed=42).build(tmp_path / "data/raw")
    assert set(hashes) == {"macro_panel.csv", "cb_statements.csv", "synthetic_wp.pdf", "macro_monthly.csv"}

    toolkit = EconHarnessToolkit(tmp_path)
    toolkit.write_file("references/configs/svar.yaml", toolkit.get_config_template("proxy_svar"))
    svar_res = json.loads(toolkit.run_proxy_svar("references/configs/svar.yaml"))
    assert svar_res["status"] == "ok"
    assert svar_res["var_nobs"] == 224
    assert (tmp_path / "data/final/proxy_svar_irfs.csv").is_file()
    assert (tmp_path / "reports/proxy_svar_irfs.tex").is_file()

    toolkit.write_file("references/configs/sent.yaml", toolkit.get_config_template("sentiment"))
    sent_res = json.loads(toolkit.run_sentiment("references/configs/sent.yaml"))
    assert sent_res["status"] == "ok"
    assert sent_res["rows"] == 16

    pdf_res = json.loads(toolkit.extract_pdf_claims("data/raw/synthetic_wp.pdf", "reports/claims.md"))
    assert pdf_res["status"] == "ok"
    assert len(pdf_res["claims"]) >= 2
    assert all(c["page"] == 2 for c in pdf_res["claims"])


def test_resolve_model_supports_ollama_prefix_and_provider(monkeypatch):
    from econ_agent_harness.agent import _resolve_model

    monkeypatch.setenv("OLLAMA_API_KEY", "dummy-ollama-key")
    m1 = _resolve_model(None, "ollama:glm-5.3-flash:cloud")
    assert m1.model_name == "glm-5.3-flash:cloud"
    assert str(m1.base_url).rstrip("/") == "https://ollama.com/v1"

    m2 = _resolve_model("ollama-api-key", "beam")
    assert m2.model_name == "beam"
    assert str(m2.base_url).rstrip("/") == "https://ollama.com/v1"

    monkeypatch.delenv("OLLAMA_API_KEY", raising=False)
    with pytest.raises(ValueError, match="OLLAMA_API_KEY"):
        _resolve_model(None, "ollama:glm-5.3-flash:cloud")

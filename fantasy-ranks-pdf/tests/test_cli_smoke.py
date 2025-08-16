from __future__ import annotations

from typer.testing import CliRunner

from fantasy_ranks.cli import app as typer_app


runner = CliRunner()


def test_cli_export_smoke(tmp_path, monkeypatch):
    out = tmp_path / "out.pdf"
    # Force provider to use a stable sample fall-back rather than live ESPN
    monkeypatch.setenv("FANTASY_RANKS_ESPN_URL", "about:blank")
    result = runner.invoke(
        typer_app,
        [
            "--source",
            "espn-editorial",
            "--scoring",
            "ppr",
            "--limit",
            "10",
            "--out",
            str(out),
        ],
    )
    assert result.exit_code == 0, result.output
    assert out.exists() and out.stat().st_size > 0

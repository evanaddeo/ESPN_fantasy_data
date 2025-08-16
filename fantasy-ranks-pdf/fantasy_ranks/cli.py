from __future__ import annotations

import subprocess
import os
import sys
from datetime import date
from pathlib import Path
from typing import Iterable, Optional

import typer
from rich.console import Console
from rich.table import Table

from fantasy_ranks.models import ScoringEnum
from fantasy_ranks.providers.espn_editorial import ESPNEditorialProvider
from fantasy_ranks.render.pdf import render_rankings_pdf
from fantasy_ranks.utils.tables import ensure_columns, filter_positions

app = typer.Typer(add_completion=False, help="Export fantasy rankings to a styled PDF")
console = Console()


def _get_provider(source: str):
    if source == "espn-editorial":
        return ESPNEditorialProvider()
    raise typer.BadParameter(f"Unsupported source: {source}")


@app.callback(invoke_without_command=True)
def export(
    source: str = typer.Option("espn-editorial", help="Data source provider."),
    scoring: ScoringEnum = typer.Option(ScoringEnum.ppr, help="Scoring format."),
    positions: Optional[str] = typer.Option(None, help="CSV list, e.g. QB,RB,WR,TE,K,DST"),
    only: Optional[str] = typer.Option(None, help="Keep only these positions (CSV)."),
    limit: Optional[int] = typer.Option(300, help="Max number of rows to include."),
    include_bye: bool = typer.Option(True, "--include-bye/--no-bye", help="Include bye week column."),
    style: str = typer.Option("light", help="PDF style: light|dark"),
    out: Path = typer.Option(Path("./ESPN_PPR_2025.pdf"), help="Output PDF path."),
    open_: bool = typer.Option(False, "--open", help="Open the generated PDF."),
    raw: bool = typer.Option(False, help="Print CSV to stdout instead of PDF."),
):
    """Export rankings to a PDF (or CSV to stdout)."""
    provider = _get_provider(source)
    pos_list = [p.strip() for p in positions.split(",")] if positions else None

    console.status("Fetching rankings...")
    df = provider.fetch(scoring, positions=pos_list, limit=limit)

    if raw:
        console.print(df.to_csv(index=False))
        raise typer.Exit(0)

    # Normalize and ensure required columns; guard against empty provider results
    if df.empty:
        console.print("No data parsed from provider; try --raw to debug.", style="yellow")
    df = filter_positions(df, only.split(",")) if only else filter_positions(df, pos_list)
    df = ensure_columns(df, include_bye=include_bye)

    title = "ESPN Fantasy Rankings"
    pdf_bytes = render_rankings_pdf(
        df,
        scoring=scoring,
        title=title,
        style="dark" if style == "dark" else "light",
        include_bye=include_bye,
        source=provider.name,
        source_url=provider.homepage_url,
        generated_date=date.today(),
        logos_enabled=False,
    )

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(pdf_bytes)
    console.print(f"Saved: {out}")

    if open_:
        try:
            typer.launch(str(out))
        except Exception:
            # fallback
            try:
                if sys.platform == "darwin":
                    subprocess.run(["open", str(out)], check=False)
                elif sys.platform.startswith("win"):
                    os.startfile(str(out))  # type: ignore[attr-defined]
                else:
                    subprocess.run(["xdg-open", str(out)], check=False)
            except Exception:
                console.print("Could not auto-open the file", style="yellow")


def main() -> None:
    app()

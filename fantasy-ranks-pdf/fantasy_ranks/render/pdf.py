from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Dict, Iterable, List, Literal, Optional, Tuple

import pandas as pd
from fpdf import FPDF

Position = Literal["QB", "RB", "WR", "TE", "K", "DST"]
Style = Literal["light", "dark"]
ConsensusDf = pd.DataFrame


@dataclass
class RenderContext:
    title: str
    scoring: str
    source: str
    source_url: str
    include_bye: bool
    style: Style
    generated_date: date
    logos_enabled: bool = False


POSITION_COLORS: Dict[Position, Tuple[int, int, int]] = {
    "QB": (66, 135, 245),
    "RB": (52, 168, 83),
    "WR": (234, 67, 53),
    "TE": (251, 188, 5),
    "K": (170, 0, 255),
    "DST": (0, 173, 181),
}

LIGHT_TEXT = (34, 34, 34)
DARK_TEXT = (240, 240, 240)
LIGHT_BG = (255, 255, 255)
DARK_BG = (24, 24, 24)


class RankingsPDF(FPDF):
    def __init__(self, ctx: RenderContext) -> None:
        super().__init__(orientation="P", unit="mm", format="A4")
        self.ctx = ctx
        self.set_auto_page_break(auto=True, margin=15)
        # Disable compression to keep byte output stable and searchable in tests
        self.set_compression(False)
        # Deterministic metadata
        self.set_title(ctx.title)
        self.set_author("fantasy-ranks-pdf")
        self.set_creator("fantasy-ranks-pdf")
        # Include source in metadata to support deterministic testing of header/footer content
        self.set_subject(f"Source: {ctx.source} | {ctx.source_url}")
        # Theme
        if ctx.style == "dark":
            self.text_rgb = DARK_TEXT
            self.bg_rgb = DARK_BG
        else:
            self.text_rgb = LIGHT_TEXT
            self.bg_rgb = LIGHT_BG

    # Header/footer
    def header(self) -> None:  # type: ignore[override]
        self.set_fill_color(*self.bg_rgb)
        self.rect(0, 0, self.w, 20, style="F")
        self.set_font("Helvetica", style="B", size=12)
        self.set_text_color(*self.text_rgb)
        header_text = f"{self.ctx.title} - {self.ctx.scoring.upper()}"
        header_text = header_text.replace("—", "-")
        self.set_xy(10, 8)
        self.cell(0, 6, txt=header_text, ln=0)
        self.set_font("Helvetica", size=10)
        self.set_xy(-70, 8)  # right-ish
        self.cell(60, 6, txt=self.ctx.generated_date.isoformat(), ln=0, align="R")
        self.ln(12)

    def footer(self) -> None:  # type: ignore[override]
        self.set_y(-15)
        self.set_font("Helvetica", size=9)
        self.set_text_color(120, 120, 120)
        footer_text = f"Source: {self.ctx.source} | {self.ctx.source_url}"
        self.cell(0, 10, footer_text, align="C")


def _column_defs(include_bye: bool) -> List[Tuple[str, str, int]]:
    cols: List[Tuple[str, str, int]] = [
        ("rank", "Rank", 15),
        ("name", "Name", 70),
        ("team", "Team", 20),
        ("pos", "Pos", 15),
    ]
    if include_bye:
        cols.append(("bye", "Bye", 15))
    return cols


def render_rankings_pdf(
    df: pd.DataFrame,
    *,
    scoring: str,
    title: str,
    style: Style,
    include_bye: bool,
    source: str,
    source_url: str,
    generated_date: Optional[date] = None,
    logos_enabled: bool = False,
) -> bytes:
    """Render rankings to a PDF and return bytes.

    Ensures deterministic header/footer by fixing metadata and accepting a fixed date.
    """
    ctx = RenderContext(
        title=title,
        scoring=scoring,
        source=source,
        source_url=source_url,
        include_bye=include_bye,
        style=style,
        generated_date=generated_date or date.today(),
        logos_enabled=logos_enabled,
    )
    pdf = RankingsPDF(ctx)
    pdf.add_page()

    # Table header
    col_defs = _column_defs(include_bye)
    pdf.set_font("Helvetica", style="B", size=10)
    pdf.set_text_color(*pdf.text_rgb)
    for _, label, width in col_defs:
        pdf.cell(width, 8, label, border=1, align="L")
    pdf.ln()

    # Table rows
    pdf.set_font("Helvetica", size=10)
    for _, row in df.iterrows():
        pos = str(row.get("pos", "")).upper()
        rgb = POSITION_COLORS.get(pos, (200, 200, 200))
        pdf.set_fill_color(*rgb)
        pdf.set_text_color(*pdf.text_rgb)
        for key, _, width in col_defs:
            value = row.get(key, "")
            pdf.cell(width, 7, str(value), border=1, align="L", fill=True)
        pdf.ln()

    out = pdf.output(dest="S")
    # fpdf2 may return bytes or bytearray depending on version
    if isinstance(out, (bytes, bytearray)):
        return bytes(out)
    # Some versions return str encoded latin1
    return out.encode("latin1")


def render_consensus_pdf(
    df: pd.DataFrame,
    *,
    style: Style,
    generated_date: Optional[date] = None,
) -> bytes:
    # Page 1: consensus top 150
    ctx = RenderContext(
        title="Consensus Fantasy Rankings",
        scoring="consensus",
        source="consensus",
        source_url="https://github.com/your-org/fantasy-ranks-pdf",
        include_bye=False,
        style=style,
        generated_date=generated_date or date.today(),
    )
    pdf = RankingsPDF(ctx)
    pdf.add_page()

    # Build table columns
    cols: List[Tuple[str, str, int]] = [
        ("consensus_rank", "Rank", 15),
        ("name", "Name", 70),
        ("team", "Team", 20),
        ("pos", "Pos", 15),
        ("delta", "Delta", 20),
    ]
    pdf.set_font("Helvetica", style="B", size=10)
    pdf.set_text_color(*pdf.text_rgb)
    for _, label, width in cols:
        pdf.cell(width, 8, label, border=1, align="L")
    pdf.ln()

    pdf.set_font("Helvetica", size=10)
    top = df.sort_values("consensus_rank").head(150)
    for _, row in top.iterrows():
        pos = str(row.get("pos", "")).upper()
        rgb = POSITION_COLORS.get(pos, (200, 200, 200))
        pdf.set_fill_color(*rgb)
        pdf.set_text_color(*pdf.text_rgb)
        for key, _, width in cols:
            value = row.get(key, "")
            pdf.cell(width, 7, str(value), border=1, align="L", fill=True)
        pdf.ln()

    # Page 2: biggest differences top +/-25
    pdf.add_page()
    pdf.set_font("Helvetica", style="B", size=10)
    for _, label, width in cols:
        pdf.cell(width, 8, label, border=1, align="L")
    pdf.ln()
    pdf.set_font("Helvetica", size=10)
    diffs = (
        df.assign(abs_delta=(df["delta"].abs()))
        .sort_values("abs_delta", ascending=False)
        .head(25)
    )
    for _, row in diffs.iterrows():
        pos = str(row.get("pos", "")).upper()
        rgb = POSITION_COLORS.get(pos, (200, 200, 200))
        pdf.set_fill_color(*rgb)
        pdf.set_text_color(*pdf.text_rgb)
        for key, _, width in cols:
            value = row.get(key, "")
            pdf.cell(width, 7, str(value), border=1, align="L", fill=True)
        pdf.ln()

    out = pdf.output(dest="S")
    if isinstance(out, (bytes, bytearray)):
        return bytes(out)
    return out.encode("latin1")

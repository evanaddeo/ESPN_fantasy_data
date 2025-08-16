from __future__ import annotations

from datetime import date

import pandas as pd

from fantasy_ranks.render.pdf import render_rankings_pdf


def test_pdf_header_footer_contains_expected_text(tmp_path):
    df = pd.DataFrame(
        [
            {"rank": 1, "name": "Test Player", "team": "AAA", "pos": "RB", "bye": 7},
        ]
    )
    pdf_bytes = render_rankings_pdf(
        df,
        scoring="ppr",
        title="Fantasy Football Rankings",
        style="light",
        include_bye=True,
        source="espn-editorial",
        source_url="https://www.espn.com/fantasy/football/",
        generated_date=date(2025, 1, 1),
        logos_enabled=False,
    )
    # Basic PDF header
    assert pdf_bytes.startswith(b"%PDF-1.")
    # Header text (title and scoring)
    assert b"Fantasy Football Rankings - PPR" in pdf_bytes
    # Header date
    assert b"2025-01-01" in pdf_bytes
    # Footer text (source and URL)
    assert b"Source: espn-editorial | https://www.espn.com/fantasy/football/" in pdf_bytes

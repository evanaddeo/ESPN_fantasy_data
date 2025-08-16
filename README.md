# Fantasy Football Rankings

[![CI](https://github.com/your-org/fantasy-ranks-pdf/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/fantasy-ranks-pdf/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/fantasy-ranks-pdf.svg)](https://pypi.org/project/fantasy-ranks-pdf/)
[![Python](https://img.shields.io/pypi/pyversions/fantasy-ranks-pdf.svg)](https://pypi.org/project/fantasy-ranks-pdf/)

A cross-platform CLI that fetches current fantasy football rankings (ESPN editorial to start), formats them into a clean, color-coded PDF, and saves locally. Designed for extension to other sources (Sleeper, Yahoo).

## Features
- **Multiple scoring presets**: PPR / Half-PPR / Standard
- **Beautiful PDFs**: header with title/scoring/date; footer with source + URL; auto page breaks; color-coded positions
- **Fast and resilient**: tolerant HTML parsing, graceful errors, and local caching
- **Extensible providers**: simple base class with ESPN editorial provider included; optional ESPN API / Sleeper ADP
- **CLI UX**: powered by Typer + Rich; supports CSV/raw output for piping

## Install

### pipx (recommended)
```bash
pipx install fantasy-ranks-pdf
```

### pip
```bash
python -m pip install fantasy-ranks-pdf
```

## Quick start
```bash
fantasy-ranks \
  --source espn-editorial \
  --scoring ppr \
  --limit 300 \
  --out ./ESPN_PPR_2025.pdf
```

Options:
- `--positions`: CSV of positions to include, e.g. `QB,RB,WR,TE,K,DST`
- `--include-bye/--no-bye`: include bye week column
- `--style`: `light` or `dark`
- `--open`: open the generated PDF after export
- `--raw`: print CSV to stdout instead of PDF

## Examples
![Example PDF - Light](docs/images/example_light.png)
![Example PDF - Dark](docs/images/example_dark.png)

> Note: images are placeholders; actual screenshots to be added.

## Architecture
```
fantasy_ranks/
  __init__.py
  cli.py
  models.py              # PlayerRank model (Pydantic)
  providers/
    base.py              # abstract Provider: fetch(scoring)->DataFrame
    espn_editorial.py    # tolerant editorial/cheat sheet scraper (bs4 + lxml)
    espn_api.py          # optional; projections if cookies provided
    sleeper_adp.py       # optional; Sleeper ADP for comparison
  render/
    pdf.py               # fpdf2 renderer from DataFrame
  utils/
    caching.py           # cache helpers (platformdirs)
    tables.py            # DataFrame table helpers
```

## Roadmap
- Additional providers: Sleeper ADP, Yahoo
- Team logos (opt-in) with caching and toggle
- More styling presets and printable layouts
- Better heuristics for table/download sources

## Disclaimer
This project may scrape or process third-party content. Use it responsibly and in accordance with the source’s terms of use. The authors are not affiliated with ESPN, Yahoo, or Sleeper.

## Contributing
Please read `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, and `SECURITY.md`.

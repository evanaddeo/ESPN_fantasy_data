# fantasy-ranks-pdf

Cross-platform CLI to fetch fantasy rankings and export styled PDFs (and CSV via stdout). Sources include ESPN editorial and Sleeper ADP. Designed for easy extension.

## Install
- pipx (recommended):
```bash
pipx install fantasy-ranks-pdf
```
- pip:
```bash
python -m pip install fantasy-ranks-pdf
```

## Quick usage
- Export ESPN editorial rankings (PDF):
```bash
fantasy-ranks --source espn-editorial --scoring ppr --limit 300 \
  --out ~/Downloads/ESPN_PPR_2025.pdf --style dark --open
```
- Export CSV instead of PDF:
```bash
fantasy-ranks --source espn-editorial --scoring ppr --limit 300 --raw > ranks.csv
```
- Filter positions (include only):
```bash
fantasy-ranks --source espn-editorial --only RB,WR,TE --limit 150 --out ./SkillPositions.pdf
```

## Sleeper ADP
- Export Sleeper ADP (no auth):
```bash
fantasy-ranks --source sleeper-adp --limit 250 --out ./Sleeper_ADP.pdf
```
- Optional: provide a fallback ADP JSON URL via env `SLEEPER_ADP_FALLBACK_URL=https://...`.

## Comparisons (consensus + deltas)
- Build a consensus across sources and export a two-page PDF (Top 150 + Biggest Differences):
```bash
fantasy-ranks compare --sources espn-editorial,sleeper-adp \
  --limit 200 --out ./Consensus.pdf --style light
```
- Delta interpretation: `delta = rank_ESPN - rank_Sleeper`. Positive delta means ESPN is higher on the player (lower rank number) than Sleeper; negative means the opposite.

## Notes
- Use `--open` to auto-open a generated PDF.
- Use `--positions QB,RB,...` to include, or `--only QB,RB,...` to keep only those.
- Set cache TTL via `FANTASY_RANKS_CACHE_TTL_SECONDS` (default: 3600s). Sleeper cache TTL via `SLEEPER_CACHE_TTL_SECONDS` (default: 21600s).
- For debugging scraping, use `--raw` to print CSV to stdout.

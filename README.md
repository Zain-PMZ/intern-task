# Reddit Top Posts Scraper

A command-line tool that fetches top posts from any public subreddit using Reddit's public JSON API and outputs clean, structured data to JSON and CSV.

## Setup

**Requirements:** Python 3.10+

```bash
pip install -r requirements.txt
```

## Usage

```bash
python scraper.py <subreddit> <timeframe> [--limit N]
```

**Examples:**
```bash
python scraper.py programming week --limit 50
python scraper.py worldnews day --limit 25
python scraper.py python all --limit 100
```

Output files are saved to the `output/` directory:
- `output/programming_week.json`
- `output/programming_week.csv`

## Running Tests

```bash
pip install pytest
pytest tests/ -v
```

## Assumptions & Decisions

- **Python + requests only** — no heavy frameworks needed for this task.
- **No authentication** — uses Reddit's public `.json` endpoints exclusively.
- **User-Agent** is set to a descriptive string as required by Reddit's API guidelines.
- **Pagination** follows Reddit's `after` cursor across pages, with a 1-second delay between requests.
- **Rate limiting** — backs off on 429 with `Retry-After`, retries up to 3 times.
- **Resilience** — malformed posts are skipped and logged; the run continues.
- Timestamps are converted from Unix UTC to ISO 8601 format.
- Deleted authors are stored as `[deleted]` rather than `null`.

## Error Handling

| Scenario | Behaviour |
|---|---|
| Subreddit not found (404) | Logs error, exits cleanly |
| Private/quarantined (403) | Logs error, exits cleanly |
| Empty results | Logs warning, saves empty output |
| Network timeout | Retries up to 3x, then exits cleanly |
| Rate limited (429) | Waits Retry-After seconds, retries |
| Malformed post | Skips the post, continues |

## What I'd Improve With More Time

- Add async requests (httpx + asyncio) for faster pagination
- Support multiple subreddits in one run
- Add a --output-dir flag for custom output paths
- Store results in SQLite for incremental runs
- Expand test coverage to include pagination logic

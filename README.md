# Reddit Top Posts Scraper

A command-line tool that fetches top posts from any public subreddit using Reddit's own JSON API. Uses Playwright browser emulation to handle Reddit's geo-restrictions and bot detection.

## Setup

**Requirements:** Python 3.10+

pip install -r requirements.txt
python3 -m playwright install chromium

## Usage

python3 scraper.py <subreddit> <timeframe> [--limit N]

**Examples:**

python3 scraper.py programming week --limit 50
python3 scraper.py worldnews day --limit 25
python3 scraper.py python all --limit 100

Output files are saved to the output/ directory:
- output/programming_week.json
- output/programming_week.csv

## Running Tests

pip install pytest pytest-timeout
pytest tests/ -v --timeout=10

## How it works

Reddit's public JSON endpoints return 403 for requests from certain regions. This scraper uses Playwright to launch a headless Chromium browser, warm up a real session on reddit.com (acquiring cookies and headers), then fetches the JSON API endpoint directly. No third-party proxy or API service is used — all data comes straight from reddit.com.

## Assumptions & Decisions

- Playwright handles the browser session; the JSON is parsed directly from the page body.
- No authentication — uses Reddit's public endpoints only. No login, no credentials.
- Pagination follows Reddit's after cursor across pages with a 1-second delay between requests.
- Rate limiting — backs off on repeated failures, retries up to 3 times.
- Resilience — malformed posts are skipped and logged; the run continues.
- Timestamps converted from Unix UTC to ISO 8601.
- Deleted authors stored as [deleted].

## Error Handling

| Scenario | Behaviour |
|---|---|
| Subreddit not found (404) | Logs error, exits cleanly |
| Private/quarantined (403) | Logs error, exits cleanly |
| Empty results | Logs warning, saves empty output |
| Network timeout | Retries up to 3x, then exits cleanly |
| Malformed post | Skips the post, continues |

## What I'd Improve With More Time

- Cache the browser session so repeated runs don't need to warm up again
- Add async fetching for faster pagination
- Support multiple subreddits in one run
- Store results in SQLite for incremental runs
- Expand test coverage to include pagination and timeout retry logic
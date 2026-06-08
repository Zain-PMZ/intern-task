"""
Reddit Top Posts Scraper
Fetches top posts from a subreddit using Reddit's public JSON API.
"""

import argparse
import csv
import json
import time
import logging
from datetime import datetime, timezone
from pathlib import Path

import requests

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

BASE_URL = "https://www.reddit.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def fetch_page(subreddit: str, timeframe: str, limit: int, after: str | None) -> dict:
    url = f"{BASE_URL}/r/{subreddit}/top.json"
    params = {"t": timeframe, "limit": min(limit, 100), "raw_json": 1}
    if after:
        params["after"] = after

    for attempt in range(3):
        try:
            resp = requests.get(url, headers=HEADERS, params=params, timeout=10)
        except requests.exceptions.Timeout:
            log.warning("Request timed out (attempt %d/3)", attempt + 1)
            time.sleep(2 ** attempt)
            continue
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Network error: {e}") from e

        if resp.status_code == 200:
            return resp.json()
        if resp.status_code == 429:
            wait = int(resp.headers.get("Retry-After", 5))
            log.warning("Rate limited. Waiting %ds...", wait)
            time.sleep(wait)
            continue
        if resp.status_code == 404:
            raise ValueError(f"Subreddit r/{subreddit} not found (404).")
        if resp.status_code == 403:
            raise ValueError(f"Subreddit r/{subreddit} is private or quarantined (403).")
        resp.raise_for_status()

    raise RuntimeError("Failed after 3 attempts (rate limit or timeout).")


def parse_post(post_data: dict) -> dict | None:
    try:
        d = post_data["data"]
        return {
            "id": d["id"],
            "title": d["title"],
            "author": d.get("author") or "[deleted]",
            "score": int(d["score"]),
            "num_comments": int(d["num_comments"]),
            "permalink": BASE_URL + d["permalink"],
            "created_at": datetime.fromtimestamp(d["created_utc"], tz=timezone.utc)
                                 .strftime("%Y-%m-%dT%H:%M:%SZ"),
            "flair": d.get("link_flair_text") or "",
        }
    except (KeyError, TypeError, ValueError) as e:
        log.warning("Skipping malformed post: %s", e)
        return None


def scrape(subreddit: str, timeframe: str, limit: int = 50) -> list[dict]:
    posts = []
    seen_ids = set()
    after = None

    while len(posts) < limit:
        batch_limit = min(limit - len(posts), 100)
        log.info("Fetching %d posts (have %d so far)...", batch_limit, len(posts))

        data = fetch_page(subreddit, timeframe, batch_limit, after)
        children = data.get("data", {}).get("children", [])

        if not children:
            log.info("No more posts available.")
            break

        for child in children:
            post = parse_post(child)
            if post and post["id"] not in seen_ids:
                seen_ids.add(post["id"])
                posts.append(post)

        after = data.get("data", {}).get("after")
        if not after:
            break

        time.sleep(1)

    return posts


def save_json(output: dict, path: Path) -> None:
    path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info("JSON saved: %s", path)


def save_csv(posts: list[dict], path: Path) -> None:
    if not posts:
        log.warning("No posts to write to CSV.")
        return
    fields = ["id", "title", "author", "score", "num_comments", "permalink", "created_at", "flair"]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(posts)
    log.info("CSV saved: %s", path)


def main():
    parser = argparse.ArgumentParser(description="Scrape top posts from a subreddit.")
    parser.add_argument("subreddit", help="Subreddit name (e.g. programming)")
    parser.add_argument("timeframe", choices=["day", "week", "month", "year", "all"],
                        help="Time filter")
    parser.add_argument("--limit", type=int, default=50, help="Max posts to fetch (default: 50)")
    args = parser.parse_args()

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    try:
        posts = scrape(args.subreddit, args.timeframe, args.limit)
    except ValueError as e:
        log.error(str(e))
        return
    except RuntimeError as e:
        log.error(str(e))
        return

    if not posts:
        log.warning("No posts found for r/%s (%s).", args.subreddit, args.timeframe)

    result = {
        "subreddit": args.subreddit,
        "timeframe": args.timeframe,
        "fetched_at": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "count": len(posts),
        "posts": posts,
    }

    stem = f"{args.subreddit}_{args.timeframe}"
    save_json(result, output_dir / f"{stem}.json")
    save_csv(posts, output_dir / f"{stem}.csv")


if __name__ == "__main__":
    main()

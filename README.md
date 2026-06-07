# OnlyStack — Intern Trial Task

**Deadline: 24 hours from the time this task is sent to you.**

Welcome. This is a short, self-contained build task. It's designed to take a focused person roughly one working day. We're not looking for a finished product — we're looking at how you think, how you write code, and how you handle the parts that aren't on the happy path.

You do **not** need anything from us to do this: no API keys, no accounts, no access to our codebase. Everything here runs against public data.

---

## The task

Build a **local scraper script** that pulls the top posts from a subreddit and outputs clean, structured data.

Reddit exposes public data as JSON — append `.json` to almost any page URL and you get a structured response instead of HTML. For example:

```
https://www.reddit.com/r/programming/top.json?t=week&limit=50
```

You do **not** need to scrape HTML, and you do **not** need to log in. Work entirely with the public JSON endpoints.

The script should take a **subreddit name** and a **timeframe** as inputs and produce a clean file of the top posts.

---

## Requirements

### Inputs
- Subreddit name (e.g. `programming`)
- Timeframe (`day`, `week`, `month`, `year`, `all`)
- (Optional) a limit on number of posts, defaulting to 50

### For each post, extract
- Title
- Author
- Score (upvotes)
- Number of comments
- Permalink (full URL)
- Created timestamp (as a readable ISO datetime, not a raw Unix number)
- Flair, if present

### Behaviour
- **Pagination** — Reddit returns posts in pages using an `after` cursor. Follow it so you can pull more than the first page when the limit requires it.
- **Rate limiting** — Reddit will rate-limit you. Set a real, descriptive `User-Agent` header, don't hammer the endpoint, and back off + retry on a `429` response. We pay specific attention to this.
- **Clean output** — write the results to **both** a `JSON` file and a `CSV` file.
- **Resilience** — dedupe posts, and skip malformed entries rather than crashing the whole run.

### Handle these failure cases gracefully (don't just crash)
- Subreddit does not exist (`404`)
- Subreddit is private or quarantined
- Empty results (valid subreddit, no posts in the timeframe)
- Network timeout / upstream error

---

## Suggested output schema

Your JSON output should be something stable and predictable, e.g.:

```json
{
  "subreddit": "programming",
  "timeframe": "week",
  "fetched_at": "2026-06-04T12:00:00Z",
  "count": 50,
  "posts": [
    {
      "id": "abc123",
      "title": "Example post title",
      "author": "some_user",
      "score": 1543,
      "num_comments": 210,
      "permalink": "https://www.reddit.com/r/programming/comments/abc123/...",
      "created_at": "2026-06-01T08:30:00Z",
      "flair": "Discussion"
    }
  ]
}
```

The CSV should contain the same per-post fields, one row per post.

---

## Tech choices

Pick your own language and libraries — choosing a sensible stack and pinning your dependencies (`requirements.txt`, `package.json`, etc.) is part of the task. Use whatever you're fastest and cleanest in.

---

## Rules

- Use **public data only**. Do not log in, do not use credentials, and do not try to bypass any access control, anti-bot measure, or CAPTCHA. If something requires that, it's out of scope — note it and move on.
- Respect the endpoint: sane request rate, real `User-Agent`, back off when asked to.

---

## Deliverables

1. The code, in a Git repo (push to a public/private GitHub repo and share the link) or as a zip.
2. A short **README** with:
   - How to install and run it (exact commands)
   - Any assumptions or decisions you made
   - Anything you'd improve or add with more time
3. The generated `JSON` and `CSV` output from at least one real run.
4. At least one or two small tests (e.g. covering the parsing logic and the "subreddit not found" path).

---

## How we evaluate

We're looking at:
- **Does it work** end to end on a real subreddit.
- **Failure handling** — how the script behaves when things go wrong, not just when they go right.
- **Code quality** — readable, minimal, no over-engineering. A clean small solution beats a clever complicated one.
- **Output quality** — is the data clean, consistent, and actually usable.
- **Communication** — a clear README, sensible commit messages, and honest notes about what's unfinished.

A note on questions: if something is genuinely ambiguous, ask us — one or two sharp questions up front is a good sign. Don't get stuck silently.

---

## Deadline

**You have 24 hours from the moment this task is sent to you.** Commit as you go so your progress is timestamped.

We'd rather see how far you get *cleanly* than a rushed attempt at everything. If you run out of time, submit what you have and use the README to explain what's done, what isn't, and what you'd do next.

Clone this repo and start the project from here and create a pull request to merge into here from your branch as a fork.

Good luck.

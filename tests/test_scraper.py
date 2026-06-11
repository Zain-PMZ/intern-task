"""Tests for scraper parsing logic and error handling."""

import pytest
from unittest.mock import patch, MagicMock
from scraper import parse_post, scrape


def make_child(overrides=None):
    base = {
        "kind": "t3",
        "data": {
            "id": "abc123",
            "title": "Test Post",
            "author": "test_user",
            "score": 100,
            "num_comments": 10,
            "permalink": "/r/test/comments/abc123/test_post/",
            "created_utc": 1717200000.0,
            "link_flair_text": "Discussion",
        }
    }
    if overrides:
        base["data"].update(overrides)
    return base


def test_parse_post_normal():
    post = parse_post(make_child())
    assert post["id"] == "abc123"
    assert post["title"] == "Test Post"
    assert post["score"] == 100
    assert post["flair"] == "Discussion"
    assert post["permalink"].startswith("https://www.reddit.com")


def test_parse_post_no_flair():
    post = parse_post(make_child({"link_flair_text": None}))
    assert post["flair"] == ""


def test_parse_post_deleted_author():
    post = parse_post(make_child({"author": None}))
    assert post["author"] == "[deleted]"


def test_parse_post_malformed():
    result = parse_post({"data": {"title": "No ID here"}})
    assert result is None


def test_parse_post_empty():
    result = parse_post({})
    assert result is None


def test_scrape_subreddit_not_found():
    with patch("scraper.sync_playwright") as mock_pw:
        mock_pw.return_value.__enter__.return_value.chromium.launch.return_value.new_context.return_value.new_page.return_value = MagicMock()
        with patch("scraper.make_browser_context", side_effect=Exception("setup")):
            pass
    with patch("scraper.fetch_page", side_effect=ValueError("Subreddit r/fake not found (404).")):
        with patch("scraper.make_browser_context") as mock_ctx:
            mock_ctx.return_value = (MagicMock(), MagicMock(), MagicMock())
            with pytest.raises(ValueError, match="not found"):
                scrape("fake", "week")


def test_scrape_private_subreddit():
    with patch("scraper.fetch_page", side_effect=ValueError("private or quarantined (403).")):
        with patch("scraper.make_browser_context") as mock_ctx:
            mock_ctx.return_value = (MagicMock(), MagicMock(), MagicMock())
            with pytest.raises(ValueError, match="private or quarantined"):
                scrape("privatetestsubreddit", "week")


def test_scrape_empty_results():
    mock_response = {"data": {"children": [], "after": None}}
    with patch("scraper.fetch_page", return_value=mock_response):
        with patch("scraper.make_browser_context") as mock_ctx:
            mock_ctx.return_value = (MagicMock(), MagicMock(), MagicMock())
            posts = scrape("emptysubreddit", "week")
    assert posts == []


def test_scrape_deduplication():
    child = make_child()
    mock_response = {"data": {"children": [child, child, child], "after": None}}
    with patch("scraper.fetch_page", return_value=mock_response):
        with patch("scraper.make_browser_context") as mock_ctx:
            mock_ctx.return_value = (MagicMock(), MagicMock(), MagicMock())
            posts = scrape("test", "week", limit=10)
    assert len(posts) == 1

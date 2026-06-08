"""Tests for scraper parsing logic and error handling."""

import pytest
from unittest.mock import patch
from scraper import parse_post, scrape


def make_post(overrides=None):
    base = {
        "id": "abc123",
        "title": "Test Post",
        "author": "test_user",
        "score": 100,
        "num_comments": 10,
        "permalink": "/r/test/comments/abc123/test_post/",
        "created_utc": 1717200000.0,
        "link_flair_text": "Discussion",
    }
    if overrides:
        base.update(overrides)
    return base


def test_parse_post_normal():
    post = parse_post(make_post())
    assert post["id"] == "abc123"
    assert post["title"] == "Test Post"
    assert post["score"] == 100
    assert post["flair"] == "Discussion"
    assert post["permalink"].startswith("https://www.reddit.com")


def test_parse_post_no_flair():
    post = parse_post(make_post({"link_flair_text": None}))
    assert post["flair"] == ""


def test_parse_post_deleted_author():
    post = parse_post(make_post({"author": None}))
    assert post["author"] == "[deleted]"


def test_parse_post_malformed():
    result = parse_post({"title": "No ID here"})
    assert result is None


def test_parse_post_empty():
    result = parse_post({})
    assert result is None


def test_scrape_subreddit_not_found():
    with patch("scraper.fetch_page", side_effect=ValueError("Subreddit r/fake not found (404).")):
        with pytest.raises(ValueError, match="not found"):
            scrape("fake", "week")


def test_scrape_private_subreddit():
    with patch("scraper.fetch_page", side_effect=ValueError("private or quarantined (403).")):
        with pytest.raises(ValueError, match="private or quarantined"):
            scrape("privatetestsubreddit", "week")


def test_scrape_empty_results():
    mock_response = {"data": []}
    with patch("scraper.fetch_page", return_value=mock_response):
        posts = scrape("emptysubreddit", "week")
    assert posts == []


def test_scrape_deduplication():
    post = make_post()
    mock_response = {"data": [post, post, post]}
    with patch("scraper.fetch_page", return_value=mock_response):
        posts = scrape("test", "week", limit=10)
    assert len(posts) == 1

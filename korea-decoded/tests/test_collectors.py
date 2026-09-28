from korea_decoded.collectors.naver import parse_news
from korea_decoded.collectors.reddit import parse_listing
from korea_decoded.collectors.rss import parse_rss

RSS = """<?xml version="1.0"?>
<rss version="2.0"><channel>
  <item>
    <title>Seoul subway adds &lt;b&gt;English&lt;/b&gt; signs</title>
    <link>https://example.com/a</link>
    <description>&lt;p&gt;More signs for tourists.&lt;/p&gt;</description>
    <pubDate>Mon, 22 Sep 2026 09:00:00 +0900</pubDate>
  </item>
  <item><title>No link, skipped</title></item>
</channel></rss>"""


def test_parse_rss_cleans_html_and_skips_incomplete_items():
    topics = parse_rss(RSS, source="rss:test")
    assert len(topics) == 1
    assert topics[0].title == "Seoul subway adds English signs"
    assert topics[0].summary == "More signs for tourists."
    assert topics[0].published_at.startswith("2026-09-22T09:00:00")


def test_parse_reddit_listing_skips_stickied_and_sums_engagement():
    payload = {"data": {"children": [
        {"data": {"title": "Weekly thread", "permalink": "/r/korea/1", "stickied": True}},
        {"data": {"title": "Why is Naver so popular?", "permalink": "/r/korea/2",
                  "selftext": "genuine question", "score": 120, "num_comments": 30,
                  "created_utc": 1790000000}},
    ]}}
    topics = parse_listing(payload, "korea")
    assert len(topics) == 1
    assert topics[0].url == "https://www.reddit.com/r/korea/2"
    assert topics[0].engagement == 150


def test_parse_naver_news_strips_bold_tags():
    payload = {"items": [{
        "title": "<b>삼성</b> 반도체 신기록",
        "originallink": "https://news.example.kr/1",
        "link": "https://n.news.naver.com/1",
        "description": "&quot;역대 최대&quot; 실적",
        "pubDate": "Mon, 22 Sep 2026 10:00:00 +0900",
    }]}
    topics = parse_news(payload, "삼성 반도체")
    assert topics[0].title == "삼성 반도체 신기록"
    assert topics[0].summary == '"역대 최대" 실적'
    assert topics[0].url == "https://news.example.kr/1"

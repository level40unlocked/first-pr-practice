"""Collectors fetch candidate topics from outside sources and return RawTopic lists."""

from korea_decoded.collectors.naver import NaverNewsCollector
from korea_decoded.collectors.reddit import RedditCollector
from korea_decoded.collectors.rss import RssCollector

__all__ = ["NaverNewsCollector", "RedditCollector", "RssCollector"]

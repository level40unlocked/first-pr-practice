from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

import requests

from korea_decoded.models import RawTopic

_TAG = re.compile(r"<[^>]+>")


def clean_text(text: str | None) -> str:
    return html.unescape(_TAG.sub("", text or "")).strip()


def to_iso(rfc822: str | None) -> str:
    if not rfc822:
        return ""
    try:
        return parsedate_to_datetime(rfc822).isoformat()
    except (TypeError, ValueError):
        return ""


def parse_rss(xml_text: str, source: str) -> list[RawTopic]:
    root = ET.fromstring(xml_text)
    topics = []
    for item in root.iter("item"):
        title = clean_text(item.findtext("title"))
        link = (item.findtext("link") or "").strip()
        if not title or not link:
            continue
        topics.append(
            RawTopic(
                source=source,
                title=title,
                url=link,
                summary=clean_text(item.findtext("description"))[:500],
                published_at=to_iso(item.findtext("pubDate")),
            )
        )
    return topics


class RssCollector:
    def __init__(self, feeds: list[str], session: requests.Session | None = None):
        self.feeds = feeds
        self.session = session or requests.Session()

    def collect(self) -> list[RawTopic]:
        topics = []
        for url in self.feeds:
            resp = self.session.get(url, timeout=20)
            resp.raise_for_status()
            topics.extend(parse_rss(resp.text, source=f"rss:{url}"))
        return topics

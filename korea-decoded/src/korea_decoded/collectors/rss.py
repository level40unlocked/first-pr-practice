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


# Some news sites refuse requests without a browser-like User-Agent.
BROWSER_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"


class RssCollector:
    def __init__(self, feeds: list[str], session: requests.Session | None = None, log=print):
        self.feeds = feeds
        self.session = session or requests.Session()
        self.log = log

    def collect(self) -> list[RawTopic]:
        """Reads every feed; one broken feed is reported and skipped, not fatal."""
        topics, errors = [], []
        for url in self.feeds:
            try:
                resp = self.session.get(url, timeout=20, headers={"User-Agent": BROWSER_UA})
                resp.raise_for_status()
                topics.extend(parse_rss(resp.text, source=f"rss:{url}"))
            except (requests.RequestException, ET.ParseError) as e:
                errors.append(e)
                self.log(f"  rss: skipped {url} ({e})")
        if errors and not topics:
            raise errors[0]
        return topics

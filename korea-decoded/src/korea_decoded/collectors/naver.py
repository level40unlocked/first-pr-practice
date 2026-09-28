from __future__ import annotations

import requests

from korea_decoded.collectors.rss import clean_text, to_iso
from korea_decoded.models import RawTopic

NEWS_URL = "https://openapi.naver.com/v1/search/news.json"


def parse_news(payload: dict, query: str) -> list[RawTopic]:
    topics = []
    for item in payload.get("items", []):
        url = item.get("originallink") or item.get("link")
        title = clean_text(item.get("title"))
        if not url or not title:
            continue
        topics.append(
            RawTopic(
                source=f"naver:{query}",
                title=title,
                url=url,
                summary=clean_text(item.get("description")),
                published_at=to_iso(item.get("pubDate")),
            )
        )
    return topics


class NaverNewsCollector:
    """Naver Search API (news). Needs an app from https://developers.naver.com."""

    def __init__(
        self,
        queries: list[str],
        client_id: str,
        client_secret: str,
        session: requests.Session | None = None,
    ):
        self.queries = queries
        self.headers = {"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret}
        self.session = session or requests.Session()

    def collect(self) -> list[RawTopic]:
        topics = []
        for q in self.queries:
            resp = self.session.get(
                NEWS_URL,
                params={"query": q, "display": 20, "sort": "sim"},
                headers=self.headers,
                timeout=20,
            )
            resp.raise_for_status()
            topics.extend(parse_news(resp.json(), q))
        return topics

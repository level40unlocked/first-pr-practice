from __future__ import annotations

from datetime import datetime, timezone

import requests

from korea_decoded.models import RawTopic


def parse_listing(payload: dict, subreddit: str) -> list[RawTopic]:
    topics = []
    for child in payload.get("data", {}).get("children", []):
        post = child.get("data", {})
        if post.get("stickied") or post.get("over_18"):
            continue
        created = post.get("created_utc")
        topics.append(
            RawTopic(
                source=f"reddit:r/{subreddit}",
                title=post.get("title", "").strip(),
                url="https://www.reddit.com" + post.get("permalink", ""),
                summary=(post.get("selftext") or "")[:500],
                engagement=int(post.get("score", 0)) + int(post.get("num_comments", 0)),
                published_at=(
                    datetime.fromtimestamp(created, tz=timezone.utc).isoformat() if created else ""
                ),
            )
        )
    return topics


class RedditCollector:
    """Reads public subreddit listings. Reddit requires a descriptive User-Agent;
    for heavier use, switch to an OAuth app (https://www.reddit.com/prefs/apps)."""

    def __init__(
        self,
        subreddits: list[str],
        user_agent: str,
        timeframe: str = "week",
        session: requests.Session | None = None,
    ):
        self.subreddits = subreddits
        self.user_agent = user_agent
        self.timeframe = timeframe
        self.session = session or requests.Session()

    def collect(self) -> list[RawTopic]:
        topics = []
        for sub in self.subreddits:
            resp = self.session.get(
                f"https://www.reddit.com/r/{sub}/top.json",
                params={"t": self.timeframe, "limit": 25},
                headers={"User-Agent": self.user_agent},
                timeout=20,
            )
            resp.raise_for_status()
            topics.extend(parse_listing(resp.json(), sub))
        return topics

from datetime import datetime
from email.utils import parsedate_to_datetime
import logging

import feedparser
from tenacity import retry, stop_after_attempt, wait_exponential

from ..models import TrendingTopic, NewsSource, TopicCategory

logger = logging.getLogger(__name__)


# (source_enum, rss_url, category)
THAI_RSS_FEEDS: list[tuple[NewsSource, str, TopicCategory]] = [
    # Thairath
    (NewsSource.THAIRATH, "https://www.thairath.co.th/rss/news.xml",         TopicCategory.OTHER),
    (NewsSource.THAIRATH, "https://www.thairath.co.th/rss/politics.xml",     TopicCategory.POLITICS),
    (NewsSource.THAIRATH, "https://www.thairath.co.th/rss/sport.xml",        TopicCategory.SPORTS),
    # Khaosod
    (NewsSource.KHAOSOD,  "https://www.khaosod.co.th/feed",                  TopicCategory.OTHER),
    # Sanook
    (NewsSource.SANOOK,   "https://www.sanook.com/news/rss/news.xml",        TopicCategory.OTHER),
    # Manager
    (NewsSource.MANAGER,  "https://mgronline.com/rss",                        TopicCategory.OTHER),
    # Prachachat
    (NewsSource.PRACHACHAT, "https://www.prachachat.net/feed",               TopicCategory.BUSINESS),
    # BBC Thai
    (NewsSource.BBC_THAI, "https://feeds.bbci.co.uk/thai/rss.xml",           TopicCategory.INTERNATIONAL),
]


def _parse_date(entry) -> datetime:
    for attr in ("published", "updated"):
        raw = getattr(entry, attr, None)
        if raw:
            try:
                return parsedate_to_datetime(raw).replace(tzinfo=None)
            except Exception:
                pass
    return datetime.now()


def _image_from_entry(entry) -> str | None:
    # Try media_thumbnail
    media = getattr(entry, "media_thumbnail", None)
    if media and isinstance(media, list) and media[0].get("url"):
        return media[0]["url"]
    # Try enclosures
    for enc in getattr(entry, "enclosures", []):
        if enc.get("type", "").startswith("image"):
            return enc.get("href")
    # Try links
    for link in getattr(entry, "links", []):
        if link.get("type", "").startswith("image"):
            return link.get("href")
    return None


class ThaiRSSFetcher:
    """ดึงข่าวจาก RSS feeds ของสำนักข่าวไทย"""

    def __init__(self, max_per_feed: int = 10):
        self._max = max_per_feed

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(min=1, max=5))
    def _fetch_feed(
        self,
        source: NewsSource,
        url: str,
        category: TopicCategory,
    ) -> list[TrendingTopic]:
        feed = feedparser.parse(
            url,
            agent="Mozilla/5.0 (compatible; ViralNewsBot/1.0; +https://github.com/smokbomb/dotfiles)",
        )
        topics: list[TrendingTopic] = []
        for entry in feed.entries[: self._max]:
            title = getattr(entry, "title", "").strip()
            link  = getattr(entry, "link",  "").strip()
            if not title or not link:
                continue
            topics.append(TrendingTopic(
                title=title,
                source=source,
                url=link,
                published_at=_parse_date(entry),
                score=0.0,
                category=category,
                summary=getattr(entry, "summary", None),
                image_url=_image_from_entry(entry),
                language="th",
            ))
        return topics

    def fetch_all(self) -> list[TrendingTopic]:
        all_topics: list[TrendingTopic] = []
        for source, url, category in THAI_RSS_FEEDS:
            try:
                items = self._fetch_feed(source, url, category)
                all_topics.extend(items)
                logger.info("Fetched %d topics from %s", len(items), source.value)
            except Exception as e:
                logger.warning("RSS feed %s failed: %s", url, e)
        return all_topics

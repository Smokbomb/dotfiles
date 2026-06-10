from datetime import datetime
from email.utils import parsedate_to_datetime
import logging
import os

import feedparser
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from ..models import TrendingTopic, NewsSource, TopicCategory

logger = logging.getLogger(__name__)


INTERNATIONAL_RSS_FEEDS: list[tuple[NewsSource, str, TopicCategory]] = [
    # BBC World
    (NewsSource.BBC_WORLD, "http://feeds.bbci.co.uk/news/rss.xml",                   TopicCategory.INTERNATIONAL),
    (NewsSource.BBC_WORLD, "http://feeds.bbci.co.uk/news/world/rss.xml",             TopicCategory.INTERNATIONAL),
    # Reuters
    (NewsSource.REUTERS,   "https://feeds.reuters.com/reuters/topNews",               TopicCategory.INTERNATIONAL),
    (NewsSource.REUTERS,   "https://feeds.reuters.com/reuters/worldNews",             TopicCategory.INTERNATIONAL),
    # AP News
    (NewsSource.AP_NEWS,   "https://rsshub.app/apnews/topics/apf-topnews",           TopicCategory.INTERNATIONAL),
    # CNN
    (NewsSource.CNN,       "http://rss.cnn.com/rss/edition.rss",                     TopicCategory.INTERNATIONAL),
    (NewsSource.CNN,       "http://rss.cnn.com/rss/edition_world.rss",               TopicCategory.INTERNATIONAL),
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
    media = getattr(entry, "media_thumbnail", None)
    if media and isinstance(media, list) and media[0].get("url"):
        return media[0]["url"]
    for enc in getattr(entry, "enclosures", []):
        if enc.get("type", "").startswith("image"):
            return enc.get("href")
    return None


class InternationalRSSFetcher:
    """ดึงข่าวจาก RSS feeds ของสำนักข่าวต่างประเทศ + NewsAPI"""

    def __init__(self, max_per_feed: int = 10, news_api_key: str | None = None):
        self._max = max_per_feed
        self._api_key = news_api_key or os.getenv("NEWS_API_KEY")

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
                language="en",
            ))
        return topics

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(min=2, max=8))
    def fetch_newsapi_top(self, count: int = 20) -> list[TrendingTopic]:
        """ดึง top headlines จาก NewsAPI (ต้องมี API key)"""
        if not self._api_key:
            logger.info("NEWS_API_KEY not set, skipping NewsAPI")
            return []
        try:
            resp = httpx.get(
                "https://newsapi.org/v2/top-headlines",
                params={"language": "en", "pageSize": count, "apiKey": self._api_key},
                timeout=10,
            )
            resp.raise_for_status()
            articles = resp.json().get("articles", [])
            topics: list[TrendingTopic] = []
            for i, art in enumerate(articles):
                title = (art.get("title") or "").strip()
                url   = (art.get("url")   or "").strip()
                if not title or not url:
                    continue
                pub_str = art.get("publishedAt") or ""
                try:
                    pub_dt = datetime.fromisoformat(pub_str.replace("Z", "+00:00")).replace(tzinfo=None)
                except Exception:
                    pub_dt = datetime.now()
                topics.append(TrendingTopic(
                    title=title,
                    source=NewsSource.AP_NEWS,          # generic NewsAPI bucket
                    url=url,
                    published_at=pub_dt,
                    score=float(count - i),
                    category=TopicCategory.INTERNATIONAL,
                    summary=art.get("description"),
                    image_url=art.get("urlToImage"),
                    language="en",
                ))
            return topics
        except Exception as e:
            logger.warning("NewsAPI failed: %s", e)
            return []

    def fetch_all(self) -> list[TrendingTopic]:
        all_topics: list[TrendingTopic] = []
        for source, url, category in INTERNATIONAL_RSS_FEEDS:
            try:
                items = self._fetch_feed(source, url, category)
                all_topics.extend(items)
                logger.info("Fetched %d topics from %s", len(items), source.value)
            except Exception as e:
                logger.warning("RSS feed %s failed: %s", url, e)

        newsapi_items = self.fetch_newsapi_top()
        all_topics.extend(newsapi_items)
        return all_topics

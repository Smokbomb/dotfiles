from datetime import datetime
from typing import Optional
import logging

from pytrends.request import TrendReq
from tenacity import retry, stop_after_attempt, wait_exponential

from ..models import TrendingTopic, NewsSource, TopicCategory

logger = logging.getLogger(__name__)


class GoogleTrendsFetcher:
    """ดึง trending topics จาก Google Trends ทั้งไทยและต่างประเทศ"""

    # geo code -> source mapping
    _GEO_MAP = {
        "TH": (NewsSource.GOOGLE_TRENDS_TH, "th"),
        "":   (NewsSource.GOOGLE_TRENDS_GLOBAL, "en"),
        "US": (NewsSource.GOOGLE_TRENDS_GLOBAL, "en"),
        "GB": (NewsSource.GOOGLE_TRENDS_GLOBAL, "en"),
    }

    def __init__(self, timeout: int = 10):
        self._pytrends = TrendReq(hl="th-TH", tz=420, timeout=(timeout, timeout))

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
    def fetch_realtime(self, geo: str = "TH", count: int = 20) -> list[TrendingTopic]:
        """ดึง real-time trending searches"""
        source, lang = self._GEO_MAP.get(geo, (NewsSource.GOOGLE_TRENDS_GLOBAL, "en"))
        topics: list[TrendingTopic] = []
        try:
            df = self._pytrends.realtime_trending_searches(pn=geo)
            for i, row in df.head(count).iterrows():
                title = row.get("title", "") or row.get("entityNames", "")
                if not title:
                    continue
                related = row.get("relatedStories", []) or []
                related_urls = [s.get("shareUrl", "") for s in related if s.get("shareUrl")]
                topics.append(TrendingTopic(
                    title=str(title).strip(),
                    source=source,
                    url=f"https://trends.google.com/trends/trendingsearches/realtime?geo={geo}",
                    published_at=datetime.now(),
                    score=float(count - i),         # rank-based score (higher rank = higher score)
                    language=lang,
                    related_urls=related_urls[:3],
                ))
        except Exception as e:
            logger.warning("Google Trends realtime (%s) failed: %s", geo, e)
        return topics

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
    def fetch_daily(self, geo: str = "TH") -> list[TrendingTopic]:
        """ดึง daily trending searches (ข่าวดังรายวัน)"""
        source, lang = self._GEO_MAP.get(geo, (NewsSource.GOOGLE_TRENDS_GLOBAL, "en"))
        topics: list[TrendingTopic] = []
        try:
            df = self._pytrends.trending_searches(pn=geo)
            for i, row in df.iterrows():
                title = str(row.iloc[0]).strip()
                if not title:
                    continue
                topics.append(TrendingTopic(
                    title=title,
                    source=source,
                    url=f"https://trends.google.com/trends/explore?q={title}&geo={geo}",
                    published_at=datetime.now(),
                    score=float(len(df) - int(str(i))),
                    language=lang,
                ))
        except Exception as e:
            logger.warning("Google Trends daily (%s) failed: %s", geo, e)
        return topics

    def fetch_all_thai(self) -> list[TrendingTopic]:
        topics = self.fetch_realtime("TH")
        if not topics:
            topics = self.fetch_daily("TH")
        return topics

    def fetch_all_global(self) -> list[TrendingTopic]:
        topics = self.fetch_realtime("")
        if not topics:
            topics = self.fetch_daily("US")
        return topics

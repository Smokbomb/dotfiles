from datetime import datetime, timedelta
from collections import defaultdict
import logging
import re

from rapidfuzz import fuzz

from ..models import TrendingTopic, TopicCategory

logger = logging.getLogger(__name__)

# คำ keyword บ่งบอก category (ไทย + อังกฤษ)
_CATEGORY_KEYWORDS: dict[TopicCategory, list[str]] = {
    TopicCategory.POLITICS: [
        "รัฐบาล","นายกฯ","สส","สว","รัฐสภา","เลือกตั้","พรรค","ยุบสภา","cabinet",
        "parliament","election","senate","minister","prime minister","policy",
    ],
    TopicCategory.ENTERTAINMENT: [
        "ดารา","นักร้อง","ละคร","เพลง","หนัง","ซีรีส์","concert","netflix",
        "celebrity","singer","actor","movie","drama","award","grammy","emmy",
    ],
    TopicCategory.SPORTS: [
        "ฟุตบอล","บอล","แข่ง","ทีมชาติ","กีฬา","เหรียญ","ชนะ",
        "football","soccer","basketball","tennis","olympic","championship","match",
    ],
    TopicCategory.BUSINESS: [
        "หุ้น","ตลาด","เศรษฐกิจ","ธนาคาร","เงินเฟ้อ","ลงทุน",
        "stock","market","economy","gdp","inflation","invest","crypto","bitcoin",
    ],
    TopicCategory.TECHNOLOGY: [
        "ai","อินเทอร์เน็ต","แอป","ซอฟต์แวร์","ไอที",
        "tech","software","app","cyber","hack","openai","chatgpt","robot",
    ],
    TopicCategory.CRIME: [
        "จับ","คดี","ฆ่า","ลักทรัพย์","ยาเสพติด","โจร","ตำรวจ",
        "arrest","murder","crime","fraud","scam","police","court","killed",
    ],
    TopicCategory.DISASTER: [
        "น้ำท่วม","แผ่นดินไหว","พายุ","ไฟไหม้","อุบัติเหตุ","ภัยพิบัติ",
        "flood","earthquake","storm","fire","accident","disaster","tsunami",
    ],
    TopicCategory.VIRAL: [
        "ไวรัล","ดัง","ฮิต","เทรนด์","กระแส","แชร์",
        "viral","trending","hot","challenge","meme","tiktok",
    ],
}

_RECENCY_WINDOW_HOURS = 24
_SIMILARITY_THRESHOLD = 75          # rapidfuzz score 0-100


def _classify(title: str) -> TopicCategory:
    title_lower = title.lower()
    for category, keywords in _CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in title_lower:
                return category
    return TopicCategory.OTHER


def _recency_score(published_at: datetime, now: datetime) -> float:
    """บทความใหม่ได้ score สูงกว่า (1.0 → 0.0 ภายใน 24 ชม.)"""
    age_hours = (now - published_at).total_seconds() / 3600
    if age_hours < 0:
        return 1.0
    return max(0.0, 1.0 - age_hours / _RECENCY_WINDOW_HOURS)


def _is_duplicate(a: TrendingTopic, b: TrendingTopic) -> bool:
    score = fuzz.token_sort_ratio(a.title, b.title)
    return score >= _SIMILARITY_THRESHOLD


class TopicRanker:
    """
    รวม topics จากหลายแหล่ง → deduplicate → score → คืน top-N
    """

    def __init__(self, top_n: int = 10):
        self._top_n = top_n

    def _deduplicate(self, topics: list[TrendingTopic]) -> list[TrendingTopic]:
        unique: list[TrendingTopic] = []
        for topic in topics:
            for seen in unique:
                if _is_duplicate(topic, seen):
                    # รวม score และ related_urls เข้าด้วยกัน
                    seen.score += topic.score * 0.5
                    seen.related_urls = list(set(seen.related_urls + topic.related_urls))[:5]
                    break
            else:
                unique.append(topic)
        return unique

    def _compute_final_score(
        self,
        topic: TrendingTopic,
        source_count: dict[str, int],
        now: datetime,
    ) -> float:
        recency = _recency_score(topic.published_at, now)
        # ถ้า topic นี้ถูกพูดถึงจากหลาย source ได้ bonus
        multi_source_bonus = source_count.get(topic.title.lower()[:20], 1) * 0.3
        return topic.score + recency * 5.0 + multi_source_bonus

    def rank(self, topics: list[TrendingTopic]) -> list[TrendingTopic]:
        now = datetime.now()

        # classify category ที่ยังไม่ได้ classify
        for t in topics:
            if t.category == TopicCategory.OTHER:
                t.category = _classify(t.title)

        # นับว่า title prefix เดียวกันมาจากกี่ source
        source_count: dict[str, int] = defaultdict(int)
        for t in topics:
            source_count[t.title.lower()[:20]] += 1

        # deduplicate
        unique = self._deduplicate(topics)

        # คำนวณ final score
        for t in unique:
            t.score = self._compute_final_score(t, source_count, now)

        # sort by score
        unique.sort(key=lambda t: t.score, reverse=True)

        return unique[: self._top_n]

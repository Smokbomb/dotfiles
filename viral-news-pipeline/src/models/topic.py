from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class TopicCategory(str, Enum):
    POLITICS = "การเมือง"
    ENTERTAINMENT = "บันเทิง"
    SPORTS = "กีฬา"
    INTERNATIONAL = "ต่างประเทศ"
    BUSINESS = "เศรษฐกิจ"
    CRIME = "อาชญากรรม"
    TECHNOLOGY = "เทคโนโลยี"
    DISASTER = "ภัยพิบัติ"
    VIRAL = "ไวรัล"
    OTHER = "อื่นๆ"


class NewsSource(str, Enum):
    GOOGLE_TRENDS_TH = "google_trends_th"
    GOOGLE_TRENDS_GLOBAL = "google_trends_global"
    THAIRATH = "thairath"
    KHAOSOD = "khaosod"
    SANOOK = "sanook"
    MANAGER = "manager"
    PRACHACHAT = "prachachat"
    BBC_THAI = "bbc_thai"
    BBC_WORLD = "bbc_world"
    REUTERS = "reuters"
    AP_NEWS = "ap_news"
    CNN = "cnn"


@dataclass
class TrendingTopic:
    title: str
    source: NewsSource
    url: str
    published_at: datetime
    score: float = 0.0                # engagement/trend score
    category: TopicCategory = TopicCategory.OTHER
    summary: Optional[str] = None
    image_url: Optional[str] = None
    language: str = "th"              # "th" or "en"
    keywords: list[str] = field(default_factory=list)
    related_urls: list[str] = field(default_factory=list)

    def __hash__(self):
        return hash(self.title.lower().strip())

    def __eq__(self, other):
        if not isinstance(other, TrendingTopic):
            return False
        return self.title.lower().strip() == other.title.lower().strip()

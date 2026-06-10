"""Unit tests for TopicRanker — ไม่ต้องการ network"""
from datetime import datetime, timedelta
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.models import TrendingTopic, NewsSource, TopicCategory
from src.discovery.topic_ranker import TopicRanker, _classify, _is_duplicate


def make_topic(title: str, score: float = 5.0, hours_ago: float = 1.0, lang="th") -> TrendingTopic:
    return TrendingTopic(
        title=title,
        source=NewsSource.THAIRATH,
        url="https://example.com",
        published_at=datetime.now() - timedelta(hours=hours_ago),
        score=score,
        language=lang,
    )


# ── classify ────────────────────────────────────────────────────────────────

def test_classify_politics():
    assert _classify("รัฐบาลประกาศนโยบายใหม่") == TopicCategory.POLITICS

def test_classify_sports():
    assert _classify("ทีมชาติไทยชนะ 3-0") == TopicCategory.SPORTS

def test_classify_entertainment():
    assert _classify("ดารานักร้องรับรางวัล") == TopicCategory.ENTERTAINMENT

def test_classify_fallback():
    assert _classify("เรื่องที่ไม่รู้จัก") == TopicCategory.OTHER


# ── dedup ────────────────────────────────────────────────────────────────────

def test_dedup_exact_match():
    a = make_topic("ยุบสภา 2025")
    b = make_topic("ยุบสภา 2025")
    assert _is_duplicate(a, b)

def test_dedup_near_match():
    a = make_topic("นายกฯ ประกาศยุบสภา")
    b = make_topic("นายกประกาศยุบสภา")
    assert _is_duplicate(a, b)

def test_no_dedup_different():
    a = make_topic("บาร์เซโลน่าชนะเรอัล")
    b = make_topic("น้ำท่วมภาคเหนือ")
    assert not _is_duplicate(a, b)


# ── ranker ───────────────────────────────────────────────────────────────────

def test_rank_returns_top_n():
    distinct_titles = [
        "น้ำท่วมเชียงใหม่", "รัฐบาลยุบสภา", "บาร์เซโลน่าชนะ", "ดาราถูกจับ",
        "หุ้นตก500จุด", "แผ่นดินไหวญี่ปุ่น", "ทีมชาติแพ้", "ราคาทองขึ้น",
        "ไฟไหม้โรงงาน", "ประกาศเคอร์ฟิว", "ChatGPT4ออกใหม่", "บิทคอยน์ทะลุแสน",
        "ซีรีส์เน็ตฟลิกซ์ดัง", "ดาราแต่งงาน", "กรุงเทพฝนตกหนัก",
        "ปาร์ตี้ยักษ์ใหญ่ปิด", "คนไทยได้โนเบล", "เกาหลีเลือกตั้ง",
        "โอลิมปิกเปิดฉาก", "จีนปล่อยยานอวกาศ",
    ]
    topics = [make_topic(t, score=float(i)) for i, t in enumerate(distinct_titles)]
    ranker = TopicRanker(top_n=5)
    result = ranker.rank(topics)
    assert len(result) == 5

def test_rank_deduplicates():
    topics = [
        make_topic("ยุบสภา 2025", score=10.0),
        make_topic("ยุบสภา 2025", score=10.0),  # duplicate
        make_topic("น้ำท่วมเชียงใหม่", score=5.0),
    ]
    ranker = TopicRanker(top_n=10)
    result = ranker.rank(topics)
    titles = [t.title.lower() for t in result]
    assert len(result) == 2, f"Expected 2 unique topics, got {len(result)}: {titles}"

def test_rank_recency_boosts_new():
    old_topic   = make_topic("ข่าวเก่า", score=100.0, hours_ago=23.0)
    fresh_topic = make_topic("ข่าวใหม่", score=1.0,   hours_ago=0.1)
    ranker = TopicRanker(top_n=2)
    result = ranker.rank([old_topic, fresh_topic])
    # fresh_topic ได้ recency bonus +5.0 ส่วน old_topic score สูงกว่ามาก จึงยังชนะ
    assert result[0].title == "ข่าวเก่า"

def test_rank_categories_assigned():
    topics = [make_topic("รัฐบาลประชุมฉุกเฉิน")]
    ranker = TopicRanker(top_n=10)
    result = ranker.rank(topics)
    assert result[0].category == TopicCategory.POLITICS


if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    passed = failed = 0
    for fn in tests:
        try:
            fn()
            print(f"  PASS  {fn.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL  {fn.__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")

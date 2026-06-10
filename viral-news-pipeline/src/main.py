"""
Entry point — ดึงข่าวดัง rank แล้วแสดงผล
Usage:
    python -m src.main
    python -m src.main --top 5
    python -m src.main --lang th
"""
import argparse
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich import box

from .discovery import (
    GoogleTrendsFetcher,
    ThaiRSSFetcher,
    InternationalRSSFetcher,
    TopicRanker,
)
from .models import TrendingTopic

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)
console = Console()


def fetch_all_topics(lang: str = "all") -> list[TrendingTopic]:
    all_topics: list[TrendingTopic] = []

    if lang in ("all", "th"):
        console.print("[cyan]Fetching Thai trends (Google)...[/]")
        gt = GoogleTrendsFetcher()
        all_topics.extend(gt.fetch_all_thai())

        console.print("[cyan]Fetching Thai news RSS...[/]")
        thai_rss = ThaiRSSFetcher()
        all_topics.extend(thai_rss.fetch_all())

    if lang in ("all", "en"):
        console.print("[cyan]Fetching global trends (Google)...[/]")
        gt = GoogleTrendsFetcher()
        all_topics.extend(gt.fetch_all_global())

        console.print("[cyan]Fetching international news RSS...[/]")
        intl_rss = InternationalRSSFetcher()
        all_topics.extend(intl_rss.fetch_all())

    return all_topics


def display_topics(topics: list[TrendingTopic]) -> None:
    table = Table(
        title=f"Top Trending Topics — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        box=box.ROUNDED,
        show_lines=True,
    )
    table.add_column("#",         style="bold white", width=3)
    table.add_column("Title",     style="bold yellow", max_width=55)
    table.add_column("Category",  style="magenta",    width=14)
    table.add_column("Source",    style="cyan",        width=18)
    table.add_column("Score",     style="green",       width=7, justify="right")
    table.add_column("Lang",      style="white",       width=5)
    table.add_column("Published", style="dim",         width=17)

    for i, t in enumerate(topics, 1):
        table.add_row(
            str(i),
            t.title[:55],
            t.category.value,
            t.source.value,
            f"{t.score:.1f}",
            t.language,
            t.published_at.strftime("%m-%d %H:%M"),
        )

    console.print(table)


def main():
    parser = argparse.ArgumentParser(description="Viral News Discovery")
    parser.add_argument("--top",  type=int, default=int(os.getenv("TOP_TOPICS_COUNT", "10")))
    parser.add_argument("--lang", choices=["all", "th", "en"], default="all")
    args = parser.parse_args()

    raw_topics = fetch_all_topics(lang=args.lang)
    console.print(f"[bold]Collected {len(raw_topics)} raw topics, ranking...[/bold]")

    ranker = TopicRanker(top_n=args.top)
    ranked = ranker.rank(raw_topics)

    display_topics(ranked)

    # คืน list เผื่อ layer ถัดไปเรียกใช้
    return ranked


if __name__ == "__main__":
    main()

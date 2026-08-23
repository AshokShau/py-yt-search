import asyncio
from py_yt import VideosSearch, HypeHint, close_session


async def main():
    """Demonstrates HYPE HINT momentum analytics and video ranking."""
    print("Searching for trending videos...")
    search = VideosSearch("space exploration", limit=5)
    result = await search.next()
    videos = result.get("result", [])

    print(f"\nAnalyzing HYPE HINT for {len(videos)} videos:\n")
    for video in videos:
        analysis = HypeHint.analyze_video(video)
        print(f"Title: {video.get('title')}")
        print(f"Views: {analysis['view_count']}")
        print(f"Hype Score: {analysis['score']} ({analysis['level']})")
        print(f"Velocity: {analysis['velocity_views_per_hour']} views/hr\n")

    ranked = HypeHint.rank(videos)
    if ranked:
        top = ranked[0]
        print(
            f"Top Hyped Video: '{top.get('title')}' with score {top.get('hype', {}).get('score')}"
        )

    await close_session()


if __name__ == "__main__":
    asyncio.run(main())

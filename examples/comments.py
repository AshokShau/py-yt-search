import asyncio
from py_yt import Comments, close_session


async def main():
    video_id = "dQw4w9WgXcQ"

    print("Basic Comments & Top-Level Pagination")
    comments = Comments(video_id)

    # Get page 1
    page = await comments.get()
    print(f"Fetched page 1 with {len(page.comments)} comments. Has more: {page.has_more}")

    for comment in page.comments[:3]:
        print(f"[{comment.author}] ({comment.published}): {comment.text}")
        print(f"  Likes: {comment.like_count} | Replies: {comment.reply_count}")

    # Fetch next page
    if page.has_more:
        page2 = await comments.next()
        print(f"\nFetched page 2 with {len(page2.comments)} comments.")

    print("\nComment Replies & Reply Pagination")
    if page.comments:
        target_comment = page.comments[0]
        print(f"Fetching replies for comment ID: {target_comment.id}")

        reply_paginator = await comments.replies(target_comment.id)
        reply_page = await reply_paginator.get()
        print(f"Fetched {len(reply_page.comments)} replies. Has more: {reply_page.has_more}")

        for reply in reply_page.comments[:3]:
            print(f"  ↳ [{reply.author}]: {reply.text}")

        while reply_page.has_more:
            reply_page = await reply_paginator.next()
            print(f"  Fetched next reply page with {len(reply_page.comments)} replies.")

    print("\nAsync Iteration over Comments")
    comments_iter = Comments(video_id)
    count = 0
    async for comment in comments_iter:
        count += 1
        print(f"#{count} [{comment.author}]: {comment.text[:50]}...")
        if count >= 10:
            break

    await close_session()


if __name__ == "__main__":
    asyncio.run(main())

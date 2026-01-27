import asyncio
from py_yt import VideosSearch

async def main():
    """
    Getting search results from the next pages on YouTube.
    Generally you'll get maximum of 20 videos in one search, for getting subsequent results, you may call `next` method.
    """
    print("--- Search Pagination ---")
    _search = VideosSearch("NoCopyrightSounds")
    index = 0
    """ Getting result on 1st page """
    result = await _search.next()
    """ Displaying the result """
    print("Page 1:")
    for video in result["result"]:
        index += 1
        print(f'{index} - {video["title"]}')
    
    """ Getting result on 2nd page """
    result = await _search.next()
    """ Displaying the result """
    print("\nPage 2:")
    for video in result["result"]:
        index += 1
        print(f'{index} - {video["title"]}')
    
    """ Getting result on 3rd page """
    result = await _search.next()
    """ Displaying the result """
    print("\nPage 3:")
    for video in result["result"]:
        index += 1
        print(f'{index} - {video["title"]}')

if __name__ == "__main__":
    asyncio.run(main())

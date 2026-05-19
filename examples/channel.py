import asyncio
from py_yt import Channel, close_session

async def main():
    """
    Getting channel information.
    """
    channel_info = await Channel.get("UC_aEa8K-EOJ3D6gOs7HcyNg")
    print(channel_info)

    """
    Using the Channel class to get playlists and paginating through them.
    """
    channel = Channel("UC_aEa8K-EOJ3D6gOs7HcyNg")
    await channel.init()
    
    print(f"Initial playlists loaded: {len(channel.result.get('playlists', []))}")
    
    while channel.has_more_playlists():
        await channel.next()
        print(f"Playlists loaded after next(): {len(channel.result.get('playlists', []))}")

    await close_session()

if __name__ == "__main__":
    asyncio.run(main())
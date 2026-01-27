import asyncio
from py_yt import Channel

async def main():
    print("--- Channel Info ---")
    print(await Channel.get("UC_aEa8K-EOJ3D6gOs7HcyNg"))

if __name__ == "__main__":
    asyncio.run(main())

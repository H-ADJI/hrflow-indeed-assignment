import asyncio

from src.crawling import JobIndexing


async def main():
    async with JobIndexing(
        is_headless=True,
        conccurent_scraper_count=5,
        data_buffer_size=25,
    ) as j_indexer:
        await j_indexer.run()


if __name__ == "__main__":
    asyncio.run(main=main())

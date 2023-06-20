import asyncio

from src.crawling import JobIndexing


async def main():
    async with JobIndexing(
        is_headless=False,
        search_location="United Kingdom",
        conccurent_scraper_count=2,
        data_buffer_size=30,
    ) as j_indexer:
        await j_indexer.run()


if __name__ == "__main__":
    asyncio.run(main=main())

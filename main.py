import asyncio

from src.crawling import JobIndexing


async def main():
    j_indexer: JobIndexing
    async with JobIndexing(is_headless=True,
        search_location="United Kingdom", conccurent_scraper_count=3, data_buffer_size=60
    ) as j_indexer:
        await j_indexer.run()


if __name__ == "__main__":
    asyncio.run(main=main())

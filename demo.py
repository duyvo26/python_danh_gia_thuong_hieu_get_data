# # https://www.google.com/search?q=%22{name_thuong_hieu}%22 after:{start_date_thuong_hieu} before:{end_date_thuong_hieu}&hl=vi&tbm=nws


# import asyncio
# from crawl4ai import *

# url = f"https://www.google.com/search?q='tra hoa sam vo dung' after:2024-08-01 before:2024-08-03"


# async def main():
#     async with AsyncWebCrawler() as crawler:
#         result = await crawler.arun(
#             url=url,
#         )
#         print(result.markdown)


# if __name__ == "__main__":
#     asyncio.run(main())


import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonXPathExtractionStrategy
from crawl4ai.async_configs import BrowserConfig, ProxyConfig


async def main():


    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="http://www.acecookvietnam.vn/",
        )
        print(result.markdown)


if __name__ == "__main__":
    asyncio.run(main())

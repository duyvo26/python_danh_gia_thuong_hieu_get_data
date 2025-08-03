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
    browser_config = BrowserConfig(
        proxy_config=ProxyConfig(
            server="http://42.96.10.198:8194",
            username="CINE66Q4duyvo",
            password="P7qWPJTd"
        ),
        headless=True,
)


    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url="https://vuonsamvodung.com",
        )
        print(result.markdown)


if __name__ == "__main__":
    asyncio.run(main())

# https://www.google.com/search?q=%22{name_thuong_hieu}%22 after:{start_date_thuong_hieu} before:{end_date_thuong_hieu}&hl=vi&tbm=nws


import asyncio
from crawl4ai import *

url = f"https://www.google.com/search?q=tr%C3%A0%20hoa%20nh%C3%A2n%20s%C3%A2m%20v%C3%B5%20d%C5%A9ng&hl=vi"

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url=url,
        )
        print(result.markdown)


if __name__ == "__main__":
    asyncio.run(main())
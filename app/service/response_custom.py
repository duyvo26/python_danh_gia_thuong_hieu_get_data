import requests
import asyncio
from crawl4ai import *  # noqa: F403
import aiofiles
import time
from urllib.parse import urlparse
from app.config import settings
import os
from bs4 import BeautifulSoup


def check_captcha(html):
    if "/recaptcha/".lower() in html.lower():
        return False
    if 'id="captcha-form"'.lower() in html.lower():
        return False
    if "https://www.google.com/recaptcha/api.js".lower() in html.lower():
        return False
    return True




import os

PROXY_FILE_PATH = "proxy_index.txt"


def read_proxy_index():
    try:
        with open(PROXY_FILE_PATH, "r") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0  # Mặc định là 0 nếu chưa có file


def write_proxy_index(index):
    with open(PROXY_FILE_PATH, "w") as f:
        f.write(str(index))


def get_proxy_config_from_env():
    index = read_proxy_index()
    next_index = (index + 1) % 2  # Giả sử có 2 proxy, bạn có thể mở rộng nếu có nhiều hơn

    # Lưu lại index cho lần gọi tiếp theo
    write_proxy_index(next_index)

    # Đọc thông tin từ biến môi trường
    prefix = "" if index == 0 else f"_{index}"
    proxy = {
        "username": os.getenv(f"PROXY_USERNAME{prefix}"),
        "password": os.getenv(f"PROXY_PASSWORD{prefix}"),
        "host": os.getenv(f"PROXY_HOST{prefix}"),
        "port": os.getenv(f"PROXY_PORT{prefix}"),
    }

    return ProxyConfig(  # noqa: F405
        server=f"http://{proxy['host']}:{proxy['port']}",
        username=proxy["username"],
        password=proxy["password"],
    )
    
    
async def crawl4ai_run_proxy(url, proxy=False):
    print(f"Đang dùng proxy")  # noqa: F541

    proxy_config = get_proxy_config_from_env()

    browser_config = BrowserConfig(  # noqa: F405
        proxy_config=proxy_config,
        headless=True,
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:  # noqa: F405
        result = await crawler.arun(
            url=url,
            config=CrawlerRunConfig(  # noqa: F405
                cache_mode=CacheMode.BYPASS  # noqa: F405
            ),
        )

        markdown_content = result.markdown
        html_content = result.html  # 👈 Phải có html mới parse meta được!

        meta = extract_meta(html_content)

        # Tạo tên file động
        timestamp = int(time.time())
        domain = urlparse(url).netloc.replace(".", "_")
        filename = f"{domain}_{timestamp}.md"
        path_file = os.path.join(settings.DIR_ROOT, "utils", "web", filename)

        async with aiofiles.open(path_file, mode="w", encoding="utf-8") as f:
            await f.write(markdown_content)

        return {
            "markdown": markdown_content,
            "meta": meta,
        }


async def crawl4ai_run(url):
    async with AsyncWebCrawler() as crawler:  # noqa: F405
        result = await crawler.arun(
            url=url,
            config=CrawlerRunConfig(  # noqa: F405
                cache_mode=CacheMode.BYPASS  # noqa: F405
            ),
        )

        markdown_content = result.markdown
        html_content = result.html

        meta = extract_meta(html_content)

        # Tạo tên file động
        timestamp = int(time.time())
        domain = urlparse(url).netloc.replace(".", "_")
        filename = f"{domain}_{timestamp}.md"
        path_file = os.path.join(settings.DIR_ROOT, "utils", "web", filename)

        async with aiofiles.open(path_file, mode="w", encoding="utf-8") as f:
            await f.write(markdown_content)

        return {
            "markdown": markdown_content,
            "meta": meta,
        }


def extract_meta(html):
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string.strip() if soup.title else ""
    description = ""
    keywords = ""

    desc_tag = soup.find("meta", attrs={"name": "description"})
    if desc_tag:
        description = desc_tag.get("content", "")

    keywords_tag = soup.find("meta", attrs={"name": "keywords"})
    if keywords_tag:
        keywords = keywords_tag.get("content", "")

    return {
        "title": title,
        "description": description,
        "keywords": keywords,
    }


def response_custom(url, proxy=False):
    try:
        if proxy:
            crawl_result = asyncio.run(crawl4ai_run_proxy(url))
        else:
            crawl_result = asyncio.run(crawl4ai_run(url))
        return crawl_result
    except Exception as e:
        print(f"Lỗi khi gửi yêu cầu: {e}")
        return None

import requests


def check_captcha(html):
    if "/recaptcha/".lower() in html.lower():
        return False
    if 'id="captcha-form"'.lower() in html.lower():
        return False
    if "https://www.google.com/recaptcha/api.js".lower() in html.lower():
        return False
    return True


# def response_custom(url):
#     url_api = "http://localhost:8000/base/get-html/"  # URL của API
#     api_key = "T0wq2yjazJmln2BRAFTysWNsp7PcZGyAPIMF7i7EWeEniAYv9GbZC81thedolHGu"  # Thay thế bằng API key của bạn

#     # Tạo payload cho request
#     data = {"url": url}
#     headers = {"API-Key": api_key}
#     # Gửi request POST tới API
#     response = requests.post(url_api, data=data, headers=headers, timeout=120)
#     # Kiểm tra kết quả
#     if response.status_code == 200:
#         result = response.json()
#         print(result["status_code"] == 200, result["status_code"])
#         if result["status_code"] == 200:
#             # Tạo một response giả để trả kết quả đúng định dạng
#             if check_captcha(result["html"]) is True:
#                 return result["html"]
#             return None
#         else:
#             return None


import asyncio
from crawl4ai import *  # noqa: F403
import aiofiles
import time
from urllib.parse import urlparse
from app.config import settings
import os


def get_proxy_config_from_env():
    return ProxyConfig(  # noqa: F405
        server=f"http://{os.getenv('PROXY_HOST')}:{os.getenv('PROXY_PORT')}",
        username=os.getenv("PROXY_USERNAME"),
        password=os.getenv("PROXY_PASSWORD"),
    )


async def crawl4ai_run(url, proxy=False):
    if proxy:
        print(f"Đang dùng proxy")  # noqa: F541

        proxy_config = get_proxy_config_from_env()

        browser_config = BrowserConfig(  # noqa: F405
            proxy_config=proxy_config,
            headless=True,  # Thêm nếu bạn muốn chạy headless như bên `main`
        )
    else:
        browser_config = BrowserConfig(  # noqa: F405
            headless=True,  # Thêm nếu bạn muốn chạy headless như bên `main`
        )

    async with AsyncWebCrawler(config=browser_config) as crawler:  # noqa: F405
        result = await crawler.arun(
            url=url,
            config=CrawlerRunConfig(  # noqa: F405
                cache_mode=CacheMode.BYPASS  # noqa: F405
            ),
        )
        markdown_content = result.markdown

        # Tạo tên file động
        timestamp = int(time.time())
        domain = urlparse(url).netloc.replace(".", "_")
        filename = f"{domain}_{timestamp}.md"
        path_file = os.path.join(settings.DIR_ROOT, "utils", "web", filename)

        async with aiofiles.open(path_file, mode="w", encoding="utf-8") as f:
            await f.write(markdown_content)

        return markdown_content


def response_custom(url, proxy=False):
    try:
        # Gọi crawl4ai_run từ def
        crawl_result = asyncio.run(crawl4ai_run(url, proxy))
        return crawl_result
    except requests.RequestException as e:
        print(f"Lỗi khi gửi yêu cầu: {e}")
        return None


# def response_custom(url):
#     try:
#         r = requests.get(url, timeout=10)  # Thêm timeout để tránh treo chương trình
#         r.raise_for_status()  # Kiểm tra lỗi HTTP
#         return r.text
#     except requests.RequestException as e:  # Bắt các lỗi liên quan đến HTTP
#         print(f"Lỗi khi gửi yêu cầu: {e}")
#         return None

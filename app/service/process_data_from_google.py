import re

# import html
from app.model.db_danh_gia_thuong_hieu import (
    get_request_thuong_hieu_list_end,
    get_brand_name,
    insert_data_thuong_hieu,
    update_request_thuong_hieu_list_end,
    check_list_google_end,
    get_number_thuong_hieu,
)
from bs4 import BeautifulSoup

# from bs4.element import Comment
from app.utils.compare_titles import CompareTitles
from app.config import settings
import time
import os
from app.service.response_custom import response_custom as _response_custom

# import requests
import traceback

from concurrent.futures import ThreadPoolExecutor, as_completed

import openai


def kiem_tra_tieu_de_giong_van_de(ten_van_de: str, tieu_de: str) -> bool:
    openai.api_key = os.environ["KEY_API_OPENAI"]

    response = openai.ChatCompletion.create(
        model=os.environ["OPENAI_LLM_MODEL_NAME"],
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "Bạn là một trợ lý AI. Nhiệm vụ của bạn là kiểm tra xem tiêu đề có đang nói về  thương hiệu đó không. "
                    "Chỉ trả lời đúng một từ 'true' hoặc 'false', không thêm giải thích."
                ),
            },
            {"role": "user", "content": f"Tên thương hiệu: {ten_van_de}\nTiêu đề bài viết: {tieu_de}"},
        ],
    )
    return response["choices"][0]["message"]["content"].strip().lower() == "true"


class ProcessDataFromGoogle:
    def __init__(self):
        pass

    def handle_url(self, url, brand_name, id_rq, _id_rq, search_timeline):
        try:
            print(f"----------------{get_number_thuong_hieu(_id_rq)}-------------------")
            # print(url)
            data_web = self.response_custom(url)
            if data_web != 404:
                percent_same = CompareTitles().compare_text(brand_name, data_web["meta"]["title"])
                if "images (" in data_web["meta"]["title"]:
                    return
                print(data_web["meta"]["title"], "|", brand_name)
                llm_check_title = kiem_tra_tieu_de_giong_van_de(brand_name, data_web["meta"]["title"])

                print("---llm_check_title---", llm_check_title)
                print("percent_same", percent_same)

                if (
                    (llm_check_title)
                    or (int(percent_same) > int(settings.BRAND_SIMILARITY_PERCENTAGE))
                    or (brand_name in data_web["meta"]["title"])
                ):
                    insert_data_thuong_hieu(
                        id_rq=str(id_rq),
                        title=data_web["meta"]["title"],
                        keyword=data_web["meta"]["keywords"],
                        page_content=url,
                        docs=str(data_web),
                        search_timeline=str(search_timeline),
                    )
        except Exception as e:
            print(f"Lỗi xử lý URL {url}: {e}")

    def run(self):
        _id_rq_list = check_list_google_end()

        for _id_rq in _id_rq_list:
            list_data = get_request_thuong_hieu_list_end(_id_rq)
            for i in list_data:
                try:
                    id_rq_list = i[0]
                    id_rq = i[1]
                    html_page = i[2]
                    brand_name = get_brand_name(i[1])[0][4]
                    start_date_thuong_hieu = i[3]
                    end_date_thuong_hieu = i[4]
                    # print("id_rq_list", id_rq_list)
                    search_timeline = {
                        "start_date_thuong_hieu": str(start_date_thuong_hieu),
                        "end_date_thuong_hieu": str(end_date_thuong_hieu),
                    }
                    print(f"----------------{get_number_thuong_hieu(_id_rq)}-------------------")
                    urls = self.extract_urls_from_parentheses(html_page)
                    # print("urls", len(urls))
                    _urls = []
                    for url_ in urls:
                        try:
                            url_ = self.extract_url(url_)
                            if url_ is None:
                                continue
                            if (
                                "google." not in url_
                                and "facebook.com" not in url_
                                and "youtube.com" not in url_
                                and "youtu.be" not in url_
                                and "tiktok." not in url_
                                and "topcv." not in url_
                                and self.is_valid_url(url_) is not None
                            ):
                                _urls.append(url_)
                        except Exception as e:
                            print("ProcessDataFromGoogle: run for 0", e)
                            traceback.print_exc()  # In chi tiết lỗi

                    with ThreadPoolExecutor(max_workers=4) as executor:
                        futures = [executor.submit(self.handle_url, url, brand_name, id_rq, _id_rq, search_timeline) for url in _urls]
                        for future in as_completed(futures):
                            future.result()  # bắt lỗi nếu có

                except Exception as e:
                    print("EX", e)
                    [time.sleep(1) or print("Null data:", _time) for _time in range(0, 5)]
                    self.run()

                update_request_thuong_hieu_list_end(id_rq_list, 2)
                print("no_record_found_with_id_rq_list")

            [time.sleep(1) or print("Null data:", _time) for _time in range(0, 10)]
            self.run()

    def parse(self, content, url):
        """Phân tích nội dung và trích xuất thông tin."""

        soup = BeautifulSoup(content, "html.parser")

        # Trích xuất tiêu đề
        title = soup.find("title").text.strip() if soup.find("title") else "Không tìm thấy tiêu đề"

        # Trích xuất meta description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        description = meta_desc["content"].strip() if meta_desc else "Không tìm thấy meta description"

        # Trích xuất meta keywords
        meta_keywords = soup.find("meta", attrs={"name": "keywords"})
        keywords = meta_keywords["content"].strip() if meta_keywords else "Không tìm thấy meta keywords"

        # Trích xuất nội dung trong body
        body = soup.find("body").get_text(separator="\n", strip=True) if soup.find("body") else "Không tìm thấy nội dung"

        return {
            "title": title,
            "description": description,
            "keywords": keywords,
            "body": (body),
            "url": url,
        }

    def response_custom(self, url):
        try:
            return _response_custom(url)
        except Exception as _:
            return None

    def is_valid_url(self, url):
        # Regular expression for validating URLs
        regex = re.compile(
            r"^(?:http|ftp)s?://"  # http:// or https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.))"  # domain...
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )

        # If the URL matches the regular expression, return True
        return re.match(regex, url) is not None

    def extract_url(self, input_string):
        if input_string is None:
            return None
        if "http" in input_string or "https" in input_string:
            # Tìm kiếm URL bắt đầu từ http hoặc https
            match = re.search(r"https?://[^\s]+", input_string)
            if match:
                return match.group(0)
            return None
        return None

    def count_urls_from_markdown_content(self, content):
        # Regex tìm URL (http hoặc https)
        urls = re.findall(r"(https?://[^\s\)]+)", content)
        url_count = len(urls)
        return url_count

    def extract_urls_from_parentheses(self, markdown_content: str) -> list:
        """
        Bắt TẤT CẢ URL nằm trong dấu ngoặc đơn (), bất kể cú pháp markdown.
        """
        import re

        pattern = r"\((https?://[^\)]+)\)"
        urls = re.findall(pattern, markdown_content)

        # Các đuôi file cần loại
        file_exts = (
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".svg",
            ".webp",
            ".bmp",
            ".ico",
            ".pdf",
            ".doc",
            ".docx",
            ".ppt",
            ".pptx",
            ".xls",
            ".xlsx",
            ".zip",
            ".rar",
            ".7z",
            ".tar",
            ".gz",
            ".mp3",
            ".wav",
            ".mp4",
            ".avi",
            ".mov",
            ".css",
            ".js",
            ".json",
            ".xml",
        )

        urls_web = [url for url in urls if not url.lower().split("?")[0].endswith(file_exts)]
        return urls_web

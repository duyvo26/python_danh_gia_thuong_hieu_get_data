import re

# import html
from app.model.db_danh_gia_thuong_hieu import (
    get_request_thuong_hieu_list_end,
    get_brand_name,
    insert_data_thuong_hieu,
    update_request_thuong_hieu_list_end,
    check_id_thuong_hieu_run,
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


class ProcessDataFromGoogle:
    def __init__(self):
        pass

    def run(self):
        _id_rq_list = check_id_thuong_hieu_run()
        # print("_id_rq_list", _id_rq_list)

        for _id_rq in _id_rq_list:
            # print("_id_rq", _id_rq)

            list_data = get_request_thuong_hieu_list_end(_id_rq)
            # print("list_data", list_data)
            # print("len", len(list_data))
            for i in list_data:
                try:
                    id_rq_list = i[0]
                    id_rq = i[1]
                    html_page = i[2]
                    brand_name = get_brand_name(i[1])[0][4]
                    start_date_thuong_hieu = i[3]
                    end_date_thuong_hieu = i[4]

                    print("id_rq_list", id_rq_list)
                    search_timeline = {
                        "start_date_thuong_hieu": str(start_date_thuong_hieu),
                        "end_date_thuong_hieu": str(end_date_thuong_hieu),
                    }

                    print(f"----------------{get_number_thuong_hieu(_id_rq)}-------------------")

                    if get_number_thuong_hieu(_id_rq) >= int(os.environ["MAX_PAGE"]):
                        update_request_thuong_hieu_list_end(id_rq_list, 2)
                        break

                    urls = self.extract_urls_from_parentheses(html_page)

                    print("urls", len(urls))
                    # print("urls", (urls))

                    _urls = []
                    for url_ in urls:
                        try:
                            url_ = self.extract_url(url_)
                            # print("extract_url", url_)

                            if url_ is None:
                                continue

                            # Bỏ qua link Google, Facebook, YouTube
                            if (
                                "google." not in url_
                                and "facebook.com" not in url_
                                and "youtube.com" not in url_
                                and "youtu.be" not in url_
                                and "tiktok." not in url_
                                and self.is_valid_url(url_) is not None
                            ):
                                _urls.append(url_)
                        except Exception as e:
                            print("ProcessDataFromGoogle: run for 0", e)
                            traceback.print_exc()  # In chi tiết lỗi

                    print("LEN URL", len(_urls))
                    # print("URL", (_urls))

                    # time.sleep(9999)
                    for url in _urls:
                        try:
                            print(f"----------------{get_number_thuong_hieu(_id_rq)}-------------------")
                            if get_number_thuong_hieu(_id_rq) >= int(os.environ["MAX_PAGE"]):
                                update_request_thuong_hieu_list_end(id_rq_list, 2)
                                break

                            print(url)
                            data_web = self.response_custom(url)

                            # print("data_web", data_web)
                            if data_web != 404:
                                percent_same = CompareTitles().compare_text(brand_name, data_web["meta"]["title"])
                                # percent_same_full = CompareTitles().compare_text(brand_name, data_web[2])
                                print("percent_same", percent_same)
                                print(data_web["meta"]["title"], "|", brand_name)
                                # print("percent_same_full", percent_same_full)

                                if int(percent_same) > int(settings.BRAND_SIMILARITY_PERCENTAGE):
                                    # time.sleep(99999)

                                    insert_data_thuong_hieu(
                                        id_rq=str(id_rq),
                                        title=data_web["meta"]["title"],
                                        keyword=data_web["meta"]["keywords"],
                                        page_content=url,
                                        docs=str(data_web),
                                        search_timeline=str(search_timeline),
                                    )

                        except Exception as e:
                            print("ProcessDataFromGoogle: run for 1", e)
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

import re
import html
from app.model.db_danh_gia_thuong_hieu import (
    get_request_thuong_hieu_list_end,
    get_brand_name,
    insert_data_thuong_hieu,
    update_request_thuong_hieu_list_end,
)
from bs4 import BeautifulSoup
from bs4.element import Comment
from app.utils.compare_titles import CompareTitles
from app.config import settings
import time
from app.service.response_custom import response_custom as _response_custom
import requests


class ProcessDataFromGoogle:
    def __init__(self):
        pass

    def extract_url(self, input_str):
        # Sử dụng regular expression để tìm URL
        match = re.search(r"url\?q=(https?://[^\s&]+)", input_str)
        if match:
            return match.group(1)  # Trả về URL
        return None  # Nếu không tìm thấy URL

    def run(self):
        list_data = get_request_thuong_hieu_list_end()
        print("len", len(list_data))
        for i in list_data:
            try:
                id_rq_list = i[0]
                id_rq = i[1]
                html_page = i[2]
                brand_name = get_brand_name(i[1])[0][4]
                start_date_thuong_hieu = i[3]
                end_date_thuong_hieu = i[4]

                print("id_rq_list", id_rq_list)
                print("id_rq", id_rq)
                # print("html_page", html_page)
                print("brand_name", brand_name)
                print("start_date_thuong_hieu", start_date_thuong_hieu)
                print("end_date_thuong_hieu", end_date_thuong_hieu)

                search_timeline = {
                    "start_date_thuong_hieu": str(start_date_thuong_hieu),
                    "end_date_thuong_hieu": str(end_date_thuong_hieu),
                }

                google_html = html.unescape(str(html_page))
                soup = BeautifulSoup(google_html, "html.parser")

                urls = list(set([self.extract_url(a.get("href")) for a in soup.find_all("a", href=True)]))

                print("_urls", urls)

                _urls = []
                for url_ in urls:
                    try:
                        if "google." not in url_ and self.is_valid_url(url_):
                            _urls.append(url_)

                    except Exception as e:
                        print("ProcessDataFromGoogle: run for 0", e)

                print("_urls", _urls)

                for url in _urls:
                    try:
                        print(url)
                        data_web = self.get_html_page(url)
                        # print("data_web", data_web)
                        if data_web != 404:
                            percent_same = CompareTitles().compare_text(brand_name, data_web[0])
                            percent_same_full = CompareTitles().compare_text(brand_name, data_web[2])
                            print("percent_same", percent_same)
                            print("percent_same_full", percent_same_full)

                            if int(percent_same) > int(settings.BRAND_SIMILARITY_PERCENTAGE) or int(percent_same_full) > int(
                                settings.BRAND_SIMILARITY_PERCENTAGE
                            ):
                                insert_data_thuong_hieu(
                                    id_rq=str(id_rq),
                                    title=str(data_web[0]),
                                    keyword=str(brand_name),
                                    page_content=str(data_web[1]),
                                    docs=str(data_web[2]),
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

    def get_html_page(self, url):
        try:

            def replace_newlines(input_string):
                return input_string.replace("\n", r"\n")

            def tag_visible(element):
                if element.parent.name in ["style", "script", "head", "title", "meta", "[document]"]:
                    return False
                if isinstance(element, Comment):
                    return False
                return True

            def text_from_html(soup):
                texts = soup.findAll(text=True)
                visible_texts = filter(tag_visible, texts)
                string_ = " ".join(t.strip() for t in visible_texts)
                return replace_newlines(string_)

            _response = self.response_custom(url)
            if _response is not None:
                soup = BeautifulSoup(_response, "html.parser")
                title = soup.find("title")
                if title:
                    title = title.string
                    print("title", title)

                    page_content = text_from_html(soup)
                    docs = self.parse(_response, url)
                    return (title), (page_content), str(docs)

            return 404
        except Exception as e:
            print("ProcessDataFromGoogle: get_html_page", e)
            return 404

    def response_custom(self, url):
        # Chọn ngẫu nhiên User-Agent
        # return _response_custom(url)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        }
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                return response.text
            return None
        except Exception as e:
            print("ProcessDataFromGoogle: response_custom", e)
            return 404

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

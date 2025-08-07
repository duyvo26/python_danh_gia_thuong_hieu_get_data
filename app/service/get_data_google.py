import time
from datetime import datetime

# from app.service.reset_wifi import reset_wifi
import threading

# import html
from app.model.db_danh_gia_thuong_hieu import get_request_thuong_hieu_list, update_request_thuong_hieu_list

# from bs4 import BeautifulSoup
# from app.utils import sanitize_for_mysql
from app.service.response_custom import response_custom as _response_custom
import re
# from requests import get
# from app.utils import check_ip
# import re


class GetDataGoogle:
    def __init__(self):
        pass

    def response_custom(self, url):
        try:
            return _response_custom(url, True)
        except Exception as _:
            return None

    def run(self, number=0, max_number=30):
        try:
            list_data = get_request_thuong_hieu_list()
            for data in list_data:
                id_rq_list = data[0]
                start_date_thuong_hieu = data[2].strftime("%Y-%m-%d") if isinstance(data[2], datetime) else str(data[2])
                end_date_thuong_hieu = data[3].strftime("%Y-%m-%d") if isinstance(data[3], datetime) else str(data[3])
                name_thuong_hieu = data[8].lower()
                url_thuong_hieu = f"https://www.google.com/search?q=%22{name_thuong_hieu}%22 after:{start_date_thuong_hieu} before:{end_date_thuong_hieu}&hl=vi&gl=vn&lr=lang_vi"
                _response = self.response_custom(url_thuong_hieu)
                if (
                    "https://support.google.com/websearch/answer/86640" in _response["markdown"]
                    or "Địa chỉ IP:" in _response["markdown"]
                    or "(https://www.google.com/policies/terms/)" in _response["markdown"]
                    or "CAPTCHA" in _response["markdown"]
                ):
                    print("ERR CAPTCHA")
                    return 0

                threading.Thread(
                    target=self.update_data,
                    args=(
                        _response["markdown"],
                        id_rq_list,
                    ),
                ).start()

                number += 1
                [time.sleep(1) or print("sleep:", _time) for _time in range(0, 5)]
        except Exception as _:
            print("********************************")
            print("get_data_google: 404")
            print("********************************")

    def count_urls_from_markdown_content(self, content):
        # Regex tìm URL (http hoặc https)
        urls = re.findall(r"(https?://[^\s\)]+)", content)
        url_count = len(urls)
        return url_count

    def update_data(self, _response, id_rq_list):
        _urls = self.count_urls_from_markdown_content(_response)
        if _urls < 1:
            return 0
        threading.Thread(
            target=update_request_thuong_hieu_list,
            args=(
                id_rq_list,
                str(_response),
                1,
            ),
        ).start()

    def is_valid_url(self, url):
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
        if "http" in input_string or "https" in input_string:
            # Tìm kiếm URL bắt đầu từ http hoặc https
            match = re.search(r"https?://[^\s]+", input_string)
            if match:
                return match.group(0)
            return None
        return None

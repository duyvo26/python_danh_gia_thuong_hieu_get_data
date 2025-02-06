import time
from datetime import datetime
from app.service.reset_wifi import reset_wifi
import threading
import html
from app.model.db_danh_gia_thuong_hieu import get_request_thuong_hieu_list, update_request_thuong_hieu_list
from bs4 import BeautifulSoup
from app.utils import sanitize_for_mysql
from app.service.response_custom import response_custom as _response_custom
import re
from requests import get
import requests


class GetDataGoogle:
    def __init__(self):
        pass

    def get_ip(self):
        ip = get("https://api.ipify.org").content.decode("utf8")
        return ip

    def response_custom(self, url):
        try:
            return _response_custom(url)
        except Exception as _:
            return None

    def reload_usb(self):
        print("-reload_usb-")

        # ip_old = self.get_ip()

        # # threading.Thread(reset_wifi()).start()
        self.check_ip()
        [time.sleep(1) or print("reload usb:", _time) for _time in range(0, 10)]
        self.check_ip()

        # ip_now = self.get_ip()

        # if ip_now == ip_old:
        #     print("-IP EQUALS-", ip_now, ip_old)
        #     self.reload_usb()

        self.run(number=0, max_number=30)

    def check_ip(self):
        # Đảm bảo bạn đã cài PySocks: pip install PySocks
        proxies = {"http": "socks5h://192.168.1.25:1080", "https": "socks5h://192.168.1.25:1080"}

        response = requests.get("https://api.ipify.org", proxies=proxies)
        print("ip proxy", response.text)
        response = requests.get("https://api.ipify.org")
        print("ip main", response.text)

    def run(self, number=0, max_number=30):
        try:
            list_data = get_request_thuong_hieu_list()
            for data in list_data:
                id_rq_list = data[0]
                start_date_thuong_hieu = data[9].strftime("%Y-%m-%d") if isinstance(data[9], datetime) else str(data[9])
                end_date_thuong_hieu = data[10].strftime("%Y-%m-%d") if isinstance(data[10], datetime) else str(data[10])
                name_thuong_hieu = data[8].lower()

                url_thuong_hieu = f"https://www.google.com/search?q=%22{name_thuong_hieu}%22 after:{start_date_thuong_hieu} before:{end_date_thuong_hieu}&hl=vi"
                print("url: ", url_thuong_hieu)
                print(__import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                _response = self.response_custom(url_thuong_hieu)

                if _response is None:
                    print("_response None")
                    self.reload_usb()

                if ">Tất cả".lower() not in _response.lower():
                    print("check tat ca fail")
                    self.reload_usb()

                # soup = BeautifulSoup(_response, "html.parser")

                # urls = list(set([a.get("href") for a in soup.find_all("a", href=True)]))

                # _urls = []
                # for url_ in urls:
                #     try:
                #         url_ = self.extract_url(url_)
                #         if url_ is None:
                #             continue
                #         if "google." not in url_ and self.is_valid_url(url_):
                #             _urls.append(url_)

                #     except Exception as e:
                #         print("ProcessDataFromGoogle: run for 0", e)

                # print("Number urls", len(_urls))

                # google_html = html.escape(str(soup))
                # print("********************************")
                # print("get_data_google: 200")
                # print(__import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                # print("-------------------------")
                # threading.Thread(
                #     target=update_request_thuong_hieu_list,
                #     args=(
                #         id_rq_list,
                #         str(sanitize_for_mysql(google_html)),
                #         1,
                #     ),
                # ).start()

                threading.Thread(
                    target=self.update_data,
                    args=(
                        _response,
                        id_rq_list,
                    ),
                ).start()

                number += 1

            [time.sleep(1) or print("Null data:", _time) for _time in range(0, 10)]

            self.run(number=0, max_number=30)

        except Exception as _:
            print(_)
            print("********************************")
            print("get_data_google: 404")
            print("-------------------------")
            self.reload_usb()

    def update_data(self, _response, id_rq_list):
        soup = BeautifulSoup(_response, "html.parser")

        urls = list(set([a.get("href") for a in soup.find_all("a", href=True)]))

        _urls = []
        for url_ in urls:
            try:
                url_ = self.extract_url(url_)
                if url_ is None:
                    continue
                if "google." not in url_ and self.is_valid_url(url_):
                    _urls.append(url_)

            except Exception as _:
                continue

        print("Number urls", len(_urls))

        google_html = html.escape(str(soup))
        print("********************************")
        print("get_data_google: 200")
        self.check_ip()
        print(__import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("-------------------------")

        threading.Thread(
            target=update_request_thuong_hieu_list,
            args=(
                id_rq_list,
                str(sanitize_for_mysql(google_html)),
                1,
            ),
        ).start()

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
        if "http" in input_string or "https" in input_string:
            # Tìm kiếm URL bắt đầu từ http hoặc https
            match = re.search(r"https?://[^\s]+", input_string)
            if match:
                return match.group(0)
            return None
        return None

import time
from datetime import datetime
from app.service.reset_wifi import reset_wifi
import threading
import requests  # type: ignore
import html
from app.model.db_danh_gia_thuong_hieu import get_request_thuong_hieu_list, update_request_thuong_hieu_list
from bs4 import BeautifulSoup
from app.utils import sanitize_for_mysql


class GetDataGoogle:
    def __init__(self):
        pass

    def response_custom(self, url):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        }
        response = requests.get(url, headers=headers, timeout=2)

        return response

    def reload_usb(self):
        threading.Thread(reset_wifi()).start()

        [time.sleep(1) or print("reload usb:", _time) for _time in range(0, 30)]

        self.run(number=0, max_number=30)

    def run(self, number=0, max_number=30):
        try:
            list_data = get_request_thuong_hieu_list()
            for data in list_data:
                # url = "https://www.google.com/search?q"
                # _response = response_custom(url)
                # if _response.status_code != 200 or (number > max_number):
                #     reload_usb()

                id_rq_list = data[0]
                start_date_thuong_hieu = data[9].strftime("%Y-%m-%d") if isinstance(data[9], datetime) else str(data[9])
                end_date_thuong_hieu = data[10].strftime("%Y-%m-%d") if isinstance(data[10], datetime) else str(data[10])
                name_thuong_hieu = data[8].lower()
                print("len data", len(list_data))
                print("name_thuong_hieu", name_thuong_hieu)
                url_thuong_hieu = f"https://www.google.com/search?q=%22{name_thuong_hieu}%22 after:{start_date_thuong_hieu} before:{end_date_thuong_hieu} lang:vi&hl=vi"
                print("url: ", url_thuong_hieu)

                _response = self.response_custom(url_thuong_hieu)

                if _response.status_code != 200 or (number > max_number):
                    self.reload_usb()

                _response.encoding = "utf-8"

                soup = BeautifulSoup(_response.text, "html.parser")
                body = soup.find("body")
                google_html = html.escape(str(body))

                threading.Thread(
                    target=update_request_thuong_hieu_list,
                    args=(
                        id_rq_list,
                        str(sanitize_for_mysql(google_html)),
                        1,
                    ),
                ).start()

                number += 1

            [time.sleep(1) or print("Null data:", _time) for _time in range(0, 10)]

            self.run(number=0, max_number=30)

        except Exception as e:  # noqa: F841
            self.reload_usb()

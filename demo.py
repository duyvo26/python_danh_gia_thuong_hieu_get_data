# from requests import get

# ip = get("https://api.ipify.org").content.decode("utf8")

# print(ip)

import requests

def check_ip():
    try:
        # Đảm bảo bạn đã cài PySocks: pip install PySocks
        response = requests.get("https://api.ipify.org", )
        ip_now = response.text

        # Đảm bảo bạn đã cài PySocks: pip install PySocks
        proxies = {"http": "socks5h://192.168.1.25:1080", "https": "socks5h://192.168.1.25:1080"}
        response = requests.get("https://api.ipify.org", proxies=proxies)
        ip_proxy = response.text

        if ip_now == ip_proxy:
            return False
        else:
            return True
    except:  # noqa: E722
        return False
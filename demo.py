# from requests import get

# ip = get("https://api.ipify.org").content.decode("utf8")

# print(ip)

import requests

# Đảm bảo bạn đã cài PySocks: pip install PySocks
proxies = {"http": "socks5h://192.168.1.25:1080", "https": "socks5h://192.168.1.25:1080"}

response = requests.get("https://api.ipify.org", proxies=proxies)
print(response.text)

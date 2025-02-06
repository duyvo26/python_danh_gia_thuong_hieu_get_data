import re
import requests


def sanitize_for_mysql(input_string):
    # Remove non-ASCII characters (if needed)
    cleaned_string = re.sub(r"[^\x00-\x7F]+", "", input_string)

    # Optionally, you can escape or replace other MySQL problematic characters
    # For example, escape single quotes to prevent SQL injection
    cleaned_string = cleaned_string.replace("'", "''")

    # Return the cleaned string
    return cleaned_string


def check_ip():
    try:
        # Đảm bảo bạn đã cài PySocks: pip install PySocks
        response = requests.get(
            "https://api.ipify.org",
        )
        ip_now = response.text

        # Đảm bảo bạn đã cài PySocks: pip install PySocks
        proxies = {"http": "socks5h://192.168.1.25:1080", "https": "socks5h://192.168.1.25:1080"}
        response = requests.get("https://api.ipify.org", proxies=proxies)
        ip_proxy = response.text

        print("ip ip_now", ip_now)
        print("ip proxy", ip_proxy)

        if ip_now == ip_proxy:
            return False
        else:
            return True
    except:  # noqa: E722
        return False

import requests


def check_captcha(html):
    if "/recaptcha/".lower() in html.lower():
        return False
    if 'id="captcha-form"'.lower() in html.lower():
        return False
    if "https://www.google.com/recaptcha/api.js".lower() in html.lower():
        return False
    return True


def response_custom(url):
    url_api = "http://localhost:8000/base/get-html/"  # URL của API
    api_key = "T0wq2yjazJmln2BRAFTysWNsp7PcZGyAPIMF7i7EWeEniAYv9GbZC81thedolHGu"  # Thay thế bằng API key của bạn

    # Tạo payload cho request
    data = {"url": url}
    headers = {"API-Key": api_key}
    # Gửi request POST tới API
    response = requests.post(url_api, data=data, headers=headers)
    # Kiểm tra kết quả
    if response.status_code == 200:
        result = response.json()
        print(result["status_code"] == 200, result["status_code"])
        if result["status_code"] == 200:
            # Tạo một response giả để trả kết quả đúng định dạng
            if check_captcha(result["html"]) is True:
                return result["html"]
            return None
        else:
            return None

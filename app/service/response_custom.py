import requests


def check_captcha(html):
    if "robot" in html:
        return False
    if "Hệ thống của chúng tôi đã phát hiện thấy lưu lượng truy cập bất thường từ mạng máy tính của bạn." in html:
        return False
    if "CAPTCHA".lower() in html.lower():
        return False
    if "rô-bốt".lower() in html.lower():
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
        if check_captcha(result["html"]):
            # Tạo một response giả để trả kết quả đúng định dạng
            fake_response = requests.models.Response()
            fake_response.status_code = 200
            fake_response.text = result["html"].encode("utf-8")  # Nội dung trả về
            return fake_response

        fake_response = requests.models.Response()
        fake_response.status_code = 404
        return fake_response

from bs4 import BeautifulSoup
import requests  # type: ignore

url = "https://www.google.com/search?q=%22sua+milo%22+after%3A2023-03-19+before%3A2023-05-26"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}

response = requests.get(url, headers=headers, timeout=5)
soup = BeautifulSoup(response.text, "html.parser")

urls = list(set([a.get("href") for a in soup.find_all("a", href=True)]))

print("_urls", urls)

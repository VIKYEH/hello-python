import urllib.parse
import requests
from bs4 import BeautifulSoup

def search_web(query: str, max_results: int = 4) -> str:
    """
    即時聯網搜尋引擎（基於 DuckDuckGo HTML API）。
    取得網頁標題與內容摘要，提供給 Gemini AI 進行事實查核與知識補充。
    """
    if not query or not query.strip():
        return ""

    clean_query = query.strip()
    encoded_query = urllib.parse.quote(clean_query)
    url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            data={"q": clean_query},
            timeout=6
        )
        if response.status_code != 200:
            return ""

        soup = BeautifulSoup(response.text, "html.parser")
        results = []

        for item in soup.select(".result__body"):
            title_node = item.select_one(".result__title")
            snippet_node = item.select_one(".result__snippet")
            link_node = item.select_one(".result__url")

            if title_node and snippet_node:
                title = title_node.get_text(strip=True)
                snippet = snippet_node.get_text(strip=True)
                link = link_node.get_text(strip=True) if link_node else ""
                results.append(f"• 標題：{title}\n  內容：{snippet}\n  網址：{link}")

            if len(results) >= max_results:
                break

        return "\n\n".join(results)

    except Exception as e:
        print(f"[Search Error]: {e}")
        return ""

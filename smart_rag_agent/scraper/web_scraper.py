import httpx
from bs4 import BeautifulSoup

def scrape_url(url: str) -> str:
    try:
        with httpx.Client(timeout=30, follow_redirects=True) as client:
            r = client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "nav", "header", "footer", "aside", "iframe", "noscript"]):
            tag.decompose()
        text = soup.get_text(separator="\n")
        clean_lines = [line.strip() for line in text.splitlines() if line.strip()]
        content = "\n".join(clean_lines)[:250_000]
        return content
    except Exception as e:
        return f"Error scraping {url}: {e}"
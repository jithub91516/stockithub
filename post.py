import os
import requests
import anthropic
import yfinance as yf
from datetime import datetime

# --- Config ---
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
WP_URL = "https://stockithub.com/wp-json/wp/v2/posts"
WP_USERNAME = os.environ["WP_USERNAME"]
WP_APP_PASSWORD = os.environ["WP_APP_PASSWORD"]
UNSPLASH_ACCESS_KEY = os.environ["UNSPLASH_ACCESS_KEY"]

TOPICS = [
    # Semiconductors & Chip (우선순위 최상위)
    {"en": "Samsung Electronics", "ko": "삼성전자", "ticker": "005930.KS", "category": "Tech", "image_query": "semiconductor chip"},
    {"en": "SK Hynix", "ko": "SK하이닉스", "ticker": "000660.KS", "category": "Tech", "image_query": "memory chip"},
    {"en": "DB HiTek", "ko": "DB하이텍", "ticker": "000990.KS", "category": "Tech", "image_query": "microchip wafer"},
    {"en": "Hanmi Semiconductor", "ko": "한미반도체", "ticker": "042700.KS", "category": "Tech", "image_query": "semiconductor equipment"},
    {"en": "HPSP", "ko": "HPSP", "ticker": "403870.KS", "category": "Tech", "image_query": "semiconductor manufacturing"},
    {"en": "Leeno Industrial", "ko": "리노공업", "ticker": "058470.KS", "category": "Tech", "image_query": "semiconductor test"},
    {"en": "Isu Petasys", "ko": "이수페타시스", "ticker": "007660.KS", "category": "Tech", "image_query": "circuit board"},
    # Tech & Internet
    {"en": "Kakao", "ko": "카카오", "ticker": "035720.KS", "category": "Tech", "image_query": "mobile technology"},
    {"en": "Naver", "ko": "NAVER", "ticker": "035420.KS", "category": "Tech", "image_query": "internet technology"},
    {"en": "Krafton", "ko": "크래프톤", "ticker": "259960.KS", "category": "Tech", "image_query": "video game"},
    {"en": "LG Electronics", "ko": "LG전자", "ticker": "066570.KS", "category": "Tech", "image_query": "electronics"},
    {"en": "SK Telecom", "ko": "SK텔레콤", "ticker": "017670.KS", "category": "Tech", "image_query": "telecommunications"},
    {"en": "KT", "ko": "KT", "ticker": "030200.KS", "category": "Tech", "image_query": "network technology"},
    {"en": "Samsung Engineering", "ko": "삼성엔지니어링", "ticker": "028050.KS", "category": "Tech", "image_query": "construction engineering"},
    # Battery & EV
    {"en": "LG Energy Solution", "ko": "LG에너지솔루션", "ticker": "373220.KS", "category": "Stocks", "image_query": "electric vehicle battery"},
    {"en": "SK Innovation", "ko": "SK이노베이션", "ticker": "096770.KS", "category": "Stocks", "image_query": "battery cell"},
    {"en": "LG Chem", "ko": "LG화학", "ticker": "051910.KS", "category": "Stocks", "image_query": "chemical"},
    {"en": "Hanwha Solutions", "ko": "한화솔루션", "ticker": "009830.KS", "category": "Stocks", "image_query": "solar energy"},
    {"en": "Samsung SDI", "ko": "삼성SDI", "ticker": "006400.KS", "category": "Stocks", "image_query": "battery"},
    # Automotive
    {"en": "Hyundai Motor", "ko": "현대자동차", "ticker": "005380.KS", "category": "Stocks", "image_query": "automobile"},
    {"en": "Kia Corporation", "ko": "기아", "ticker": "000270.KS", "category": "Stocks", "image_query": "car"},
    {"en": "Hyundai Mobis", "ko": "현대모비스", "ticker": "012330.KS", "category": "Stocks", "image_query": "auto parts"},
    {"en": "Hyundai Glovis", "ko": "현대글로비스", "ticker": "086280.KS", "category": "Stocks", "image_query": "logistics"},
    {"en": "Hyundai Rotem", "ko": "현대로템", "ticker": "064350.KS", "category": "Stocks", "image_query": "railway train"},
    # Materials & Heavy Industry
    {"en": "POSCO Holdings", "ko": "POSCO홀딩스", "ticker": "005490.KS", "category": "Stocks", "image_query": "steel factory"},
    {"en": "HD Hyundai Heavy Industries", "ko": "HD현대중공업", "ticker": "329180.KS", "category": "Stocks", "image_query": "shipbuilding"},
    {"en": "Hyundai Steel", "ko": "현대제철", "ticker": "004020.KS", "category": "Stocks", "image_query": "steel"},
    {"en": "Korea Zinc", "ko": "고려아연", "ticker": "010130.KS", "category": "Stocks", "image_query": "mining metal"},
    {"en": "Doosan Enerbility", "ko": "두산에너빌리티", "ticker": "034020.KS", "category": "Stocks", "image_query": "power plant"},
    {"en": "HD Hyundai", "ko": "HD현대", "ticker": "267250.KS", "category": "Stocks", "image_query": "heavy machinery"},
    {"en": "OCI Holdings", "ko": "OCI홀딩스", "ticker": "456040.KS", "category": "Stocks", "image_query": "solar energy"},
    {"en": "Kumho Petrochemical", "ko": "금호석유", "ticker": "011780.KS", "category": "Stocks", "image_query": "refinery"},
    # Energy & Chemicals
    {"en": "S-Oil", "ko": "에스오일", "ticker": "010950.KS", "category": "Stocks", "image_query": "oil energy"},
    {"en": "GS Holdings", "ko": "GS홀딩스", "ticker": "078930.KS", "category": "Stocks", "image_query": "energy"},
    {"en": "Lotte Chemical", "ko": "롯데케미칼", "ticker": "011170.KS", "category": "Stocks", "image_query": "chemical plant"},
    # Finance & Banking
    {"en": "KB Financial Group", "ko": "KB금융", "ticker": "105560.KS", "category": "Stocks", "image_query": "bank"},
    {"en": "Shinhan Financial Group", "ko": "신한지주", "ticker": "055550.KS", "category": "Stocks", "image_query": "finance"},
    {"en": "Hana Financial Group", "ko": "하나금융지주", "ticker": "086790.KS", "category": "Stocks", "image_query": "investment"},
    {"en": "Woori Financial Group", "ko": "우리금융지주", "ticker": "316140.KS", "category": "Stocks", "image_query": "stock market"},
    {"en": "Samsung Life Insurance", "ko": "삼성생명", "ticker": "032830.KS", "category": "Stocks", "image_query": "insurance"},
    # Defense & Aerospace
    {"en": "Hanwha Aerospace", "ko": "한화에어로스페이스", "ticker": "012450.KS", "category": "Stocks", "image_query": "aerospace"},
    {"en": "Hanwha Corporation", "ko": "한화", "ticker": "000880.KS", "category": "Stocks", "image_query": "defense"},
    # Biotech & Pharma
    {"en": "Samsung Biologics", "ko": "삼성바이오로직스", "ticker": "207940.KS", "category": "Stocks", "image_query": "biotechnology laboratory"},
    {"en": "Celltrion", "ko": "셀트리온", "ticker": "068270.KS", "category": "Stocks", "image_query": "pharmaceutical"},
    {"en": "Hanmi Pharm", "ko": "한미약품", "ticker": "128940.KS", "category": "Stocks", "image_query": "medicine"},
    {"en": "Yuhan Corporation", "ko": "유한양행", "ticker": "000100.KS", "category": "Stocks", "image_query": "healthcare"},
    {"en": "Daewoong Pharmaceutical", "ko": "대웅제약", "ticker": "069620.KS", "category": "Stocks", "image_query": "pharmacy"},
    # Consumer & Retail
    {"en": "Amorepacific", "ko": "아모레퍼시픽", "ticker": "090430.KS", "category": "Stocks", "image_query": "beauty skincare"},
    {"en": "LG H&H", "ko": "LG생활건강", "ticker": "051900.KS", "category": "Stocks", "image_query": "cosmetics"},
    {"en": "CJ CheilJedang", "ko": "CJ제일제당", "ticker": "097950.KS", "category": "Stocks", "image_query": "food"},
    {"en": "Nongshim", "ko": "농심", "ticker": "004370.KS", "category": "Stocks", "image_query": "noodle"},
    {"en": "Ottogi", "ko": "오뚜기", "ticker": "007310.KS", "category": "Stocks", "image_query": "food"},
    {"en": "KT&G", "ko": "KT&G", "ticker": "033780.KS", "category": "Stocks", "image_query": "plant herb"},
    {"en": "Lotte Shopping", "ko": "롯데쇼핑", "ticker": "023530.KS", "category": "Stocks", "image_query": "shopping mall"},
    {"en": "Hotel Shilla", "ko": "호텔신라", "ticker": "008770.KS", "category": "Stocks", "image_query": "luxury hotel"},
    {"en": "Hyundai Department Store", "ko": "현대백화점", "ticker": "069960.KS", "category": "Stocks", "image_query": "retail store"},
    # Conglomerates
    {"en": "Samsung C&T", "ko": "삼성물산", "ticker": "028260.KS", "category": "Stocks", "image_query": "construction"},
    {"en": "SK Inc", "ko": "SK㈜", "ticker": "034730.KS", "category": "Stocks", "image_query": "energy"},
    {"en": "LG Corporation", "ko": "LG", "ticker": "003550.KS", "category": "Stocks", "image_query": "technology"},
    {"en": "Lotte Holdings", "ko": "롯데지주", "ticker": "004990.KS", "category": "Stocks", "image_query": "business"},
    # Utilities & Energy
    {"en": "Korea Electric Power", "ko": "한국전력", "ticker": "015760.KS", "category": "Stocks", "image_query": "electric power"},
    # Shipbuilding
    {"en": "Samsung Heavy Industries", "ko": "삼성중공업", "ticker": "010140.KS", "category": "Stocks", "image_query": "ship"},
    {"en": "Hyundai Mipo Dockyard", "ko": "현대미포조선", "ticker": "010620.KS", "category": "Stocks", "image_query": "shipyard"},
    # GS Retail
    {"en": "GS Retail", "ko": "GS리테일", "ticker": "007070.KS", "category": "Stocks", "image_query": "convenience store"},
    # Doosan
    {"en": "Doosan Bobcat", "ko": "두산밥캣", "ticker": "241560.KS", "category": "Stocks", "image_query": "construction equipment"},
]


def fetch_stock_data(ticker: str) -> dict:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        data = {}

        price = info.get("currentPrice") or info.get("regularMarketPrice")
        if price:
            data["current_price"] = f"₩{price:,.0f}"

        market_cap = info.get("marketCap")
        if market_cap:
            if market_cap >= 1_000_000_000_000:
                data["market_cap"] = f"₩{market_cap / 1_000_000_000_000:.1f}T"
            else:
                data["market_cap"] = f"₩{market_cap / 100_000_000:.0f}B"

        pe = info.get("trailingPE")
        if pe:
            data["pe_ratio"] = f"{pe:.1f}x"

        pb = info.get("priceToBook")
        if pb:
            data["pb_ratio"] = f"{pb:.2f}x"

        high52 = info.get("fiftyTwoWeekHigh")
        low52 = info.get("fiftyTwoWeekLow")
        if high52 and low52:
            data["52w_range"] = f"₩{low52:,.0f} – ₩{high52:,.0f}"
            if price and high52:
                pct_from_high = (price - high52) / high52 * 100
                data["pct_from_52w_high"] = f"{pct_from_high:+.1f}%"

        div_yield = info.get("dividendYield")
        if div_yield:
            data["dividend_yield"] = f"{div_yield * 100:.2f}%"

        revenue = info.get("totalRevenue")
        if revenue:
            if revenue >= 1_000_000_000_000:
                data["revenue_ttm"] = f"₩{revenue / 1_000_000_000_000:.1f}T"
            else:
                data["revenue_ttm"] = f"₩{revenue / 100_000_000:.0f}B"

        roe = info.get("returnOnEquity")
        if roe:
            data["roe"] = f"{roe * 100:.1f}%"

        return data
    except Exception as e:
        print(f"[yfinance] Failed to fetch data for {ticker}: {e}")
        return {}


def format_stock_data_for_prompt(data: dict) -> str:
    if not data:
        return "Live market data unavailable at time of writing."
    lines = []
    if "current_price" in data:
        lines.append(f"- Current Price: {data['current_price']}")
    if "market_cap" in data:
        lines.append(f"- Market Cap: {data['market_cap']}")
    if "pe_ratio" in data:
        lines.append(f"- P/E Ratio: {data['pe_ratio']}")
    if "pb_ratio" in data:
        lines.append(f"- P/B Ratio: {data['pb_ratio']}")
    if "52w_range" in data:
        lines.append(f"- 52-Week Range: {data['52w_range']}")
    if "pct_from_52w_high" in data:
        lines.append(f"- vs. 52-Week High: {data['pct_from_52w_high']}")
    if "dividend_yield" in data:
        lines.append(f"- Dividend Yield: {data['dividend_yield']}")
    if "revenue_ttm" in data:
        lines.append(f"- Revenue (TTM): {data['revenue_ttm']}")
    if "roe" in data:
        lines.append(f"- Return on Equity: {data['roe']}")
    return "\n".join(lines)


def generate_post(topic: dict) -> dict:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    stock_data = fetch_stock_data(topic["ticker"])
    stock_data_str = format_stock_data_for_prompt(stock_data)
    today = datetime.now().strftime("%B %d, %Y")

    prompt = f"""Write a high-quality, data-driven English blog post analyzing the following Korean stock for international investors.

Company: {topic['en']} ({topic['ko']}, {topic['ticker']})
Date: {today}

Live Market Data (as of today):
{stock_data_str}

Requirements:
- Title: SEO-friendly, include both English name and Korean name (e.g. "Samsung Electronics (삼성전자): ...")
- Length: 1200-1600 words
- Structure: Introduction, 3-4 main sections with <h2> subheadings, Conclusion
- Tone: Analytical and data-driven, accessible for international investors
- Always write the company name as: {topic['en']} ({topic['ko']}, {topic['ticker']}) on first mention, then just {topic['en']} afterwards
- Weave the live market data naturally into the analysis — comment on valuation, price vs. 52-week high/low, dividend attractiveness, etc.
- Include: business overview, competitive position, key risks, and investment thesis for international investors
- Use specific numbers from the market data to back up claims
- End with a brief disclaimer that this is not financial advice

Return your response in exactly this format:
TITLE: <title here>
TAGS: <comma-separated list of 5 tags>
CONTENT:
<full blog post content in HTML format using <h2>, <p>, <ul> tags>
"""

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text

    title_line = [l for l in raw.splitlines() if l.startswith("TITLE:")][0]
    tags_line = [l for l in raw.splitlines() if l.startswith("TAGS:")][0]
    content = raw.split("CONTENT:")[1].strip()

    title = title_line.replace("TITLE:", "").strip()
    tags = [t.strip() for t in tags_line.replace("TAGS:", "").split(",")]

    return {"title": title, "tags": tags, "content": content}


def fetch_unsplash_images(query: str, count: int = 3) -> list:
    res = requests.get(
        "https://api.unsplash.com/search/photos",
        params={"query": query, "per_page": count, "orientation": "landscape"},
        headers={"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"},
    )
    if res.status_code != 200 or not res.json()["results"]:
        return []
    return [
        {
            "url": photo["urls"]["regular"],
            "alt": photo["alt_description"] or query,
            "photographer": photo["user"]["name"],
        }
        for photo in res.json()["results"]
    ]


def upload_image_to_wp(image: dict, title: str, suffix: str = "") -> dict | None:
    import re
    img_data = requests.get(image["url"]).content
    filename = re.sub(r"[^a-z0-9-]", "", title.lower().replace(" ", "-"))[:40] + suffix + ".jpg"
    res = requests.post(
        "https://stockithub.com/wp-json/wp/v2/media",
        auth=(WP_USERNAME, WP_APP_PASSWORD),
        headers={"Content-Disposition": f'attachment; filename="{filename}"', "Content-Type": "image/jpeg"},
        data=img_data,
    )
    if res.status_code == 201:
        media_id = res.json()["id"]
        media_url = res.json()["source_url"]
        requests.post(
            f"https://stockithub.com/wp-json/wp/v2/media/{media_id}",
            auth=(WP_USERNAME, WP_APP_PASSWORD),
            json={"alt_text": image["alt"]},
        )
        return {"id": media_id, "url": media_url, "alt": image["alt"], "photographer": image["photographer"]}
    return None


def get_or_create_tags(tag_names: list) -> list:
    tag_ids = []
    for name in tag_names:
        res = requests.post(
            "https://stockithub.com/wp-json/wp/v2/tags",
            auth=(WP_USERNAME, WP_APP_PASSWORD),
            json={"name": name},
        )
        if res.status_code in (200, 201):
            tag_ids.append(res.json()["id"])
        elif res.status_code == 400:
            # Tag already exists
            search = requests.get(
                "https://stockithub.com/wp-json/wp/v2/tags",
                params={"search": name},
                auth=(WP_USERNAME, WP_APP_PASSWORD),
            )
            if search.json():
                tag_ids.append(search.json()[0]["id"])
    return tag_ids


def get_or_create_category(name: str) -> int | None:
    res = requests.post(
        "https://stockithub.com/wp-json/wp/v2/categories",
        auth=(WP_USERNAME, WP_APP_PASSWORD),
        json={"name": name},
    )
    if res.status_code == 201:
        return res.json()["id"]
    elif res.status_code == 400:
        search = requests.get(
            "https://stockithub.com/wp-json/wp/v2/categories",
            params={"search": name},
            auth=(WP_USERNAME, WP_APP_PASSWORD),
        )
        if search.json():
            return search.json()[0]["id"]
    return None


def make_img_html(media: dict) -> str:
    return (
        f'<figure class="wp-block-image">'
        f'<img src="{media["url"]}" alt="{media["alt"]}" />'
        f'<figcaption>Photo by {media["photographer"]} on Unsplash</figcaption>'
        f'</figure>'
    )


def inject_images_into_content(content: str, media_list: list) -> str:
    if not media_list:
        return content

    # Insert first image before first <h2>
    if len(media_list) >= 1:
        pos = content.find("<h2>")
        if pos != -1:
            content = content[:pos] + make_img_html(media_list[0]) + content[pos:]

    # Insert second image before second <h2>
    if len(media_list) >= 2:
        pos = -1
        for _ in range(2):
            pos = content.find("<h2>", pos + 1)
            if pos == -1:
                break
        if pos != -1:
            content = content[:pos] + make_img_html(media_list[1]) + content[pos:]

    # Insert third image before the last <p>
    if len(media_list) >= 3:
        pos = content.rfind("<p>")
        if pos != -1:
            content = content[:pos] + make_img_html(media_list[2]) + content[pos:]

    return content


def publish_post(post: dict, topic: dict):
    tag_ids = get_or_create_tags(post["tags"])

    # Fetch images from Unsplash
    images = fetch_unsplash_images(topic["image_query"], count=4)
    featured_media_id = None
    content = post["content"]

    if images:
        uploaded = []
        for i, img in enumerate(images):
            media = upload_image_to_wp(img, post["title"], suffix=f"-{i+1}")
            if media:
                uploaded.append(media)
                print(f"Image {i+1}: {media['url']} (by {media['photographer']})")

        if uploaded:
            featured_media_id = uploaded[0]["id"]
            # Inject images into body (skip first, use rest)
            content = inject_images_into_content(content, uploaded[1:])

    category_id = get_or_create_category(topic["category"])

    payload = {
        "title": post["title"],
        "content": content,
        "status": "publish",
        "tags": tag_ids,
        "categories": [category_id] if category_id else [],
    }
    if featured_media_id:
        payload["featured_media"] = featured_media_id

    res = requests.post(WP_URL, auth=(WP_USERNAME, WP_APP_PASSWORD), json=payload)
    res.raise_for_status()
    return res.json()["link"]


if __name__ == "__main__":
    index = (datetime.now().timetuple().tm_yday - 1) % len(TOPICS)
    topic = TOPICS[index]
    print(f"[{datetime.now()}] Topic #{index}: {topic['en']} ({topic['ko']})")

    post = generate_post(topic)
    print(f"Title: {post['title']}")

    url = publish_post(post, topic)
    print(f"Published: {url}")

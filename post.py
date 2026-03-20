import os
import random
import requests
import anthropic
from datetime import datetime

# --- Config ---
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
WP_URL = "https://stockithub.com/wp-json/wp/v2/posts"
WP_USERNAME = os.environ["WP_USERNAME"]
WP_APP_PASSWORD = os.environ["WP_APP_PASSWORD"]
UNSPLASH_ACCESS_KEY = os.environ["UNSPLASH_ACCESS_KEY"]

TOPICS = [
    {"en": "Samsung Electronics", "ko": "삼성전자", "ticker": "005930.KS"},
    {"en": "SK Hynix", "ko": "SK하이닉스", "ticker": "000660.KS"},
    {"en": "LG Energy Solution", "ko": "LG에너지솔루션", "ticker": "373220.KS"},
    {"en": "Samsung SDI", "ko": "삼성SDI", "ticker": "006400.KS"},
    {"en": "POSCO Holdings", "ko": "POSCO홀딩스", "ticker": "005490.KS"},
    {"en": "Hyundai Motor", "ko": "현대자동차", "ticker": "005380.KS"},
    {"en": "Kia Corporation", "ko": "기아", "ticker": "000270.KS"},
    {"en": "Kakao", "ko": "카카오", "ticker": "035720.KS"},
    {"en": "Naver", "ko": "NAVER", "ticker": "035420.KS"},
    {"en": "Samsung Biologics", "ko": "삼성바이오로직스", "ticker": "207940.KS"},
    {"en": "Celltrion", "ko": "셀트리온", "ticker": "068270.KS"},
    {"en": "KB Financial Group", "ko": "KB금융", "ticker": "105560.KS"},
    {"en": "Shinhan Financial Group", "ko": "신한지주", "ticker": "055550.KS"},
    {"en": "Hanwha Aerospace", "ko": "한화에어로스페이스", "ticker": "012450.KS"},
    {"en": "LG Chem", "ko": "LG화학", "ticker": "051910.KS"},
    {"en": "SK Innovation", "ko": "SK이노베이션", "ticker": "096770.KS"},
    {"en": "Krafton", "ko": "크래프톤", "ticker": "259960.KS"},
    {"en": "HD Hyundai Heavy Industries", "ko": "HD현대중공업", "ticker": "329180.KS"},
]


def generate_post(topic: str) -> dict:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = f"""Write a high-quality English blog post introducing the following Korean stock for international investors:

Company: {topic['en']} ({topic['ko']}, {topic['ticker']})

Requirements:
- Title: SEO-friendly, include both English name and Korean name (e.g. "Samsung Electronics (삼성전자): ...")
- Length: 800-1200 words
- Structure: Introduction, 2-3 main sections with subheadings, Conclusion
- Tone: Informative and accessible for international investors
- Always write the company name as: {topic['en']} ({topic['ko']}, {topic['ticker']}) on first mention, then just {topic['en']} afterwards
- Include business overview, recent performance, and why international investors should pay attention
- End with a brief disclaimer that this is not financial advice

Return your response in exactly this format:
TITLE: <title here>
TAGS: <comma-separated list of 5 tags>
CONTENT:
<full blog post content in HTML format using <h2>, <p>, <ul> tags>
"""

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text

    title_line = [l for l in raw.splitlines() if l.startswith("TITLE:")][0]
    tags_line = [l for l in raw.splitlines() if l.startswith("TAGS:")][0]
    content = raw.split("CONTENT:")[1].strip()

    title = title_line.replace("TITLE:", "").strip()
    tags = [t.strip() for t in tags_line.replace("TAGS:", "").split(",")]

    return {"title": title, "tags": tags, "content": content}


def fetch_unsplash_image(query: str) -> dict | None:
    res = requests.get(
        "https://api.unsplash.com/search/photos",
        params={"query": query, "per_page": 1, "orientation": "landscape"},
        headers={"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"},
    )
    print(f"Unsplash status: {res.status_code}, body: {res.text[:200]}")
    if res.status_code != 200 or not res.json()["results"]:
        return None
    photo = res.json()["results"][0]
    return {
        "url": photo["urls"]["regular"],
        "alt": photo["alt_description"] or query,
        "photographer": photo["user"]["name"],
    }


def upload_image_to_wp(image: dict, title: str) -> int | None:
    img_data = requests.get(image["url"]).content
    import re
    filename = re.sub(r"[^a-z0-9-]", "", title.lower().replace(" ", "-"))[:50] + ".jpg"
    res = requests.post(
        "https://stockithub.com/wp-json/wp/v2/media",
        auth=(WP_USERNAME, WP_APP_PASSWORD),
        headers={"Content-Disposition": f'attachment; filename="{filename}"', "Content-Type": "image/jpeg"},
        data=img_data,
    )
    if res.status_code == 201:
        media_id = res.json()["id"]
        # Set alt text
        requests.post(
            f"https://stockithub.com/wp-json/wp/v2/media/{media_id}",
            auth=(WP_USERNAME, WP_APP_PASSWORD),
            json={"alt_text": image["alt"]},
        )
        return media_id
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


def publish_post(post: dict, topic: str):
    tag_ids = get_or_create_tags(post["tags"])

    # Fetch and upload thumbnail
    image = fetch_unsplash_image(topic["en"])
    featured_media = None
    if image:
        featured_media = upload_image_to_wp(image, post["title"])
        print(f"Thumbnail: {image['url']} (by {image['photographer']})")

    payload = {
        "title": post["title"],
        "content": post["content"],
        "status": "publish",
        "tags": tag_ids,
    }
    if featured_media:
        payload["featured_media"] = featured_media

    res = requests.post(WP_URL, auth=(WP_USERNAME, WP_APP_PASSWORD), json=payload)
    res.raise_for_status()
    return res.json()["link"]


if __name__ == "__main__":
    topic = random.choice(TOPICS)
    print(f"[{datetime.now()}] Topic: {topic['en']} ({topic['ko']})")

    post = generate_post(topic)
    print(f"Title: {post['title']}")

    url = publish_post(post, topic)
    print(f"Published: {url}")

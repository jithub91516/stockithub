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

TOPICS = [
    "KOSPI market outlook",
    "KOSDAQ small-cap stocks",
    "Samsung Electronics stock analysis",
    "SK Hynix and the semiconductor industry",
    "Korean battery stocks (LG Energy Solution, Samsung SDI)",
    "Korean EV supply chain stocks",
    "POSCO Holdings and steel industry in Korea",
    "Korean banking sector stocks",
    "Kakao and Korean big tech stocks",
    "Korean biotech and pharma stocks",
    "Korea's export data and stock market impact",
    "Foreign investor trends in Korean stock market",
    "Korean ETF guide for international investors",
    "How to invest in Korean stocks from abroad",
    "Korean defense stocks outlook",
]


def generate_post(topic: str) -> dict:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = f"""Write a high-quality English blog post about the following topic related to the Korean stock market:

Topic: {topic}

Requirements:
- Title: SEO-friendly, clear and compelling
- Length: 800-1200 words
- Structure: Introduction, 2-3 main sections with subheadings, Conclusion
- Tone: Informative and accessible for international investors interested in Korean stocks
- Include relevant context about the Korean market where appropriate
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


def publish_post(post: dict):
    tag_ids = get_or_create_tags(post["tags"])

    res = requests.post(
        WP_URL,
        auth=(WP_USERNAME, WP_APP_PASSWORD),
        json={
            "title": post["title"],
            "content": post["content"],
            "status": "publish",
            "tags": tag_ids,
        },
    )
    res.raise_for_status()
    return res.json()["link"]


if __name__ == "__main__":
    topic = random.choice(TOPICS)
    print(f"[{datetime.now()}] Topic: {topic}")

    post = generate_post(topic)
    print(f"Title: {post['title']}")

    url = publish_post(post)
    print(f"Published: {url}")

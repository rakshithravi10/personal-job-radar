import os
import json
import re
from datetime import datetime
import requests

SERPER_API_KEY = os.environ["SERPER_API_KEY"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

QUERIES = {
    "A": 'Werkstudent ADAS OR "autonomous driving" OR "Computer Vision" OR "Sensor Fusion" Bayern site:linkedin.com OR site:stepstone.de OR site:indeed.de',
    "B": 'Werkstudent "Technisches Projektmanagement" OR Projektingenieur OR Digitalisierung OR "Systems Engineering" Bayern',
}


def search_serper(query):
    r = requests.post(
        "https://google.serper.dev/search",
        headers={"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"},
        json={"q": query, "gl": "de", "hl": "de", "num": 10, "tbs": "qdr:w"},
        timeout=30,
    )
    r.raise_for_status()
    return r.json().get("organic", [])


def parse_results():
    jobs = []
    for query in QUERIES.values():
        for r in search_serper(query):
            jobs.append({
                "title": r.get("title", ""),
                "link": r.get("link", ""),
                "snippet": r.get("snippet", ""),
                "date": r.get("date", "unknown"),
            })
    return jobs


def score_jobs(jobs):
    prompt = (
        'You must respond with ONLY a JSON array. No backticks. No markdown. No code blocks. '
        'No explanation. Start your response with [ and end with ]. '
        'Example format: [{"title":"job","url":"http://example.com","score":75,"track":"A","reason":"good match"}]. '
        'Now score these jobs for Rakshith Ravi (Python PyTorch ROS2 ADAS Bavaria Werkstudent). '
        'Track A: ADAS CV ML. Track B: Technical PM. NO FIT: business HR pharma. Score 0-100. '
        f'Jobs: {json.dumps(jobs)}'
    )
    r = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-haiku-4-5-20251001",
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=60,
    )
    r.raise_for_status()
    text = r.json()["content"][0]["text"]

    start, end = text.find("["), text.rfind("]")
    if start == -1 or end == -1:
        print("---CLAUDE RESPONSE (no JSON array found)---")
        print(text)
        print("---END---")
        raise RuntimeError("Claude did not return a JSON array — see raw response above")

    clean = text[start:end + 1]
    clean = re.sub(r"[\r\n\t]", " ", clean)
    clean = re.sub(r"\\n", " ", clean)
    clean = re.sub(r"\s+", " ", clean)
    clean = re.sub(r"^```json\s*", "", clean)
    clean = re.sub(r"```$", "", clean).strip()
    clean = clean.replace("`", "")
    try:
        return json.loads(clean)
    except json.JSONDecodeError as e:
        print("---CLEANED TEXT THAT FAILED TO PARSE---")
        print(clean)
        print("---END---")
        raise RuntimeError(f"Could not parse Claude's JSON: {e}") from e


def format_message(jobs):
    filtered = sorted(
        (j for j in jobs if j.get("track") != "NO FIT" and j.get("score", 0) >= 40),
        key=lambda j: j["score"],
        reverse=True,
    )
    if not filtered:
        return "No matches found today."

    lines = ["RaxJobRadar Daily Report", datetime.now().strftime("%d.%m.%Y"), ""]
    for i, j in enumerate(filtered, 1):
        lines += [
            f"{i}. {j['title']}",
            f"Track {j['track']} | Score: {j['score']}/100",
            f"{j['reason']}",
            f"{j['url']}",
            "",
        ]
    lines.append(f"Total: {len(filtered)} matches found.")
    return "\n".join(lines)


def send_telegram(text):
    r = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        json={"chat_id": TELEGRAM_CHAT_ID, "text": text},
        timeout=30,
    )
    r.raise_for_status()


def main():
    jobs = parse_results()
    print(f"Fetched {len(jobs)} raw results")
    scored = score_jobs(jobs)
    message = format_message(scored)
    print(message)
    send_telegram(message)


if __name__ == "__main__":
    main()

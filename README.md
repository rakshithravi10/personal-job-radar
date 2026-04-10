# 🎯 personal-job-radar

An AI-powered daily job search pipeline that automatically finds, scores, and delivers Werkstudent job matches to Telegram — built with n8n, Claude API, and Google Search.

---

## What it does

Runs 3 times daily (08:00, 14:00, 19:00) and:

1. Searches Google for fresh Werkstudent job postings in Bavaria
2. Parses and filters results from LinkedIn, Stepstone, and Indeed
3. Scores each job against a candidate profile using Claude AI (Haiku)
4. Sends a ranked report directly to Telegram

---

## Architecture

```
Schedule Trigger (3x daily: 08:00, 14:00, 19:00)
        ↓
Serper API (Google Search)
        ├── Track A: ADAS / CV / ML Engineering jobs
        └── Track B: Technical PM / Systems Engineering jobs
        ↓
Merge & Parse Results
        ↓
Claude API (Haiku) — AI scoring & ranking
        ↓
Format Message
        ↓
Telegram Bot — delivers ranked report to phone
```

---

## Scoring Logic

Each job is scored 0–100 and assigned a track:

| Track | Focus | Keywords |
|-------|-------|----------|
| A | Engineering (preferred) | ADAS, Computer Vision, Sensor Fusion, ROS2, PyTorch, ML |
| B | Technical PM (secondary) | Projektmanagement, Digitalisierung, Systems Engineering |
| NO FIT | Filtered out | Business, HR, Pharma, Sales |

Only jobs scoring ≥ 40 are included in the daily report.

---

## Sample Telegram Output

```
RaxJobRadar Daily Report
10.4.2026

1. Werkstudent ADAS Perception - Continental AG
Track A | Score: 88/100
Strong match — ROS2, sensor fusion, Bavaria location
https://...

2. Werkstudent Systems Engineering - Audi AG
Track A | Score: 75/100
Good match — autonomous systems focus, Ingolstadt
https://...

Total: 2 matches found.
```

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| n8n (self-hosted) | Workflow automation |
| Serper API | Google Search API |
| Claude API (Haiku) | AI job scoring and ranking |
| Telegram Bot API | Daily report delivery |
| pm2 | Process management |
| Ubuntu 22.04 | Host OS |

---

## Setup

### Prerequisites

- Node.js 20+
- n8n self-hosted
- Serper API key — [serper.dev](https://serper.dev)
- Anthropic API key — [console.anthropic.com](https://console.anthropic.com)
- Telegram bot token — create via [@BotFather](https://t.me/BotFather)

### Install n8n

```bash
mkdir -p ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
npm install n8n -g
n8n start
```

Open [http://localhost:5678](http://localhost:5678)

### Keep n8n running with pm2

```bash
npm install pm2 -g
pm2 start n8n
pm2 save
pm2 startup
# Run the command pm2 outputs
```

### Import the workflow

1. Open n8n → `...` menu → **Import from file**
2. Select `workflow.json`
3. Replace all placeholder credentials:
   - `YOUR_SERPER_API_KEY` in both Search nodes
   - `YOUR_ANTHROPIC_API_KEY` in the Code in JavaScript node
   - Add your Telegram bot token in the Telegram credentials panel
   - `YOUR_TELEGRAM_CHAT_ID` in the Send Telegram node
4. Click **Publish**

### Get your Telegram chat ID

After creating your bot via @BotFather and sending it a message, visit:

```
https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
```

Your chat ID is the `id` field inside the `chat` object.

---

## Security

All sensitive credentials are stored inside n8n and are **not committed to this repository**. The `workflow.json` file contains only placeholder values. Never commit real API keys to version control.

---

## Project Structure

```
personal-job-radar/
├── workflow.json       # n8n workflow export (credentials removed)
└── README.md
```

---

## Roadmap

- [ ] Migrate to Oracle Cloud free VM for 24/7 operation
- [ ] Add direct company career page scraping (CARIAD, Bosch, Continental, Audi)
- [ ] Deduplicate jobs across daily runs
- [ ] Track applied/skipped jobs
- [ ] Weekly summary digest

---

## Author

**Rakshith Ravi**  
M.Eng. AI Engineering of Autonomous Systems — Technische Hochschule Ingolstadt  
[LinkedIn](https://linkedin.com/in/rakshithravi10) · [GitHub](https://github.com/rakshithravi10)

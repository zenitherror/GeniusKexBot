# 🤖 GeniusKexBot — Ultimate Telegram Utility Bot

> 31 elite tools + NVIDIA AI powered. Production-ready for Render deployment.

## ⚡ Architecture

```
Telegram → Render Worker → NVIDIA AI API → Database → Utility System
```

## 🚀 Features (31 Total)

### Original Tools (15)
| # | Feature | Description |
|---|---------|-------------|
| 1 | URL Shortener | Shorten URLs via is.gd API |
| 2 | QR Code Generator | Generate QR codes instantly |
| 3 | YT/IG Downloader | Download YouTube/Instagram videos |
| 4 | Referral System | Viral growth with unique referral codes |
| 5 | Earning Dashboard | Track points and referrals |
| 6 | Auto Welcome | Personalized greeting for new/returning users |
| 7 | Broadcast System | Admin-only mass messaging |
| 8 | Secret Vault | Locked content behind referral wall |
| 9 | Daily Bonus | +5 points daily engagement reward |
| 10 | Mini Calculator | Math expression evaluator |
| 11 | Unit Converter | km/miles, C/F, kg/lbs, m/ft, cm/inch, l/gal |
| 12 | Weather Check | Real-time weather via wttr.in |
| 13 | Password Generator | 6-50 char secure passwords |
| 14 | Notes / To-Do | Personal note storage |
| 15 | Website Traffic | Site analysis (title, scripts, links, size) |

### Dark Tools (15)
| # | Feature | Description |
|---|---------|-------------|
| 16 | IP Lookup | Full IP trace (location, ISP, org, lat/lon) |
| 17 | Phone Lookup | Country detection, validation |
| 18 | Email Breach Check | Reputation, breach data, profiles |
| 19 | WHOIS Lookup | Domain owner, registrar, dates |
| 20 | Port Scanner | Scans 20 common ports |
| 21 | Header Analyzer | Security headers + grade (A+ to F) |
| 22 | Hash Generator | MD5, SHA1, SHA256, SHA512 |
| 23 | Base64 Encode/Decode | Encode and decode messages |
| 24 | DNS Lookup | A, AAAA, MX, NS, TXT records |
| 25 | Fake Identity Generator | Full random identity |
| 26 | Subdomain Finder | Find subdomains via crt.sh |
| 27 | Link Analyzer | Phishing detection, risk scoring |
| 28 | Dark Web Email Check | Email exposure check |
| 29 | User Agent / Header Info | Via header analysis |
| 30 | Broadcast via State | Admin message broadcast |

### AI System (1)
| # | Feature | Description |
|---|---------|-------------|
| 31 | /ask AI Command | NVIDIA Llama 3.1 70B powered AI chat |

## 🛠️ Setup

### Prerequisites
- Python 3.11+
- Telegram Bot Token (from @BotFather)
- NVIDIA API Key (from build.nvidia.com)

### Local Development

```bash
git clone https://github.com/zenitherror/GeniusKexBot.git
cd GeniusKexBot
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your values
python bot.py
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `BOT_TOKEN` | Telegram Bot API token | ✅ |
| `ADMIN_ID` | Your Telegram user ID (for broadcast) | ✅ |
| `DATABASE_URL` | Database path (default: geniuskex.db) | ❌ |
| `NVIDIA_API_KEY` | NVIDIA API key for AI features | ✅ |

## 🚀 Render Deployment

### One-Click Deploy

1. Fork/push this repo to GitHub
2. Go to [render.com](https://render.com) → New → **Background Worker**
3. Connect your GitHub repo: `zenitherror/GeniusKexBot`
4. Settings:
   - **Runtime:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python bot.py`
5. Add Environment Variables:
   - `BOT_TOKEN` = your bot token
   - `ADMIN_ID` = your telegram user ID
   - `NVIDIA_API_KEY` = your NVIDIA key
6. Deploy!

### Auto-Redeploy
Render auto-redeploys on every push to `main` branch.

## 📋 Commands

| Command | Description |
|---------|-------------|
| `/start` | Main menu with all tools |
| `/ask <question>` | Ask AI anything |
| `/viewnotes` | View saved notes |
| `/broadcast <msg>` | Admin-only broadcast |
| `/help` | Help message |

## 📁 Project Structure

```
GeniusKexBot/
├── bot.py              # Main bot code (all 31 features)
├── requirements.txt    # Python dependencies
├── Procfile            # Render worker process
├── render.yaml         # Render deployment config
├── runtime.txt         # Python version
├── .env.example        # Environment template
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## 🔒 Security

- Admin-only broadcast (verified by Telegram user ID)
- No hardcoded tokens (all via environment variables)
- Error handling on all features
- Rate limiting on port scanner

## 📊 Tech Stack

- **Bot Framework:** python-telegram-bot 21.6
- **AI:** NVIDIA API (meta/llama-3.1-70b-instruct)
- **Database:** SQLite3
- **Deployment:** Render Background Worker
- **CI/CD:** GitHub → Render auto-deploy

---

**Built for digital dominance. 31 tools. One bot. Zero limits.**

# ⚡ ElectroServ — AI Voice Customer Support Agent

> Real-time voice-based AI support for **AC**, **Washing Machine**, and **Microwave Oven**  
> Supports **English**, **Hindi**, and **Hinglish** conversations

---

## 🏗️ Architecture

```
User Voice  →  Browser MediaRecorder
            →  POST /api/transcribe  (Groq Whisper)
            →  POST /api/chat        (RAG + Groq LLaMA 3.3 70B)
            →  Browser SpeechSynthesis.speak()
            →  Voice Playback
```

## 🔑 Free APIs Used

| Layer | Service | Cost |
|---|---|---|
| STT | Groq Whisper `whisper-large-v3` | **Free** (2000 req/day) |
| LLM | Groq `llama-3.3-70b-versatile` | **Free** (30 req/min) |
| TTS | Browser Web Speech API | **Free** (built-in) |
| DB  | PostgreSQL | **Free** (local) |

---

## 📁 Project Structure

```
AI - Voice Chat Bot/
├── backend/                 ← Python FastAPI
│   ├── main.py              ← API routes
│   ├── config.py            ← Settings (reads .env)
│   ├── database.py          ← SQLAlchemy engine
│   ├── models.py            ← DB models (3 tables)
│   ├── schemas.py           ← Pydantic schemas
│   ├── groq_client.py       ← Groq STT + LLM wrapper
│   ├── knowledge_base.py    ← RAG + intent detection
│   ├── seed_db.py           ← Seeds 18 KB articles
│   ├── requirements.txt
│   └── .env.example         ← Copy to .env and fill keys
│
└── frontend/                ← Next.js 14
    ├── app/
    │   ├── page.tsx         ← Main chat UI
    │   ├── layout.tsx
    │   ├── globals.css      ← Design system
    │   └── page.module.css
    ├── components/
    │   ├── VoiceButton.tsx  ← Push-to-talk mic
    │   ├── ChatHistory.tsx  ← Message display
    │   └── TicketModal.tsx  ← Service ticket form
    ├── lib/api.ts           ← API client
    ├── package.json
    └── .env.local.example   ← Copy to .env.local
```

---

## 🚀 Setup Guide

### Step 1 — Get Your Free Groq API Key

1. Go to [https://console.groq.com](https://console.groq.com)
2. Sign up (free, no credit card needed)
3. Click **"Create API Key"**
4. Copy the key — you'll use it in Step 3

---

### Step 2 — Set Up PostgreSQL Database

Make sure PostgreSQL is installed and running. Then create the database:

```sql
-- In psql or pgAdmin:
CREATE DATABASE voice_support_db;
```

---

### Step 3 — Configure Backend

```powershell
cd "AI - Voice Chat Bot\backend"

# Copy and edit the env file
copy .env.example .env
```

Open `.env` and fill in your values:

```env
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/voice_support_db
```

---

### Step 4 — Install Backend Dependencies

```powershell
cd "AI - Voice Chat Bot\backend"

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install packages
pip install -r requirements.txt
```

---

### Step 5 — Initialize Database & Seed Knowledge Base

```powershell
# (Still inside backend/ with venv active)
python seed_db.py
```

Expected output:
```
✅ Database tables created successfully.
✅ Seeded 18 knowledge base items successfully!
   → AC: 6 items
   → Washing Machine: 6 items
   → Microwave: 6 items
```

---

### Step 6 — Start Backend Server

```powershell
# (Still inside backend/ with venv active)
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Test it: open [http://localhost:8000/health](http://localhost:8000/health)  
You should see: `{"status":"ok","service":"ElectroServ Voice Support API"}`

Also check the interactive API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Step 7 — Configure Frontend

```powershell
cd "AI - Voice Chat Bot\frontend"

copy .env.local.example .env.local
```

`.env.local` content (default, no changes needed if backend is on port 8000):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

### Step 8 — Install & Start Frontend

```powershell
cd "AI - Voice Chat Bot\frontend"

npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) 🎉

---

## 🎙️ How to Use

| Action | How |
|---|---|
| **Voice Input** | Hold the glowing mic button, speak, then release |
| **Text Input** | Type in the text box and press Enter |
| **Stop AI voice** | Click the "Stop Speaking" button |
| **New conversation** | Click "🔄 New Chat" |
| **Create ticket** | After 3+ exchanges, the ticket button appears |

### Example Phrases

```
"My AC is not cooling even after setting it to 18 degrees"
"Washing machine ka door nahi khul raha hai"
"Microwave mein khana garam nahi ho raha"
"What are the error codes for washing machine?"
```

---

## 🗄️ Database Tables

| Table | Purpose |
|---|---|
| `knowledge_items` | 18 troubleshooting articles (RAG source) |
| `conversation_sessions` | Per-session chat history + detected context |
| `service_tickets` | Customer service requests |

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/api/transcribe` | Audio → text (Groq Whisper) |
| `POST` | `/api/chat` | Text → AI response (RAG + LLaMA) |
| `POST` | `/api/tickets` | Create service ticket |
| `GET` | `/api/tickets` | List all tickets |
| `GET` | `/api/session/{id}` | Get session details |
| `POST` | `/api/knowledge` | Add KB article |
| `GET` | `/api/knowledge` | List KB articles |

---

## ⚡ Performance

| Component | Target | Achieved |
|---|---|---|
| STT (Groq Whisper) | < 500ms | ✅ ~200ms |
| LLM (Groq LLaMA) | < 1000ms | ✅ ~400ms |
| TTS (Web Speech) | < 500ms | ✅ Instant |
| **Total** | **< 2s** | ✅ **~700ms** |

---

## 🔧 Troubleshooting

**Microphone not working?**
- Allow microphone permission in browser settings
- Use Chrome or Edge (best Web Speech API support)

**Database connection error?**
- Ensure PostgreSQL is running: `pg_ctl status`
- Check `DATABASE_URL` in `.env` has correct password

**Groq API error?**
- Check your `GROQ_API_KEY` in `.env`
- Free tier limit: 30 requests/min — wait a moment if rate limited

**Hindi TTS not working?**
- Install Hindi language pack in Windows: Settings → Time & Language → Language → Add Hindi
- Restart browser after installing

---

## 📋 Supported Products & Intents

| Product | Intents |
|---|---|
| ❄️ AC | `not_cooling`, `water_leakage`, `remote_not_working`, `power_issue`, `noise_issue`, `error_code` |
| 🫧 Washing Machine | `not_spinning`, `not_draining`, `door_lock_issue`, `power_issue`, `noise_issue`, `error_code` |
| 📡 Microwave | `not_heating`, `turntable_issue`, `display_issue`, `power_issue`, `noise_issue`, `error_code` |

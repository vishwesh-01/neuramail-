# NeuraMail

NeuraMail is a lightweight **email prioritization and analysis tool** built using Python and Flask.  
It connects to a Gmail inbox, reads recent emails from the **Primary** category, and uses **Google Gemini** to summarize, classify, and assign urgency to each email.

The goal of this project is to reduce inbox overload by automatically highlighting which emails need attention first.

---

## What NeuraMail does

- Connects to Gmail using IMAP  
- Fetches recent emails from the **Primary inbox**  
- Uses Gemini to analyze each email and extract:
  - A short summary
  - Email category (work, security, payments, promotions, etc.)
  - Sender (person or organization)
  - Urgency level (`high`, `medium`, `low`)
- Stores analyzed emails in a local **SQLite database**
- Avoids duplicate entries using content-based hashing
- Displays emails in a web dashboard, sorted by urgency and date

This project focuses on **email understanding and prioritization**, not email sending or reply generation.

---

## Why this project exists

NeuraMail was built to:
- Apply LLMs to a real-world problem (email overload)
- Learn how to combine Flask, IMAP, databases, and LLM APIs
- Build a complete working system instead of isolated demos

The emphasis is on backend logic and AI integration rather than UI polish.

---

## Tech stack

- Backend: Python, Flask
- AI / NLP: Google Gemini (`gemini-2.0-flash`) via LangChain
- Email access: Gmail IMAP
- Database: SQLite
- Frontend: HTML (Jinja templates)
- Configuration: python-dotenv

---

## Project structure

```
.
├── app.py            # Flask app, Gmail fetch, database logic
├── classify.py       # Gemini-based email classification
├── templates/
│   └── index.html    # Dashboard UI
├── emails.db         # SQLite database (auto-created)
├── .env              # Environment variables
└── README.md
```

---

## Setup instructions

### 1. Clone the repository

```bash
git clone https://github.com/vishwesh-01/neuramail-.git
cd neuramail-
```

### 2. Create a virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install flask langchain langchain-google-genai python-dotenv
```

---

## Environment configuration

Create a `.env` file in the project root:

```env
EMAIL=your_email@gmail.com
APP_PASSWORD=your_gmail_app_password
GEMINI_API_KEY=your_gemini_api_key
```

### Important notes

- Use a **Gmail App Password**, not your normal Gmail password  
- IMAP must be enabled in Gmail settings  
- Gemini API key can be generated from Google AI Studio  

---

## Running NeuraMail

```bash
python app.py
```

Open your browser and visit:

```
http://127.0.0.1:5000/
```

On each load:
1. Emails are fetched from Gmail
2. New emails are analyzed using Gemini
3. Results are stored and displayed on the dashboard

---

## Clearing stored emails

To clear all stored email data:

```
http://127.0.0.1:5000/cleardb
```

---

## How prioritization works

- **High**: urgent actions, security alerts, payment issues, time-sensitive messages
- **Medium**: important but not immediate
- **Low**: routine updates, promotions, non-critical messages

Emails are displayed by urgency first, then by received time.

---

## Limitations

- Gmail only
- No user authentication
- Basic UI
- Read-only (cannot send or reply to emails)
- Uses free-tier LLM limits

---

## Future improvements

- OAuth-based Gmail login
- Multi-user support
- Improved UI with filters and search
- Background email polling
- Email reply or action suggestions
- Cloud deployment

---

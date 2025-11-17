from flask import Flask, render_template, request
import imaplib
import email
from dotenv import load_dotenv
import os
from email.header import decode_header
from classify import classify_emails
import sqlite3
from datetime import datetime
import hashlib

load_dotenv()

app = Flask(__name__)

EMAIL = os.getenv("EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")
DATABASE = 'emails.db'

def init_db():
    """Initialize the database with emails table"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_hash TEXT UNIQUE,
            subject TEXT,
            sender TEXT,
            body TEXT,
            summary TEXT,
            category TEXT,
            urgency TEXT,
            received_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def get_email_hash(subject, sender, body):
    content = f"{subject}{sender}{body[:100]}" 
    return hashlib.md5(content.encode()).hexdigest()

def clean(text):
    decoded, charset = decode_header(text)[0]
    if isinstance(decoded, bytes):
        return decoded.decode(charset or 'utf-8', errors='ignore')
    return decoded

def get_primary_inbox_email(limit=10):
    emails = []
    try:
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        imap.login(EMAIL, APP_PASSWORD)
        imap.select("inbox")
        result, data = imap.uid('SEARCH', 'X-GM-RAW', '"category:primary"')
        if result != 'OK':
            return []

        email_uids = data[0].split()[-limit:]
        for uid in reversed(email_uids):
            result, data = imap.uid('FETCH', uid, '(RFC822)')
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)

            subject = clean(msg['Subject'] or "")
            sender = clean(msg.get('From', ''))
            
            received_date = msg.get('Date', '')
            if received_date:
                try:
                    parsed_date = email.utils.parsedate_tz(received_date)
                    if parsed_date:
                        timestamp = email.utils.mktime_tz(parsed_date)
                        received_datetime = datetime.fromtimestamp(timestamp)
                    else:
                        received_datetime = datetime.now()
                except:
                    received_datetime = datetime.now()
            else:
                received_datetime = datetime.now()
            
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain" and not part.get('Content-Disposition'):
                        body = part.get_payload(decode=True).decode(errors='ignore')
                        break
            else:
                body = msg.get_payload(decode=True).decode(errors='ignore')

            emails.append({
                "subject": subject,
                "from": sender,
                "body": body,
                "received_date": received_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                "email_hash": get_email_hash(subject, sender, body)
            })

        imap.logout()
    except Exception as e:
        print(f"Email fetch failed: {e}")
    return emails

def store_new_emails(emails_data):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    new_emails_count = 0
    for email_data in emails_data:
        try:
            cursor.execute('''
                INSERT INTO emails (email_hash, subject, sender, body, summary, category, urgency, received_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                email_data['email_hash'],
                email_data['subject'],
                email_data['from'],
                email_data['body'],
                email_data['summary'],
                email_data['category'],
                email_data['urgency'],
                email_data['received_date']
            ))
            new_emails_count += 1
        except sqlite3.IntegrityError:
            continue
    
    conn.commit()
    conn.close()
    return new_emails_count

def get_stored_emails():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    priority_order = "CASE urgency WHEN 'high' THEN 1 WHEN 'medium' THEN 2 WHEN 'low' THEN 3 ELSE 4 END"
    
    cursor.execute(f'''
        SELECT sender, category, summary, urgency, received_date, created_at
        FROM emails
        ORDER BY {priority_order}, datetime(received_date) DESC
    ''')
    
    emails = []
    for row in cursor.fetchall():
        emails.append({
            'from': row[0],
            'category': row[1],
            'summary': row[2],
            'urgency': row[3],
            'received_date': row[4],
            'created_at': row[5]
        })
    
    conn.close()
    return emails

@app.route("/", methods=["GET"])
def index():
    init_db()
    raw_emails = get_primary_inbox_email(limit=10)
    
    if raw_emails:
        email_bodies = [email["body"] for email in raw_emails]
        
        try:
            classified = classify_emails(email_bodies)
            for i, result in enumerate(classified):
                raw_emails[i].update({
                    "summary": result["summary"],
                    "category": result["category"],
                    "urgency": result["urgency"],
                    "from": result["from_"]
                })
            
            new_count = store_new_emails(raw_emails)
            print(f"Added {new_count} new emails to database")
            
        except Exception as e:
            print(f"Classification error: {e}")
    
    all_emails = get_stored_emails()
    
    return render_template("index.html", emails=all_emails)

@app.route("/cleardb", methods=["GET"])
def clear_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM emails')
    conn.commit()
    conn.close()
    print("database is cleared")
    return "Database cleared"

if __name__ == "__main__":
    app.run(debug=True)
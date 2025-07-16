import json
import csv
import smtplib
from email.message import EmailMessage
from pathlib import Path
from datetime import datetime
from secrets import EMAIL_ADDRESS, EMAIL_PASSWORD


MOVIE_FILE = Path.home() / "movie_tracker.json"
RECIPIENT_CSV = Path.home() / "recipients.csv"

# ----------- Setup ----------
def init_data():
    if not MOVIE_FILE.exists():
        with open(MOVIE_FILE, "w") as f:
            json.dump({"movies": []}, f)

def load_data():
    with open(MOVIE_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(MOVIE_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_recipients():
    if not RECIPIENT_CSV.exists():
        print("❌ recipients.csv not found.")
        return []
    with open(RECIPIENT_CSV, "r") as f:
        return [line.strip() for line in f if line.strip()]

# ----------- Actions ----------
def add_movie():
    title = input("Title: ").strip()
    mtype = input("Type (movie/series): ").strip().lower()
    watched = input("Watched? (yes/no): ").strip().lower() == "yes"
    notes = input("Notes or Strategy: ").strip()
    trailer = input("Trailer URL (optional): ").strip()

    data = load_data()
    data["movies"].append({
        "title": title,
        "type": mtype,
        "watched": watched,
        "notes": notes,
        "trailer": trailer,
        "added": str(datetime.now())
    })
    save_data(data)
    print(f"✅ Added: {title}")

def view_all():
    data = load_data()
    for i, m in enumerate(data["movies"], 1):
        status = "✅" if m["watched"] else "❌"
        print(f"{i}. {m['title']} ({m['type']}) {status}")
        print(f"   Notes: {m['notes']}")
        if m['trailer']:
            print(f"   Trailer: {m['trailer']}")

def send_email():
    
    recipients = load_recipients()
    if not recipients:
        print("❌ No recipients found.")
        return

    data = load_data()
    unwatched = [m for m in data["movies"] if not m["watched"]]

    if not unwatched:
        print("🎉 No unwatched items to send.")
        return

    msg = EmailMessage()
    msg["Subject"] = "🎬 Lethu’s Watchlist Update"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = ", ".join(recipients)

    body = "Here’s your current watchlist:\n\n"
    for m in unwatched:
        body += f"- {m['title']} ({m['type']})\n"
        body += f"  Notes: {m['notes']}\n"
        if m['trailer']:
            body += f"  Trailer: {m['trailer']}\n"
        body += "\n"

    body += "-- Sent by Lethu's Ubuntu Movie Tracker"

    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
            print(f"📧 Email sent to: {len(recipients)} recipients")
    except Exception as e:
        print("❌ Email failed:", e)

# ----------- Menu ----------
def menu():
    init_data()
    while True:
        print("\n--- Movie & Series Tracker ---")
        print("1. Add New")
        print("2. View All")
        print("3. Send Watchlist Email")
        print("4. Exit")
        choice = input("Select: ")

        if choice == "1":
            add_movie()
        elif choice == "2":
            view_all()
        elif choice == "3":
            send_email()
        elif choice == "4":
            break
        else:
            print("Invalid option.")

if __name__ == "__main__":
    menu()

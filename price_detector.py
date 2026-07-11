import pandas as pd
import json
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ------------------ CONFIG ------------------
YESTERDAY_CSV = "books_yesterday.csv"
TODAY_CSV = "books_today.csv"
SUBSCRIBERS_FILE = "subscribers.json"
SENDER = "tesfawtsions@gmail.com"
SENDER_NAME = "Dealkly Alerts"
# Get password from environment (set in GitHub Secrets)
PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")
if not PASSWORD:
    raise ValueError("GMAIL_APP_PASSWORD environment variable not set.")
# --------------------------------------------

def load_subscribers():
    with open(SUBSCRIBERS_FILE, "r") as f:
        data = json.load(f)
    return data  # list of email addresses

def detect_price_drops():
    # Read both CSVs
    yest = pd.read_csv(YESTERDAY_CSV)
    today = pd.read_csv(TODAY_CSV)

    # Merge on book title or unique ID (assuming title is unique)
    merged = pd.merge(yest, today, on="title", suffixes=("_yest", "_today"))
    # Calculate price difference
    merged["drop"] = merged["price_today"] - merged["price_yest"]
    # Filter only drops (negative difference)
    drops = merged[merged["drop"] < 0]
    return drops

def send_alert(drops):
    if drops.empty:
        print("No price drops today.")
        return

    # Build email content
    subject = "Dealkly Alert: Price Drops Detected!"
    body = "The following books have dropped in price:\n\n"
    for _, row in drops.iterrows():
        body += f"- {row['title']}: from ${row['price_yest']:.2f} to ${row['price_today']:.2f} (drop: ${-row['drop']:.2f})\n"

    # Send to all subscribers
    subscribers = load_subscribers()
    if not subscribers:
        print("No subscribers. Email not sent.")
        return

    msg = MIMEMultipart()
    msg["From"] = f"{SENDER_NAME} <{SENDER}>"
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER, PASSWORD)
        for subscriber in subscribers:
            msg["To"] = subscriber
            server.send_message(msg)
            print(f"Alert sent to {subscriber}")

if __name__ == "__main__":
    drops = detect_price_drops()
    send_alert(drops)

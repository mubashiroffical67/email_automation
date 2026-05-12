
import streamlit as st
import smtplib
import pandas as pd
import schedule
import threading
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

LOG_FILE = "email_logs.csv"

st.set_page_config(page_title="Email Automation", layout="centered")

st.title("📧 Email Automation System")

st.markdown("Send scheduled emails using Gmail SMTP service.")

sender_email = st.text_input("Your Gmail Address")
app_password = st.text_input("Gmail App Password", type="password")
receiver_email = st.text_input("Receiver Email")
subject = st.text_input("Email Subject")
message = st.text_area("Email Message")

schedule_time = st.time_input("Schedule Time")

def log_email(receiver, subject, status):
    log_data = {
        "Time": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        "Receiver": [receiver],
        "Subject": [subject],
        "Status": [status]
    }

    try:
        existing = pd.read_csv(LOG_FILE)
        updated = pd.concat([existing, pd.DataFrame(log_data)], ignore_index=True)
    except:
        updated = pd.DataFrame(log_data)

    updated.to_csv(LOG_FILE, index=False)

def send_email():
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject

        msg.attach(MIMEText(message, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, app_password)

        server.send_message(msg)
        server.quit()

        log_email(receiver_email, subject, "Success")
        print("Email sent successfully")

    except Exception as e:
        log_email(receiver_email, subject, f"Failed: {e}")
        print(e)

def scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

if st.button("Schedule Email"):
    formatted_time = schedule_time.strftime("%H:%M")
    schedule.every().day.at(formatted_time).do(send_email)

    thread = threading.Thread(target=scheduler, daemon=True)
    thread.start()

    st.success(f"Email scheduled at {formatted_time}")

st.subheader("📜 Email History")

try:
    logs = pd.read_csv(LOG_FILE)
    st.dataframe(logs)
except:
    st.info("No email history found.")

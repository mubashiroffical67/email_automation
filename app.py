import streamlit as st
import smtplib
import pandas as pd
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

LOG_FILE = "email_logs.csv"

st.set_page_config(page_title="Email Automation", layout="centered")

st.title("📧 Email Automation System")
st.markdown("Send scheduled emails using Gmail SMTP service.")

# Initialize scheduler once
if 'scheduler' not in st.session_state:
    st.session_state.scheduler = BackgroundScheduler()
    st.session_state.scheduler.start()

scheduler = st.session_state.scheduler

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


def send_email(sender, password, receiver, sub, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = receiver
        msg['Subject'] = sub

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)

        server.send_message(msg)
        server.quit()

        log_email(receiver, sub, "Success")
        print("Email sent successfully")

    except Exception as e:
        log_email(receiver, sub, f"Failed: {e}")
        print(e)


if st.button("Schedule Email"):

    run_time = schedule_time.strftime("%H:%M")

    scheduler.add_job(
        send_email,
        trigger='cron',
        hour=schedule_time.hour,
        minute=schedule_time.minute,
        args=[sender_email, app_password, receiver_email, subject, message],
        id=f"email_{time.time()}",
        replace_existing=False
    )

    st.success(f"✅ Email scheduled successfully at {run_time}")


st.subheader("📜 Email History")

try:
    logs = pd.read_csv(LOG_FILE)
    st.dataframe(logs)
except:
    st.info("No email history found.")

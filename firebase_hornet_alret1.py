import pyrebase4 as pyrebase

import smtplib
from email.mime.text import MIMEText

# ✅ Firebase Configuration
firebase_config  = {
  "apiKey": "AIzaSyCc2CHbWxVlmLtGGF5L5tY_VxOnfuRo5FU",
  "authDomain": "test1-3e832.firebaseapp.com",
  "databaseURL": "https://test1-3e832-default-rtdb.europe-west1.firebasedatabase.app",
  "projectId": "test1-3e832",
  "storageBucket": "test1-3e832.firebasestorage.app",
  "messagingSenderId": "518093938096",
  "appId": "1:518093938096:web:c29cb0c1981327777e4a75",
  "measurementId": "G-C0X95TBMCL"
}

firebase = pyrebase.initialize_app(firebase_config)
db = firebase.database()

# ✅ Gmail SMTP Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "smartbeehive8@gmail.com"  # ✅ Replace with your Gmail
SMTP_PASSWORD = "zjur pgwy fnlt euwf"  # ✅ Use the generated App Password

# ✅ Function to Fetch Emails of Users under `2490315/users`
def get_recipient_emails():
    users = db.child("2490315").child("users").get().val()  # Fetch all users under `2490315`
    recipient_emails = []

    if users:
        for user_id, user_data in users.items():
            if "email" in user_data:
                recipient_emails.append(user_data["email"])

    return recipient_emails

# ✅ Function to Send Email Alerts
def send_email_alert(node_id):
    recipient_emails = get_recipient_emails()  # Get all emails for `2490315`

    if not recipient_emails:
        print("❌ No users found under 2490315/users")
        return

    subject = f"🚨 Hornet Alert: Beehive Node {node_id} at Risk!"
    body = f"A hornet has been detected in **Node {node_id}**. Immediate action is required!"

    msg = MIMEText(body)
    msg["From"] = SMTP_USERNAME
    msg["Subject"] = subject

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)

            for recipient_email in recipient_emails:
                msg["To"] = recipient_email
                server.sendmail(SMTP_USERNAME, recipient_email, msg.as_string())

        print(f"✅ Email sent successfully to {len(recipient_emails)} users!")
    except Exception as e:
        print("❌ Failed to send email:", e)

# ✅ Function to Monitor Firebase for Hornet Detection
def firebase_listener(event):
    print(f"🔹 Firebase Event Received: {event}")  # Debugging

    if isinstance(event, dict) and "data" in event:
        data = event["data"]

        if data and isinstance(data, dict):  # Ensure it's a dictionary
            for node_id, node_data in data.items():
                if node_data.get("hornetDetected") is True:
                    print(f"🚨 Hornet detected in {node_id}, sending email alerts...")
                    send_email_alert(node_id)

# ✅ Attach Listener to Firebase Realtime Database (Monitoring all nodes under 2490315)
db.child("2490315").stream(firebase_listener)

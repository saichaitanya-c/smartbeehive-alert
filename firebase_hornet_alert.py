import pyrebase
import smtplib
import os
from email.mime.text import MIMEText
from dotenv import load_dotenv

# ✅ Load Environment Variables (For Local Testing)
load_dotenv()

# ✅ Firebase Configuration (Using Environment Variables)
firebase_config = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID"),
    "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID"),
}

firebase = pyrebase.initialize_app(firebase_config)
db = firebase.database()

# ✅ Gmail SMTP Configuration (Using Environment Variables)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = os.getenv("SMTP_USERNAME")  # ✅ Use Environment Variable
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")  # ✅ Use Environment Variable

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

    # ✅ Extract node_id safely
    node_id = "unknown"
    try:
        if isinstance(event, dict) and "path" in event and isinstance(event["path"], str):
            path_parts = event["path"].strip("/").split("/")
            if path_parts:
                node_id = path_parts[0]  # Extract node_id

        # ✅ Ensure data exists and check for `hornetDetected`
        if "data" in event:
            if isinstance(event["data"], dict):
                for key, value in event["data"].items():
                    if isinstance(value, dict) and value.get("hornetDetected") is True:
                        print(f"🚨 Hornet detected in {node_id}, sending email alerts...")
                        send_email_alert(node_id)
            elif event["data"] == True:
                print(f"🚨 Hornet detected in {node_id}, sending email alerts...")
                send_email_alert(node_id)

    except Exception as e:
        print(f"❌ Error processing Firebase event: {e}")


# ✅ Attach Listener to Firebase Realtime Database (Monitoring all nodes under 2490315)
db.child("2490315").stream(firebase_listener)

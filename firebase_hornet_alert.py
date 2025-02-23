import pyrebase
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
SMTP_USERNAME = "smartbeehive8@gmail.com"  # ✅ Your Gmail
SMTP_PASSWORD = "zjur pgwy fnlt euwf"  # ✅ Use the generated App Password

# ✅ Function to Fetch Emails of Users with uniqueId = "2490315"
def get_recipient_emails():
    users = db.child("users").get().val()  # Fetch all users from Firebase
    recipient_emails = []

    if users:
        for user_id, user_data in users.items():
            if user_data.get("uniqueId") == "2490315":
                recipient_emails.append(user_data.get("email"))

    return recipient_emails

# ✅ Function to Send Email Alerts
def send_email_alert(node_id):
    recipient_emails = get_recipient_emails()  # Get all emails for uniqueId = "2490315"

    if not recipient_emails:
        print("❌ No users found with uniqueId 2490315")
        return

    subject = "🚨 Hornet Alert: Beehive at Risk!"
    body = f"A hornet has been detected in Node {node_id}. Immediate action is required!"

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
    node_id = event.path.split("/")[1]  # Extract node ID
    new_value = event.data

    if new_value is True:  # ✅ Send email only when value changes to True
        print(f"🚨 Hornet detected in {node_id}, sending email alerts...")
        send_email_alert(node_id)

# ✅ Attach Listener to Firebase Realtime Database
db.child("2490315").child("hornetDetected").stream(firebase_listener)

from flask import Flask, render_template, request, jsonify, session, redirect
import sqlite3
import pickle
import numpy as np
from tensorflow.keras.models import load_model
import json
import random
import nltk
from nltk.stem import WordNetLemmatizer
from textblob import TextBlob
from werkzeug.security import generate_password_hash, check_password_hash
import os
import smtplib
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from flask import request
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
nltk.download('punkt')
nltk.download('wordnet')
app = Flask(__name__)
app.secret_key = 'your_super_secret_random_string'
database = "new.db"
model = load_model('chatbot_model.h5')
lemmatizer = WordNetLemmatizer()
with open("words.pkl", "rb") as f:
    words = pickle.load(f)
    print(len(words))  # MUST be 1121
with open("classes.pkl", "rb") as f:
    classes = pickle.load(f)
with open('intents.json', encoding='utf-8') as file:
    intents = json.load(file)
def init_db():
    conn = sqlite3.connect(database)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS register (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            usermail TEXT UNIQUE NOT NULL,
            guardmail TEXT,
            password TEXT NOT NULL,
            age INTEGER,
            number TEXT,
            profile_image TEXT,
            wellness_score INTEGER DEFAULT 50,
            reset_token TEXT,
            token_expire DATETIME
        )
        """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS wellness_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            login_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            logout_time DATETIME,
            wellness_score INTEGER,
            risk_level INTEGER,
            FOREIGN KEY (user_id) REFERENCES register(id)
        )
        """)
    conn.commit()
    conn.close()
init_db()
import secrets
import smtplib
import ssl
from email.message import EmailMessage
from datetime import datetime, timedelta
import sqlite3
from flask import render_template, request
SENDER_EMAIL = "triossoftwaremail@gmail.com"
SENDER_PASSWORD = "knaxddlwfpkplsik"
from flask import Flask, request, render_template_string, flash
RESET_PAGE_TEMPLATE = """
HTMLCODE:
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <title>Reset Password</title>
</head>
<body class="bg-gray-50 flex items-center justify-center min-h-screen">
    <div class="bg-white p-8 rounded-xl shadow-lg w-full max-w-md border border-gray-100">
        <div class="text-center mb-8">
            <div class="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                </svg>
            </div>
            <h2 class="text-2xl font-bold text-gray-800">Forgot Password?</h2>
            <p class="text-gray-500 mt-2 text-sm">Enter your email and we'll send you a link.</p>
        </div>
        {% if message %}
        <div class="mb-6 p-4 rounded-lg bg-green-50 text-green-700 text-sm border border-green-200">
            {{ message }}
        </div>
        {% endif %}
        <form method="POST" class="space-y-6">
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
                <input type="email" name="usermail" placeholder="name@company.com" 
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all" required>
            </div>
            <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-lg transition-colors shadow-md">
                Send Reset Link
            </button>
        </form>
  
        <div class="mt-6 text-center">
            <a href="/login" class="text-sm text-gray-400 hover:text-blue-600 transition-colors">Back to log in</a>
        </div>
    </div>
</body>
</html>
"""
@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    message = None
    if request.method == "POST":
        usermail = request.form["usermail"]
        token = secrets.token_urlsafe(32)
        expire_time = (datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
        conn = sqlite3.connect(database)
        cur = conn.cursor()
        # Check if user exists first to avoid unnecessary email attempts
        cur.execute("UPDATE register SET reset_token=?, token_expire=? WHERE usermail=?", 
                   (token, expire_time, usermail))
 
        if cur.rowcount > 0:
            conn.commit()
            # Email Logic
            reset_link = f"http://127.0.0.1:5000/reset-password/{token}"
            msg = EmailMessage()
            msg["Subject"] = "Password Reset Request"
            msg["From"] = SENDER_EMAIL
            msg["To"] = usermail
            msg.set_content(f"Click the link to reset your password: {reset_link}")
            try:
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                    server.login(SENDER_EMAIL, SENDER_PASSWORD)
                    server.send_message(msg)
            except Exception as e:
                print(f"Error sending email: {e}")
      
        conn.close()
        # We show the same message regardless of whether the email exists (Security Best Practice)
        message = "If that email is in our system, a reset link has been sent."
    return render_template_string(RESET_PAGE_TEMPLATE, message=message)
@app.route('/profile', methods=['GET'])
def get_profile():
    usermail = session.get("usermail")
    if not usermail:
        return jsonify({"error": "Not logged in"}), 401
    conn = sqlite3.connect(database)
    cur = conn.cursor()
    cur.execute("""
        SELECT username, usermail, guardmail, age, number, profile_image, wellness_score
        FROM register WHERE usermail=?
    """, (usermail,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "User not found"}), 404
    profile = {
        "username": row[0],
        "usermail": row[1],
        "guardmail": row[2],
        "age": row[3],
        "number": row[4],
        "profile_image": row[5] or "static/default-profile.png",
        "wellness_score": row[6] if row[6] else 50
    }
    return jsonify(profile)
import hashlib
NEW_PASSWORD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <title>Set New Password</title>
</head>
<body class="bg-gray-50 flex items-center justify-center min-h-screen">
    <div class="bg-white p-8 rounded-xl shadow-lg w-full max-w-md border border-gray-100">
        <div class="text-center mb-8">
            <div class="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
            </div>
            <h2 class="text-2xl font-bold text-gray-800">Secure Your Account</h2>
            <p class="text-gray-500 mt-2 text-sm">Please enter a strong new password below.</p>
        </div>
        {% if error %}
        <div class="mb-4 p-3 rounded bg-red-50 text-red-700 text-xs border border-red-200">
            {{ error }}
        </div>
        {% endif %}
        <form method="POST" class="space-y-4">
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">New Password</label>
                <input type="password" name="password" placeholder="••••••••" 
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 outline-none transition-all" required minlength="8">
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Confirm New Password</label>
                <input type="password" name="confirm_password" placeholder="••••••••" 
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 outline-none transition-all" required minlength="8">
            </div>
            <button type="submit" class="w-full bg-gray-900 hover:bg-black text-white font-semibold py-3 rounded-lg transition-colors shadow-md mt-2">
                Update Password
            </button>
        </form>
    </div>
</body>
</html>
"""
@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    conn = sqlite3.connect(database)
    cur = conn.cursor()
    # Use strftime to match the format we saved in the previous step
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  SQL:
    cur.execute("""
        SELECT Id FROM register 
        WHERE reset_token=? AND token_expire > ?
    """, (token, now))

    user = cur.fetchone()
    if not user:
        conn.close()
        return "<h3>Invalid or expired token.</h3><p>Please request a new link.</p>", 400
    error = None
    if request.method == "POST":
        new_password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        if new_password != confirm_password:
            error = "Passwords do not match."
        else:
            hashed_password = generate_password_hash(new_password)
            cur.execute("""
                UPDATE register 
                SET password=?, reset_token=NULL, token_expire=NULL 
                WHERE Id=?
            """, (hashed_password, user[0]))
         
            conn.commit()
            conn.close()
            return "Password updated successfully! You can now <a href='/login'>login</a>."
    return render_template_string(NEW_PASSWORD_TEMPLATE, error=error)
def send_alert_email(user_name, user_mail, mobile_number,latitude,longitude):
    host = "smtp.gmail.com"
    mmail = "triossoftwaremail@gmail.com"        
    hmail = user_mail
    receiver_name = "Emergency Department"
    sender_name= "Alert System"
    msg = MIMEMultipart()
    subject = "Alert Message"
    text = f"""🚨 Emergency Alert 🚨
    User Details:
    Name: {user_name}
    Mobile Number: {mobile_number}
    Message: The user has expressed suicidal thoughts while interacting with the chatbot.
    Location Information:
    Latitude: {latitude}
    Longitude: {longitude}
    Please take immediate action and contact emergency services.
    """
    msg = MIMEText(text, 'plain')
    msg['To'] = formataddr((receiver_name, hmail))
    msg['From'] = formataddr((sender_name, mmail))
    msg['Subject'] = 'Hello  ' + receiver_name
    server = smtplib.SMTP(host, 587)
    server.ehlo()
    server.starttls()
    password = "knaxddlwfpkplsik"
    server.login(mmail, password)
    server.sendmail(mmail, [hmail], msg.as_string())
    server.quit()
@app.route('/profile', methods=['POST'])
def update_profile():
    usermail = session.get("usermail")
    if not usermail:
        return jsonify({"error": "Not logged in"}), 401
    username = request.form.get("username")
    guardmail = request.form.get("guardmail")
    age = request.form.get("age")
    number = request.form.get("number")
    file = request.files.get("profile_image")
    filename = None
    if file:
        ext = file.filename.split('.')[-1]
        filename = f"{usermail}_{uuid.uuid4().hex}.{ext}"
        file.save(os.path.join(UPLOAD_FOLDER, filename))
    conn = sqlite3.connect(database)
    cur = conn.cursor()
    if filename:
        cur.execute("""
            UPDATE register
            SET username=?, guardmail=?, age=?, number=?, profile_image=?
            WHERE usermail=?
        """, (username, guardmail, age, number, os.path.join(UPLOAD_FOLDER, filename), usermail))
    else:
        cur.execute("""
            UPDATE register
            SET username=?, guardmail=?, age=?, number=?
            WHERE usermail=?
        """, (username, guardmail, age, number, usermail))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Profile updated"})
@app.route('/')
def index():
    return render_template("register.html")
import re # Add this at the top of your file
@app.route('/register', methods=['POST','GET'])
def register():
    if request.method == 'POST':
        username = request.form.get("username")
        usermail = request.form.get("usermail")
        guardmail = request.form.get("guardmail")
        password = request.form.get("password")
        age = request.form.get('age')
        number = request.form.get('number')
        if not (username and usermail and password):
            return "Please fill all required fields"

   
        password_pattern = r"^(?=.*[A-Z])(?=.*[!@#$%^&*(),.?\":{}|<>]).{8,}$"
       
        if not re.match(password_pattern, password):
            return "Password must be at least 8 characters long, include one uppercase letter, and one special character."
        # ---------------------------------
        hashed_password = generate_password_hash(password)
        try:
            conn = sqlite3.connect(database)
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO register (username, usermail, guardmail, password, age, number) VALUES (?, ?, ?, ?, ?, ?)",
                (username, usermail, guardmail, hashed_password, age, number)
            )
            conn.commit()
            conn.close()
            return redirect('/login')
        except sqlite3.IntegrityError:
            return "User already exists"
    return render_template("register.html")
from datetime import timedelta
# Add this to your app configuration (usually at the top)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=31)
@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        usermail = request.form.get("usermail")
        password = request.form.get("password")
        remember = request.form.get("remember") # This gets the checkbox value
        conn = sqlite3.connect(database)
        cur = conn.cursor()
        cur.execute("SELECT password FROM register WHERE usermail=?", (usermail,))
        data = cur.fetchone()
        conn.close()
        if data and check_password_hash(data[0], password):
            session.clear()
            session['usermail'] = usermail
            session["risk_level"] = 0
            session["wellness_score"] = 50
            session["emotion_count"] = 0
            session["last_intent"] = None

            conn = sqlite3.connect(database)
            cur = conn.cursor()
            cur.execute("SELECT id FROM register WHERE usermail=?", (usermail,))
            user = cur.fetchone()
            user_id = user[0]
            session["user_id"] = user_id
            cur.execute("""
                INSERT INTO wellness_history (user_id, wellness_score, risk_level)
                VALUES (?, ?, ?)
            """, (user_id, 50, 0))
            session["session_history_id"] = cur.lastrowid
            conn.commit()
            conn.close()
            if remember:
                session.permanent = True
            else:
                session.permanent = False
            return render_template("chatbot.html")
        else:
            return render_template("index.html", message="Invalid credentials")
    return render_template("index.html")
@app.route('/logout')
def logout():
    if session.get("session_history_id"):

        conn = sqlite3.connect(database)
        cur = conn.cursor()
        cur.execute("""
            UPDATE wellness_history
            SET wellness_score=?,
                risk_level=?,
                logout_time=CURRENT_TIMESTAMP
            WHERE id=?
        """, (
            session.get("wellness_score", 50),
            session.get("risk_level", 0),
            session["session_history_id"]
        ))
        conn.commit()
        conn.close()
    session.clear()
    return redirect('/')
def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    return [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
    return np.array(bag)
def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]), verbose=0)[0]
    ERROR_THRESHOLD = 0.75
    results = [
        {"intent": classes[i], "probability": float(prob)}
        for i, prob in enumerate(res)
        if prob > ERROR_THRESHOLD
    ]
    results.sort(key=lambda x: x["probability"], reverse=True)
    return results
def get_intent(predictions):
    if len(predictions) > 0:
        return predictions[0]["intent"]
    return None
recommendations = {
    "sad": [
        "• Try stepping outside for fresh air.",
        "• Write down what you're feeling.",
        "• Talk to someone you trust.",
        "• Be gentle with yourself today.",
        "• Take a short walk, even for 5 minutes.",
        "• Listen to calming or uplifting music.",
        "• Drink a glass of water.",
        "• Do one very small task to feel a sense of progress.",
        "• Practice slow deep breathing.",
        "• Watch something comforting or familiar."
    ],
    "stressed": [
        "• Break tasks into smaller steps.",
        "• Take a 5-minute breathing break.",
        "• Prioritize only 1 thing right now.",
        "• Stretch your body gently.",
        "• Step away from screens for 10 minutes.",
        "• Make a short to-do list.",
        "• Drink water and pause for a moment.",
        "• Practice mindful breathing."
    ],
    "anxiety": [
        "• Try 4-4-6 breathing.",
        "• Ground yourself by naming 5 things you see.",
        "• Remind yourself this feeling will pass.",
        "• Place your hand on your chest and breathe slowly.",
        "• Reduce caffeine for today.",
        "• Focus on one simple physical task.",
        "• Listen to calming sounds or white noise.",
        "• Splash cool water on your face."
    ],
    "suicidal": [
        "• Please contact a trusted person immediately.",
        "• Reach out to your local emergency number.",
        "• Contact a suicide prevention helpline in your country.",
        "• You deserve support right now — please seek immediate help.",
        "• Stay with someone physically if possible.",
        "• Remove anything harmful from your surroundings.",
        "• Go to a safe public place if you can."
    ]
}
POLITE_PHRASES = {
    "bye": [
        "Take care! Remember, I'm always here if you want to chat.",
        "Goodbye! Wishing you a calm and peaceful day.",
        "See you soon! Keep taking care of yourself."
    ],
    "thank_you": [
        "You're welcome! I'm glad I could help.",
        "No problem! Remember, you can always talk to me.",
        "Anytime! Take care of yourself."
    ]
}
def build_supportive_reply(intent):
    empathy_bank = {
        "sad": [
            "I'm really sorry you're feeling this way.",
            "That sounds really heavy to carry.",
            "It must be difficult going through this.",
            "I can hear how much this is affecting you."
        ],
        "stressed": [
            "It sounds like you're under a lot of pressure.",
            "That must feel overwhelming.",
            "You're carrying a lot right now.",
            "I can sense how tense this feels for you."
        ],
        "anxiety": [
            "That sounds really uncomfortable.",
            "Anxiety can feel very intense.",
            "Your body might be on high alert right now.",
            "I can understand how unsettling that feels."
        ],
        "suicidal": [
            "I'm really concerned about you.",
            "I'm glad you told me this.",
            "You don't have to face this alone.",
            "Your pain sounds very deep."
        ],
        "default": [
            "Thank you for sharing that with me.",
            "I'm here and listening.",
            "I appreciate you opening up.",
            "Tell me more about that."
        ]
    }
    if intent in empathy_bank:
        empathy_line = random.choice(empathy_bank[intent])
    else:
        empathy_line = ""
    base_reply = ""
    for i in intents["intents"]:
        if i["tag"] == intent:
            base_reply = random.choice(i["responses"])
            break
    return f"{empathy_line}\n{base_reply}"
import random
import random
def get_recommendation(intent):
    items = recommendations.get(intent, [])
    if not items:
        return ""
    last_shown = session.get(f"last_{intent}_recs", [])
    available = [item for item in items if item not in last_shown]
    if len(available) < 4:
        available = items
    if len(available) <= 4:
        selected = available
    else:
        selected = random.sample(available, 4)

    session[f"last_{intent}_recs"] = selected
    return "\n".join(selected)
    return "\n".join(selected)
def get_plain_response(intent):
    for i in intents["intents"]:
        if i["tag"] == intent:
            return random.choice(i["responses"])
    return "I'm here with you."
from textblob import TextBlob
def detect_emotion(message):
    msg = message.lower()
    blob = TextBlob(message)
    polarity = blob.sentiment.polarity
    if any(word in msg for word in ['stressed','pressure','overwhelmed']):
        return "stressed"
    if any(word in msg for word in ['anxious','nervous','worried']):
        return "anxiety"
    loneliness_patterns = [
        "no one",
        "nobody",
        "left out",
        "by myself",
        "alone",
        "miss someone",
        "wish someone",
        "no friends",
        "feel invisible",
        "no one understands"
    ]
    if any(pattern in msg for pattern in loneliness_patterns):
        return "lonely"
    if polarity < -0.2 and any(word in msg for word in ['talk', 'friends', 'people', 'together']):
        return "lonely
    return "neutral"
from googletrans import Translator
from gtts import gTTS
import os
import uuid
translator = Translator()
def translate_text(text, target_lang):
    from googletrans import Translator
    translator = Translator()
  
    if not text:
        return ""  
   
    translated = translator.translate(str(text), dest=target_lang)
    return translated.text
def generate_audio(text, lang):
    filename = f"static/audio_{uuid.uuid4().hex}.mp3"
    tts = gTTS(text=text, lang=lang)
    tts.save(filename)
    return filename
def analyze_sentiment(message):
    blob = TextBlob(message)
    polarity = blob.sentiment.polarity
    if polarity > 0:
        return "positive"
    elif polarity < 0:
        return "negative"
    else:
        return "neutral"
from flask import Flask, render_template, request, jsonify, session, redirect
import sqlite3
import pickle
import numpy as np
from tensorflow.keras.models import load_model
import json
import random
import nltk
from nltk.stem import WordNetLemmatizer
from textblob import TextBlob
from werkzeug.security import generate_password_hash, check_password_hash
import os
import smtplib
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from flask import request
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
nltk.download('punkt')
nltk.download('wordnet')
app = Flask(__name__)
app.secret_key = 'your_super_secret_random_string'
database = "new.db"
model = load_model('chatbot_model.h5')
lemmatizer = WordNetLemmatizer()
with open("words.pkl", "rb") as f:
    words = pickle.load(f)
with open("classes.pkl", "rb") as f:
    classes = pickle.load(f)
with open('intents.json', encoding='utf-8') as file:
    intents = json.load(file)
def init_db():
    conn = sqlite3.connect(database)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS register (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            usermail TEXT UNIQUE NOT NULL,
            guardmail TEXT,
            password TEXT NOT NULL,
            age INTEGER,
            number TEXT,
            profile_image TEXT,
            wellness_score INTEGER DEFAULT 50,
            reset_token TEXT,
            token_expire DATETIME
        )
        """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS wellness_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            login_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            logout_time DATETIME,
            wellness_score INTEGER,
            risk_level INTEGER,
            FOREIGN KEY (user_id) REFERENCES register(id)
        )
        """)
    conn.commit()
    conn.close()

init_db()
import secrets
import smtplib
import ssl
from email.message import EmailMessage
from datetime import datetime, timedelta
import sqlite3
from flask import render_template, request
SENDER_EMAIL = "triossoftwaremail@gmail.com"
SENDER_PASSWORD = "knaxddlwfpkplsik"
from flask import Flask, request, render_template_string, flash
RESET_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <title>Reset Password</title>
</head>
<body class="bg-gray-50 flex items-center justify-center min-h-screen">
    <div class="bg-white p-8 rounded-xl shadow-lg w-full max-w-md border border-gray-100">
        <div class="text-center mb-8">
            <div class="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                </svg>
            </div>
            <h2 class="text-2xl font-bold text-gray-800">Forgot Password?</h2>
            <p class="text-gray-500 mt-2 text-sm">Enter your email and we'll send you a link.</p>
        </div>
        {% if message %}
        <div class="mb-6 p-4 rounded-lg bg-green-50 text-green-700 text-sm border border-green-200">
            {{ message }}
        </div>
        {% endif %}
        <form method="POST" class="space-y-6">
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
                <input type="email" name="usermail" placeholder="name@company.com" 
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all" required>
            </div>
            <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-lg transition-colors shadow-md">
                Send Reset Link
            </button>
        </form>
       
        <div class="mt-6 text-center">
            <a href="/login" class="text-sm text-gray-400 hover:text-blue-600 transition-colors">Back to log in</a>
        </div>
    </div>
</body>
</html>
"""
@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    message = None
    if request.method == "POST":
        usermail = request.form["usermail"]
        token = secrets.token_urlsafe(32)
        expire_time = (datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
        conn = sqlite3.connect(database)
        cur = conn.cursor()
        # Check if user exists first to avoid unnecessary email attempts
        cur.execute("UPDATE register SET reset_token=?, token_expire=? WHERE usermail=?", 
                   (token, expire_time, usermail))
       
        if cur.rowcount > 0:
            conn.commit()
            # Email Logic
            reset_link = f"http://127.0.0.1:5000/reset-password/{token}"
            msg = EmailMessage()
            msg["Subject"] = "Password Reset Request"
            msg["From"] = SENDER_EMAIL
            msg["To"] = usermail
            msg.set_content(f"Click the link to reset your password: {reset_link}")
            try:
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                    server.login(SENDER_EMAIL, SENDER_PASSWORD)
                    server.send_message(msg)
            except Exception as e:
                print(f"Error sending email: {e}")
       
        conn.close()
        # We show the same message regardless of whether the email exists (Security Best Practice)
        message = "If that email is in our system, a reset link has been sent."
    return render_template_string(RESET_PAGE_TEMPLATE, message=message)
@app.route('/profile', methods=['GET'])
def get_profile():
    usermail = session.get("usermail")
    if not usermail:
        return jsonify({"error": "Not logged in"}), 401
    conn = sqlite3.connect(database)
    cur = conn.cursor()
    cur.execute("""
        SELECT username, usermail, guardmail, age, number, profile_image, wellness_score
        FROM register WHERE usermail=?
    """, (usermail,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "User not found"}), 404
    profile = {
        "username": row[0],
        "usermail": row[1],
        "guardmail": row[2],
        "age": row[3],
        "number": row[4],
        "profile_image": row[5] or "static/default-profile.png",
        "wellness_score": row[6] if row[6] else 50
    }
    return jsonify(profile)
import hashlib
NEW_PASSWORD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <title>Set New Password</title>
</head>
<body class="bg-gray-50 flex items-center justify-center min-h-screen">
    <div class="bg-white p-8 rounded-xl shadow-lg w-full max-w-md border border-gray-100">
        <div class="text-center mb-8">
            <div class="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
            </div>
            <h2 class="text-2xl font-bold text-gray-800">Secure Your Account</h2>
            <p class="text-gray-500 mt-2 text-sm">Please enter a strong new password below.</p>
        </div>

        {% if error %}
        <div class="mb-4 p-3 rounded bg-red-50 text-red-700 text-xs border border-red-200">
            {{ error }}
        </div>
        {% endif %}
        <form method="POST" class="space-y-4">
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">New Password</label>
                <input type="password" name="password" placeholder="••••••••" 
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 outline-none transition-all" required minlength="8">
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Confirm New Password</label>
                <input type="password" name="confirm_password" placeholder="••••••••" 
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 outline-none transition-all" required minlength="8">
            </div>
            <button type="submit" class="w-full bg-gray-900 hover:bg-black text-white font-semibold py-3 rounded-lg transition-colors shadow-md mt-2">
                Update Password
            </button>
        </form>
    </div>
</body>
</html>
"""

@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    conn = sqlite3.connect(database)
    cur = conn.cursor()
    # Use strftime to match the format we saved in the previous step
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
   
    cur.execute("""
        SELECT Id FROM register 
        WHERE reset_token=? AND token_expire > ?
    """, (token, now))
   
    user = cur.fetchone()
    if not user:
        conn.close()
        return "<h3>Invalid or expired token.</h3><p>Please request a new link.</p>", 400
    error = None
    if request.method == "POST":
        new_password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        if new_password != confirm_password:
            error = "Passwords do not match."
        else:
            hashed_password = generate_password_hash(new_password)
            cur.execute("""
                UPDATE register 
                SET password=?, reset_token=NULL, token_expire=NULL 
                WHERE Id=?
            """, (hashed_password, user[0]))
           
            conn.commit()
            conn.close()
            return "Password updated successfully! You can now <a href='/login'>login</a>."
    return render_template_string(NEW_PASSWORD_TEMPLATE, error=error)
def send_alert_email(user_name, user_mail, mobile_number,latitude,longitude):
    host = "smtp.gmail.com"
    mmail = "triossoftwaremail@gmail.com"        
    hmail = user_mail
    receiver_name = "Emergency Department"
    sender_name= "Alert System"
    msg = MIMEMultipart()
    subject = "Alert Message"
    text = f"""🚨 Emergency Alert 🚨
    User Details:
    Name: {user_name}
    Mobile Number: {mobile_number}

    Message: The user has expressed suicidal thoughts while interacting with the chatbot.
    Location Information:
    Latitude: {latitude}
    Longitude: {longitude}
    Please take immediate action and contact emergency services.
    """
    msg = MIMEText(text, 'plain')
    msg['To'] = formataddr((receiver_name, hmail))
    msg['From'] = formataddr((sender_name, mmail))
    msg['Subject'] = 'Hello  ' + receiver_name
    server = smtplib.SMTP(host, 587)
    server.ehlo()
    server.starttls()
    password = "knaxddlwfpkplsik"
    server.login(mmail, password)
    server.sendmail(mmail, [hmail], msg.as_string())
    server.quit()
@app.route('/profile', methods=['POST'])
def update_profile():
    usermail = session.get("usermail")
    if not usermail:
        return jsonify({"error": "Not logged in"}), 401
    username = request.form.get("username")
    guardmail = request.form.get("guardmail")
    age = request.form.get("age")
    number = request.form.get("number")
    file = request.files.get("profile_image")
    filename = None
    if file:
        ext = file.filename.split('.')[-1]
        filename = f"{usermail}_{uuid.uuid4().hex}.{ext}"
        file.save(os.path.join(UPLOAD_FOLDER, filename))
    conn = sqlite3.connect(database)
    cur = conn.cursor()
    if filename:
        cur.execute("""
            UPDATE register
            SET username=?, guardmail=?, age=?, number=?, profile_image=?
            WHERE usermail=?
        """, (username, guardmail, age, number, os.path.join(UPLOAD_FOLDER, filename), usermail))
    else:
        cur.execute("""
            UPDATE register
            SET username=?, guardmail=?, age=?, number=?
            WHERE usermail=?
        """, (username, guardmail, age, number, usermail))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Profile updated"})
@app.route('/')
def index():
    return render_template("register.html")
import re # Add this at the top of your file
@app.route('/register', methods=['POST','GET'])
def register():
    if request.method == 'POST':
        username = request.form.get("username")
        usermail = request.form.get("usermail")
        guardmail = request.form.get("guardmail")
        password = request.form.get("password")
        age = request.form.get('age')
        number = request.form.get('number')
        if not (username and usermail and password):
            return "Please fill all required fields"

    
        password_pattern = r"^(?=.*[A-Z])(?=.*[!@#$%^&*(),.?\":{}|<>]).{8,}$"
       
        if not re.match(password_pattern, password):
            return "Password must be at least 8 characters long, include one uppercase letter, and one special character."
        # ---------------------------------
        hashed_password = generate_password_hash(password)
        try:
            conn = sqlite3.connect(database)
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO register (username, usermail, guardmail, password, age, number) VALUES (?, ?, ?, ?, ?, ?)",
                (username, usermail, guardmail, hashed_password, age, number)
            )
            conn.commit()
            conn.close()
            return redirect('/login')
        except sqlite3.IntegrityError:
            return "User already exists"

    return render_template("register.html")
from datetime import timedelta
# Add this to your app configuration (usually at the top)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=31)
@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        usermail = request.form.get("usermail")
        password = request.form.get("password")
        remember = request.form.get("remember") # This gets the checkbox value
        conn = sqlite3.connect(database)
        cur = conn.cursor()
        cur.execute("SELECT password FROM register WHERE usermail=?", (usermail,))
        data = cur.fetchone()
        conn.close()

        if data and check_password_hash(data[0], password):
            session.clear()
            session['usermail'] = usermail
            session["risk_level"] = 0
            session["wellness_score"] = 50
            session["emotion_count"] = 0
            session["last_intent"] = None
            conn = sqlite3.connect(database)
            cur = conn.cursor()
            cur.execute("SELECT id FROM register WHERE usermail=?", (usermail,))
            user = cur.fetchone()
            user_id = user[0]
            session["user_id"] = user_id
            cur.execute("""
                INSERT INTO wellness_history (user_id, wellness_score, risk_level)
                VALUES (?, ?, ?)
            """, (user_id, 50, 0))
            session["session_history_id"] = cur.lastrowid
            conn.commit()
            conn.close()
            if remember:
                session.permanent = True
            else:
                session.permanent = False
            return render_template("chatbot.html")
        else:
            return render_template("index.html", message="Invalid credentials")
    return render_template("index.html")
@app.route('/logout')
def logout():
    if session.get("session_history_id"):
        conn = sqlite3.connect(database)
        cur = conn.cursor()
        cur.execute("""
            UPDATE wellness_history
            SET wellness_score=?,
                risk_level=?,
                logout_time=CURRENT_TIMESTAMP
            WHERE id=?
        """, (
            session.get("wellness_score", 50),
            session.get("risk_level", 0),
            session["session_history_id"]
        ))
        conn.commit()
        conn.close()
    session.clear()
    return redirect('/')


def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    return [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
    return np.array(bag)
def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]), verbose=0)[0]
    ERROR_THRESHOLD = 0.75
    results = [
        {"intent": classes[i], "probability": float(prob)}
        for i, prob in enumerate(res)
        if prob > ERROR_THRESHOLD
    ]
    results.sort(key=lambda x: x["probability"], reverse=True)
    return results
def get_intent(predictions):
    if len(predictions) > 0:
        return predictions[0]["intent"]
    return None
recommendations = {
    "sad": [
        "• Try stepping outside for fresh air.",
        "• Write down what you're feeling.",
        "• Talk to someone you trust.",
        "• Be gentle with yourself today.",
        "• Take a short walk, even for 5 minutes.",
        "• Listen to calming or uplifting music.",
        "• Drink a glass of water.",
        "• Do one very small task to feel a sense of progress.",
        "• Practice slow deep breathing.",
        "• Watch something comforting or familiar."
    ],
    "stressed": [
        "• Break tasks into smaller steps.",
        "• Take a 5-minute breathing break.",
        "• Prioritize only 1 thing right now.",
        "• Stretch your body gently.",
        "• Step away from screens for 10 minutes.",
        "• Make a short to-do list.",
        "• Drink water and pause for a moment.",
        "• Practice mindful breathing."
    ],
    "anxiety": [
        "• Try 4-4-6 breathing.",
        "• Ground yourself by naming 5 things you see.",
        "• Remind yourself this feeling will pass.",
        "• Place your hand on your chest and breathe slowly.",
        "• Reduce caffeine for today.",
        "• Focus on one simple physical task.",
        "• Listen to calming sounds or white noise.",
        "• Splash cool water on your face."
    ],
    "suicidal": [
        "• Please contact a trusted person immediately.",
        "• Reach out to your local emergency number.",
        "• Contact a suicide prevention helpline in your country.",
        "• You deserve support right now — please seek immediate help.",
        "• Stay with someone physically if possible.",
        "• Remove anything harmful from your surroundings.",
        "• Go to a safe public place if you can."
    ]
}
POLITE_PHRASES = {
    "bye": [
        "Take care! Remember, I'm always here if you want to chat.",
        "Goodbye! Wishing you a calm and peaceful day.",
        "See you soon! Keep taking care of yourself."
    ],
    "thank_you": [
        "You're welcome! I'm glad I could help.",
        "No problem! Remember, you can always talk to me.",
        "Anytime! Take care of yourself."
    ]
}
def build_supportive_reply(intent):
    empathy_bank = {
        "sad": [
            "I'm really sorry you're feeling this way.",
            "That sounds really heavy to carry.",
            "It must be difficult going through this.",
            "I can hear how much this is affecting you."
        ],
        "stressed": [
            "It sounds like you're under a lot of pressure.",
            "That must feel overwhelming.",
            "You're carrying a lot right now.",
            "I can sense how tense this feels for you."
        ],
        "anxiety": [
            "That sounds really uncomfortable.",
            "Anxiety can feel very intense.",
            "Your body might be on high alert right now.",
            "I can understand how unsettling that feels."
        ],
        "suicidal": [
            "I'm really concerned about you.",
            "I'm glad you told me this.",
            "You don't have to face this alone.",
            "Your pain sounds very deep."
        ],
        "default": [
            "Thank you for sharing that with me.",
            "I'm here and listening.",
            "I appreciate you opening up.",
            "Tell me more about that."
        ]
    }
    if intent in empathy_bank:
        empathy_line = random.choice(empathy_bank[intent])
    else:
        empathy_line = ""

    base_reply = ""
    for i in intents["intents"]:
        if i["tag"] == intent:
            base_reply = random.choice(i["responses"])
            break
    return f"{empathy_line}\n{base_reply}"
import random
import random
def get_recommendation(intent):
    items = recommendations.get(intent, [])

    if not items:
        return ""
    last_shown = session.get(f"last_{intent}_recs", [])
    available = [item for item in items if item not in last_shown]
    if len(available) < 4:
        available = items
    if len(available) <= 4:
        selected = available
    else:
        selected = random.sample(available, 4)
    session[f"last_{intent}_recs"] = selected
    return "\n".join(selected)
    return "\n".join(selected)
def get_plain_response(intent):
    for i in intents["intents"]:
        if i["tag"] == intent:
            return random.choice(i["responses"])
    return "I'm here with you."
from textblob import TextBlob
def detect_emotion(message):
    msg = message.lower()
    blob = TextBlob(message)
    polarity = blob.sentiment.polarity
    if any(word in msg for word in ['stressed','pressure','overwhelmed']):
        return "stressed"
    if any(word in msg for word in ['anxious','nervous','worried']):
        return "anxiety"
    loneliness_patterns = [
        "no one",
        "nobody",
        "left out",
        "by myself",
        "alone",
        "miss someone",
        "wish someone",
        "no friends",
        "feel invisible",
        "no one understands"
    ]
    if any(pattern in msg for pattern in loneliness_patterns):
        return "lonely"
    if polarity < -0.2 and any(word in msg for word in ['talk', 'friends', 'people', 'together']):
        return "lonely"
    return "neutral"
from googletrans import Translator
from gtts import gTTS
import os
import uuid
translator = Translator()
def translate_text(text, target_lang):
    from googletrans import Translator
    translator = Translator()
   
    if not text:
        return ""  
  
    translated = translator.translate(str(text), dest=target_lang)
    return translated.text
def generate_audio(text, lang):
    filename = f"static/audio_{uuid.uuid4().hex}.mp3"
    tts = gTTS(text=text, lang=lang)
    tts.save(filename)
    return filename
def analyze_sentiment(message):
    blob = TextBlob(message)
    polarity = blob.sentiment.polarity
    if polarity > 0:
        return "positive"
    elif polarity < 0:
        return "negative"
    else:
        return "neutral"
@app.route('/chat', methods=['POST'])
def chat():
    # 1. Authentication & Session Check
    if not session.get('usermail'):
        return jsonify({'reply': 'Please login first', 'recommendation': '', 'audio': ''})
    data = request.get_json()
    user_message = data.get("message", "").strip()
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    selected_language = data.get("language", "en")
    session["language"] = selected_language
    tts_lang = selected_language.split('-')[0]
    # 2. Translation Logic (Non-English support)
    if selected_language != "en":
        try:
            user_message_en = translator.translate(user_message, src=tts_lang, dest='en').text
        except:
            user_message_en = user_message
    else:
        user_message_en = user_message
    message_lower = user_message_en.lower()
    # 3. Crisis Detection & Immediate Database Alert
    CRISIS_PHRASES = ["i want to die", "i want to kill myself", "end my life", "suicide", "kill myself"]
    for phrase in CRISIS_PHRASES:
        if phrase in message_lower:
            session["risk_level"] = 3
            score = max(0, session.get("wellness_score", 50) - 15)
            session["wellness_score"] = score
            # Sync Crisis State to DB immediately
            conn = sqlite3.connect(database)
            cur = conn.cursor()
            cur.execute("UPDATE register SET wellness_score=? WHERE usermail=?", (score, session["usermail"]))
            if session.get("session_history_id"):
                cur.execute("UPDATE wellness_history SET wellness_score=?, risk_level=? WHERE id=?", 
                           (score, 3, session["session_history_id"]))
           
            # Fetch details for Emergency Alert
            cur.execute("SELECT username, guardmail, number FROM register WHERE usermail=?", (session["usermail"],))
            user_data = cur.fetchone()
            conn.commit()
            conn.close()
            if user_data and user_data[1]:
                send_alert_email(user_data[0], user_data[1], user_data[2], latitude=latitude, longitude=longitude)
            reply = "I'm really concerned about you.\nYour life matters deeply.\nAre you safe right now?"
            recommendation = "\n".join(recommendations.get("suicidal", []))
            if selected_language != "en":
                reply = translate_text(reply, tts_lang)
                recommendation = translate_text(recommendation, tts_lang)
            audio_path = generate_audio(reply, tts_lang)
            return jsonify({"reply": reply, "recommendation": recommendation, "audio": "/" + audio_path, "wellness_score": score})

    # 4. Sentiment Analysis & Score Calculation
    blob = TextBlob(user_message_en)
    polarity = blob.sentiment.polarity  # -1 to +1
   
    score = session.get("wellness_score", 50)
    score_change = int(polarity * 10)
    score = max(0, min(100, score + score_change))
    session["wellness_score"] = score
    # 5. AI Intent Prediction & Risk Tracking
    predictions = predict_class(user_message_en)
    final_intent = get_intent(predictions)
   
    if not final_intent:
        reply = "I want to understand you better. Can you tell me more?"
        if selected_language != "en":
            reply = translate_text(reply, tts_lang)
        audio_path = generate_audio(reply, tts_lang)
        return jsonify({"reply": reply, "recommendation": "", "audio": "/" + audio_path, "wellness_score": score})
    previous_intent = session.get("last_intent")
    emotion_count = session.get("emotion_count", 0)
    emotion_count = emotion_count + 1 if previous_intent == final_intent else 1
    session["emotion_count"] = emotion_count
    risk_level = session.get("risk_level", 0)
    if final_intent == "sad": risk_level = max(risk_level, 1)
    if emotion_count >= 4: risk_level = min(3, risk_level + 1)
    session["risk_level"] = risk_level
    # 6. DATABASE SYNC (The Critical Fix)
    try:
        conn = sqlite3.connect(database)
        cur = conn.cursor()
        # Update main user record
        cur.execute("UPDATE register SET wellness_score=? WHERE usermail=?", (score, session["usermail"]))
        # Update current session history for Dashboard Charts
        if session.get("session_history_id"):
            cur.execute("""
                UPDATE wellness_history 
                SET wellness_score=?, risk_level=? 
                WHERE id=?
            """, (score, risk_level, session["session_history_id"]))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database error during live update: {e}")
    # 7. Build Supportive Reply
    if final_intent == "sad":
        if emotion_count == 1:
            reply = build_supportive_reply(final_intent)
        elif emotion_count == 2:
            reply = "It sounds like this feeling is still really strong. Has something specific happened?"
        else:
            reply = "I'm noticing this sadness is staying with you. On a scale of 1-10, how intense is it?"
        recommendation = get_recommendation(final_intent)
    else:
        reply = build_supportive_reply(final_intent)
        recommendation = get_recommendation(final_intent)
    # 8. Translation & Audio Generation
    if selected_language != "en":
        reply = translate_text(reply, tts_lang)
        recommendation = translate_text(recommendation, tts_lang)
    session["last_intent"] = final_intent
    audio_path = generate_audio(reply + recommendation, tts_lang)
    # 9. Return updated score to frontend for instant UI refresh
    return jsonify({
        "reply": reply,
        "recommendation": recommendation,
        "audio": "/" + audio_path,
        "wellness_score": score 
    })
@app.route('/api/wellness-stats')
def get_wellness_stats():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    conn = sqlite3.connect(database)
    cur = conn.cursor()
   
    # Fetch last 30 entries of wellness history
    cur.execute("""
        SELECT login_time, wellness_score, risk_level 
        FROM wellness_history 
        WHERE user_id = ? 
        ORDER BY login_time DESC LIMIT 30
    """, (user_id,))
   
    rows = cur.fetchall()
    conn.close()
    # Process data for Chart.js (reverse to show chronological order)
    rows.reverse()
   
    stats = {
        "dates": [r[0].split()[0] for r in rows], # YYYY-MM-DD
        "scores": [r[1] for r in rows],
        "risks": [r[2] for r in rows]
    }
    return jsonify(stats)
if __name__ == '__main__':
    app.run(debug=False, port=659)
 

from flask import Flask, render_template, request, redirect, send_file, session
import sqlite3
import os
import base64
import csv
import cv2
import numpy as np
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "change_this_secret_key"

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load face detector
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")


# ---------------- DATABASE ----------------

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        image_data = request.form.get("image")

        if not image_data:
            return "Face capture required"

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM voters WHERE email=?", (email,))
        if cursor.fetchone():
            conn.close()
            return "Email already registered"

        try:
            image_data = image_data.split(",")[1]
            image_bytes = base64.b64decode(image_data)
        except:
            return "Image error"

        filename = secure_filename(email + ".png")
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        with open(filepath, "wb") as f:
            f.write(image_bytes)

        cursor.execute(
            "INSERT INTO voters (name,email,photo,has_voted) VALUES (?,?,?,0)",
            (name, email, filepath)
        )

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")


# ---------------- FACE LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        image_data = request.form.get("image")

        if not image_data:
            return "Capture face first"

        try:
            image_data = image_data.split(",")[1]
            image_bytes = base64.b64decode(image_data)

            nparr = np.frombuffer(image_bytes, np.uint8)
            captured_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        except:
            return "Image processing error"

        gray = cv2.cvtColor(captured_img, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.3,
            minNeighbors=5,
            minSize=(50, 50)
        )

        if len(faces) == 0:
            return "No face detected. Try again."

        captured_img = cv2.resize(captured_img, (200, 200))

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM voters")
        voters = cursor.fetchall()

        matched_user = None

        for user in voters:

            if not os.path.exists(user["photo"]):
                continue

            stored_img = cv2.imread(user["photo"])

            if stored_img is None:
                continue

            stored_img = cv2.resize(stored_img, (200, 200))

            stored_gray = cv2.cvtColor(stored_img, cv2.COLOR_BGR2GRAY)
            captured_gray = cv2.cvtColor(captured_img, cv2.COLOR_BGR2GRAY)

            diff = cv2.absdiff(stored_gray, captured_gray)

            score = np.mean(diff)

            # Higher threshold for cloud environments
            if score < 120:
                matched_user = user
                break

        conn.close()

        if matched_user:
            return redirect(f"/vote/{matched_user['id']}")

        return "Face not matched. Try again."

    return render_template("login.html")


# ---------------- VOTING PAGE ----------------

@app.route("/vote/<int:user_id>")
def vote(user_id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM voters WHERE id=?", (user_id,))
    user = cursor.fetchone()

    cursor.execute("SELECT * FROM candidates")
    candidates = cursor.fetchall()

    conn.close()

    return render_template(
        "vote.html",
        user=user,
        candidates=candidates
    )


# ---------------- SUBMIT VOTE ----------------

@app.route("/submit_vote", methods=["POST"])
def submit_vote():

    user_id = request.form.get("user_id")
    candidate_id = request.form.get("candidate")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT status FROM election_status WHERE id=1")
    status = cursor.fetchone()["status"]

    if status == "stopped":
        conn.close()
        return "Election stopped by admin"

    cursor.execute(
        "UPDATE candidates SET votes=votes+1 WHERE id=?",
        (candidate_id,)
    )

    cursor.execute(
        "UPDATE voters SET has_voted=1 WHERE id=?",
        (user_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/result")


# ---------------- RESULTS ----------------

@app.route("/result")
def result():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT name,votes FROM candidates")
    data = cursor.fetchall()

    conn.close()

    labels = [row["name"] for row in data]
    votes = [row["votes"] for row in data]

    winner = max(data, key=lambda x: x["votes"])["name"] if data else "No votes"

    return render_template(
        "result.html",
        labels=labels,
        votes=votes,
        winner=winner
    )


# ---------------- ADMIN LOGIN ----------------

@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM admin WHERE username=? AND password=?",
            (username, password)
        )

        admin = cursor.fetchone()
        conn.close()

        if admin:
            session["admin"] = username
            return redirect("/admin")

        return "Invalid credentials"

    return render_template("admin_login.html")


# ---------------- ADMIN DASHBOARD ----------------

@app.route("/admin")
def admin():

    if "admin" not in session:
        return redirect("/admin_login")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM candidates")
    candidates = cursor.fetchall()

    conn.close()

    return render_template("admin_dashboard.html", candidates=candidates)


# ---------------- ADD CANDIDATE ----------------

@app.route("/add_candidate", methods=["POST"])
def add_candidate():

    if "admin" not in session:
        return redirect("/admin_login")

    name = request.form.get("name")
    party = request.form.get("party")

    symbol = request.files["symbol"]
    photo = request.files["photo"]

    symbol_filename = secure_filename(symbol.filename)
    photo_filename = secure_filename(photo.filename)

    symbol_path = os.path.join("static/uploads", symbol_filename)
    photo_path = os.path.join("static/uploads", photo_filename)

    symbol.save(symbol_path)
    photo.save(photo_path)

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO candidates (name,party,symbol,photo,votes) VALUES (?,?,?,?,0)",
        (name, party, symbol_path, photo_path)
    )

    conn.commit()
    conn.close()

    return redirect("/admin")


# ---------------- DELETE CANDIDATE ----------------

@app.route("/delete_candidate/<int:id>")
def delete_candidate(id):

    if "admin" not in session:
        return redirect("/admin_login")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM candidates WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/admin")


# ---------------- DOWNLOAD RESULT ----------------

@app.route("/download_result")
def download_result():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT name,votes FROM candidates")
    data = cursor.fetchall()

    conn.close()

    filename = "result.csv"

    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Candidate", "Votes"])

        for row in data:
            writer.writerow(row)

    return send_file(filename, as_attachment=True)


# ---------------- START ELECTION ----------------

@app.route("/start_election")
def start_election():

    if "admin" not in session:
        return redirect("/admin_login")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("UPDATE election_status SET status='running' WHERE id=1")

    conn.commit()
    conn.close()

    return redirect("/admin")


# ---------------- STOP ELECTION ----------------

@app.route("/stop_election")
def stop_election():

    if "admin" not in session:
        return redirect("/admin_login")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("UPDATE election_status SET status='stopped' WHERE id=1")

    conn.commit()
    conn.close()

    return redirect("/admin")


# ---------------- RUN SERVER ----------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
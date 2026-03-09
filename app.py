from flask import Flask, render_template, request, redirect, send_file
import sqlite3
import os
import base64
import csv

app = Flask(__name__)

# Increase upload size to 16MB
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ---------------- DATABASE CONNECTION ----------------

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- HOME PAGE ----------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- REGISTER VOTER ----------------

@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        image_data = request.form["image"]

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM voters WHERE email=?", (email,))
        user = cursor.fetchone()

        if user:
            conn.close()
            return "⚠ This email is already registered!"

        image_data = image_data.split(",")[1]
        image_bytes = base64.b64decode(image_data)

        filename = email + ".png"
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        with open(filepath,"wb") as f:
            f.write(image_bytes)

        cursor.execute(
            "INSERT INTO voters (name,email,photo,has_voted) VALUES (?,?,?,0)",
            (name,email,filepath)
        )

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")


# ---------------- LOGIN PAGE ----------------

@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        image_data = request.form["image"]

        # convert captured image
        image_data = image_data.split(",")[1]
        image_bytes = base64.b64decode(image_data)

        nparr = np.frombuffer(image_bytes, np.uint8)
        captured_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        captured_img = cv2.resize(captured_img,(200,200))

        conn = sqlite3.connect("database.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM voters")
        voters = cursor.fetchall()

        matched_user = None

        for user in voters:

            stored_img = cv2.imread(user["photo"])

            stored_img = cv2.resize(stored_img,(200,200))

            diff = cv2.absdiff(stored_img,captured_img)

            score = np.mean(diff)

            if score < 50:   # threshold
                matched_user = user
                break

        if matched_user:

            if matched_user["has_voted"] == 1:
                return "You have already voted"

            cursor.execute("SELECT * FROM candidates")
            candidates = cursor.fetchall()

            return render_template(
                "vote.html",
                user=matched_user,
                candidates=candidates
            )

        else:
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

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT status FROM election_status WHERE id=1")
    status = cursor.fetchone()[0]

    if status == "stopped":
        return "Election has been stopped by admin!"

    user_id = request.form["user_id"]
    candidate_id = request.form["candidate"]

    cursor.execute("UPDATE candidates SET votes=votes+1 WHERE id=?", (candidate_id,))
    cursor.execute("UPDATE voters SET has_voted=1 WHERE id=?", (user_id,))

    conn.commit()
    conn.close()

    return redirect("/result")


# ---------------- RESULT PAGE ----------------

@app.route("/result")
def result():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT name,votes FROM candidates")
    data = cursor.fetchall()

    conn.close()

    labels = [row["name"] for row in data]
    votes = [row["votes"] for row in data]

    winner = max(data, key=lambda x: x["votes"])["name"]

    return render_template(
        "result.html",
        labels=labels,
        votes=votes,
        winner=winner
    )

# ----------------ADMIN LOGIN ----------------

@app.route("/admin_login", methods=["GET","POST"])
def admin_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
        "SELECT * FROM admin WHERE username=? AND password=?",
        (username,password)
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

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM candidates")
    candidates = cursor.fetchall()

    conn.close()

    return render_template("admin_dashboard.html", candidates=candidates)


# ---------------- ADD CANDIDATE ----------------

@app.route("/add_candidate", methods=["POST"])
def add_candidate():

    name = request.form["name"]
    party = request.form["party"]

    symbol = request.files["symbol"]
    photo = request.files["photo"]

    symbol_path = "static/uploads/" + symbol.filename
    photo_path = "static/uploads/" + photo.filename

    symbol.save(symbol_path)
    photo.save(photo_path)

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO candidates (name,party,symbol,photo,votes) VALUES (?,?,?,?,0)",
        (name,party,symbol_path,photo_path)
    )

    conn.commit()
    conn.close()

    return redirect("/admin")


# ---------------- DELETE CANDIDATE ----------------

@app.route("/delete_candidate/<int:id>")
def delete_candidate(id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM candidates WHERE id=?",
        (id,)
    )

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


#-----------START ELECTION ----------------

@app.route("/start_election")
def start_election():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("UPDATE election_status SET status='running' WHERE id=1")

    conn.commit()
    conn.close()

    return redirect("/admin")
# ---------------- STOP ELECTION ----------------
@app.route("/stop_election")
def stop_election():

    conn = get_db()
    cursor = conn.cursor()

    # change election status to stopped
    cursor.execute("UPDATE election_status SET status='stopped' WHERE id=1")

    conn.commit()
    conn.close()

    return redirect("/admin")

# ---------------- RUN SERVER ----------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
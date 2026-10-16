from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_connection
from config import SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Escalation rule: if the average of the last N check-ins is at or below the threshold,
# we offer the user a counselor referral. Change these two numbers to change the rule.
ESCALATION_COUNT = 3
ESCALATION_THRESHOLD = 2.0

# Words in a journal note that make us show crisis resources straight away
DISTRESS_WORDS = ["hopeless", "worthless", "want to die", "end it all",
                  "hurt myself", "kill myself", "suicide", "no reason to live"]

@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form["full_name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        # Basic validation
        if not full_name or not email or len(password) < 6:
            flash("Please fill in every field. Your password needs at least 6 characters.", "error")
            return render_template("register.html")

        conn = get_connection()
        cursor = conn.cursor()

        # Is this email already taken?
        cursor.execute("SELECT COUNT(*) FROM users WHERE email = :email", {"email": email})
        if cursor.fetchone()[0] > 0:
            cursor.close()
            conn.close()
            flash("That email is already registered. Try logging in instead.", "error")
            return render_template("register.html")

        # Save the new user. We store a hash, never the real password.
        cursor.execute(
            "INSERT INTO users (full_name, email, password_hash) VALUES (:name, :email, :pw)",
            {"name": full_name, "email": email, "pw": generate_password_hash(password)},
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash("Your account is ready. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id, full_name, password_hash FROM users WHERE email = :email",
            {"email": email},
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        # row[2] is the stored hash. check_password_hash compares it with what was typed.
        if row and check_password_hash(row[2], password):
            session["user_id"] = row[0]
            session["name"] = row[1]
            return redirect(url_for("dashboard"))

        flash("Incorrect email or password.", "error")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    # 1. The five most recent check-ins (the list, and also the escalation check)
    cursor.execute(
        """SELECT mood_score, tags, entry_date
           FROM mood_entries
           WHERE user_id = :user_id
           ORDER BY entry_date DESC, entry_id DESC
           FETCH FIRST 5 ROWS ONLY""",
        {"user_id": session["user_id"]},
    )
    entries = cursor.fetchall()

    # 2. Daily numbers for the last 7 days (the chart)
    cursor.execute(
        """SELECT TRUNC(entry_date) AS entry_day,
                  ROUND(AVG(mood_score), 1) AS avg_mood,
                  COUNT(*) AS total,
                  SUM(mood_score) AS score_sum
           FROM mood_entries
           WHERE user_id = :user_id
             AND entry_date >= TRUNC(CURRENT_DATE) - 6
           GROUP BY TRUNC(entry_date)""",
        {"user_id": session["user_id"]},
    )
    daily = {row[0].date(): row for row in cursor.fetchall()}

    # 3. Tips that match the mood of the latest check-in
    tips = []
    if entries:
        cursor.execute(
            """SELECT title, description FROM tips
               WHERE mood_level = :mood
               FETCH FIRST 2 ROWS ONLY""",
            {"mood": entries[0][0]},
        )
        tips = cursor.fetchall()

    # 4. Does the user already have a pending counselor request?
    cursor.execute(
        "SELECT COUNT(*) FROM referrals WHERE user_id = :user_id AND status = 'PENDING'",
        {"user_id": session["user_id"]},
    )
    pending_referral = cursor.fetchone()[0] > 0

    cursor.close()
    conn.close()

    # Escalation rule: average of the last N check-ins at or below the threshold
    recent_scores = [e[0] for e in entries[:ESCALATION_COUNT]]
    escalate = (
        len(recent_scores) == ESCALATION_COUNT
        and sum(recent_scores) / ESCALATION_COUNT <= ESCALATION_THRESHOLD
    )

    # Build exactly 7 days, oldest first. Days with no check-in get None (a gap in the line).
    today = datetime.now().date()
    days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    chart_labels = [d.strftime("%a %d") for d in days]
    chart_values = [float(daily[d][1]) if d in daily else None for d in days]

    week_checkins = sum(row[2] for row in daily.values())
    week_total_score = sum(row[3] for row in daily.values())
    week_avg = round(week_total_score / week_checkins, 1) if week_checkins else None

    return render_template(
        "dashboard.html",
        entries=entries,
        chart_labels=chart_labels,
        chart_values=chart_values,
        week_avg=week_avg,
        week_checkins=week_checkins,
        tips=tips,
        escalate=escalate,
        pending_referral=pending_referral,
    )

@app.route("/checkin", methods=["GET", "POST"])
def checkin():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        # The mood arrives as text, so convert it to a number and validate it
        try:
            mood_score = int(request.form.get("mood_score", ""))
        except ValueError:
            mood_score = 0

        if mood_score < 1 or mood_score > 5:
            flash("Please choose how you are feeling.", "error")
            return render_template("checkin.html")

        tags = ", ".join(request.form.getlist("tags"))   # e.g. "Calm, Grateful"
        note = request.form.get("note", "").strip()

        conn = get_connection()
        cursor = conn.cursor()

        # Save the mood and ask Oracle to hand back the new entry_id
        new_id = cursor.var(int)
        cursor.execute(
            """INSERT INTO mood_entries (user_id, mood_score, tags)
               VALUES (:user_id, :score, :tags)
               RETURNING entry_id INTO :new_id""",
            {"user_id": session["user_id"], "score": mood_score, "tags": tags or None, "new_id": new_id},
        )
        entry_id = new_id.getvalue()[0]

        # Only save a journal note if the user wrote one
        if note:
            cursor.execute(
                "INSERT INTO journal_entries (entry_id, content) VALUES (:eid, :content)",
                {"eid": entry_id, "content": note},
            )

        conn.commit()
        cursor.close()
        conn.close()

        flash("Check-in saved.", "success")

        # If the note contains distress words, also show crisis resources
        if any(word in note.lower() for word in DISTRESS_WORDS):
            flash("It sounds like things feel very heavy right now, and you don't have to carry that alone. "
                  "You can call Tele-MANAS at 14416 (free, 24/7), or reach out to someone you trust. "
                  "If you are in immediate danger, call 112.", "crisis")

        return redirect(url_for("dashboard"))

    return render_template("checkin.html")

@app.route("/referral", methods=["GET", "POST"])
def referral():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT counselor_id, name, specialization FROM counselors ORDER BY name")
    counselors = cursor.fetchall()

    if request.method == "POST":
        counselor_id = request.form.get("counselor_id", "")
        reason = request.form.get("reason", "").strip()[:300]
        consent = request.form.get("consent")

        # Consent is mandatory: we never share anything without it
        if not counselor_id or not consent:
            cursor.close()
            conn.close()
            flash("Please choose a counselor and confirm your consent.", "error")
            return render_template("referral.html", counselors=counselors)

        cursor.execute(
            """INSERT INTO referrals (user_id, counselor_id, reason)
               VALUES (:user_id, :counselor_id, :reason)""",
            {"user_id": session["user_id"], "counselor_id": int(counselor_id), "reason": reason or None},
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash("Your request has been sent. You've taken a good step.", "success")
        return redirect(url_for("dashboard"))

    cursor.close()
    conn.close()
    return render_template("referral.html", counselors=counselors)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, port=5001)
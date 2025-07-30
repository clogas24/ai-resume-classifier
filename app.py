from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import joblib
import os
import fitz  # type: ignore
import requests
import traceback
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sys
sys.path.append("/home/clogas")
from database import get_connection  # type: ignore

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# pre load model and vectorizer for quicker cleaning and classification
model = joblib.load('resume_classifier_model.pkl')
vectorizer = joblib.load('tfidf_vectorizer.pkl')

app = Flask(__name__)
app.secret_key = "clogas" #yes i know this is bad, i couldnt be bothered to fix it since school is done

def login_required(route_func):
    @wraps(route_func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return route_func(*args, **kwargs)
    return wrapper

# home page route
@app.route('/')
@login_required
def index():
    return render_template('index.html')

# jobs page route
@app.route('/jobs')
@login_required
def jobs():
    return render_template('jobs.html')

# profile page route
@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', username=session.get("username"), email=session.get("email"))

# contact page route
@app.route('/contact')
def contact():
    return render_template('contact.html')

# signup page route, also handles the sign up function(checks if username/
# email already exists, then allows them to create account and sends them to index page)
@app.route('/signup', methods=["GET", "POST"])
def signup():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        hashed = generate_password_hash(password)

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM SPusers WHERE username = %s OR email = %s", (username, email))
        user = cursor.fetchone()

        if user:
            error = "Username or email already exists."
        else:
            cursor.execute(
                "INSERT INTO SPusers (username, email, password_hash) VALUES (%s, %s, %s)",
                (username, email, hashed)
            )
            conn.commit()
            user_id = cursor.lastrowid

            session["user_id"] = user_id
            session["email"] = email
            session["username"] = username

            cursor.close()
            conn.close()
            return redirect(url_for("index"))

        cursor.close()
        conn.close()

    return render_template("signup.html", error=error)

# login page route, checks to if the user and password is correct and in the SPusers database
# Password is hashed in the database
@app.route('/login', methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM SPusers WHERE email = %s", (email,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if not user or not check_password_hash(user["password_hash"], password):
            error = "Invalid email or password."
        else:
            session["user_id"] = user["id"]
            session["email"] = user["email"]
            session["username"] = user["username"]
            return redirect(url_for("index"))

    return render_template("login.html", error=error)

# handles the logout feature
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("login"))

# this route handles the paste text part of the resume classifier
@app.route('/predict', methods=['POST'])
@login_required
def predict():
    data = request.get_json()
    resume_text = data.get('resume')
    if not resume_text:
        return jsonify({'error': 'No resume text provided'}), 400
    vector = vectorizer.transform([resume_text])
    prediction = model.predict(vector)[0]
    return jsonify({'predicted_job_category': prediction})

# this route handles the PDF upload function of the website if the user chooses to upload their resume
@app.route('/upload', methods=['POST'])
@login_required
def upload_pdf():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['resume']
    if not file.filename.endswith('.pdf'):
        return jsonify({'error': 'Only PDF files are supported'}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    text = extract_text_from_pdf(filepath)
    if not text.strip():
        return jsonify({'error': 'No text extracted from PDF'}), 400

    vector = vectorizer.transform([text])
    prediction = model.predict(vector)[0]
    return jsonify({'predicted_job_category': prediction})

# this handles the API and rules for the API
@app.route('/api/jobs')
@login_required
def get_remote_jobs():
    category = request.args.get('category', '').strip()
    user_id = session['user_id']

    print(f"Searching JSearch for: '{category}'")

    url = "https://jsearch.p.rapidapi.com/search"
    querystring = {
        "query": f"{category} jobs in remote",
        "page": "1",
        "num_pages": "1",
        "country": "us",
        "date_posted": "all"
    }

    headers = {
        "x-rapidapi-key": "db69f64e3cmshafb87221313df6ep116495jsn98638a118ec7", #yes i know this is bad, i couldnt be bothered to fix it since school is done
        "x-rapidapi-host": "jsearch.p.rapidapi.com"
    }

    conn = get_connection()
    cursor = conn.cursor()

    try:
        response = requests.get(url, headers=headers, params=querystring)
        print(f"Status: {response.status_code}")
        response.raise_for_status()

        api_data = response.json()
        jobs = api_data.get("data", [])

        saved_jobs = []

        # Get jobs user already interacted with
        cursor.execute("""
            SELECT job_id FROM SPuser_jobs WHERE user_id = %s
        """, (user_id,))
        seen_jobs = {row['job_id'] for row in cursor.fetchall()}

        for job in jobs:
            job_title = job.get("job_title", "Unknown Title")
            company = job.get("employer_name", "Unknown Company")
            location = job.get("job_city", "Remote") or job.get("job_country", "Remote")
            url_link = job.get("job_apply_link", "")

            # Check if job already exists by title + company
            cursor.execute("SELECT id FROM SPjobs WHERE title = %s AND company = %s", (job_title, company))
            existing = cursor.fetchone()

            if existing:
                job_id = existing["id"]
            else:
                cursor.execute(
                    "INSERT INTO SPjobs (title, company, location, url) VALUES (%s, %s, %s, %s)",
                    (job_title, company, location, url_link)
                )
                conn.commit()
                job_id = cursor.lastrowid

            if job_id not in seen_jobs:
                saved_jobs.append({
                    "job_id": job_id,
                    "job_title": job_title,
                    "employer_name": company,
                    "job_city": location,
                    "job_country": "",
                    "job_apply_link": url_link
                })

        return jsonify({"data": saved_jobs})

    except Exception as e:
        print("JSearch API error:", e)
        traceback.print_exc()
        return jsonify({"data": []}), 200
    finally:
        cursor.close()
        conn.close()

# allows user to save, like, dislike jobs on the jobs page
@app.route('/api/save_job', methods=['POST'])
@login_required
def save_job():
    data = request.get_json()
    job_id = data.get('job_id')
    status = data.get('status')
    user_id = session['user_id']

    if not job_id or status not in ['liked', 'disliked', 'saved']:
        return jsonify({'error': 'Invalid input'}), 400

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # check if already exists
        cursor.execute("""
            SELECT id FROM SPuser_jobs WHERE user_id = %s AND job_id = %s
        """, (user_id, job_id))
        existing = cursor.fetchone()

        if existing:
            # if exists, update
            cursor.execute("""
                UPDATE SPuser_jobs SET status = %s WHERE id = %s
            """, (status, existing['id']))
        else:
            # if not exists, insert new
            cursor.execute("""
                INSERT INTO SPuser_jobs (user_id, job_id, status)
                VALUES (%s, %s, %s)
            """, (user_id, job_id, status))

        conn.commit()
        return jsonify({'success': True})

    except Exception as e:
        print("Save job error:", e)
        traceback.print_exc()
        return jsonify({'error': 'Database error'}), 500
    finally:
        cursor.close()
        conn.close()

# pulls the jobs from saved, liked, dislikes part of the database and displays them
@app.route('/api/profile_jobs')
@login_required
def profile_jobs():
    user_id = session['user_id']

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT SPjobs.id AS job_id, SPjobs.title, SPjobs.company, SPjobs.location, SPjobs.url, SPuser_jobs.status
            FROM SPuser_jobs
            JOIN SPjobs ON SPuser_jobs.job_id = SPjobs.id
            WHERE SPuser_jobs.user_id = %s
        """, (user_id,))
        rows = cursor.fetchall()

        liked = []
        saved = []
        disliked = []

        for row in rows:
            job = {
                'job_id': row['job_id'],
                'title': row['title'],
                'company': row['company'],
                'location': row['location'],
                'url': row['url']
            }
            if row['status'] == 'liked':
                liked.append(job)
            elif row['status'] == 'saved':
                saved.append(job)
            elif row['status'] == 'disliked':
                disliked.append(job)

        return jsonify({
            "liked": liked,
            "saved": saved,
            "disliked": disliked
        })

    except Exception as e:
        print("Profile job fetch error:", e)
        traceback.print_exc()
        return jsonify({"liked": [], "saved": [], "disliked": []})
    finally:
        cursor.close()
        conn.close()

# handles if the user wants to remove a job from the profile whether its on the liked, disliked, or saved part
@app.route('/api/remove_job', methods=['POST'])
@login_required
def remove_job():
    data = request.get_json()
    job_id = data.get('job_id')
    user_id = session['user_id']

    if not job_id:
        return jsonify({'error': 'Invalid input'}), 400

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE FROM SPuser_jobs WHERE user_id = %s AND job_id = %s
        """, (user_id, job_id))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        print("Remove job error:", e)
        traceback.print_exc()
        return jsonify({'error': 'Database error'}), 500
    finally:
        cursor.close()
        conn.close()

# handles extracting the text from the PDF if the user decides to upload their resume
def extract_text_from_pdf(pdf_path):
    print(f"Opening PDF at: {pdf_path}")
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            page_text = page.get_text()
            print(f"Extracted from page {page.number}: {repr(page_text[:100])}")
            text += page_text
        return text
    except Exception as e:
        print("Error reading PDF:", e)
        return ""

# hosts at the port 8123
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8123))
    app.run(host='0.0.0.0', port=port)

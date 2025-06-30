# AI-Powered Resume Classifier

> **⚠️ Project Status:**
> The backend services (MySQL on Turing & JSearch API) are no longer operational.
> This repository is provided **solely for code review and learning**—it cannot be run live.

A Flask web application that classifies pasted or uploaded resumes into job roles using scikit-learn, then (when it was live) fetched remote job listings via the JSearch API.

---

## 📂 Tech Stack

* **Language:** Python 3.12
* **Web Framework:** Flask
* **ML:** scikit-learn (TF-IDF + classifier pipeline)
* **Database:** MySQL (tables prefixed `SP`)
* **Frontend:** HTML5, CSS3, JavaScript
* **APIs:** JSearch API
* **Deployment (original):** Turing (Linux, port 8123)

---

## 🔍 Project Structure

```
SeniorProject/
├── app.py
├── schema.sql
├── requirements.txt
├── config_example.env
├── resume_classifier_model.pkl
├── tfidf_vectorizer.pkl
├── UpdatedResumeDataSet.csv
├── Resume.csv
├── notes.txt
├── static/
│   ├── style.css
│   ├── script.js
│   ├── jobs.js
│   └── profile.js
├── templates/
│   ├── index.html
│   ├── signup.html
│   ├── login.html
│   ├── contact.html
│   ├── jobs.html
│   └── profile.html
└── uploads/          ← sample user-uploaded resumes
```

* **app.py** — Flask routes, model loading, classification logic, user auth stubs
* **schema.sql** — MySQL schema dump (tables `SPusers`, `SPuser_jobs`, etc.)
* **config\_example.env** — placeholder for API keys and DB URL
* **requirements.txt** — pinned Python dependencies
* **model & vectorizer** — `resume_classifier_model.pkl`, `tfidf_vectorizer.pkl`
* **datasets** — two CSV files used for training: `UpdatedResumeDataSet.csv`, `Resume.csv`
* **static/** — CSS & JS for client-side interactions
* **templates/** — Jinja2 HTML templates for pages
* **uploads/** — example resume files used in testing

---

## 🚧 Code Overview

1. **Authentication (MySQL-backed)**

   * Signup/Login routes write to/read from `SPusers` table
   * Session management via Flask’s `SECRET_KEY`

2. **Classification Pipeline**

   * Loads TF-IDF vectorizer + trained scikit-learn model
   * Accepts resume **text** or **PDF** uploads (`uploads/`)
   * Outputs a job-role label

3. **Job Listings (JSearch API)**

   * For each predicted label, fetched remote job data
   * Provided Like/Save/Dislike actions, stored in `SPuser_jobs`

4. **Frontend & UX**

   * Responsive layout with forms for upload/paste
   * Protected routes (only authenticated users access `/jobs`, `/profile`)

---

## 📖 How to Explore the Code

1. **Clone this repo**

   ```bash
   git clone https://github.com/clogas24/ai-resume-classifier.git
   cd ai-resume-classifier
   ```

2. **Browse the core files**

   * **app.py** for routing & logic
   * **templates/** for page structure
   * **static/** for styling & client-side scripts

3. **Inspect the ML artifacts**

   * `resume_classifier_model.pkl` & `tfidf_vectorizer.pkl`: see how the pipeline is built in `app.py`

4. **Review the database schema**

   * Open `schema.sql` to understand table design (`SPusers`, `SPuser_jobs`)

5. **Read `notes.txt`** for development reminders and data nuances.

> Nothing to install—this is a read-only snapshot of the project as it stood in Spring 2025.

---

This project is for educational purposes only

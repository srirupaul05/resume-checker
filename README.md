# Resume Checker

A simple web app that reviews your resume, scores how professional it looks, and suggests which professions you fit best based on your skills.

**Live demo:** [https://resume-checker-8y06.onrender.com]

> The demo runs on a free hosting plan, so the first load after a period of inactivity can take up to a minute.

## Features

- Upload a resume as **PDF, DOCX or TXT**
- **Professionalism score** out of 100
- **Top 3 best-fit professions** (Data Scientist, ML Engineer, Backend, Frontend, DevOps, UI/UX and more) with skills found and skills to add
- **Fix list** with clear tips: missing contact details, links and sections, resume length, weak action verbs, missing numbers and results, clichés, and first-person pronouns
- Uploaded files are read in memory and are **not stored**

## How it works

The app extracts text from your resume, then runs rule-based checks (sections, contact info, length, action verbs, measurable results) and compares your skills against keyword lists for each profession. It is a quick first check, not a replacement for human feedback.

## Tech stack

- Python 3
- Flask
- pypdf (PDF text extraction)
- python-docx (DOCX text extraction)
- Gunicorn (production server)
- Hosted on Render

## Run it locally

```bash
# 1. Clone the repo
git clone https://github.com/RIRU-BIt/resume-checker.git
cd resume-checker

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the app
python resume_analyzer.py
```

Then open http://127.0.0.1:5000 in your browser.

## Project structure

```
resume-checker/
├── resume_analyzer.py   # Flask app, checks and profession matching
├── requirements.txt     # Python dependencies
└── README.md
```

## Customize

To add or change professions, edit the `PROFESSIONS` dictionary at the top of `resume_analyzer.py`. Each profession is a list of keywords the app looks for in a resume.

## Deploy on Render

1. Push the code to GitHub
2. On Render, create a **New Web Service** and connect the repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn resume_analyzer:app`
5. Add the environment variable `PYTHON_VERSION` set to `3.12.7`

## Future ideas

- AI-written feedback using the Claude API
- OCR support for scanned PDFs
- More professions and a job-description matching mode

import re
from io import BytesIO

from flask import Flask, request, render_template_string
from pypdf import PdfReader
from docx import Document

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB upload limit

# ---------- Profession keywords ----------
PROFESSIONS = {
    "Data Scientist": ["python", "pandas", "numpy", "scikit-learn", "statistics", "machine learning",
                       "tensorflow", "pytorch", "data visualization", "sql", "jupyter", "deep learning"],
    "Machine Learning Engineer": ["python", "pytorch", "tensorflow", "deep learning", "nlp", "computer vision",
                                  "mlops", "docker", "model deployment", "neural network", "scikit-learn"],
    "Data Analyst": ["excel", "sql", "power bi", "tableau", "python", "pandas", "dashboard",
                     "data cleaning", "statistics", "reporting", "visualization"],
    "Backend Developer": ["python", "flask", "django", "node.js", "api", "rest", "sql", "postgresql",
                          "mongodb", "docker", "redis", "git", "java"],
    "Frontend Developer": ["javascript", "react", "html", "css", "typescript", "tailwind", "responsive",
                           "next.js", "redux", "figma", "git"],
    "Full Stack Developer": ["react", "node.js", "javascript", "api", "sql", "mongodb", "html", "css",
                             "git", "express", "docker", "typescript"],
    "Mobile App Developer": ["flutter", "dart", "kotlin", "swift", "react native", "android", "ios",
                             "firebase", "api", "mobile"],
    "DevOps / Cloud Engineer": ["docker", "kubernetes", "aws", "azure", "gcp", "ci/cd", "linux",
                                "terraform", "jenkins", "github actions", "bash"],
    "Cybersecurity Analyst": ["security", "penetration testing", "network", "firewall", "vulnerability",
                              "siem", "encryption", "linux", "owasp", "incident response"],
    "UI/UX Designer": ["figma", "wireframe", "prototype", "user research", "usability", "adobe xd",
                       "design system", "user flow", "ux", "ui"],
    "Digital Marketer": ["seo", "social media", "content", "google analytics", "campaign", "email marketing",
                         "copywriting", "ads", "branding", "marketing"],
    "Project / Product Manager": ["agile", "scrum", "roadmap", "stakeholder", "jira", "product",
                                  "requirements", "planning", "leadership", "budget"],
}

# ---------- Checking rules ----------
SECTIONS = {
    "Summary / Objective": r"summary|objective|profile|about me",
    "Education": r"education|academic",
    "Experience / Internships": r"experience|employment|internships?|work history",
    "Projects": r"projects?",
    "Skills": r"skills|technologies|tech stack",
    "Achievements / Certifications": r"achievements?|certifications?|awards?|publications?",
}

ACTION_VERBS = {
    "built", "developed", "designed", "implemented", "led", "created", "improved", "optimized",
    "launched", "automated", "analyzed", "managed", "reduced", "increased", "deployed", "trained",
    "achieved", "engineered", "delivered", "collaborated", "researched", "organized", "established",
    "streamlined", "integrated", "architected", "mentored", "initiated", "executed", "solved",
}

WEAK_PHRASES = [
    "responsible for", "worked on", "helped with", "hardworking", "team player", "fast learner",
    "good communication", "duties included", "references available", "detail oriented",
]


def extract_text(f):
    name = f.filename.lower()
    data = f.read()
    if name.endswith(".pdf"):
        return "\n".join(p.extract_text() or "" for p in PdfReader(BytesIO(data)).pages)
    if name.endswith(".docx"):
        return "\n".join(p.text for p in Document(BytesIO(data)).paragraphs)
    if name.endswith(".txt"):
        return data.decode("utf-8", errors="ignore")
    return None


def has_term(term, text):
    return re.search(r"(?<![\w+#])" + re.escape(term) + r"(?![\w+#])", text) is not None


def check_resume(text):
    low = text.lower()
    words = re.findall(r"\b\w+\b", text)
    checks = []  # (label, passed, points, tip)

    # Contact info
    email = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)
    checks.append(("Email address", bool(email), 8,
                   "Add a professional email (e.g. firstname.lastname@gmail.com)."))
    if email:
        local = email.group().split("@")[0]
        ok = len(re.findall(r"\d", local)) < 4
        checks.append(("Professional-looking email", ok, 4,
                       "Your email has many digits. Use a cleaner, name-based address."))
    checks.append(("Phone number", bool(re.search(r"(\+?\d[\d\s()-]{8,}\d)", text)), 6,
                   "Add a phone number with country code."))
    checks.append(("LinkedIn / GitHub / portfolio link",
                   bool(re.search(r"linkedin\.com|github\.com|portfolio|behance\.net", low)), 8,
                   "Add your LinkedIn and GitHub (or portfolio) links."))

    # Sections
    for label, pat in SECTIONS.items():
        found = re.search(rf"^\s*(?:{pat})\b", text, re.I | re.M) is not None
        checks.append((f"Section: {label}", found, 5,
                       f"Add a clear '{label.split(' /')[0]}' section heading."))

    # Length
    n = len(words)
    checks.append(("Good length (250-800 words)", 250 <= n <= 800, 8,
                   f"Your resume has about {n} words. "
                   + ("Add more detail on projects and impact." if n < 250
                      else "Trim it. Aim for one page (two max for experienced people).")))

    # Content quality
    verbs = sum(1 for w in re.findall(r"[a-z]+", low) if w in ACTION_VERBS)
    checks.append(("Strong action verbs (5+)", verbs >= 5, 8,
                   "Start bullets with verbs like Built, Developed, Optimized, Led, Automated."))

    no_years = re.sub(r"\b(19|20)\d{2}\b", "", text)
    numbers = re.findall(r"\d+(?:\.\d+)?\s*(?:%|\+|k\b|x\b)|[$₹]\s?\d+|\b\d{2,}\b", no_years)
    checks.append(("Measurable results (3+ numbers)", len(numbers) >= 3, 10,
                   "Quantify your impact, e.g. 'Improved accuracy by 12%' or 'Served 500+ users'."))

    weak = [p for p in WEAK_PHRASES if p in low]
    checks.append(("No clichés / weak phrases", not weak, 6,
                   "Replace weak phrases (" + ", ".join(weak) + ") with specific achievements."))

    pronouns = len(re.findall(r"\b(i|my|me)\b", low))
    checks.append(("No first-person pronouns", pronouns <= 2, 4,
                   "Remove 'I' and 'my'. Write bullets without pronouns."))

    bullets = len(re.findall(r"^\s*[•\-\*●▪◦]", text, re.M))
    checks.append(("Uses bullet points", bullets >= 5, 4,
                   "Use short bullet points instead of long paragraphs."))

    score = round(sum(p for _, ok, p, _ in checks if ok) / sum(p for _, _, p, _ in checks) * 100)
    return score, checks


def match_professions(text):
    low = text.lower()
    results = []
    for prof, kws in PROFESSIONS.items():
        found = [k for k in kws if has_term(k, low)]
        missing = [k for k in kws if k not in found]
        results.append({"name": prof, "pct": round(len(found) / len(kws) * 100),
                        "found": found, "missing": missing})
    results.sort(key=lambda r: r["pct"], reverse=True)
    return results[:3]


PAGE = """
<!doctype html>
<html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Resume Checker</title>
<style>
  body{font-family:system-ui,sans-serif;max-width:760px;margin:30px auto;padding:0 16px;color:#222}
  .card{border:1px solid #ddd;border-radius:12px;padding:16px;margin:16px 0}
  .score{font-size:44px;font-weight:700}
  .bar{background:#eee;border-radius:8px;height:12px;overflow:hidden}
  .bar>div{background:#2f7df6;height:100%}
  .ok{color:#188038}.bad{color:#c5221f}
  .tag{display:inline-block;background:#e8f0fe;border-radius:12px;padding:2px 10px;margin:2px;font-size:13px}
  .miss{background:#fce8e6}
  button{background:#2f7df6;color:#fff;border:0;border-radius:8px;padding:10px 18px;font-size:16px}
</style></head><body>
<h2>Resume Checker</h2>
<form method="post" enctype="multipart/form-data" class="card">
  <input type="file" name="file" accept=".pdf,.docx,.txt" required>
  <button>Analyze</button>
</form>

{% if error %}<p class="bad">{{ error }}</p>{% endif %}

{% if score is not none %}
  <div class="card">
    <div class="score">{{ score }}/100</div>
    <div>Professionalism score</div>
  </div>

  <div class="card">
    <h3>Best-fit professions</h3>
    {% for p in professions %}
      <p><b>{{ p.name }}</b> ({{ p.pct }}% match)</p>
      <div class="bar"><div style="width:{{ p.pct }}%"></div></div>
      <p>{% for k in p.found %}<span class="tag">{{ k }}</span>{% endfor %}
         {% for k in p.missing[:5] %}<span class="tag miss">+ {{ k }}</span>{% endfor %}</p>
    {% endfor %}
    <small>Blue = skills found. Red = skills to add if you want this career.</small>
  </div>

  <div class="card">
    <h3>What to fix</h3>
    {% for label, ok, tip in checks if not ok %}
      <p class="bad">&#10008; <b>{{ label }}</b><br>{{ tip }}</p>
    {% else %}
      <p class="ok">Nothing to fix. Great resume!</p>
    {% endfor %}
  </div>

  <div class="card">
    <h3>What you did well</h3>
    {% for label, ok, tip in checks if ok %}
      <p class="ok">&#10004; {{ label }}</p>
    {% endfor %}
  </div>
{% endif %}
</body></html>
"""


@app.route("/", methods=["GET", "POST"])
def home():
    ctx = {"score": None, "checks": [], "professions": [], "error": None}
    if request.method == "POST":
        f = request.files.get("file")
        if not f or not f.filename:
            ctx["error"] = "Please choose a file."
        else:
            text = extract_text(f)
            if text is None:
                ctx["error"] = "Unsupported file type. Use PDF, DOCX or TXT."
            elif len(text.strip()) < 50:
                ctx["error"] = "Couldn't read text from this file (scanned PDFs need OCR)."
            else:
                score, checks = check_resume(text)
                ctx.update(score=score,
                           checks=[(l, ok, tip) for l, ok, _, tip in checks],
                           professions=match_professions(text))
    return render_template_string(PAGE, **ctx)


if __name__ == "__main__":
    app.run(debug=True)
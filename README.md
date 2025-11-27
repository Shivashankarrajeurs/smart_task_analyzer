# Smart Task Analyzer

Repository for the **Smart Task Analyzer** — a small Django backend + simple frontend that analyzes and ranks tasks by priority using a multi-factor scoring algorithm.

---

## Repo structure

backend/
├─ manage.py
├─ task_analyzer/
│ ├─ settings.py
│ └─ urls.py
├─ tasks/
│ ├─ models.py
│ ├─ views.py
│ ├─ scoring.py
│ ├─ serializers.py
│ └─ tests.py
└─ requirements.txt

frontend/
├─ index.html
├─ style.css
└─ script.js

README.md
.gitignore




---

## Quick Setup (Run locally)

> Tested with Python 3.10+ and Django 4+/5.x on Windows (Git Bash) and Linux/Mac.

1. Clone the repo:
```bash
git clone <your-repo-url>
cd <repo-folder>/backend

2. Create & activate a virtual environment (Git Bash / Linux / macOS):

python -m venv .venv
source .venv/bin/activate

3. Install dependencies:

pip install -r requirements.txt

4. Apply migrations and run tests:

python manage.py makemigrations
python manage.py migrate
python manage.py test

5. Start the development server:

python manage.py runserver

6.Open the frontend:

If using static files served separately, open frontend/index.html in your browser (the frontend talks to http://127.0.0.1:8000 by default).

If you prefer, you can serve frontend files via Django staticfiles or a simple static server.


API Endpoints

POST /api/tasks/analyze/ — Accepts an array of task objects and returns tasks sorted by priority with score and explanation.

GET /api/tasks/suggest/ — Returns top 3 recommended tasks from last analysis (or accept tasks via query param).

Task object schema used by API:

{
  "id": "T1",               // optional (frontend auto-generates)
  "title": "Fix login bug",
  "due_date": "YYYY-MM-DD",
  "estimated_hours": 3,
  "importance": 1-10,
  "dependencies": ["T2","T3"]  // optional, IDs of other tasks
}


Algorithm Explanation

The scoring algorithm blends urgency, importance, effort and dependency influence to produce a normalized priority value for each task. This multi-factor approach mirrors real-world tradeoffs: urgent tasks should be addressed quickly, important tasks may require more investment but yield more impact, and low-effort tasks can deliver quick wins. Tasks that block others gain extra priority because resolving them unlocks downstream work.

Components

Urgency — measured from the task due date. Overdue tasks receive the highest urgency. The mapping is coarse and intentional: overdue → 10, due today → 9, within 3 days → 7, within 7 days → 5, otherwise → 3. This provides a robust signal without needing fine-grained tuning for every day.

Importance — the user-provided 1–10 rating. It is used directly since it already matches the 0–10 scale.

Effort (Quick-win) — inversely proportional to estimated hours. Short tasks score higher (quick wins). The simple mapping (e.g., <=1h → 8, <=3h → 6, <=6h → 4, else → 2) encourages finishing small tasks, useful for momentum.

Dependencies — tasks with many dependents receive higher priority because removing blockers multiplies team productivity. We count how many other tasks depend on the given task.

Combining and normalization

Weights are configurable (defaults were chosen by experiment):

Urgency: 0.40

Importance: 0.35

Effort: 0.15

Dependencies: 0.10

Each component returns a 0–10 style value. The weighted sum yields a raw score which is then scaled/clamped to 0–10 so UI and comparisons are easy and consistent.

Cycle detection & Validation

Dependencies may introduce cycles. We perform a simple DFS cycle detection and return a clear error describing the cycle. This ensures the algorithm doesn’t accidentally infinite-loop and provides helpful debugging for the user. Input validation is handled with DRF serializers — missing/invalid data leads to informative 400 errors.

Why this design?

Six months of practical development shows teams value simple, explainable heuristics over opaque models for prioritization. The algorithm is deterministic and debuggable. We deliberately kept mappings coarse (e.g., urgency buckets) to avoid overfitting and to match human mental models (overdue, due soon, etc.).

We added hooks to adjust weights for different strategies (Fastest Wins, High Impact, Deadline Driven, Smart Balance). The frontend can modify weights or perform local scoring to preview results.

Design decisions & trade-offs

Simplicity vs accuracy: I favored clear, explainable heuristics over complex ML models. This keeps the product easy to test and maintain.

Stateless API with optional cache: The API is primarily stateless; a small module-level cache holds last analyzed results so /api/tasks/suggest/ can return top 3 without re-submission. This simplifies the assignment while providing good UX.

Dependencies as IDs: Dependencies use string IDs (not positional indexes) for clarity and to avoid brittle order-based mappings.

SQLite default: Default Django SQLite keeps the project simple to run locally.

Unit tests

tasks/tests.py contains 3+ tests covering:

Scoring ordering and fields

Cycle detection raises an error on cyclic graph

Cycle-free examples pass

Run python manage.py test to execute them.



Future improvements

Add user preferences to persist weighting per user and save task lists.

Visual timeline or Gantt view to surface deadline clusters.

Add authenticated multi-user support and persistent DB for tasks (task ownership).

Replace heuristic scoring with a learning-to-rank model trained on historical completion data.

Add e2e tests and accessibility improvements.
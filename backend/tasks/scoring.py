
from datetime import datetime, date

# weights
WEIGHTS = {
    "urgency": 4.0,
    "importance": 3.0,
    "effort": 2.0,       
    "dependencies": 1.0  
}
# cache
LAST_ANALYZED = []


# cycle checking

def detect_cycles(task_map):
    def visit(task_id, path):
        if task_id in path:
            raise ValueError(f"Circular dependency detected: {' -> '.join(path + [task_id])}")
        path.append(task_id)
        for dep in task_map[task_id].get("dependencies", []):
            if dep in task_map:
                visit(dep, path.copy())
    for tid in task_map:
        visit(tid, [])


def calc_urgency(due):
    today = datetime.now().date()
    if isinstance(due, str):
        due = datetime.strptime(due, "%Y-%m-%d").date()
    elif isinstance(due, date):
        pass
    else:
        return 0
    days_left = (due - today).days
    if days_left < 0:
        return 10
    if days_left == 0:
        return 9
    if days_left <= 3:
        return 7
    if days_left <= 7:
        return 5
    return 3

def calc_effort(hours):
    hours = max(hours, 0)  
    return 1 / (1 + hours)  

# scoring fun
def score_tasks(tasks):
    """
    tasks: list of dicts
    Each task must have 'id', 'title', 'due_date', 'estimated_hours', 'importance', 'dependencies'
    """
   
    for idx, task in enumerate(tasks):
      if "id" not in task:
         task["id"] = str(idx)

    task_map = {t["id"]: t for t in tasks}

    
    for t in tasks:
        for d in t.get("dependencies", []):
           if d not in task_map:
              raise ValueError(f"Task {t['id']} has invalid dependency {d}")

    # cycle detection
    detect_cycles(task_map)

    # count the number of dependents
    dependents_count = {tid: 0 for tid in task_map}
    for t in tasks:
        for d in t.get("dependencies", []):
            dependents_count[d] += 1

    scored = []
    for t in tasks:
        urgency = calc_urgency(t.get("due_date", datetime.now().date()))
        importance = t.get("importance", 5)
        effort = calc_effort(t.get("estimated_hours", 1))
        dependency_score = dependents_count.get(t["id"], 0)

        raw_score = (
            urgency * WEIGHTS["urgency"] +
            importance * WEIGHTS["importance"] +
            effort * WEIGHTS["effort"] +
            dependency_score * WEIGHTS["dependencies"]
        )

        # Normalize to 0-10
        score = max(0, min(10, raw_score / 10))  # simple scaling

        # Build explanation
        explanation = []
        days_left = (datetime.strptime(t["due_date"], "%Y-%m-%d").date() - datetime.now().date()).days if isinstance(t["due_date"], str) else (t["due_date"] - datetime.now().date()).days
        if days_left < 0:
            explanation.append("Overdue")
        elif days_left == 0:
            explanation.append("Due today")
        elif days_left <= 3:
            explanation.append("Due soon")

        if importance >= 8:
            explanation.append("High importance")
        elif importance <= 3:
            explanation.append("Low importance")

        if t.get("estimated_hours", 1) <= 2:
            explanation.append("Low effort (quick win)")
        elif t.get("estimated_hours", 1) >= 6:
            explanation.append("High effort")

        if dependency_score > 0:
            explanation.append(f"Blocks {dependency_score} task(s)")

        scored.append({
            **t,
            "score": round(score, 2),
            "explanation": ". ".join(explanation)
        })

    # Sort descending
    scored.sort(key=lambda x: x["score"], reverse=True)

    global LAST_ANALYZED
    LAST_ANALYZED = scored

    return scored

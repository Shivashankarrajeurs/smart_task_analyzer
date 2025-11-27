let tasks = [];
let taskIdCounter = 0;

const taskForm = document.getElementById('task-form');
const bulkInput = document.getElementById('bulk-tasks');
const addBulkBtn = document.getElementById('add-bulk');
const analyzeBtn = document.getElementById('analyze-tasks');
const taskList = document.getElementById('task-list');
const top3List = document.getElementById('top3-list');
const sortStrategy = document.getElementById('sort-strategy');
const feedback = document.getElementById('feedback');

// Render task cards
function renderTasks(scoredTasks = []) {
    taskList.innerHTML = '';
    scoredTasks.forEach(t => {
        const div = document.createElement('div');
        div.className = `task-card ${getPriorityClass(t.score)}`;
        div.innerHTML = `<strong>${t.title}</strong> (Due: ${t.due_date})<br>
                         Score: ${t.score ?? 'N/A'}<br>
                         Hours: ${t.estimated_hours} | Importance: ${t.importance}<br>
                         ${t.explanation ?? ''}`;
        taskList.appendChild(div);
    });
}

// Render top 3 recommendations
function renderTop3(top3) {
    top3List.innerHTML = '';
    top3.forEach(t => {
        const div = document.createElement('div');
        div.className = `task-card ${getPriorityClass(t.score)}`;
        div.innerHTML = `<strong>${t.title}</strong> (Due: ${t.due_date})<br>
                         Score: ${t.score ?? 'N/A'}<br>
                         ${t.explanation ?? ''}`;
        top3List.appendChild(div);
    });
}

// Map score to color class
function getPriorityClass(score) {
    if (score >= 7) return 'high';
    if (score >= 4) return 'medium';
    return 'low';
}

// Add individual task
taskForm.addEventListener('submit', e => {
    e.preventDefault();
    const title = document.getElementById('title').value.trim();
    const due_date = document.getElementById('due_date').value;
    const estimated_hours = parseFloat(document.getElementById('estimated_hours').value);
    const importance = parseInt(document.getElementById('importance').value);
    const dependencies = document.getElementById('dependencies').value
        .split(',').map(d => d.trim()).filter(d => d !== '').map(Number);

    if (!title || !due_date || isNaN(estimated_hours) || isNaN(importance)) {
        feedback.innerText = 'Please fill all required fields correctly.';
        return;
    }

    const task = {
        id: taskIdCounter++,
        title,
        due_date,
        estimated_hours,
        importance,
        dependencies
    };
    tasks.push(task);
    taskForm.reset();
    renderTasks(tasks);
    feedback.innerText = '';
});

// Add bulk tasks
addBulkBtn.addEventListener('click', () => {
    try {
        const bulkTasks = JSON.parse(bulkInput.value);
        bulkTasks.forEach(t => {
            t.id = taskIdCounter++;
            t.dependencies = t.dependencies || [];
            tasks.push(t);
        });
        bulkInput.value = '';
        renderTasks(tasks);
        feedback.innerText = '';
    } catch (err) {
        feedback.innerText = 'Invalid JSON for bulk tasks.';
    }
});

// Analyze tasks with sorting strategy
analyzeBtn.addEventListener('click', async () => {
    if (!tasks.length) {
        feedback.innerText = 'No tasks to analyze.';
        return;
    }
    feedback.innerText = 'Analyzing tasks...';

    // Adjust weights based on selected strategy
    let strategy = sortStrategy.value;
    let tasksToSend = JSON.parse(JSON.stringify(tasks)); // deep copy

    tasksToSend.forEach(t => {
        t.urgency_weight = 1;
        t.importance_weight = 1;
        t.effort_weight = 1;
        t.dependency_weight = 1;

        switch (strategy) {
            case 'fastest':
                t.effort_weight = 3;        // low-effort tasks prioritized
                t.importance_weight = 0.5;
                t.urgency_weight = 0.5;
                t.dependency_weight = 0.5;
                break;
            case 'high-impact':
                t.importance_weight = 3;    // importance prioritized
                t.effort_weight = 0.5;
                t.urgency_weight = 0.5;
                t.dependency_weight = 0.5;
                break;
            case 'deadline':
                t.urgency_weight = 3;       // deadline prioritized
                t.importance_weight = 0.5;
                t.effort_weight = 0.5;
                t.dependency_weight = 0.5;
                break;
            case 'smart':
                // balanced weights, keep default
                break;
        }
    });

    try {
        const res = await fetch('http://localhost:8000/api/tasks/analyze/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(tasksToSend)
        });

        if (!res.ok) {
            const errorData = await res.json();
            feedback.innerText = 'Error analyzing tasks: ' + JSON.stringify(errorData);
            return;
        }

        const scoredTasks = await res.json();
        tasks = scoredTasks.map(t => ({ ...t }));
        renderTasks(scoredTasks);

        // Fetch top 3 suggestions
        const top3Res = await fetch('http://localhost:8000/api/tasks/suggest/');
        if (!top3Res.ok) {
            feedback.innerText = 'Error fetching top 3 suggestions.';
            return;
        }
        const top3 = await top3Res.json();
        renderTop3(top3);

        feedback.innerText = 'Analysis complete.';
    } catch (err) {
        feedback.innerText = 'Error: ' + err;
    }
});

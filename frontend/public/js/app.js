const apiBaseUrl = '';
const form = document.getElementById('workout-form');
const userForm = document.getElementById('user-form');
const resultBox = document.getElementById('result');
const caloriesEl = document.getElementById('calories');
const historyList = document.getElementById('history-list');
const userMessage = document.getElementById('user-message');

function showUserMessage(message, isError = false) {
  userMessage.textContent = message;
  userMessage.classList.toggle('error', isError);
}

async function request(path, options = {}) {
  const response = await fetch(`${apiBaseUrl}${path}`, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || `Request failed (${response.status})`);
  return data;
}

userForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const payload = { name: document.getElementById('user-name').value.trim(), age: Number(document.getElementById('user-age').value), email: document.getElementById('user-email').value.trim() };
  const weight = document.getElementById('user-weight').value;
  const height = document.getElementById('user-height').value;
  if (weight) payload.weightKg = Number(weight);
  if (height) payload.heightCm = Number(height);
  try {
    const data = await request('/api/users', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    showUserMessage(`Profile saved for ${data.name}.`);
    userForm.reset();
  } catch (error) {
    showUserMessage(`Could not save profile: ${error.message}`, true);
  }
});

async function loadHistory() {
  try {
    const workouts = await request('/api/workouts');
    historyList.innerHTML = workouts.length ? '' : '<li>No workouts yet.</li>';
    workouts.slice(0, 5).forEach((workout) => {
      const item = document.createElement('li');
      item.textContent = `${workout.activity} - ${workout.durationMinutes} min - ${workout.weightKg} kg - ${workout.caloriesBurned} kcal`;
      historyList.appendChild(item);
    });
  } catch {
    historyList.innerHTML = '<li>Could not load workout history.</li>';
  }
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const payload = { activity: document.getElementById('activity').value, durationMinutes: Number(document.getElementById('duration').value), weightKg: Number(document.getElementById('weight').value) };
  try {
    const data = await request('/api/workouts', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    caloriesEl.textContent = data.caloriesBurned;
    resultBox.classList.remove('hidden');
    await loadHistory();
  } catch (error) {
    alert(error.message);
  }
});

loadHistory();
const apiBaseUrl = '';
const form = document.getElementById('workout-form');
const userForm = document.getElementById('user-form');
const resultBox = document.getElementById('result');
const caloriesEl = document.getElementById('calories');
const historyList = document.getElementById('history-list');
const userMessage = document.getElementById('user-message');
const preferredActivityInput = document.getElementById('activity-preferred');
const activitySelect = document.getElementById('activity');
const activityOptions = document.getElementById('activity-options');
const newActivityDialog = document.getElementById('new-activity-dialog');
const newActivityForm = document.getElementById('new-activity-form');
const newActivityName = document.getElementById('new-activity-name');
const newActivityMet = document.getElementById('new-activity-met');
const activityMessage = document.getElementById('activity-message');

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

function findActivity(name) {
  return [...activitySelect.options].find((option) => option.value.toLowerCase() === name.trim().toLowerCase());
}

function setActivities(activities) {
  activitySelect.innerHTML = '';
  activityOptions.innerHTML = '';
  activities.forEach((activity) => {
    const option = new Option(activity.name, activity.name);
    activitySelect.add(option);
    activityOptions.appendChild(new Option(activity.name));
  });
}

function openNewActivityForm(name) {
  newActivityName.value = name.trim();
  newActivityMet.value = '';
  activityMessage.textContent = '';
  newActivityDialog.showModal();
  newActivityMet.focus();
}

function selectPreferredActivity() {
  const preferredName = preferredActivityInput.value.trim();
  if (!preferredName) return;
  const option = findActivity(preferredName);
  if (option) {
    activitySelect.value = option.value;
    preferredActivityInput.value = option.value;
    return;
  }
  openNewActivityForm(preferredName);
}

async function loadActivities() {
  const activities = await request('/api/activities');
  setActivities(activities);
  selectPreferredActivity();
}

preferredActivityInput.addEventListener('change', selectPreferredActivity);
preferredActivityInput.addEventListener('blur', selectPreferredActivity);

document.getElementById('cancel-activity').addEventListener('click', () => newActivityDialog.close());

newActivityForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  try {
    const activity = await request('/api/activities', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: newActivityName.value.trim(), metValue: Number(newActivityMet.value) }),
    });
    const option = new Option(activity.name, activity.name);
    activitySelect.add(option);
    activityOptions.appendChild(new Option(activity.name));
    activitySelect.value = activity.name;
    preferredActivityInput.value = activity.name;
    newActivityDialog.close();
    showUserMessage(`Activity ${activity.name} created. You can now save your profile.`);
  } catch (error) {
    activityMessage.textContent = error.message;
    activityMessage.classList.add('error');
  }
});

userForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (preferredActivityInput.value.trim() && !findActivity(preferredActivityInput.value)) {
    selectPreferredActivity();
    return;
  }
  const payload = { name: document.getElementById('user-name').value.trim(), age: Number(document.getElementById('user-age').value), email: document.getElementById('user-email').value.trim(), activityPreferred: preferredActivityInput.value.trim() || null };
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

Promise.all([loadActivities(), loadHistory()]).catch(() => {
  activitySelect.innerHTML = '<option value="">Could not load activities</option>';
});
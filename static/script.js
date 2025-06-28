let userData;
let activeUser = null;
let interval = null;
let selectedStat = "strength";

document.addEventListener("DOMContentLoaded", () => {
  // Animate opening
  const anim = document.querySelector(".opening-animation");
  setTimeout(() => {
    anim.style.display = "none";
    document.querySelector(".main-container").style.display = "flex";
  }, 2500);

  // Fetch user data
  fetch("/get_user_data")
    .then(res => res.json())
    .then(data => {
      userData = data;
      const userSelect = document.getElementById("user-select");
      Object.keys(userData).forEach(username => {
        const option = document.createElement("option");
        option.value = username;
        option.textContent = username;
        userSelect.appendChild(option);
      });
      updateUI();
    });

  // Login switch
  document.getElementById("user-select").addEventListener("change", (e) => {
    activeUser = e.target.value;
    updateUI();
  });

  // Timer buttons
  document.getElementById("start-btn").addEventListener("click", () => {
    const stat = document.getElementById("grind-select").value;
    selectedStat = stat;
    startTimer(stat);
  });

  document.getElementById("pause-btn").addEventListener("click", () => {
    clearInterval(interval);
  });

  document.getElementById("stop-btn").addEventListener("click", () => {
    stopTimer();
  });

  // Add task
  document.getElementById("add-task-btn").addEventListener("click", () => {
    const taskList = document.getElementById("task-list");
    const task = document.createElement("div");
    const nameInput = document.createElement("input");
    const xpInput = document.createElement("input");
    const checkbox = document.createElement("input");

    nameInput.placeholder = "Task";
    xpInput.type = "number";
    xpInput.placeholder = "XP";
    checkbox.type = "checkbox";

    checkbox.addEventListener("change", () => {
      if (checkbox.checked) {
        const xp = parseInt(xpInput.value) || 0;
        gainXP(xp);
        task.remove(); // Remove after check
      }
    });

    task.appendChild(nameInput);
    task.appendChild(xpInput);
    task.appendChild(checkbox);
    taskList.appendChild(task);
  });
});

function updateUI() {
  if (!activeUser) return;
  const stats = userData[activeUser].stats;
  const xp = userData[activeUser].xp;
  const level = userData[activeUser].level;

  Object.keys(stats).forEach(stat => {
    const el = document.getElementById(`stat-${stat}`);
    if (el) el.textContent = stats[stat];
  });

  document.getElementById("level").textContent = level;
  document.getElementById("xp").textContent = xp;

  const xpNeeded = 100 + 100 * level;
  const fillPercent = Math.min(100, (xp / xpNeeded) * 100);
  document.querySelector(".xp-bar-fill").style.width = fillPercent + "%";

  // Update class
  const classBox = document.getElementById("class-rank");
  const classes = ["Rookie", "Apprentice", "Adept", "Elite", "Master", "Ascendant"];
  const classIndex = Math.floor(level / 10);
  classBox.textContent = classes[classIndex] || "Legend";
}

function gainXP(amount) {
  if (!activeUser) return;
  userData[activeUser].xp += amount;

  // Level Up?
  let xp = userData[activeUser].xp;
  let level = userData[activeUser].level;
  const xpNeeded = 100 + 100 * level;

  if (xp >= xpNeeded) {
    userData[activeUser].xp = xp - xpNeeded;
    userData[activeUser].level++;
    document.body.classList.add("level-up");
    setTimeout(() => document.body.classList.remove("level-up"), 2000);
  }

  saveData();
  updateUI();
}

function startTimer(stat) {
  let time = 0;
  interval = setInterval(() => {
    time++;
    if (time >= 3600) {
      userData[activeUser].stats[stat]++;
      saveData();
      updateUI();
      time = 0;
    }
  }, 1000); // Every second
}

function stopTimer() {
  clearInterval(interval);
}

function saveData() {
  fetch("/save_user_data", {
    method: "POST",
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(userData)
  });
}

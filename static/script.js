document.addEventListener('DOMContentLoaded', () => {
  const xpBar = document.getElementById('xp-bar');
  const xpValue = document.getElementById('xp-value');
  const levelValue = document.getElementById('level-value');
  const totalStat = document.getElementById('total-stat');
  const classBox = document.getElementById('class');
  const todayBox = document.getElementById('today');
  const rankBox = document.getElementById('rank');

  const taskList = document.getElementById('task-ul');
  const taskInput = document.getElementById('task-input');
  const xpInput = document.getElementById('xp-input');
  const addTaskBtn = document.getElementById('add-task');

  const timerDisplay = document.getElementById('timer-display');
  const timerStart = document.getElementById('timer-start');
  const timerPause = document.getElementById('timer-pause');
  const timerStop = document.getElementById('timer-stop');
  const statSelect = document.getElementById('stat-select');

  let xp = 0;
  let level = 0;
  let timer = null;
  let startTime = null;
  let pausedTime = 0;

  // Initial UI updates
  updateXP(0);
  const today = new Date().toLocaleDateString();
  if (todayBox) todayBox.textContent = today;

  function updateXP(gain) {
    xp += gain;
    let levelUp = false;
    const xpNeeded = (level + 1) * 100;
    if (xp >= xpNeeded) {
      xp -= xpNeeded;
      level++;
      levelUp = true;
    }
    const xpPercent = (xp / ((level + 1) * 100)) * 100;
    xpBar.style.width = xpPercent + '%';
    xpValue.textContent = `${xp} / ${(level + 1) * 100}`;
    levelValue.textContent = level;

    const classTitles = ['Rookie', 'Fighter', 'Elite', 'Warrior', 'Veteran', 'Champion', 'Master', 'Godslayer'];
    const currentClass = classTitles[Math.floor(level / 10)] || 'Legend';
    if (classBox) classBox.textContent = currentClass;

    if (levelUp) {
      animateLevelUp();
    }
  }

  function animateLevelUp() {
    const msg = document.createElement('div');
    msg.textContent = 'LEVEL UP!';
    msg.style.position = 'fixed';
    msg.style.top = '40%';
    msg.style.left = '50%';
    msg.style.transform = 'translate(-50%, -50%)';
    msg.style.fontSize = '4rem';
    msg.style.color = 'gold';
    msg.style.zIndex = 1000;
    msg.style.textShadow = '0 0 10px gold';
    document.body.appendChild(msg);
    setTimeout(() => msg.remove(), 2000);
  }

  addTaskBtn.addEventListener('click', () => {
    const name = taskInput.value.trim();
    const xp = parseInt(xpInput.value.trim(), 10);
    if (name && !isNaN(xp)) {
      const li = document.createElement('li');
      li.innerHTML = `<span>${name} (+${xp} XP)</span><button class="check">✓</button>`;
      taskList.appendChild(li);
      li.querySelector('.check').addEventListener('click', () => {
        updateXP(xp);
        li.remove();
      });
      taskInput.value = '';
      xpInput.value = '';
    }
  });

  // TIMER
  function updateTimerDisplay(seconds) {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    timerDisplay.textContent = `${String(hrs).padStart(2, '0')}:${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  }

  timerStart.addEventListener('click', () => {
    if (!timer) {
      startTime = Date.now() - pausedTime;
      timer = setInterval(() => {
        const elapsed = Math.floor((Date.now() - startTime) / 1000);
        updateTimerDisplay(elapsed);
      }, 1000);
    }
  });

  timerPause.addEventListener('click', () => {
    if (timer) {
      clearInterval(timer);
      pausedTime = Date.now() - startTime;
      timer = null;
    }
  });

  timerStop.addEventListener('click', () => {
    if (timer) {
      clearInterval(timer);
    }
    const elapsed = Math.floor((Date.now() - startTime) / 1000);
    const fullHours = Math.floor(elapsed / 3600);
    const stat = statSelect.value;
    if (stat && fullHours > 0) {
      const statEl = document.getElementById(stat);
      if (statEl) {
        const old = parseInt(statEl.textContent, 10);
        statEl.textContent = old + fullHours;
      }
      const allStats = ['intelligence', 'strength', 'endurance', 'looks', 'mindset'];
      let total = 0;
      allStats.forEach(s => {
        const el = document.getElementById(s);
        total += parseInt(el.textContent, 10);
      });
      totalStat.textContent = total;
    }
    updateTimerDisplay(0);
    pausedTime = 0;
    timer = null;
  });

  // Opening vault animation
  const openingScreen = document.querySelector('.opening-screen');
  setTimeout(() => {
    if (openingScreen) openingScreen.remove();
  }, 4000);
});

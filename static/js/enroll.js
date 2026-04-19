// enroll.js — runs on set_password.html only

const enroll = initSignatureCanvas('canvas-enroll');
let enrollCount = 0;
const MAX_ENROLLS = 5;
const enrolledSets = [];

document.getElementById('enroll-clear').addEventListener('click', () => {
  enroll.clear();
  document.getElementById('enroll-hint').textContent =
    `~ Draw your signature (${enrollCount + 1}/${MAX_ENROLLS})`;
});

document.getElementById('enroll-confirm').addEventListener('click', async () => {
  const strokes = enroll.getStrokes();
  if (strokes.length === 0) return;

  enrolledSets.push(strokes);
  enrollCount++;
  document.getElementById('attempt-label').textContent = `(${enrollCount} / ${MAX_ENROLLS})`;

  if (enrollCount >= MAX_ENROLLS) {
    document.getElementById('enroll-hint').textContent = '~ Enrolling…';
    try {
      const res = await fetch('/enroll', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ signatures: enrolledSets })
      });
      const data = await res.json();
      document.getElementById('enroll-hint').textContent = data.message || '~ Enrolled!';
    } catch (err) {
      document.getElementById('enroll-hint').textContent = '~ Error — check console';
      console.error(err);
    }
    setTimeout(() => { window.location.href = '/unlocked'; }, 1500);
  } else {
    enroll.clear();
    document.getElementById('enroll-hint').textContent =
      `~ Draw again (${enrollCount + 1}/${MAX_ENROLLS})`;
  }
});
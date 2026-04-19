// verify.js — runs on plocked.html only

const verify = initSignatureCanvas('canvas-verify');

document.getElementById('verify-clear').addEventListener('click', () => {
  verify.clear();
  document.getElementById('verify-hint').textContent = '~ Draw your signature to unlock';
});

document.getElementById('verify-submit').addEventListener('click', async () => {
  const strokes = verify.getStrokes();
  if (strokes.length === 0) return;

  document.getElementById('verify-hint').textContent = '~ Verifying…';
  try {
    const res = await fetch('/verify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ signature: strokes })
    });
    const data = await res.json();
    if (data.match) {
      document.getElementById('verify-hint').textContent = '~ Matched — unlocking!';
      setTimeout(() => { window.location.href = '/unlocked'; }, 900);
    } else {
      document.getElementById('verify-hint').textContent =
        `~ No match (score: ${data.score ?? '—'}) — try again`;
      verify.clear();
    }
  } catch (err) {
    document.getElementById('verify-hint').textContent = '~ Error — check console';
    console.error(err);
  }
});
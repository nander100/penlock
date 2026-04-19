let signatureStartTime = null;
let lastPenDownTime = null;
let penUpTime = null;
let signatureSet = [];
let currentSignature = [];
let currentSegment = [];
let drawingSegment = false;
let drawingSignature = false;
let paint = false;
let numberOfPenLifts = 0;
let liftTimer = null;
let signatureDuration = 0;
let signatureComplete = false;

const canvas = document.querySelector('#canvas');
const ctx = canvas.getContext('2d');
let coord = { x: 0, y: 0 };

class Point {
  constructor(newx, newy, time = null) {
    this.x = newx;
    this.y = newy;
    this.timestamp = time;
  }
}

window.addEventListener('load', () => {
  resize();
  canvas.addEventListener('pointerdown', startPainting);
  canvas.addEventListener('pointerup', startLiftTimer);
  canvas.addEventListener('pointermove', sketch);
  canvas.addEventListener('touchstart', e => e.preventDefault(), { passive: false });
  canvas.addEventListener('touchmove', e => e.preventDefault(), { passive: false });
  window.addEventListener('resize', resize);
});

function resize() {
  ctx.canvas.width = canvas.offsetWidth || 480;
  ctx.canvas.height = 200;
}

function getPosition(event) {
  coord.x = event.clientX - canvas.getBoundingClientRect().left;
  coord.y = event.clientY - canvas.getBoundingClientRect().top;
  return new Point(coord.x, coord.y);
}

function startPainting(event) {
  if (event.pointerType === 'touch') return;
  if (signatureComplete) return;
  clearTimeout(liftTimer);

  if (!signatureStartTime) {
    signatureStartTime = Date.now();
    drawingSignature = true;
  }
  drawingSegment = true;
  paint = true;
  getPosition(event);
}

function startLiftTimer(event) {
  if (event.pointerType === 'touch') return;

  drawingSegment = false;
  if (currentSegment.length > 0) {
    currentSignature.push([...currentSegment]);
  }
  currentSegment = [];
  numberOfPenLifts++;
  lastPenDownTime = Date.now();

  liftTimer = setTimeout(() => {
    paint = false;
    signatureComplete = true;
    verifySignature();
  }, 1000);
}

async function verifySignature() {
  const signatureToSend = [...currentSignature];

  // Reset for next attempt
  currentSignature = [];
  signatureStartTime = null;
  paint = true;
  signatureComplete = false;

  const hint = document.getElementById('verify-hint');
  hint.textContent = '~ Verifying…';

  // Flash while verifying
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = 'rgba(0, 200, 255, 0.15)';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  setTimeout(() => { ctx.clearRect(0, 0, canvas.width, canvas.height); }, 400);

  try {
    const response = await fetch('/verify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ signature: signatureToSend })
    });
    const data = await response.json();

    if (data.genuine) {
      // Show green flash
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = 'rgba(0, 255, 0, 0.2)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      setTimeout(() => { ctx.clearRect(0, 0, canvas.width, canvas.height); }, 500);

      hint.textContent = '~ Matched — safe unlocked!';

      // Show the close button now that match is confirmed
      document.getElementById('close-btn').style.display = 'block';

    } else {
      // Show red flash
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = 'rgba(255, 0, 0, 0.1)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      setTimeout(() => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        hint.textContent = '~ No match — try again';
      }, 500);
    }

  } catch (err) {
    hint.textContent = '~ Error — check console';
    console.error(err);
  }
}

function sketch(event) {
  if (event.buttons === 0) return;
  if (event.pointerType === 'touch') return;
  if (signatureComplete) return;
  if (!paint) return;

  lastPenDownTime = Date.now();
  ctx.beginPath();
  ctx.lineCap = 'round';
  ctx.lineWidth = 5;
  ctx.strokeStyle = 'black';
  ctx.moveTo(coord.x, coord.y);
  getPosition(event);
  ctx.lineTo(coord.x, coord.y);
  ctx.stroke();
  const newPoint = new Point(coord.x, coord.y, Date.now());
  currentSegment.push(newPoint);
}
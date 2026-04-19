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
    clearSign();
  }, 1000);
}

async function clearSign() {
  signatureDuration = Date.now() - signatureStartTime - 1000;
  signatureSet.push([currentSignature]);
  currentSignature = [];
  signatureStartTime = null;

  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = 'rgba(0, 255, 0, 0.3)';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  setTimeout(() => { ctx.clearRect(0, 0, canvas.width, canvas.height); }, 500);


  // Update attempt counter if on set-password page
  const attemptLabel = document.getElementById('attempt-label');
  if (attemptLabel) {
    attemptLabel.textContent = `(${signatureSet.length} / 3)`;
  }
    paint=true;
    signatureComplete=false;

    if(signatureSet.length==4){
      const response = await fetch('/getSignatureSet',{
        method:"POST",
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ signatureSet })
        });
        const data = await response.json();
        console.log(data);
        signatureSet = []; // clear after sending

        if (data.redirect) {
            window.location.href = data.redirect; 
        }
            

      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      ctx.fillStyle = 'rgba(0, 255, 0, 0.3)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      setTimeout(() => {
          ctx.clearRect(0, 0, canvas.width, canvas.height);
      }, 500);

      signatureSet=[]
    }else{
          ctx.fillStyle = 'rgba(0, 0, 255, 0.3)';

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

function undoLastSignature() {
    if (signatureSet.length > 0) {
        signatureSet.pop();  // remove last signature
        const attemptLabel = document.getElementById('attempt-label');
        if (attemptLabel) {
            attemptLabel.textContent = `(${signatureSet.length} / 3+ 1)`;
        }
        console.log('removed last signature, remaining:', signatureSet.length);
    }
}
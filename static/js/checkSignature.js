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
    const rect = canvas.getBoundingClientRect();
    ctx.canvas.width = rect.width || 400;
    ctx.canvas.height = rect.height || 200;
}

function getPosition(event) {
    const rect = canvas.getBoundingClientRect();
    coord.x = event.clientX - rect.left;
    coord.y = event.clientY - rect.top;
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

async function verifySignature() {
    const signatureToSend = [...currentSignature];

    const response = await fetch('/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ signature: signatureToSend })
    });
    const data = await response.json();

    if (data.genuine) {
        window.location.href = '/unlocked';
    } else {
        document.getElementById('result').innerText = 'Try again';
        signatureComplete = false;
        paint = true;
        currentSignature = [];
        currentSegment = [];
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
}
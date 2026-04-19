let signatureStartTime = null;
let lastPenDownTime = null;
let penUpTime = null;
let signatureSet = [];
let currentSignature=[];
let currentSegment=[];

let drawingSegment = false
let drawingSignature = false
let paint = false;
let numberOfPenLifts=0
let liftTimer=null
let signatureDuration = 0;
let signatureComplete = false; // add at top
const canvas = document.querySelector('#canvas');
const ctx = canvas.getContext('2d');
let coord = {x: 0, y: 0}; // add at top

class Point{
  constructor(newx,newy, time=null){
    this.x=newx;
    this.y=newy;
    this.timestamp=time
  }

}
// Load
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
    ctx.canvas.width = 1000;
    ctx.canvas.height = 300;
}

//retunrs current pos in point objects
function getPosition(event) {
    coord.x = event.clientX - canvas.offsetLeft;
    coord.y = event.clientY - canvas.offsetTop;
    return new Point(coord.x,coord.y)
}

function startPainting(event) { 
    if (event.pointerType === 'touch') return;
    if (signatureComplete) return;
    clearTimeout(liftTimer)

    if (!signatureStartTime) {
        signatureStartTime = Date.now(); // only set on first down
        drawingSignature=true;
    }
    drawingSegment=true;

    paint = true;
    getPosition(event);
}

function startLiftTimer(event) {
    if (event.pointerType === 'touch') return;

    drawingSegment=false;
    if (currentSegment.length > 0) {  // 👈 only push if not empty
        currentSignature.push([...currentSegment]);
    }

    console.log('currentSegment length:', currentSegment.length);  // check points
    console.log('currentSignature length:', currentSignature.length);  // check segments


    currentSegment=[]

    numberOfPenLifts++;
    lastPenDownTime = Date.now();

    liftTimer = setTimeout(() => {
        paint = false; signatureComplete =true; clearSign();
    }, 1000);
}

async function clearSign(){
    signDuration=Date.now()-signatureStartTime-1000;

    signatureSet.push([currentSignature])
    currentSignature=[]

    console.log('signatureset length:', signatureSet.length);  // check segments

    signatureStartTime=null;
    console.log("clearSign called");
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    ctx.fillStyle = 'rgba(0, 255, 0, 0.3)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    setTimeout(() => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    }, 500);

    paint=true;
    signatureComplete=false;

    if(signatureSet.length==5){
      const response = await fetch('/getSignatureSet',{
        method:"POST",
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ signatureSet })
        });
        const data = await response.json();
        console.log(data);
        signatureSet = []; // clear after sending
    

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
    if(signatureComplete)return;
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
    newPoint= new Point(coord.x,coord.y,Date.now())
    currentSegment.push(newPoint);
}

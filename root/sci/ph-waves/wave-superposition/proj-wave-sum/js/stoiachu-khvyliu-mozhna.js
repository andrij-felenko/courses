const cv = document.querySelector('canvas');
const g  = cv.getContext('2d');
const A = 60, k = 2*Math.PI/140, w = 2*Math.PI*0.4;   // піксели, повільно

function draw(t) {
  g.clearRect(0, 0, cv.width, cv.height);
  g.beginPath();
  for (let px = 0; px <= cv.width; px++) {
    const right = A*Math.sin(k*px - w*t);
    const left  = A*Math.sin(k*px + w*t);
    const y = cv.height/2 - (right + left);   // та сама сума двох зустрічних
    px ? g.lineTo(px, y) : g.moveTo(px, y);
  }
  g.stroke();
  requestAnimationFrame(ts => draw(ts / 1000));   // ts у мс → секунди
}
requestAnimationFrame(ts => draw(ts / 1000));

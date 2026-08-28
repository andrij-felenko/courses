let lastBlink = 0;
let lastRead  = 0;
const blinkInterval = 500;   // мс
const readInterval  = 100;   // мс

function loop() {
  const now = performance.now();   // мс від старту

  if (now - lastBlink >= blinkInterval) {   // діло 1: блимати
    lastBlink += blinkInterval;
    ledState = !ledState;
    setLed(ledState);
  }

  if (now - lastRead >= readInterval) {     // діло 2: опитати давач
    lastRead += readInterval;
    readSensor();
  }

  // кнопки й будь-що інше — теж тут, нічого не блокує
  requestAnimationFrame(loop);
}
requestAnimationFrame(loop);

function bestRational(r: number, maxDen = 32): [number, number] {
  let hPrev = 0, h = 1, kPrev = 1, k = 0, v = r;
  for (let i = 0; i < 64; i++) {
    const a = Math.floor(v);
    [hPrev, h] = [h, a * h + hPrev];
    [kPrev, k] = [k, a * k + kPrev];
    if (k > maxDen) return [hPrev, kPrev];
    const rem = v - a;
    if (rem < 1e-12) return [h, k];
    v = 1 / rem;
  }
  return [h, k];
}

/** XY-осцилограф на canvas: старий слід тане, як люмінофор на трубці. */
function drawTrace(
  ctx: CanvasRenderingContext2D, fx: number, fy: number,
  { phase = 0, ax = 1, ay = 1, fs = 48_000, loops = 1 } = {},
): void {
  const [p] = bestRational(fx / fy, 64);
  const n = Math.round(fs * (p / fx) * loops);   // ціле число спільних періодів
  const { width: W, height: H } = ctx.canvas;
  const r = Math.min(W, H) / 2 - 20;

  ctx.fillStyle = "rgba(0, 0, 0, 0.10)";         // згасання попереднього кадру
  ctx.fillRect(0, 0, W, H);

  ctx.beginPath();
  for (let i = 0; i < n; i++) {
    const t = i / fs;
    const px = W / 2 + r * ax * Math.sin(2 * Math.PI * fx * t + phase);
    const py = H / 2 - r * ay * Math.sin(2 * Math.PI * fy * t);
    if (i === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
  }
  ctx.closePath();                               // остання точка вертається в першу
  ctx.strokeStyle = "#5cf08a";
  ctx.lineWidth = 1.6;
  ctx.stroke();
}

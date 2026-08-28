const ac  = new AudioContext();
const out = ac.createGain();
out.gain.value = 0.2;                 // запас: багато джерел — тихіше кожне
out.connect(ac.destination);

const f0 = 220;
for (let k = 1; k < 32; k += 2) {     // непарні гармоніки квадрата
  const osc = ac.createOscillator();  // чистий синус частоти k·f0
  const g   = ac.createGain();
  osc.frequency.value = k * f0;
  g.gain.value = (4/Math.PI) / k;     // амплітуда 1/k
  osc.connect(g).connect(out);        // усі течуть в ОДИН вузол out
  osc.start();
}
// ніде немає циклу підсумовування: мікшер вузла out ДОДАЄ всі входи сам.
// Це фізична суперпозиція — тільки замість повітря складає аудіограф.

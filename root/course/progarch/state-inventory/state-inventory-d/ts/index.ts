const THRESHOLD  = 20.0;
const MAX_RUN_MS = 2 * 3600 * 1000;   // безпека: не гріти довше 2 год поспіль

let heaterOnFlag = false;             // ← стан у пам'яті процесу
let onSince: number | null = null;    // ← і час теж лише в пам'яті

while (true) {
  const t = await readSensor();
  const wantOn = t < THRESHOLD;

  if (wantOn && !heaterOnFlag) {
    await relayOn();  heaterOnFlag = true;  onSince = now();
  } else if (!wantOn && heaterOnFlag) {
    await relayOff(); heaterOnFlag = false; onSince = null;
  }

  // захисна межа рахує час від змінної в пам'яті:
  if (heaterOnFlag && now() - onSince! > MAX_RUN_MS) {
    await relayOff(); heaterOnFlag = false; onSince = null;
  }

  await reportToCloud(heaterOnFlag);  // застосунок показує цей самий прапорець
  await sleep(30_000);
}

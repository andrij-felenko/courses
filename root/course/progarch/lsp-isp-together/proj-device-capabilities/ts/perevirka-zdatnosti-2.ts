// ✓ перевірили ОДИН раз на межі — далі течуть уже вузькі типи
interface Fleet {
  switchable: Switchable[];
  lockable:   Lockable[];
  streamable: Streamable[];
}
function classify(devices: unknown[]): Fleet {
  const f: Fleet = { switchable: [], lockable: [], streamable: [] };
  for (const d of devices) {
    if (isSwitchable(d)) f.switchable.push(d);   // тут d звужено до Switchable
    if (isLockable(d))   f.lockable.push(d);
    if (isStreamable(d)) f.streamable.push(d);
  }
  return f;
}
function nightMode(f: Fleet): void {
  f.switchable.forEach((s) => s.turnOff());       // жодного isXxx — тип уже вузький
  f.lockable.forEach((l) => l.lock());
  f.streamable.forEach((c) => c.startStream());
}

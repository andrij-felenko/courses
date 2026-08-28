function nightMode(devices: unknown[]): void {
  for (const d of devices) {
    if (isSwitchable(d)) d.turnOff();      // світло й розетки — вимкнути
    if (isLockable(d))   d.lock();         // двері — замкнути
    if (isStreamable(d)) d.startStream();  // камери — на нічне чування
  }
}

// Запускається як є: змішаний парк проходить без жодного винятку.
const fleet: unknown[] = [
  new TempSensor(21.5),
  new SmartSocket(),
  new DoorLock(),
  new Camera(),
];
nightMode(fleet);   // давач мовчки пропущено — кинути виняток нема звідки

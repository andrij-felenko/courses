// ❌ здатність перевіряють ГЛИБОКО в логіці, знову й знову
function runSchedule(devices: unknown[], plan: Step[]): void {
  for (const step of plan) {
    for (const d of devices) {
      if (step.kind === "off"  && isSwitchable(d)) d.turnOff();
      if (step.kind === "lock" && isLockable(d))   d.lock();
    }
  }
  // …і той самий частокіл if-isXxx у кожній наступній функції
}

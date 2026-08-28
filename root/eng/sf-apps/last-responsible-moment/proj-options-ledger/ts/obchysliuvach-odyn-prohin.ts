interface FireEvent {
  decisionId: string; title: string; owner: string;
  adr: string; options: string[]; uncertainty: string;
}

function tick(ledger: Decision[], w: Window): FireEvent[] {
  const fired: FireEvent[] = [];
  for (const d of ledger) {
    if (d.status === "superseded") continue;         // закрите не чіпаємо
    const armed = isArmed(d.trigger, w);
    const firing = armed && isFiring(d.trigger, w);  // стріляти лише в межах смуги

    if (d.status === "open" && armed) {
      d.status = "armed";
      d.holdCount = 0;
    }
    if (d.status === "armed") {
      if (!armed) {
        d.status = "open";                 // впали нижче arm — відбій, тремтіння згашене
        d.holdCount = 0;
      } else if (firing) {
        d.holdCount += 1;                  // стійкість: рахуємо виміри поспіль
        if (d.holdCount >= d.trigger.holdFor) {
          d.status = "due";
          fired.push({
            decisionId: d.id, title: d.title, owner: d.owner,
            adr: d.adr, options: d.options, uncertainty: d.uncertainty,
          });
        }
      } else {
        d.holdCount = 0;                   // серія урвалась — лічильник у нуль
      }
    }
  }
  return fired;
}

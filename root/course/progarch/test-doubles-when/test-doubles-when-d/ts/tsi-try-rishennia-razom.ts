// Заплутаний різ: годинник, база й залізо прибиті просто в логіку рішення.
class CoolingController {
  tick(): void {
    const now = Date.now();                                  // ← прибитий годинник
    const rows = db.query("select at, celsius from readings order by at desc limit 50");
    const inWindow = rows.filter(r => r.at >= now - 300_000); // 5 хв — сама логіка…
    const avg = inWindow.reduce((s, r) => s + r.celsius, 0) / inWindow.length;
    if (avg > 25) gpio.write(COOLER_PIN, 1);                 // ← прибите залізо
  }
}

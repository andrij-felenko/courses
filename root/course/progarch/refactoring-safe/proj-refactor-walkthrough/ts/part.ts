type Tariff = "day" | "night" | "business";
interface Line { meter: string; tariff: Tariff; kWh: number; }
interface Account { customer: string; active: boolean; lines: Line[]; }

function statement(acc: Account): string {
  let ta = 0;                    // total amount, у копійках
  let vc = 0;                    // volume credits — бонусні кВт·год
  let out = `Рахунок — ${acc.customer}\n`;

  for (const l of acc.lines) {
    // ціна рядка за тарифом
    let a = 0;
    if (l.tariff === "day") {
      a = l.kWh * 250;
      if (l.kWh > 100) a += (l.kWh - 100) * 30;
    } else if (l.tariff === "night") {
      a = l.kWh * 120;
    } else if (l.tariff === "business") {
      a = l.kWh * 300;
      if (l.kWh > 500) a += (l.kWh - 500) * 40;
    } else {
      throw new Error(`невідомий тариф: ${l.tariff}`);
    }

    // бонусні кВт·год — лише активним і не бізнесу
    if (acc.active) {
      if (l.tariff !== "business") {
        vc += Math.max(l.kWh - 200, 0);
        if (l.tariff === "night") vc += Math.floor(l.kWh / 500);
      }
    }

    out += `  ${l.meter}: ${l.kWh} кВт·год — ${(a / 100).toFixed(2)} грн\n`;
    ta += a;
  }

  out += `Разом: ${(ta / 100).toFixed(2)} грн\n`;
  out += `Бонусні кіловати: ${vc}\n`;
  return out;
}

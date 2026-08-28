// «Екран»: поточне число живе прямо у віджеті-полі. Моделі нема.
let screenTarget = 22;      // ← джерело правди — саме поле на екрані
let barWidget = "";

function onPlusClicked(): void {
  // 1) ВВІД+ЧИТАННЯ: беремо поточне число з ПОЛЯ на екрані
  let current = screenTarget;
  // 2) ПРАВИЛО предметної області: підняти на 1, але не вище 30
  current = current + 1;
  if (current > 30) current = 30;
  // 3) РЕНДЕР: вписати назад у поле і перемалювати смужку
  screenTarget = current;
  const filled = Math.round((current - 5) / (30 - 5) * 20);
  barWidget = "█".repeat(filled) + "·".repeat(20 - filled);
  // 4) ЗБЕРЕЖЕННЯ: записати на диск
  fs.writeFileSync("target.txt", String(current));
}

function onMinusClicked(): void {
  let current = screenTarget;
  current = current - 1;
  if (current < 5) current = 5;              // ← та сама логіка, інша межа
  screenTarget = current;
  const filled = Math.round((current - 5) / (30 - 5) * 20);  // ← рендер скопійовано
  barWidget = "█".repeat(filled) + "·".repeat(20 - filled);
  fs.writeFileSync("target.txt", String(current));           // ← збереження скопійовано
}

// ── Тарифи керованого брокера (AWS IoT Core, US-East, 2025) ─────────────────
const PRICE_PER_M_MSG = 1.0;        // $ за млн повідомлень (при обсязі → ~0.70)
const PRICE_PER_M_CONN_MIN = 0.08;  // $ за млн хвилин з'єднання
const MSG_PER_HOME_MONTH = 86_400;  // 1 повідомл./30 с → 86 400/міс
const CONN_MIN_PER_MONTH = 43_200;  // з'єднання тримається цілий місяць

// ── Своє: разова побудова + вічний хвіст ────────────────────────────────────
const ENG_MONTH_USD = 12_500;       // повна вартість інженер-місяця (з накладними)
const BUILD_USD = ENG_MONTH_USD * 12;     // 2 інж. × 6 міс = $150 000 до v1
const SECURITY_MONTH = 2_500;       // аудити, пентести, секрети
const INFRA_PER_HOME = 0.01;        // свої сервери + резерв, на дім/міс

const managedMonthly = (homes: number): number =>
  (homes * MSG_PER_HOME_MONTH) / 1e6 * PRICE_PER_M_MSG +
  (homes * CONN_MIN_PER_MONTH) / 1e6 * PRICE_PER_M_CONN_MIN;

// Скільки інженерів тримають брокер живим 24/7. Щедро занижено: гайд Google SRE
// радить від ~8 на майданчик для сталого чергування — ми беремо від 2.
const opsFte = (homes: number): number =>
  Math.max(2, 2 + 2 * Math.log10(homes / 10_000));

const ownMonthly = (homes: number): number =>
  opsFte(homes) * ENG_MONTH_USD + INFRA_PER_HOME * homes + SECURITY_MONTH;

const ownTco = (homes: number, months: number): number =>
  BUILD_USD + ownMonthly(homes) * months;

// Найменший масштаб, де своє дешевше (months → повна вартість; 0 → сталий місяць).
function breakevenHomes(months = 0): number {
  const own = (h: number) => (months ? ownTco(h, months) : ownMonthly(h));
  const buy = (h: number) => managedMonthly(h) * (months || 1);
  let [lo, hi] = [1_000, 100_000_000];
  for (let i = 0; i < 60; i++) {
    const mid = Math.sqrt(lo * hi);         // геом. середина: вісь логарифмічна
    if (own(mid) > buy(mid)) lo = mid; else hi = mid;
  }
  return Math.sqrt(lo * hi);
}

const money = (x: number) => `$${Math.round(x).toLocaleString("uk-UA")}`;
const scenarios = [5_000, 50_000, 500_000, 1_000_000, 5_000_000, 10_000_000];

for (const n of scenarios) {
  const buy = managedMonthly(n), own = ownMonthly(n);
  console.log(
    `${n.toLocaleString("uk-UA").padStart(11)}  ` +
    `${Math.round(n / 30).toLocaleString("uk-UA").padStart(9)}/с  ` +
    `куплене ${money(buy).padStart(10)}  своє ${money(own).padStart(10)}  ` +
    `→ ${own < buy ? "СВОЄ" : "куплене"}`,
  );
}
const beNow = breakevenHomes();
console.log(`\nперетин, сталий місяць:     ${Math.round(beNow).toLocaleString("uk-UA")} домів`);
console.log(`перетин, володіння 36 міс:  ${Math.round(breakevenHomes(36)).toLocaleString("uk-UA")} домів`);
console.log(`DH сьогодні 5 000 → ще ~${Math.round(beNow / 5_000)}× до перетину`);

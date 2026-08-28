// ── Стенд: усе детерміноване, час — це число, а не реальний сон ──
// Віртуальний МОНОТОННИЙ годинник. now і deadline — модельні мілісекунди.
type Ctx = { now: number; deadline: number };

// Детермінований генератор — щоб «27» і p99 повторювались від прогону до прогону.
let seed = 1;
const rnd = () => (seed = (seed * 1103515245 + 12345) & 0x7fffffff) / 0x7fffffff;

let cCalls = 0;          // ЄДИНА метрика навантаження на дно ланцюга
let sick = false;        // драйвер вмикає «інцидент» на частину запитів

// Результат несе сигнал «чи варто мене повторювати» — він потече ВГОРУ по ланцюгу.
type Ok  = { ok: true;  value: string; latency: number };
type Err = { ok: false; kind: string; retryable: boolean; latency: number };
type Res = Ok | Err;
type Call = (ctx: Ctx) => Promise<Res>;

// ── C — квола й подеколи повільна залежність ──
// Здоровий: 5% помилок, зрідка залипає. Хворий: 90% помилок, залипає часто.
const rawCallC: Call = async (_ctx) => {
  cCalls++;
  const pFail = sick ? 0.90 : 0.05;
  const pSlow = sick ? 0.70 : 0.01;
  const latency = rnd() < pSlow ? 600 : 20;      // модель, НЕ реальний сон
  if (rnd() < pFail) return { ok: false, kind: "overloaded", retryable: true, latency };
  return { ok: true, value: "camera-frame", latency };
};

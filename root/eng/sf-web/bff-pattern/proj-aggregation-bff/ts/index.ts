import express from "express";
import { Agent, setGlobalDispatcher } from "undici";

// ── Пул з'єднань: ОДИН на весь процес, а не сокет на кожен виклик ──
setGlobalDispatcher(new Agent({
  connections: 128,           // стеля одночасних сокетів НА КОЖЕН хост
  keepAliveTimeout: 60_000,   // тримати з'єднання теплим між викликами
  keepAliveMaxTimeout: 600_000,
}));

const OVERALL = 400;   // весь запит клієнта має вкластися в 400 мс
const PER_PROFILE = 300, PER_ORDERS = 300, PER_TIPS = 250;

// Один крок фанауту: GET-JSON з дедлайном. Кидає, якщо не встиг чи не 2xx.
async function getJSON<T>(url: string, signal: AbortSignal): Promise<T> {
  const r = await fetch(url, { signal, headers: { accept: "application/json" } });
  if (!r.ok) throw new Error(`${url} → ${r.status}`);
  return r.json() as Promise<T>;
}

const app = express();

app.get("/home", async (req, res) => {
  const uid = (req as any).user.id;

  // спільний бюджет на ВЕСЬ запит — стеля, під якою живуть усі виклики
  const budget = AbortSignal.timeout(OVERALL);        // Node 17.3+
  // дедлайн виклику = min(власний ліміт, залишок бюджету запиту)
  const dl = (ms: number) =>
    AbortSignal.any([budget, AbortSignal.timeout(ms)]); // Node 20+

  // три виклики СТАРТУЮТЬ РАЗОМ; allSettled не зірветься від одного провалу
  const [profile, orders, tips] = await Promise.allSettled([
    getJSON<Profile>(`http://profile/users/${uid}`,              dl(PER_PROFILE)),
    getJSON<Order[]>(`http://orders/users/${uid}/recent?limit=3`, dl(PER_ORDERS)),
    getJSON<Tip[]>(`http://tips/users/${uid}/today`,             dl(PER_TIPS)),
  ]);

  // profile — КРИТИЧНИЙ: без нього персонального екрана немає
  if (profile.status === "rejected") {
    return res.status(503).json({ error: "home_unavailable" });
  }

  // orders і tips — НЕОБОВ'ЯЗКОВІ: провал ховає блок, екран лишається
  res.json(shapeHome(profile.value, orders, tips));
});

// ── Скроювання: будуємо РІВНО форму екрана, не сирі відповіді сервісів ──
function shapeHome(
  p: Profile,
  orders: PromiseSettledResult<Order[]>,
  tips: PromiseSettledResult<Tip[]>,
) {
  const ok = <T>(r: PromiseSettledResult<T>) => r.status === "fulfilled";
  return {
    greeting:  p.displayName,               // рівно те, що малює шапка
    avatarUrl: p.avatar?.small ?? null,
    orders: ok(orders)
      ? orders.value.map(o => ({ id: o.id, title: o.title, thumb: o.image }))
      : [],                                  // впав — порожня стрічка
    tips: ok(tips)
      ? tips.value.slice(0, 5).map(t => ({ id: t.id, text: t.text }))
      : null,                                // null → клієнт ховає секцію
    degraded: !ok(orders) || !ok(tips),      // натяк клієнту: щось не догрузилось
  };
}

// СЛОВНИК дій — закритий. Чого тут нема, того правило висловити НЕ МОЖЕ
const ACTIONS: Record<string, (args: any, ctx: HubContext) => void> = {
  "light.blink": (a, ctx) => ctx.light.blink(a.room, a.times),
  "notify.push": (a, ctx) => ctx.notify.push(a.text),
};

const MAX_CASCADE = 4;

function runRule(rule: Rule, ev: MotionEvent, ctx: HubContext, depth = 0): void {
  if (depth > MAX_CASCADE) { log.warn("каскад правил задовгий — обрив"); return; }
  const env = {
    "time.hour":  new Date(ev.at).getHours(),
    "home.mode":  ctx.home.mode,
    "event.room": ev.room,
  };
  const fuel = { left: 10_000 };                 // стеля обчислення на один тригер
  let pass = false;
  try {
    pass = Boolean(evalCond(rule.cond, env, fuel));
  } catch (e) {
    if (e instanceof FuelOut) { log.warn("правило обірвано: скінчилося пальне"); return; }
    log.warn("умова правила кинула виняток", e); return;   // навіть кривий вузол не валить хаб
  }
  if (!pass) return;
  for (const step of rule.then) {
    const run = ACTIONS[step.action];
    if (!run) continue;                          // невідоме дієслово — тихо ігноруємо
    try { run(step.args, ctx); }
    catch (e) { log.warn(`дія ${step.action} впала`, e); }  // один крок упав — решта живе
  }
}

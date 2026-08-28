import { describe, it, expect } from "vitest";

function makeWorld(faults: Record<string, number>, claimAccepted = true) {
  const log: string[] = [], fired: Record<string, number> = {}, seen = new Set<string>();
  const box = { alerted: null as string | null };

  const act = (name: string) => async (_c: Ctx) => {      // рахує й падає перші faults[name] разів
    fired[name] = (fired[name] ?? 0) + 1;
    if (fired[name] <= (faults[name] ?? 0)) { log.push(name + "✗"); throw new Error("збій " + name); }
    log.push(name);
  };
  const waitOrPark = async (_c: Ctx) => {
    log.push("postInvite");
    if (!claimAccepted) throw new WaitingForHuman(0);      // паркуємось; 0 → одразу «протерміновано»
    log.push("accepted");
  };

  const S: Step[] = [
    { name: "freeze",          kind: "compensatable", run: act("freeze"),        compensate: act("unfreeze") },
    { name: "revokeAccess",    kind: "compensatable", run: act("revokeOldKeys"), compensate: act("restoreOldKeys") },
    { name: "awaitClaim",      kind: "compensatable", run: waitOrPark,           compensate: act("cancelClaim") },
    { name: "transferAndWipe", kind: "pivot",         run: act("transferAndShred") },
    { name: "rebindDevices",   kind: "retriable",     run: act("reissueCerts") },
    { name: "openBilling",     kind: "retriable",     run: act("switchBilling") },
    { name: "welcome",         kind: "retriable",     run: act("notifyNewOwner") },
  ];

  const db = new Map<string, Saga>();
  const clone = (s: Saga) => structuredClone(s);
  const ports: Ports = {
    load:   async (id) => clone(db.get(id)!),
    persist:async (s)  => void db.set(s.id, clone(s)),
    txn:    async (fn) => fn({}),                          // у пам'яті транзакція атомарна тривіально
    seen:   async (_t, k) => seen.has(k),
    mark:   async (_t, k) => void seen.add(k),
    saveIn: async (_t, s) => void db.set(s.id, clone(s)),
    outbox: async () => {},                                // подію ковтаємо — тут перевіряємо стан
    alert:  async (s) => void (box.alerted = s.id),
  };
  db.set("h1", { id: "h1", homeId: "home-1", cursor: 0, dir: "forward", status: "running", attempts: 0 });
  return { S, ports, log, fired, box };
}

const COMPS = ["cancelClaim", "restoreOldKeys", "unfreeze"];

describe("дві невдачі — дві долі", () => {
  it("ДО півота: компенсації у ЗВОРОТНОМУ порядку, чисте скасування, півот не чіпано", async () => {
    const w = makeWorld({}, /*claimAccepted*/ false);
    let saga = await drive(w.ports, "h1", w.S);            // дійде до awaitClaim і запаркується
    expect(saga.status).toBe("waiting");
    await onClaimDeadline(w.ports, "h1", w.S);             // витримка вичерпана

    saga = await w.ports.load("h1");
    expect(saga.status).toBe("aborted");                                  // чисте скасування
    expect(w.log.filter((x) => COMPS.includes(x))).toEqual(COMPS);        // рівно зворотний порядок
    expect(w.fired["transferAndShred"]).toBeUndefined();                  // ПІВОТ так і не настав
  });

  it("ПІСЛЯ півота (минуще): повтори до успіху, ЖОДНОЇ компенсації", async () => {
    const w = makeWorld({ switchBilling: 2 });            // білінг падає двічі, тоді встає
    const saga = await drive(w.ports, "h1", w.S);
    expect(saga.status).toBe("done");
    expect(w.fired["switchBilling"]).toBe(3);             // 2 падіння + 1 успіх
    expect(w.fired["transferAndShred"]).toBe(1);          // півот стався
    expect(w.log.some((x) => COMPS.includes(x))).toBe(false);            // нічого не відкочено
  });

  it("ПІСЛЯ півота (затяте): повтори вичерпано → DLQ і сигнал людині, без відкату", async () => {
    const w = makeWorld({ switchBilling: 999 });          // білінг лежить назавжди
    const saga = await drive(w.ports, "h1", w.S);
    expect(saga.status).toBe("stuck");                    // застрягло → мертва черга
    expect(w.box.alerted).toBe("h1");                     // людину покликано
    expect(w.fired["switchBilling"]).toBe(MAX_ATTEMPTS + 1);
    expect(w.fired["transferAndShred"]).toBe(1);          // передане лишається переданим
    expect(w.log.some((x) => COMPS.includes(x))).toBe(false);           // нічого не відкочено
  });

  it("КРАХ на терміналі: курсор за останнім кроком, статус іще 'running' → підйом завершує в 'done', без DLQ", async () => {
    const w = makeWorld({});
    // Щілина: остання транзакція вже посунула cursor ЗА останній крок (applyStep закомітив),
    // але p.persist(status='done') не встиг — машину смикнули з розетки саме тут.
    await w.ports.persist({ id: "h1", homeId: "home-1", cursor: w.S.length, dir: "forward", status: "running", attempts: 0 });
    const saga = await drive(w.ports, "h1", w.S);
    expect(saga.status).toBe("done");     // підйом дочитав термінал із самого курсора
    expect(w.box.alerted).toBeNull();     // сагу НЕ здано в DLQ — вона таки завершилась
    expect(w.log).toEqual([]);            // жодного кроку не перезапущено
  });
});

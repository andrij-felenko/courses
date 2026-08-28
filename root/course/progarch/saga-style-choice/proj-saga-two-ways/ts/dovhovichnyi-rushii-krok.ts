type Step = { name: string; run: () => Promise<void>; comp: () => Promise<void> };
type SagaState = { cursor: number; status: "running" | "compensating" | "committed" | "compensated" };

class Store {                                 // «диск» — переживає смерть процесу саги
  private db = new Map<string, SagaState>();
  load(id: string) { return this.db.get(id); }
  save(id: string, st: SagaState) { this.db.set(id, { ...st }); }   // копія = «лягло на диск»
}

class ProcessKilled extends Error {}          // імітація жорсткої смерті процесу

async function runSaga(id: string, steps: Step[], store: Store) {
  const st = store.load(id) ?? { cursor: 0, status: "running" as const };

  // ── ВІДРОДЖЕННЯ: диск каже не лише «доки дійшло» (cursor), а й «куди йшло» (status) ──
  if (st.status === "committed" || st.status === "compensated") return;   // уже завершено
  if (st.status === "compensating") { await rollBack(id, steps, store, st); return; }  // помер ПОСЕРЕД відкоту → дороби відкіт, не прямий хід

  try {
    while (st.cursor < steps.length) {
      await steps[st.cursor].run();
      st.cursor += 1;
      store.save(id, st);                     // ← крок зафіксовано на диску ПЕРЕД наступним
    }
    st.status = "committed"; store.save(id, st);
  } catch (err) {
    if (err instanceof ProcessKilled) { store.save(id, st); throw err; }  // не відкіт — процес помер, диск лишився
    st.status = "compensating"; store.save(id, st);   // ← спершу зафіксуй НАПРЯМОК на диску, тоді відкочуй
    await rollBack(id, steps, store, st);
    throw err;
  }
}

// Відкіт зворотним порядком. Сюди веде ДВА шляхи: свіжий бізнес-збій (щойно вгорі)
// і відродження процесу, що помер посеред цього самого відкоту.
async function rollBack(id: string, steps: Step[], store: Store, st: SagaState) {
  while (st.cursor > 0) {
    st.cursor -= 1;
    await steps[st.cursor].comp();
    store.save(id, st);                       // прогрес відкоту теж лягає на диск
  }
  st.status = "compensated"; store.save(id, st);
}

const step = (name: string, run: () => Promise<void>, comp: () => Promise<void>): Step =>
  ({ name, run, comp });

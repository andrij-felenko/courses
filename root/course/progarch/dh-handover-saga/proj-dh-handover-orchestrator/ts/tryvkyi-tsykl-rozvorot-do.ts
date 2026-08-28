const sleep = (_ms: number) => new Promise((r) => setTimeout(r, _ms));
const backoff = (n: number) => fullJitter(n);   // відступ із джитером — деталі в іншому кроці

async function tick(p: Ports, saga: Saga, steps: Step[]): Promise<Saga> {
  if (saga.status !== "running") return saga;
  const pivot = steps.findIndex((s) => s.kind === "pivot");

  if (saga.dir === "back") {                          // ── задкуємо, відкочуючи ──
    if (saga.cursor < 0) { saga.status = "aborted"; await p.persist(saga); return saga; }
    const step = steps[saga.cursor];
    await applyStep(p, saga, step, "back");           // компенсація + cursor-- атомарно
    if (saga.cursor < 0) saga.status = "aborted";     // відкотили все → чисте скасування
    await p.persist(saga);
    return saga;
  }

  // ── ідемо вперед ──
  if (saga.cursor >= steps.length) {                  // курсор ЗА останнім кроком = ЗАВЕРШЕНО (термінал з курсора)
    saga.status = "done"; await p.persist(saga); return saga;   // ідемпотентний сторож: закриває щілину крах-на-терміналі
  }
  const step = steps[saga.cursor];                    // тепер гарантовано в межах
  try {
    await applyStep(p, saga, step, "forward");        // ефект + cursor++ атомарно
    saga.attempts = 0;
    if (saga.cursor >= steps.length) saga.status = "done";      // ступили за останній → done уже цього такту
    await p.persist(saga);
  } catch (err) {
    if (err instanceof WaitingForHuman) {             // awaitClaim паркується — це НЕ невдача
      saga.status = "waiting"; saga.deadline = err.until;
      await p.persist(saga);
    } else if (saga.cursor > pivot) {                 // ПІСЛЯ півота: не скасовуй — повторюй, тоді DLQ
      saga.attempts += 1;
      if (saga.attempts > MAX_ATTEMPTS) {             // затято застрягло → мертва черга
        saga.status = "stuck"; await p.persist(saga); await p.alert(saga, step, err);
      } else {
        await p.persist(saga); await sleep(backoff(saga.attempts));   // той самий cursor — повтор
      }
    } else {                                          // ДО півота: розвертайся й відкочуй зроблене
      saga.dir = "back"; saga.cursor -= 1;            // невдалий крок не завершився — компенсуємо лише DONE
      await p.persist(saga);
    }
  }
  return saga;
}

// Тривкий цикл: пам'ять — у сховищі, тож крах = перезавантажити й тикати далі.
async function drive(p: Ports, id: string, steps: Step[]): Promise<Saga> {
  let saga = await p.load(id);
  while (saga.status === "running") saga = await tick(p, saga, steps);
  return saga;                                        // done | aborted | stuck | waiting
}

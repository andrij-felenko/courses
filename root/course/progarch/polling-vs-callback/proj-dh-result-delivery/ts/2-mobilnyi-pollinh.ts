// ТЕЛЕФОН — поллінг ОБМЕЖЕНИЙ: бюджет часу + експоненційний відступ + ПОВНИЙ джитер.
// Виходимо, коли: термінальний стан АБО вичерпано бюджет АБО згорнули екран (abort).
async function pollJob(id: string, budgetMs: number, signal: AbortSignal): Promise<Job> {
  const deadline = Date.now() + budgetMs;           // напр. 5 хв — далі спінер не має сенсу
  const base = 1000, cap = 15_000;                  // 1 → 2 → 4 → 8 → стеля 15 с
  for (let attempt = 0; ; attempt++) {
    const job = await (await fetch(`/jobs/${id}`, { signal })).json();
    if (job.status === "done" || job.status === "failed") return job; // ← єдиний нормальний вихід

    const window = Math.min(cap, base * 2 ** attempt);
    const wait = Math.random() * window;            // повний джитер: рівномірно в [0, вікно]
    if (Date.now() + wait > deadline) throw new Error("poll budget exhausted"); // не спати за бюджет
    await sleep(wait, signal);                      // прокидається на abort → екран згорнули
  }
}

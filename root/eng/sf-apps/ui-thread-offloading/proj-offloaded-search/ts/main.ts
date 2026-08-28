// ═══ main.ts — усе тут виконується на потоці інтерфейсу ══════════════════
type Found     = { kind: "found";     ids: Uint32Array };
type Failed    = { kind: "failed";    message: string };
type Cancelled = { kind: "cancelled" };
type Reply = (Found | Failed | Cancelled) & { gen: number };

const worker = new Worker(new URL("./search-worker.js", import.meta.url),
                          { type: "module" });

// Прапорець скасування мусять бачити обидва боки ОДНОЧАСНО, а звичайного
// повідомлення робітник не побачить, доки крутить свій цикл. Тому — спільна
// пам'ять. SharedArrayBuffer живе лише на сторінці з cross-origin isolation
// (COOP: same-origin + COEP: require-corp); інакше запасний план — terminate().
const shared = crossOriginIsolated ? new SharedArrayBuffer(4) : null;
const cancelFlag = shared ? new Int32Array(shared) : null;
if (shared) worker.postMessage({ kind: "init", shared });

let generation = 0;
let debounceTimer: ReturnType<typeof setTimeout> | undefined;
let busy = false;                     // робітник зараз щось рахує
let pending: string | null = null;    // ← скриня на одне місце, ворота 2

// ── Ворота 1: 150 мс тиші ──
export function onInput(text: string): void {
  if (cancelFlag) Atomics.store(cancelFlag, 0, 1);   // те, що біжить, не потрібне
  clearTimeout(debounceTimer);                       // кожен знак переставляє таймер
  debounceTimer = setTimeout(() => start(text), 150);
}

// ── Ворота 2 і 3: скриня та штамп покоління ──
function start(text: string): void {
  if (busy) { pending = text; return; }   // витісняє попереднє нестартоване
  busy = true;
  if (cancelFlag) Atomics.store(cancelFlag, 0, 0);   // нове завдання — чистий прапорець
  const gen = ++generation;
  showSpinner();
  worker.postMessage({ kind: "search", text, gen });
}

// ── Ворота 5: onmessage — це і є маршалінг у чергу потоку інтерфейсу ──
worker.onmessage = (e: MessageEvent<Reply>) => {
  busy = false;                          // ЗВІЛЬНЯЄМО РОБІТНИКА ПЕРШИМ
  if (pending !== null) { const next = pending; pending = null; start(next); }

  const msg = e.data;
  if (msg.gen !== generation) return;    // застаріла відповідь — тихо в нікуди
  hideSpinner();
  switch (msg.kind) {
    case "found":     renderRows(msg.ids); break;
    case "failed":    showError(msg.message); break;
    case "cancelled": break;             // користувач сам передумав
  }
};

// Закриття: без цього робітник живе далі й тримає весь індекс у пам'яті
export function dispose(): void {
  clearTimeout(debounceTimer);
  if (cancelFlag) Atomics.store(cancelFlag, 0, 1);
  worker.terminate();
}

// ═══ search-worker.ts — окремий потік; DOM тут недоступний ═══════════════
let flag: Int32Array | null = null;
const records: Row[] = loadIndex();

self.onmessage = (e: MessageEvent) => {
  const msg = e.data;
  if (msg.kind === "init") { flag = new Int32Array(msg.shared); return; }
  if (msg.kind !== "search") return;

  try {
    const ids = new Uint32Array(200);
    let n = 0;
    for (let i = 0; i < records.length; i++) {
      // ── Ворота 4: погляд у прапорець на межі блоку ──
      if ((i & 0x1ff) === 0 && flag && Atomics.load(flag, 0) === 1) {
        self.postMessage({ kind: "cancelled", gen: msg.gen });
        return;
      }
      if (matches(records[i], msg.text)) {
        ids[n++] = i;
        if (n === ids.length) break;
      }
    }
    const out = ids.slice(0, n);
    // Другий аргумент — список того, що ПЕРЕДАЄМО, а не копіюємо:
    // після цього рядка out.buffer тут уже відірваний (detached).
    self.postMessage({ kind: "found", ids: out, gen: msg.gen }, [out.buffer]);
  } catch (err) {
    self.postMessage({ kind: "failed", message: String(err), gen: msg.gen });
  }
};

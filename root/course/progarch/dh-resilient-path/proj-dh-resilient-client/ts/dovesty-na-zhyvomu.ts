// Фейкова мережа: лічить ОДНОЧАСНІ виклики на сервіс і душить телеметрію.
const delay = (ms: number) => new Promise((r) => setTimeout(r, ms));

class FakeNet {
  maxConc: Record<string, number> = {};
  private live: Record<string, number> = {};
  telemetryMode: "healthy" | "slow" | "fail" = "healthy";

  transportFor(dep: string): Transport {
    return async (_addr, _path, _body, signal) => {
      this.live[dep] = (this.live[dep] ?? 0) + 1;
      this.maxConc[dep] = Math.max(this.maxConc[dep] ?? 0, this.live[dep]);
      try {
        if (dep === "telemetry" && this.telemetryMode === "slow") {
          await abortable(5000, signal);                       // висить 5 с; таймаут скасує на 3-й
          return { status: 200, body: [] };
        }
        if (dep === "telemetry" && this.telemetryMode === "fail") {
          await delay(20); return { status: 503, body: null }; // швидко падає
        }
        await delay(20); return { status: 200, body: sample(dep) };
      } finally { this.live[dep]--; }
    };
  }
}
// abortable: чекає ms, але прокидається помилкою, щойно таймаут викликав abort (скасування).
function abortable(ms: number, signal: AbortSignal): Promise<void> {
  return new Promise((resolve, reject) => {
    const t = setTimeout(resolve, ms);
    signal.addEventListener("abort", () => { clearTimeout(t); reject(new Error("aborted")); });
  });
}

async function testDegradeAndIsolate() {
  const net = new FakeNet();
  net.telemetryMode = "slow";                                 // ← душимо телеметрію
  // 50 головних екранів + 10 команд «зачинити», усі водночас.
  const screens = Array.from({ length: 50 }, (_, i) => timed(() => mainScreen(`u${i}`)));
  const cmds = Array.from({ length: 10 }, (_, i) => lockDoor(`d${i}`));
  const [tiles, cmdRes] = await Promise.all([Promise.all(screens), Promise.allSettled(cmds)]);

  // 1. Екран ДЕГРАДУВАВ, а не завис: кожна плитка має пристрій, але reading = null.
  assert(tiles.every((t) => t.value.every((x) => x.device && x.reading === null)));
  // 2. Телеметрія НЕ з'їла більше за свій пул; ядро качало вільно.
  assert(net.maxConc.telemetry <= 10);
  assert(net.maxConc.core >= 40);
  // 3. БІЛЬШІСТЬ екранів повернулись швидко (миттєвий «відсік повний» → фолбек).
  assert(tiles.filter((t) => t.ms < 100).length >= 40);
  // 4. Усі команди пройшли своїм пулом — жодної брехні «зачинено».
  assert(cmdRes.every((c) => c.status === "fulfilled"));
  console.log("деградація й ізоляція: OK", net.maxConc);
}

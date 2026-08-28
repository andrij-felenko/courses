class FakeWire implements Wire {
  silent = false;
  dropAckOnce = false;
  constructor(private srv: CloudServer) {}
  async postCmd(cmd: Command): Promise<Result> {
    if (this.silent) throw new Unreachable();
    return this.srv.handleCmd(cmd);
  }
  async postReport(rep: Report): Promise<void> {
    if (this.silent) throw new Unreachable();                 // хмара мовчить
    this.srv.handleReport(rep);                                // дійшло й ЗАСТОСОВАНО
    if (this.dropAckOnce) { this.dropAckOnce = false; throw new Unreachable(); } // …а ACK загублено
  }
  async getState(dev: string): Promise<string> {
    if (this.silent) throw new Unreachable();
    return this.srv.get(dev);
  }
}

class Hub {                                                    // життєвий контур: кнопка → замок
  lock = "closed";
  private tick = 0;
  constructor(private cloud: NetworkCloud) {}
  press(open: boolean): void {                                // жодного await, жодного Wire — локально
    this.lock = open ? "open" : "closed";
    this.cloud.emit({ dev: "lock-42", field: "lock", value: this.lock, ts: ++this.tick });
  }
}

test("межа переживає тишу хмари", async () => {
  const srv = new CloudServer();
  const wire = new FakeWire(srv);
  wire.dropAckOnce = true;                                     // озброїмо один загублений ACK
  const cloud = new NetworkCloud(wire);
  const ac = new AbortController();
  const flushing = cloud.flushLoop(ac.signal);
  const hub = new Hub(cloud);

  const N = 20;
  let pendingMid = 0;
  for (let i = 1; i <= N; i++) {
    if (i === 5)  wire.silent = true;                          // ← хмара впала ПОСЕРЕД потоку
    if (i === 14) pendingMid = cloud.pending();                // буфер тримає непідтверджені
    if (i === 15) wire.silent = false;                         // ← зв'язок вернувся
    hub.press(i % 2 === 0);
    await sleep(2);                                            // хай флашер устигне щось доставити
  }

  const want = N % 2 === 0 ? "open" : "closed";
  expect(hub.lock).toBe(want);                                // 1) контур не здригнувся
  expect(pendingMid).toBeGreaterThan(0);                      // 2) store-and-forward тримав звіти

  const t0 = performance.now();                               // 3) чекаємо, поки буфер долетить
  while (cloud.pending() > 0 && performance.now() - t0 < 5000) await sleep(10);
  expect(cloud.pending()).toBe(0);
  expect(srv.applied).toBe(N);                                // 4) кожен звіт застосовано РІВНО раз
  expect(srv.get("lock-42")).toBe(want);                      // 5) хмара догнала дім

  ac.abort();
  await flushing;
});

type DeviceId = string;
type State = number;
type Update = { deviceId: DeviceId; version: number; value: State };

// (1) ДЖЕРЕЛО — свій монотонний лічильник НА КОЖЕН пристрій
class Source {
  private version = new Map<DeviceId, number>();
  stamp(deviceId: DeviceId, value: State): Update {
    const next = (this.version.get(deviceId) ?? 0) + 1;   // 1, 2, 3 … окремо на пристрій
    this.version.set(deviceId, next);
    return { deviceId, version: next, value };
  }
}

// (2) ВАРТОВИЙ — те, що випробовуємо; одне число межі на пристрій
class Store {
  private value = new Map<DeviceId, State>();
  private applied = new Map<DeviceId, number>();
  versionOf(id: DeviceId): number {
    return this.applied.get(id) ?? -1;                    // −1 = пристрій ще не знайомий
  }
  applyUpdate(u: Update): "applied" | "dropped" {
    if (u.version <= this.versionOf(u.deviceId)) return "dropped";
    this.value.set(u.deviceId, u.value);
    this.applied.set(u.deviceId, u.version);              // рухаємо межу ЦЬОГО пристрою
    return "applied";
  }
  snapshot(): Map<DeviceId, State> { return new Map(this.value); }
}

// маленький ГПВЧ із зерном — щоб будь-яке падіння відтворити точно
function mulberry32(seed: number): () => number {
  let s = seed >>> 0;
  return () => {
    s = (s + 0x6d2b79f5) >>> 0;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
function shuffle<T>(a: T[], rnd: () => number): void {     // Фішер–Єйтс
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(rnd() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
}

// (3) СТЕНД — одне випробування з фіксованим зерном
function runTrial(seed: number): void {
  const rnd = mulberry32(seed);
  const source = new Source();
  const store = new Store();
  const devices = ["living", "bedroom", "hall", "kitchen"];

  // 3a. істинний потік: кожен пристрій дістає серію оновлень зі зростальними версіями
  const stream: Update[] = [];
  for (const d of devices) {
    const n = 1 + Math.floor(rnd() * 12);                 // 1..12 оновлень на пристрій
    for (let i = 0; i < n; i++) {
      stream.push(source.stamp(d, Math.round(rnd() * 100)));
    }
  }

  // 3b. ОРАКУЛ: ціль знаємо напряму — найбільша версія на пристрій
  const oracle = new Map<DeviceId, { version: number; value: State }>();
  for (const u of stream) {
    const cur = oracle.get(u.deviceId);
    if (cur === undefined || u.version > cur.version) {
      oracle.set(u.deviceId, { version: u.version, value: u.value });
    }
  }

  // 3c. ЗЛОВОРОЖА МЕРЕЖА: задублювати ×1..3 і перемішати
  const scrambled: Update[] = [];
  for (const u of stream) {
    const copies = 1 + Math.floor(rnd() * 3);             // 1..3 копії кожного оновлення
    for (let c = 0; c < copies; c++) scrambled.push(u);
  }
  shuffle(scrambled, rnd);

  // 3d. згодувати вартовому у переставленому, задубльованому порядку
  for (const u of scrambled) store.applyUpdate(u);

  // 3e. ствердити: кінець кожного пристрою = оновлення з найбільшою версією
  const final = store.snapshot();
  for (const d of devices) {
    const want = oracle.get(d)!.value;
    const got = final.get(d);
    if (got !== want) {
      throw new Error(`seed=${seed} ${d}: чекали ${want} (max версія), маємо ${got}`);
    }
  }
  if (final.size !== oracle.size) {                       // жодних привидів — див. пастку 1
    throw new Error(`seed=${seed}: привид-пристрій у підсумку`);
  }
}

for (let seed = 1; seed <= 10_000; seed++) runTrial(seed);
console.log("10000 випробувань пройдено: копія щоразу зійшлася до правди");

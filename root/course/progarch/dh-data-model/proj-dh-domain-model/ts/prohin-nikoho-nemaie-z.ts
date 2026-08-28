// ── 4. Прогін: «нікого немає» з одним офлайн-замком ──

// Макет заліза: знає, хто на зв'язку. Online — замкнеться; offline — мовчить.
// (У житті тут Wi-Fi, черга команд, таймаути, повторні спроби.)
class FakeGateway implements DeviceGateway {
  constructor(private online: Set<string>) {}
  bringOnline(id: string): void { this.online.add(id); }
  sendLock(id: DeviceId): LockOutcome {
    if (!this.online.has(id.value)) return { kind: "offline" };
    return { kind: "acked", state: "Locked" };
  }
}

// Будуємо дім із десятьма дверима.
const homeId = new HomeId("h-1");
const home = new Home(homeId, new UserId("u-owner"));
const hall = new RoomId("hall");
home.addRoom(hall);

const doorNames = ["front","back","garage","balcony","cellar","gate","patio","side","roof","shed"];
const locks = new Map<string, Lock>();
for (const name of doorNames) {
  const id = new DeviceId(name);
  home.attachLock(id);
  locks.set(name, new Lock(id, homeId, new Location(hall, name)));
}

// Гараж — офлайн. Решта дев'ять — на зв'язку.
const gateway = new FakeGateway(new Set(doorNames.filter(n => n !== "garage")));
const reconciler = new AwayReconciler(gateway);

// Власник тисне «йдемо»: дім ставить БАЖАНИЙ режим — і тільки. Це одна транзакція.
home.setMode("Away");

// Прохід 1: дев'ять замкнулися, гараж мовчить.
const r1 = reconciler.sweep(home, locks);
console.log("прохід 1:", r1.toString(), "· зведено:", r1.settled);
console.log("гараж зараз:", locks.get("garage")!.current);

// ...згодом гараж повертається на зв'язок. Повторюємо — доганяємо решту.
gateway.bringOnline("garage");
const r2 = reconciler.sweep(home, locks);
console.log("прохід 2:", r2.toString(), "· зведено:", r2.settled);
console.log("гараж зараз:", locks.get("garage")!.current);

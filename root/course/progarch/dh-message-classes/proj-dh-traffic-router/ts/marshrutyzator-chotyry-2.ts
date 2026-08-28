const dh = new DHTraffic();

// command → адресована черга: лише той замок дістає команду
const garageGot: Command[] = [];
dh.registerDevice("lock-garage", c => garageGot.push(c));
dh.registerDevice("lock-front",  () => { throw new Error("front не мав дістати цю команду!"); });
dh.command("lock-garage", { deviceId: "lock-garage", verb: "close" });
console.log("command → гаражний замок дістав", garageGot.length, "(front — жодної)");

// append → журнал: два незалежні читачі, кожен бачить УСЕ у своєму темпі
for (let i = 0; i < 3; i++) dh.append({ deviceId: "th-1", kind: "temp", value: 20 + i, at: i });
const panel1 = dh.telemetry.read("live-panel").length;   // 3 — усе, що є
dh.append({ deviceId: "th-1", kind: "temp", value: 23, at: 3 });
const panel2 = dh.telemetry.read("live-panel").length;   // 1 — лише нове, свій offset посунувся
const history = dh.telemetry.read("history").length;     // 4 — свій offset із нуля: усе з початку
console.log("append  → панель:", panel1, "+", panel2, " історія:", history, "(кожен свій offset)");

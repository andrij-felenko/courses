const store = new ShardStore();
const audit = new AuditLog();
store.seed({ homeId: "home42", version: 5, bolt: "unlocked", lastCmd: "" });   // дім уже жив
const svc = new TwinService(store, audit);

// (1) КОМАНДА «замкни двері» — крізь живу сесію (гідратація + наскрізний запис)
svc.command("home42", { kind: "lock", seq: 6, by: "owner" });
console.log(svc.show("home42"));   // ТЕПЛЕ: {version:6, bolt:"locked", lastCmd:"owner#6"} — з актора

// (2) вузол із домом home42 ГИНЕ — жива сесія зникає разом із пам'яттю вузла
svc.release("home42");             // (аварія === сесії більше нема)
console.log(svc.show("home42"));   // ХОЛОДНЕ: {version:6, bolt:"locked"} — прямо зі шарда, повз актор

// (3) наступна команда просто РЕГІДРАТУЄ на іншому вузлі — «відновлення» = store.get
svc.command("home42", { kind: "unlock", seq: 7, by: "owner" });
console.log(svc.show("home42"));   // {version:7, bolt:"unlocked"} — стан піднято з рядка, не з нуля

// (4) ІСТОРІЯ «хто відмикав уночі» — прямо з журналу, повз актор і поточний стан
for (const e of svc.history("home42", 0, Date.now() + 1))
  console.log(e.action, "by", e.by);   // locked by owner ; unlocked by owner

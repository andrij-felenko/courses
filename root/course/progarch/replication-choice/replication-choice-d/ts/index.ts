// ── Один лідер: усі записи серіалізуються в одному місці ──
class SingleLeader {
  private value: string | null = null;
  write(v: string) { this.value = v; }      // лягає ПОВЕРХ попереднього
  read()           { return this.value; }   // завжди рівно одне значення
}
const leader = new SingleLeader();
leader.write("off");        // застосунок вимкнув обігрівач
leader.write("on");         // автоматизація ввімкнула — ПІЗНІШЕ, побачивши "off"
console.log(leader.read()); // -> "on"   одна історія, конфлікту нема за побудовою

// ── Кілька писарів: два вузли приймають запис у той самий ключ ──
class Replica {
  value: string | null = null;
  constructor(public name: string) {}
  write(v: string) { this.value = v; }
}
const a = new Replica("A"), b = new Replica("B");
a.write("off");             // застосунок пише у вузол свого регіону
b.write("on");              // хаб пише в інший вузол — у ту саму мить, не бачачи A
// репліки синхронізуються й виявляють: обидва змінили ключ НЕЗАЛЕЖНО
const versions = new Set([a.value, b.value]);  // -> {"off","on"} — дві версії
console.assert(versions.size === 2);           // жодна не "пізніша" → конфлікт

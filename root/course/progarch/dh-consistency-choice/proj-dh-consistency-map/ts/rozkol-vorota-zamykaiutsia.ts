// Локальне керування домом — НЕ потребує ні хмари, ні кворуму.
class Hub {
  private telemetry: Array<{ key: string; value: number }> = [];
  constructor(private edge: Replica) {}
  toggleLight(on: boolean): string { return `лампу ${on ? "увімкнено" : "вимкнено"} локально`; }
  recordTemp(key: string, celsius: number): void { this.telemetry.push({ key, value: celsius }); }
  backlog(): number { return this.telemetry.length; }
}

const a = new Replica("A"), b = new Replica("B"), edge = new Replica("E·край");
const cloud = new Cluster([a, b, edge], a, (to) => (to === b ? 1 : 5));
const GK = "grant:home-42:guest";
cloud.write(GK, true); cloud.advance(10);   // усі копії: v1(true) — доступ виданий

edge.linked = false;                         // РОЗКОЛ: край відрізано від хмари

cloud.write(GK, false); cloud.advance(10);   // у хмарі відкликано (a,b → v2); до краю НЕ доходить

// Дім живе локально: хаб керує пристроями й копить телеметрію в чергу.
const hub = new Hub(edge);
console.log("хаб:", hub.toggleLight(true));          // працює без хмари
hub.recordTemp("temp:home-42:kitchen", 21.4);
console.log("телеметрія в черзі:", hub.backlog());   // доллється потім

// Ворота на боці хаба: доступна ЛИШЕ застаріла edge.
console.log("край локально каже:", readEventual(GK, edge)?.value); // true — ЗАСТАРІЛЕ!
console.log("ворота (строго, лише край):",
            mayOpen(GK, [edge]) ? "ВІДЧИНИТИ" : "ВІДМОВА");          // fail-closed
console.log("ворота (строго, хмара):",
            mayOpen(GK, [a, b]) ? "ВІДЧИНИТИ" : "ВІДМОВА");          // бачить v2

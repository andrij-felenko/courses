// hub.ts — увесь «розумний дім» Digital Homes v0, один файл
const THRESHOLD = 20.0;          // °C — поріг зашитий просто в код

// ── Драйвери-моки: кімната живе в пам'яті. Холоне сама,
//    гріється, коли ввімкнено розетку. ──
let roomTemp = 18.0;             // прихований «фізичний» стан, °C
let heaterIsOn = false;          // чи подано живлення

function readSensor(): number {  // драйвер давача → °C
  roomTemp += (heaterIsOn ? 0.4 : -0.2) + (Math.random() - 0.5) * 0.1;
  return Math.round(roomTemp * 10) / 10;
}

function heaterOn(): void {      // драйвер розетки: подати живлення
  if (!heaterIsOn) {             // ідемпотентно: не смикати реле дарма
    heaterIsOn = true;
    console.log("[розетка] обігрівач УВІМКНЕНО");
  }
}

function heaterOff(): void {
  if (heaterIsOn) {
    heaterIsOn = false;
    console.log("[розетка] обігрівач вимкнено");
  }
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

// ── Серце дому: read → decide → act, і так вічно. ──
async function main() {
  while (true) {
    const t = readSensor();              // read
    if (t < THRESHOLD) heaterOn();       // decide → act
    else heaterOff();
    await sleep(30_000);                 // знову спитати давач за 30 с
  }
}
main();

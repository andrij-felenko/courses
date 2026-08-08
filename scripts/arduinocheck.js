#!/usr/bin/env node
/* ============================================================================
   arduinocheck.js — ЛОКАЛЬНИЙ гейт «приклад не має бути лише під Arduino».

   Arduino сам по собі нормальний і часто найзрозуміліший — питання в тому, що
   стаття, де він ЄДИНИЙ, мовчки прирівнює «як це робиться» до «як це робиться
   на Arduino». Читач із ESP-IDF, STM32, Zephyr чи звичайного Linux лишається
   без перекладу. Тому гейт шукає не Arduino, а Arduino БЕЗ пари.

   Що робить:
     • ріже кожен .md на код-блоки (``` … ```) і групи вкладок (:::tabs … :::);
     • судить КОЖЕН блок: Arduino / інша платформа / нейтральний;
     • судить прозу окремо: пояснення, що спирається на Arduino (скетч, IDE,
       назви плат) без жодної згадки іншої платформи;
     • дає вирок на файл.

   Вироки:
     ✖ ЛИШЕ ARDUINO      — код Arduino є, іншої платформи в статті нема зовсім
     ▲ ВКЛАДКА-ОДИНАК    — :::tabs-група, де всі вкладки Arduino (перемикач
                            обіцяє вибір, а вибору нема) — навіть якщо деінде
                            у файлі альтернатива є
     · ПРОЗА ЧЕРЕЗ ARDUINO — коду нема, але пояснення веде через Arduino й лише
                            через нього
     ✓ Arduino + ще щось — усе гаразд, у звіті не показується

   Запуск:  node scripts/arduinocheck.js                    (увесь корпус)
            node scripts/arduinocheck.js catalog/sensors    (тека)
            node scripts/arduinocheck.js --all              (перелічити всі файли)
            node scripts/arduinocheck.js --json out.json    (payload для батчу)
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const argv = process.argv.slice(2);
const showAll = argv.includes("--all");
const jsonAt = argv.indexOf("--json");
const jsonOut = jsonAt >= 0 ? argv[jsonAt + 1] : null;
const targets = argv.filter((a, i) => !a.startsWith("--") && i !== jsonAt + 1);
const ROOTS = targets.length ? targets : ["book", "guide", "catalog", "reference"];

/* --- Ознаки ---------------------------------------------------------------
   Arduino пізнається за ФУНКЦІЯМИ його середовища, не за словом «Arduino»:
   стаття може жодного разу його не назвати, а весь код бути скетчем. */
const ARDUINO_STRONG = [
  /\bdigital(Write|Read)\s*\(/, /\bpinMode\s*\(/, /\banalog(Read|Write|Reference)\s*\(/,
  /\battachInterrupt\s*\(/, /\bSerial[0-9]?\s*\.\s*(begin|print|println|available|read|write)\s*\(/,
  /#\s*include\s*<Arduino\.h>/, /\bWire\s*\.\s*(begin|beginTransmission|requestFrom)\s*\(/,
  /\bSPI\s*\.\s*(begin|transfer|beginTransaction)\s*\(/, /\b(tone|noTone|pulseIn|shiftOut|shiftIn)\s*\(/,
  /\bEEPROM\s*\.\s*(read|write|get|put)\s*\(/, /\bSoftwareSerial\b/, /\bServo\s+\w+\s*;/,
];
// setup()+loop() разом — теж сильна ознака, але тільки в парі
const HAS_SETUP = /\bvoid\s+setup\s*\(\s*\)/;
const HAS_LOOP = /\bvoid\s+loop\s*\(\s*\)/;
const ARDUINO_WEAK = [/\bdelay\s*\(\s*\d/, /\bmillis\s*\(\s*\)/, /\bmicros\s*\(\s*\)/, /\bmap\s*\(\s*\w+\s*,/, /\bHIGH\b|\bLOW\b/];

const ALT_PLATFORM = [
  // ESP-IDF / FreeRTOS
  [/\besp_err_t\b|\bgpio_set_level\s*\(|\bgpio_config\s*\(|\bESP_LOG[EWIDV]\s*\(|\bnvs_/, "ESP-IDF"],
  [/\bxTaskCreate\w*\s*\(|\bvTaskDelay\s*\(|\bxQueue\w+\s*\(/, "FreeRTOS"],
  // STM32
  [/\bHAL_[A-Z]\w*\s*\(|\bLL_[A-Z]\w*\s*\(|\bGPIO[A-K]\s*->|\bRCC\s*->|\bTIM\d\s*->/, "STM32"],
  // Zephyr
  [/\bgpio_pin_(set|get|configure)_dt\s*\(|\bk_(msleep|sleep|work)\b|\bDT_(ALIAS|NODELABEL)\s*\(/, "Zephyr"],
  // Linux userspace
  [/\bioctl\s*\(|\/sys\/(class|bus|devices)\/|\/dev\/(gpiochip|i2c-|spidev|tty)|\bgpiod_\w+\s*\(|\blibgpiod\b/, "Linux"],
  [/\bopen\s*\(\s*"\/dev\/|\bmmap\s*\(|\bO_RDWR\b/, "Linux"],
  // Raspberry Pi / Python-платформи
  [/\bRPi\.GPIO\b|\bgpiozero\b|\bimport\s+board\b|\bbusio\b|\bperiphery\b/, "RPi/Python"],
  [/\bmachine\.(Pin|I2C|SPI|ADC)\b|\bfrom\s+machine\s+import\b/, "MicroPython"],
  // Голе залізо без вендорного HAL
  [/\*\s*\(\s*volatile\s+uint(8|16|32)_t\s*\*\s*\)|->\s*(ODR|BSRR|IDR|MODER|CRL|CRH)\b/, "регістри"],
  [/\bnrf_gpio_\w+\s*\(|\bnrfx_\w+\s*\(/, "nRF"],
  [/\bavr\/io\.h\b|\bPORT[A-D]\s*(\||&)?=|\bDDR[A-D]\s*(\||&)?=|_BV\s*\(/, "AVR-регістри"],
  [/\bpico\/stdlib\.h\b|\bgpio_put\s*\(|\bsleep_ms\s*\(/, "RP2040 SDK"],
];

/* Теги мов, що САМІ називають платформу: вкладка «micropython» біля вкладки «cpp» —
   це вже другий приклад, навіть якщо в тілі нема жодного machine.Pin. Тег тут вагоміший
   за вміст, бо саме він каже читачеві, під що цей код. */
const LANG_PLATFORM = {
  micropython: "MicroPython", circuitpython: "CircuitPython", verilog: "HDL", vhdl: "HDL", rust: "Rust", go: "Go",
  "esp-idf": "ESP-IDF", espidf: "ESP-IDF", esp32: "ESP-IDF",
  stm32: "STM32", "stm32-hal": "STM32", "stm32-ll": "STM32",
  zephyr: "Zephyr", "pico-sdk": "RP2040 SDK", avr: "AVR-регістри",
};
// теги, що САМІ означають «це скетч» — навіть якщо в тілі жодного digitalWrite
const LANG_ARDUINO = new Set(["arduino", "ino"]);

// Мови, які самі по собі означають «не скетч»
const NEUTRAL_LANGS = new Set(["", "text", "txt", "console", "shell", "bash", "sh", "ini", "cfg",
  "json", "yaml", "yml", "toml", "make", "makefile", "cmake", "diff", "asm", "s"]);
const C_LANGS = new Set(["c", "cpp", "c++", "arduino", "ino", "h", "hpp"]);

/* Проза, що спирається саме на Arduino.
   ГОЛОВНА ознака мусить бути присутня — назви плат самі по собі не годяться: «Leonardo»
   ловив Леонардо да Вінчі в історії тертя, «sketch» — count-min-sketch у алгоритмах,
   а «Nano» зловив би текстовий редактор у unix-linux. Тому плати рахуються ЛИШЕ поряд
   зі згадкою самого Arduino. */
const PROSE_ARDUINO_MAIN = /\bArduino\b|\bАрду[іи]но\b|\bскетч/i;
const PROSE_ARDUINO_BOARD = /\bArduino\s+(Uno|Nano|Mega|Leonardo|Pro\s*Mini)\b|\b(Uno|Mega\s*2560)\b/i;
const PROSE_ALT = /\bESP-?IDF\b|\bESP32\b|\bSTM32\b|\bZephyr\b|\bLinux\b|\bRaspberry\b|\bMicroPython\b|\bCircuitPython\b|\bFreeRTOS\b|\bnRF\d|\bRP2040\b|\bPico\b|\bAVR\b|\bплат[аиуі]\s+на\s+\w+|\bбез\s+Arduino\b/i;

function walk(dir, out) {
  let ents; try { ents = fs.readdirSync(dir, { withFileTypes: true }) } catch (e) { return out }
  for (const e of ents) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) { if (e.name !== "img" && e.name !== "node_modules" && e.name[0] !== "_") walk(p, out) }
    else if (e.isFile() && e.name.endsWith(".md") && e.name[0] !== "_") out.push(p);
  }
  return out;
}

/* Розбір файлу на блоки. Повертає {blocks, tabGroups, prose}. */
function parse(md) {
  const lines = md.split(/\r?\n/);
  const blocks = [], tabGroups = [];
  let cur = null, tabs = null, prose = [];
  for (let i = 0; i < lines.length; i++) {
    const L = lines[i];
    if (!cur && /^:::tabs\b/.test(L.trim())) { tabs = { line: i + 1, blocks: [] }; continue; }
    if (!cur && tabs && /^:::\s*$/.test(L.trim())) { tabGroups.push(tabs); tabs = null; continue; }
    const fence = L.match(/^\s*```([a-zA-Z0-9+#_-]*)\s*$/);
    if (fence && !cur) { cur = { lang: fence[1].toLowerCase(), line: i + 1, body: [] }; continue; }
    if (cur && /^\s*```\s*$/.test(L)) {
      cur.text = cur.body.join("\n");
      blocks.push(cur); if (tabs) tabs.blocks.push(cur);
      cur = null; continue;
    }
    if (cur) cur.body.push(L); else prose.push(L);
  }
  if (tabs) tabGroups.push(tabs);            // незакрита група — все одно судимо
  return { blocks, tabGroups, prose: prose.join("\n") };
}

function judgeBlock(b) {
  const t = b.text || "";
  let ard = 0;
  for (const re of ARDUINO_STRONG) if (re.test(t)) ard += 2;
  if (HAS_SETUP.test(t) && HAS_LOOP.test(t)) ard += 2;
  if (LANG_ARDUINO.has(b.lang)) ard += 2;
  if (ard === 0) { let w = 0; for (const re of ARDUINO_WEAK) if (re.test(t)) w++; if (w >= 3) ard = 1; }
  const alts = [];
  for (const [re, name] of ALT_PLATFORM) if (re.test(t)) alts.push(name);
  if (LANG_PLATFORM[b.lang]) alts.push(LANG_PLATFORM[b.lang]);
  // мова, що не C/C++ і не службова, — сама по собі інша доріжка
  const otherLang = !C_LANGS.has(b.lang) && !NEUTRAL_LANGS.has(b.lang) ? b.lang : null;
  return { arduino: ard >= 2, alts: [...new Set(alts)], otherLang };
}

const results = [];
const STAT = { files: 0, withArduino: 0, paired: 0 };
for (const r of ROOTS) {
  for (const f of walk(path.join(ROOT, r), [])) {
    STAT.files++;
    const md = fs.readFileSync(f, "utf8");
    const { blocks, tabGroups, prose } = parse(md);
    const judged = blocks.map(judgeBlock);
    const ardBlocks = judged.filter((j) => j.arduino).length;
    // ПАРОЮ рахується лише КОД на іншій платформі. Ані блок іншою мовою (Python, що
    // рахує формулу, не показує, як це зробити не на Arduino), ані згадка «на ESP32
    // так само» в прозі парою не є: читачеві потрібен другий приклад, а не обіцянка.
    const altSet = new Set();
    for (const j of judged) for (const a of j.alts) altSet.add(a);
    const otherLangs = new Set(judged.map((j) => j.otherLang).filter(Boolean));

    // вкладки-одинаки: група, де є Arduino і ЖОДНОЇ альтернативи серед вкладок
    const lonelyTabs = [];
    for (const g of tabGroups) {
      const js = g.blocks.map(judgeBlock);
      if (!js.some((j) => j.arduino)) continue;
      const alt = js.some((j) => j.alts.length || j.otherLang);
      if (!alt) lonelyTabs.push({ line: g.line, tabs: g.blocks.length });
    }

    // Головна ознака обов'язкова; назва плати сама по собі вироку не робить (див. коментар
    // біля PROSE_ARDUINO_BOARD) — вона лише підсилює вже наявну згадку.
    const proseArd = PROSE_ARDUINO_MAIN.test(prose);
    const proseBoard = proseArd && PROSE_ARDUINO_BOARD.test(prose);
    const proseAlt = PROSE_ALT.test(prose);

    if (ardBlocks) STAT.withArduino++;
    if (ardBlocks && altSet.size) STAT.paired++;

    let verdict = null;
    if (ardBlocks && altSet.size === 0) verdict = "only";
    else if (lonelyTabs.length) verdict = "tabs";
    else if (!ardBlocks && proseArd && !proseAlt) verdict = "prose";
    // без вироку файл потрапляє у звіт лише з --all і лише якщо Arduino там ВЗАГАЛІ є:
    // решта корпусу до цього гейта стосунку не має.
    if (!verdict && (!showAll || !ardBlocks)) continue;

    results.push({
      file: path.relative(ROOT, f).replace(/\\/g, "/"),
      verdict: verdict || "ok", ardBlocks, blocks: blocks.length,
      alts: [...altSet], otherLangs: [...otherLangs], lonelyTabs, proseArd, proseBoard, proseAlt,
    });
  }
}

const V = { only: "✖ ЛИШЕ ARDUINO", tabs: "▲ ВКЛАДКА-ОДИНАК", prose: "· ПРОЗА ЧЕРЕЗ ARDUINO", ok: "✓ є пара" };
const ORDER = ["only", "tabs", "prose", "ok"];
console.log(`\n== ARDUINO-ГЕЙТ ==  перевірено тек: ${ROOTS.join(", ")}`);
for (const v of ORDER) {
  const grp = results.filter((r) => r.verdict === v);
  if (!grp.length || (v === "ok" && !showAll)) continue;
  console.log(`\n-- ${V[v]} (${grp.length}) --`);
  const byDir = {};
  for (const r of grp) { const d = r.file.split("/").slice(0, 2).join("/"); (byDir[d] = byDir[d] || []).push(r) }
  for (const d of Object.keys(byDir).sort((a, b) => byDir[b].length - byDir[a].length)) {
    console.log(`  ${String(byDir[d].length).padStart(4)}  ${d}`);
    if (showAll || v === "only") for (const r of byDir[d].slice(0, showAll ? 1e9 : 6)) {
      const near = [r.otherLangs.length ? "поруч " + r.otherLangs.join("/") : "", r.proseAlt ? "проза згадує іншу платформу" : ""].filter(Boolean).join(", ");
      const tail = v === "tabs" ? `  вкладок-одинаків ${r.lonelyTabs.length} (рядки ${r.lonelyTabs.map((t) => t.line).join(", ")})`
        : v === "only" ? `  arduino-блоків ${r.ardBlocks}/${r.blocks}${near ? "  · " + near : ""}`
          : "";
      console.log(`        ${r.file}${tail}`);
    }
    if (!showAll && v === "only" && byDir[d].length > 6) console.log(`        … і ще ${byDir[d].length - 6} (--all покаже всі)`);
  }
}
const flagged = results.filter((r) => r.verdict !== "ok");
const pct = STAT.withArduino ? Math.round((100 * (STAT.withArduino - STAT.paired)) / STAT.withArduino) : 0;
console.log(`\n  .md переглянуто ${STAT.files} · з Arduino-КОДОМ ${STAT.withArduino} · з них мають пару ${STAT.paired}, без пари ${STAT.withArduino - STAT.paired} (${pct}%)`);
console.log(`  разом до правки: ${flagged.length}  (лише-arduino ${results.filter((r) => r.verdict === "only").length} · вкладки-одинаки ${results.filter((r) => r.verdict === "tabs").length} · проза ${results.filter((r) => r.verdict === "prose").length})`);

if (jsonOut) {
  fs.writeFileSync(jsonOut, JSON.stringify(flagged, null, 2), "utf8");
  console.log(`  payload → ${jsonOut}`);
}
process.exit(0);

#!/usr/bin/env node
/* ============================================================================
   writefile.js — записати файл у теку теми, не борючись із кодуванням оболонки.

   ЧОМУ ЦЕ ІСНУЄ. 2026-08-19 у scripts/ назбиралося шістнадцять власних збирачів
   на дві теми: build.py, build_all.py, build_mems.py, build_mems_all.py,
   build_all_mems_clean.py, gen_all.py, make_all_heap.py, gen_heap.py… Кожен
   починався заново з makedirs і власного write_file, три з них навіть не
   компілюються, один містив друкарську помилку в імені змінної, а найбільший
   (21 КБ) обірваний посеред рядка. Поруч лежали math_b64.txt і hist_b64.txt —
   текст статей у base64, і write_hex.py, що складав файл із шістнадцяткового
   рядка в аргументі. Це все — обхід однієї й тієї самої проблеми: українську
   прозу важко провести через оболонку Windows без спотворення.

   Тому один інструмент замість шістнадцяти одноразових:

     node scripts/writefile.js <файл> --b64 <base64>          вміст у base64
     node scripts/writefile.js <файл> --hex <шістнадцятково>  вміст шістнадцятково
     node scripts/writefile.js <файл> --from <джерело>        копія іншого файлу
     echo … | node scripts/writefile.js <файл> --stdin        з потоку

     --append   дописати в кінець, а не перезаписати
     --dry      сказати, що зробив би, і нічого не робити

   Завжди: створює теку, пише UTF-8 без BOM, нормалізує переноси на \n,
   відмовляється писати поза репозиторієм і друкує шлях та розмір.
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const argv = process.argv.slice(2);
const val = (n) => { const i = argv.indexOf("--" + n); return i >= 0 ? argv[i + 1] : null; };
const has = (n) => argv.includes("--" + n);

const file = argv[0] && !argv[0].startsWith("--") ? argv[0] : null;
if (!file) {
  console.error("Ужиток: node scripts/writefile.js <файл> --b64|--hex <дані> | --from <джерело> | --stdin  [--append] [--dry]");
  process.exit(2);
}

const abs = path.resolve(ROOT, file);
if (!abs.startsWith(ROOT + path.sep)) { console.error(`✖ поза репозиторієм: ${abs}`); process.exit(2); }

function body(cb) {
  if (val("b64") !== null) return cb(Buffer.from(val("b64"), "base64"));
  if (val("hex") !== null) return cb(Buffer.from(val("hex").replace(/\s+/g, ""), "hex"));
  if (val("from") !== null) return cb(fs.readFileSync(path.resolve(ROOT, val("from"))));
  if (has("stdin")) {
    const chunks = [];
    process.stdin.on("data", (d) => chunks.push(d));
    process.stdin.on("end", () => cb(Buffer.concat(chunks)));
    return;
  }
  console.error("✖ звідки брати вміст: --b64, --hex, --from або --stdin");
  process.exit(2);
}

body((buf) => {
  /* Проза в корпусі — UTF-8 із \n. BOM ламає перший заголовок, CRLF ламає порівняння
     цитат у review-apply, тож і те, і те знімаємо тут, а не в кожному викликачі. */
  let text = buf.toString("utf8").replace(/^\uFEFF/, "").replace(/\r\n/g, "\n");
  if (!text.endsWith("\n")) text += "\n";
  const mode = has("append") ? "дописано" : "записано";
  if (has("dry")) { console.log(`[dry] ${mode} б ${path.relative(ROOT, abs)} — ${text.length} символів`); return; }
  fs.mkdirSync(path.dirname(abs), { recursive: true });
  if (has("append")) fs.appendFileSync(abs, text, "utf8"); else fs.writeFileSync(abs, text, "utf8");
  const size = fs.statSync(abs).size;
  console.log(`${mode}: ${path.relative(ROOT, abs).split(path.sep).join("/")} — ${text.split("\n").length - 1} рядків, ${size} байт`);
});

import os

os.makedirs("book/programming/databases/mvcc/img", exist_ok=True)

svg1 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 280" width="100%" height="100%">
<style>
  .box { fill: #1e293b; stroke: #3b82f6; stroke-width: 2; rx: 8px; }
  .box-dead { fill: #1e293b; stroke: #ef4444; stroke-width: 2; rx: 8px; }
  .box-live { fill: #1e293b; stroke: #10b981; stroke-width: 2; rx: 8px; }
  .hdr { fill: #0f172a; stroke: #64748b; stroke-width: 1; rx: 8px; }
  .txt { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 13px; }
  .txt-bold { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 14px; font-weight: bold; }
  .txt-muted { fill: #94a3b8; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 11px; }
  .arrow { stroke: #38bdf8; stroke-width: 2; fill: none; marker-end: url(#arrowhead); }
</style>
<defs>
  <marker id="arrowhead" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="#38bdf8" />
  </marker>
</defs>
<rect width="800" height="280" fill="#0b0f19" rx="12" />
<text x="30" y="35" class="txt-bold" font-size="16">Ланцюжок версій рядка (Tuple Version Chain / Undo Chain)</text>
<text x="30" y="55" class="txt-muted">Зв'язок між версіями через покажчики t_ctid / roll_ptr та межі видимості xmin / xmax</text>
<g transform="translate(40, 80)">
  <rect width="210" height="150" class="box-dead" />
  <rect width="210" height="30" class="hdr" />
  <text x="15" y="20" class="txt-bold" fill="#ef4444">Версія 1 (Застаріла)</text>
  <text x="15" y="50" class="txt">xmin: 100 (Створена T100)</text>
  <text x="15" y="72" class="txt">xmax: 105 (Змінена T105)</text>
  <text x="15" y="94" class="txt">t_ctid: (0, 2) → V2</text>
  <text x="15" y="125" class="txt-bold" fill="#38bdf8">Дані: balance = $100</text>
</g>
<path d="M 250 155 L 290 155" class="arrow" />
<g transform="translate(295, 80)">
  <rect width="210" height="150" class="box-dead" />
  <rect width="210" height="30" class="hdr" />
  <text x="15" y="20" class="txt-bold" fill="#ef4444">Версія 2 (Застаріла)</text>
  <text x="15" y="50" class="txt">xmin: 105 (Створена T105)</text>
  <text x="15" y="72" class="txt">xmax: 110 (Змінена T110)</text>
  <text x="15" y="94" class="txt">t_ctid: (0, 3) → V3</text>
  <text x="15" y="125" class="txt-bold" fill="#38bdf8">Дані: balance = $150</text>
</g>
<path d="M 505 155 L 545 155" class="arrow" />
<g transform="translate(550, 80)">
  <rect width="210" height="150" class="box-live" />
  <rect width="210" height="30" class="hdr" />
  <text x="15" y="20" class="txt-bold" fill="#10b981">Версія 3 (Поточна/Жива)</text>
  <text x="15" y="50" class="txt">xmin: 110 (Створена T110)</text>
  <text x="15" y="72" class="txt">xmax: 0 (Не видалена)</text>
  <text x="15" y="94" class="txt">t_ctid: (0, 3) [Self]</text>
  <text x="15" y="125" class="txt-bold" fill="#38bdf8">Дані: balance = $220</text>
</g>
</svg>"""

svg2 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 300" width="100%" height="100%">
<style>
  .bar { fill: #1e293b; stroke: #64748b; stroke-width: 1.5; rx: 6px; }
  .zone-past { fill: #064e3b; opacity: 0.7; rx: 6px; }
  .zone-active { fill: #78350f; opacity: 0.7; }
  .zone-future { fill: #7f1d1d; opacity: 0.7; rx: 6px; }
  .txt { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 13px; }
  .txt-bold { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 14px; font-weight: bold; }
  .txt-muted { fill: #94a3b8; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 11px; }
  .marker { stroke: #38bdf8; stroke-dasharray: 4; stroke-width: 2; }
</style>
<rect width="800" height="300" fill="#0b0f19" rx="12" />
<text x="30" y="35" class="txt-bold" font-size="16">Правило видимості знімка: Snapshot(xmin=100, xmax=120, active=[105, 115])</text>
<text x="30" y="55" class="txt-muted">Вісь транзакційних ідентифікаторів (XID) та класифікація видимості кортежів</text>
<rect x="50" y="100" width="700" height="50" class="bar" />
<rect x="50" y="100" width="230" height="50" class="zone-past" />
<rect x="280" y="100" width="240" height="50" class="zone-active" />
<rect x="520" y="100" width="230" height="50" class="zone-future" />
<line x1="280" y1="80" x2="280" y2="180" class="marker" />
<text x="250" y="75" class="txt-bold" fill="#38bdf8">xmin = 100</text>
<line x1="520" y1="80" x2="520" y2="180" class="marker" />
<text x="490" y="75" class="txt-bold" fill="#38bdf8">xmax = 120</text>
<text x="80" y="130" class="txt-bold" fill="#34d399">XID &lt; 100: Зафіксовані</text>
<text x="80" y="145" class="txt-muted">Повністю ВИДИМІ</text>
<text x="320" y="125" class="txt-bold" fill="#fbbf24">100 ≤ XID &lt; 120</text>
<text x="295" y="142" class="txt-muted">Активні [105, 115]: НЕВИДИМІ</text>
<text x="560" y="130" class="txt-bold" fill="#f87171">XID ≥ 120: Майбутні</text>
<text x="560" y="145" class="txt-muted">Повністю НЕВИДИМІ</text>
<g transform="translate(50, 190)">
  <rect width="210" height="80" fill="#1e293b" stroke="#10b981" stroke-width="1.5" rx="6" />
  <text x="15" y="25" class="txt-bold" fill="#34d399">✓ T95 (XID=95)</text>
  <text x="15" y="45" class="txt">Зафіксована до xmin</text>
  <text x="15" y="65" class="txt-muted">Результат: ВИДИМО</text>
</g>
<g transform="translate(295, 190)">
  <rect width="210" height="80" fill="#1e293b" stroke="#ef4444" stroke-width="1.5" rx="6" />
  <text x="15" y="25" class="txt-bold" fill="#f87171">✗ T105 (В активних)</text>
  <text x="15" y="45" class="txt">Виконується паралельно</text>
  <text x="15" y="65" class="txt-muted">Результат: НЕВИДИМО</text>
</g>
<g transform="translate(540, 190)">
  <rect width="210" height="80" fill="#1e293b" stroke="#ef4444" stroke-width="1.5" rx="6" />
  <text x="15" y="25" class="txt-bold" fill="#f87171">✗ T125 (XID ≥ xmax)</text>
  <text x="15" y="45" class="txt">Почалася після знімка</text>
  <text x="15" y="65" class="txt-muted">Результат: НЕВИДИМО</text>
</g>
</svg>"""

svg3 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 280" width="100%" height="100%">
<style>
  .box { fill: #1e293b; stroke: #64748b; stroke-width: 1.5; rx: 6px; }
  .box-purge { fill: #3b0764; stroke: #a855f7; stroke-width: 2; stroke-dasharray: 4; rx: 6px; }
  .txt { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 13px; }
  .txt-bold { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 14px; font-weight: bold; }
  .txt-muted { fill: #94a3b8; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 11px; }
  .line-threshold { stroke: #ef4444; stroke-width: 2; stroke-dasharray: 6; }
</style>
<rect width="800" height="280" fill="#0b0f19" rx="12" />
<text x="30" y="35" class="txt-bold" font-size="16">Очищення застарілих версій (Vacuum / Purge) та поріг OldestXmin</text>
<text x="30" y="55" class="txt-muted">Версії з xmax &lt; OldestXmin стають мертвими для всіх активних транзакцій та видаляються</text>
<line x1="420" y1="80" x2="420" y2="240" class="line-threshold" />
<text x="430" y="100" class="txt-bold" fill="#ef4444">OldestXmin = 200</text>
<text x="430" y="118" class="txt-muted">Найстарша активна транзакція</text>
<g transform="translate(40, 120)">
  <rect width="160" height="110" class="box-purge" />
  <text x="12" y="25" class="txt-bold" fill="#c084fc">Мертва версія 1</text>
  <text x="12" y="50" class="txt">xmin: 120, xmax: 150</text>
  <text x="12" y="70" class="txt-muted">xmax (150) &lt; 200</text>
  <text x="12" y="95" class="txt-bold" fill="#ef4444">🗑️ ПРИБИРАЄТЬСЯ</text>
</g>
<g transform="translate(220, 120)">
  <rect width="160" height="110" class="box-purge" />
  <text x="12" y="25" class="txt-bold" fill="#c084fc">Мертва версія 2</text>
  <text x="12" y="50" class="txt">xmin: 150, xmax: 180</text>
  <text x="12" y="70" class="txt-muted">xmax (180) &lt; 200</text>
  <text x="12" y="95" class="txt-bold" fill="#ef4444">🗑️ ПРИБИРАЄТЬСЯ</text>
</g>
<g transform="translate(440, 120)">
  <rect width="160" height="110" class="box" stroke="#3b82f6" stroke-width="2" />
  <text x="12" y="25" class="txt-bold" fill="#60a5fa">Потрібна версія</text>
  <text x="12" y="50" class="txt">xmin: 180, xmax: 220</text>
  <text x="12" y="70" class="txt-muted">xmax (220) ≥ 200</text>
  <text x="12" y="95" class="txt-bold" fill="#38bdf8">🔒 ЗБЕРІГАЄТЬСЯ</text>
</g>
<g transform="translate(615, 120)">
  <rect width="150" height="110" class="box" stroke="#10b981" stroke-width="2" />
  <text x="12" y="25" class="txt-bold" fill="#34d399">Поточна жива</text>
  <text x="12" y="50" class="txt">xmin: 220, xmax: 0</text>
  <text x="12" y="70" class="txt-muted">xmax = 0 (Активна)</text>
  <text x="12" y="95" class="txt-bold" fill="#34d399">✓ АКТИВНА</text>
</g>
</svg>"""

svg4 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 260" width="100%" height="100%">
<style>
  .card { fill: #1e293b; stroke: #334155; stroke-width: 1.5; rx: 8px; }
  .txt { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 13px; }
  .txt-bold { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 14px; font-weight: bold; }
  .txt-muted { fill: #94a3b8; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 11px; }
</style>
<rect width="800" height="260" fill="#0b0f19" rx="12" />
<text x="30" y="35" class="txt-bold" font-size="16">Порівняння конкуренції: Песимістичні замки (2PL) проти MVCC</text>
<g transform="translate(40, 70)">
  <rect width="335" height="160" class="card" stroke="#ef4444" stroke-width="2" />
  <text x="20" y="30" class="txt-bold" fill="#f87171" font-size="15">Традиційне блокування (2PL)</text>
  <text x="20" y="60" class="txt">⛔ Читач бере Shared Lock → Блокує Запис</text>
  <text x="20" y="85" class="txt">⛔ Письменник бере Exclusive Lock → Блокує Читання</text>
  <text x="20" y="110" class="txt">⚠️ Довгі аналітичні SELECT паралізують OLTP</text>
  <text x="20" y="135" class="txt-muted">Результат: Простій ядер, дедлоки під навантаженням</text>
</g>
<g transform="translate(425, 70)">
  <rect width="335" height="160" class="card" stroke="#10b981" stroke-width="2" />
  <text x="20" y="30" class="txt-bold" fill="#34d399" font-size="15">Багатоверсійність (MVCC)</text>
  <text x="20" y="60" class="txt">✓ Читачі бачать свій історичний знімок</text>
  <text x="20" y="85" class="txt">✓ Письменники створюють нові версії рядків</text>
  <text x="20" y="110" class="txt">⚡ Читачі НІКОЛИ не блокують Письменників</text>
  <text x="20" y="135" class="txt-bold" fill="#38bdf8">Письменники НІКОЛИ не блокують Читачів</text>
</g>
</svg>"""

with open("book/programming/databases/mvcc/img/version-chain.svg", "w", encoding="utf-8") as f: f.write(svg1)
with open("book/programming/databases/mvcc/img/snapshot-visibility.svg", "w", encoding="utf-8") as f: f.write(svg2)
with open("book/programming/databases/mvcc/img/vacuum-cleanup.svg", "w", encoding="utf-8") as f: f.write(svg3)
with open("book/programming/databases/mvcc/img/mvcc-vs-locking.svg", "w", encoding="utf-8") as f: f.write(svg4)

print("Generated MVCC SVGs")

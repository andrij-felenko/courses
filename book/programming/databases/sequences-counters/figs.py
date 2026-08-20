import os

img_dir = "book/programming/databases/sequences-counters/img"
os.makedirs(img_dir, exist_ok=True)

# 1. sequence-contention-gap.svg
svg1 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 320" width="100%" height="100%">
<style>
  .bg { fill: #0b0f19; rx: 12px; }
  .box { fill: #1e293b; stroke: #3b82f6; stroke-width: 1.5; rx: 8px; }
  .box-err { fill: #1e293b; stroke: #ef4444; stroke-width: 1.5; rx: 8px; }
  .box-hilo { fill: #0f172a; stroke: #10b981; stroke-width: 1.5; rx: 8px; }
  .txt { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 13px; }
  .txt-bold { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 14px; font-weight: bold; }
  .txt-muted { fill: #94a3b8; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 11px; }
  .txt-red { fill: #f87171; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; font-weight: bold; }
  .txt-green { fill: #34d399; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; font-weight: bold; }
  .arrow { stroke: #38bdf8; stroke-width: 2; fill: none; marker-end: url(#ah); }
  .seq-cell { fill: #334155; stroke: #64748b; stroke-width: 1; rx: 4px; }
  .seq-gap { fill: #7f1d1d; stroke: #ef4444; stroke-width: 1.5; stroke-dasharray: 3 3; rx: 4px; }
</style>
<defs>
  <marker id="ah" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="#38bdf8" />
  </marker>
</defs>
<rect width="880" height="320" class="bg" />
<text x="30" y="32" class="txt-bold" font-size="16">Механіка утворення дірок у централізованих послідовностях та оптимізація Hi/Lo</text>
<text x="30" y="52" class="txt-muted">Відкат транзакції (ROLLBACK) вивільняє блокування, але не повертає стан лічильника SEQUENCE</text>

<!-- Секція 1: Транзакційний відкат -->
<g transform="translate(30, 75)">
  <rect width="400" height="225" class="box-err" />
  <text x="20" y="28" class="txt-bold" fill="#f87171">Централізований SEQUENCE + ROLLBACK</text>
  
  <rect x="20" y="45" width="60" height="35" class="seq-cell" />
  <text x="35" y="67" class="txt-bold">#101</text>
  
  <rect x="90" y="45" width="60" height="35" class="seq-cell" />
  <text x="105" y="67" class="txt-bold">#102</text>
  
  <rect x="160" y="45" width="60" height="35" class="seq-gap" />
  <text x="175" y="67" class="txt-red">#103</text>
  
  <rect x="230" y="45" width="60" height="35" class="seq-cell" />
  <text x="245" y="67" class="txt-bold">#104</text>
  
  <rect x="300" y="45" width="60" height="35" class="seq-cell" />
  <text x="315" y="67" class="txt-bold">#105</text>

  <text x="20" y="110" class="txt">Транзакція A: nextval() = 101 → COMMIT</text>
  <text x="20" y="132" class="txt">Транзакція B: nextval() = 102 → COMMIT</text>
  <text x="20" y="154" class="txt-red">Транзакція C: nextval() = 103 → ПОМИЛКА / ROLLBACK</text>
  <text x="20" y="176" class="txt">Транзакція D: nextval() = 104 → COMMIT</text>
  <text x="20" y="206" class="txt-muted">Дірка #103 залишається назавжди: лічильник не відкочується</text>
</g>

<!-- Секція 2: Алгоритм Hi/Lo -->
<g transform="translate(450, 75)">
  <rect width="400" height="225" class="box-hilo" />
  <text x="20" y="28" class="txt-bold" fill="#34d399">Блокова алокація діапазонів (Алгоритм Hi/Lo)</text>
  
  <rect x="20" y="48" width="170" height="55" class="box" stroke="#10b981" />
  <text x="30" y="70" class="txt-bold" fill="#6ee7b7">БД: Hi = 42</text>
  <text x="30" y="90" class="txt-muted">next_hi = nextval()</text>

  <path d="M 200 75 L 230 75" class="arrow" />

  <rect x="240" y="48" width="140" height="55" class="box" stroke="#38bdf8" />
  <text x="250" y="70" class="txt-bold" fill="#38bdf8">Вузол 1 (RAM)</text>
  <text x="250" y="90" class="txt-muted">Lo: 0..999</text>

  <text x="20" y="130" class="txt">Діапазон ID: [42 × 1000] .. [42 × 1000 + 999]</text>
  <text x="20" y="152" class="txt">Генерація в RAM: atomic_inc(Lo) без дискового I/O</text>
  <text x="20" y="174" class="txt-green">1 звернення до бази на 1000 виданих ID</text>
  <text x="20" y="206" class="txt-muted">При краху вузла втрачається лише нерозданий хвіст Lo</text>
</g>
</svg>"""

# 2. snowflake-bit-layout.svg
svg2 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 340" width="100%" height="100%">
<style>
  .bg { fill: #0b0f19; rx: 12px; }
  .bit-box { stroke-width: 1.5; rx: 6px; }
  .txt { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 13px; }
  .txt-bold { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 14px; font-weight: bold; }
  .txt-mono { fill: #f8fafc; font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace; font-size: 12px; }
  .txt-muted { fill: #94a3b8; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 11px; }
</style>
<rect width="880" height="340" class="bg" />
<text x="30" y="32" class="txt-bold" font-size="16">Анатомія 64-бітного ідентифікатора Twitter Snowflake та 128-бітного UUIDv7</text>
<text x="30" y="52" class="txt-muted">Розподіл бітових полів забезпечує монотонне сортування за часом та децентралізовану унікальність</text>

<!-- 64-bit Snowflake -->
<g transform="translate(30, 75)">
  <text x="0" y="16" class="txt-bold" fill="#60a5fa">Twitter Snowflake (64 біти / 8 байтів — Int64 / BIGINT)</text>
  
  <!-- 1-bit unused -->
  <rect x="0" y="28" width="30" height="50" class="bit-box" fill="#1e293b" stroke="#64748b" />
  <text x="8" y="58" class="txt-mono" fill="#94a3b8">0</text>
  <text x="4" y="94" class="txt-muted">1 б.</text>

  <!-- 41-bit timestamp -->
  <rect x="35" y="28" width="460" height="50" class="bit-box" fill="#1e3a5f" stroke="#3b82f6" />
  <text x="130" y="52" class="txt-bold" fill="#93c5fd">Часова мітка (Timestamp)</text>
  <text x="145" y="68" class="txt-mono" fill="#bfdbfe">41 біт (мілісекунди від епохи)</text>
  <text x="210" y="94" class="txt-muted">41 біт ≈ 69.7 року</text>

  <!-- 10-bit node ID -->
  <rect x="500" y="28" width="160" height="50" class="bit-box" fill="#134e4a" stroke="#14b8a6" />
  <text x="530" y="52" class="txt-bold" fill="#5eead4">Вузол / Node ID</text>
  <text x="545" y="68" class="txt-mono" fill="#99f6e4">10 бітів (0..1023)</text>
  <text x="540" y="94" class="txt-muted">1024 машини/потоки</text>

  <!-- 12-bit sequence -->
  <rect x="665" y="28" width="155" height="50" class="bit-box" fill="#701a75" stroke="#d946ef" />
  <text x="690" y="52" class="txt-bold" fill="#f0abfc">Лічильник</text>
  <text x="695" y="68" class="txt-mono" fill="#fae8ff">12 бітів (0..4095)</text>
  <text x="680" y="94" class="txt-muted">4096 ID / мс / вузол</text>
</g>

<!-- 128-bit UUIDv7 -->
<g transform="translate(30, 205)">
  <text x="0" y="16" class="txt-bold" fill="#34d399">UUIDv7 за RFC 9562 (128 бітів / 16 байтів — Binary(16) / UUID)</text>
  
  <!-- 48-bit unix_ts_ms -->
  <rect x="0" y="28" width="310" height="50" class="bit-box" fill="#1e3a5f" stroke="#3b82f6" />
  <text x="70" y="52" class="txt-bold" fill="#93c5fd">unix_ts_ms (Unix час)</text>
  <text x="85" y="68" class="txt-mono" fill="#bfdbfe">48 бітів (мілісекунди)</text>
  <text x="100" y="94" class="txt-muted">До 10889 року н.е.</text>

  <!-- 4-bit ver -->
  <rect x="315" y="28" width="45" height="50" class="bit-box" fill="#312e81" stroke="#6366f1" />
  <text x="323" y="52" class="txt-bold" fill="#a5b4fc">0111</text>
  <text x="320" y="68" class="txt-mono" fill="#c7d2fe">ver 7</text>
  <text x="320" y="94" class="txt-muted">4 біти</text>

  <!-- 12-bit rand_a / sub-ms seq -->
  <rect x="365" y="28" width="160" height="50" class="bit-box" fill="#701a75" stroke="#d946ef" />
  <text x="390" y="52" class="txt-bold" fill="#f0abfc">rand_a / seq</text>
  <text x="400" y="68" class="txt-mono" fill="#fae8ff">12 бітів ентропії</text>
  <text x="395" y="94" class="txt-muted">Субмілісекундний лічильник</text>

  <!-- 2-bit var -->
  <rect x="530" y="28" width="45" height="50" class="bit-box" fill="#312e81" stroke="#6366f1" />
  <text x="540" y="52" class="txt-bold" fill="#a5b4fc">10</text>
  <text x="535" y="68" class="txt-mono" fill="#c7d2fe">var 2</text>
  <text x="535" y="94" class="txt-muted">2 біти</text>

  <!-- 62-bit rand_b -->
  <rect x="580" y="28" width="240" height="50" class="bit-box" fill="#064e3b" stroke="#10b981" />
  <text x="635" y="52" class="txt-bold" fill="#6ee7b7">rand_b (Крипто-ентропія)</text>
  <text x="640" y="68" class="txt-mono" fill="#a7f3d0">62 біти випадкових чисел</text>
  <text x="625" y="94" class="txt-muted">Захист від колізій без координації</text>
</g>
</svg>"""

# 3. btree-locality-uuid4-vs-uuid7.svg
svg3 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 320" width="100%" height="100%">
<style>
  .bg { fill: #0b0f19; rx: 12px; }
  .card-err { fill: #1e293b; stroke: #ef4444; stroke-width: 1.5; rx: 8px; }
  .card-ok { fill: #1e293b; stroke: #10b981; stroke-width: 1.5; rx: 8px; }
  .page { fill: #334155; stroke: #64748b; stroke-width: 1; rx: 4px; }
  .page-split { fill: #7f1d1d; stroke: #ef4444; stroke-width: 1.5; rx: 4px; }
  .page-tail { fill: #064e3b; stroke: #10b981; stroke-width: 1.5; rx: 4px; }
  .txt { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 13px; }
  .txt-bold { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 14px; font-weight: bold; }
  .txt-muted { fill: #94a3b8; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 11px; }
  .txt-red { fill: #f87171; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; font-weight: bold; }
  .txt-green { fill: #34d399; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; font-weight: bold; }
  .arrow-red { stroke: #ef4444; stroke-width: 1.5; fill: none; marker-end: url(#ar); }
  .arrow-green { stroke: #10b981; stroke-width: 1.5; fill: none; marker-end: url(#ag); }
</style>
<defs>
  <marker id="ar" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><polygon points="0 0, 6 3, 0 6" fill="#ef4444" /></marker>
  <marker id="ag" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><polygon points="0 0, 6 3, 0 6" fill="#10b981" /></marker>
</defs>
<rect width="880" height="320" class="bg" />
<text x="30" y="32" class="txt-bold" font-size="16">Поведінка B-Tree індексу: випадковий UUIDv4 проти час-сортованого UUIDv7 / Snowflake</text>
<text x="30" y="52" class="txt-muted">Випадкові вставки призводять до лавиноподібного розщеплення сторінок та деградації буферного пулу</text>

<!-- UUIDv4 -->
<g transform="translate(30, 75)">
  <rect width="400" height="225" class="card-err" />
  <text x="20" y="28" class="txt-bold" fill="#f87171">UUIDv4 (Повністю випадковий розподіл)</text>
  
  <rect x="20" y="45" width="70" height="45" class="page-split" />
  <text x="30" y="65" class="txt">Сторінка 1</text>
  <text x="30" y="80" class="txt-muted">50% fill</text>

  <rect x="100" y="45" width="70" height="45" class="page-split" />
  <text x="110" y="65" class="txt">Сторінка 2</text>
  <text x="110" y="80" class="txt-muted">50% fill</text>

  <rect x="180" y="45" width="70" height="45" class="page-split" />
  <text x="190" y="65" class="txt">Сторінка 3</text>
  <text x="190" y="80" class="txt-muted">Page Split!</text>

  <rect x="260" y="45" width="70" height="45" class="page-split" />
  <text x="270" y="65" class="txt">Сторінка 4</text>
  <text x="270" y="80" class="txt-muted">50% fill</text>

  <path d="M 135 100 L 135 118" class="arrow-red" />
  <path d="M 215 100 L 215 118" class="arrow-red" />

  <text x="20" y="135" class="txt-red">Випадкова адресація = постійний Random I/O</text>
  <text x="20" y="157" class="txt">• Лавинне розщеплення B-Tree сторінок (Page Splits)</text>
  <text x="20" y="177" class="txt">• Ефективність заповнення сторінок падає до ~50%</text>
  <text x="20" y="197" class="txt">• Вимивання гарячого кешу в Buffer Pool RAM</text>
</g>

<!-- UUIDv7 / Snowflake -->
<g transform="translate(450, 75)">
  <rect width="400" height="225" class="card-ok" />
  <text x="20" y="28" class="txt-bold" fill="#34d399">UUIDv7 / Snowflake (Час-сортований ID)</text>
  
  <rect x="20" y="45" width="70" height="45" class="page" />
  <text x="30" y="65" class="txt">Сторінка 1</text>
  <text x="30" y="80" class="txt-green">95% fill</text>

  <rect x="100" y="45" width="70" height="45" class="page" />
  <text x="110" y="65" class="txt">Сторінка 2</text>
  <text x="110" y="80" class="txt-green">95% fill</text>

  <rect x="180" y="45" width="70" height="45" class="page" />
  <text x="190" y="65" class="txt">Сторінка 3</text>
  <text x="190" y="80" class="txt-green">95% fill</text>

  <rect x="260" y="45" width="90" height="45" class="page-tail" />
  <text x="270" y="65" class="txt">Хвіст дерева</text>
  <text x="270" y="80" class="txt-green">Right-Append</text>

  <path d="M 305 100 L 305 118" class="arrow-green" />

  <text x="20" y="135" class="txt-green">Строго монотонна дозапис у правий край (Append-Only)</text>
  <text x="20" y="157" class="txt">• Нуль розщеплень проміжних вузлів</text>
  <text x="20" y="177" class="txt">• Максимальна щільність заповнення сторінок (~95–99%)</text>
  <text x="20" y="197" class="txt">• Всі вставки потрапляють у єдину гарячу сторінку в RAM</text>
</g>
</svg>"""

# 4. sharded-counter-striping.svg
svg4 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 320" width="100%" height="100%">
<style>
  .bg { fill: #0b0f19; rx: 12px; }
  .panel { fill: #1e293b; stroke: #334155; stroke-width: 1.5; rx: 8px; }
  .slot { fill: #0f172a; stroke: #3b82f6; stroke-width: 1.5; rx: 6px; }
  .txt { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 13px; }
  .txt-bold { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 14px; font-weight: bold; }
  .txt-mono { fill: #f8fafc; font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace; font-size: 12px; }
  .txt-muted { fill: #94a3b8; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 11px; }
  .arrow { stroke: #38bdf8; stroke-width: 1.5; fill: none; marker-end: url(#ah); }
  .arrow-sum { stroke: #10b981; stroke-width: 2; fill: none; marker-end: url(#ag); }
</style>
<defs>
  <marker id="ah" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><polygon points="0 0, 6 3, 0 6" fill="#38bdf8" /></marker>
  <marker id="ag" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><polygon points="0 0, 6 3, 0 6" fill="#10b981" /></marker>
</defs>
<rect width="880" height="320" class="bg" />
<text x="30" y="32" class="txt-bold" font-size="16">Архітектура шардованого лічильника (Striped Counter)</text>
<text x="30" y="52" class="txt-muted">Розподіл інкрементів по N незалежних комірках усуває блокування ексклюзивного рядка</text>

<!-- Клієнтські потоки запису -->
<g transform="translate(30, 80)">
  <rect width="140" height="40" class="panel" stroke="#38bdf8" />
  <text x="15" y="25" class="txt-bold" fill="#38bdf8">Клієнт 1 (+1)</text>

  <rect y="60" width="140" height="40" class="panel" stroke="#38bdf8" />
  <text x="15" y="85" class="txt-bold" fill="#38bdf8">Клієнт 2 (+1)</text>

  <rect y="120" width="140" height="40" class="panel" stroke="#38bdf8" />
  <text x="15" y="145" class="txt-bold" fill="#38bdf8">Клієнт 3 (+1)</text>

  <rect y="180" width="140" height="40" class="panel" stroke="#38bdf8" />
  <text x="15" y="205" class="txt-bold" fill="#38bdf8">Клієнт K (+1)</text>
</g>

<!-- Стрілки вибору слота -->
<path d="M 170 100 L 250 100" class="arrow" />
<path d="M 170 160 L 250 140" class="arrow" />
<path d="M 170 220 L 250 180" class="arrow" />
<path d="M 170 280 L 250 220" class="arrow" />

<text x="180" y="85" class="txt-muted">hash(tid) % N</text>

<!-- Шарди лічильника в таблиці / пам'яті -->
<g transform="translate(255, 75)">
  <rect width="320" height="225" class="panel" stroke="#3b82f6" />
  <text x="15" y="25" class="txt-bold" fill="#60a5fa">Шарди лічильника (N слотів без спільних блокувань)</text>

  <rect x="15" y="38" width="290" height="38" class="slot" />
  <text x="25" y="62" class="txt-mono">Слот #0: val = 14,208  [Рядок / Шард 0]</text>

  <rect x="15" y="82" width="290" height="38" class="slot" />
  <text x="25" y="106" class="txt-mono">Слот #1: val = 14,195  [Рядок / Шард 1]</text>

  <rect x="15" y="126" width="290" height="38" class="slot" />
  <text x="25" y="150" class="txt-mono">Слот #2: val = 14,212  [Рядок / Шард 2]</text>

  <rect x="15" y="170" width="290" height="38" class="slot" />
  <text x="25" y="194" class="txt-mono">Слот #3: val = 14,201  [Рядок / Шард 3]</text>
</g>

<!-- Стрілка об'єднання -->
<path d="M 575 185 L 635 185" class="arrow-sum" />
<text x="582" y="175" class="txt-bold" fill="#34d399">SUM()</text>

<!-- Фінальне читання -->
<g transform="translate(640, 130)">
  <rect width="210" height="110" class="panel" stroke="#10b981" />
  <text x="15" y="28" class="txt-bold" fill="#34d399">Операція читання</text>
  <text x="15" y="55" class="txt-mono">SELECT SUM(val)</text>
  <text x="15" y="75" class="txt-mono">FROM counter_shards</text>
  <text x="15" y="98" class="txt-bold" fill="#f8fafc">Разом: 56,816</text>
</g>
</svg>"""

with open(f"{img_dir}/sequence-contention-gap.svg", "w", encoding="utf-8") as f: f.write(svg1)
with open(f"{img_dir}/snowflake-bit-layout.svg", "w", encoding="utf-8") as f: f.write(svg2)
with open(f"{img_dir}/btree-locality-uuid4-vs-uuid7.svg", "w", encoding="utf-8") as f: f.write(svg3)
with open(f"{img_dir}/sharded-counter-striping.svg", "w", encoding="utf-8") as f: f.write(svg4)

print("Generated 4 SVG diagrams in sequences-counters/img/")

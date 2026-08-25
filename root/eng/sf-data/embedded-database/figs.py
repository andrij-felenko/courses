import os

os.makedirs("root/eng/sf-data/embedded-database/img", exist_ok=True)

# 1. in-process-vs-client-server.svg
svg1 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 380" width="100%" height="100%">
<style>
  .bg { fill: #0b0f19; rx: 12px; }
  .panel-srv { fill: #111827; stroke: #ef4444; stroke-width: 1.5; stroke-dasharray: 4 4; rx: 8px; }
  .panel-emb { fill: #111827; stroke: #10b981; stroke-width: 1.5; rx: 8px; }
  .box { fill: #1e293b; stroke: #3b82f6; stroke-width: 1.5; rx: 6px; }
  .box-proc { fill: #1e293b; stroke: #64748b; stroke-width: 1.5; rx: 6px; }
  .box-ipc { fill: #271e3b; stroke: #a855f7; stroke-width: 1.5; rx: 6px; }
  .box-green { fill: #064e3b; stroke: #10b981; stroke-width: 1.5; rx: 6px; }
  .txt { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; }
  .txt-bold { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 13px; font-weight: bold; }
  .txt-title { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 15px; font-weight: bold; }
  .txt-muted { fill: #94a3b8; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 11px; }
  .arrow { stroke: #38bdf8; stroke-width: 1.5; fill: none; marker-end: url(#arr); }
  .arrow-ipc { stroke: #c084fc; stroke-width: 1.5; fill: none; marker-end: url(#arr-p); }
  .arrow-fast { stroke: #34d399; stroke-width: 2; fill: none; marker-end: url(#arr-g); }
</style>
<defs>
  <marker id="arr" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#38bdf8" /></marker>
  <marker id="arr-p" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#c084fc" /></marker>
  <marker id="arr-g" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#34d399" /></marker>
</defs>
<rect width="880" height="380" class="bg" />
<text x="30" y="32" class="txt-title">Архітектурна межа: Клієнт-серверна СУБД проти Вбудованої СУБД</text>
<text x="30" y="52" class="txt-muted">Порівняння шляху виконання запиту: системні виклики та серіалізація проти прямих викликів ABI</text>

<!-- Left: Client-Server -->
<g transform="translate(30, 70)">
  <rect width="390" height="285" class="panel-srv" />
  <text x="15" y="25" class="txt-bold" fill="#f87171">Клієнт-серверна модель (TCP / Unix Domain Socket)</text>
  
  <!-- Client Process -->
  <rect x="15" y="40" width="160" height="100" class="box-proc" />
  <text x="25" y="60" class="txt-bold" fill="#60a5fa">Процес клієнта</text>
  <text x="25" y="80" class="txt">Код застосунку</text>
  <text x="25" y="100" class="txt">Драйвер / ORM</text>
  <text x="25" y="125" class="txt-muted">Серіалізація DTO</text>

  <!-- Server Process -->
  <rect x="215" y="40" width="160" height="100" class="box-proc" />
  <text x="225" y="60" class="txt-bold" fill="#f87171">Процес СУБД</text>
  <text x="225" y="80" class="txt">Парсер / Планувальник</text>
  <text x="225" y="100" class="txt">Буферний пул (RAM)</text>
  <text x="225" y="125" class="txt-muted">Десеріалізація рядків</text>

  <!-- IPC Middle Layer -->
  <rect x="15" y="160" width="360" height="55" class="box-ipc" />
  <text x="25" y="180" class="txt-bold" fill="#c084fc">Міжпроцесна взаємодія (IPC / Сокетний рівень ядра)</text>
  <text x="25" y="200" class="txt-muted">Системні виклики send/recv, перемикання контексту, копіювання буферів сокета</text>

  <!-- Flow arrows -->
  <path d="M 95 140 L 95 160" class="arrow-ipc" />
  <path d="M 295 160 L 295 140" class="arrow-ipc" />

  <!-- Bottom Metric -->
  <rect x="15" y="230" width="360" height="40" fill="#1f1523" stroke="#ef4444" stroke-width="1" rx="4" />
  <text x="25" y="255" class="txt-bold" fill="#fca5a5">Затримка: 50–2000 мкс (90% часу витрачається на IPC/мережу)</text>
</g>

<!-- Right: Embedded -->
<g transform="translate(460, 70)">
  <rect width="390" height="285" class="panel-emb" />
  <text x="15" y="25" class="txt-bold" fill="#34d399">Вбудована модель (Прямий ABI виклик у спільному heap)</text>
  
  <!-- Host Application Memory Space -->
  <rect x="15" y="40" width="360" height="175" class="box-green" />
  <text x="25" y="60" class="txt-bold" fill="#34d399">Єдиний адресний простір процесу застосунку</text>
  
  <rect x="25" y="75" width="150" height="85" class="box" />
  <text x="35" y="95" class="txt-bold" fill="#60a5fa">Логіка застосунку</text>
  <text x="35" y="115" class="txt">Виклик функції C/C++</text>
  <text x="35" y="135" class="txt">Прямий покажчик</text>

  <rect x="215" y="75" width="150" height="85" class="box" stroke="#10b981" />
  <text x="225" y="95" class="txt-bold" fill="#34d399">Рушій СУБД (lib)</text>
  <text x="225" y="115" class="txt">SQLite / DuckDB</text>
  <text x="225" y="135" class="txt">Buffer Pool / Chunks</text>

  <!-- In-process arrow -->
  <path d="M 175 117 L 215 117" class="arrow-fast" />

  <text x="25" y="185" class="txt-bold" fill="#f8fafc">Zero-Copy доступ:</text>
  <text x="145" y="185" class="txt-muted">читання комірок пам'яті за прямими адресами</text>
  <text x="25" y="202" class="txt-muted">Без сокетів, без копіювання ОС, без десеріалізації</text>

  <!-- Bottom Metric -->
  <rect x="15" y="230" width="360" height="40" fill="#063828" stroke="#10b981" stroke-width="1" rx="4" />
  <text x="25" y="255" class="txt-bold" fill="#6ee7b7">Затримка: 5–25 нс (виклик функції через регістри CPU)</text>
</g>
</svg>"""

# 2. sqlite-wal-concurrency.svg
svg2 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 370" width="100%" height="100%">
<style>
  .bg { fill: #0b0f19; rx: 12px; }
  .box { fill: #1e293b; stroke: #3b82f6; stroke-width: 1.5; rx: 6px; }
  .box-disk { fill: #0f172a; stroke: #10b981; stroke-width: 1.5; rx: 6px; }
  .box-shm { fill: #2d1f3d; stroke: #c084fc; stroke-width: 1.5; rx: 6px; }
  .box-wal { fill: #182822; stroke: #34d399; stroke-width: 1.5; rx: 6px; }
  .txt { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; }
  .txt-bold { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 13px; font-weight: bold; }
  .txt-title { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 15px; font-weight: bold; }
  .txt-muted { fill: #94a3b8; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 11px; }
  .arrow { stroke: #38bdf8; stroke-width: 1.5; fill: none; marker-end: url(#arr2); }
  .arrow-green { stroke: #34d399; stroke-width: 1.5; fill: none; marker-end: url(#arr2-g); }
  .arrow-purple { stroke: #c084fc; stroke-width: 1.5; fill: none; marker-end: url(#arr2-p); }
</style>
<defs>
  <marker id="arr2" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#38bdf8" /></marker>
  <marker id="arr2-g" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#34d399" /></marker>
  <marker id="arr2-p" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#c084fc" /></marker>
</defs>
<rect width="880" height="370" class="bg" />
<text x="30" y="32" class="txt-title">Конкурентний доступ у SQLite через WAL та індекс спільної пам'яті (.shm)</text>
<text x="30" y="52" class="txt-muted">Паралельні читачі читають фіксований знімок без блокування запису; єдиний записувач додає кадри в лог</text>

<!-- Top layer: Threads / Connections -->
<g transform="translate(40, 75)">
  <rect x="0" y="0" width="220" height="75" class="box" />
  <text x="15" y="25" class="txt-bold" fill="#60a5fa">Потоки-читачі (Readers 1..N)</text>
  <text x="15" y="45" class="txt">sqlite3_step(SELECT)</text>
  <text x="15" y="63" class="txt-muted">Фіксують Read Mark у заголовку .shm</text>

  <rect x="300" y="0" width="220" height="75" class="box-shm" />
  <text x="15" y="25" class="txt-bold" fill="#c084fc">Спільна пам'ять (.db-shm)</text>
  <text x="15" y="45" class="txt">Індекс хеш-таблиці кадрів WAL</text>
  <text x="15" y="63" class="txt-muted">Відображення mmap() між процесами</text>

  <rect x="580" y="0" width="220" height="75" class="box" stroke="#f59e0b" />
  <text x="15" y="25" class="txt-bold" fill="#fbbf24">Потік-записувач (Single Writer)</text>
  <text x="15" y="45" class="txt">sqlite3_step(INSERT/UPDATE)</text>
  <text x="15" y="63" class="txt-muted">Бере ексклюзивне блокування WAL</text>
</g>

<!-- Middle connections -->
<path d="M 150 150 L 150 200" class="arrow" />
<path d="M 260 112 L 300 112" class="arrow-purple" />
<path d="M 690 150 L 690 200" class="arrow-green" />
<path d="M 580 112 L 520 112" class="arrow-purple" />

<!-- Bottom storage layer -->
<g transform="translate(40, 200)">
  <!-- Main DB File -->
  <rect x="0" y="0" width="360" height="130" class="box-disk" />
  <text x="20" y="30" class="txt-bold" fill="#34d399">Головний файл бази даних (.db)</text>
  <text x="20" y="55" class="txt">Структура B-Tree зі сторінками 4096 байтів</text>
  <text x="20" y="78" class="txt">Містить стабільний стан на момент чекпойнта</text>
  <text x="20" y="105" class="txt-muted">Читачі звертаються сюди, якщо сторінки нема у WAL</text>

  <!-- WAL File -->
  <rect x="440" y="0" width="360" height="130" class="box-wal" />
  <text x="20" y="30" class="txt-bold" fill="#6ee7b7">Журнал WAL (.db-wal)</text>
  <text x="20" y="55" class="txt">Послідовні кадри (Header + Page 4KB)</text>
  <text x="20" y="78" class="txt">Append-Only запис нових транзакцій</text>
  <text x="20" y="105" class="txt-muted">Читачі беруть найсвіжіші версії сторінок</text>
</g>

<!-- Checkpoint arrow -->
<path d="M 480 300 L 400 300" class="arrow-green" />
<text x="380" y="285" class="txt-bold" fill="#34d399">Checkpoint (перенесення сторінок із WAL в .db)</text>
</svg>"""

# 3. duckdb-vector-columnar.svg
svg3 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 350" width="100%" height="100%">
<style>
  .bg { fill: #0b0f19; rx: 12px; }
  .card { fill: #1e293b; stroke: #334155; stroke-width: 1.5; rx: 8px; }
  .col-box { fill: #0f2744; stroke: #38bdf8; stroke-width: 1.5; rx: 4px; }
  .simd-box { fill: #064e3b; stroke: #10b981; stroke-width: 1.5; rx: 4px; }
  .txt { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; }
  .txt-bold { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 13px; font-weight: bold; }
  .txt-title { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 15px; font-weight: bold; }
  .txt-muted { fill: #94a3b8; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 11px; }
  .arrow { stroke: #38bdf8; stroke-width: 1.5; fill: none; marker-end: url(#arr3); }
</style>
<defs>
  <marker id="arr3" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#38bdf8" /></marker>
</defs>
<rect width="880" height="350" class="bg" />
<text x="30" y="32" class="txt-title">Векторизоване стовпцеве виконання DuckDB в оперативній пам'яті</text>
<text x="30" y="52" class="txt-muted">Опрацювання векторів по 2048 значень у кеші L1/L2 процесора з підтримкою інструкцій SIMD</text>

<!-- Left: DataChunk representation -->
<g transform="translate(40, 75)">
  <rect width="360" height="240" class="card" stroke="#3b82f6" />
  <text x="20" y="30" class="txt-bold" fill="#60a5fa">Пакет стовпців DataChunk (2048 рядків)</text>
  
  <rect x="20" y="50" width="95" height="135" class="col-box" />
  <text x="30" y="70" class="txt-bold" fill="#38bdf8">Vector 1</text>
  <text x="30" y="90" class="txt">id: int64</text>
  <text x="30" y="115" class="txt-muted">[1001]</text>
  <text x="30" y="135" class="txt-muted">[1002]</text>
  <text x="30" y="155" class="txt-muted">[ ... ]</text>
  <text x="30" y="175" class="txt-muted">2048 елементів</text>

  <rect x="130" y="50" width="95" height="135" class="col-box" />
  <text x="140" y="70" class="txt-bold" fill="#38bdf8">Vector 2</text>
  <text x="140" y="90" class="txt">price: f64</text>
  <text x="140" y="115" class="txt-muted">[19.99]</text>
  <text x="140" y="135" class="txt-muted">[45.50]</text>
  <text x="140" y="155" class="txt-muted">[ ... ]</text>
  <text x="140" y="175" class="txt-muted">2048 елементів</text>

  <rect x="240" y="50" width="95" height="135" class="col-box" />
  <text x="250" y="70" class="txt-bold" fill="#38bdf8">Vector 3</text>
  <text x="250" y="90" class="txt">qty: int32</text>
  <text x="250" y="115" class="txt-muted">[5]</text>
  <text x="250" y="135" class="txt-muted">[12]</text>
  <text x="250" y="155" class="txt-muted">[ ... ]</text>
  <text x="250" y="175" class="txt-muted">2048 елементів</text>

  <text x="20" y="215" class="txt-muted">Послідовні масиви в RAM: 100% локальність кешу</text>
</g>

<!-- Processing Arrow -->
<path d="M 405 195 L 455 195" class="arrow" />

<!-- Right: Vectorized Execution Engine -->
<g transform="translate(460, 75)">
  <rect width="380" height="240" class="card" stroke="#10b981" />
  <text x="20" y="30" class="txt-bold" fill="#34d399">Векторний конвеєр (Push-Based Execution)</text>
  
  <rect x="20" y="50" width="340" height="60" class="simd-box" />
  <text x="35" y="72" class="txt-bold" fill="#6ee7b7">SIMD фільтрація та агрегація (AVX2 / NEON)</text>
  <text x="35" y="92" class="txt">Векторне обчислення `total = price * qty` за 1 такт CPU</text>

  <rect x="20" y="125" width="340" height="95" class="card" stroke="#475569" />
  <text x="35" y="148" class="txt-bold" fill="#f8fafc">Zero-Copy взаємодія з кодом процесу:</text>
  <text x="35" y="170" class="txt">• Apache Arrow C Data Interface (передача покажчиків)</text>
  <text x="35" y="190" class="txt">• Пряма інтеграція з C++ std::span, Rust, Python Polars</text>
  <text x="35" y="208" class="txt-muted">Без перекопіювання пам'яті та без трансляції типів</text>
</g>
</svg>"""

# 4. rocksdb-lsm-embedded.svg
svg4 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 360" width="100%" height="100%">
<style>
  .bg { fill: #0b0f19; rx: 12px; }
  .mem-panel { fill: #111d2e; stroke: #3b82f6; stroke-width: 1.5; rx: 8px; }
  .disk-panel { fill: #14221c; stroke: #10b981; stroke-width: 1.5; rx: 8px; }
  .box { fill: #1e293b; stroke: #475569; stroke-width: 1.5; rx: 6px; }
  .box-hot { fill: #1e3a5f; stroke: #38bdf8; stroke-width: 1.5; rx: 6px; }
  .box-sst { fill: #0f3325; stroke: #34d399; stroke-width: 1.5; rx: 6px; }
  .txt { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; }
  .txt-bold { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 13px; font-weight: bold; }
  .txt-title { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 15px; font-weight: bold; }
  .txt-muted { fill: #94a3b8; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 11px; }
  .arrow { stroke: #38bdf8; stroke-width: 1.5; fill: none; marker-end: url(#arr4); }
  .arrow-green { stroke: #34d399; stroke-width: 1.5; fill: none; marker-end: url(#arr4-g); }
</style>
<defs>
  <marker id="arr4" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#38bdf8" /></marker>
  <marker id="arr4-g" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#34d399" /></marker>
</defs>
<rect width="880" height="360" class="bg" />
<text x="30" y="32" class="txt-title">Архітектура вбудованого LSM-рушія RocksDB у пам'яті процесу</text>
<text x="30" y="52" class="txt-muted">MemTable у купі процесу застосунку, паралельне фонове скидання (Flush) та ущільнення (Compaction)</text>

<!-- Top Memory space of Host Process -->
<g transform="translate(30, 70)">
  <rect width="820" height="120" class="mem-panel" />
  <text x="20" y="25" class="txt-bold" fill="#60a5fa">Оперативна пам'ять процесу застосунку (Host Heap)</text>
  
  <rect x="20" y="40" width="180" height="65" class="box-hot" />
  <text x="30" y="60" class="txt-bold" fill="#38bdf8">Активний MemTable</text>
  <text x="30" y="78" class="txt">SkipList (без блокувань)</text>
  <text x="30" y="95" class="txt-muted">Гарячий буфер запису</text>

  <rect x="220" y="40" width="180" height="65" class="box" />
  <text x="230" y="60" class="txt-bold" fill="#f8fafc">Immutable MemTables</text>
  <text x="230" y="78" class="txt">Черга на скидання</text>
  <text x="230" y="95" class="txt-muted">Готові для запису на диск</text>

  <rect x="420" y="40" width="200" height="65" class="box" stroke="#c084fc" />
  <text x="430" y="60" class="txt-bold" fill="#c084fc">Block Cache (LRU / 2Q)</text>
  <text x="430" y="78" class="txt">Кеш розпакованих блоків</text>
  <text x="430" y="95" class="txt-muted">Спільний ліміт пам'яті</text>

  <rect x="640" y="40" width="160" height="65" class="box" stroke="#f59e0b" />
  <text x="650" y="60" class="txt-bold" fill="#fbbf24">Потоки процесу</text>
  <text x="650" y="78" class="txt">Flush &amp; Compaction</text>
  <text x="650" y="95" class="txt-muted">Фонові воркери в хості</text>
</g>

<!-- Transition Arrows -->
<path d="M 310 190 L 310 220" class="arrow-green" />
<text x="320" y="210" class="txt-bold" fill="#34d399">Minor Compaction (Flush)</text>

<!-- Bottom Disk space -->
<g transform="translate(30, 225)">
  <rect width="820" height="105" class="disk-panel" />
  <text x="20" y="25" class="txt-bold" fill="#34d399">Дискове сховище (SSTables &amp; WAL)</text>

  <rect x="20" y="40" width="150" height="50" class="box-sst" />
  <text x="30" y="60" class="txt-bold" fill="#6ee7b7">WAL (Послідовний)</text>
  <text x="30" y="78" class="txt-muted">Гарантія ACID Durability</text>

  <rect x="190" y="40" width="180" height="50" class="box-sst" />
  <text x="200" y="60" class="txt-bold" fill="#6ee7b7">Level 0 (Несортовані)</text>
  <text x="200" y="78" class="txt-muted">Прямий зліпок MemTable</text>

  <rect x="390" y="40" width="190" height="50" class="box-sst" />
  <text x="400" y="60" class="txt-bold" fill="#6ee7b7">Level 1 (Сортовані SST)</text>
  <text x="400" y="78" class="txt-muted">Діапазони без перетинів</text>

  <rect x="600" y="40" width="200" height="50" class="box-sst" />
  <text x="610" y="60" class="txt-bold" fill="#6ee7b7">Level 2..N (Масивні SST)</text>
  <text x="610" y="78" class="txt-muted">Фільтри Блума + Індекси</text>
</g>
</svg>"""

out_dir = "root/eng/sf-data/embedded-database/img"
with open(f"{out_dir}/in-process-vs-client-server.svg", "w", encoding="utf-8") as f:
    f.write(svg1)
with open(f"{out_dir}/sqlite-wal-concurrency.svg", "w", encoding="utf-8") as f:
    f.write(svg2)
with open(f"{out_dir}/duckdb-vector-columnar.svg", "w", encoding="utf-8") as f:
    f.write(svg3)
with open(f"{out_dir}/rocksdb-lsm-embedded.svg", "w", encoding="utf-8") as f:
    f.write(svg4)

print("SVGs generated successfully.")

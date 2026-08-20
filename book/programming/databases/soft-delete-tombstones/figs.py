import os
import sys

# Шлях до директорії зображень
IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)

# 1. hard-vs-soft-delete.svg
svg1 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 380" width="100%" height="100%">
<style>
  .bg { fill: #0b0f19; rx: 12px; }
  .panel { fill: #1e293b; stroke: #475569; stroke-width: 1.5; rx: 8px; }
  .panel-del { fill: #1e293b; stroke: #ef4444; stroke-width: 2; rx: 8px; }
  .panel-soft { fill: #1e293b; stroke: #3b82f6; stroke-width: 2; rx: 8px; }
  .hdr-hard { fill: #450a0a; stroke: #ef4444; stroke-width: 1; rx: 6px; }
  .hdr-soft { fill: #172554; stroke: #3b82f6; stroke-width: 1; rx: 6px; }
  .row-live { fill: #064e3b; stroke: #10b981; stroke-width: 1; rx: 4px; }
  .row-dead { fill: #7f1d1d; stroke: #ef4444; stroke-width: 1; stroke-dasharray: 4; rx: 4px; }
  .row-tomb { fill: #312e81; stroke: #818cf8; stroke-width: 1; rx: 4px; }
  .txt { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 13px; }
  .txt-bold { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 14px; font-weight: bold; }
  .txt-title { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 16px; font-weight: bold; }
  .txt-muted { fill: #94a3b8; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; }
  .txt-danger { fill: #f87171; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; font-weight: bold; }
  .txt-success { fill: #34d399; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; font-weight: bold; }
  .txt-info { fill: #60a5fa; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; font-weight: bold; }
  .arrow { stroke: #94a3b8; stroke-width: 1.8; fill: none; marker-end: url(#arrow); }
  .arrow-broken { stroke: #ef4444; stroke-width: 1.8; stroke-dasharray: 4; fill: none; marker-end: url(#arrow-red); }
</style>
<defs>
  <marker id="arrow" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="#94a3b8" />
  </marker>
  <marker id="arrow-red" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="#ef4444" />
  </marker>
</defs>
<rect width="920" height="380" class="bg" />
<text x="30" y="32" class="txt-title">Фізичні наслідки: Жорстке видалення (Hard Delete) проти М'якого (Soft Delete)</text>
<text x="30" y="52" class="txt-muted">Вплив на сторінки диска, цілісність реляційних зв'язків (Foreign Keys) та стан індексів</text>

<!-- Ліва колонка: Hard Delete -->
<g transform="translate(30, 75)">
  <rect width="415" height="280" class="panel-del" />
  <rect x="10" y="10" width="395" height="32" class="hdr-hard" />
  <text x="20" y="31" class="txt-bold" fill="#f87171">Жорстке видалення (DELETE FROM users)</text>
  
  <text x="20" y="65" class="txt-bold">Сторінка даних таблиці users (Page #42):</text>
  <rect x="20" y="75" width="375" height="30" class="row-live" />
  <text x="30" y="95" class="txt">Row #1: id=1, name='Alice' [Живий]</text>
  
  <rect x="20" y="112" width="375" height="30" class="row-dead" />
  <text x="30" y="132" class="txt-danger">Row #2: [Вивільнений слот / Діра в пам'яті]</text>
  
  <text x="20" y="165" class="txt-bold">Зовнішні зв'язки в таблиці orders:</text>
  <rect x="20" y="175" width="375" height="42" class="panel" />
  <text x="30" y="193" class="txt">Order #801: user_id=2, amount=$150</text>
  <text x="30" y="210" class="txt-danger">Порушення зв'язку: user_id=2 більше не існує!</text>
  
  <text x="20" y="242" class="txt-danger">✗ Втрата аудиторського сліду та історії операцій</text>
  <text x="20" y="260" class="txt-danger">✗ Потреба в ON DELETE CASCADE або помилка FK</text>
</g>

<!-- Права колонка: Soft Delete -->
<g transform="translate(475, 75)">
  <rect width="415" height="280" class="panel-soft" />
  <rect x="10" y="10" width="395" height="32" class="hdr-soft" />
  <text x="20" y="31" class="txt-bold" fill="#60a5fa">М'яке видалення (UPDATE users SET deleted_at=...)</text>
  
  <text x="20" y="65" class="txt-bold">Сторінка даних таблиці users (Page #42):</text>
  <rect x="20" y="75" width="375" height="30" class="row-live" />
  <text x="30" y="95" class="txt">Row #1: id=1, name='Alice', deleted_at=NULL</text>
  
  <rect x="20" y="112" width="375" height="30" class="row-tomb" />
  <text x="30" y="132" class="txt-info">Row #2: id=2, name='Bob', deleted_at=1724179200</text>
  
  <text x="20" y="165" class="txt-bold">Зовнішні зв'язки в таблиці orders:</text>
  <rect x="20" y="175" width="375" height="42" class="panel" />
  <text x="30" y="193" class="txt">Order #801: user_id=2, amount=$150</text>
  <text x="30" y="210" class="txt-success">✓ Цілісність збережена: user_id=2 фізично на місці</text>
  
  <text x="20" y="242" class="txt-success">✓ Можливість миттєвого відновлення (Undo)</text>
  <text x="20" y="260" class="txt-danger">⚠ Забруднення індексів та вимога фільтрації запитів</text>
</g>
</svg>"""

# 2. lsm-tombstone-lifecycle.svg
svg2 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 420" width="100%" height="100%">
<style>
  .bg { fill: #0b0f19; rx: 12px; }
  .box-mem { fill: #1e1b4b; stroke: #6366f1; stroke-width: 1.8; rx: 8px; }
  .box-l0 { fill: #172554; stroke: #3b82f6; stroke-width: 1.8; rx: 8px; }
  .box-l1 { fill: #0f172a; stroke: #64748b; stroke-width: 1.5; rx: 8px; }
  .box-tomb { fill: #450a0a; stroke: #ef4444; stroke-width: 1.5; rx: 6px; }
  .box-data { fill: #064e3b; stroke: #10b981; stroke-width: 1.5; rx: 6px; }
  .txt { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 13px; }
  .txt-bold { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 14px; font-weight: bold; }
  .txt-title { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 16px; font-weight: bold; }
  .txt-muted { fill: #94a3b8; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; }
  .txt-danger { fill: #f87171; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; font-weight: bold; }
  .txt-success { fill: #34d399; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; font-weight: bold; }
  .txt-info { fill: #818cf8; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; font-weight: bold; }
  .arrow-flow { stroke: #38bdf8; stroke-width: 2; fill: none; marker-end: url(#arrow-flow-head); }
  .arrow-compact { stroke: #f59e0b; stroke-width: 2; stroke-dasharray: 4; fill: none; marker-end: url(#arrow-compact-head); }
</style>
<defs>
  <marker id="arrow-flow-head" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="#38bdf8" />
  </marker>
  <marker id="arrow-compact-head" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="#f59e0b" />
  </marker>
</defs>
<rect width="940" height="420" class="bg" />
<text x="30" y="32" class="txt-title">Життєвий цикл надгробка (Tombstone) у деревах LSM (Log-Structured Merge)</text>
<text x="30" y="52" class="txt-muted">Від запису в оперативну пам'ять (MemTable) до злиття SSTable (Compaction) та фізичного видалення</text>

<!-- 1. Операція DELETE -->
<g transform="translate(30, 75)">
  <rect width="260" height="135" class="box-mem" />
  <text x="15" y="25" class="txt-bold" fill="#818cf8">1. Клієнт: DELETE("user:42")</text>
  <text x="15" y="45" class="txt">Запис у MemTable (RAM):</text>
  <rect x="15" y="55" width="230" height="32" class="box-tomb" />
  <text x="25" y="76" class="txt-danger">Key: "user:42" | TOMBSTONE (t=20)</text>
  <text x="15" y="105" class="txt-muted">Видалення — це звичайний append!</text>
  <text x="15" y="122" class="txt-muted">Старі дані на диску не чіпаються.</text>
</g>

<!-- Стрілка Flush -->
<path d="M 290 140 L 340 140" class="arrow-flow" />
<text x="295" y="130" class="txt-muted">Flush</text>

<!-- 2. Flush у SSTable L0 -->
<g transform="translate(345, 75)">
  <rect width="260" height="135" class="box-l0" />
  <text x="15" y="25" class="txt-bold" fill="#60a5fa">2. SSTable на диску (Level 0)</text>
  <text x="15" y="45" class="txt">Незмінний файл SSTable #105:</text>
  <rect x="15" y="55" width="230" height="32" class="box-tomb" />
  <text x="25" y="76" class="txt-danger">"user:42" → [TOMBSTONE, t=20]</text>
  <text x="15" y="105" class="txt">Читання: надгробок маскує старі дані.</text>
  <text x="15" y="122" class="txt-muted">Запит повертає NotFound.</text>
</g>

<!-- Стрілка Compaction -->
<path d="M 605 140 L 655 140" class="arrow-compact" />
<text x="610" y="130" class="txt-muted">Merge</text>

<!-- 3. Старий рівень Level 1/2 -->
<g transform="translate(660, 75)">
  <rect width="250" height="135" class="box-l1" />
  <text x="15" y="25" class="txt-bold" fill="#94a3b8">3. SSTable на диску (Level 1)</text>
  <text x="15" y="45" class="txt">Старий файл SSTable #88:</text>
  <rect x="15" y="55" width="220" height="32" class="box-data" />
  <text x="25" y="76" class="txt-success">"user:42" → {"name": "Bob"} (t=10)</text>
  <text x="15" y="105" class="txt-danger">Стара версія все ще на диску!</text>
  <text x="15" y="122" class="txt-muted">Чекає на фонове злиття.</text>
</g>

<!-- Нижня панель: Ущільнення та очищення -->
<g transform="translate(30, 235)">
  <rect width="880" height="165" class="panel" fill="#0f172a" stroke="#f59e0b" stroke-width="1.8" />
  <text x="20" y="30" class="txt-bold" fill="#fbbf24">4. Процес злиття (Compaction) та остаточне знищення надгробка (GC)</text>
  
  <rect x="20" y="45" width="380" height="105" class="panel" />
  <text x="35" y="70" class="txt-bold">Ущільнення (Compaction Phase):</text>
  <text x="35" y="90" class="txt">Рушій читає паралельно SSTable #105 та #88.</text>
  <text x="35" y="110" class="txt">Оскільки t=20 &gt; t=10, надгробок поглинає дані.</text>
  <text x="35" y="130" class="txt-success">Старий запис Bob (t=10) фізично відкидається.</text>
  
  <rect x="420" y="45" width="440" height="105" class="panel" />
  <text x="435" y="70" class="txt-bold">Коли можна видалити сам надгробок?</text>
  <text x="435" y="90" class="txt-danger">Тільки коли надгробок досяг найглибшого рівня (L_max),</text>
  <text x="435" y="108" class="txt-danger">АБО коли вичерпано gc_grace_seconds (Cassandra)!</text>
  <text x="435" y="132" class="txt-muted">Передчасне видалення надгробка призведе до "воскресіння" старих даних.</text>
</g>
</svg>"""

# 3. unique-index-trap.svg
svg3 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 360" width="100%" height="100%">
<style>
  .bg { fill: #0b0f19; rx: 12px; }
  .panel-bad { fill: #1e293b; stroke: #ef4444; stroke-width: 1.8; rx: 8px; }
  .panel-good { fill: #1e293b; stroke: #10b981; stroke-width: 1.8; rx: 8px; }
  .hdr-bad { fill: #450a0a; stroke: #ef4444; stroke-width: 1; rx: 6px; }
  .hdr-good { fill: #064e3b; stroke: #10b981; stroke-width: 1; rx: 6px; }
  .node { fill: #334155; stroke: #64748b; stroke-width: 1.2; rx: 4px; }
  .node-bad { fill: #7f1d1d; stroke: #ef4444; stroke-width: 1.5; rx: 4px; }
  .node-good { fill: #065f46; stroke: #34d399; stroke-width: 1.5; rx: 4px; }
  .txt { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 13px; }
  .txt-bold { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 14px; font-weight: bold; }
  .txt-title { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 16px; font-weight: bold; }
  .txt-muted { fill: #94a3b8; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; }
  .txt-danger { fill: #f87171; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; font-weight: bold; }
  .txt-success { fill: #34d399; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; font-weight: bold; }
</style>
<rect width="920" height="360" class="bg" />
<text x="30" y="32" class="txt-title">Пастка унікальних індексів (Unique Constraint Trap) та рішення через часткові індекси</text>
<text x="30" y="52" class="txt-muted">Конфлікт повторної реєстрації видаленого користувача з тим самим email у B-Tree</text>

<!-- Ліва колонка: Проблема зі звичайним UNIQUE -->
<g transform="translate(30, 75)">
  <rect width="415" height="260" class="panel-bad" />
  <rect x="10" y="10" width="395" height="32" class="hdr-bad" />
  <text x="20" y="31" class="txt-bold" fill="#f87171">Звичайний індекс: CREATE UNIQUE INDEX (email)</text>
  
  <text x="20" y="65" class="txt-bold">Вміст B-Tree індексу:</text>
  <rect x="20" y="75" width="375" height="32" class="node" />
  <text x="30" y="96" class="txt">Key: 'alice@ex.com' → Ptr: Row #1 (Живий)</text>
  
  <rect x="20" y="115" width="375" height="32" class="node-bad" />
  <text x="30" y="136" class="txt-danger">Key: 'bob@ex.com' → Ptr: Row #2 (М'яко видалений!)</text>
  
  <text x="20" y="170" class="txt-bold">Нова операція:</text>
  <text x="20" y="190" class="txt">INSERT INTO users (email) VALUES ('bob@ex.com')</text>
  
  <rect x="20" y="202" width="375" height="42" fill="#450a0a" stroke="#ef4444" stroke-width="1" rx="4" />
  <text x="30" y="220" class="txt-danger">💥 ERROR: duplicate key value violates unique constraint</text>
  <text x="30" y="236" class="txt-muted">Індекс не знає, що Row #2 позначено як deleted_at!</text>
</g>

<!-- Права колонка: Рішення через Partial Index -->
<g transform="translate(475, 75)">
  <rect width="415" height="260" class="panel-good" />
  <rect x="10" y="10" width="395" height="32" class="hdr-good" />
  <text x="20" y="31" class="txt-bold" fill="#34d399">Частковий індекс: ... WHERE deleted_at IS NULL</text>
  
  <text x="20" y="65" class="txt-bold">Вміст B-Tree індексу (Тільки активні!):</text>
  <rect x="20" y="75" width="375" height="32" class="node" />
  <text x="30" y="96" class="txt">Key: 'alice@ex.com' → Ptr: Row #1 (Живий)</text>
  
  <rect x="20" y="115" width="375" height="32" class="node-good" />
  <text x="30" y="136" class="txt-success">М'яко видалений Row #2 взагалі НЕ потрапляє в індекс!</text>
  
  <text x="20" y="170" class="txt-bold">Нова операція:</text>
  <text x="20" y="190" class="txt">INSERT INTO users (email) VALUES ('bob@ex.com')</text>
  
  <rect x="20" y="202" width="375" height="42" fill="#064e3b" stroke="#10b981" stroke-width="1" rx="4" />
  <text x="30" y="220" class="txt-success">✓ SUCCESS: Новий запис успішно додано до B-Tree</text>
  <text x="30" y="236" class="txt-muted">Індекс менший на 30-70% і не блокує повторні реєстрації</text>
</g>
</svg>"""

# 4. purge-pipeline-lifecycle.svg
svg4 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 370" width="100%" height="100%">
<style>
  .bg { fill: #0b0f19; rx: 12px; }
  .step-box { fill: #1e293b; stroke: #475569; stroke-width: 1.5; rx: 8px; }
  .step-hdr { fill: #0f172a; stroke: #64748b; stroke-width: 1; rx: 6px; }
  .txt { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 13px; }
  .txt-bold { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 14px; font-weight: bold; }
  .txt-title { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 16px; font-weight: bold; }
  .txt-muted { fill: #94a3b8; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; }
  .txt-danger { fill: #f87171; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; font-weight: bold; }
  .txt-success { fill: #34d399; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; font-weight: bold; }
  .txt-info { fill: #60a5fa; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; font-weight: bold; }
  .txt-amber { fill: #fbbf24; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; font-weight: bold; }
  .arrow { stroke: #38bdf8; stroke-width: 2; fill: none; marker-end: url(#arrow-p); }
</style>
<defs>
  <marker id="arrow-p" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="#38bdf8" />
  </marker>
</defs>
<rect width="940" height="370" class="bg" />
<text x="30" y="32" class="txt-title">Чотириетапний конвеєр життєвого циклу даних (Data Purge Pipeline)</text>
<text x="30" y="52" class="txt-muted">Безпечний перехід від активного стану до фізичного вивільнення сторінок без блокування бази</text>

<!-- Етап 1: Active -->
<g transform="translate(30, 80)">
  <rect width="200" height="250" class="step-box" stroke="#10b981" />
  <rect x="8" y="8" width="184" height="30" class="step-hdr" fill="#064e3b" />
  <text x="18" y="28" class="txt-bold" fill="#34d399">1. Живий (Active)</text>
  <text x="15" y="60" class="txt-bold">Стан рядка:</text>
  <text x="15" y="78" class="txt">deleted_at IS NULL</text>
  <text x="15" y="96" class="txt">status = 'ACTIVE'</text>
  <text x="15" y="130" class="txt-bold">Доступність:</text>
  <text x="15" y="150" class="txt">Повний доступ для</text>
  <text x="15" y="168" class="txt">клієнтів та API.</text>
  <text x="15" y="200" class="txt-bold">Індексація:</text>
  <text x="15" y="220" class="txt-success">Присутній у B-Tree</text>
</g>

<path d="M 235 205 L 260 205" class="arrow" />

<!-- Етап 2: Soft Deleted / Retention -->
<g transform="translate(265, 80)">
  <rect width="200" height="250" class="step-box" stroke="#3b82f6" />
  <rect x="8" y="8" width="184" height="30" class="step-hdr" fill="#1e3a8a" />
  <text x="18" y="28" class="txt-bold" fill="#60a5fa">2. М'яко видалений</text>
  <text x="15" y="60" class="txt-bold">Стан рядка:</text>
  <text x="15" y="78" class="txt">deleted_at = NOW()</text>
  <text x="15" y="96" class="txt">Grace Period (30 днів)</text>
  <text x="15" y="130" class="txt-bold">Видимість:</text>
  <text x="15" y="150" class="txt">Прихований через RLS/</text>
  <text x="15" y="168" class="txt">фільтри ORM.</text>
  <text x="15" y="200" class="txt-bold">Можливість:</text>
  <text x="15" y="220" class="txt-info">Миттєвий UNDO</text>
</g>

<path d="M 470 205 L 495 205" class="arrow" />

<!-- Етап 3: Batch Hard Purge -->
<g transform="translate(500, 80)">
  <rect width="200" height="250" class="step-box" stroke="#f59e0b" />
  <rect x="8" y="8" width="184" height="30" class="step-hdr" fill="#78350f" />
  <text x="18" y="28" class="txt-bold" fill="#fbbf24">3. Батчеве очищення</text>
  <text x="15" y="60" class="txt-bold">Фоновий Purger:</text>
  <text x="15" y="78" class="txt">deleted_at &lt; cutoff</text>
  <text x="15" y="96" class="txt">Порціями по 5000 рядків</text>
  <text x="15" y="130" class="txt-bold">Запобігання аваріям:</text>
  <text x="15" y="150" class="txt">Ніякого Lock Escalation,</text>
  <text x="15" y="168" class="txt">контрольований WAL.</text>
  <text x="15" y="200" class="txt-bold">Результат:</text>
  <text x="15" y="220" class="txt-amber">Hard DELETE з таблиці</text>
</g>

<path d="M 705 205 L 730 205" class="arrow" />

<!-- Етап 4: Physical Reclamation -->
<g transform="translate(735, 80)">
  <rect width="180" height="250" class="step-box" stroke="#ef4444" />
  <rect x="8" y="8" width="164" height="30" class="step-hdr" fill="#450a0a" />
  <text x="18" y="28" class="txt-bold" fill="#f87171">4. Рекультивація</text>
  <text x="15" y="60" class="txt-bold">Фізичний рівень:</text>
  <text x="15" y="78" class="txt">Postgres VACUUM</text>
  <text x="15" y="96" class="txt">InnoDB Page Merge</text>
  <text x="15" y="114" class="txt">LSM Compaction</text>
  <text x="15" y="145" class="txt-bold">Крипто-стирання:</text>
  <text x="15" y="165" class="txt">Знищення ключів DEK</text>
  <text x="15" y="183" class="txt">для GDPR Art. 17.</text>
  <text x="15" y="210" class="txt-bold">Результат:</text>
  <text x="15" y="228" class="txt-danger">Повне вивільнення</text>
</g>
</svg>"""

files = {
    "hard-vs-soft-delete.svg": svg1,
    "lsm-tombstone-lifecycle.svg": svg2,
    "unique-index-trap.svg": svg3,
    "purge-pipeline-lifecycle.svg": svg4,
}

for name, content in files.items():
    p = os.path.join(IMG_DIR, name)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Generated: {p}")

"""Generate technical SVG diagrams for Database Migrations."""
import os
import sys

# Add scripts/ to python path for svgkit if available
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../scripts")))
try:
    import svgkit
except ImportError:
    pass

def generate_expand_contract():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 380" width="100%" height="100%">
  <style>
    .bg { fill: #0d1117; }
    .box { fill: #161b22; stroke: #30363d; stroke-width: 1.5; rx: 6px; }
    .box-active { fill: #1f2937; stroke: #58a6ff; stroke-width: 2; rx: 6px; }
    .box-old { fill: #161b22; stroke: #f85149; stroke-width: 1.5; stroke-dasharray: 4,4; rx: 6px; }
    .text-title { fill: #58a6ff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 14px; }
    .text-body { fill: #c9d1d9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 12px; }
    .text-accent { fill: #3fb950; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 12px; }
    .text-warn { fill: #d29922; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 12px; }
    .text-del { fill: #f85149; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 12px; }
    .arrow { stroke: #8b949e; stroke-width: 1.5; fill: none; marker-end: url(#arrowhead); }
    .step-badge { fill: #238636; font-family: monospace; font-size: 11px; font-weight: bold; }
  </style>
  <defs>
    <marker id="arrowhead" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="#8b949e"/>
    </marker>
  </defs>

  <rect width="100%" height="100%" class="bg"/>

  <!-- Step 1: Expand -->
  <g transform="translate(30, 40)">
    <rect width="160" height="280" class="box"/>
    <text x="80" y="25" text-anchor="middle" class="text-title">1. EXPAND</text>
    <rect x="15" y="45" width="130" height="45" class="box-active"/>
    <text x="80" y="65" text-anchor="middle" class="text-body">Схема БД</text>
    <text x="80" y="80" text-anchor="middle" class="text-accent">+ нова колонка</text>
    <rect x="15" y="105" width="130" height="45" class="box"/>
    <text x="80" y="125" text-anchor="middle" class="text-body">Додаток (Старий)</text>
    <text x="80" y="140" text-anchor="middle" class="text-warn">читає/пише v1</text>
    <text x="80" y="190" text-anchor="middle" class="text-body" fill="#8b949e">Зворотна сумісність</text>
    <text x="80" y="210" text-anchor="middle" class="text-body" fill="#8b949e">гарантована</text>
  </g>

  <line x1="200" y1="180" x2="220" y2="180" class="arrow"/>

  <!-- Step 2: Write Both -->
  <g transform="translate(225, 40)">
    <rect width="160" height="280" class="box"/>
    <text x="80" y="25" text-anchor="middle" class="text-title">2. WRITE BOTH</text>
    <rect x="15" y="45" width="130" height="45" class="box-active"/>
    <text x="80" y="65" text-anchor="middle" class="text-body">Схема БД</text>
    <text x="80" y="80" text-anchor="middle" class="text-accent">v1 + v2 паралельно</text>
    <rect x="15" y="105" width="130" height="45" class="box-active"/>
    <text x="80" y="125" text-anchor="middle" class="text-body">Додаток (Новий)</text>
    <text x="80" y="140" text-anchor="middle" class="text-accent">двійний запис (Dual)</text>
    <text x="80" y="190" text-anchor="middle" class="text-body" fill="#8b949e">Фоновий бекфіл</text>
    <text x="80" y="210" text-anchor="middle" class="text-body" fill="#8b949e">старих даних</text>
  </g>

  <line x1="395" y1="180" x2="415" y2="180" class="arrow"/>

  <!-- Step 3: Read New -->
  <g transform="translate(420, 40)">
    <rect width="160" height="280" class="box"/>
    <text x="80" y="25" text-anchor="middle" class="text-title">3. READ NEW</text>
    <rect x="15" y="45" width="130" height="45" class="box-active"/>
    <text x="80" y="65" text-anchor="middle" class="text-body">Схема БД</text>
    <text x="80" y="80" text-anchor="middle" class="text-accent">дані синхронізовані</text>
    <rect x="15" y="105" width="130" height="45" class="box-active"/>
    <text x="80" y="125" text-anchor="middle" class="text-body">Додаток (Новий)</text>
    <text x="80" y="140" text-anchor="middle" class="text-accent">читає/пише v2</text>
    <text x="80" y="190" text-anchor="middle" class="text-body" fill="#8b949e">Стара колонка</text>
    <text x="80" y="210" text-anchor="middle" class="text-warn">більше не читається</text>
  </g>

  <line x1="590" y1="180" x2="610" y2="180" class="arrow"/>

  <!-- Step 4: Contract -->
  <g transform="translate(615, 40)">
    <rect width="160" height="280" class="box"/>
    <text x="80" y="25" text-anchor="middle" class="text-title">4. CONTRACT</text>
    <rect x="15" y="45" width="130" height="45" class="box-old"/>
    <text x="80" y="65" text-anchor="middle" class="text-body">Схема БД</text>
    <text x="80" y="80" text-anchor="middle" class="text-del">- видалення старої</text>
    <rect x="15" y="105" width="130" height="45" class="box-active"/>
    <text x="80" y="125" text-anchor="middle" class="text-body">Додаток (Фінал)</text>
    <text x="80" y="140" text-anchor="middle" class="text-accent">чиста версія v2</text>
    <text x="80" y="190" text-anchor="middle" class="text-body" fill="#8b949e">Нульовий простій</text>
    <text x="80" y="210" text-anchor="middle" class="text-accent">Zero-Downtime OK</text>
  </g>
</svg>'''
    return svg

def generate_lock_modes():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 360" width="100%" height="100%">
  <style>
    .bg { fill: #0d1117; }
    .box { fill: #161b22; stroke: #30363d; stroke-width: 1.5; rx: 6px; }
    .box-danger { fill: #2d1215; stroke: #f85149; stroke-width: 1.5; rx: 6px; }
    .box-safe { fill: #0e2a18; stroke: #3fb950; stroke-width: 1.5; rx: 6px; }
    .text-title { fill: #58a6ff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 14px; }
    .text-sub { fill: #8b949e; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 11px; }
    .text-body { fill: #c9d1d9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 12px; }
    .text-danger { fill: #f85149; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 12px; }
    .text-safe { fill: #3fb950; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 12px; }
    .arrow { stroke: #f85149; stroke-width: 2; fill: none; marker-end: url(#arrow-red); }
  </style>
  <defs>
    <marker id="arrow-red" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="#f85149"/>
    </marker>
  </defs>

  <rect width="100%" height="100%" class="bg"/>

  <text x="400" y="30" text-anchor="middle" class="text-title">Ієрархія блокувань DDL та блокувальні каскади у PostgreSQL</text>

  <!-- Left: Dangerous DDL -->
  <g transform="translate(40, 60)">
    <rect width="340" height="260" class="box-danger"/>
    <text x="170" y="30" text-anchor="middle" class="text-danger">НЕБЕЗПЕЧНИЙ ШЛЯХ: AccessExclusiveLock</text>
    
    <rect x="20" y="55" width="300" height="40" class="box"/>
    <text x="30" y="80" class="text-body">1. Довгий SELECT (AccessShareLock)</text>
    
    <rect x="20" y="105" width="300" height="40" class="box-danger"/>
    <text x="30" y="130" class="text-danger">2. ALTER TABLE ADD COLUMN DEFAULT (Чекає)</text>
    
    <rect x="20" y="155" width="300" height="40" class="box"/>
    <text x="30" y="180" class="text-body">3. Нові швидкі SELECT/INSERT (Заблоковані!)</text>

    <text x="170" y="225" text-anchor="middle" class="text-danger">Каскад вичерпує connection pool</text>
    <text x="170" y="245" text-anchor="middle" class="text-sub">Повний простій системи (Downtime)</text>
  </g>

  <!-- Right: Safe DDL -->
  <g transform="translate(420, 60)">
    <rect width="340" height="260" class="box-safe"/>
    <text x="170" y="30" text-anchor="middle" class="text-safe">БЕЗПЕЧНИЙ ШЛЯХ: Неблокуючі міграції</text>
    
    <rect x="20" y="55" width="300" height="40" class="box"/>
    <text x="30" y="80" class="text-body">1. SET lock_timeout = '2s';</text>
    
    <rect x="20" y="105" width="300" height="40" class="box-safe"/>
    <text x="30" y="130" class="text-safe">2. CREATE INDEX CONCURRENTLY</text>
    
    <rect x="20" y="155" width="300" height="40" class="box"/>
    <text x="30" y="180" class="text-body">3. Паралельні SELECT/INSERT працюють</text>

    <text x="170" y="225" text-anchor="middle" class="text-safe">Низький рівень ShareUpdateExclusive</text>
    <text x="170" y="245" text-anchor="middle" class="text-sub">Нульове блокування читання й запису</text>
  </g>
</svg>'''
    return svg

def generate_shadow_table():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 360" width="100%" height="100%">
  <style>
    .bg { fill: #0d1117; }
    .box { fill: #161b22; stroke: #30363d; stroke-width: 1.5; rx: 6px; }
    .box-active { fill: #1f2937; stroke: #58a6ff; stroke-width: 1.5; rx: 6px; }
    .box-shadow { fill: #1a2332; stroke: #3fb950; stroke-width: 2; rx: 6px; stroke-dasharray: 4,4; }
    .text-title { fill: #58a6ff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 14px; }
    .text-body { fill: #c9d1d9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 12px; }
    .text-accent { fill: #3fb950; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 12px; }
    .arrow { stroke: #8b949e; stroke-width: 1.5; fill: none; marker-end: url(#arrow-grey); }
    .arrow-sync { stroke: #3fb950; stroke-width: 2; fill: none; marker-end: url(#arrow-green); }
  </style>
  <defs>
    <marker id="arrow-grey" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="#8b949e"/>
    </marker>
    <marker id="arrow-green" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="#3fb950"/>
    </marker>
  </defs>

  <rect width="100%" height="100%" class="bg"/>

  <text x="400" y="30" text-anchor="middle" class="text-title">Онлайн-міграція великих таблиць через тіньову таблицю (gh-ost / pt-osc)</text>

  <!-- Original Table -->
  <g transform="translate(60, 70)">
    <rect width="200" height="200" class="box-active"/>
    <text x="100" y="30" text-anchor="middle" class="text-title">Оригінальна таблиця</text>
    <text x="100" y="55" text-anchor="middle" class="text-body" fill="#8b949e">`users` (100 млн рядків)</text>
    
    <rect x="20" y="80" width="160" height="40" class="box"/>
    <text x="100" y="105" text-anchor="middle" class="text-body">Live Traffic (OLTP)</text>

    <text x="100" y="150" text-anchor="middle" class="text-body">Стара схема</text>
    <text x="100" y="170" text-anchor="middle" class="text-body" fill="#8b949e">Читання й Запис</text>
  </g>

  <!-- Middle Component: Replication Stream / Chunker -->
  <g transform="translate(300, 70)">
    <rect width="200" height="90" class="box"/>
    <text x="100" y="30" text-anchor="middle" class="text-title">Порядковий бекфіл</text>
    <text x="100" y="55" text-anchor="middle" class="text-body">Батчі по 1000 рядків</text>
    <text x="100" y="75" text-anchor="middle" class="text-body" fill="#8b949e">WHERE id BETWEEN x AND y</text>

    <rect y="110" width="200" height="90" class="box"/>
    <text x="100" y="140" text-anchor="middle" class="text-accent">CDC / Binlog Stream</text>
    <text x="100" y="165" text-anchor="middle" class="text-body">Синхронізація дельт</text>
    <text x="100" y="185" text-anchor="middle" class="text-body" fill="#8b949e">(INSERT/UPDATE/DELETE)</text>
  </g>

  <!-- Shadow Table -->
  <g transform="translate(540, 70)">
    <rect width="200" height="200" class="box-shadow"/>
    <text x="100" y="30" text-anchor="middle" class="text-accent">Тіньова таблиця</text>
    <text x="100" y="55" text-anchor="middle" class="text-body" fill="#8b949e">`_users_gho`</text>
    
    <rect x="20" y="80" width="160" height="40" class="box"/>
    <text x="100" y="105" text-anchor="middle" class="text-accent">Нова схема</text>

    <text x="100" y="150" text-anchor="middle" class="text-body">Атомарне перейменування</text>
    <text x="100" y="170" text-anchor="middle" class="text-accent">RENAME TABLE (1 мс)</text>
  </g>

  <!-- Flow Arrows -->
  <line x1="260" y1="115" x2="300" y2="115" class="arrow"/>
  <line x1="260" y1="210" x2="300" y2="210" class="arrow-sync"/>
  <line x1="500" y1="115" x2="540" y2="115" class="arrow"/>
  <line x1="500" y1="210" x2="540" y2="210" class="arrow-sync"/>

  <text x="400" y="320" text-anchor="middle" class="text-body" fill="#8b949e">Атомарне перемикання (Cutover) через RENAME TABLE tbl TO tbl_old, _tbl_gho TO tbl без простою</text>
</svg>'''
    return svg

def generate_zero_downtime():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 320" width="100%" height="100%">
  <style>
    .bg { fill: #0d1117; }
    .box { fill: #161b22; stroke: #30363d; stroke-width: 1.5; rx: 6px; }
    .box-green { fill: #0e2a18; stroke: #3fb950; stroke-width: 1.5; rx: 6px; }
    .text-title { fill: #58a6ff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 14px; }
    .text-body { fill: #c9d1d9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 12px; }
    .text-accent { fill: #3fb950; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 12px; }
    .arrow { stroke: #58a6ff; stroke-width: 1.5; fill: none; marker-end: url(#arrow-blue); }
  </style>
  <defs>
    <marker id="arrow-blue" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="#58a6ff"/>
    </marker>
  </defs>

  <rect width="100%" height="100%" class="bg"/>

  <text x="400" y="30" text-anchor="middle" class="text-title">Пайплайн неперервної доставки міграцій (CI/CD Zero-Downtime Pipeline)</text>

  <!-- Step 1: Migration Linting -->
  <g transform="translate(40, 70)">
    <rect width="160" height="180" class="box"/>
    <text x="80" y="30" text-anchor="middle" class="text-title">1. CI Лінтинг</text>
    <text x="80" y="60" text-anchor="middle" class="text-body">Squawk / pg-audit</text>
    <text x="80" y="90" text-anchor="middle" class="text-body" fill="#8b949e">Перевірка на</text>
    <text x="80" y="110" text-anchor="middle" class="text-body" fill="#8b949e">AccessExclusiveLock</text>
    <text x="80" y="140" text-anchor="middle" class="text-accent">Статичний аудит</text>
  </g>

  <line x1="200" y1="160" x2="230" y2="160" class="arrow"/>

  <!-- Step 2: Pre-deployment Migration -->
  <g transform="translate(230, 70)">
    <rect width="160" height="180" class="box"/>
    <text x="80" y="30" text-anchor="middle" class="text-title">2. Pre-Deploy DDL</text>
    <text x="80" y="60" text-anchor="middle" class="text-body">ADD COLUMN NULL</text>
    <text x="80" y="90" text-anchor="middle" class="text-body" fill="#8b949e">CREATE INDEX</text>
    <text x="80" y="110" text-anchor="middle" class="text-body" fill="#8b949e">CONCURRENTLY</text>
    <text x="80" y="140" text-anchor="middle" class="text-accent">Сумісно зі старим</text>
  </g>

  <line x1="390" y1="160" x2="420" y2="160" class="arrow"/>

  <!-- Step 3: Rolling App Deploy -->
  <g transform="translate(420, 70)">
    <rect width="160" height="180" class="box-green"/>
    <text x="80" y="30" text-anchor="middle" class="text-accent">3. Rolling Deploy</text>
    <text x="80" y="60" text-anchor="middle" class="text-body">Оновлення подів</text>
    <text x="80" y="90" text-anchor="middle" class="text-body" fill="#8b949e">v1 та v2 працюють</text>
    <text x="80" y="110" text-anchor="middle" class="text-body" fill="#8b949e">одночасно в кластері</text>
    <text x="80" y="140" text-anchor="middle" class="text-accent">Нуль помилок 5xx</text>
  </g>

  <line x1="580" y1="160" x2="610" y2="160" class="arrow"/>

  <!-- Step 4: Post-deployment Cleanup -->
  <g transform="translate(610, 70)">
    <rect width="160" height="180" class="box"/>
    <text x="80" y="30" text-anchor="middle" class="text-title">4. Post-Deploy DDL</text>
    <text x="80" y="60" text-anchor="middle" class="text-body">DROP NOT NULL</text>
    <text x="80" y="90" text-anchor="middle" class="text-body" fill="#8b949e">DROP COLUMN old</text>
    <text x="80" y="110" text-anchor="middle" class="text-body" fill="#8b949e">Прибирання тригерів</text>
    <text x="80" y="140" text-anchor="middle" class="text-accent">Фінал циклу</text>
  </g>
</svg>'''
    return svg

def main():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    
    files = {
        "expand-contract-migration.svg": generate_expand_contract(),
        "lock-modes-ddl.svg": generate_lock_modes(),
        "shadow-table-flow.svg": generate_shadow_table(),
        "zero-downtime-pipeline.svg": generate_zero_downtime()
    }
    
    for filename, content in files.items():
        filepath = os.path.join(img_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Generated {filepath}")

if __name__ == "__main__":
    main()

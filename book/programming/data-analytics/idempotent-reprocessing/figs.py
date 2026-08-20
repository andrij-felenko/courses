# -*- coding: utf-8 -*-
"""Generate technical SVG diagrams for Idempotent Reprocessing and Backfilling."""
import os
import sys

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def generate_partition_overwrite_vs_append():
    return '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 380" width="100%" height="100%">
  <style>
    .bg { fill: #0d1117; }
    .box-bad { fill: #1f1618; stroke: #f85149; stroke-width: 1.5; rx: 6px; }
    .box-good { fill: #122118; stroke: #3fb950; stroke-width: 1.5; rx: 6px; }
    .box-inner { fill: #161b22; stroke: #30363d; stroke-width: 1.2; rx: 4px; }
    .title-bad { fill: #f85149; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 15px; }
    .title-good { fill: #3fb950; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 15px; }
    .text-head { fill: #58a6ff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 13px; }
    .text-body { fill: #c9d1d9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 12px; }
    .text-sub { fill: #8b949e; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 11px; }
    .text-warn { fill: #d29922; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 12px; }
    .text-ok { fill: #3fb950; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 12px; }
    .arrow { stroke: #8b949e; stroke-width: 1.5; fill: none; marker-end: url(#arr); }
    .arrow-bad { stroke: #f85149; stroke-width: 1.5; fill: none; marker-end: url(#arr-bad); }
    .arrow-good { stroke: #3fb950; stroke-width: 1.5; fill: none; marker-end: url(#arr-good); }
  </style>
  <defs>
    <marker id="arr" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="#8b949e"/>
    </marker>
    <marker id="arr-bad" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="#f85149"/>
    </marker>
    <marker id="arr-good" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="#3fb950"/>
    </marker>
  </defs>

  <rect width="100%" height="100%" class="bg"/>

  <!-- Left: Naive Append -->
  <g transform="translate(30, 25)">
    <rect width="380" height="330" class="box-bad"/>
    <text x="190" y="28" text-anchor="middle" class="title-bad">Наївний долив (INSERT / Append)</text>

    <!-- Run 1 -->
    <rect x="20" y="45" width="340" height="60" class="box-inner"/>
    <text x="35" y="68" class="text-head">Перший прогін (день 1):</text>
    <text x="35" y="88" class="text-body">INSERT 100 рядків за 2026-08-20 → Сума = 10 000 ₴</text>

    <!-- Run 2 -->
    <rect x="20" y="120" width="340" height="75" class="box-inner"/>
    <text x="35" y="142" class="text-head">Повторний прогін (Backfill після збою):</text>
    <text x="35" y="162" class="text-body">Повторний INSERT тих самих 100 рядків</text>
    <text x="35" y="180" class="text-warn">Рядки дублюються: у таблиці 200 записів!</text>

    <!-- Impact -->
    <rect x="20" y="210" width="340" height="95" class="box-inner"/>
    <text x="35" y="235" class="title-bad">Наслідки неідемпотентності:</text>
    <text x="35" y="257" class="text-body">• Звіти спотворені: Сума = 20 000 ₴ (подвоєння)</text>
    <text x="35" y="277" class="text-body">• Часткове падіння залишає розламаний стан</text>
    <text x="35" y="297" class="text-sub">• Відновлення вимагає складної ручної чистки</text>
  </g>

  <!-- Right: Partition Overwrite / Upsert -->
  <g transform="translate(440, 25)">
    <rect width="380" height="330" class="box-good"/>
    <text x="190" y="28" text-anchor="middle" class="title-good">Ідемпотентна заміна (Atomic Overwrite)</text>

    <!-- Run 1 -->
    <rect x="20" y="45" width="340" height="60" class="box-inner"/>
    <text x="35" y="68" class="text-head">Перший прогін (день 1):</text>
    <text x="35" y="88" class="text-body">OVERWRITE партиції dt='2026-08-20' → 10 000 ₴</text>

    <!-- Run 2 -->
    <rect x="20" y="120" width="340" height="75" class="box-inner"/>
    <text x="35" y="142" class="text-head">Повторний прогін (Backfill / Перерахунок):</text>
    <text x="35" y="162" class="text-body">Атомарна заміна тієї самої партиції</text>
    <text x="35" y="180" class="text-ok">Результат ідентичний: рівно 100 рядків</text>

    <!-- Impact -->
    <rect x="20" y="210" width="340" height="95" class="box-inner"/>
    <text x="35" y="235" class="title-good">Гарантії ідемпотентності:</text>
    <text x="35" y="257" class="text-body">• Результат n прогонів = результату 1 прогону</text>
    <text x="35" y="277" class="text-body">• Падіння не руйнує дані (атомарний commit)</text>
    <text x="35" y="297" class="text-sub">• Безпечний перерахунок у будь-який момент</text>
  </g>
</svg>'''

def generate_backfill_time_windowing():
    return '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 360" width="100%" height="100%">
  <style>
    .bg { fill: #0d1117; }
    .panel { fill: #161b22; stroke: #30363d; stroke-width: 1.5; rx: 6px; }
    .chunk-box { fill: #1f2937; stroke: #58a6ff; stroke-width: 1.2; rx: 4px; }
    .chunk-active { fill: #1a3826; stroke: #3fb950; stroke-width: 1.5; rx: 4px; }
    .chunk-late { fill: #38271a; stroke: #d29922; stroke-width: 1.2; stroke-dasharray: 3,3; rx: 4px; }
    .text-title { fill: #58a6ff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 15px; }
    .text-head { fill: #e6edf3; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 13px; }
    .text-body { fill: #c9d1d9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 12px; }
    .text-sub { fill: #8b949e; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 11px; }
    .text-accent { fill: #3fb950; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 12px; }
    .text-warn { fill: #d29922; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 12px; }
    .axis { stroke: #484f58; stroke-width: 2; marker-end: url(#arr-axis); }
    .grid-line { stroke: #30363d; stroke-dasharray: 4,4; stroke-width: 1; }
  </style>
  <defs>
    <marker id="arr-axis" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="#484f58"/>
    </marker>
  </defs>

  <rect width="100%" height="100%" class="bg"/>

  <g transform="translate(30, 20)">
    <rect width="790" height="320" class="panel"/>
    <text x="395" y="28" text-anchor="middle" class="text-title">Детермінована нарізка історії на часові вікна (Event-Time Chunks)</text>

    <!-- Timeline Axis -->
    <line x1="50" y1="90" x2="740" y2="90" class="axis"/>
    <text x="745" y="94" class="text-sub">Час подій (Event Time, t)</text>

    <!-- Chunks -->
    <rect x="60" y="110" width="140" height="85" class="chunk-box"/>
    <text x="130" y="132" text-anchor="middle" class="text-head">Вікно 1</text>
    <text x="130" y="152" text-anchor="middle" class="text-sub">[2026-08-01, 08-05)</text>
    <text x="130" y="177" text-anchor="middle" class="text-accent">✓ Завершено</text>

    <rect x="220" y="110" width="140" height="85" class="chunk-box"/>
    <text x="290" y="132" text-anchor="middle" class="text-head">Вікно 2</text>
    <text x="290" y="152" text-anchor="middle" class="text-sub">[2026-08-05, 08-10)</text>
    <text x="290" y="177" text-anchor="middle" class="text-accent">✓ Завершено</text>

    <rect x="380" y="110" width="140" height="85" class="chunk-active"/>
    <text x="450" y="132" text-anchor="middle" class="text-head">Вікно 3 (Backfill)</text>
    <text x="450" y="152" text-anchor="middle" class="text-sub">[2026-08-10, 08-15)</text>
    <text x="450" y="177" text-anchor="middle" class="text-head" fill="#3fb950">⚙ В процесі</text>

    <rect x="540" y="110" width="140" height="85" class="chunk-late"/>
    <text x="610" y="132" text-anchor="middle" class="text-head">Запізнілі дані</text>
    <text x="610" y="152" text-anchor="middle" class="text-sub">t_event &lt; t_watermark</text>
    <text x="610" y="177" text-anchor="middle" class="text-warn">Точковий реплей</text>

    <!-- Rules Box -->
    <rect x="50" y="215" width="690" height="85" class="panel" style="fill: #0d1117; stroke: #21262d;"/>
    <text x="70" y="238" class="text-head">Ключові правила детермінізму вікон:</text>
    <text x="70" y="260" class="text-body">1. Межі фільтрації суворо замкнені за часом події: [t_start, t_end) — без використання now() чи wall-clock.</text>
    <text x="70" y="282" class="text-body">2. Розмір чанка фіксований: забезпечує обмежений blast radius при помилці та легкий перезапуск з курсора.</text>
  </g>
</svg>'''

def generate_as_of_dimension_join():
    return '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 370" width="100%" height="100%">
  <style>
    .bg { fill: #0d1117; }
    .box { fill: #161b22; stroke: #30363d; stroke-width: 1.5; rx: 6px; }
    .box-bad { fill: #20171a; stroke: #f85149; stroke-width: 1.5; rx: 6px; }
    .box-good { fill: #13241b; stroke: #3fb950; stroke-width: 1.5; rx: 6px; }
    .text-title { fill: #58a6ff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 15px; }
    .text-bad { fill: #f85149; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 13px; }
    .text-good { fill: #3fb950; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 13px; }
    .text-head { fill: #e6edf3; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 12px; }
    .text-body { fill: #c9d1d9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 11.5px; }
    .text-sub { fill: #8b949e; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 11px; }
    .arrow { stroke: #8b949e; stroke-width: 1.5; fill: none; marker-end: url(#arr-asof); }
  </style>
  <defs>
    <marker id="arr-asof" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="#8b949e"/>
    </marker>
  </defs>

  <rect width="100%" height="100%" class="bg"/>

  <g transform="translate(30, 20)">
    <rect width="790" height="330" class="box"/>
    <text x="395" y="28" text-anchor="middle" class="text-title">Точка в часі (Point-in-Time / AS-OF Join) при перерахунку історії</text>

    <!-- Top: Historical Fact -->
    <rect x="250" y="48" width="290" height="50" class="box" style="fill: #1f2937; stroke: #58a6ff;"/>
    <text x="395" y="68" text-anchor="middle" class="text-head">Історична подія: Замовлення #402</text>
    <text x="395" y="86" text-anchor="middle" class="text-sub">event_time = 2024-03-15 | клієнт: user_12</text>

    <!-- Left: Naive Join with Current Dimension -->
    <g transform="translate(30, 120)">
      <rect width="345" height="185" class="box-bad"/>
      <text x="172" y="24" text-anchor="middle" class="text-bad">Наївний JOIN з поточною таблицею</text>
      
      <rect x="15" y="38" width="315" height="42" class="box" style="fill: #161b22;"/>
      <text x="25" y="56" class="text-head">Таблиця users (Стан на сьогодні):</text>
      <text x="25" y="72" class="text-sub">user_12 → Тариф: "VIP" (змінено в 2026 році)</text>

      <text x="20" y="105" class="text-body">• Подія 2024 року зв'язується з тарифом 2026 р.</text>
      <text x="20" y="125" class="text-body">• Знижка порахована хибно (історія спотворена)</text>
      <text x="20" y="145" class="text-body">• Перерахунок дає інше число, ніж було в чеку!</text>
      <text x="172" y="170" text-anchor="middle" class="text-bad" style="font-size: 11px;">✖ Порушення історичної правдивості</text>
    </g>

    <!-- Right: AS-OF Join with SCD Type 2 -->
    <g transform="translate(415, 120)">
      <rect width="345" height="185" class="box-good"/>
      <text x="172" y="24" text-anchor="middle" class="text-good">Ідемпотентний AS-OF Join (SCD2)</text>
      
      <rect x="15" y="38" width="315" height="42" class="box" style="fill: #161b22;"/>
      <text x="25" y="56" class="text-head">Таблиця users_history (SCD Type 2):</text>
      <text x="25" y="72" class="text-sub">valid_from &lt;= '2024-03-15' &lt; valid_to → "Базовий"</text>

      <text x="20" y="105" class="text-body">• Подія зв'язується зі станом, чинним на дату події</text>
      <text x="20" y="125" class="text-body">• Знижка та податки відтворюються абсолютно точно</text>
      <text x="20" y="145" class="text-body">• Детермінований результат незалежно від дати запуску</text>
      <text x="172" y="170" text-anchor="middle" class="text-good" style="font-size: 11px;">✓ Повна відтворюваність історії</text>
    </g>
  </g>
</svg>'''

def generate_idempotent_pipeline_architecture():
    return '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 380" width="100%" height="100%">
  <style>
    .bg { fill: #0d1117; }
    .layer { fill: #161b22; stroke: #30363d; stroke-width: 1.5; rx: 6px; }
    .box-step { fill: #1f2937; stroke: #58a6ff; stroke-width: 1.2; rx: 4px; }
    .box-swap { fill: #1c3224; stroke: #3fb950; stroke-width: 1.5; rx: 4px; }
    .text-title { fill: #58a6ff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 15px; }
    .text-head { fill: #e6edf3; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 12px; }
    .text-body { fill: #c9d1d9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 11.5px; }
    .text-sub { fill: #8b949e; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 11px; }
    .text-accent { fill: #3fb950; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 12px; }
    .arrow { stroke: #58a6ff; stroke-width: 1.5; fill: none; marker-end: url(#arr-pipe); }
    .arrow-swap { stroke: #3fb950; stroke-width: 2; fill: none; marker-end: url(#arr-swap); }
  </style>
  <defs>
    <marker id="arr-pipe" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="#58a6ff"/>
    </marker>
    <marker id="arr-swap" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="#3fb950"/>
    </marker>
  </defs>

  <rect width="100%" height="100%" class="bg"/>

  <g transform="translate(25, 20)">
    <rect width="800" height="340" class="layer"/>
    <text x="400" y="28" text-anchor="middle" class="text-title">Архітектура ідемпотентного конвеєра: Ізольована генерація та атомарний Swap</text>

    <!-- Stage 1: Immutable Source -->
    <rect x="25" y="60" width="165" height="150" class="box-step"/>
    <text x="107" y="85" text-anchor="middle" class="text-head">1. Нерухоме сире</text>
    <text x="107" y="105" text-anchor="middle" class="text-sub">(Raw Events / Bronze)</text>
    <text x="35" y="135" class="text-body">• Append-only лог</text>
    <text x="35" y="155" class="text-body">• Незмінні факти</text>
    <text x="35" y="175" class="text-body">• Первинне джерело</text>
    <text x="35" y="195" class="text-sub">Partition: dt=YYYY-MM-DD</text>

    <line x1="195" y1="135" x2="225" y2="135" class="arrow"/>

    <!-- Stage 2: Pure Transform Engine -->
    <rect x="230" y="60" width="175" height="150" class="box-step"/>
    <text x="317" y="85" text-anchor="middle" class="text-head">2. Чиста трансформація</text>
    <text x="317" y="105" text-anchor="middle" class="text-sub">(Spark / DuckDB / dbt)</text>
    <text x="240" y="135" class="text-body">• Детермінований код</text>
    <text x="240" y="155" class="text-body">• AS-OF розмітка</text>
    <text x="240" y="175" class="text-body">• Без побічних дій</text>
    <text x="240" y="195" class="text-sub">F(Raw[t1, t2]) = Derived</text>

    <line x1="410" y1="135" x2="440" y2="135" class="arrow"/>

    <!-- Stage 3: Staging Area -->
    <rect x="445" y="60" width="165" height="150" class="box-step"/>
    <text x="527" y="85" text-anchor="middle" class="text-head">3. Тіньовий запис</text>
    <text x="527" y="105" text-anchor="middle" class="text-sub">(Staging Partition)</text>
    <text x="455" y="135" class="text-body">• _staging_part_0820</text>
    <text x="455" y="155" class="text-body">• Повна ізоляція</text>
    <text x="455" y="175" class="text-body">• Перевірка тестів</text>
    <text x="455" y="195" class="text-sub">Fail → DROP staging</text>

    <line x1="615" y1="135" x2="645" y2="135" class="arrow-swap"/>

    <!-- Stage 4: Production Gold Table -->
    <rect x="650" y="60" width="125" height="150" class="box-swap"/>
    <text x="712" y="85" text-anchor="middle" class="text-head" fill="#3fb950">4. Продакшн</text>
    <text x="712" y="105" text-anchor="middle" class="text-sub">(Gold Layer)</text>
    <text x="660" y="135" class="text-body">• Атомарний</text>
    <text x="660" y="155" class="text-body">  SWAP /</text>
    <text x="660" y="175" class="text-body">  OVERWRITE</text>
    <text x="660" y="195" class="text-accent">&lt; 5 мс затримка</text>

    <!-- Bottom summary bar -->
    <rect x="25" y="235" width="750" height="80" class="layer" style="fill: #0d1117; stroke: #21262d;"/>
    <text x="45" y="260" class="text-head">Чому ця схема невразлива до аварій під час перерахунку:</text>
    <text x="45" y="282" class="text-body">Якщо генератор падає на кроці 2 чи 3, жива продакшн-таблиця не містить жодного сміття чи напівзаписаних рядків.</text>
    <text x="45" y="302" class="text-body">Атомарна зміна метаданих на кроці 4 перемикає покажчик партиції миттєво, усуваючи стан гонитви з читачами.</text>
  </g>
</svg>'''

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = os.path.join(base_dir, "img")
    ensure_dir(img_dir)

    figs = {
        "partition-overwrite-vs-append.svg": generate_partition_overwrite_vs_append(),
        "backfill-time-windowing.svg": generate_backfill_time_windowing(),
        "as-of-dimension-join.svg": generate_as_of_dimension_join(),
        "idempotent-pipeline-architecture.svg": generate_idempotent_pipeline_architecture(),
    }

    for name, content in figs.items():
        out_path = os.path.join(img_dir, name)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Generated: {out_path}")

if __name__ == "__main__":
    main()

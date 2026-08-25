"""Generate technical SVG diagrams for Schema-on-write vs Schema-on-read."""
import os
import sys

def generate_schema_on_write():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 340" width="100%" height="100%">
  <style>
    .bg { fill: #0d1117; }
    .box { fill: #161b22; stroke: #30363d; stroke-width: 1.5; rx: 6px; }
    .box-step { fill: #1a2332; stroke: #58a6ff; stroke-width: 1.5; rx: 6px; }
    .box-db { fill: #13271f; stroke: #3fb950; stroke-width: 1.5; rx: 6px; }
    .text-title { fill: #58a6ff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 14px; }
    .text-body { fill: #c9d1d9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 11px; }
    .text-sub { fill: #8b949e; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 10px; }
    .text-green { fill: #3fb950; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 12px; }
  </style>

  <rect width="100%" height="100%" class="bg"/>
  <text x="400" y="30" text-anchor="middle" class="text-title">Архітектурний потік Schema-on-write (Класичні СУБД)</text>

  <!-- Step 1: Ingestion -->
  <g transform="translate(40, 70)">
    <rect width="180" height="180" class="box-step"/>
    <text x="90" y="30" text-anchor="middle" class="text-title">1. Вхідні дані</text>
    <text x="90" y="60" text-anchor="middle" class="text-body">Клієнтський запит</text>
    <text x="90" y="85" text-anchor="middle" class="text-body">JSON / DTO об'єкт</text>
    <text x="90" y="125" text-anchor="middle" class="text-sub">Дані неструктуровані</text>
    <text x="90" y="145" text-anchor="middle" class="text-sub">або напівструктуровані</text>
  </g>

  <!-- Step 2: Strict Validation -->
  <g transform="translate(310, 70)">
    <rect width="180" height="180" class="box" stroke="#d29922"/>
    <text x="90" y="30" text-anchor="middle" class="text-title" fill="#d29922">2. Валідація схеми</text>
    <text x="90" y="60" text-anchor="middle" class="text-body">Перевірка типів</text>
    <text x="90" y="85" text-anchor="middle" class="text-body">Перевірка NOT NULL</text>
    <text x="90" y="110" text-anchor="middle" class="text-body">Foreign Key інваріанти</text>
    <text x="90" y="145" text-anchor="middle" class="text-sub">Невідповідність -> Відхилення</text>
  </g>

  <!-- Step 3: Structured Storage -->
  <g transform="translate(580, 70)">
    <rect width="180" height="180" class="box-db"/>
    <text x="90" y="30" text-anchor="middle" class="text-green">3. Табличний диск</text>
    <text x="90" y="60" text-anchor="middle" class="text-body">Фіксовані зміщення</text>
    <text x="90" y="85" text-anchor="middle" class="text-body">Компактні бінарні кортежі</text>
    <text x="90" y="110" text-anchor="middle" class="text-body">B-Tree індексація</text>
    <text x="90" y="145" text-anchor="middle" class="text-sub">Миттєве читання O(1)</text>
  </g>

  <path d="M 220 160 L 310 160" stroke="#58a6ff" stroke-width="2" marker-end="url(#arr)"/>
  <path d="M 490 160 L 580 160" stroke="#58a6ff" stroke-width="2" marker-end="url(#arr)"/>
  
  <text x="400" y="290" text-anchor="middle" class="text-sub">Ціна валідації сплачується ОДИН раз під час запису (Write-heavy validation, Read-fast)</text>
</svg>'''
    return svg

def generate_schema_on_read():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 340" width="100%" height="100%">
  <style>
    .bg { fill: #0d1117; }
    .box { fill: #161b22; stroke: #30363d; stroke-width: 1.5; rx: 6px; }
    .box-step { fill: #1a2332; stroke: #58a6ff; stroke-width: 1.5; rx: 6px; }
    .box-lake { fill: #2c1a1d; stroke: #f85149; stroke-width: 1.5; rx: 6px; }
    .text-title { fill: #58a6ff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 14px; }
    .text-body { fill: #c9d1d9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 11px; }
    .text-sub { fill: #8b949e; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 10px; }
    .text-warn { fill: #f85149; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 12px; }
  </style>

  <rect width="100%" height="100%" class="bg"/>
  <text x="400" y="30" text-anchor="middle" class="text-title">Архітектурний потік Schema-on-read (Data Lake / NoSQL)</text>

  <!-- Step 1: Raw Ingestion -->
  <g transform="translate(40, 70)">
    <rect width="180" height="180" class="box-step"/>
    <text x="90" y="30" text-anchor="middle" class="text-title">1. Миттєвий запис</text>
    <text x="90" y="60" text-anchor="middle" class="text-body">Сирі логи, JSON, CSV</text>
    <text x="90" y="85" text-anchor="middle" class="text-body">Без перевірки схеми</text>
    <text x="90" y="110" text-anchor="middle" class="text-body">Запис за 1 мс</text>
    <text x="90" y="145" text-anchor="middle" class="text-sub">Висока пропускна здатність</text>
  </g>

  <!-- Step 2: Data Lake Store -->
  <g transform="translate(310, 70)">
    <rect width="180" height="180" class="box-lake"/>
    <text x="90" y="30" text-anchor="middle" class="text-warn">2. Сире сховище (Lake)</text>
    <text x="90" y="60" text-anchor="middle" class="text-body">Amazon S3, HDFS, Mongo</text>
    <text x="90" y="85" text-anchor="middle" class="text-body">Невпорядковані поля</text>
    <text x="90" y="110" text-anchor="middle" class="text-body">Різні версії структур</text>
    <text x="90" y="145" text-anchor="middle" class="text-sub">Ризик Data Swamp</text>
  </g>

  <!-- Step 3: Query Interpretation -->
  <g transform="translate(580, 70)">
    <rect width="180" height="180" class="box" stroke="#a371f7"/>
    <text x="90" y="30" text-anchor="middle" class="text-title" fill="#a371f7">3. Парсинг при читанні</text>
    <text x="90" y="60" text-anchor="middle" class="text-body">Spark / Presto / Athena</text>
    <text x="90" y="85" text-anchor="middle" class="text-body">Накладання схеми на льоту</text>
    <text x="90" y="110" text-anchor="middle" class="text-body">Парсинг JSON у CPU</text>
    <text x="90" y="145" text-anchor="middle" class="text-sub">Високі накладні витрати</text>
  </g>

  <path d="M 220 160 L 310 160" stroke="#58a6ff" stroke-width="2" marker-end="url(#arr)"/>
  <path d="M 490 160 L 580 160" stroke="#58a6ff" stroke-width="2" marker-end="url(#arr)"/>
  
  <text x="400" y="290" text-anchor="middle" class="text-sub">Ціна інтерпретації сплачується при КОЖНОМУ читанні (Write-fast, Read-heavy CPU overhead)</text>
</svg>'''
    return svg

def generate_schema_evolution():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 340" width="100%" height="100%">
  <style>
    .bg { fill: #0d1117; }
    .box { fill: #161b22; stroke: #30363d; stroke-width: 1.5; rx: 6px; }
    .text-title { fill: #58a6ff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 14px; }
    .text-body { fill: #c9d1d9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 11px; }
    .text-sub { fill: #8b949e; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 10px; }
    .text-highlight { fill: #f0883e; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 12px; }
  </style>

  <rect width="100%" height="100%" class="bg"/>
  <text x="400" y="30" text-anchor="middle" class="text-title">Режими сумісності схем (Schema Compatibility Modes)</text>

  <!-- Backward -->
  <g transform="translate(40, 60)">
    <rect width="220" height="230" class="box" stroke="#58a6ff"/>
    <text x="110" y="30" text-anchor="middle" class="text-highlight">1. BACKWARD</text>
    <text x="20" y="65" class="text-body">Новий код читає старі дані</text>
    <text x="20" y="100" class="text-body">• Додавання необов'язкових</text>
    <text x="30" y="120" class="text-body">полів із дефолтом</text>
    <text x="20" y="150" class="text-body">• Видалення обов'язкових</text>
    <text x="30" y="170" class="text-body">полів</text>
    <text x="110" y="210" text-anchor="middle" class="text-sub">Стандарт для споживачів</text>
  </g>

  <!-- Forward -->
  <g transform="translate(290, 60)">
    <rect width="220" height="230" class="box" stroke="#3fb950"/>
    <text x="110" y="30" text-anchor="middle" class="text-highlight">2. FORWARD</text>
    <text x="20" y="65" class="text-body">Старий код читає нові дані</text>
    <text x="20" y="100" class="text-body">• Видалення необов'язкових</text>
    <text x="30" y="120" class="text-body">полів</text>
    <text x="20" y="150" class="text-body">• Додавання обов'язкових</text>
    <text x="30" y="170" class="text-body">полів</text>
    <text x="110" y="210" text-anchor="middle" class="text-sub">Стандарт для виробників</text>
  </g>

  <!-- Full -->
  <g transform="translate(540, 60)">
    <rect width="220" height="230" class="box" stroke="#a371f7"/>
    <text x="110" y="30" text-anchor="middle" class="text-highlight">3. FULL (Повна сумісність)</text>
    <text x="20" y="65" class="text-body">Взаємна сумісність версій</text>
    <text x="20" y="100" class="text-body">• Одночасна підтримка</text>
    <text x="30" y="120" class="text-body">старого та нового коду</text>
    <text x="20" y="150" class="text-body">• Лише поля з дефолтами</text>
    <text x="110" y="210" text-anchor="middle" class="text-sub">Zero-Downtime розгортання</text>
  </g>
</svg>'''
    return svg

def main():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    
    files = {
        "schema-on-write-flow.svg": generate_schema_on_write(),
        "schema-on-read-flow.svg": generate_schema_on_read(),
        "schema-evolution-patterns.svg": generate_schema_evolution()
    }
    
    for filename, content in files.items():
        filepath = os.path.join(img_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Generated {filepath}")

if __name__ == "__main__":
    main()

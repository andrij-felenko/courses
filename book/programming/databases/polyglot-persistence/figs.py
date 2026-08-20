"""Generate technical SVG diagrams for Polyglot Persistence Architecture."""
import os
import sys

def generate_monolithic_vs_polyglot():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 360" width="100%" height="100%">
  <style>
    .bg { fill: #0d1117; }
    .box { fill: #161b22; stroke: #30363d; stroke-width: 1.5; rx: 6px; }
    .box-bad { fill: #2c1a1d; stroke: #f85149; stroke-width: 1.5; rx: 6px; }
    .box-good { fill: #13271f; stroke: #3fb950; stroke-width: 1.5; rx: 6px; }
    .text-title { fill: #58a6ff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 14px; }
    .text-body { fill: #c9d1d9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 11px; }
    .text-sub { fill: #8b949e; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 10px; }
    .text-bad { fill: #f85149; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 12px; }
    .text-good { fill: #3fb950; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 12px; }
  </style>

  <rect width="100%" height="100%" class="bg"/>
  <text x="400" y="30" text-anchor="middle" class="text-title">Монолітне сховище (One Size Fits All) проти Поліглотного збереження</text>

  <!-- Left: Monolithic Single DB -->
  <g transform="translate(40, 60)">
    <rect width="330" height="260" class="box-bad"/>
    <text x="165" y="30" text-anchor="middle" class="text-bad">1. Універсальний моноліт (RDBMS)</text>
    
    <rect x="25" y="55" width="280" height="40" class="box"/>
    <text x="165" y="80" text-anchor="middle" class="text-body">Одна реляційна БД для ВСІХ задач</text>

    <text x="35" y="125" class="text-body">• Транзакції: Чудово (ACID)</text>
    <text x="35" y="150" class="text-body">• Повнотекстовий пошук: Повільно (LIKE %..%)</text>
    <text x="35" y="175" class="text-body">• Кеш сесій: Високе навантаження на диск</text>
    <text x="35" y="200" class="text-body">• Графи/Друзі: Важкі рекурсивні JOIN</text>
    <text x="35" y="225" class="text-body">• Аналітика: Блокує операційні транзакції</text>
    <text x="165" y="250" text-anchor="middle" class="text-sub">Результат: Вузьке місце всієї системи</text>
  </g>

  <!-- Right: Polyglot Architecture -->
  <g transform="translate(430, 60)">
    <rect width="330" height="260" class="box-good"/>
    <text x="165" y="30" text-anchor="middle" class="text-good">2. Поліглотне збереження (Polyglot)</text>
    
    <rect x="25" y="50" width="280" height="30" class="box" stroke="#58a6ff"/>
    <text x="165" y="70" text-anchor="middle" class="text-body">PostgreSQL -> Транзакції та платежі</text>

    <rect x="25" y="90" width="280" height="30" class="box" stroke="#f85149"/>
    <text x="165" y="110" text-anchor="middle" class="text-body">Redis -> Сесії та лічильники O(1)</text>

    <rect x="25" y="130" width="280" height="30" class="box" stroke="#d29922"/>
    <text x="165" y="150" text-anchor="middle" class="text-body">Elasticsearch -> Пошук та автокомпліт</text>

    <rect x="25" y="170" width="280" height="30" class="box" stroke="#a371f7"/>
    <text x="165" y="190" text-anchor="middle" class="text-body">Neo4j -> Графи рекомендацій</text>

    <rect x="25" y="210" width="280" height="30" class="box" stroke="#3fb950"/>
    <text x="165" y="230" text-anchor="middle" class="text-body">ClickHouse -> Аналітика мільярдів логів</text>

    <text x="165" y="252" text-anchor="middle" class="text-sub">Результат: Ідеальний інструмент під кожне навантаження</text>
  </g>
</svg>'''
    return svg

def generate_polyglot_data_flows():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 360" width="100%" height="100%">
  <style>
    .bg { fill: #0d1117; }
    .box { fill: #161b22; stroke: #30363d; stroke-width: 1.5; rx: 6px; }
    .box-main { fill: #1a2332; stroke: #58a6ff; stroke-width: 1.5; rx: 6px; }
    .box-cdc { fill: #2c1a1d; stroke: #f85149; stroke-width: 1.5; rx: 6px; }
    .text-title { fill: #58a6ff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 14px; }
    .text-body { fill: #c9d1d9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 11px; }
    .text-code { fill: #d29922; font-family: "Courier New", monospace; font-size: 11px; }
  </style>

  <rect width="100%" height="100%" class="bg"/>
  <text x="400" y="30" text-anchor="middle" class="text-title">Синхронізація поліглотних сховищ через CDC та шину подій</text>

  <!-- Client & Primary DB -->
  <g transform="translate(40, 70)">
    <rect width="140" height="70" class="box-main"/>
    <text x="70" y="30" text-anchor="middle" class="text-title">Клієнт / API</text>
    <text x="70" y="50" text-anchor="middle" class="text-body">POST /orders</text>

    <!-- Arrow down -->
    <path d="M 70 70 L 70 120" stroke="#58a6ff" stroke-width="2" marker-end="url(#arr)"/>

    <rect y="120" width="140" height="90" class="box-main"/>
    <text x="70" y="145" text-anchor="middle" class="text-title">Primary OLTP</text>
    <text x="70" y="165" text-anchor="middle" class="text-body">PostgreSQL</text>
    <text x="70" y="185" text-anchor="middle" class="text-code">WAL / Outbox</text>
  </g>

  <!-- CDC Engine & Kafka -->
  <g transform="translate(250, 140)">
    <rect width="130" height="140" class="box-cdc"/>
    <text x="65" y="30" text-anchor="middle" class="text-title" fill="#f85149">CDC Engine</text>
    <text x="65" y="55" text-anchor="middle" class="text-body">Debezium</text>
    <text x="65" y="75" text-anchor="middle" class="text-body">Читання WAL</text>
    <text x="65" y="105" text-anchor="middle" class="text-code">Event Bus</text>
    <text x="65" y="125" text-anchor="middle" class="text-code">Apache Kafka</text>
  </g>

  <!-- Polyglot Read Models -->
  <g transform="translate(450, 60)">
    <!-- Redis -->
    <rect width="300" height="50" class="box" stroke="#f85149"/>
    <text x="150" y="25" text-anchor="middle" class="text-body" font-weight="bold">1. Redis Cache (L1 Read)</text>
    <text x="150" y="42" text-anchor="middle" class="text-sub">Миттєве отримання замовлення за 1 мс</text>

    <!-- Elasticsearch -->
    <rect y="70" width="300" height="50" class="box" stroke="#d29922"/>
    <text x="150" y="95" text-anchor="middle" class="text-body" font-weight="bold">2. Elasticsearch (Search Engine)</text>
    <text x="150" y="112" text-anchor="middle" class="text-sub">Фільтри товарів за назвою, брендом, ціною</text>

    <!-- Neo4j -->
    <rect y="140" width="300" height="50" class="box" stroke="#a371f7"/>
    <text x="150" y="165" text-anchor="middle" class="text-body" font-weight="bold">3. Neo4j (Graph Engine)</text>
    <text x="150" y="182" text-anchor="middle" class="text-sub">«З цим товаром також купують...»</text>

    <!-- ClickHouse -->
    <rect y="210" width="300" height="50" class="box" stroke="#3fb950"/>
    <text x="150" y="235" text-anchor="middle" class="text-body" font-weight="bold">4. ClickHouse (OLAP)</text>
    <text x="150" y="252" text-anchor="middle" class="text-sub">Агрегація продажів за квартал за 50 мс</text>
  </g>
</svg>'''
    return svg

def generate_cqrs_polyglot():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 360" width="100%" height="100%">
  <style>
    .bg { fill: #0d1117; }
    .box { fill: #161b22; stroke: #30363d; stroke-width: 1.5; rx: 6px; }
    .box-cmd { fill: #1a2332; stroke: #58a6ff; stroke-width: 1.5; rx: 6px; }
    .box-qry { fill: #13271f; stroke: #3fb950; stroke-width: 1.5; rx: 6px; }
    .text-title { fill: #58a6ff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 14px; }
    .text-body { fill: #c9d1d9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 11px; }
    .text-cmd { fill: #58a6ff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 12px; }
    .text-qry { fill: #3fb950; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 12px; }
  </style>

  <rect width="100%" height="100%" class="bg"/>
  <text x="400" y="30" text-anchor="middle" class="text-title">Патерн CQRS у поліглотній архітектурі</text>

  <!-- Command Side -->
  <g transform="translate(60, 60)">
    <rect width="320" height="250" class="box-cmd"/>
    <text x="160" y="30" text-anchor="middle" class="text-cmd">Command Side (Запис / Мутація)</text>
    
    <rect x="20" y="55" width="280" height="40" class="box"/>
    <text x="160" y="80" text-anchor="middle" class="text-body">Реляційна СУБД (PostgreSQL)</text>

    <text x="30" y="125" class="text-body">• Нормалізовані таблиці (3NF)</text>
    <text x="30" y="150" class="text-body">• Строгі транзакції ACID</text>
    <text x="30" y="175" class="text-body">• Валідація інваріантів та CHECK</text>
    <text x="30" y="200" class="text-body">• Оптимізація на надійність запису</text>
  </g>

  <!-- Query Side -->
  <g transform="translate(420, 60)">
    <rect width="320" height="250" class="box-qry"/>
    <text x="160" y="30" text-anchor="middle" class="text-qry">Query Side (Читання / Вибірка)</text>
    
    <rect x="20" y="55" width="280" height="40" class="box"/>
    <text x="160" y="80" text-anchor="middle" class="text-body">Спеціалізовані NoSQL сховища</text>

    <text x="30" y="125" class="text-body">• Денормалізовані матеріалізовані в'ю</text>
    <text x="30" y="150" class="text-body">• Документні та пошукові індекси</text>
    <text x="30" y="175" class="text-body">• Відсутність JOIN на момент запиту</text>
    <text x="30" y="200" class="text-body">• Кінцева узгодженість (Eventual Consistency)</text>
  </g>
</svg>'''
    return svg

def main():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    
    files = {
        "monolithic-db-vs-polyglot.svg": generate_monolithic_vs_polyglot(),
        "polyglot-data-flows-sync.svg": generate_polyglot_data_flows(),
        "cqrs-polyglot-architecture.svg": generate_cqrs_polyglot()
    }
    
    for filename, content in files.items():
        filepath = os.path.join(img_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Generated {filepath}")

if __name__ == "__main__":
    main()

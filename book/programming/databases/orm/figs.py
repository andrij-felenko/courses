"""Generate technical SVG diagrams for Object-Relational Mapping (ORM)."""
import os
import sys

def generate_impedance_mismatch():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 360" width="100%" height="100%">
  <style>
    .bg { fill: #0d1117; }
    .box { fill: #161b22; stroke: #30363d; stroke-width: 1.5; rx: 6px; }
    .box-obj { fill: #1a2332; stroke: #58a6ff; stroke-width: 1.5; rx: 6px; }
    .box-rel { fill: #261b2d; stroke: #bc8cff; stroke-width: 1.5; rx: 6px; }
    .text-title { fill: #58a6ff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 14px; }
    .text-body { fill: #c9d1d9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 12px; }
    .text-accent { fill: #3fb950; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 12px; }
    .text-warn { fill: #d29922; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 12px; }
    .arrow { stroke: #f85149; stroke-width: 2; fill: none; stroke-dasharray: 4,4; marker-end: url(#arrow-red); }
  </style>
  <defs>
    <marker id="arrow-red" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="#f85149"/>
    </marker>
  </defs>

  <rect width="100%" height="100%" class="bg"/>
  <text x="400" y="30" text-anchor="middle" class="text-title">Невідповідність об'єктно-реляційного імпедансу (Impedance Mismatch)</text>

  <!-- Left: Object World -->
  <g transform="translate(50, 60)">
    <rect width="320" height="260" class="box-obj"/>
    <text x="160" y="30" text-anchor="middle" class="text-title" fill="#58a6ff">Об'єктний світ (ООП)</text>
    <text x="30" y="70" class="text-body">• Граф об'єктів та вказівники</text>
    <text x="30" y="105" class="text-body">• Інкапсуляція стану та поведінки</text>
    <text x="30" y="140" class="text-body">• Успадкування та поліморфізм</text>
    <text x="30" y="175" class="text-body">• Ідентичність за адресою пам'яті (==)</text>
    <text x="30" y="210" class="text-body">• Нескінченна вкладеність зв'язків</text>
    <text x="160" y="245" text-anchor="middle" class="text-accent">Навігація по графу (user.getOrders())</text>
  </g>

  <!-- Right: Relational World -->
  <g transform="translate(430, 60)">
    <rect width="320" height="260" class="box-rel"/>
    <text x="160" y="30" text-anchor="middle" class="text-title" fill="#bc8cff">Реляційний світ (СУБД / SQL)</text>
    <text x="30" y="70" class="text-body">• Двовимірні плоскі таблиці</text>
    <text x="30" y="105" class="text-body">• Теорія множин та реляційна алгебра</text>
    <text x="30" y="140" class="text-body">• Первинні та зовнішні ключі (PK/FK)</text>
    <text x="30" y="175" class="text-body">• Ідентичність за значенням ключів</text>
    <text x="30" y="210" class="text-body">• Нормалізація (1NF, 2NF, 3NF)</text>
    <text x="160" y="245" text-anchor="middle" class="text-accent">Декларативні множинні операції (JOIN)</text>
  </g>

  <!-- Center Conflict Indicator -->
  <line x1="370" y1="190" x2="430" y2="190" class="arrow"/>
  <line x1="430" y1="190" x2="370" y2="190" class="arrow"/>
  <circle cx="400" cy="190" r="16" fill="#2d1215" stroke="#f85149" stroke-width="1.5"/>
  <text x="400" y="195" text-anchor="middle" fill="#f85149" font-weight="bold" font-size="12">VS</text>
</svg>'''
    return svg

def generate_active_record_vs_data_mapper():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 360" width="100%" height="100%">
  <style>
    .bg { fill: #0d1117; }
    .box { fill: #161b22; stroke: #30363d; stroke-width: 1.5; rx: 6px; }
    .box-ar { fill: #1a2332; stroke: #58a6ff; stroke-width: 1.5; rx: 6px; }
    .box-dm { fill: #13271f; stroke: #3fb950; stroke-width: 1.5; rx: 6px; }
    .text-title { fill: #58a6ff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 14px; }
    .text-body { fill: #c9d1d9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 12px; }
    .text-accent { fill: #3fb950; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 12px; }
    .arrow { stroke: #8b949e; stroke-width: 1.5; fill: none; marker-end: url(#arrowhead); }
  </style>
  <defs>
    <marker id="arrowhead" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="#8b949e"/>
    </marker>
  </defs>

  <rect width="100%" height="100%" class="bg"/>
  <text x="400" y="30" text-anchor="middle" class="text-title">Архітектурні патерни ORM: Active Record проти Data Mapper</text>

  <!-- Left: Active Record -->
  <g transform="translate(50, 60)">
    <rect width="320" height="260" class="box-ar"/>
    <text x="160" y="30" text-anchor="middle" class="text-title" fill="#58a6ff">Active Record (Rails, Django)</text>
    
    <rect x="20" y="55" width="280" height="70" class="box"/>
    <text x="160" y="80" text-anchor="middle" class="text-body" font-weight="bold">Об'єкт = Рядок таблиці + SQL логіка</text>
    <text x="160" y="105" text-anchor="middle" class="text-body" fill="#8b949e">user.name = 'Bob'; user.save();</text>

    <text x="30" y="160" class="text-body">• Простота та швидкий старт (CRUD)</text>
    <text x="30" y="190" class="text-body">• Зв'язок бізнес-домену з таблицею 1:1</text>
    <text x="30" y="220" class="text-body">• Складно тестувати без живий бази даних</text>
    <text x="160" y="250" text-anchor="middle" class="text-accent">Підходить для простих CRUD систем</text>
  </g>

  <!-- Right: Data Mapper -->
  <g transform="translate(430, 60)">
    <rect width="320" height="260" class="box-dm"/>
    <text x="160" y="30" text-anchor="middle" class="text-title" fill="#3fb950">Data Mapper (Hibernate, SQLAlchemy)</text>
    
    <rect x="20" y="55" width="130" height="70" class="box"/>
    <text x="85" y="85" text-anchor="middle" class="text-body" font-weight="bold">Чистий Домен</text>
    <text x="85" y="105" text-anchor="middle" class="text-body" fill="#8b949e">POCO / POJO</text>

    <rect x="170" y="55" width="130" height="70" class="box"/>
    <text x="235" y="85" text-anchor="middle" class="text-accent" font-weight="bold">Data Mapper</text>
    <text x="235" y="105" text-anchor="middle" class="text-body" fill="#8b949e">Unit of Work</text>

    <text x="30" y="160" class="text-body">• Повна ізоляція бізнес-моделі від БД</text>
    <text x="30" y="190" class="text-body">• Identity Map + Dirty Checking</text>
    <text x="30" y="220" class="text-body">• Легке юніт-тестування домену в пам'яті</text>
    <text x="160" y="250" text-anchor="middle" class="text-accent">Підходить для складного домену (DDD)</text>
  </g>
</svg>'''
    return svg

def generate_n_plus_one():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 360" width="100%" height="100%">
  <style>
    .bg { fill: #0d1117; }
    .box { fill: #161b22; stroke: #30363d; stroke-width: 1.5; rx: 6px; }
    .box-danger { fill: #2d1215; stroke: #f85149; stroke-width: 1.5; rx: 6px; }
    .box-safe { fill: #0e2a18; stroke: #3fb950; stroke-width: 1.5; rx: 6px; }
    .text-title { fill: #58a6ff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 14px; }
    .text-body { fill: #c9d1d9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 12px; }
    .text-danger { fill: #f85149; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 12px; }
    .text-safe { fill: #3fb950; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 12px; }
    .text-sub { fill: #8b949e; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 11px; }
  </style>

  <rect width="100%" height="100%" class="bg"/>
  <text x="400" y="30" text-anchor="middle" class="text-title">Анатомія проблеми N+1 запитів: Lazy Loading проти Eager Fetching</text>

  <!-- Left: N+1 Problem -->
  <g transform="translate(40, 60)">
    <rect width="340" height="260" class="box-danger"/>
    <text x="170" y="30" text-anchor="middle" class="text-danger">ПРОБЛЕМА N+1: Lazy Loading</text>
    
    <rect x="20" y="55" width="300" height="40" class="box"/>
    <text x="30" y="80" class="text-body">1. SELECT * FROM users; (1 запит)</text>
    
    <rect x="20" y="105" width="300" height="85" class="box-danger"/>
    <text x="30" y="125" class="text-danger">for (user in users) {</text>
    <text x="50" y="145" class="text-danger">  SELECT * FROM orders WHERE uid = ?;</text>
    <text x="30" y="165" class="text-danger">} -> N окремих запитів до мережі!</text>

    <text x="170" y="225" text-anchor="middle" class="text-danger">Загалом: 1 + 1000 = 1001 мережевий RTT</text>
    <text x="170" y="245" text-anchor="middle" class="text-sub">Катастрофічне зростання Latency</text>
  </g>

  <!-- Right: Eager Solution -->
  <g transform="translate(420, 60)">
    <rect width="340" height="260" class="box-safe"/>
    <text x="170" y="30" text-anchor="middle" class="text-safe">РІШЕННЯ: Eager Loading / JOIN</text>
    
    <rect x="20" y="55" width="300" height="60" class="box-safe"/>
    <text x="30" y="80" class="text-safe">SELECT * FROM users u</text>
    <text x="30" y="100" class="text-safe">LEFT JOIN orders o ON o.uid = u.id;</text>
    
    <rect x="20" y="130" width="300" height="60" class="box"/>
    <text x="30" y="155" class="text-body">Або Batch Fetching (2 запити):</text>
    <text x="30" y="175" class="text-body" fill="#3fb950">SELECT * FROM orders WHERE uid IN (...);</text>

    <text x="170" y="225" text-anchor="middle" class="text-safe">Загалом: 1 або 2 запити до бази</text>
    <text x="170" y="245" text-anchor="middle" class="text-sub">Мінімальне навантаження на мережу</text>
  </g>
</svg>'''
    return svg

def generate_unit_of_work():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 320" width="100%" height="100%">
  <style>
    .bg { fill: #0d1117; }
    .box { fill: #161b22; stroke: #30363d; stroke-width: 1.5; rx: 6px; }
    .box-uow { fill: #13271f; stroke: #3fb950; stroke-width: 1.5; rx: 6px; }
    .text-title { fill: #58a6ff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 14px; }
    .text-body { fill: #c9d1d9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 12px; }
    .text-accent { fill: #3fb950; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 12px; }
    .arrow { stroke: #58a6ff; stroke-width: 1.5; fill: none; marker-end: url(#arrowhead); }
  </style>
  <defs>
    <marker id="arrowhead" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="#58a6ff"/>
    </marker>
  </defs>

  <rect width="100%" height="100%" class="bg"/>
  <text x="400" y="30" text-anchor="middle" class="text-title">Життєвий цикл змін у Unit of Work (Identity Map + Dirty Checking)</text>

  <!-- Step 1: Query & Register -->
  <g transform="translate(40, 70)">
    <rect width="160" height="180" class="box"/>
    <text x="80" y="30" text-anchor="middle" class="text-title">1. Читання</text>
    <text x="80" y="60" text-anchor="middle" class="text-body">Identity Map</text>
    <text x="80" y="90" text-anchor="middle" class="text-body" fill="#8b949e">Збереження snapshot</text>
    <text x="80" y="110" text-anchor="middle" class="text-body" fill="#8b949e">початкового стану</text>
    <text x="80" y="140" text-anchor="middle" class="text-accent">Кеш L1</text>
  </g>

  <line x1="200" y1="160" x2="230" y2="160" class="arrow"/>

  <!-- Step 2: In-memory mutation -->
  <g transform="translate(230, 70)">
    <rect width="160" height="180" class="box"/>
    <text x="80" y="30" text-anchor="middle" class="text-title">2. Модифікація</text>
    <text x="80" y="60" text-anchor="middle" class="text-body">user.email = '...'</text>
    <text x="80" y="90" text-anchor="middle" class="text-body" fill="#8b949e">Зміни в пам'яті</text>
    <text x="80" y="110" text-anchor="middle" class="text-body" fill="#8b949e">без запитів до БД</text>
    <text x="80" y="140" text-anchor="middle" class="text-accent">Нуль I/O</text>
  </g>

  <line x1="390" y1="160" x2="420" y2="160" class="arrow"/>

  <!-- Step 3: Dirty Checking -->
  <g transform="translate(420, 70)">
    <rect width="160" height="180" class="box-uow"/>
    <text x="80" y="30" text-anchor="middle" class="text-accent">3. Dirty Check</text>
    <text x="80" y="60" text-anchor="middle" class="text-body">Порівняння</text>
    <text x="80" y="90" text-anchor="middle" class="text-body" fill="#8b949e">поточного стану з</text>
    <text x="80" y="110" text-anchor="middle" class="text-body" fill="#8b949e">початковим знімком</text>
    <text x="80" y="140" text-anchor="middle" class="text-accent">План DML</text>
  </g>

  <line x1="580" y1="160" x2="610" y2="160" class="arrow"/>

  <!-- Step 4: Batch Flush -->
  <g transform="translate(610, 70)">
    <rect width="160" height="180" class="box"/>
    <text x="80" y="30" text-anchor="middle" class="text-title">4. Flush / Commit</text>
    <text x="80" y="60" text-anchor="middle" class="text-body">Топологічне</text>
    <text x="80" y="90" text-anchor="middle" class="text-body" fill="#8b949e">впорядкування</text>
    <text x="80" y="110" text-anchor="middle" class="text-body" fill="#8b949e">батч INSERT/UPDATE</text>
    <text x="80" y="140" text-anchor="middle" class="text-accent">1 транзакція</text>
  </g>
</svg>'''
    return svg

def main():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    
    files = {
        "object-relational-impedance.svg": generate_impedance_mismatch(),
        "active-record-vs-data-mapper.svg": generate_active_record_vs_data_mapper(),
        "n-plus-one-problem.svg": generate_n_plus_one(),
        "unit-of-work-lifecycle.svg": generate_unit_of_work()
    }
    
    for filename, content in files.items():
        filepath = os.path.join(img_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Generated {filepath}")

if __name__ == "__main__":
    main()

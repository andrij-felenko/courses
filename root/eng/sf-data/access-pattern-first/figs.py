"""Generate technical SVG diagrams for Access-Pattern-First Modeling."""
import os
import sys

def generate_relational_vs_access_pattern():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 360" width="100%" height="100%">
  <style>
    .bg { fill: #0d1117; }
    .box { fill: #161b22; stroke: #30363d; stroke-width: 1.5; rx: 6px; }
    .box-rel { fill: #1a2332; stroke: #58a6ff; stroke-width: 1.5; rx: 6px; }
    .box-apf { fill: #13271f; stroke: #3fb950; stroke-width: 1.5; rx: 6px; }
    .text-title { fill: #58a6ff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 14px; }
    .text-body { fill: #c9d1d9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 12px; }
    .text-sub { fill: #8b949e; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 11px; }
    .text-accent { fill: #3fb950; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 12px; }
  </style>

  <rect width="100%" height="100%" class="bg"/>
  <text x="400" y="30" text-anchor="middle" class="text-title">Реляційне моделювання (ER) проти Access-Pattern-First</text>

  <!-- Left: Relational ER Model -->
  <g transform="translate(40, 60)">
    <rect width="330" height="260" class="box-rel"/>
    <text x="165" y="30" text-anchor="middle" class="text-title" fill="#58a6ff">1. Реляційний підхід (Entity-First)</text>
    
    <rect x="25" y="55" width="280" height="40" class="box"/>
    <text x="165" y="80" text-anchor="middle" class="text-body">Крок 1: Нормалізація сутностей (3NF)</text>
    
    <rect x="25" y="105" width="280" height="40" class="box"/>
    <text x="165" y="130" text-anchor="middle" class="text-body">Крок 2: Зв'язки через Foreign Keys</text>

    <text x="35" y="175" class="text-body">• Питання: «Як виглядають дані?»</text>
    <text x="35" y="200" class="text-body">• Гнучкі довільні SQL-запити через JOIN</text>
    <text x="35" y="225" class="text-body">• Запити конструюються після створення схеми</text>
    <text x="165" y="250" text-anchor="middle" class="text-sub">Ціна: Важкі JOIN при масштабуванні</text>
  </g>

  <!-- Right: Access Pattern First -->
  <g transform="translate(430, 60)">
    <rect width="330" height="260" class="box-apf"/>
    <text x="165" y="30" text-anchor="middle" class="text-title" fill="#3fb950">2. NoSQL (Access-Pattern-First)</text>
    
    <rect x="25" y="55" width="280" height="40" class="box"/>
    <text x="165" y="80" text-anchor="middle" class="text-body">Крок 1: Перелік УСІХ запитів бізнесу</text>
    
    <rect x="25" y="105" width="280" height="40" class="box"/>
    <text x="165" y="130" text-anchor="middle" class="text-body">Крок 2: 1 таблиця на 1 патерн вибірки</text>

    <text x="35" y="175" class="text-body">• Питання: «Як дані будуть ЧИТАТИСЯ?»</text>
    <text x="35" y="200" class="text-body">• Повна денормалізація заради O(1) вибірки</text>
    <text x="35" y="225" class="text-body">• Заборонено створювати таблицю без запиту</text>
    <text x="165" y="250" text-anchor="middle" class="text-accent">Результат: Константна затримка при масштабуванні</text>
  </g>
</svg>'''
    return svg

def generate_single_table_design():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 360" width="100%" height="100%">
  <style>
    .bg { fill: #0d1117; }
    .box { fill: #161b22; stroke: #30363d; stroke-width: 1.5; rx: 6px; }
    .text-title { fill: #58a6ff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 14px; }
    .text-body { fill: #c9d1d9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 11px; }
    .text-pk { fill: #58a6ff; font-family: "Courier New", monospace; font-weight: bold; font-size: 11px; }
    .text-sk { fill: #3fb950; font-family: "Courier New", monospace; font-weight: bold; font-size: 11px; }
    .text-val { fill: #d29922; font-family: "Courier New", monospace; font-size: 11px; }
    .header-row { fill: #1f2937; }
  </style>

  <rect width="100%" height="100%" class="bg"/>
  <text x="400" y="30" text-anchor="middle" class="text-title">DynamoDB Single Table Design: Перевантаження ключів (Key Overloading)</text>

  <!-- Table View -->
  <g transform="translate(50, 60)">
    <!-- Header -->
    <rect width="700" height="35" class="header-row"/>
    <rect width="700" height="230" fill="none" stroke="#30363d" stroke-width="1.5" rx="4"/>
    
    <text x="70" y="22" text-anchor="middle" class="text-title" fill="#58a6ff">Partition Key (PK)</text>
    <text x="230" y="22" text-anchor="middle" class="text-title" fill="#3fb950">Sort Key (SK)</text>
    <text x="390" y="22" text-anchor="middle" class="text-body" font-weight="bold">Type</text>
    <text x="560" y="22" text-anchor="middle" class="text-body" font-weight="bold">Attributes (Payload)</text>
    
    <!-- Row 1: User metadata -->
    <line x1="0" y1="35" x2="700" y2="35" stroke="#30363d"/>
    <text x="70" y="60" text-anchor="middle" class="text-pk">USER#1001</text>
    <text x="230" y="60" text-anchor="middle" class="text-sk">#METADATA</text>
    <text x="390" y="60" text-anchor="middle" class="text-body">User</text>
    <text x="560" y="60" text-anchor="middle" class="text-val">{"name": "Alex", "email": "a@ex.com"}</text>

    <!-- Row 2: User order 1 -->
    <line x1="0" y1="80" x2="700" y2="80" stroke="#30363d"/>
    <text x="70" y="105" text-anchor="middle" class="text-pk">USER#1001</text>
    <text x="230" y="105" text-anchor="middle" class="text-sk">ORDER#2024#001</text>
    <text x="390" y="105" text-anchor="middle" class="text-body">Order</text>
    <text x="560" y="105" text-anchor="middle" class="text-val">{"total": 149.50, "status": "PAID"}</text>

    <!-- Row 3: User order 2 -->
    <line x1="0" y1="125" x2="700" y2="125" stroke="#30363d"/>
    <text x="70" y="150" text-anchor="middle" class="text-pk">USER#1001</text>
    <text x="230" y="150" text-anchor="middle" class="text-sk">ORDER#2024#002</text>
    <text x="390" y="150" text-anchor="middle" class="text-body">Order</text>
    <text x="560" y="150" text-anchor="middle" class="text-val">{"total": 89.00, "status": "PENDING"}</text>

    <!-- Row 4: User address -->
    <line x1="0" y1="170" x2="700" y2="170" stroke="#30363d"/>
    <text x="70" y="195" text-anchor="middle" class="text-pk">USER#1001</text>
    <text x="230" y="195" text-anchor="middle" class="text-sk">ADDR#HOME</text>
    <text x="390" y="195" text-anchor="middle" class="text-body">Address</text>
    <text x="560" y="195" text-anchor="middle" class="text-val">{"city": "Kyiv", "street": "Khreshchatyk"}</text>
  </g>

  <text x="400" y="325" text-anchor="middle" class="text-body" fill="#3fb950">1 запит Query(PK="USER#1001") повертає профіль, усі замовлення та адреси без жодного JOIN!</text>
</svg>'''
    return svg

def generate_cassandra_clustering():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 360" width="100%" height="100%">
  <style>
    .bg { fill: #0d1117; }
    .box { fill: #161b22; stroke: #30363d; stroke-width: 1.5; rx: 6px; }
    .box-pk { fill: #1a2332; stroke: #58a6ff; stroke-width: 1.5; rx: 6px; }
    .text-title { fill: #58a6ff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 14px; }
    .text-body { fill: #c9d1d9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 12px; }
    .text-code { fill: #d29922; font-family: "Courier New", monospace; font-size: 12px; }
    .text-accent { fill: #3fb950; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 12px; }
  </style>

  <rect width="100%" height="100%" class="bg"/>
  <text x="400" y="30" text-anchor="middle" class="text-title">Cassandra: Partition Key (Розподіл) та Clustering Columns (Сортування)</text>

  <!-- Node Hash Ring Routing -->
  <g transform="translate(60, 60)">
    <rect width="320" height="250" class="box-pk"/>
    <text x="160" y="30" text-anchor="middle" class="text-title" fill="#58a6ff">1. Partition Key (Шардування)</text>
    
    <rect x="20" y="55" width="280" height="50" class="box"/>
    <text x="160" y="75" text-anchor="middle" class="text-code">PK: sensor_id = 'S-42'</text>
    <text x="160" y="95" text-anchor="middle" class="text-body">Murmur3Partitioner -> Вузол №3</text>

    <text x="30" y="145" class="text-body">• Визначає, на який сервер летять дані</text>
    <text x="30" y="170" class="text-body">• Гарантує локальність однієї сутності</text>
    <text x="30" y="195" class="text-body">• Виключає розподілений перебір вузлів</text>
    <text x="160" y="230" text-anchor="middle" class="text-accent">Точковий роутинг за O(1)</text>
  </g>

  <!-- On-disk Sorted SSTable Rows -->
  <g transform="translate(420, 60)">
    <rect width="320" height="250" class="box"/>
    <text x="160" y="30" text-anchor="middle" class="text-title" fill="#3fb950">2. Clustering Key (Дисковий порядок)</text>
    
    <rect x="20" y="55" width="280" height="60" class="box" stroke="#3fb950"/>
    <text x="160" y="75" text-anchor="middle" class="text-code">CLUSTERING ORDER BY (ts DESC)</text>
    <text x="160" y="95" text-anchor="middle" class="text-body">Рядки лежать на диску відсортовано!</text>

    <text x="30" y="145" class="text-body">• Миттєвий діапазонний пошук (Slice)</text>
    <text x="30" y="170" class="text-body">• WHERE sensor_id='S-42' AND ts > t1</text>
    <text x="30" y="195" class="text-body">• Послідовне читання без сортування в RAM</text>
    <text x="160" y="230" text-anchor="middle" class="text-accent">Ідеально для Time-Series та IoT</text>
  </g>
</svg>'''
    return svg

def main():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    
    files = {
        "relational-vs-access-pattern.svg": generate_relational_vs_access_pattern(),
        "single-table-design-dynamodb.svg": generate_single_table_design(),
        "cassandra-clustering-keys.svg": generate_cassandra_clustering()
    }
    
    for filename, content in files.items():
        filepath = os.path.join(img_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Generated {filepath}")

if __name__ == "__main__":
    main()

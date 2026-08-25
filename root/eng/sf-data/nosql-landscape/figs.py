"""Generate technical SVG diagrams for NoSQL Landscape."""
import os
import sys

def generate_four_models():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 360" width="100%" height="100%">
  <style>
    .bg { fill: #0d1117; }
    .box { fill: #161b22; stroke: #30363d; stroke-width: 1.5; rx: 6px; }
    .box-kv { fill: #1a2332; stroke: #58a6ff; stroke-width: 1.5; rx: 6px; }
    .box-doc { fill: #13271f; stroke: #3fb950; stroke-width: 1.5; rx: 6px; }
    .box-col { fill: #2b2216; stroke: #d29922; stroke-width: 1.5; rx: 6px; }
    .box-graph { fill: #261b2d; stroke: #bc8cff; stroke-width: 1.5; rx: 6px; }
    .text-title { fill: #58a6ff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 13px; }
    .text-body { fill: #c9d1d9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 11px; }
    .text-sub { fill: #8b949e; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 10px; }
  </style>

  <rect width="100%" height="100%" class="bg"/>
  <text x="400" y="25" text-anchor="middle" class="text-title" font-size="15">Чотири базові моделі даних NoSQL</text>

  <!-- 1. Key-Value -->
  <g transform="translate(30, 45)">
    <rect width="170" height="290" class="box-kv"/>
    <text x="85" y="25" text-anchor="middle" class="text-title" fill="#58a6ff">1. Key-Value</text>
    <text x="85" y="45" text-anchor="middle" class="text-sub">Redis, DynamoDB</text>
    
    <rect x="15" y="65" width="140" height="70" class="box"/>
    <text x="85" y="90" text-anchor="middle" class="text-body" fill="#58a6ff">"user:101"</text>
    <text x="85" y="115" text-anchor="middle" class="text-body">-> "0xAF312..."</text>

    <text x="20" y="160" class="text-body">• Прямий доступ O(1)</text>
    <text x="20" y="185" class="text-body">• Простий CRUD за ключем</text>
    <text x="20" y="210" class="text-body">• Кешування, сесії</text>
    <text x="85" y="260" text-anchor="middle" class="text-body" fill="#3fb950">Максимальний RPS</text>
  </g>

  <!-- 2. Document -->
  <g transform="translate(220, 45)">
    <rect width="170" height="290" class="box-doc"/>
    <text x="85" y="25" text-anchor="middle" class="text-title" fill="#3fb950">2. Document</text>
    <text x="85" y="45" text-anchor="middle" class="text-sub">MongoDB, Couchbase</text>
    
    <rect x="15" y="65" width="140" height="70" class="box"/>
    <text x="85" y="85" text-anchor="middle" class="text-body" fill="#3fb950">{ id: 101,</text>
    <text x="85" y="105" text-anchor="middle" class="text-body">  name: "Alex",</text>
    <text x="85" y="125" text-anchor="middle" class="text-body">  tags: [...] }</text>

    <text x="20" y="160" class="text-body">• Вкладені JSON/BSON</text>
    <text x="20" y="185" class="text-body">• Гнучка динамічна схема</text>
    <text x="20" y="210" class="text-body">• Вторинні індекси</text>
    <text x="85" y="260" text-anchor="middle" class="text-body" fill="#3fb950">Ієрархічні дані</text>
  </g>

  <!-- 3. Wide-Column -->
  <g transform="translate(410, 45)">
    <rect width="170" height="290" class="box-col"/>
    <text x="85" y="25" text-anchor="middle" class="text-title" fill="#d29922">3. Wide-Column</text>
    <text x="85" y="45" text-anchor="middle" class="text-sub">Cassandra, ScyllaDB</text>
    
    <rect x="15" y="65" width="140" height="70" class="box"/>
    <text x="85" y="85" text-anchor="middle" class="text-body" fill="#d29922">Row: "sensor_42"</text>
    <text x="85" y="105" text-anchor="middle" class="text-body">t1: 22.4 | t2: 22.5</text>
    <text x="85" y="125" text-anchor="middle" class="text-body">t3: 22.8 | ...</text>

    <text x="20" y="160" class="text-body">• Мільярди колонок</text>
    <text x="20" y="185" class="text-body">• Розподілене сортування</text>
    <text x="20" y="210" class="text-body">• Часові ряди, IoT</text>
    <text x="85" y="260" text-anchor="middle" class="text-body" fill="#3fb950">Високий Write Rate</text>
  </g>

  <!-- 4. Graph -->
  <g transform="translate(600, 45)">
    <rect width="170" height="290" class="box-graph"/>
    <text x="85" y="25" text-anchor="middle" class="text-title" fill="#bc8cff">4. Graph</text>
    <text x="85" y="45" text-anchor="middle" class="text-sub">Neo4j, Amazon Neptune</text>
    
    <rect x="15" y="65" width="140" height="70" class="box"/>
    <circle cx="45" cy="100" r="14" fill="#1f2937" stroke="#bc8cff"/>
    <text x="45" y="104" text-anchor="middle" class="text-body">A</text>
    <line x1="59" y1="100" x2="111" y2="100" stroke="#bc8cff" stroke-width="1.5"/>
    <circle cx="125" cy="100" r="14" fill="#1f2937" stroke="#bc8cff"/>
    <text x="125" y="104" text-anchor="middle" class="text-body">B</text>

    <text x="20" y="160" class="text-body">• Вершини та ребра</text>
    <text x="20" y="185" class="text-body">• Безблокувальний обхід</text>
    <text x="20" y="210" class="text-body">• Соцмережі, антифрод</text>
    <text x="85" y="260" text-anchor="middle" class="text-body" fill="#3fb950">Складні зв'язки</text>
  </g>
</svg>'''
    return svg

def generate_cap_theorem():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 360" width="100%" height="100%">
  <style>
    .bg { fill: #0d1117; }
    .box { fill: #161b22; stroke: #30363d; stroke-width: 1.5; rx: 6px; }
    .text-title { fill: #58a6ff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 14px; }
    .text-body { fill: #c9d1d9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 12px; }
    .text-accent { fill: #3fb950; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 12px; }
    .text-warn { fill: #d29922; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: bold; font-size: 12px; }
    .circle-c { fill: rgba(88, 166, 255, 0.15); stroke: #58a6ff; stroke-width: 2; }
    .circle-a { fill: rgba(63, 185, 80, 0.15); stroke: #3fb950; stroke-width: 2; }
    .circle-p { fill: rgba(210, 153, 34, 0.15); stroke: #d29922; stroke-width: 2; }
  </style>

  <rect width="100%" height="100%" class="bg"/>
  <text x="400" y="30" text-anchor="middle" class="text-title">Теорема CAP та класифікація розподілених сховищ</text>

  <!-- Triangle Diagram with overlapping circles -->
  <g transform="translate(180, 50)">
    <!-- Circle C: Consistency -->
    <circle cx="220" cy="80" r="90" class="circle-c"/>
    <text x="220" y="30" text-anchor="middle" class="text-title" fill="#58a6ff">C (Consistency)</text>
    <text x="220" y="50" text-anchor="middle" class="text-body">Усі вузли бачать</text>
    <text x="220" y="65" text-anchor="middle" class="text-body">однакові дані</text>

    <!-- Circle A: Availability -->
    <circle cx="140" cy="180" r="90" class="circle-a"/>
    <text x="90" y="215" text-anchor="middle" class="text-accent">A (Availability)</text>
    <text x="90" y="235" text-anchor="middle" class="text-body">Завжди повертає</text>
    <text x="90" y="250" text-anchor="middle" class="text-body">відповідь без помилок</text>

    <!-- Circle P: Partition Tolerance -->
    <circle cx="300" cy="180" r="90" class="circle-p"/>
    <text x="350" y="215" text-anchor="middle" class="text-warn">P (Partition Tolerance)</text>
    <text x="350" y="235" text-anchor="middle" class="text-body">Стійкість до</text>
    <text x="350" y="250" text-anchor="middle" class="text-body">обриву мережі</text>

    <!-- Intersections -->
    <!-- CP: MongoDB, HBase, Redis Cluster -->
    <rect x="225" y="115" width="80" height="40" class="box" stroke="#58a6ff"/>
    <text x="265" y="130" text-anchor="middle" class="text-body" font-weight="bold">CP</text>
    <text x="265" y="145" text-anchor="middle" class="text-sub" font-size="9" fill="#8b949e">MongoDB, HBase</text>

    <!-- AP: Cassandra, DynamoDB, CouchDB -->
    <rect x="180" y="200" width="80" height="40" class="box" stroke="#3fb950"/>
    <text x="220" y="215" text-anchor="middle" class="text-body" font-weight="bold">AP</text>
    <text x="220" y="230" text-anchor="middle" class="text-sub" font-size="9" fill="#8b949e">Cassandra, Dynamo</text>

    <!-- CA (RDBMS non-distributed) -->
    <rect x="135" y="115" width="80" height="40" class="box" stroke="#bc8cff"/>
    <text x="175" y="130" text-anchor="middle" class="text-body" font-weight="bold">CA*</text>
    <text x="175" y="145" text-anchor="middle" class="text-sub" font-size="9" fill="#8b949e">RDBMS (один вузол)</text>
  </g>

  <text x="400" y="335" text-anchor="middle" class="text-body" fill="#8b949e">*У розподілених мережах обрив зв'язку (P) неминучий, тому вибір зводиться до компромісу між CP та AP</text>
</svg>'''
    return svg

def generate_lsm_vs_btree():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 360" width="100%" height="100%">
  <style>
    .bg { fill: #0d1117; }
    .box { fill: #161b22; stroke: #30363d; stroke-width: 1.5; rx: 6px; }
    .box-lsm { fill: #1a2332; stroke: #58a6ff; stroke-width: 1.5; rx: 6px; }
    .box-btree { fill: #261b2d; stroke: #bc8cff; stroke-width: 1.5; rx: 6px; }
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
  <text x="400" y="30" text-anchor="middle" class="text-title">Рушії зберігання: LSM-Tree (NoSQL) проти B+Tree (RDBMS)</text>

  <!-- Left: LSM-Tree -->
  <g transform="translate(50, 60)">
    <rect width="320" height="260" class="box-lsm"/>
    <text x="160" y="30" text-anchor="middle" class="text-title" fill="#58a6ff">LSM-Tree (Cassandra, RocksDB)</text>
    
    <rect x="20" y="55" width="280" height="40" class="box"/>
    <text x="160" y="80" text-anchor="middle" class="text-body">1. MemTable (Пам'ять) + WAL</text>
    
    <rect x="20" y="105" width="280" height="40" class="box"/>
    <text x="160" y="130" text-anchor="middle" class="text-body">2. SSTables L0, L1, L2 (Послідовний запис)</text>

    <text x="30" y="175" class="text-body">• Запис: Послідовний (Sequential I/O)</text>
    <text x="30" y="200" class="text-body">• Фонова Compaction зливає рівні</text>
    <text x="30" y="225" class="text-body">• Bloom-фільтри для швидкого пошуку</text>
    <text x="160" y="250" text-anchor="middle" class="text-accent">Оптимізовано для інтенсивного запису</text>
  </g>

  <!-- Right: B+Tree -->
  <g transform="translate(430, 60)">
    <rect width="320" height="260" class="box-btree"/>
    <text x="160" y="30" text-anchor="middle" class="text-title" fill="#bc8cff">B+Tree (PostgreSQL, InnoDB)</text>
    
    <rect x="20" y="55" width="280" height="40" class="box"/>
    <text x="160" y="80" text-anchor="middle" class="text-body">1. Buffer Pool (Кеш сторінок 8KB/16KB)</text>
    
    <rect x="20" y="105" width="280" height="40" class="box"/>
    <text x="160" y="130" text-anchor="middle" class="text-body">2. Модифікація сторінок на місці (In-place)</text>

    <text x="30" y="175" class="text-body">• Читання: Константна глибина O(log N)</text>
    <text x="30" y="200" class="text-body">• Випадковий запис (Random I/O)</text>
    <text x="30" y="225" class="text-body">• Подвійний запис для захисту від torn pages</text>
    <text x="160" y="250" text-anchor="middle" class="text-accent">Оптимізовано для швидкого точкового читання</text>
  </g>
</svg>'''
    return svg

def main():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    
    files = {
        "nosql-four-models.svg": generate_four_models(),
        "cap-theorem-tradeoffs.svg": generate_cap_theorem(),
        "lsm-tree-vs-btree.svg": generate_lsm_vs_btree()
    }
    
    for filename, content in files.items():
        filepath = os.path.join(img_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Generated {filepath}")

if __name__ == "__main__":
    main()

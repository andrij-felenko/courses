import os

def generate_svgs():
    topic_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = os.path.join(topic_dir, "img")
    os.makedirs(img_dir, exist_ok=True)

    # 1. gso-tso.svg
    gso_tso_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 420" width="100%" height="100%">
  <style>
    .bg { fill: #ffffff; }
    .box-kernel { fill: #f1f3f5; stroke: #495057; stroke-width: 2; rx: 8px; }
    .box-driver { fill: #e7f5ff; stroke: #1971c2; stroke-width: 2; rx: 8px; }
    .box-nic { fill: #ebfbee; stroke: #2b8a3e; stroke-width: 2; rx: 8px; }
    .title { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 16px; font-weight: bold; fill: #212529; }
    .subtitle { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; fill: #495057; }
    .text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 13px; fill: #212529; }
    .text-sm { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 11px; fill: #495057; }
    .text-bold { font-weight: bold; }
    .badge { fill: #1c7ed6; font-size: 11px; fill: #ffffff; font-weight: bold; }
    .badge-gso { fill: #d9480f; }
    .badge-tso { fill: #2b8a3e; }
    .arrow { stroke: #343a40; stroke-width: 2; marker-end: url(#arrowhead); }
    .arrow-dash { stroke: #d9480f; stroke-width: 2; stroke-dasharray: 4,4; marker-end: url(#arrowhead-orange); }
    .packet-large { fill: #d0ebff; stroke: #1971c2; stroke-width: 1.5; rx: 4px; }
    .packet-small { fill: #d3f9d8; stroke: #2b8a3e; stroke-width: 1.5; rx: 3px; }
  </style>

  <defs>
    <marker id="arrowhead" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="#343a40" />
    </marker>
    <marker id="arrowhead-orange" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="#d9480f" />
    </marker>
  </defs>

  <rect width="100%" height="100%" class="bg" />

  <!-- Title -->
  <text x="450" y="28" text-anchor="middle" class="title">Конвеєр відправки даних (TX): TCP/IP Стек -> GSO -> TSO -> Дріт</text>

  <!-- Step 1: Userspace & Kernel Sock Buffer -->
  <rect x="30" y="55" width="240" height="340" class="box-kernel" />
  <text x="150" y="80" text-anchor="middle" class="title">Стек ядра Linux</text>
  <text x="150" y="98" text-anchor="middle" class="subtitle">Socket Layer &amp; TCP/IP Stack</text>

  <rect x="50" y="120" width="200" height="70" class="packet-large" />
  <text x="150" y="145" text-anchor="middle" class="text text-bold">Супер-пакет (sk_buff)</text>
  <text x="150" y="165" text-anchor="middle" class="text-sm">Розмір до 64 КБ (65535 B)</text>
  <text x="150" y="180" text-anchor="middle" class="text-sm">gso_size = 1460, gso_type = SKB_GSO_TCPV4</text>

  <rect x="50" y="210" width="200" height="60" fill="#fff" stroke="#adb5bd" rx="4" />
  <text x="150" y="235" text-anchor="middle" class="text">Обхід Netfilter / TC / Routing</text>
  <text x="150" y="252" text-anchor="middle" class="text-sm">Виконується 1 раз на 64 КБ</text>

  <rect x="50" y="290" width="200" height="80" fill="#ffe3e3" stroke="#e03131" rx="4" />
  <text x="150" y="312" text-anchor="middle" class="text text-bold">TX Checksum Offload</text>
  <text x="150" y="330" text-anchor="middle" class="text-sm">CHECKSUM_PARTIAL</text>
  <text x="150" y="348" text-anchor="middle" class="text-sm">csum_start / csum_offset вказані</text>

  <!-- Arrow to Driver/Software GSO -->
  <path d="M 270 225 L 320 225" class="arrow" />

  <!-- Step 2: GSO Layer -->
  <rect x="325" y="55" width="250" height="340" class="box-driver" />
  <text x="450" y="80" text-anchor="middle" class="title">Драйвер &amp; GSO Fallback</text>
  <text x="450" y="98" text-anchor="middle" class="subtitle">dev_hard_start_xmit() / validate_xmit_skb()</text>

  <rect x="345" y="125" width="210" height="110" fill="#fff" stroke="#1971c2" rx="6" />
  <text x="450" y="148" text-anchor="middle" class="text text-bold">Перевірка підтримки TSO</text>
  <text x="450" y="170" text-anchor="middle" class="text-sm">Якщо NIC підтримує NETIF_F_TSO:</text>
  <text x="450" y="188" text-anchor="middle" class="text-sm text-bold" fill="#2b8a3e">-> Передача 64 KB пакета на NIC</text>
  <text x="450" y="210" text-anchor="middle" class="text-sm">Якщо TSO вимкнено або відсутній:</text>
  <text x="450" y="225" text-anchor="middle" class="text-sm text-bold" fill="#d9480f">-> Виклик skb_segment() (Програмний GSO)</text>

  <rect x="345" y="255" width="210" height="120" fill="#fff4e6" stroke="#d9480f" rx="6" />
  <text x="450" y="278" text-anchor="middle" class="text text-bold" fill="#d9480f">GSO Software Segmentation</text>
  <text x="450" y="298" text-anchor="middle" class="text-sm">Розбиття skb на ~44 пакети по MTU</text>
  <text x="450" y="316" text-anchor="middle" class="text-sm">Програмний розрахунок TCP Seq No</text>
  <text x="450" y="334" text-anchor="middle" class="text-sm">Програмне обчислення Checksum</text>
  <text x="450" y="352" text-anchor="middle" class="text-sm">Передача кільцю DMA NIC</text>

  <!-- Arrow to Hardware NIC -->
  <path d="M 575 180 L 625 180" class="arrow" />
  <path d="M 575 315 L 625 315" class="arrow-dash" />

  <!-- Step 3: Hardware NIC -->
  <rect x="630" y="55" width="240" height="340" class="box-nic" />
  <text x="750" y="80" text-anchor="middle" class="title">Мережева карта (NIC)</text>
  <text x="750" y="98" text-anchor="middle" class="subtitle">Hardware DMA &amp; PHY Engine</text>

  <rect x="650" y="125" width="200" height="110" fill="#d3f9d8" stroke="#2b8a3e" rx="6" />
  <text x="750" y="150" text-anchor="middle" class="text text-bold" fill="#2b8a3e">Hardware TSO Engine</text>
  <text x="750" y="170" text-anchor="middle" class="text-sm">Розщеплення 64 KB -> MSS (1460B)</text>
  <text x="750" y="188" text-anchor="middle" class="text-sm">Генерація IP ID та TCP Seq/Ack</text>
  <text x="750" y="206" text-anchor="middle" class="text-sm">Апаратне обчислення L3/L4 Checksum</text>
  <text x="750" y="222" text-anchor="middle" class="text-sm">Формування Ethernet CRC32</text>

  <!-- Small packets output -->
  <g transform="translate(660, 260)">
    <rect x="0" y="0" width="50" height="40" class="packet-small" />
    <text x="25" y="24" text-anchor="middle" class="text-sm">1500B</text>
    <rect x="65" y="0" width="50" height="40" class="packet-small" />
    <text x="90" y="24" text-anchor="middle" class="text-sm">1500B</text>
    <rect x="130" y="0" width="50" height="40" class="packet-small" />
    <text x="155" y="24" text-anchor="middle" class="text-sm">1500B</text>
  </g>
  <text x="750" y="325" text-anchor="middle" class="text-sm text-bold">Потік кадрів у фізичний кабель (PHY)</text>
  <text x="750" y="345" text-anchor="middle" class="text-sm">148.8 Mpps на 100 GbE без навантаження CPU</text>

</svg>"""

    # 2. gro-lro.svg
    gro_lro_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 420" width="100%" height="100%">
  <style>
    .bg { fill: #ffffff; }
    .box-phy { fill: #e9ecef; stroke: #495057; stroke-width: 2; rx: 8px; }
    .box-lro { fill: #ffe3e3; stroke: #e03131; stroke-width: 2; rx: 8px; }
    .box-gro { fill: #e7f5ff; stroke: #1971c2; stroke-width: 2; rx: 8px; }
    .title { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 16px; font-weight: bold; fill: #212529; }
    .subtitle { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; fill: #495057; }
    .text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 13px; fill: #212529; }
    .text-sm { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 11px; fill: #495057; }
    .text-bold { font-weight: bold; }
    .arrow { stroke: #343a40; stroke-width: 2; marker-end: url(#arrowhead); }
    .packet-small { fill: #fff3bf; stroke: #f59f00; stroke-width: 1.5; rx: 3px; }
    .packet-merged { fill: #d0ebff; stroke: #1971c2; stroke-width: 1.5; rx: 4px; }
    .packet-broken { fill: #ffc9c9; stroke: #e03131; stroke-width: 1.5; rx: 4px; }
  </style>

  <defs>
    <marker id="arrowhead" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="#343a40" />
    </marker>
  </defs>

  <rect width="100%" height="100%" class="bg" />

  <!-- Title -->
  <text x="450" y="28" text-anchor="middle" class="title">Прийом пакетів (RX): Апаратний LRO проти Програмного GRO у NAPI</text>

  <!-- Physical Packets Incoming -->
  <rect x="30" y="60" width="180" height="330" class="box-phy" />
  <text x="120" y="85" text-anchor="middle" class="title">Фізичний потік (RX)</text>
  <text x="120" y="103" text-anchor="middle" class="subtitle">Потік MTU-кадрів (1500B)</text>

  <g transform="translate(50, 120)">
    <rect x="0" y="0" width="140" height="35" class="packet-small" />
    <text x="70" y="22" text-anchor="middle" class="text-sm">Packet #1 (Seq 1..1460)</text>
    <rect x="0" y="45" width="140" height="35" class="packet-small" />
    <text x="70" y="67" text-anchor="middle" class="text-sm">Packet #2 (Seq 1461..2920)</text>
    <rect x="0" y="90" width="140" height="35" class="packet-small" />
    <text x="70" y="112" text-anchor="middle" class="text-sm">Packet #3 (Seq 2921..4380)</text>
    <rect x="0" y="135" width="140" height="35" class="packet-small" />
    <text x="70" y="157" text-anchor="middle" class="text-sm">Packet #4 (Seq 4381..5840)</text>
  </g>

  <text x="120" y="325" text-anchor="middle" class="text-sm">Тисячі переривань/сек</text>
  <text x="120" y="345" text-anchor="middle" class="text-sm">Високе навантаження CPU без GRO/LRO</text>

  <!-- LRO Architecture (Top Right) -->
  <rect x="250" y="60" width="620" height="155" class="box-lro" />
  <text x="560" y="85" text-anchor="middle" class="title" fill="#c92a2a">Апаратний LRO (Large Receive Offload) - Руйнівний для Forwarding</text>
  
  <rect x="270" y="100" width="260" height="95" fill="#fff" stroke="#e03131" rx="4" />
  <text x="400" y="120" text-anchor="middle" class="text text-bold">Агрегація на контролері NIC</text>
  <text x="400" y="138" text-anchor="middle" class="text-sm">• Об'єднує TCP дані у 64 KB</text>
  <text x="400" y="154" text-anchor="middle" class="text-sm">• ВТРАЧАЄ точні IP TTL, TOS, ECN</text>
  <text x="400" y="170" text-anchor="middle" class="text-sm">• ВТРАЧАЄ варіанти TCP заголовків (Timestamps)</text>
  <text x="400" y="186" text-anchor="middle" class="text-sm text-bold" fill="#e03131">НЕБЕЗПЕЧНО ДЛЯ ROUTING / BRIDGING!</text>

  <rect x="560" y="105" width="290" height="85" class="packet-broken" />
  <text x="705" y="130" text-anchor="middle" class="text text-bold" fill="#c92a2a">Злитий LRO-пакет</text>
  <text x="705" y="150" text-anchor="middle" class="text-sm">Заголовки переписані апаратурою</text>
  <text x="705" y="170" text-anchor="middle" class="text-sm">Повторне розбиття при маршрутизації зіпсоване</text>

  <!-- GRO Architecture (Bottom Right) -->
  <rect x="250" y="235" width="620" height="155" class="box-gro" />
  <text x="560" y="260" text-anchor="middle" class="title" fill="#1864ab">Програмний GRO (Generic Receive Offload) у NAPI - Безпечний і Універсальний</text>

  <rect x="270" y="275" width="260" height="95" fill="#fff" stroke="#1971c2" rx="4" />
  <text x="400" y="295" text-anchor="middle" class="text text-bold">NAPI Polling Loop (napi_gro_receive)</text>
  <text x="400" y="313" text-anchor="middle" class="text-sm">• Строга перевірка інваріантів IP/TCP</text>
  <text x="400" y="329" text-anchor="middle" class="text-sm">• Зберігає опції, ECN та точні TTL</text>
  <text x="400" y="345" text-anchor="middle" class="text-sm">• Формує skb з skb_shared_info (frag_list)</text>
  <text x="400" y="361" text-anchor="middle" class="text-sm text-bold" fill="#2b8a3e">ПОВНІСТЮ БЕЗПЕЧНО ДЛЯ ROUTER / BRIDGE</text>

  <rect x="560" y="280" width="290" height="85" class="packet-merged" />
  <text x="705" y="305" text-anchor="middle" class="text text-bold" fill="#1864ab">Структурований GRO Супер-пакет</text>
  <text x="705" y="325" text-anchor="middle" class="text-sm">Всі оригінальні метадані збережені</text>
  <text x="705" y="345" text-anchor="middle" class="text-sm">Легко розділяється назад при forwarding (GSO)</text>

  <!-- Arrows from PHY -->
  <path d="M 210 140 L 250 140" class="arrow" />
  <path d="M 210 310 L 250 310" class="arrow" />

</svg>"""

    with open(os.path.join(img_dir, "gso-tso.svg"), "w", encoding="utf-8") as f:
        f.write(gso_tso_content)

    with open(os.path.join(img_dir, "gro-lro.svg"), "w", encoding="utf-8") as f:
        f.write(gro_lro_content)

    print("SVG figures generated successfully in img/")

if __name__ == '__main__':
    generate_svgs()

import os
import sys

def render():
    os.makedirs("img", exist_ok=True)
    
    # 1. tcp-urgent-pointer.svg
    svg1_path = os.path.join("img", "tcp-urgent-pointer.svg")
    svg1_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="920" height="460" viewBox="0 0 920 460">
    <style>
        .bg { fill: #f8fafc; }
        .hdr-box { fill: #ffffff; stroke: #334155; stroke-width: 2; }
        .urg-box { fill: #fef2f2; stroke: #dc2626; stroke-width: 2; }
        .flag-urg { fill: #dc2626; font-weight: bold; }
        .title { font-family: sans-serif; font-size: 18px; font-weight: bold; fill: #0f172a; }
        .text-hdr { font-family: monospace; font-size: 13px; fill: #334155; }
        .text-urg { font-family: monospace; font-size: 13px; font-weight: bold; fill: #991b1b; }
        .text-sub { font-family: sans-serif; font-size: 12px; fill: #475569; }
        .seq-box { fill: #e2e8f0; stroke: #475569; stroke-width: 1.5; rx: 4px; }
        .seq-oob { fill: #fecaca; stroke: #b91c1c; stroke-width: 2; rx: 4px; }
        .arrow-urg { stroke: #dc2626; stroke-width: 2; fill: none; marker-end: url(#arrow-red); }
        .arrow-std { stroke: #2563eb; stroke-width: 2; fill: none; marker-end: url(#arrow-blue); }
    </style>
    <defs>
        <marker id="arrow-red" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#dc2626" />
        </marker>
        <marker id="arrow-blue" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#2563eb" />
        </marker>
    </defs>

    <!-- Canvas background -->
    <rect width="920" height="460" class="bg" />

    <!-- Title -->
    <text x="30" y="35" class="title">Заголовок TCP та механізм покажчика терміновости (Urgent Pointer)</text>

    <!-- TCP Header Grid (Width 860) -->
    <!-- Row 1: Source & Destination Port -->
    <rect x="30" y="65" width="430" height="35" class="hdr-box" />
    <text x="245" y="88" class="text-hdr" text-anchor="middle">Source Port (16 біт)</text>
    <rect x="460" y="65" width="430" height="35" class="hdr-box" />
    <text x="675" y="88" class="text-hdr" text-anchor="middle">Destination Port (16 біт)</text>

    <!-- Row 2: Sequence Number -->
    <rect x="30" y="100" width="860" height="35" class="hdr-box" />
    <text x="460" y="123" class="text-hdr" text-anchor="middle">Sequence Number = 1000 (32 біти)</text>

    <!-- Row 3: Acknowledgment Number -->
    <rect x="30" y="135" width="860" height="35" class="hdr-box" />
    <text x="460" y="158" class="text-hdr" text-anchor="middle">Acknowledgment Number (32 біти)</text>

    <!-- Row 4: Offset, Resvd, Flags, Window -->
    <rect x="30" y="170" width="100" height="35" class="hdr-box" />
    <text x="80" y="193" class="text-hdr" text-anchor="middle">Offset</text>
    <rect x="130" y="170" width="90" height="35" class="hdr-box" />
    <text x="175" y="193" class="text-hdr" text-anchor="middle">Resvd</text>
    
    <!-- Flags Box -->
    <rect x="220" y="170" width="240" height="35" class="hdr-box" />
    <text x="340" y="193" class="text-hdr" text-anchor="middle">C E <tspan class="flag-urg">URG=1</tspan> A P R S F</text>
    
    <!-- Window Size -->
    <rect x="460" y="170" width="430" height="35" class="hdr-box" />
    <text x="675" y="193" class="text-hdr" text-anchor="middle">Window Size (16 біт)</text>

    <!-- Row 5: Checksum & Urgent Pointer -->
    <rect x="30" y="205" width="430" height="35" class="hdr-box" />
    <text x="245" y="228" class="text-hdr" text-anchor="middle">Checksum (16 біт)</text>
    <rect x="460" y="205" width="430" height="35" class="urg-box" />
    <text x="675" y="228" class="text-urg" text-anchor="middle">Urgent Pointer = 2 (16 біт)</text>

    <!-- Sequence Stream Visualization -->
    <text x="30" y="275" class="title">Потік байтів у TCP та зміщення Urgent Pointer</text>

    <!-- Byte Boxes -->
    <rect x="30" y="300" width="160" height="50" class="seq-box" />
    <text x="110" y="322" class="text-hdr" text-anchor="middle">Seq 1000</text>
    <text x="110" y="340" class="text-sub" text-anchor="middle">Звичайні дані</text>

    <rect x="200" y="300" width="160" height="50" class="seq-box" />
    <text x="280" y="322" class="text-hdr" text-anchor="middle">Seq 1001</text>
    <text x="280" y="340" class="text-sub" text-anchor="middle">Звичайні дані</text>

    <rect x="370" y="300" width="160" height="50" class="seq-oob" />
    <text x="450" y="322" class="text-urg" text-anchor="middle">Seq 1002 (OOB)</text>
    <text x="450" y="340" class="text-urg" text-anchor="middle">Терміновий байт</text>

    <rect x="540" y="300" width="160" height="50" class="seq-box" />
    <text x="620" y="322" class="text-hdr" text-anchor="middle">Seq 1003</text>
    <text x="620" y="340" class="text-sub" text-anchor="middle">Наступний байт</text>

    <rect x="710" y="300" width="180" height="50" class="seq-box" />
    <text x="800" y="322" class="text-hdr" text-anchor="middle">Seq 1004...</text>
    <text x="800" y="340" class="text-sub" text-anchor="middle">Звичайний потік</text>

    <!-- Arrow RFC 1122 vs RFC 793 -->
    <path d="M 675 240 V 270 H 450 V 292" class="arrow-urg" />
    <text x="450" y="262" class="text-urg" text-anchor="middle">RFC 1122 / Linux (tcp_stdurg=0): Seq + Urgent Ptr (1000 + 2 = 1002)</text>

    <path d="M 675 240 V 270 H 620 V 292" class="arrow-std" />
    <text x="650" y="380" class="text-hdr" text-anchor="middle">RFC 793 / BSD (tcp_stdurg=1): Seq + Urgent Ptr вказує на байт після OOB (1003)</text>
</svg>
"""
    with open(svg1_path, "w", encoding="utf-8") as f:
        f.write(svg1_content)
    print(f"Generated {svg1_path}")

    # 2. oob-signal-flow.svg
    svg2_path = os.path.join("img", "oob-signal-flow.svg")
    svg2_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="940" height="480" viewBox="0 0 940 480">
    <style>
        .bg { fill: #f8fafc; }
        .box-sender { fill: #eff6ff; stroke: #2563eb; stroke-width: 2; rx: 8px; }
        .box-kernel { fill: #fef2f2; stroke: #dc2626; stroke-width: 2; rx: 8px; }
        .box-recv { fill: #f0fdf4; stroke: #16a34a; stroke-width: 2; rx: 8px; }
        .title-box { font-family: monospace; font-size: 15px; font-weight: bold; }
        .text-main { font-family: monospace; font-size: 13px; fill: #1e293b; }
        .text-bold { font-family: monospace; font-size: 13px; font-weight: bold; fill: #0f172a; }
        .text-urg { font-family: monospace; font-size: 13px; font-weight: bold; fill: #991b1b; }
        .arrow-red { stroke: #dc2626; stroke-width: 2; fill: none; marker-end: url(#arr-red); }
        .arrow-blue { stroke: #2563eb; stroke-width: 2; fill: none; marker-end: url(#arr-blue); }
        .arrow-green { stroke: #16a34a; stroke-width: 2; fill: none; marker-end: url(#arr-green); }
    </style>
    <defs>
        <marker id="arr-red" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#dc2626" />
        </marker>
        <marker id="arr-blue" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#2563eb" />
        </marker>
        <marker id="arr-green" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#16a34a" />
        </marker>
    </defs>

    <!-- Canvas background -->
    <rect width="940" height="480" class="bg" />

    <!-- Column 1: Process Sender -->
    <rect x="30" y="40" width="250" height="400" class="box-sender" />
    <text x="155" y="70" class="title-box" fill="#1d4ed8" text-anchor="middle">Процес-відправник</text>
    <text x="50" y="110" class="text-bold">1. Підготовка даних</text>
    <text x="50" y="135" class="text-main">Звичайний потік даних</text>
    <text x="50" y="180" class="text-bold">2. Виклик send():</text>
    <text x="50" y="205" class="text-urg">send(fd, "!", 1,</text>
    <text x="90" y="225" class="text-urg">MSG_OOB);</text>
    <text x="50" y="270" class="text-main">Байт '!' позначається</text>
    <text x="50" y="290" class="text-main">як терміновий (OOB)</text>

    <!-- Column 2: Kernel TCP Stack -->
    <rect x="340" y="40" width="260" height="400" class="box-kernel" />
    <text x="470" y="70" class="title-box" fill="#b91c1c" text-anchor="middle">Стек TCP ядра Linux</text>
    <text x="360" y="110" class="text-bold">Формування TCP-пакета:</text>
    <text x="360" y="135" class="text-urg">URG=1, Urgent Pointer=N</text>
    <text x="360" y="180" class="text-bold">Отримання пакета:</text>
    <text x="360" y="205" class="text-main">skb-&gt;urgent_pointer</text>
    <text x="360" y="225" class="text-main">Оновлення tp-&gt;urg_data</text>
    <text x="360" y="270" class="text-bold">Генерація подій:</text>
    <text x="360" y="295" class="text-urg">1. Сигнал SIGURG</text>
    <text x="360" y="320" class="text-urg">2. Прапорець POLLPRI</text>
    <text x="360" y="345" class="text-urg">3. select exceptfds</text>

    <!-- Column 3: Process Receiver -->
    <rect x="660" y="40" width="250" height="400" class="box-recv" />
    <text x="785" y="70" class="title-box" fill="#15803d" text-anchor="middle">Процес-приймач</text>
    <text x="680" y="110" class="text-bold">Реєстрація власника:</text>
    <text x="680" y="135" class="text-main">fcntl(fd, F_SETOWN, pid)</text>
    <text x="680" y="175" class="text-bold">Реакція на SIGURG:</text>
    <text x="680" y="200" class="text-main">Переривання циклу</text>
    <text x="680" y="240" class="text-bold">Читання OOB байта:</text>
    <text x="680" y="265" class="text-urg">recv(fd, &amp;c, 1, MSG_OOB)</text>
    <text x="680" y="290" class="text-main">або через SO_OOBINLINE</text>
    <text x="680" y="330" class="text-bold">Перевірка маркера:</text>
    <text x="680" y="355" class="text-main">ioctl(fd, SIOCATMARK)</text>

    <!-- Connectors -->
    <!-- Sender -> Kernel -->
    <path d="M 280 210 H 340" class="arrow-blue" />
    
    <!-- Kernel -> Receiver SIGURG -->
    <path d="M 600 295 H 660" class="arrow-red" />
    
    <!-- Receiver read -> Kernel -->
    <path d="M 660 265 H 600" class="arrow-green" />
</svg>
"""
    with open(svg2_path, "w", encoding="utf-8") as f:
        f.write(svg2_content)
    print(f"Generated {svg2_path}")

if __name__ == "__main__":
    render()

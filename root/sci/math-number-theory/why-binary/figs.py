# -*- coding: utf-8 -*-
import os
import sys

IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(IMG_DIR, exist_ok=True)

DEFS = """<defs>
  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="#1b1b1b"/></marker>
  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="#c0271e"/></marker>
  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="#1f47b5"/></marker>
  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="#1f8a3b"/></marker>
</defs>"""

FONT_FAMILY = "Segoe UI, Arial, Helvetica, sans-serif"


def svg_header(w, h):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<rect width="{w}" height="{h}" fill="#ffffff"/>
{DEFS}"""


def svg_footer():
    return "</svg>\n"


def gen_timeline():
    w, h = 880, 760
    lines = [svg_header(w, h)]
    lines.append(f'<text x="440.0" y="38.0" font-family="{FONT_FAMILY}" font-size="21" fill="#1b1b1b" text-anchor="middle" font-weight="bold" font-style="normal">Ланцюг питань: скількома символами можна рахувати?</text>')
    lines.append(f'<text x="440.0" y="60.0" font-family="{FONT_FAMILY}" font-size="12.5" fill="#8a8a8a" text-anchor="middle" font-weight="normal" font-style="italic">від десяти цифр (пальці) до двох (0 і 1) — і чому остання, найбідніша система перемогла</text>')
    lines.append('<line x1="250.0" y1="100.0" x2="250.0" y2="730.0" stroke="#8a8a8a" stroke-width="3" stroke-linecap="round"/>')

    nodes = [
        (130.0, "давнина", "Пінгала, I Ching", "Двійкові ідеї задовго до Європи: просодія в Індії, гексаграми в Китаї", False),
        (225.0, "позиційні", "місце = степінь основи", "Геній «розрядів»: значення цифри залежить від місця (десяткова — з пальців)", False),
        (320.0, "1703", "Лейбніц / Leibniz", "ВСІ числа з 0 і 1: «Explication de l'Arithmétique Binaire»", True),
        (415.0, "~1703", "гексаграми I Ching", "Лейбніц вражений: давні китайці «вже мали» двійкову (інь=0, ян=1)", False),
        (510.0, "та ж епоха", "машина Лейбніца", "А рахувала вона… ДЕСЯТКОВО. Двійкова лишилась чистою теорією", False),
        (605.0, "1703–1937", "«лише курйоз»", "Двійкова чекала на застосування понад 200 років (як алгебра Буля)", False),
        (700.0, "XX ст.", "комп\'ютер", "Два стани (Розд. 14) + логіка (Розд. 15) + двійкові числа — нарешті РАЗОМ", False),
    ]

    for y, time_label, title, subtitle, is_red in nodes:
        if is_red:
            lines.append(f'<circle cx="250.0" cy="{y}" r="11.0" fill="#fff" stroke="#c0271e" stroke-width="0"/>')
            lines.append(f'<circle cx="250.0" cy="{y}" r="10.0" fill="none" stroke="#c0271e" stroke-width="3.2"/>')
            lines.append(f'<circle cx="250.0" cy="{y}" r="4.5" fill="#c0271e" stroke="#c0271e" stroke-width="1"/>')
            lines.append(f'<text x="228.0" y="{y + 5.0}" font-family="{FONT_FAMILY}" font-size="12.5" fill="#8a8a8a" text-anchor="end" font-weight="bold" font-style="normal">{time_label}</text>')
            lines.append(f'<text x="276.0" y="{y - 3.0}" font-family="{FONT_FAMILY}" font-size="15" fill="#c0271e" text-anchor="start" font-weight="bold" font-style="normal">{title}</text>')
        else:
            lines.append(f'<circle cx="250.0" cy="{y}" r="7.0" fill="#fff" stroke="#1b1b1b" stroke-width="2.6"/>')
            lines.append(f'<text x="228.0" y="{y + 5.0}" font-family="{FONT_FAMILY}" font-size="12.5" fill="#8a8a8a" text-anchor="end" font-weight="bold" font-style="normal">{time_label}</text>')
            lines.append(f'<text x="276.0" y="{y - 3.0}" font-family="{FONT_FAMILY}" font-size="15" fill="#1b1b1b" text-anchor="start" font-weight="bold" font-style="normal">{title}</text>')
        lines.append(f'<text x="276.0" y="{y + 17.0}" font-family="{FONT_FAMILY}" font-size="12" fill="#1b1b1b" text-anchor="start" font-weight="normal" font-style="italic">{subtitle}</text>')

    lines.append(svg_footer())
    with open(os.path.join(IMG_DIR, "timeline.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def gen_leibniz_idea():
    w, h = 880, 450
    lines = [svg_header(w, h)]
    lines.append(f'<text x="440.0" y="36.0" font-family="{FONT_FAMILY}" font-size="21" fill="#1b1b1b" text-anchor="middle" font-weight="bold" font-style="normal">Ідея Лейбніца: будь-яке число — лише з 0 і 1</text>')
    lines.append(f'<text x="440.0" y="58.0" font-family="{FONT_FAMILY}" font-size="12.5" fill="#8a8a8a" text-anchor="middle" font-weight="normal" font-style="italic">рахунок «перевалює» вже на двох символах; значення дає МІСЦЕ цифри — степінь двійки</text>')
    lines.append(f'<text x="120.0" y="100.0" font-family="{FONT_FAMILY}" font-size="13" fill="#1b1b1b" text-anchor="start" font-weight="bold" font-style="normal">Лічба двійкою:</text>')

    counts = [
        (0, "0"), (1, "1"), (2, "10"), (3, "11"),
        (4, "100"), (5, "101"), (6, "110"), (7, "111"), (8, "1000")
    ]
    for idx, (dec_val, bin_val) in enumerate(counts):
        cur_y = 128.0 + idx * 28.0
        lines.append(f'<text x="150.0" y="{cur_y}" font-family="{FONT_FAMILY}" font-size="13" fill="#8a8a8a" text-anchor="end" font-weight="normal" font-style="normal">{dec_val}</text>')
        lines.append(f'<text x="165.0" y="{cur_y}" font-family="{FONT_FAMILY}" font-size="11" fill="#8a8a8a" text-anchor="start" font-weight="normal" font-style="normal">→</text>')
        lines.append(f'<text x="195.0" y="{cur_y}" font-family="{FONT_FAMILY}" font-size="14" fill="#1b1b1b" text-anchor="start" font-weight="bold" font-style="normal">{bin_val}</text>')

    lines.append(f'<text x="560.0" y="110.0" font-family="{FONT_FAMILY}" font-size="13" fill="#1b1b1b" text-anchor="middle" font-weight="bold" font-style="normal">Розряди = степені двійки:</text>')

    bits_info = [
        (440.0, "1", "×8", "2³", "#fdf4f4", "#c0271e"),
        (520.0, "0", "×4", "2²", "#f3f5fd", "#1f47b5"),
        (600.0, "1", "×2", "2¹", "#fdf4f4", "#c0271e"),
        (680.0, "1", "×1", "2⁰", "#fdf4f4", "#c0271e"),
    ]
    for bx, digit, mult, pwr, bg_col, stroke_col in bits_info:
        lines.append(f'<rect x="{bx}" y="140.0" width="56.0" height="50.0" rx="6" fill="{bg_col}" stroke="{stroke_col}" stroke-width="2"/>')
        lines.append(f'<text x="{bx + 28.0}" y="172.0" font-family="{FONT_FAMILY}" font-size="18" fill="{stroke_col}" text-anchor="middle" font-weight="bold" font-style="normal">{digit}</text>')
        lines.append(f'<text x="{bx + 28.0}" y="210.0" font-family="{FONT_FAMILY}" font-size="12" fill="#8a8a8a" text-anchor="middle" font-weight="bold" font-style="normal">{mult}</text>')
        lines.append(f'<text x="{bx + 28.0}" y="128.0" font-family="{FONT_FAMILY}" font-size="11" fill="#8a8a8a" text-anchor="middle" font-weight="normal" font-style="normal">{pwr}</text>')

    lines.append(f'<text x="680.0" y="250.0" font-family="{FONT_FAMILY}" font-size="16" fill="#1f8a3b" text-anchor="middle" font-weight="bold" font-style="normal">= 8 + 0 + 2 + 1 = 11</text>')
    lines.append('<rect x="440.0" y="290.0" width="400.0" height="110.0" rx="10" fill="#f4f7f4" stroke="#1f8a3b" stroke-width="1.6"/>')
    lines.append(f'<text x="640.0" y="316.0" font-family="{FONT_FAMILY}" font-size="12.5" fill="#1b1b1b" text-anchor="middle" font-weight="bold" font-style="normal">«Гачок» Лейбніца був і філософський:</text>')
    lines.append(f'<text x="640.0" y="342.0" font-family="{FONT_FAMILY}" font-size="12" fill="#1b1b1b" text-anchor="middle" font-weight="normal" font-style="normal">0 — ніщо (порожнеча), 1 — єдність;</text>')
    lines.append(f'<text x="640.0" y="364.0" font-family="{FONT_FAMILY}" font-size="12" fill="#1b1b1b" text-anchor="middle" font-weight="normal" font-style="normal">усе суще будується з нічого і одиниці.</text>')
    lines.append(f'<text x="640.0" y="386.0" font-family="{FONT_FAMILY}" font-size="11" fill="#8a8a8a" text-anchor="middle" font-weight="normal" font-style="italic">Для нього двійкова була майже священною.</text>')

    lines.append(svg_footer())
    with open(os.path.join(IMG_DIR, "leibniz-idea.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def gen_iching():
    w, h = 880, 400
    lines = [svg_header(w, h)]
    lines.append(f'<text x="440.0" y="36.0" font-family="{FONT_FAMILY}" font-size="20" fill="#1b1b1b" text-anchor="middle" font-weight="bold" font-style="normal">Подив Лейбніца: гексаграми I Ching — це і є двійкові числа</text>')
    lines.append(f'<text x="440.0" y="58.0" font-family="{FONT_FAMILY}" font-size="12" fill="#8a8a8a" text-anchor="middle" font-weight="normal" font-style="italic">давньокитайські фігури з рисок: суцільна (ян) = 1, розірвана (інь) = 0 — точна двійкова лічба</text>')

    trigrams = [
        (110.0, "000", 0, [False, False, False]),
        (200.0, "001", 1, [False, False, True]),
        (290.0, "010", 2, [False, True, False]),
        (380.0, "011", 3, [False, True, True]),
        (470.0, "100", 4, [True, False, False]),
        (560.0, "101", 5, [True, False, True]),
        (650.0, "110", 6, [True, True, False]),
        (740.0, "111", 7, [True, True, True]),
    ]

    for cx, code, val, bits in trigrams:
        for row_idx, is_solid in enumerate(bits):
            ry = 156.0 + row_idx * 14.0
            if is_solid:
                lines.append(f'<line x1="{cx - 27.0:.1f}" y1="{ry:.1f}" x2="{cx + 27.0:.1f}" y2="{ry:.1f}" stroke="#1b1b1b" stroke-width="4" stroke-linecap="round"/>')
            else:
                lines.append(f'<line x1="{cx - 27.0:.1f}" y1="{ry:.1f}" x2="{cx - 7.6:.1f}" y2="{ry:.1f}" stroke="#1b1b1b" stroke-width="4" stroke-linecap="round"/>')
                lines.append(f'<line x1="{cx + 7.6:.1f}" y1="{ry:.1f}" x2="{cx + 27.0:.1f}" y2="{ry:.1f}" stroke="#1b1b1b" stroke-width="4" stroke-linecap="round"/>')
        lines.append(f'<text x="{cx:.1f}" y="215.0" font-family="{FONT_FAMILY}" font-size="13" fill="#1b1b1b" text-anchor="middle" font-weight="bold" font-style="normal">{code}</text>')
        lines.append(f'<text x="{cx:.1f}" y="234.0" font-family="{FONT_FAMILY}" font-size="12" fill="#c0271e" text-anchor="middle" font-weight="bold" font-style="normal">= {val}</text>')

    lines.append(f'<text x="60.0" y="156.0" font-family="{FONT_FAMILY}" font-size="11" fill="#1b1b1b" text-anchor="end" font-weight="bold" font-style="normal">ян 1</text>')
    lines.append('<line x1="77.0" y1="156.0" x2="113.0" y2="156.0" stroke="#1b1b1b" stroke-width="4" stroke-linecap="round"/>')
    lines.append(f'<text x="60.0" y="184.0" font-family="{FONT_FAMILY}" font-size="11" fill="#1b1b1b" text-anchor="end" font-weight="bold" font-style="normal">інь 0</text>')
    lines.append('<line x1="77.0" y1="184.0" x2="90.0" y2="184.0" stroke="#1b1b1b" stroke-width="4" stroke-linecap="round"/>')
    lines.append('<line x1="100.0" y1="184.0" x2="113.0" y2="184.0" stroke="#1b1b1b" stroke-width="4" stroke-linecap="round"/>')

    lines.append('<rect x="70.0" y="270.0" width="740.0" height="80.0" rx="10" fill="#f4f7f4" stroke="#1f8a3b" stroke-width="1.6"/>')
    lines.append(f'<text x="440.0" y="296.0" font-family="{FONT_FAMILY}" font-size="12" fill="#1b1b1b" text-anchor="middle" font-weight="bold" font-style="normal">Лейбніц упізнав у тисячолітніх гексаграмах власну двійкову систему — і був вражений до глибини душі.</text>')
    lines.append(f'<text x="440.0" y="318.0" font-family="{FONT_FAMILY}" font-size="11.5" fill="#8a8a8a" text-anchor="middle" font-weight="normal" font-style="italic">Усіх гексаграм (по 6 рисок) — 64, тобто рівно двійкові числа 0…63. Збіг не випадковий: це й є рахунок двома станами.</text>')
    lines.append(f'<text x="440.0" y="338.0" font-family="{FONT_FAMILY}" font-size="11" fill="#8a8a8a" text-anchor="middle" font-weight="normal" font-style="italic">Одна й та сама ідея незалежно зринала в різних культурах — настільки вона глибока.</text>')

    lines.append(svg_footer())
    with open(os.path.join(IMG_DIR, "iching.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def gen_convergence():
    w, h = 880, 420
    lines = [svg_header(w, h)]
    lines.append(f'<text x="440.0" y="36.0" font-family="{FONT_FAMILY}" font-size="20" fill="#1b1b1b" text-anchor="middle" font-weight="bold" font-style="normal">Куди привів цей ланцюг: три потоки 0/1 сходяться в комп\'ютері</text>')
    lines.append(f'<text x="440.0" y="58.0" font-family="{FONT_FAMILY}" font-size="12" fill="#8a8a8a" text-anchor="middle" font-weight="normal" font-style="italic">двійкова чекала ~200 років, аж поки фізика й логіка не дали їй тіло — і всі три злилися воєдино</text>')

    lines.append('<rect x="70.0" y="110.0" width="280.0" height="52.0" rx="10" fill="#f3f5fd" stroke="#1f47b5" stroke-width="1.8"/>')
    lines.append(f'<text x="210.0" y="132.0" font-family="{FONT_FAMILY}" font-size="13" fill="#1f47b5" text-anchor="middle" font-weight="bold" font-style="normal">ДВА ФІЗИЧНІ СТАНИ</text>')
    lines.append(f'<text x="210.0" y="151.0" font-family="{FONT_FAMILY}" font-size="11" fill="#8a8a8a" text-anchor="middle" font-weight="normal" font-style="normal">напруга низько/високо  (Розділ 14)</text>')
    lines.append('<line x1="350.0" y1="136.0" x2="470.0" y2="220.0" stroke="#1b1b1b" stroke-width="1.8" marker-end="url(#aInk)"/>')

    lines.append('<rect x="70.0" y="185.0" width="280.0" height="52.0" rx="10" fill="#eef7ee" stroke="#1f8a3b" stroke-width="1.8"/>')
    lines.append(f'<text x="210.0" y="207.0" font-family="{FONT_FAMILY}" font-size="13" fill="#1f8a3b" text-anchor="middle" font-weight="bold" font-style="normal">БУЛЕВА ЛОГІКА</text>')
    lines.append(f'<text x="210.0" y="226.0" font-family="{FONT_FAMILY}" font-size="11" fill="#8a8a8a" text-anchor="middle" font-weight="normal" font-style="normal">і / або / не над 0,1  (Розділ 15)</text>')
    lines.append('<line x1="350.0" y1="211.0" x2="470.0" y2="220.0" stroke="#1b1b1b" stroke-width="1.8" marker-end="url(#aInk)"/>')

    lines.append('<rect x="70.0" y="260.0" width="280.0" height="52.0" rx="10" fill="#fdf4f4" stroke="#c0271e" stroke-width="1.8"/>')
    lines.append(f'<text x="210.0" y="282.0" font-family="{FONT_FAMILY}" font-size="13" fill="#c0271e" text-anchor="middle" font-weight="bold" font-style="normal">ДВІЙКОВІ ЧИСЛА</text>')
    lines.append(f'<text x="210.0" y="301.0" font-family="{FONT_FAMILY}" font-size="11" fill="#8a8a8a" text-anchor="middle" font-weight="normal" font-style="normal">число з 0 і 1 (Лейбніц)  (Розділ 17)</text>')
    lines.append('<line x1="350.0" y1="286.0" x2="470.0" y2="220.0" stroke="#1b1b1b" stroke-width="1.8" marker-end="url(#aInk)"/>')

    lines.append('<rect x="470.0" y="160.0" width="340.0" height="120.0" rx="12" fill="#fff8e8" stroke="#caa24a" stroke-width="2"/>')
    lines.append(f'<text x="640.0" y="195.0" font-family="{FONT_FAMILY}" font-size="16" fill="#9a7322" text-anchor="middle" font-weight="bold" font-style="normal">КОМП\'ЮТЕР</text>')
    lines.append(f'<text x="640.0" y="221.0" font-family="{FONT_FAMILY}" font-size="12.5" fill="#1b1b1b" text-anchor="middle" font-weight="bold" font-style="normal">0 і 1 — це водночас</text>')
    lines.append(f'<text x="640.0" y="243.0" font-family="{FONT_FAMILY}" font-size="12" fill="#1b1b1b" text-anchor="middle" font-weight="normal" font-style="normal">і фізичний стан, і логіка,</text>')
    lines.append(f'<text x="640.0" y="263.0" font-family="{FONT_FAMILY}" font-size="13" fill="#c0271e" text-anchor="middle" font-weight="bold" font-style="normal">і ЧИСЛО</text>')

    lines.append(f'<text x="440.0" y="355.0" font-family="{FONT_FAMILY}" font-size="12" fill="#1b1b1b" text-anchor="middle" font-weight="bold" font-style="normal">Третій потік — про те, як саме з 0 і 1 робити ЧИСЛА: додатні й від\'ємні, дробові, великі.</text>')
    lines.append(f'<text x="440.0" y="378.0" font-family="{FONT_FAMILY}" font-size="11.5" fill="#8a8a8a" text-anchor="middle" font-weight="normal" font-style="italic">Бо щойно «0 і 1» стають числом, біти в регістрах перетворюються на арифметику.</text>')

    lines.append(svg_footer())
    with open(os.path.join(IMG_DIR, "convergence.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def gen_why_two():
    w, h = 880, 440
    lines = [svg_header(w, h)]
    lines.append(f'<text x="440.0" y="34.0" font-family="{FONT_FAMILY}" font-size="20" fill="#1b1b1b" text-anchor="middle" font-weight="bold" font-style="normal">Чому в залізі два символи, а не десять: надійність розряду</text>')
    lines.append(f'<text x="440.0" y="56.0" font-family="{FONT_FAMILY}" font-size="11.5" fill="#8a8a8a" text-anchor="middle" font-weight="normal" font-style="italic">щоб зберегти цифру дротом, кожне значення — окремий рівень напруги; менше рівнів = ширші «ями»</text>')

    # Left: Decimal 10 levels
    lines.append(f'<text x="230.0" y="86.0" font-family="{FONT_FAMILY}" font-size="14" fill="#1b1b1b" text-anchor="middle" font-weight="bold" font-style="normal">десяткова: 10 рівнів</text>')
    lines.append('<rect x="180.0" y="100.0" width="100.0" height="280.0" rx="0" fill="#fafafa" stroke="#1b1b1b" stroke-width="2"/>')
    lines.append('<line x1="180.0" y1="380.0" x2="280.0" y2="380.0" stroke="#1f47b5" stroke-width="2" stroke-linecap="round"/>')
    for y_val in [348.9, 317.8, 286.7, 255.6, 224.4, 193.3, 162.2, 131.1]:
        lines.append(f'<line x1="180.0" y1="{y_val}" x2="280.0" y2="{y_val}" stroke="#8a8a8a" stroke-width="2" stroke-linecap="round"/>')
    lines.append('<line x1="180.0" y1="100.0" x2="280.0" y2="100.0" stroke="#c0271e" stroke-width="2" stroke-linecap="round"/>')

    lines.append('<line x1="294.0" y1="380.0" x2="294.0" y2="348.9" stroke="#1b1b1b" stroke-width="1.6" stroke-linecap="round"/>')
    lines.append('<line x1="290.0" y1="380.0" x2="298.0" y2="380.0" stroke="#1b1b1b" stroke-width="1.6" stroke-linecap="round"/>')
    lines.append('<line x1="290.0" y1="348.9" x2="298.0" y2="348.9" stroke="#1b1b1b" stroke-width="1.6" stroke-linecap="round"/>')
    lines.append(f'<text x="302.0" y="368.4" font-family="{FONT_FAMILY}" font-size="11" fill="#1b1b1b" text-anchor="start" font-weight="bold" font-style="normal">яма</text>')

    lines.append('<rect x="216.0" y="130.0" width="28.0" height="42.4" rx="2" fill="#fbf3e0" stroke="#caa24a" stroke-width="1.6"/>')
    lines.append(f'<text x="230.0" y="124.0" font-family="{FONT_FAMILY}" font-size="10.5" fill="#caa24a" text-anchor="middle" font-weight="bold" font-style="normal">шум</text>')
    lines.append(f'<text x="230.0" y="404.0" font-family="{FONT_FAMILY}" font-size="12" fill="#c0271e" text-anchor="middle" font-weight="bold" font-style="normal">крок ~0.37 В → шум плутає</text>')
    lines.append(f'<text x="230.0" y="422.0" font-family="{FONT_FAMILY}" font-size="12" fill="#c0271e" text-anchor="middle" font-weight="bold" font-style="normal">✘ тісно, ненадійно</text>')

    # Right: Binary 2 levels
    lines.append(f'<text x="640.0" y="86.0" font-family="{FONT_FAMILY}" font-size="14" fill="#1b1b1b" text-anchor="middle" font-weight="bold" font-style="normal">двійкова: 2 рівні</text>')
    lines.append('<rect x="590.0" y="100.0" width="100.0" height="280.0" rx="0" fill="#fafafa" stroke="#1b1b1b" stroke-width="2"/>')
    lines.append('<line x1="590.0" y1="380.0" x2="690.0" y2="380.0" stroke="#1f47b5" stroke-width="2" stroke-linecap="round"/>')
    lines.append('<line x1="590.0" y1="100.0" x2="690.0" y2="100.0" stroke="#c0271e" stroke-width="2" stroke-linecap="round"/>')

    lines.append('<line x1="704.0" y1="380.0" x2="704.0" y2="100.0" stroke="#1b1b1b" stroke-width="1.6" stroke-linecap="round"/>')
    lines.append('<line x1="700.0" y1="380.0" x2="708.0" y2="380.0" stroke="#1b1b1b" stroke-width="1.6" stroke-linecap="round"/>')
    lines.append('<line x1="700.0" y1="100.0" x2="708.0" y2="100.0" stroke="#1b1b1b" stroke-width="1.6" stroke-linecap="round"/>')
    lines.append(f'<text x="712.0" y="244.0" font-family="{FONT_FAMILY}" font-size="11" fill="#1b1b1b" text-anchor="start" font-weight="bold" font-style="normal">яма</text>')

    lines.append('<rect x="626.0" y="130.0" width="28.0" height="42.4" rx="2" fill="#fbf3e0" stroke="#caa24a" stroke-width="1.6"/>')
    lines.append(f'<text x="640.0" y="124.0" font-family="{FONT_FAMILY}" font-size="10.5" fill="#caa24a" text-anchor="middle" font-weight="bold" font-style="normal">шум</text>')
    lines.append(f'<text x="640.0" y="404.0" font-family="{FONT_FAMILY}" font-size="12" fill="#1f8a3b" text-anchor="middle" font-weight="bold" font-style="normal">крок 3.3 В → шум безсилий</text>')
    lines.append(f'<text x="640.0" y="422.0" font-family="{FONT_FAMILY}" font-size="12" fill="#1f8a3b" text-anchor="middle" font-weight="bold" font-style="normal">✔ просто, надійно</text>')

    lines.append(f'<text x="440.0" y="250.0" font-family="{FONT_FAMILY}" font-size="11" fill="#8a8a8a" text-anchor="middle" font-weight="normal" font-style="italic">той самий</text>')
    lines.append(f'<text x="440.0" y="266.0" font-family="{FONT_FAMILY}" font-size="11" fill="#8a8a8a" text-anchor="middle" font-weight="normal" font-style="italic">шум 0.5 В</text>')

    lines.append(svg_footer())
    with open(os.path.join(IMG_DIR, "why-two.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def gen_cost():
    w, h = 860, 340
    lines = [svg_header(w, h)]
    lines.append(f'<text x="430.0" y="34.0" font-family="{FONT_FAMILY}" font-size="19.5" fill="#1b1b1b" text-anchor="middle" font-weight="bold" font-style="normal">Ціна двійкової — довжина; виграш — простота й надійність розряду</text>')
    lines.append(f'<text x="430.0" y="56.0" font-family="{FONT_FAMILY}" font-size="11.5" fill="#8a8a8a" text-anchor="middle" font-weight="normal" font-style="italic">те саме число займає більше розрядів, та кожен розряд тепер тривіальний (0 або 1) і стійкий до шуму</text>')

    # Decimal row
    lines.append(f'<text x="120.0" y="130.0" font-family="{FONT_FAMILY}" font-size="13" fill="#1b1b1b" text-anchor="start" font-weight="bold" font-style="normal">десяткова:</text>')
    for idx, digit in enumerate(["2", "3", "3"]):
        rx = 280.0 + idx * 60.0
        lines.append(f'<rect x="{rx}" y="110.0" width="50.0" height="50.0" rx="6" fill="#eef4ff" stroke="#1b1b1b" stroke-width="2"/>')
        lines.append(f'<text x="{rx + 25.0}" y="144.0" font-family="{FONT_FAMILY}" font-size="18" fill="#1b1b1b" text-anchor="middle" font-weight="bold" font-style="normal">{digit}</text>')
    lines.append(f'<text x="480.0" y="144.0" font-family="{FONT_FAMILY}" font-size="12" fill="#8a8a8a" text-anchor="start" font-weight="normal" font-style="normal">3 розряди (по 10 значень)</text>')

    # Binary row: 11101001
    lines.append(f'<text x="120.0" y="230.0" font-family="{FONT_FAMILY}" font-size="13" fill="#1b1b1b" text-anchor="start" font-weight="bold" font-style="normal">двійкова:</text>')
    bin_digits = [("1", "#fdf4f4", "#c0271e"), ("1", "#fdf4f4", "#c0271e"), ("1", "#fdf4f4", "#c0271e"),
                  ("0", "#f3f5fd", "#1f47b5"), ("1", "#fdf4f4", "#c0271e"), ("0", "#f3f5fd", "#1f47b5"),
                  ("0", "#f3f5fd", "#1f47b5"), ("1", "#fdf4f4", "#c0271e")]
    for idx, (b_digit, bg_col, stroke_col) in enumerate(bin_digits):
        rx = 230.0 + idx * 56.0
        lines.append(f'<rect x="{rx}" y="210.0" width="46.0" height="46.0" rx="6" fill="{bg_col}" stroke="{stroke_col}" stroke-width="2"/>')
        lines.append(f'<text x="{rx + 23.0}" y="240.4" font-family="{FONT_FAMILY}" font-size="17" fill="{stroke_col}" text-anchor="middle" font-weight="bold" font-style="normal">{b_digit}</text>')

    lines.append(f'<text x="120.0" y="290.0" font-family="{FONT_FAMILY}" font-size="12" fill="#8a8a8a" text-anchor="start" font-weight="normal" font-style="normal">8 розрядів (по 2 значення)</text>')
    lines.append(f'<text x="700.0" y="290.0" font-family="{FONT_FAMILY}" font-size="12.5" fill="#1f8a3b" text-anchor="end" font-weight="bold" font-style="normal">= 128+64+32+8+1 = 233</text>')

    lines.append(f'<text x="430.0" y="326.0" font-family="{FONT_FAMILY}" font-size="11.5" fill="#1b1b1b" text-anchor="middle" font-weight="bold" font-style="normal">Більше дротів/бітів — дешево; надійність кожного біта — безцінна. Тому машини обрали довшу, зате просту двійкову.</text>')

    lines.append(svg_footer())
    with open(os.path.join(IMG_DIR, "cost.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def gen_capacity():
    w, h = 880, 420
    lines = [svg_header(w, h)]
    lines.append(f'<text x="440.0" y="34.0" font-family="{FONT_FAMILY}" font-size="20" fill="#1b1b1b" text-anchor="middle" font-weight="bold" font-style="normal">Біт — один двійковий розряд; N бітів тримають 2ᴺ значень</text>')
    lines.append(f'<text x="440.0" y="56.0" font-family="{FONT_FAMILY}" font-size="12" fill="#8a8a8a" text-anchor="middle" font-weight="normal" font-style="italic">кожен доданий біт ПОДВОЮЄ кількість можливих комбінацій — місткість росте вибухово</text>')

    lines.append(f'<text x="144.0" y="96.0" font-family="{FONT_FAMILY}" font-size="12" fill="#1b1b1b" text-anchor="middle" font-weight="bold" font-style="normal">1 біт → 2</text>')
    lines.append(f'<text x="130.0" y="122.0" font-family="{FONT_FAMILY}" font-size="12" fill="#1f47b5" text-anchor="start" font-weight="bold" font-style="normal">0</text>')
    lines.append(f'<text x="130.0" y="144.0" font-family="{FONT_FAMILY}" font-size="12" fill="#c0271e" text-anchor="start" font-weight="bold" font-style="normal">1</text>')

    lines.append(f'<text x="294.0" y="96.0" font-family="{FONT_FAMILY}" font-size="12" fill="#1b1b1b" text-anchor="middle" font-weight="bold" font-style="normal">2 біт → 4</text>')
    lines.append(f'<text x="280.0" y="122.0" font-family="{FONT_FAMILY}" font-size="12" fill="#1f47b5" text-anchor="start" font-weight="bold" font-style="normal">00</text>')
    lines.append(f'<text x="280.0" y="144.0" font-family="{FONT_FAMILY}" font-size="12" fill="#c0271e" text-anchor="start" font-weight="bold" font-style="normal">01</text>')
    lines.append(f'<text x="280.0" y="166.0" font-family="{FONT_FAMILY}" font-size="12" fill="#c0271e" text-anchor="start" font-weight="bold" font-style="normal">10</text>')
    lines.append(f'<text x="280.0" y="188.0" font-family="{FONT_FAMILY}" font-size="12" fill="#c0271e" text-anchor="start" font-weight="bold" font-style="normal">11</text>')

    lines.append(f'<text x="454.0" y="96.0" font-family="{FONT_FAMILY}" font-size="12" fill="#1b1b1b" text-anchor="middle" font-weight="bold" font-style="normal">3 біт → 8</text>')
    lines.append(f'<text x="440.0" y="122.0" font-family="{FONT_FAMILY}" font-size="12" fill="#1f47b5" text-anchor="start" font-weight="bold" font-style="normal">000</text>')
    for idx, c_val in enumerate(["001", "010", "011", "100", "101", "110", "111"]):
        lines.append(f'<text x="440.0" y="{144.0 + idx * 22.0}" font-family="{FONT_FAMILY}" font-size="12" fill="#c0271e" text-anchor="start" font-weight="bold" font-style="normal">{c_val}</text>')

    lines.append('<rect x="580.0" y="90.0" width="270.0" height="240.0" rx="10" fill="#f4f7f4" stroke="#1f8a3b" stroke-width="1.6"/>')
    lines.append(f'<text x="715.0" y="116.0" font-family="{FONT_FAMILY}" font-size="13" fill="#1b1b1b" text-anchor="middle" font-weight="bold" font-style="normal">Місткість = 2ᴺ</text>')

    capacities = [
        ("1 біт", "2"),
        ("4 біти", "16"),
        ("8 бітів (байт)", "256"),
        ("16 бітів", "65 536"),
        ("32 біти", "≈ 4.3 млрд"),
        ("64 біти", "≈ 1.8·10¹⁹"),
    ]
    for idx, (b_label, cap_label) in enumerate(capacities):
        cy = 146.0 + idx * 30.0
        lines.append(f'<text x="600.0" y="{cy}" font-family="{FONT_FAMILY}" font-size="12" fill="#1b1b1b" text-anchor="start" font-weight="bold" font-style="normal">{b_label}</text>')
        lines.append(f'<text x="830.0" y="{cy}" font-family="{FONT_FAMILY}" font-size="12" fill="#1f8a3b" text-anchor="end" font-weight="bold" font-style="normal">{cap_label}</text>')

    lines.append(f'<text x="440.0" y="396.0" font-family="{FONT_FAMILY}" font-size="11.5" fill="#1b1b1b" text-anchor="middle" font-weight="bold" font-style="normal">Один біт — це 2 значення; вісім — уже 256; тридцять два — мільярди. Кожен біт коштує небагато, а дає вдвічі більше.</text>')

    lines.append(svg_footer())
    with open(os.path.join(IMG_DIR, "capacity.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def gen_byte():
    w, h = 880, 380
    lines = [svg_header(w, h)]
    lines.append(f'<text x="440.0" y="34.0" font-family="{FONT_FAMILY}" font-size="18.5" fill="#1b1b1b" text-anchor="middle" font-weight="bold" font-style="normal">Байт — 8 бітів (256 значень); але що вони ЗНАЧАТЬ — справа тлумачення</text>')
    lines.append(f'<text x="440.0" y="56.0" font-family="{FONT_FAMILY}" font-size="12" fill="#8a8a8a" text-anchor="middle" font-weight="normal" font-style="italic">вісім бітів — стандартна «порція»; самі по собі вони лише 0/1 — сенс їм надає домовленість</text>')

    weights = [128, 64, 32, 16, 8, 4, 2, 1]
    for idx, wt in enumerate(weights):
        bx = 210.0 + idx * 56.0
        lines.append(f'<rect x="{bx}" y="100.0" width="50.0" height="50.0" rx="6" fill="#fdf4f4" stroke="#c0271e" stroke-width="2"/>')
        lines.append(f'<text x="{bx + 25.0}" y="133.0" font-family="{FONT_FAMILY}" font-size="17" fill="#c0271e" text-anchor="middle" font-weight="bold" font-style="normal">1</text>')
        lines.append(f'<text x="{bx + 25.0}" y="92.0" font-family="{FONT_FAMILY}" font-size="10" fill="#8a8a8a" text-anchor="middle" font-weight="normal" font-style="normal">{wt}</text>')

    lines.append(f'<text x="198.0" y="132.0" font-family="{FONT_FAMILY}" font-size="13" fill="#1b1b1b" text-anchor="end" font-weight="bold" font-style="normal">байт:</text>')
    lines.append(f'<text x="434.0" y="178.0" font-family="{FONT_FAMILY}" font-size="11.5" fill="#8a8a8a" text-anchor="middle" font-weight="normal" font-style="italic">8 бітів = одна порція = 256 можливих значень (0…255)</text>')
    lines.append(f'<text x="440.0" y="220.0" font-family="{FONT_FAMILY}" font-size="13" fill="#1b1b1b" text-anchor="middle" font-weight="bold" font-style="normal">Ті самі 8 бітів 11111111 можуть означати:</text>')

    meanings = [
        (130.0, "255", "беззнакове ціле"),
        (320.0, "−1", "знакове ціле"),
        (510.0, "\'ÿ\'", "символ (код)"),
        (700.0, "0.996…", "дріб"),
    ]
    for mx, main_txt, sub_txt in meanings:
        lines.append(f'<rect x="{mx}" y="244.0" width="170.0" height="56.0" rx="8" fill="#fafafa" stroke="#1b1b1b" stroke-width="1.6"/>')
        lines.append(f'<text x="{mx + 85.0}" y="270.0" font-family="{FONT_FAMILY}" font-size="15" fill="#c0271e" text-anchor="middle" font-weight="bold" font-style="normal">{main_txt}</text>')
        lines.append(f'<text x="{mx + 85.0}" y="290.0" font-family="{FONT_FAMILY}" font-size="9.5" fill="#8a8a8a" text-anchor="middle" font-weight="normal" font-style="normal">{sub_txt}</text>')

    lines.append(f'<text x="440.0" y="340.0" font-family="{FONT_FAMILY}" font-size="11.5" fill="#1b1b1b" text-anchor="middle" font-weight="bold" font-style="normal">Біти однакові — а число різне, залежно від ДОМОВЛЕНОСТІ. Саме ці домовленості й кодують числа.</text>')

    lines.append(svg_footer())
    with open(os.path.join(IMG_DIR, "byte.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def gen_everything():
    w, h = 860, 360
    lines = [svg_header(w, h)]
    lines.append(f'<text x="430.0" y="34.0" font-family="{FONT_FAMILY}" font-size="19" fill="#1b1b1b" text-anchor="middle" font-weight="bold" font-style="normal">Усе цифрове — це біти; а ось як саме з бітів робити ЧИСЛА</text>')
    lines.append(f'<text x="430.0" y="56.0" font-family="{FONT_FAMILY}" font-size="11.5" fill="#8a8a8a" text-anchor="middle" font-weight="normal" font-style="italic">число, текст, зображення, звук — усе кодують тими самими 0 і 1; різниця лише в домовленості тлумачення</text>')

    # Central bits box
    lines.append('<rect x="360.0" y="150.0" width="160.0" height="60.0" rx="10" fill="#fff8e8" stroke="#caa24a" stroke-width="2"/>')
    lines.append(f'<text x="440.0" y="178.0" font-family="{FONT_FAMILY}" font-size="14" fill="#1b1b1b" text-anchor="middle" font-weight="bold" font-style="normal">0 1 0 1 1 0 …</text>')
    lines.append(f'<text x="440.0" y="198.0" font-family="{FONT_FAMILY}" font-size="11" fill="#9a7322" text-anchor="middle" font-weight="bold" font-style="normal">біти</text>')

    # Top-Left: ЧИСЛО
    lines.append('<rect x="50.0" y="104.0" width="160.0" height="52.0" rx="8" fill="#eef4ff" stroke="#1b1b1b" stroke-width="1.6"/>')
    lines.append(f'<text x="130.0" y="126.0" font-family="{FONT_FAMILY}" font-size="12" fill="#1f8a3b" text-anchor="middle" font-weight="bold" font-style="normal">ЧИСЛО</text>')
    lines.append(f'<text x="130.0" y="144.0" font-family="{FONT_FAMILY}" font-size="10" fill="#8a8a8a" text-anchor="middle" font-weight="normal" font-style="normal">233, −7, 3.14</text>')
    lines.append('<line x1="360.0" y1="180.0" x2="210.0" y2="130.0" stroke="#8a8a8a" stroke-width="1.6" stroke-dasharray="4 3" marker-end="url(#aInk)"/>')

    # Bottom-Left: ТЕКСТ (Ukrainian Cyrillic Т, NOT Latin T)
    lines.append('<rect x="50.0" y="214.0" width="160.0" height="52.0" rx="8" fill="#eef4ff" stroke="#1b1b1b" stroke-width="1.6"/>')
    lines.append(f'<text x="130.0" y="236.0" font-family="{FONT_FAMILY}" font-size="12" fill="#1b1b1b" text-anchor="middle" font-weight="bold" font-style="normal">ТЕКСТ</text>')
    lines.append(f'<text x="130.0" y="254.0" font-family="{FONT_FAMILY}" font-size="10" fill="#8a8a8a" text-anchor="middle" font-weight="normal" font-style="normal">\'A\' = 65</text>')
    lines.append('<line x1="360.0" y1="180.0" x2="210.0" y2="240.0" stroke="#8a8a8a" stroke-width="1.6" stroke-dasharray="4 3" marker-end="url(#aInk)"/>')

    # Top-Right: ЗОБРАЖЕННЯ
    lines.append('<rect x="650.0" y="104.0" width="160.0" height="52.0" rx="8" fill="#eef4ff" stroke="#1b1b1b" stroke-width="1.6"/>')
    lines.append(f'<text x="730.0" y="126.0" font-family="{FONT_FAMILY}" font-size="12" fill="#1b1b1b" text-anchor="middle" font-weight="bold" font-style="normal">ЗОБРАЖЕННЯ</text>')
    lines.append(f'<text x="730.0" y="144.0" font-family="{FONT_FAMILY}" font-size="10" fill="#8a8a8a" text-anchor="middle" font-weight="normal" font-style="normal">піксель = R,G,B</text>')
    lines.append('<line x1="520.0" y1="180.0" x2="650.0" y2="130.0" stroke="#8a8a8a" stroke-width="1.6" stroke-dasharray="4 3" marker-end="url(#aInk)"/>')

    # Bottom-Right: ЗВУК
    lines.append('<rect x="650.0" y="214.0" width="160.0" height="52.0" rx="8" fill="#eef4ff" stroke="#1b1b1b" stroke-width="1.6"/>')
    lines.append(f'<text x="730.0" y="236.0" font-family="{FONT_FAMILY}" font-size="12" fill="#1b1b1b" text-anchor="middle" font-weight="bold" font-style="normal">ЗВУК</text>')
    lines.append(f'<text x="730.0" y="254.0" font-family="{FONT_FAMILY}" font-size="10" fill="#8a8a8a" text-anchor="middle" font-weight="normal" font-style="normal">відлік амплітуди</text>')
    lines.append('<line x1="520.0" y1="180.0" x2="650.0" y2="240.0" stroke="#8a8a8a" stroke-width="1.6" stroke-dasharray="4 3" marker-end="url(#aInk)"/>')

    lines.append(f'<text x="440.0" y="300.0" font-family="{FONT_FAMILY}" font-size="12.5" fill="#1f8a3b" text-anchor="middle" font-weight="bold" font-style="normal">Розділ 17 — про лівий верхній квадрат: ЧИСЛА з 0 і 1</text>')
    lines.append(f'<text x="430.0" y="336.0" font-family="{FONT_FAMILY}" font-size="11" fill="#8a8a8a" text-anchor="middle" font-weight="normal" font-style="italic">Опанувавши числа, ви зрозумієте й решту: текст, колір, звук — це теж числа, лише інакше витлумачені.</text>')

    lines.append(svg_footer())
    with open(os.path.join(IMG_DIR, "everything.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    gen_timeline()
    gen_leibniz_idea()
    gen_iching()
    gen_convergence()
    gen_why_two()
    gen_cost()
    gen_capacity()
    gen_byte()
    gen_everything()
    print("All 9 figures generated successfully.")


if __name__ == "__main__":
    main()

import os
import sys

# Add scripts directory to path to import svgkit
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../scripts")))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def generate_shadow_memory_mapping():
    w_canvas, h_canvas = 850, 480
    svg_parts = []

    # Title
    svg_parts.append(text(425, 30, "Відображення пам'яті ядра в Shadow Memory (Generic KASAN)", size=18, bold=True, anchor="middle"))

    # Main Memory Container
    svg_parts.append(rect(40, 60, 770, 130, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    svg_parts.append(text(60, 85, "Віртуальна пам'ять ядра (64-бітні адреси)", size=12, color=MUTED, bold=True, anchor="start"))

    # 8 Bytes of Main Memory
    for i in range(8):
        x = 100 + i * 80
        svg_parts.append(rect(x, 105, 75, 60, fill="#e0f2fe", stroke="#0284c7", sw=1.5, rx=4))
        svg_parts.append(text(x + 37, 132, f"Байт {i}", size=11, bold=True, anchor="middle"))
        svg_parts.append(text(x + 37, 152, f"+0x0{i}", size=10, color=MUTED, anchor="middle"))

    # Address translation formula box
    b_formula, _, _ = textbox(425, 230, "Формула адресації тіньової пам'яті:\nS = (A >> 3) + KASAN_SHADOW_OFFSET", size=12, fill="#fef3c7", stroke="#d97706", bold=True)
    svg_parts.append(b_formula)

    # Arrows from Main Memory to Formula and Shadow Memory
    svg_parts.append(arrow(425, 170, 425, 205, color="#d97706", sw=2))
    svg_parts.append(arrow(425, 255, 425, 290, color=POS, sw=2))

    # Shadow Memory Container
    svg_parts.append(rect(40, 295, 770, 160, fill="#f0fdf4", stroke=POS, sw=1.5, rx=8))
    svg_parts.append(text(60, 320, "Тіньова пам'ять (1 байт на 8 байтів адресного простору)", size=12, color=POS, bold=True, anchor="start"))

    # Shadow byte explanation cells
    s1, _, _ = textbox(150, 385, "0x00\nУсі 8 байтів\nдоступні", size=11, fill="#ffffff", stroke=POS)
    s2, _, _ = textbox(330, 385, "0x01 .. 0x07\nПерші N байтів\nдоступні (padding)", size=11, fill="#ffffff", stroke="#0284c7")
    s3, _, _ = textbox(520, 385, "0xFC (KASAN_SLAB_FREE)\nВикористання після\nзвільнення (UAF)", size=11, fill="#fee2e2", stroke="#dc2626", bold=True)
    s4, _, _ = textbox(700, 385, "0xF1 / 0xFA\nЧервона зона\n(Out-of-Bounds)", size=11, fill="#fef3c7", stroke="#d97706", bold=True)

    svg_parts.extend([s1, s2, s3, s4])

    svg_content = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w_canvas} {h_canvas}" width="{w_canvas}" height="{h_canvas}">',
        '  <defs>',
        '    <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">',
        '      <path d="M0,0 L0,6 L9,3 z" fill="#333" />',
        '    </marker>',
        '  </defs>',
        '  <rect width="100%" height="100%" fill="#ffffff"/>',
        '\n'.join(svg_parts),
        '</svg>'
    ]

    out_path = os.path.join(IMG, "shadow-memory-mapping.svg")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_content))
    print(f"Generated {out_path}")


def generate_kasan_modes_comparison():
    w_canvas, h_canvas = 850, 500
    svg_parts = []

    # Title
    svg_parts.append(text(425, 30, "Порівняння режимів KASAN: Generic, SW Tag-Based та HW Tag-Based", size=18, bold=True, anchor="middle"))

    # Mode 1: Generic KASAN
    svg_parts.append(rect(30, 65, 250, 410, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    svg_parts.append(text(155, 95, "Generic KASAN", size=14, color="#1e293b", bold=True, anchor="middle"))
    m1_1, _, _ = textbox(155, 155, "Механізм:\nПрограмна Shadow Memory\n(пропорція 8:1)", size=11, fill="#ffffff", stroke="#64748b")
    m1_2, _, _ = textbox(155, 245, "Перевірка:\nІнструментування компілятора\n(__asan_load/store)", size=11, fill="#ffffff", stroke="#64748b")
    m1_3, _, _ = textbox(155, 335, "Накладні витрати:\nCPU: ~2x-3x уповільнення\nRAM: 1/8 пам'яті (~12.5%)", size=11, fill="#fee2e2", stroke="#dc2626")
    m1_4, _, _ = textbox(155, 425, "Призначення:\nРозробка, тестування,\nsyzkaller фазинг", size=11, fill="#e0f2fe", stroke="#0284c7")
    svg_parts.extend([m1_1, m1_2, m1_3, m1_4])

    # Mode 2: SW Tag-Based
    svg_parts.append(rect(300, 65, 250, 410, fill="#f8fafc", stroke="#0284c7", sw=1.5, rx=8))
    svg_parts.append(text(425, 95, "SW Tag-Based (SW_TAGS)", size=14, color="#0369a1", bold=True, anchor="middle"))
    m2_1, _, _ = textbox(425, 155, "Механізм:\nARM Top-Byte Ignore (TBI)\n8-бітні теги вказувачів", size=11, fill="#ffffff", stroke="#0284c7")
    m2_2, _, _ = textbox(425, 245, "Перевірка:\nПорівняння тегу вказувача\nі тегу в Shadow (16:1)", size=11, fill="#ffffff", stroke="#0284c7")
    m2_3, _, _ = textbox(425, 335, "Накладні витрати:\nCPU: ~1.5x-2x уповільнення\nRAM: 1/16 пам'яті (~6.25%)", size=11, fill="#fef3c7", stroke="#d97706")
    m2_4, _, _ = textbox(425, 425, "Призначення:\nТестування на ARM64\n(Android dogfooding)", size=11, fill="#e0f2fe", stroke="#0284c7")
    svg_parts.extend([m2_1, m2_2, m2_3, m2_4])

    # Mode 3: HW Tag-Based
    svg_parts.append(rect(570, 65, 250, 410, fill="#f0fdf4", stroke=POS, sw=1.5, rx=8))
    svg_parts.append(text(695, 95, "HW Tag-Based (HW_TAGS)", size=14, color="#15803d", bold=True, anchor="middle"))
    m3_1, _, _ = textbox(695, 155, "Механізм:\nARM MTE (Memory Tagging)\n4-бітні апаратні теги", size=11, fill="#ffffff", stroke=POS)
    m3_2, _, _ = textbox(695, 245, "Перевірка:\nАпаратна перевірка CPU\nпри LDR/STR інструкціях", size=11, fill="#ffffff", stroke=POS)
    m3_3, _, _ = textbox(695, 335, "Накладні витрати:\nCPU: < 5% уповільнення\nRAM: 0% програмної shadow", size=11, fill="#dcfce7", stroke=POS, bold=True)
    m3_4, _, _ = textbox(695, 425, "Призначення:\nProduction-сервери,\nмобільні пристрої в бою", size=11, fill="#dcfce7", stroke=POS)
    svg_parts.extend([m3_1, m3_2, m3_3, m3_4])

    svg_content = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w_canvas} {h_canvas}" width="{w_canvas}" height="{h_canvas}">',
        '  <rect width="100%" height="100%" fill="#ffffff"/>',
        '\n'.join(svg_parts),
        '</svg>'
    ]

    out_path = os.path.join(IMG, "kasan-modes-comparison.svg")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_content))
    print(f"Generated {out_path}")


def generate_kasan_quarantine_uaf():
    w_canvas, h_canvas = 850, 460
    svg_parts = []

    # Title
    svg_parts.append(text(425, 30, "Механізм Карантину KASAN для виявлення Use-After-Free", size=18, bold=True, anchor="middle"))

    # Step 1: kmalloc
    b1, _, _ = textbox(130, 110, "1. kmalloc(size)\nВиділення об'єкта в SLUB\nShadow = 0x00 (Valid)", size=11, fill="#e0f2fe", stroke="#0284c7", bold=True)
    svg_parts.append(b1)

    # Step 2: kfree -> Quarantine
    b2, _, _ = textbox(425, 110, "2. kfree(ptr)\nKASAN поміщає об'єкт у Quarantine\nShadow = 0xFC (KASAN_SLAB_FREE)", size=11, fill="#fef3c7", stroke="#d97706", bold=True)
    svg_parts.append(b2)

    # Step 3: Access attempt
    b3, _, _ = textbox(720, 110, "3. Звернення за ptr\nІнструкція читання/запису\nперевіряє Shadow Memory", size=11, fill="#fee2e2", stroke="#dc2626", bold=True)
    svg_parts.append(b3)

    # Arrow 1 -> 2
    svg_parts.append(arrow(210, 110, 310, 110, color="#0284c7", sw=2))

    # Arrow 2 -> 3
    svg_parts.append(arrow(540, 110, 610, 110, color="#d97706", sw=2))

    # Quarantine Queue Visualization Box
    svg_parts.append(rect(40, 190, 770, 130, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    svg_parts.append(text(60, 215, "Черга Карантину (Quarantine Queue FIFO)", size=12, color=MUTED, bold=True, anchor="start"))

    for i, name in enumerate(["Об'єкт A (0xFC)", "Об'єкт B (0xFC)", "Об'єкт C (0xFC)", "Об'єкт D (0xFC)"]):
        x = 100 + i * 160
        svg_parts.append(rect(x, 235, 130, 60, fill="#fee2e2", stroke="#dc2626", sw=1.5, rx=4))
        svg_parts.append(text(x + 65, 260, name, size=11, bold=True, anchor="middle"))
        svg_parts.append(text(x + 65, 280, "Повернуто в SLUB пізніше", size=9, color=MUTED, anchor="middle"))

    # Result Box
    b_res, _, _ = textbox(425, 395, "Результат: KASAN негайно фіксує читання 0xFC та генерує KASAN Bug Report у dmesg\nіз повним стеком викликів виділення (alloc) та звільнення (free)", size=11, fill="#f0fdf4", stroke=POS, bold=True)
    svg_parts.append(b_res)

    svg_parts.append(arrow(720, 140, 425, 360, color="#dc2626", sw=2))

    svg_content = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w_canvas} {h_canvas}" width="{w_canvas}" height="{h_canvas}">',
        '  <defs>',
        '    <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">',
        '      <path d="M0,0 L0,6 L9,3 z" fill="#333" />',
        '    </marker>',
        '  </defs>',
        '  <rect width="100%" height="100%" fill="#ffffff"/>',
        '\n'.join(svg_parts),
        '</svg>'
    ]

    out_path = os.path.join(IMG, "kasan-quarantine-uaf.svg")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_content))
    print(f"Generated {out_path}")


if __name__ == "__main__":
    generate_shadow_memory_mapping()
    generate_kasan_modes_comparison()
    generate_kasan_quarantine_uaf()

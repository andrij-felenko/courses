import sys
import os

scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../scripts"))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

from svgkit import rect, line, arrow, text, mtext, textbox, FONT, INK, FILL, MUTED, POS, NEG, FIELD

def build_svg_defs():
    return [
        '<defs>',
        '  <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 1 L 10 5 L 0 9 z" fill="#333333"/>',
        '  </marker>',
        '</defs>'
    ]

def render_lazy_binding():
    w, h = 860, 540
    parts = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    parts.extend(build_svg_defs())
    parts.append(f'<rect width="{w}" height="{h}" fill="#ffffff"/>')

    # Title
    parts.append(text(w / 2, 30, "Механізм відкладеного зв'язування: Перший виклик (Lazy Binding)", size=16, bold=True))

    # Column 1: Code Section (.plt)
    parts.append(rect(40, 60, 240, 450, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    parts.append(text(160, 85, "Секція коду (.plt / r-x)", size=13, bold=True, color="#1e293b"))

    # Block foo@plt
    parts.append(rect(50, 105, 220, 165, fill="#dbeafe", stroke="#3b82f6", sw=1.5, rx=6))
    parts.append(text(160, 125, "Трамплін foo@plt", size=12, bold=True, color="#1d4ed8"))
    parts.append(rect(60, 135, 200, 32, fill="#ffffff", stroke="#93c5fd", sw=1))
    parts.append(text(160, 155, "1. jmp *GOT[foo]", size=11, bold=True))
    parts.append(rect(60, 172, 200, 32, fill="#ffffff", stroke="#93c5fd", sw=1))
    parts.append(text(160, 192, "2. push reloc_index", size=11))
    parts.append(rect(60, 209, 200, 50, fill="#ffffff", stroke="#93c5fd", sw=1))
    parts.append(text(160, 229, "3. jmp PLT[0]", size=11, bold=True, color="#c2410c"))
    parts.append(text(160, 248, "(перехід на службовий)", size=10, color=MUTED))

    # Block PLT[0]
    parts.append(rect(50, 290, 220, 140, fill="#ffedd5", stroke="#f97316", sw=1.5, rx=6))
    parts.append(text(160, 310, "Службовий запис PLT[0]", size=12, bold=True, color="#c2410c"))
    parts.append(rect(60, 322, 200, 32, fill="#ffffff", stroke="#fdba74", sw=1))
    parts.append(text(160, 342, "push GOT[1] (link_map)", size=11))
    parts.append(rect(60, 359, 200, 60, fill="#ffffff", stroke="#fdba74", sw=1))
    parts.append(text(160, 379, "jmp *GOT[2]", size=11, bold=True, color="#b91c1c"))
    parts.append(text(160, 400, "(_dl_runtime_resolve)", size=10, color="#b91c1c"))

    # Column 2: Data Section (.got.plt)
    parts.append(rect(310, 60, 240, 450, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    parts.append(text(430, 85, "Секція даних (.got.plt / rw-)", size=13, bold=True, color="#1e293b"))

    parts.append(rect(320, 110, 220, 40, fill="#f1f5f9", stroke="#64748b", sw=1))
    parts.append(text(430, 128, "GOT[0]: .dynamic section", size=11))

    parts.append(rect(320, 155, 220, 40, fill="#f1f5f9", stroke="#64748b", sw=1))
    parts.append(text(430, 173, "GOT[1]: link_map ptr", size=11))

    parts.append(rect(320, 200, 220, 40, fill="#fee2e2", stroke="#ef4444", sw=1))
    parts.append(text(430, 218, "GOT[2]: resolver addr", size=11, bold=True, color="#b91c1c"))

    parts.append(rect(320, 260, 220, 75, fill="#fef9c3", stroke="#eab308", sw=1.5, rx=6))
    parts.append(text(430, 280, "GOT[foo] (Початковий стан)", size=11, bold=True, color="#854d0e"))
    parts.append(text(430, 298, "Вказує на foo@plt + 6", size=11, color="#854d0e"))
    parts.append(text(430, 318, "(повернення у трамплін!)", size=10, italic=True, color="#854d0e"))

    parts.append(rect(320, 355, 220, 75, fill="#dcfce7", stroke="#22c55e", sw=1.5, rx=6))
    parts.append(text(430, 375, "GOT[foo] (Оновлений стан)", size=11, bold=True, color="#15803d"))
    parts.append(text(430, 395, "Фізична адреса foo()", size=11, color="#15803d"))
    parts.append(text(430, 415, "в пам'яті libc.so", size=10, italic=True, color="#15803d"))

    # Column 3: Dynamic Linker & Shared Object
    parts.append(rect(580, 60, 240, 450, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    parts.append(text(700, 85, "Динамічний завантажувач", size=13, bold=True, color="#1e293b"))

    parts.append(rect(590, 150, 220, 110, fill="#fee2e2", stroke="#ef4444", sw=1.5, rx=6))
    parts.append(text(700, 175, "ld-linux.so", size=13, bold=True, color="#991b1b"))
    parts.append(text(700, 198, "_dl_runtime_resolve()", size=11, bold=True, color="#b91c1c"))
    parts.append(text(700, 220, "1. Пошук символу 'foo'", size=10, color="#7f1d1d"))
    parts.append(text(700, 238, "2. Перезапис GOT[foo]", size=10, bold=True, color="#7f1d1d"))

    parts.append(rect(590, 330, 220, 110, fill="#e0e7ff", stroke="#6366f1", sw=1.5, rx=6))
    parts.append(text(700, 355, "Бібліотека libc.so", size=13, bold=True, color="#3730a3"))
    parts.append(text(700, 380, "Реальний код foo()", size=12, bold=True, color="#4338ca"))
    parts.append(text(700, 405, "Виконання інструкцій", size=10, color="#312e81"))

    # Flow arrows
    # 1. foo@plt jump -> GOT[foo] initial
    parts.append(arrow(260, 151, 320, 275, color="#2563eb", sw=1.8))
    parts.append(text(290, 140, "Крок 1", size=10, bold=True, color="#2563eb"))

    # 2. GOT[foo] initial -> foo@plt instruction 2 (push reloc)
    parts.append(arrow(320, 300, 260, 192, color="#d97706", sw=1.8))
    parts.append(text(290, 265, "Крок 2", size=10, bold=True, color="#d97706"))

    # 3. PLT[0] jump -> GOT[2] resolver
    parts.append(arrow(260, 390, 320, 220, color="#c2410c", sw=1.8))

    # 4. GOT[2] -> _dl_runtime_resolve
    parts.append(arrow(540, 220, 590, 200, color="#b91c1c", sw=1.8))
    parts.append(text(565, 190, "Крок 3", size=10, bold=True, color="#b91c1c"))

    # 5. resolver updates GOT[foo] (horizontal arrow)
    parts.append(arrow(590, 392, 540, 392, color="#16a34a", sw=1.8))
    parts.append(text(565, 380, "Оновлення", size=10, bold=True, color="#16a34a"))

    # 6. resolver transfers execution to foo()
    parts.append(arrow(700, 260, 700, 330, color="#4338ca", sw=1.8))
    parts.append(text(735, 295, "Крок 5", size=10, bold=True, color="#4338ca"))

    parts.append("</svg>")
    return "\n".join(parts)

def render_resolved_call():
    w, h = 860, 360
    parts = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    parts.extend(build_svg_defs())
    parts.append(f'<rect width="{w}" height="{h}" fill="#ffffff"/>')

    # Title
    parts.append(text(w / 2, 30, "Повторний виклик: Прямий перехід через оновлений GOT", size=16, bold=True))

    # Column 1: PLT Stub
    parts.append(rect(50, 70, 240, 240, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    parts.append(text(170, 95, "Секція коду (.plt / r-x)", size=13, bold=True, color="#1e293b"))

    parts.append(rect(60, 115, 220, 170, fill="#dbeafe", stroke="#3b82f6", sw=1.5, rx=6))
    parts.append(text(170, 138, "Трамплін foo@plt", size=12, bold=True, color="#1d4ed8"))
    parts.append(rect(70, 150, 200, 45, fill="#dcfce7", stroke="#16a34a", sw=2))
    parts.append(text(170, 177, "jmp *GOT[foo]", size=12, bold=True, color="#15803d"))
    parts.append(rect(70, 205, 200, 30, fill="#f1f5f9", stroke="#cbd5e1", sw=1))
    parts.append(text(170, 224, "(push reloc_index)", size=10, color=MUTED))
    parts.append(rect(70, 240, 200, 30, fill="#f1f5f9", stroke="#cbd5e1", sw=1))
    parts.append(text(170, 259, "(jmp PLT[0])", size=10, color=MUTED))

    # Column 2: GOT entry
    parts.append(rect(320, 70, 240, 240, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    parts.append(text(440, 95, "Секція даних (.got.plt / rw-)", size=13, bold=True, color="#1e293b"))

    parts.append(rect(330, 130, 220, 130, fill="#dcfce7", stroke="#22c55e", sw=2, rx=6))
    parts.append(text(440, 160, "GOT[foo]", size=13, bold=True, color="#15803d"))
    parts.append(text(440, 190, "0x7fff... (адреса в RAM)", size=11, bold=True, color="#166534"))
    parts.append(text(440, 220, "Прямий вказівник на libc", size=10, italic=True, color="#14532d"))

    # Column 3: Destination libc function
    parts.append(rect(590, 70, 220, 240, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    parts.append(text(700, 95, "Спільна бібліотека (libc.so)", size=13, bold=True, color="#1e293b"))

    parts.append(rect(600, 130, 200, 130, fill="#e0e7ff", stroke="#6366f1", sw=1.5, rx=6))
    parts.append(text(700, 165, "Функція foo()", size=14, bold=True, color="#3730a3"))
    parts.append(text(700, 195, "Пряме виконання", size=11, color="#4338ca"))
    parts.append(text(700, 225, "Без участі ld-linux.so", size=10, italic=True, color="#312e81"))

    # Arrows
    parts.append(arrow(270, 172, 330, 172, color="#16a34a", sw=2.5))
    parts.append(text(300, 155, "1", size=11, bold=True, color="#16a34a"))

    parts.append(arrow(550, 172, 600, 172, color="#4338ca", sw=2.5))
    parts.append(text(575, 155, "2", size=11, bold=True, color="#4338ca"))

    parts.append("</svg>")
    return "\n".join(parts)

def render():
    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    
    path1 = os.path.join(out_dir, "plt-got-lazy-binding.svg")
    with open(path1, "w", encoding="utf-8") as f:
        f.write(render_lazy_binding())

    path2 = os.path.join(out_dir, "plt-got-resolved.svg")
    with open(path2, "w", encoding="utf-8") as f:
        f.write(render_resolved_call())

    print(f"Generated {path1} and {path2}")

if __name__ == "__main__":
    render()

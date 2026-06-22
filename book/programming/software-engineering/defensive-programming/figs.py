# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── where-to-check: периметрова оборона, а не рівномірна параноя ──────────────
# Ідея: три вкладені зони — недовірений світ (жовте кільце), межі модулів
# (зелене), гаряче ядро (сіре). Перевірки густо на кордонах, у ядрі — майже нема.
def fig_where_to_check():
    W, H = 720, 470
    cx, cy = 360, 250
    p = []

    # три вкладені зони
    p.append('<ellipse cx="%d" cy="%d" rx="178" ry="168" fill="#fff8ec" '
             'stroke="%s" stroke-width="3" stroke-dasharray="9 5"/>' % (cx, cy, POS))
    p.append('<ellipse cx="%d" cy="%d" rx="120" ry="112" fill="#eef9f0" '
             'stroke="%s" stroke-width="2.4"/>' % (cx, cy, FIELD))
    p.append('<ellipse cx="%d" cy="%d" rx="62" ry="58" fill="%s" '
             'stroke="%s" stroke-width="1.6"/>' % (cx, cy, FILL, MUTED))

    # підписи зон
    p.append(mtext(cx, cy - 4, ["гаряче ядро", "(довірені дані)"], size=11, color=MUTED))
    p.append(text(cx, cy - 128, "межі між модулями", size=12, color=FIELD, bold=True))
    p.append(text(cx, cy - 196, "недовірений світ: UART · мережа · давач · NVS · ввід",
                  size=12, color=POS, bold=True))

    # рамка-припис на зовнішньому кордоні (густа перевірка)
    b, bw, bh = textbox(cx, 48, "ПЕРЕВІРЯЙ: діапазон · довжина · magic · CRC · NULL",
                        size=12, bold=True, fill="#fff3cd", stroke=POS, sw=2.4)
    p.append(b)
    p.append(arrow(cx, 48 + bh / 2, cx, cy - 168 + 6, color=POS, sw=1.8))

    # рамка на межі модулів (легша перевірка)
    b2, bw2, bh2 = textbox(600, cy, ["передумови", "публічного API"],
                           size=11, fill="#eef9f0", stroke=FIELD, sw=2.0)
    p.append(b2)
    p.append(arrow(600 - bw2 / 2, cy, cx + 120 + 2, cy, color=FIELD, sw=1.6))

    # у ядрі — не дублюй
    p.append(mtext(cx, cy + 26, ["не дублюй", "не гальмуй"], size=10, color=MUTED))

    # рамка-«параноя» у гарячому циклі (перекреслена)
    b3 = fitbox(120, cy + 132, 150, 40, "перевірка в кожному\nрядку циклу",
                size=10, fill="#fdecea", stroke=POS, sw=1.4)
    p.append(b3)
    p.append(line(120, cy + 132, 270, cy + 172, color=POS, sw=2.2))
    p.append(line(120, cy + 172, 270, cy + 132, color=POS, sw=2.2))
    p.append(text(195, cy + 188, "марна параноя", size=9, color=POS))

    p.append(text(cx, H - 16,
                  "Перевіряй НЕДОВІРЕНЕ джерело й ДОРОГУ помилку. Не дублюй перевірку, за яку вже відповів виклик вище.",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "where-to-check.svg"), W, H, *p,
           title="Де перевіряти: периметрова оборона, а не рівномірна параноя")


# ── validate-packet: ланцюг перевірок кадру, кожна ловить свій клас біди ──────
# Ідея: сирий кадр угорі; п'ять воріт-перевірок одне за одним; провал кожних
# скидає кадр (червона гілка вниз), і лише наскрізний прохід пускає до payload.
def fig_validate_packet():
    W, H = 760, 470
    p = []

    # сирий кадр — поля
    fx, fy = 70, 70
    fields = [("magic", 70, "#fff3cd", POS), ("len", 52, "#eaf0fd", NEG),
              ("payload", 150, "#eef9f0", FIELD), ("CRC", 70, "#fdecea", POS)]
    x = fx
    for lab, w, fill, st in fields:
        p.append(rect(x, fy, w, 46, fill=fill, stroke=st, sw=1.8))
        p.append(text(x + w / 2, fy + 28, lab, size=11, color=INK))
        x += w
    p.append(text((fx + x) / 2, fy - 12, "сирий кадр з UART (недовірений)",
                  size=11, color=MUTED, italic=True))

    # ланцюг воріт
    gates = [
        ("buf != NULL", "крах за NULL-вказівником", POS, "#fff3cd"),
        ("len ≥ header", "читання за межами буфера", NEG, "#eaf0fd"),
        ("magic == 0xA55A", "чужий / зашумований кадр", FIELD, "#eef9f0"),
        ("payload_len у межах", "переповнення буфера (memcpy)", "#8a5fb0", "#f2ecf8"),
        ("CRC збігся", "биті дані (шум, пошкодження)", POS, "#fdecea"),
    ]
    gx, gw, gh = 70, 196, 40
    gy = 150
    step = 52
    prev_cx = (fx + x) / 2
    for i, (cond, threat, col, fill) in enumerate(gates):
        y = gy + i * step
        p.append(rect(gx, y, gw, gh, fill=fill, stroke=col, sw=2.0))
        p.append(text(gx + gw / 2, y + 25, cond, size=12, color=INK, bold=True))
        # вхід зверху
        p.append(arrow(prev_cx if i == 0 else gx + gw / 2, (fy + 46) if i == 0 else y - step + gh,
                       gx + gw / 2, y, color=MUTED, sw=1.5))
        prev_cx = gx + gw / 2
        # червона гілка «провал → скинути кадр»
        p.append(arrow(gx + gw, y + gh / 2, gx + gw + 150, y + gh / 2, color=POS, sw=1.8))
        p.append(text(gx + gw + 156, y + gh / 2 - 3,
                      "✗ %s" % threat, size=10, color=POS, anchor="start"))

    # лише наскрізний прохід → читаємо payload
    last_y = gy + (len(gates) - 1) * step + gh
    p.append(arrow(gx + gw / 2, last_y, gx + gw / 2, last_y + 22, color=FIELD, sw=2.0))
    b, bw, bh = textbox(gx + gw / 2, last_y + 40, "усі ворота пройдено → читаємо payload",
                        size=11, bold=True, color=FIELD, fill="#eef9f0", stroke=FIELD, sw=2.0)
    p.append(b)

    render(os.path.join(OUT, "validate-packet.svg"), W, H, *p,
           title="Розбір кадру: кожна перевірка — ворота на свій клас біди")


# ── validation-layers: чотири рівні валідації входу ───────────────────────────
# Ідея: дані ззовні проходять чотири сита згори вниз — існування, форма/розмір,
# діапазон, зміст. Кожне сито відсіює свій клас брехні; що нижче, то «розумніше».
def fig_validation_layers():
    W, H = 720, 400
    p = []
    layers = [
        ("1. Існування", "вказівник не NULL · поле присутнє", POS, "#fff3cd"),
        ("2. Форма й розмір", "довжина в межах · тип збігається · магічне число", NEG, "#eaf0fd"),
        ("3. Діапазон", "число у [min..max] · індекс < розміру", FIELD, "#eef9f0"),
        ("4. Зміст (семантика)", "значення правдоподібне · узгоджене з іншими полями", "#8a5fb0", "#f2ecf8"),
    ]
    bx, bw, bh = 150, 420, 56
    gap = 22
    y = 60
    p.append(text(W / 2, 46, "недовірений вхід", size=12, color=MUTED, italic=True))
    for i, (title, sub, col, fill) in enumerate(layers):
        yy = y + i * (bh + gap)
        p.append(rect(bx, yy, bw, bh, fill=fill, stroke=col, sw=2.0))
        p.append(text(bx + 14, yy + 23, title, size=12, color=INK, bold=True, anchor="start"))
        p.append(text(bx + 14, yy + 42, sub, size=10, color=MUTED, anchor="start"))
        # бічна гілка «провал → відкинути»
        p.append(arrow(bx + bw, yy + bh / 2, bx + bw + 96, yy + bh / 2, color=POS, sw=1.6))
        p.append(text(bx + bw + 100, yy + bh / 2 - 3, "✗ відкинути", size=10, color=POS, anchor="start"))
        if i < len(layers) - 1:
            p.append(arrow(bx + bw / 2, yy + bh, bx + bw / 2, yy + bh + gap, color=MUTED, sw=1.6))
    last = y + (len(layers) - 1) * (bh + gap) + bh
    p.append(arrow(bx + bw / 2, last, bx + bw / 2, last + 18, color=FIELD, sw=2.0))
    p.append(text(W / 2, last + 34, "пройшло всі рівні → дані довірені",
                  size=11, color=FIELD, bold=True))
    render(os.path.join(OUT, "validation-layers.svg"), W, H, *p,
           title="Чотири рівні валідації входу: від існування до змісту")


# ── clamp-vs-wrap: затиск проти мовчазного перевалювання ──────────────────────
# Ідея: те саме завелике значення. Зліва wrap кидає його на дно (стрибок),
# справа clamp притискає до стелі безпечного діапазону (плато).
def fig_clamp_vs_wrap():
    W, H = 720, 320
    p = []

    def axes(ox, oy, aw, ah, title):
        out = [arrow(ox, oy, ox, oy - ah - 8, color=INK, sw=1.5),
               arrow(ox, oy, ox + aw, oy, color=INK, sw=1.5),
               text(ox + aw / 2, oy + 30, "вхід зростає", size=10, color=MUTED, italic=True),
               text(ox + aw / 2, oy - ah - 18, title, size=12, color=INK, bold=True)]
        return out

    aw, ah = 250, 170
    oy = 250
    # ── ліворуч: wrap ──
    ox = 70
    p += axes(ox, oy, aw, ah, "wrap: тихо перевалює")
    cap = oy - ah * 0.78
    p.append(line(ox, cap, ox + aw, cap, color=MUTED, sw=1.2, dash="5 4"))
    p.append(text(ox + aw + 2, cap + 4, "межа", size=9, color=MUTED, anchor="start"))
    # лінія, що росте до межі, тоді падає на дно (перевалила)
    p.append('<polyline points="%.0f,%.0f %.0f,%.0f %.0f,%.0f %.0f,%.0f" '
             'fill="none" stroke="%s" stroke-width="2.6"/>'
             % (ox + 6, oy - 6, ox + aw * 0.6, cap + 4, ox + aw * 0.6, oy - 6,
                ox + aw - 6, oy - ah * 0.30, POS))
    p.append(text(ox + aw * 0.6, oy - 6 + 16, "стрибок на дно", size=10, color=POS))

    # ── праворуч: clamp ──
    ox = 400
    p += axes(ox, oy, aw, ah, "clamp: притискає до стелі")
    cap = oy - ah * 0.78
    band_lo = oy - 6
    p.append(rect(ox, cap, aw, oy - cap, fill="#eef9f0", stroke="none", sw=0, rx=0))
    p.append(line(ox, cap, ox + aw, cap, color=FIELD, sw=1.4, dash="5 4"))
    p.append(text(ox + aw + 2, cap + 4, "стеля", size=9, color=FIELD, anchor="start"))
    # лінія росте до межі й тримається плато
    p.append('<polyline points="%.0f,%.0f %.0f,%.0f %.0f,%.0f" '
             'fill="none" stroke="%s" stroke-width="2.6"/>'
             % (ox + 6, band_lo, ox + aw * 0.6, cap + 3, ox + aw - 6, cap + 3, FIELD))
    p.append(text(ox + aw * 0.72, cap - 8, "плато на межі", size=10, color=FIELD))

    p.append(text(W / 2, H - 12,
                  "Те саме завелике значення: wrap робить його малим і брехливим, clamp лишає на безпечній межі.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "clamp-vs-wrap.svg"), W, H, *p,
           title="Затиск (clamp) проти тихого перевалювання (wrap)")


if __name__ == "__main__":
    fig_where_to_check()
    fig_validate_packet()
    fig_validation_layers()
    fig_clamp_vs_wrap()
    print("OK: figures written to", OUT)

# -*- coding: utf-8 -*-
"""Фігури до статті «Лінії та з'єднання на схемі». Чистий Python, SVG через svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

WIRE = "#1a1a1a"      # дріт
WSW = 2.0            # товщина дроту
BUS = "#1a1a1a"      # шина
BSW = 5.0            # товщина шини


def dot(cx, cy, r=4.2):
    """Жирна крапка-з'єднання."""
    return '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (cx, cy, r, WIRE)


def pin(cx, cy, r=3.0):
    """Маленьке кружальце-вивід (кінець дроту)."""
    return circle(cx, cy, r, fill=BG, stroke=WIRE, sw=1.6)


# ── Фігура 1: крапка / перетин / місток ─────────────────────────────────────
def fig_dot_cross_hop():
    W, H = 720, 250
    parts = []
    cells = [
        (120, "З'ЄДНАНО", "крапка"),
        (360, "ПЕРЕТИН", "без крапки"),
        (600, "ПЕРЕТИН", "місток"),
    ]
    cy = 120
    for cx, top, bot in cells:
        # горизонтальний і вертикальний дроти
        parts.append(line(cx - 70, cy, cx + 70, cy, color=WIRE, sw=WSW))
    # — клітинка 1: крапка
    cx = 120
    parts.append(line(cx, cy - 60, cx, cy + 60, color=WIRE, sw=WSW))
    parts.append(dot(cx, cy))
    # — клітинка 2: суцільний перетин навхрест (вертикаль НЕ розривається)
    cx = 360
    parts.append(line(cx, cy - 60, cx, cy + 60, color=WIRE, sw=WSW))
    # — клітинка 3: місток-дуга (вертикаль перестрибує горизонталь)
    cx = 600
    parts.append(line(cx, cy - 60, cx, cy - 8, color=WIRE, sw=WSW))
    parts.append(line(cx, cy + 8, cx, cy + 60, color=WIRE, sw=WSW))
    # півколо-горб, що оминає горизонталь
    parts.append('<path d="M %.1f %.1f A 8 8 0 0 1 %.1f %.1f" fill="none" stroke="%s" stroke-width="%.1f"/>'
                 % (cx, cy - 8, cx, cy + 8, WIRE, WSW))
    # підписи
    for cx, top, bot in cells:
        parts.append(text(cx, 210, top, size=15, bold=True))
        parts.append(text(cx, 232, bot, size=13, color=MUTED))
    return render(os.path.join(IMG, "dot-cross-hop.svg"), W, H, *parts)


# ── Фігура 2: ортогональне розведення й напрям сигналу ──────────────────────
def fig_orthogonal():
    W, H = 720, 300
    parts = []
    # ── ліворуч: ПОГАНО — навскісні дроти, безлад ──
    parts.append(textbox(180, 40, "ПОГАНО", size=14, bold=True, fill="#fdecea", stroke=POS, color=POS)[0])
    a = (70, 110); b = (300, 90); c = (90, 230); d = (290, 215)
    parts.append(pin(*a)); parts.append(pin(*b)); parts.append(pin(*c)); parts.append(pin(*d))
    # навскісні + злам під випадковим кутом
    parts.append(line(a[0], a[1], 190, 160, color=POS, sw=WSW))
    parts.append(line(190, 160, b[0], b[1], color=POS, sw=WSW))
    parts.append(line(c[0], c[1], 200, 175, color=POS, sw=WSW))
    parts.append(line(200, 175, d[0], d[1], color=POS, sw=WSW))
    # ── праворуч: ДОБРЕ — лише прямі кути, сигнал зліва направо ──
    ox = 380
    parts.append(textbox(ox + 150, 40, "ДОБРЕ", size=14, bold=True, fill="#eafaf1", stroke=FIELD, color="#1e8449")[0])
    # вхід ліворуч → вихід праворуч, манхеттенська траса
    parts.append(pin(ox + 20, 110)); parts.append(pin(ox + 290, 110))
    parts.append(line(ox + 20, 110, ox + 150, 110, color=WIRE, sw=WSW))
    parts.append(line(ox + 150, 110, ox + 150, 215, color=WIRE, sw=WSW))
    parts.append(line(ox + 150, 215, ox + 290, 215, color=WIRE, sw=WSW))
    parts.append(pin(ox + 290, 215))
    # друга гілка з трійника
    parts.append(dot(ox + 150, 110))
    parts.append(line(ox + 150, 110, ox + 290, 110, color=WIRE, sw=WSW))
    # стрілка напряму
    parts.append('<line x1="%d" y1="265" x2="%d" y2="265" stroke="%s" stroke-width="2" marker-end="url(#arrow)"/>'
                 % (ox + 20, ox + 280, MUTED))
    parts.append(text(ox + 150, 285, "сигнал тече зліва направо", size=12, color=MUTED))
    return render(os.path.join(IMG, "orthogonal.svg"), W, H, *parts)


# ── Фігура 3: 4-перехрестя проти двох трійників ─────────────────────────────
def fig_tee_vs_cross():
    W, H = 720, 250
    parts = []
    cy = 120
    # ── ліворуч: двозначне 4-перехрестя з крапкою ──
    cx = 200
    parts.append(line(cx - 80, cy, cx + 80, cy, color=POS, sw=WSW))
    parts.append(line(cx, cy - 70, cx, cy + 70, color=POS, sw=WSW))
    parts.append(dot(cx, cy))
    parts.append(textbox(cx, 220, "4 дроти + крапка — двозначно", size=13, bold=True,
                         fill="#fdecea", stroke=POS, color=POS)[0])
    # ── праворуч: два зміщені трійники ──
    cx = 520
    # горизонталь
    parts.append(line(cx - 80, cy, cx + 80, cy, color=WIRE, sw=WSW))
    # верхня гілка входить лівіше
    parts.append(line(cx - 24, cy - 70, cx - 24, cy, color=WIRE, sw=WSW))
    parts.append(dot(cx - 24, cy))
    # нижня гілка входить правіше
    parts.append(line(cx + 24, cy + 70, cx + 24, cy, color=WIRE, sw=WSW))
    parts.append(dot(cx + 24, cy))
    parts.append(textbox(cx, 220, "два Т-з'єднання — однозначно", size=13, bold=True,
                         fill="#eafaf1", stroke=FIELD, color="#1e8449")[0])
    return render(os.path.join(IMG, "tee-vs-cross.svg"), W, H, *parts)


# ── Фігура 4: шина з відгалуженнями й мітками членів ────────────────────────
def fig_bus():
    W, H = 720, 320
    parts = []
    # товста шина по центру
    bx0, bx1, by = 120, 600, 70
    parts.append(line(bx0, by, bx1, by, color=BUS, sw=BSW))
    # ім'я шини
    parts.append(text(bx0 - 8, by - 12, "DATA[0..7]", size=15, bold=True, anchor="start"))
    # відгалуження: 45° entry stub + горизонтальна мітка члена
    members = [(180, "DATA0"), (300, "DATA1"), (420, "DATA2"), (540, "DATA7")]
    for x, name in members:
        # 45° «зрив» з шини
        parts.append(line(x, by, x + 22, by + 22, color=WIRE, sw=WSW))
        # вертикаль униз до піна
        parts.append(line(x + 22, by + 22, x + 22, 210, color=WIRE, sw=WSW))
        parts.append(pin(x + 22, 210))
        # мітка члена коло стуба (тег-стрілка)
        parts.append(_label(x + 22, by + 44, name, size=12))
    # пунктир-рамка з підписом про правило
    parts.append(_label(660, by, "вісім ліній", size=12, anchor="end"))
    note = ("Жирна лінія = ШИНА (жмут ліній). Скісні «зриви» — лише графіка;\n"
            "до конкретної лінії під'єднують МІТКОЮ члена (DATA0 = DATA0), не дротом.")
    parts.append(textbox(W / 2, 280, note, size=12.5, fill=FILL, stroke=MUTED)[0])
    return render(os.path.join(IMG, "bus.svg"), W, H, *parts)


def _label(x, y, s, size=12, anchor="middle", fill="#eef2ff", stroke=NEG):
    """Прямокутна мітка-тег ланцюга коло точки (x,y)."""
    w = text_width(s, size, True) + 14
    h = size + 10
    bx = x - w / 2 if anchor == "middle" else (x - w if anchor == "end" else x)
    out = rect(bx, y - h / 2, w, h, fill=fill, stroke=stroke, sw=1.4, rx=4)
    out += text(bx + w / 2, y + size * 0.35, s, size=size, color=INK, bold=True)
    return out


# ── Фігура 5: три способи «бездротового» з'єднання ──────────────────────────
def fig_labels_ports():
    W, H = 720, 300
    parts = []
    cols = [
        (130, "Локальна мітка", "у межах аркуша", "VCC"),
        (370, "Глобальна мітка", "по всіх аркушах", "VCC"),
        (610, "Міжаркушевий\nпорт", "вхід/вихід аркуша", "DATA"),
    ]
    for cx, title, sub, name in cols:
        parts.append(text(cx, 40, title.replace("\n", " "), size=14, bold=True))
        parts.append(text(cx, 60, sub, size=12, color=MUTED))
    # — локальна мітка: простий тег на кінці дроту
    cx = 130
    parts.append(pin(cx, 150)); parts.append(line(cx, 150, cx, 110, color=WIRE, sw=WSW))
    parts.append(_label(cx, 95, "VCC", fill="#eef2ff", stroke=NEG))
    parts.append(text(cx, 210, "тут і там «VCC»\n= один ланцюг", size=12, color=MUTED))
    parts[-1] = mtext(cx, 205, ["тут і там «VCC»", "= один ланцюг"], size=12, color=MUTED)
    # — глобальна мітка: тег-стрілка (шеврон)
    cx = 370
    parts.append(pin(cx, 150)); parts.append(line(cx, 150, cx, 110, color=WIRE, sw=WSW))
    parts.append(_chevron(cx, 95, "VCC", FIELD))
    parts.append(mtext(cx, 205, ["видно з будь-якого", "аркуша проєкту"], size=12, color=MUTED))
    # — міжаркушевий порт: рамка-конектор
    cx = 610
    parts.append(pin(cx, 150)); parts.append(line(cx, 150, cx, 110, color=WIRE, sw=WSW))
    parts.append(_offpage(cx, 92, "DATA"))
    parts.append(mtext(cx, 205, ["місток між", "аркушами"], size=12, color=MUTED))
    # роздільники
    parts.append(line(250, 75, 250, 230, color="#dddddd", sw=1))
    parts.append(line(490, 75, 490, 230, color="#dddddd", sw=1))
    return render(os.path.join(IMG, "labels-ports.svg"), W, H, *parts)


def _chevron(cx, cy, s, color):
    """Тег-шеврон (глобальна мітка) — пятикутник зі вістрям праворуч."""
    w = text_width(s, 12, True) + 22
    h = 22
    x0 = cx - w / 2
    pts = "%d,%d %d,%d %d,%d %d,%d %d,%d" % (
        x0, cy - h / 2, x0 + w - 10, cy - h / 2, x0 + w, cy,
        x0 + w - 10, cy + h / 2, x0, cy + h / 2)
    out = '<polygon points="%s" fill="#eafaf1" stroke="%s" stroke-width="1.6"/>' % (pts, color)
    out += text(cx - 4, cy + 4, s, size=12, color=INK, bold=True)
    return out


def _offpage(cx, cy, s):
    """Міжаркушевий конектор — рамка-«прапорець»."""
    w = text_width(s, 12, True) + 26
    h = 24
    x0 = cx - w / 2
    pts = "%d,%d %d,%d %d,%d %d,%d %d,%d %d,%d" % (
        x0, cy - h / 2, x0 + w - 12, cy - h / 2, x0 + w, cy,
        x0 + w - 12, cy + h / 2, x0, cy + h / 2, x0, cy - h / 2)
    out = '<polygon points="%s" fill="#fff7e6" stroke="#b9770e" stroke-width="1.6"/>' % pts
    out += text(cx - 5, cy + 4, s, size=12, color=INK, bold=True)
    return out


# ── Фігура 6: три механізми складання нетлиста (вставка proj-netlist-build) ──
def fig_build_pipeline():
    W, H = 720, 360
    parts = []
    # три «доріжки» зліва, що зливаються у нетлист праворуч
    lanes = [
        (70,  "ГЕОМЕТРІЯ", "дотик кінців і Т-дотики", FIELD, "#eafaf1"),
        (155, "ІМЕНА", "однойменні мітки", NEG, "#eef2ff"),
        (240, "ШИНА", "DATA[0..7] → 8 імен", "#b9770e", "#fff7e6"),
    ]
    lx0, lx1 = 30, 250          # межі лівої колонки-доріжок
    for cy, title, sub, col, fill in lanes:
        parts.append(rect(lx0, cy - 26, lx1 - lx0, 52, fill=fill, stroke=col, sw=1.6, rx=6))
        parts.append(text((lx0 + lx1) / 2, cy - 4, title, size=13, bold=True))
        parts.append(text((lx0 + lx1) / 2, cy + 15, sub, size=11, color=MUTED))

    # ── центральний блок union-find ──
    ux0, uy0, uw, uh = 320, 110, 120, 130
    parts.append(rect(ux0, uy0, uw, uh, fill=FILL, stroke=INK, sw=1.8, rx=8))
    parts.append(text(ux0 + uw / 2, uy0 + 26, "union-find", size=14, bold=True))
    parts.append(mtext(ux0 + uw / 2, uy0 + 52,
                       ["злити", "сполучені", "вузли"], size=12, color=MUTED))
    # маленькі «множини», що зливаються в один корінь
    yy = uy0 + 100
    parts.append(dot(ux0 + 30, yy, 5)); parts.append(dot(ux0 + 60, yy, 5))
    parts.append(dot(ux0 + 90, yy, 5))
    parts.append(line(ux0 + 30, yy, ux0 + 90, yy, color=INK, sw=1.6))

    # стрілки від доріжок до union-find
    for cy, *_ in lanes:
        parts.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="%s" '
                     'stroke-width="1.8" marker-end="url(#arrow)"/>'
                     % (lx1 + 4, cy, ux0 - 4, uy0 + uh / 2, MUTED))

    # ── правий блок: готовий нетлист ──
    nx0, ny0, nw = 510, 95, 180
    rows = ["+5В: U1.1  U2.8  C3.1",
            "DATA3: U1.5  U2.12",
            "LED_EN: U1.7  R4.2",
            "GND: U1.4  U2.10 …"]
    nh = 40 + len(rows) * 26
    parts.append(rect(nx0, ny0, nw, nh, fill=BG, stroke=INK, sw=1.8, rx=8))
    parts.append(text(nx0 + nw / 2, ny0 + 24, "НЕТЛИСТ", size=14, bold=True))
    for i, r in enumerate(rows):
        parts.append(text(nx0 + 12, ny0 + 50 + i * 26, r, size=12,
                          color=INK, anchor="start"))
    # стрілка union-find → нетлист
    parts.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="%s" '
                 'stroke-width="2" marker-end="url(#arrow)"/>'
                 % (ux0 + uw + 4, uy0 + uh / 2, nx0 - 4, ny0 + nh / 2, INK))

    # підпис унизу
    parts.append(text(W / 2, 340,
                      "три механізми → один перелік ланцюгів із пінами",
                      size=12.5, color=MUTED))
    return render(os.path.join(IMG, "build-pipeline.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_dot_cross_hop()
    fig_orthogonal()
    fig_tee_vs_cross()
    fig_bus()
    fig_labels_ports()
    fig_build_pipeline()
    print("figs done")

# -*- coding: utf-8 -*-
"""Фігури до статті «Ієрархічні та багатоаркушні схеми». Чистий Python, SVG через svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

WIRE = "#1a1a1a"
WSW = 1.8


def sheet(x, y, w, h, label, fill=BG, stroke=INK, sw=1.8):
    """Прямокутник-аркуш із підписом угорі всередині."""
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=4)
    out += text(x + w / 2, y + 17, label, size=12, bold=True)
    return out


def block(x, y, w, h, label, fill="#eef2ff", stroke=NEG):
    """Блок-символ (обкладинка дочірнього аркуша)."""
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.8, rx=4)
    out += text(x + w / 2, y + h / 2 + 4, label, size=11, bold=True)
    return out


def namelabel(x, y, s, fill="#eafaf1", stroke=FIELD):
    """Тег-мітка ланцюга (зшивання за іменем)."""
    w = text_width(s, 11, True) + 12
    h = 19
    out = rect(x - w / 2, y - h / 2, w, h, fill=fill, stroke=stroke, sw=1.3, rx=3)
    out += text(x, y + 4, s, size=11, color=INK, bold=True)
    return out


# ── Фігура 1: три устрої набору аркушів ─────────────────────────────────────
def fig_three_structures():
    W, H = 760, 360
    parts = []
    # три колонки-панелі
    panels = [(20, "ПЛОСКИЙ"), (270, "ПРОСТА ІЄРАРХІЯ"), (520, "СКЛАДНА ІЄРАРХІЯ")]
    pw = 220
    for px, title in panels:
        parts.append(rect(px, 40, pw, 300, fill="#fbfcfd", stroke="#dddddd", sw=1.2, rx=8))
        parts.append(text(px + pw / 2, 62, title, size=13, bold=True))

    # ── ПЛОСКИЙ: три рівні аркуші, зв'язані спільним іменем ──
    px = 20
    cx = px + pw / 2
    for i, lab in enumerate(("Живлення", "Аналог", "Цифра")):
        sy = 90 + i * 70
        parts.append(sheet(cx - 75, sy, 150, 50, lab))
    # спільне ім'я +5В збоку, що «зшиває» всі три
    for i in range(3):
        sy = 90 + i * 70 + 25
        parts.append(line(cx + 75, sy, cx + 96, sy, color=FIELD, sw=1.4, dash="3 3"))
    parts.append(namelabel(cx + 96, 90 + 70 + 25, "+5В"))
    parts.append(text(cx, 332, "зв'язок лише за іменем", size=10.5, color=MUTED))

    # ── ПРОСТА ІЄРАРХІЯ: корінь + дерево, кожен блок раз ──
    px = 270
    cx = px + pw / 2
    # корінь із трьома блоками
    parts.append(sheet(cx - 95, 88, 190, 64, "Корінь", fill="#f4f6f8"))
    bx = [cx - 80, cx - 18, cx + 44]
    for x in bx:
        parts.append(block(x, 116, 56, 28, ""))
    # три дочірні аркуші під коренем
    for j, x in enumerate(bx):
        cxd = x + 28
        parts.append(line(cxd, 144, cxd, 188, color=INK, sw=1.4, marker="arrow"))
        parts.append(sheet(cxd - 30, 188, 60, 46, "A%d" % (j + 1)))
    parts.append(text(cx, 332, "кожен аркуш — один раз", size=10.5, color=MUTED))

    # ── СКЛАДНА ІЄРАРХІЯ: один аркуш-визначення, 3 екземпляри ──
    px = 520
    cx = px + pw / 2
    parts.append(sheet(cx - 95, 88, 190, 50, "Корінь", fill="#f4f6f8"))
    # три однакові блоки «Канал»
    inst = [cx - 78, cx - 22, cx + 34]
    for k, x in enumerate(inst):
        parts.append(block(x, 110, 50, 24, "Канал"))
        cxd = x + 25
        parts.append(line(cxd, 134, cxd, 196, color=INK, sw=1.3, marker="arrow"))
    # один аркуш-визначення, на який вказують усі три
    defx = cx
    parts.append(sheet(defx - 42, 196, 84, 50, "Канал", fill="#fff7e6", stroke="#b9770e"))
    parts.append(text(defx, 232, "(один лист)", size=9.5, color=MUTED))
    parts.append(mtext(cx, 318, ["один аркуш-визначення,", "багато екземплярів"], size=10.5, color=MUTED))
    return render(os.path.join(IMG, "three-structures.svg"), W, H, *parts)


# ── Фігура 2: поділ реальної плати на аркуші ────────────────────────────────
def fig_sheet_map():
    W, H = 760, 380
    parts = []
    # корінь-карта зверху
    rx, ry, rw, rh = 250, 50, 260, 60
    parts.append(sheet(rx, ry, rw, rh, "Корінь — карта системи", fill="#f4f6f8"))
    parts.append(text(rx + rw / 2, ry + 42, "Аркуш 1 з 4", size=10.5, color=MUTED))

    # чотири функціональні аркуші внизу
    cells = [
        (40,  "Живлення",      "стабілізатори, шини", "Арк. 2"),
        (230, "MCU",           "мікроконтролер",      "Арк. 3"),
        (420, "Аналог. тракт", "підсилювач, фільтр",  "Арк. 4"),
        (610, "Роз'єми",       "зовнішні конектори",  "Арк. 5"),
    ]
    sy, sw_, sh = 230, 150, 86
    centres = []
    for sx, title, sub, num in cells:
        parts.append(sheet(sx, sy, sw_, sh, title))
        parts.append(text(sx + sw_ / 2, sy + 42, sub, size=10.5, color=MUTED))
        parts.append(text(sx + sw_ / 2, sy + 70, num, size=10, color=MUTED))
        centres.append(sx + sw_ / 2)
    # лінії корінь → аркуші (дерево навігації)
    rootbot = (rx + rw / 2, ry + rh)
    for cxx in centres:
        parts.append(line(rootbot[0], rootbot[1], cxx, sy, color="#bbbbbb", sw=1.2, dash="4 4"))

    # шина живлення +3.3В / GND — глобальне ім'я на всі аркуші
    busY = sy + sh + 34
    parts.append(line(centres[0] - 30, busY, centres[-1] + 30, busY, color=FIELD, sw=4))
    parts.append(namelabel(centres[0] - 30, busY, "+3.3В / GND"))
    for cxx in centres:
        parts.append(line(cxx, sy + sh, cxx, busY, color=FIELD, sw=1.4, dash="3 3"))
    parts.append(text(W / 2, busY + 26, "шини живлення — глобальним іменем на всі аркуші",
                      size=11, color=MUTED))

    # сигнальний ланцюг між MCU та аналогом — міжаркушевий конектор за іменем
    sigY = sy - 16
    parts.append(line(centres[1] + 20, sigY, centres[2] - 20, sigY, color=NEG, sw=1.6, dash="2 3"))
    parts.append(namelabel((centres[1] + centres[2]) / 2, sigY, "ADC_IN", fill="#eef2ff", stroke=NEG))
    return render(os.path.join(IMG, "sheet-map.svg"), W, H, *parts)


# ── Фігура 3 (до вставки-історії): родовід багатоаркушного оформлення ────────
def fig_sheet_history():
    """Вертикальна стрічка часу: як збиралися штамп, нумерація й перехресні
    посилання — від креслярні Селлерса до елементів редактора схем."""
    W, H = 760, 540
    parts = []

    # хребет стрічки
    axx = 150
    top, bot = 70, H - 40
    parts.append(line(axx, top, axx, bot, color=MUTED, sw=2.5))

    # віхи: (рік, заголовок, опис праворуч)
    rows = [
        ("≈1878", "Кут штампа усталюється",
         "Креслярня В. Селлерса (Філадельфія):\nлегенда стало в правому нижньому куті"),
        ("≈1885", "Зміст штампа стандартизують",
         "номер документа за таксономією\nтипів машин і креслень"),
        ("1935", "Перший національний стандарт",
         "ASA «Drawings and Drafting Room Practice»:\nформат аркуша, лінії, шрифт, поля"),
        ("1940-ві", "Воєнна стандартизація",
         "однаковий папір на десятки заводів;\nверсії аркушів — питання збирання"),
        ("Y14 / 61082", "Писане правило",
         "ASME Y14.1 (формат) · Y14.100 (практики)\nIEC 61082 (електротехнічні документи)"),
        ("САПР", "Перенесено в редактор схем",
         "title block · «Аркуш N з M» ·\noff-page connector · sheet symbol"),
    ]
    n = len(rows)
    span = bot - top
    for i, (yr, head, body) in enumerate(rows):
        cy = top + span * (i + 0.5) / n
        last = (i == n - 1)
        dot = FIELD if last else NEG
        parts.append(circle(axx, cy, 7, fill=dot, stroke=BG, sw=2.5))
        # рік ліворуч від хребта
        parts.append(text(axx - 18, cy - 4, yr, size=12, color=INK, bold=True, anchor="end"))
        # картка віхи праворуч
        bx, bw = axx + 28, W - (axx + 28) - 22
        bh = 60
        parts.append(rect(bx, cy - bh / 2, bw, bh,
                          fill=("#eafaf1" if last else FILL),
                          stroke=(FIELD if last else LINE), sw=1.4, rx=5))
        parts.append(line(axx + 7, cy, bx, cy, color=MUTED, sw=1.4))
        parts.append(text(bx + 12, cy - 11, head, size=12.5, color=INK, bold=True, anchor="start"))
        for j, ln in enumerate(body.split("\n")):
            parts.append(text(bx + 12, cy + 6 + j * 15, ln, size=10.5, color=MUTED, anchor="start"))

    parts.append(text(W / 2, 36, "Як збиралося багатоаркушне оформлення креслення",
                      size=15, bold=True))
    return render(os.path.join(IMG, "sheet-history.svg"), W, H, *parts)


# svgkit.line не приймає marker — додамо тонку обгортку зі стрілкою
def _patch_line_marker():
    """Дозволити line(..., marker='arrow') через monkey-patch локально."""
    import svgkit
    orig = svgkit.line

    def line2(x1, y1, x2, y2, color=svgkit.LINE, sw=1.5, dash=None, marker=None):
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        m = ' marker-end="url(#arrow)"' if marker else ''
        return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                'stroke-width="%.1f"%s%s/>' % (x1, y1, x2, y2, color, sw, d, m))
    svgkit.line = line2
    globals()["line"] = line2


if __name__ == "__main__":
    _patch_line_marker()
    fig_three_structures()
    fig_sheet_map()
    fig_sheet_history()
    print("figs done")

# -*- coding: utf-8 -*-
"""Фігури до статті «З'єднання без дротів: мітки, шини й міжаркушеві зв'язки».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).
Символи схеми малюються лінійними примітивами svgkit; рамки з текстом —
через textbox()/fitbox(), тож написи гарантовано не вилазять за межі."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

WIRE_SW = 2.0
LABELCOL = "#e08030"   # колір мітки-ланцюга (той самий відтінок, що в reading-schematics)


def wire(x1, y1, x2, y2, sw=WIRE_SW, color=INK):
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
            'stroke-width="%.1f" stroke-linecap="round"/>' % (x1, y1, x2, y2, color, sw))


def dot(cx, cy, r=3.2, color=INK):
    return circle(cx, cy, r, fill=color, stroke=color, sw=1)


def label_tag(cx, cy, s, col=LABELCOL, w=None):
    """Мітка-ланцюг: прямокутник-«ярличок» із назвою всередині."""
    if w is None:
        w = max(40, text_width(s, 11, True) + 14)
    out = rect(cx - w / 2, cy - 12, w, 24, fill="#fff7e6", stroke=col, sw=1.5, rx=4)
    out += text(cx, cy + 5, s, size=11, color=col, bold=True)
    return out, w


def pin_block(cx, cy, w, h, name, col=NEG, sub=None):
    out = rect(cx - w / 2, cy - h / 2, w, h, fill="#eef2fb", stroke=col, sw=2, rx=8)
    out += text(cx, cy - (4 if sub else -5), name, size=13, color=col, bold=True)
    if sub:
        out += text(cx, cy + 16, sub, size=9.5, color=INK)
    return out


# ── 1) Навіщо мітки: та сама схема — павутиною і за іменами ──────────────────
def fig_why_labels():
    """Ліворуч жмут дротів, що плутано перетинаються; праворуч ті самі
    з'єднання, замінені однаковими мітками. Одне коло — два креслення."""
    W, H = 780, 380
    frags = []
    # заголовки половин
    frags.append(text(200, 62, "Дротами: лінії плутаються", size=13, color=POS, bold=True))
    frags.append(text(580, 62, "Мітками: чисто", size=13, color=FIELD, bold=True))
    frags.append(line(390, 74, 390, 344, color="#d0d5dd", sw=1.4, dash="5 6"))

    # ── ЛІВА половина: три блоки, з'єднані дротами навхрест ──
    # три блоки-прямокутники
    lb = [(90, 110, "МК"), (300, 110, "давач"), (90, 280, "драйвер")]
    for x, y, nm in lb:
        frags.append(pin_block(x, y, 96, 54, nm))
    # заплутані дроти (навмисно перетинаються)
    frags.append(wire(138, 110, 200, 200, color=INK))
    frags.append(wire(200, 200, 252, 110, color=INK))
    frags.append(wire(138, 130, 138, 253, color=INK))
    frags.append(wire(300, 137, 300, 230, color=INK))
    frags.append(wire(300, 230, 138, 300, color=INK))
    frags.append(wire(252, 96, 138, 96, color=INK))
    frags.append(wire(348, 96, 348, 300, color=INK))
    frags.append(wire(348, 300, 138, 300, color=INK))
    # перетини без крапок — показати навхрест
    frags.append(dot(138, 300))
    frags.append(text(200, 355, "погляд плутається у клубку", size=10, color=MUTED))

    # ── ПРАВА половина: ті самі блоки, але з'єднання — мітками ──
    rb = [(515, 115, "МК"), (700, 115, "давач"), (515, 265, "драйвер")]
    for x, y, nm in rb:
        frags.append(pin_block(x, y, 96, 54, nm))
    # кожен вивід дістає коротку лінію + ярличок-мітку, розведений НАЗОВНІ,
    # щоб мітки не наповзали одна на одну (панель має читатися чисто)
    def w0(name):
        return max(40, text_width(name, 11, True) + 14)
    # DATA: у МК тег ліворуч (назовні), у давача — праворуч (назовні) → та сама назва
    frags.append(wire(467, 105, 447, 105))
    t, _ = label_tag(447 - w0("DATA") / 2 - 2, 105, "DATA"); frags.append(t)
    frags.append(wire(748, 105, 768, 105))
    t, _ = label_tag(768 - w0("DATA") / 2, 105, "DATA"); frags.append(t)
    # EN: у МК тег донизу, у драйвера — теж донизу → та сама назва
    frags.append(wire(515, 142, 515, 160))
    t, _ = label_tag(515, 173, "EN"); frags.append(t)
    frags.append(wire(515, 292, 515, 310))
    t, _ = label_tag(515, 323, "EN"); frags.append(t)
    frags.append(text(680, 205, "однакові імена =", size=10, color=MUTED))
    frags.append(text(680, 221, "ті самі з'єднання", size=10, color=MUTED))
    render(os.path.join(IMG, "why-labels.svg"), W, H, *frags,
           title="Те саме коло: павутиною дротів і за іменами")


# ── 2) Мітка з'єднує за іменем; одруківка тихо рве вузол ─────────────────────
def fig_net_label():
    """Зверху: дві далекі точки з міткою MOTOR_EN — один вузол. Знизу: та сама
    схема, але друга мітка з одруківкою MOTOR_FN — редактор бачить ДВА вузли."""
    W, H = 780, 360
    frags = []
    # ── ВЕРХ: правильно ──
    y = 110
    frags.append(text(60, 70, "Однакова назва → один вузол", size=13, color=FIELD,
                      anchor="start", bold=True))
    frags.append(pin_block(120, y, 90, 50, "МК"))
    frags.append(wire(165, y, 210, y))
    t, w = label_tag(232, y, "MOTOR_EN"); frags.append(t)
    frags.append(pin_block(660, y, 96, 50, "драйвер"))
    frags.append(wire(615, y, 570, y))
    t, w = label_tag(548, y, "MOTOR_EN", w=w); frags.append(t)
    # «невидимий» зв'язок між ними — пунктир + галочка
    frags.append(line(276, y + 20, 526, y + 20, color=FIELD, sw=1.4, dash="4 5"))
    frags.append(text(400, y + 38, "з'єднано, хоч дроту немає  ✓", size=10.5, color=FIELD))

    # ── НИЗ: одруківка ──
    y = 250
    frags.append(text(60, 212, "Одна літера різниться → мовчазний розрив",
                      size=13, color=POS, anchor="start", bold=True))
    frags.append(pin_block(120, y, 90, 50, "МК"))
    frags.append(wire(165, y, 210, y))
    t, w = label_tag(232, y, "MOTOR_EN", col=POS); frags.append(t)
    frags.append(pin_block(660, y, 96, 50, "драйвер"))
    frags.append(wire(615, y, 570, y))
    t, w = label_tag(548, y, "MOTOR_FN", col=POS, w=w); frags.append(t)
    # розрив — два хрестики
    frags.append(line(300, y + 20, 500, y + 20, color=POS, sw=1.4, dash="4 5"))
    frags.append(text(400, y + 38, "EN ≠ FN → два різні кола, драйвер «мертвий»  ✗",
                      size=10.5, color=POS))
    render(os.path.join(IMG, "net-label.svg"), W, H, *frags,
           title="Мітка з'єднує за назвою — і за назвою ж розривається")


# ── 3) Шина: жмут ліній однією товстою, зрив члена за іменем ─────────────────
def fig_bus():
    """Вісім ліній D0..D7 збігаються в товсту шину D[7..0]; праворуч зрив
    одного члена D3 скісною рискою + мітка на пін приймача."""
    W, H = 780, 380
    frags = []
    BUS = FIELD
    # блок-джерело ліворуч з 8 виводами
    frags.append(rect(60, 90, 70, 200, fill="#eef2fb", stroke=NEG, sw=2, rx=8))
    frags.append(text(95, 84, "пам'ять", size=11, color=NEG, bold=True))
    ys = [110 + i * 24 for i in range(8)]
    for i, yy in enumerate(ys):
        nm = "D%d" % (7 - i)
        frags.append(wire(130, yy, 165, yy, sw=1.6))
        frags.append(text(160, yy - 4, nm, size=9, color=MUTED, anchor="end"))
        # скіс у шину
        frags.append(wire(165, yy, 200, 190 + (i - 3.5) * 3, sw=1.4))
    # товста шина
    frags.append(wire(200, 190, 560, 190, sw=6.0, color=BUS))
    frags.append(text(380, 178, "D[7..0]", size=13, color=BUS, bold=True))
    frags.append(text(380, 214, "одна товста лінія = вісім проводів", size=10, color=MUTED))

    # зрив члена D3 праворуч
    frags.append(wire(500, 190, 535, 120, sw=1.4))          # скісний зрив (bus entry)
    t, w = label_tag(560, 120, "D3"); frags.append(t)
    frags.append(wire(583, 120, 630, 120, sw=1.6))
    frags.append(rect(630, 96, 90, 60, fill="#eef2fb", stroke="#e08030", sw=2, rx=8))
    frags.append(text(675, 122, "АЦП", size=12, color="#e08030", bold=True))
    frags.append(text(675, 140, "вхід D3", size=9, color=INK))
    frags.append(text(600, 168, "зрив вибирає один член за іменем", size=9.5, color=MUTED))
    render(os.path.join(IMG, "bus.svg"), W, H, *frags,
           title="Шина: жмут однакових ліній — однією товстою")


# ── 4) Міжаркушевий зв'язок: сигнал переходить межу аркуша за іменем ─────────
def fig_off_sheet():
    """Два аркуші поряд; сигнал VBAT виходить з аркуша 1 через п'ятикутник-
    конектор і входить в аркуш 2 через такий самий — зшито за іменем."""
    W, H = 780, 340
    frags = []
    POSc = POS
    # два «аркуші» — рамки
    frags.append(rect(40, 80, 320, 210, fill="#fbfbfd", stroke=LINE, sw=1.4, rx=10))
    frags.append(rect(420, 80, 320, 210, fill="#fbfbfd", stroke=LINE, sw=1.4, rx=10))
    frags.append(text(60, 104, "Аркуш 1 — живлення", size=12, color=INK, anchor="start", bold=True))
    frags.append(text(440, 104, "Аркуш 2 — контролер", size=12, color=INK, anchor="start", bold=True))

    # аркуш 1: LDO → вихід VBAT
    frags.append(rect(80, 150, 90, 60, fill=FILL, stroke=POSc, sw=1.8, rx=6))
    frags.append(text(125, 176, "LDO", size=12, color=POSc, bold=True))
    frags.append(text(125, 194, "3.3 В", size=9, color=INK))
    frags.append(wire(170, 180, 250, 180))
    # п'ятикутник-конектор, що вказує праворуч (вихід)
    frags.append('<polygon points="250,%d 310,%d 334,%d 310,%d 250,%d" fill="#fdecea" '
                 'stroke="%s" stroke-width="1.8"/>' % (167, 167, 180, 193, 193, POSc))
    frags.append(text(286, 185, "VBAT", size=10, color=POSc, bold=True))

    # аркуш 2: приймальний конектор → МК
    frags.append('<polygon points="490,%d 430,%d 406,%d 430,%d 490,%d" fill="#fdecea" '
                 'stroke="%s" stroke-width="1.8"/>' % (167, 167, 180, 193, 193, POSc))
    frags.append(text(454, 185, "VBAT", size=10, color=POSc, bold=True))
    frags.append(wire(490, 180, 560, 180))
    frags.append(rect(560, 150, 110, 60, fill="#eef2fb", stroke=NEG, sw=2, rx=8))
    frags.append(text(615, 176, "МК", size=13, color=NEG, bold=True))
    frags.append(text(615, 194, "живлення +3.3 В", size=9, color=INK))

    # «невидимий» зв'язок через межу
    frags.append(line(334, 210, 406, 210, color=POSc, sw=1.4, dash="4 5"))
    frags.append(text(370, 232, "той самий вузол", size=9.5, color=POSc))
    frags.append(text(390, 312, "однойменні конектори зшивають сигнал наскрізь через межу аркушів",
                      size=10, color=MUTED))
    render(os.path.join(IMG, "off-sheet.svg"), W, H, *frags,
           title="Міжаркушевий зв'язок: сигнал переходить межу за іменем")


if __name__ == "__main__":
    fig_why_labels()
    fig_net_label()
    fig_bus()
    fig_off_sheet()
    print("OK: фігури згенеровано у", IMG)

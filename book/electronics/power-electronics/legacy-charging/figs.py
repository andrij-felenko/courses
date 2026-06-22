# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── dumb-charger: хост, з яким говорять, проти блока, з яким нема як ───────────
# Ідея: ліворуч є з ким домовитися (енумерація по D+/D−), праворуч процесора
# нема — тож скільки брати, треба впізнати самими лініями даних. Це і є задача.

def fig_dumb_charger():
    W, H = 720, 360
    p = []
    # дві панелі
    p.append(rect(40, 60, 300, 250, fill="#eef4ff", stroke=NEG, sw=1.4, rx=10))
    p.append(rect(380, 60, 300, 250, fill="#fdf6e3", stroke="#b8901f", sw=1.4, rx=10))
    p.append(text(190, 84, "Хост-порт (ПК)", size=13, color=NEG, bold=True))
    p.append(text(530, 84, "Блок у розетку", size=13, color="#b8901f", bold=True))

    # — ліва: ПК ⇄ пристрій, дві стрілки даних —
    p.append(fitbox(70, 110, 100, 50, "ПК\n(є процесор)", size=11, fill=BG, stroke=NEG, sw=1.6, bold=True, color=NEG))
    p.append(fitbox(210, 110, 100, 50, "пристрій", size=11, fill=BG, stroke=FIELD, sw=1.6, bold=True, color=FIELD))
    p.append(arrow(170, 126, 208, 126, color=INK, sw=1.6))
    p.append(arrow(208, 144, 170, 144, color=INK, sw=1.6))
    p.append(text(190, 182, "D+/D−: енумерація", size=11, color=INK, bold=True))
    p.append(text(190, 200, "(домовляються)", size=10, color=MUTED))
    p.append(text(190, 236, "хост дозволяє", size=11, color=NEG, bold=True))
    p.append(text(190, 254, "0.5 А (USB2) / 0.9 А (USB3)", size=11, color=INK))
    p.append(text(190, 290, "є з ким говорити —", size=11, color=NEG, bold=True))
    p.append(text(190, 304, "беремо рівно дозволене", size=10, color=MUTED))

    # — права: блок ⇢ пристрій, розмови нема —
    p.append(fitbox(410, 110, 100, 50, "блок\n(нема CPU)", size=11, fill=BG, stroke="#b8901f", sw=1.6, bold=True, color="#b8901f"))
    p.append(fitbox(550, 110, 100, 50, "пристрій", size=11, fill=BG, stroke=FIELD, sw=1.6, bold=True, color=FIELD))
    p.append(line(510, 135, 548, 135, color=MUTED, sw=1.6, dash="5 4"))
    p.append(text(530, 122, "нема з ким", size=9, color=MUTED))
    p.append(text(530, 182, "D+/D−: розмови нема", size=11, color=POS, bold=True))
    p.append(text(530, 214, "скільки можна взяти?", size=13, color=POS, bold=True))
    p.append(text(530, 250, "забагато → просадка", size=10, color=INK))
    p.append(text(530, 266, "чи перегрів блока", size=10, color=INK))
    p.append(text(530, 290, "треба впізнати порт", size=11, color="#b8901f", bold=True))
    p.append(text(530, 304, "самими D+/D− (BC1.2)", size=10, color=MUTED))

    # нижня смуга-висновок
    b, bw, bh = textbox(W / 2, 338, "BC1.2 дає пристрою впізнати тип порту самими лініями даних — без жодного хоста",
                        size=11, fill="#eafaf0", stroke=FIELD, sw=1.3, pad=8)
    p.append(b)

    render(os.path.join(OUT, "dumb-charger.svg"), W, H, *p,
           title="Чому пристрій мусить упізнавати порт")


# ── port-types: SDP / CDP / DCP поруч ─────────────────────────────────────────
# Ідея: три колонки — звичайний порт, порт-із-зарядкою, тупий блок; під кожною
# спосіб упізнання й дозволений струм. Видно, що зарядними виглядають двоє.

def fig_port_types():
    W, H = 720, 330
    p = []
    cols = [
        (130, "SDP", "Standard\nDownstream Port", "звичайний порт ПК", NEG, "#eef4ff",
         "дані як завжди", "0.5 / 0.9 А", "після енумерації"),
        (360, "CDP", "Charging\nDownstream Port", "порт ПК + зарядка", FIELD, "#eafaf0",
         "дані + активне\nрукостискання", "до 1.5 А", "відповідає на пробу"),
        (590, "DCP", "Dedicated\nCharging Port", "тупий блок", "#b8901f", "#fdf6e3",
         "D+ замкнено на D−", "до 1.5 А", "даних нема"),
    ]
    for cx, abbr, full, sub, col, fill, sig, cur, note in cols:
        p.append(rect(cx - 95, 64, 190, 232, fill=fill, stroke=col, sw=1.5, rx=10))
        p.append(text(cx, 96, abbr, size=20, color=col, bold=True))
        p.append(mtext(cx, 120, full, size=10, color=MUTED))
        p.append(text(cx, 158, sub, size=11, color=INK, bold=True))
        p.append(line(cx - 70, 172, cx + 70, 172, color=col, sw=1.0))
        p.append(text(cx, 192, "ознака:", size=9, color=MUTED))
        p.append(mtext(cx, 208, sig, size=11, color=INK, bold=True))
        p.append(text(cx, 256, cur, size=15, color=col, bold=True))
        p.append(text(cx, 278, note, size=9, color=MUTED))

    render(os.path.join(OUT, "port-types.svg"), W, H, *p,
           title="Три типи портів BC1.2")


# ── dcp-short: підпис тупої зарядки і дзеркальна проба пристрою ────────────────
# Ідея: всередині блока перемичка D+→D− (≤200 Ом); пристрій подає напругу на D+
# і ловить її на D−. Перетекла — лінії замкнені, перед нами зарядка.

def fig_dcp_short():
    W, H = 720, 300
    p = []
    # блок (джерело)
    p.append(rect(60, 80, 250, 170, fill="#fdf6e3", stroke="#b8901f", sw=1.5, rx=10))
    p.append(text(185, 104, "DCP: тупий блок", size=12, color="#b8901f", bold=True))
    # дві лінії D+ / D− та перемичка між ними
    yp, ym = 150, 200
    p.append(line(90, yp, 280, yp, color=INK, sw=2.0))
    p.append(line(90, ym, 280, ym, color=INK, sw=2.0))
    p.append(text(86, yp - 8, "D+", size=11, color=POS, bold=True, anchor="start"))
    p.append(text(86, ym + 18, "D−", size=11, color=NEG, bold=True, anchor="start"))
    p.append(line(250, yp, 250, ym, color=FIELD, sw=2.4))
    p.append(text(262, (yp + ym) / 2 + 4, "≤200 Ом", size=10, color=FIELD, anchor="start", bold=True))
    p.append(text(185, 234, "увесь «підпис» — одна перемичка", size=10, color=MUTED))

    # пристрій (проба)
    p.append(rect(430, 80, 230, 170, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=10))
    p.append(text(545, 104, "пристрій: проба", size=12, color=FIELD, bold=True))
    p.append(text(545, 132, "подає ~0.6 В на D+", size=11, color=POS, bold=True))
    p.append(arrow(455, 156, 635, 156, color=POS, sw=1.8))
    p.append(text(545, 184, "дивиться на D−", size=11, color=NEG, bold=True))
    p.append(text(545, 210, "напруга перетекла →", size=11, color=INK))
    p.append(text(545, 228, "лінії замкнені → це зарядка", size=10, color=FIELD, bold=True))

    # стрілка-зв'язок між панелями
    p.append(arrow(312, 165, 428, 165, color=MUTED, sw=1.4))

    render(os.path.join(OUT, "dcp-short.svg"), W, H, *p,
           title="Підпис зарядки: D+ замкнено на D−")


# ── bc12-flow: дві перевірки впізнавання ──────────────────────────────────────
# Ідея: після VBUS — контакт даних, тоді «це зарядний порт?» (SDP/далі), тоді
# «тупий чи розумний?» (DCP/CDP). Кінець — безпечний струм.

def fig_bc12_flow():
    W, H = 720, 360
    p = []
    cx = W / 2

    def box(cx, cy, s, col, fill, **kw):
        b, bw, bh = textbox(cx, cy, s, size=11, bold=True, color=col, fill=fill, stroke=col, sw=1.6, **kw)
        p.append(b); return bw, bh

    box(cx, 56, "VBUS з'явилася → контакт даних (DCD)", INK, FILL, min_w=360)
    p.append(arrow(cx, 76, cx, 100, color=INK, sw=1.6))
    box(cx, 122, "первинне виявлення: це зарядний порт?", "#b8901f", "#fdf6e3", min_w=360)

    # розгалуження «ні» → SDP (ліворуч)
    p.append(line(cx - 180, 122, 150, 122, color=NEG, sw=1.5))
    p.append(arrow(150, 122, 150, 168, color=NEG, sw=1.5))
    p.append(text(cx - 188, 114, "нема відгуку", size=10, color=NEG, anchor="end"))
    box(150, 196, "SDP\n0.5 / 0.9 А\n(треба енумерація)", NEG, "#eef4ff")

    # «так» → вниз
    p.append(arrow(cx, 144, cx, 186, color=FIELD, sw=1.6))
    p.append(text(cx + 12, 168, "є відгук", size=10, color=FIELD, anchor="start"))
    box(cx, 208, "вторинне виявлення: лінії замкнені наскрізь?", FIELD, "#eafaf0", min_w=380)

    # DCP / CDP
    p.append(line(cx, 230, cx, 250, color=INK, sw=1.5))
    p.append(line(220, 250, W - 220, 250, color=INK, sw=1.5))
    p.append(arrow(220, 250, 220, 280, color=INK, sw=1.5))
    p.append(arrow(W - 220, 250, W - 220, 280, color=INK, sw=1.5))
    p.append(text(232, 244, "так (пасивно)", size=10, color=INK, anchor="start"))
    p.append(text(W - 232, 244, "ні (відповідає активно)", size=10, color=INK, anchor="end"))
    box(220, 306, "DCP\nдо 1.5 А", "#b8901f", "#fdf6e3")
    box(W - 220, 306, "CDP\nдо 1.5 А", FIELD, "#eafaf0")

    p.append(text(cx, 344, "уся процедура — мілісекунди, до початку заряджання", size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "bc12-flow.svg"), W, H, *p,
           title="Дві перевірки впізнавання BC1.2")


# ── proprietary: три способи закодувати струм на D+/D− ─────────────────────────
# Ідея: BC1.2 — просто замкнути; фірмові — тримати фіксовані напруги. Пристрій
# шукає САМЕ свій підпис, тож на чужому відкочується в безпечні 0.5 А.

def fig_proprietary():
    W, H = 720, 320
    p = []
    cards = [
        (130, "BC1.2", "#b8901f", "#fdf6e3",
         ["D+ ─┐", "D− ─┘ замкнено", "(≤200 Ом)"], "до 1.5 А"),
        (360, "Apple", "#7a4fb0", "#f2ecf8",
         ["D+ = 2.7 В", "D− = 2.7 В", "(дільники з VBUS)"], "до 2.4 А"),
        (590, "Quick Charge", NEG, "#eef4ff",
         ["D+ = 0.6 В", "D− → GND", "далі ростить В"], "9 / 12 В"),
    ]
    for cx, name, col, fill, lines, out in cards:
        p.append(rect(cx - 95, 70, 190, 180, fill=fill, stroke=col, sw=1.5, rx=10))
        p.append(text(cx, 98, name, size=14, color=col, bold=True))
        p.append(line(cx - 70, 110, cx + 70, 110, color=col, sw=1.0))
        for i, ln in enumerate(lines):
            p.append(text(cx, 138 + i * 24, ln, size=12 if i < 2 else 10,
                          color=INK if i < 2 else MUTED, bold=(i < 2)))
        p.append(text(cx, 234, out, size=13, color=col, bold=True))

    b, bw, bh = textbox(W / 2, 292,
                        "пристрій шукає САМЕ свій підпис: чужий не впізнає → відкочується в безпечні 0.5 А",
                        size=11, fill="#fdecea", stroke=POS, sw=1.3, pad=8)
    p.append(b)

    render(os.path.join(OUT, "proprietary.svg"), W, H, *p,
           title="Три діалекти підпису струму на D+/D−")


# ── two-worlds: D+/D− і CC співіснують в одному роз'ємі ───────────────────────
# Ідея: легасі-механізм (коди на лініях даних) і сучасний (CC + PD) не воюють —
# добрий зарядний виставляє обидва; кожен пристрій бере зрозуміле йому запитання.

def fig_two_worlds():
    W, H = 720, 320
    p = []
    # центр — роз'єм / зарядний
    cx = W / 2
    cb, cbw, cbh = textbox(cx, 165, "сучасний\nзарядний", size=12, bold=True,
                           fill="#f6f4ec", stroke=INK, sw=2, pad=14, min_w=130)
    # ліва панель — легасі
    p.append(rect(40, 70, 230, 190, fill="#fdf6e3", stroke="#b8901f", sw=1.5, rx=10))
    p.append(text(155, 96, "легасі-світ", size=13, color="#b8901f", bold=True))
    p.append(text(155, 124, "коди на D+/D−", size=12, color=INK, bold=True))
    p.append(text(155, 148, "BC1.2 + фірмові", size=11, color=MUTED))
    p.append(text(155, 184, "межа ≈ 1.5 А (7.5 Вт)", size=11, color="#b8901f", bold=True))
    p.append(text(155, 214, "для старих пристроїв", size=10, color=MUTED))
    p.append(text(155, 232, "і перехідників", size=10, color=MUTED))
    # права панель — сучасний
    p.append(rect(W - 270, 70, 230, 190, fill="#eef4ff", stroke=NEG, sw=1.5, rx=10))
    p.append(text(W - 155, 96, "сучасний світ", size=13, color=NEG, bold=True))
    p.append(text(W - 155, 124, "резистори CC + PD", size=12, color=INK, bold=True))
    p.append(text(W - 155, 148, "на лініях CC", size=11, color=MUTED))
    p.append(text(W - 155, 184, "CC → 15 Вт, PD → 240 Вт", size=11, color=NEG, bold=True))
    p.append(text(W - 155, 214, "для USB-C", size=10, color=MUTED))
    p.append(text(W - 155, 232, "пристроїв", size=10, color=MUTED))
    # стрілки від центру до обох панелей (двомовність)
    p.append(arrow(cx - cbw / 2, 165, 272, 165, color="#b8901f", sw=1.8))
    p.append(arrow(cx + cbw / 2, 165, W - 272, 165, color=NEG, sw=1.8))
    p.append(cb)

    b, bw, bh = textbox(cx, 296, "добрий зарядний говорить обома мовами — кожен пристрій бере зрозуміле йому запитання",
                        size=11, fill="#eafaf0", stroke=FIELD, sw=1.3, pad=8)
    p.append(b)

    render(os.path.join(OUT, "two-worlds.svg"), W, H, *p,
           title="Два механізми в одному роз'ємі")


if __name__ == "__main__":
    fig_dumb_charger()
    fig_port_types()
    fig_dcp_short()
    fig_bc12_flow()
    fig_proprietary()
    fig_two_worlds()
    print("OK: figures written to", OUT)

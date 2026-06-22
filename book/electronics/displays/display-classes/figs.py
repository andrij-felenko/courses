# -*- coding: utf-8 -*-
"""Фігури до теми «Класи дисплеїв».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# локальні кольори, що доповнюють палітру svgkit
LAMP   = "#caa24a"   # світло / лампа (тепле)
LAMPF  = "#fff4c2"
GLASS  = "#5d7e93"
PAPER  = "#9bbdd6"


def eye(cx, cy):
    """Око — спільний значок «куди дивиться світло»."""
    return ('<ellipse cx="%.1f" cy="%.1f" rx="16" ry="9" fill="%s" stroke="%s" stroke-width="2"/>'
            % (cx, cy, BG, INK)
            + circle(cx, cy + 2, 4.5, fill=INK, stroke=INK, sw=1)
            + text(cx + 26, cy + 3, "око", size=11.5, color=MUTED, anchor="start"))


def rgb_pixel(x, y, w=62, h=36):
    """Піксель R·G·B — три підпікселі поруч."""
    s = w / 3.0
    return (rect(x, y, s, h, fill=POS, stroke=BG, sw=1, rx=0)
            + rect(x + s, y, s, h, fill=FIELD, stroke=BG, sw=1, rx=0)
            + rect(x + 2 * s, y, s, h, fill=NEG, stroke=BG, sw=1, rx=0)
            + rect(x, y, w, h, fill="none", stroke=INK, sw=1.2, rx=0))


def sun(cx, cy, r=10):
    """Сонечко-промінчики — «світло довкола»."""
    import math
    out = [circle(cx, cy, r, fill=LAMPF, stroke=LAMP, sw=2)]
    for k in range(8):
        a = k * math.pi / 4
        out.append(line(cx + (r + 2) * math.cos(a), cy + (r + 2) * math.sin(a),
                        cx + (r + 7) * math.cos(a), cy + (r + 7) * math.sin(a),
                        color=LAMP, sw=1.5))
    return "".join(out)


# ── 1. Три класи за джерелом світла ─────────────────────────────────────────
def fig_classes():
    W, H = 820, 420
    f = [text(W / 2, 34, "Три класи дисплеїв — за тим, звідки береться світло", size=19, bold=True),
         text(W / 2, 55, "одне це питання вирішує енергію, чорний колір і читаність на сонці",
              size=12.5, color=MUTED, italic=True)]

    def panel(x0, head, name, draw):
        cx = x0 + 110
        f.append(rect(x0, 76, 220, 320, fill="none", stroke="#e4e4e4", sw=1.4, rx=8))
        f.append(text(cx, 100, head, size=16, bold=True))
        f.append(eye(cx, 132))
        f.append(rgb_pixel(cx - 31, 234))
        f.append(text(cx, 284, "піксель (R·G·B)", size=11, color=MUTED))
        draw(cx)
        f.append(text(cx, 390, name, size=13, bold=True))

    # OLED — світиться сам
    def d_oled(cx):
        for dx in (-14, 0, 14):
            f.append(arrow(cx + dx, 228, cx + dx * 0.4, 146, color=FIELD, sw=2))
        f.append(text(cx, 200, "світиться сам", size=12.5, color=FIELD, bold=True))
    panel(40, "ВИПРОМІНЮЄ", "OLED", d_oled)

    # TFT-LCD — лампа позаду, світло крізь піксель
    def d_lcd(cx):
        f.append(rect(cx - 90, 350, 180, 16, fill=LAMPF, stroke=LAMP, sw=1.4, rx=3))
        f.append(text(cx, 362, "підсвітка (лампа)", size=10.5, color="#9a7d2e"))
        f.append(arrow(cx, 348, cx, 272, color=LAMP, sw=2))
        f.append(arrow(cx, 228, cx, 146, color=FIELD, sw=2))
        f.append(text(cx + 44, 300, "крізь", size=12, color=MUTED))
    panel(300, "ПРОПУСКАЄ", "TFT-LCD", d_lcd)

    # e-ink — відбиває навколишнє
    def d_eink(cx):
        f.append(sun(cx - 76, 158))
        f.append(text(cx - 76, 136, "світло", size=10.5, color="#9a7d2e"))
        f.append(arrow(cx - 68, 166, cx - 20, 228, color=LAMP, sw=2))
        f.append(arrow(cx - 8, 228, cx - 2, 146, color=FIELD, sw=2))
        f.append(text(cx + 40, 205, "відбиває", size=12, color=MUTED))
    panel(560, "ВІДБИВАЄ", "e-ink", d_eink)

    render(os.path.join(IMG, "classes.svg"), W, H, *f)


# ── 2. Стос шарів пікселя TFT-LCD ───────────────────────────────────────────
def fig_lcd_stack():
    W, H = 780, 360
    f = [text(W / 2, 34, "Піксель TFT-LCD: заслінка з рідкого кристала перед лампою", size=18, bold=True),
         text(W / 2, 55, "світло підсвітки йде знизу вгору крізь стос шарів; колір дає фільтр",
              size=12.5, color=MUTED, italic=True)]
    f.append(eye(260, 78))
    x, w = 110, 300
    lab = 424  # де починаються підписи праворуч

    def layer(y, h, fill, stroke, name, sw=1.4):
        f.append(rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=0))
        f.append(text(lab, y + h / 2 + 4, name, size=12, color=INK, anchor="start"))

    layer(98, 12, "#a9c8dd", GLASS, "скло (переднє)")
    layer(112, 14, "#eceff1", MUTED, "поляризатор ↕")
    # кольорофільтр R·G·B
    f.append(rect(x, 128, 100, 22, fill=POS, stroke=BG, sw=1, rx=0))
    f.append(rect(x + 100, 128, 100, 22, fill=FIELD, stroke=BG, sw=1, rx=0))
    f.append(rect(x + 200, 128, 100, 22, fill=NEG, stroke=BG, sw=1, rx=0))
    f.append(rect(x, 128, w, 22, fill="none", stroke=INK, sw=1.2, rx=0))
    f.append(text(lab, 143, "кольорофільтр — R · G · B", size=12, anchor="start"))
    # рідкий кристал — паличками
    f.append(rect(x, 152, w, 32, fill="#eaf3ff", stroke=PAPER, sw=1.4, rx=0))
    for k in range(5):
        cx = x + 30 + k * 58
        f.append(line(cx - 9, 163, cx + 9, 173, color=INK, sw=4))
    f.append(text(lab, 172, "рідкий кристал (заслінка)", size=12, anchor="start"))
    layer(186, 20, "#dfe6ea", GLASS, "скло + TFT + ITO-електрод")
    layer(208, 14, "#eceff1", MUTED, "поляризатор ↔")
    f.append(rect(x, 246, w, 24, fill=LAMPF, stroke=LAMP, sw=1.6, rx=3))
    f.append(text(lab, 260, "підсвітка (біле світло)", size=12, color="#9a7d2e", anchor="start"))
    f.append(arrow(92, 246, 92, 94, color=FIELD, sw=2.4))
    f.append(text(86, 175, "світло", size=11.5, color=FIELD, anchor="end"))
    f.append(text(W / 2, 300, "Лампа світить завжди (звідси й споживання), а заслінка лише дозує, скільки пройде.",
                  size=12, color=MUTED, italic=True))
    f.append(text(W / 2, 320, "«Чорний» — це закрита заслінка, та трохи світла все одно протікає: чорний виходить сіруватим.",
                  size=12, color=MUTED, italic=True))
    render(os.path.join(IMG, "lcd-stack.svg"), W, H, *f)


# ── 3. Активна матриця: транзистор тримає піксель ───────────────────────────
def fig_active_matrix():
    W, H = 740, 340
    f = [text(W / 2, 34, "Активна матриця: чому на кожному пікселі сидить транзистор (TFT)", size=18, bold=True),
         text(W / 2, 55, "транзистор заряджає піксель і тримає заряд, доки рядок не виберуть знову",
              size=12.5, color=MUTED, italic=True)]
    # рядок (gate) і стовпець (data)
    f.append(line(70, 130, 360, 130, color=INK, sw=2.6))
    f.append(text(64, 123, "РЯДОК", size=12, bold=True, anchor="end"))
    f.append(text(64, 139, "(gate)", size=10.5, color=MUTED, anchor="end"))
    f.append(line(200, 90, 200, 130, color=INK, sw=2.6))
    f.append(text(200, 84, "СТОВПЕЦЬ (data)", size=12, bold=True))
    # транзистор
    f.append(rect(174, 142, 52, 28, fill="#eef2f5", stroke=INK, sw=1.8, rx=5))
    f.append(text(200, 161, "TFT", size=13, bold=True))
    f.append(line(200, 130, 200, 142, color=INK, sw=2))
    f.append(line(200, 170, 200, 192, color=INK, sw=2))
    f.append(line(136, 192, 280, 192, color=INK, sw=2))
    # конденсатор C (пам'ять)
    f.append(line(136, 192, 136, 208, color=INK, sw=2))
    f.append(line(121, 208, 151, 208, color=INK, sw=3))
    f.append(line(121, 216, 151, 216, color=INK, sw=3))
    f.append(line(136, 216, 136, 234, color=INK, sw=2))
    f.append(text(115, 204, "C", size=13, bold=True, anchor="end"))
    f.append(text(136, 250, "пам'ять", size=10.5, color=MUTED))
    # піксель (рідкокристалічна комірка) як друга «ємність»
    f.append(line(280, 192, 280, 208, color=INK, sw=2))
    f.append(line(263, 208, 297, 208, color=GLASS, sw=3))
    f.append(line(263, 216, 297, 216, color=GLASS, sw=3))
    f.append(line(280, 216, 280, 234, color=INK, sw=2))
    f.append(text(303, 206, "піксель", size=11, anchor="start"))
    f.append(text(303, 220, "(LC)", size=11, color=MUTED, anchor="start"))
    f.append(line(136, 234, 280, 234, color=INK, sw=2))
    f.append(text(208, 250, "спільний електрод", size=10.5, color=MUTED))
    # кроки праворуч
    steps = ["1 · вибрали РЯДОК → TFT відкрився",
             "2 · напруга СТОВПЦЯ зарядила C і піксель",
             "3 · рядок зняли → TFT закрився",
             "4 · C ТРИМАЄ напругу весь кадр"]
    for i, s in enumerate(steps):
        f.append(text(400, 120 + i * 30, s, size=12.5, anchor="start"))
    render(os.path.join(IMG, "active-matrix.svg"), W, H, *f)


# ── 4. Стос шарів пікселя OLED ──────────────────────────────────────────────
def fig_oled_stack():
    W, H = 780, 360
    f = [text(W / 2, 34, "Піксель OLED: органічний шар світиться сам", size=18, bold=True),
         text(W / 2, 55, "електрон і дірка зустрічаються в емісійному шарі — народжується фотон",
              size=12, color=MUTED, italic=True)]
    f.append(eye(270, 78))
    x, w, lab = 120, 300, 434

    def layer(y, h, fill, stroke, name):
        f.append(rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.4, rx=0))
        f.append(text(lab, y + h / 2 + 4, name, size=11.5, anchor="start"))

    layer(98, 12, "#a9c8dd", GLASS, "скло / інкапсуляція")
    layer(112, 12, "#cfd8dc", MUTED, "катод (−)")
    layer(126, 12, "#e8eef0", PAPER, "ETL — транспорт електронів")
    # емісійний шар R·G·B
    f.append(rect(x, 140, 100, 22, fill=POS, stroke=BG, sw=1, rx=0))
    f.append(rect(x + 100, 140, 100, 22, fill=FIELD, stroke=BG, sw=1, rx=0))
    f.append(rect(x + 200, 140, 100, 22, fill=NEG, stroke=BG, sw=1, rx=0))
    f.append(rect(x, 140, w, 22, fill="none", stroke=INK, sw=1.2, rx=0))
    f.append(text(lab, 155, "EML — емісійний шар R · G · B", size=11.5, anchor="start"))
    layer(164, 12, "#e8eef0", PAPER, "HTL — транспорт дірок")
    layer(178, 12, "#f0d6a8", LAMP, "анод (+)")
    layer(192, 24, "#dfe6ea", GLASS, "підкладка + TFT-основа")
    # електрон і дірка летять у EML
    f.append(minus(90, 124, 6))
    f.append(arrow(98, 128, 146, 148, color=NEG, sw=1.8))
    f.append(text(80, 120, "e⁻", size=12, color=NEG, bold=True, anchor="end"))
    f.append(plus(90, 182, 6))
    f.append(arrow(98, 178, 146, 158, color=POS, sw=1.8))
    f.append(text(80, 198, "дірка", size=11, color=POS, bold=True, anchor="end"))
    # фотон угору
    f.append(arrow(334, 140, 334, 94, color=FIELD, sw=2.4))
    f.append(text(342, 120, "фотон", size=11, color=FIELD, anchor="start"))
    f.append(text(W / 2, 280, "Жодної лампи й заслінки: вимкнений піксель = справжній чорний.",
                  size=12, color=MUTED, italic=True))
    f.append(text(W / 2, 300, "Світло народжується прямо в пікселі — але органіка поступово старіє (вигоряння).",
                  size=12, color=MUTED, italic=True))
    render(os.path.join(IMG, "oled-stack.svg"), W, H, *f)


# ── 5. Мікрокапсула e-ink ───────────────────────────────────────────────────
def fig_eink_capsule():
    W, H = 780, 420
    f = [text(W / 2, 34, "Піксель e-ink: заряджені частинки в мікрокапсулі", size=18, bold=True),
         text(W / 2, 55, "поле піднімає білі або чорні частинки до поверхні — і тримає їх без струму",
              size=12.5, color=MUTED, italic=True),
         text(W / 2, 108, "білі частинки (+)  ·  чорні частинки (−)  у прозорій рідині",
              size=12, color=MUTED, italic=True)]

    def cell(cx, top_sign, bot_sign, white_on_top, title, sub):
        # електроди
        f.append(rect(cx - 92, 100, 184, 12, fill="#dfe6ea", stroke=GLASS, sw=1.4, rx=0))
        f.append(rect(cx - 92, 308, 184, 12, fill="#cfd8dc", stroke=GLASS, sw=1.4, rx=0))
        # знаки на електродах
        f.append((plus if top_sign == "+" else minus)(cx - 76, 106, 6))
        f.append((plus if bot_sign == "+" else minus)(cx - 76, 314, 6))
        # капсула
        f.append(circle(cx, 210, 92, fill="#f4fbff", stroke="#7fa9c4", sw=2))
        # частинки: два ряди вгорі, два внизу
        def row(y, white):
            for k in range(4):
                px = cx - 33 + k * 22
                if white:
                    f.append(circle(px, y, 8, fill=BG, stroke=PAPER, sw=1.4))
                else:
                    f.append(circle(px, y, 6, fill="#2b2f33", stroke="#2b2f33", sw=1.4))
        row(146, white_on_top); row(166, white_on_top)
        row(258, not white_on_top); row(278, not white_on_top)
        f.append(text(cx, 344, title, size=13, bold=True))
        f.append(text(cx, 362, sub, size=11, color=MUTED))

    cell(230, "−", "+", True, "БІЛИЙ піксель — відбиває", "тримається без струму")
    # стрілки падаючого/відбитого світла лівій капсулі
    f.append(arrow(130, 84, 212, 114, color=LAMP, sw=2))
    f.append(arrow(224, 114, 264, 82, color=FIELD, sw=2))
    cell(560, "+", "−", False, "ЧОРНИЙ піксель — поглинає", "тримається без струму")
    f.append(arrow(460, 84, 542, 114, color=LAMP, sw=2))
    render(os.path.join(IMG, "eink-capsule.svg"), W, H, *f)


# ── 6. Карта компромісів (таблиця) ──────────────────────────────────────────
def fig_compare():
    W, H = 824, 320
    f = [text(W / 2, 34, "Карта компромісів: TFT-LCD · OLED · e-ink", size=19, bold=True)]
    GOODF, GOODS = "#e7f5ea", FIELD
    BADF, BADS = "#fdeceb", POS
    MEHF, MEHS = "#fff8e8", "#b07d18"
    cols = [(42, 108, ""), (150, 152, "Джерело світла"), (302, 132, "Чорний колір"),
            (434, 132, "Статична P"), (566, 118, "На сонці"), (684, 130, "Рух / відео")]
    # шапка
    for x, w, head in cols:
        f.append(rect(x, 70, w, 36, fill="#eef0f2", stroke=MUTED, sw=1.2, rx=0))
        if head:
            f.append(text(x + w / 2, 92, head, size=12.5, bold=True))
    # рядки: (назва, [ (текст, заливка, колір) ×5 ])
    G = lambda t: (t, GOODF, GOODS)
    B = lambda t: (t, BADF, BADS)
    M = lambda t: (t, MEHF, MEHS)
    rows = [
        ("TFT-LCD", [M("підсвітка ззаду"), B("сіруватий"), B("висока (лампа)"), G("добре"), G("відмінно")]),
        ("OLED",    [G("сам піксель"), G("ідеальний"), M("за вмістом"), M("блики"), G("відмінно")]),
        ("e-ink",   [G("відбите"), G("як папір"), G("нуль"), G("ідеально"), B("ні (повільно)")]),
    ]
    for r, (name, cells) in enumerate(rows):
        y = 106 + r * 58
        f.append(rect(42, y, 108, 58, fill="#f6f7f8", stroke=MUTED, sw=1.2, rx=0))
        f.append(text(96, y + 34, name, size=13, bold=True))
        for c, (txt, fill, col) in enumerate(cells):
            x, w = cols[c + 1][0], cols[c + 1][1]
            f.append(rect(x, y, w, 58, fill=fill, stroke=MUTED, sw=1.2, rx=0))
            f.append(text(x + w / 2, y + 34, txt, size=12, color=col, bold=True))
    f.append(text(W / 2, 300, "Жодна не «найкраща»: вибір — це питання живлення, світла довкола і того, що показуємо.",
                  size=12, color=MUTED, italic=True))
    render(os.path.join(IMG, "compare.svg"), W, H, *f)


# ── 7. Потужність у часі ────────────────────────────────────────────────────
def fig_power():
    W, H = 780, 380
    f = [text(W / 2, 34, "Потужність у часі для майже статичного екрана", size=19, bold=True),
         text(W / 2, 55, "чому для рідко оновлюваної інформації e-ink виграє на порядки",
              size=12.5, color=MUTED, italic=True)]
    # осі
    f.append(arrow(96, 300, 700, 300, color=INK, sw=2))
    f.append(arrow(96, 300, 96, 88, color=INK, sw=2))
    f.append(text(700, 322, "час →", size=12, anchor="end"))
    f.append(text(90, 84, "потужність ↑", size=12, anchor="start"))
    # TFT — рівна висока лінія
    f.append(line(96, 128, 688, 128, color=POS, sw=2.6))
    f.append(text(692, 122, "TFT-LCD (лампа завжди)", size=12, color=POS, anchor="end"))
    # OLED — нижче, пунктир
    f.append(line(96, 196, 688, 196, color=NEG, sw=2.4, dash="6 4"))
    f.append(text(692, 190, "OLED (за вмістом)", size=12, color=NEG, anchor="end"))
    # e-ink — нуль + короткі піки
    f.append(line(96, 288, 688, 288, color=FIELD, sw=2.6))
    for px in (200, 380, 560):
        f.append(line(px, 288, px, 222, color=FIELD, sw=2.4))
        f.append(line(px, 222, px + 8, 222, color=FIELD, sw=2.4))
        f.append(line(px + 8, 222, px + 8, 288, color=FIELD, sw=2.4))
    f.append(text(692, 282, "e-ink (нуль між оновленнями)", size=12, color=FIELD, anchor="end"))
    f.append(text(380, 322, "↑ короткі піки лише коли картинка змінюється", size=11.5, color=FIELD))
    render(os.path.join(IMG, "power.svg"), W, H, *f)


def rod(cx, cy, ang_deg, ln=22, color=INK, sw=4.6):
    """Паличка-молекула під кутом ang_deg (0 = горизонталь)."""
    import math
    a = math.radians(ang_deg)
    dx, dy = ln / 2 * math.cos(a), ln / 2 * math.sin(a)
    return line(cx - dx, cy - dy, cx + dx, cy + dy, color=color, sw=sw)


# ── hist-1. Часова стрічка: від ботаніки до годинника ────────────────────────
def fig_hist_timeline():
    W, H = 900, 760
    f = [text(W / 2, 36, "Рідкий кристал → дисплей: ланцюг від ботаніки до годинника", size=20, bold=True),
         text(W / 2, 57, "наука була готова за 70 років до приладу; синім — те, що сталося поза RCA",
              size=12.5, color=MUTED, italic=True)]
    AX = 250
    f.append(line(AX, 92, AX, 730, color=MUTED, sw=3))
    BLUE = "#1f47b5"
    BLUET = "#4a5a86"
    # (рік, y, заголовок, опис, колір вузла, колір тексту, акцент?)
    nodes = [
        ("1888", 116, "Райнітцер / Reinitzer", "Холестерилбензоат має ДВІ точки плавлення — каламутний проміжний стан", BLUE, BLUET, False),
        ("1889", 190, "Леманн / Lehmann", "Це «рідкий кристал»: тече як рідина, а світло заломлює як кристал", BLUE, BLUET, False),
        ("1911", 264, "Можен / Mauguin", "Закручений шар нематика повертає площину поляризації світла", BLUE, BLUET, False),
        ("1962", 338, "Вільямс / Williams · RCA", "Електричне поле збурює нематик у смуги-домени — є електрооптика!", INK, INK, False),
        ("1968", 412, "Гайльмаєр / Heilmeier · RCA", "Динамічне розсіяння: прозоре скло мутніє від струму — ПЕРШИЙ LCD", POS, INK, True),
        ("1970", 486, "Гельфріх / Helfrich", "Іде з RCA до Roche: ідею «закрученого нематика» в RCA зустріли байдуже", BLUE, BLUET, False),
        ("1971", 560, "Шадт+Гельфріх · Ферґасон", "Twisted nematic (TN): польовий ефект, копійки енергії — оце й переможе", BLUE, BLUET, False),
        ("1973", 634, "Sharp · Seiko · Японія", "Калькулятор і годинник на LCD — виробництво їде в Азію", BLUE, BLUET, False),
        ("1976", 708, "RCA продає LC-бізнес", "Винахід остаточно йде з компанії, що його породила", INK, INK, False),
    ]
    for yr, y, head, desc, ncol, tcol, accent in nodes:
        if accent:
            f.append(circle(AX, y, 10.5, fill=ncol, stroke=ncol, sw=3))
            f.append(circle(AX, y, 5, fill=BG, stroke=BG, sw=0))
        else:
            f.append(circle(AX, y, 7, fill=BG, stroke=ncol, sw=2.6))
        f.append(text(AX - 22, y + 5, yr, size=13, color=MUTED, bold=True, anchor="end"))
        f.append(text(AX + 26, y - 3, head, size=15, color=ncol, bold=True, anchor="start"))
        f.append(text(AX + 26, y + 16, desc, size=12.3, color=tcol, italic=True, anchor="start"))
    f.append(text(W / 2, 752, "Іронія: RCA зробила перший дисплей (1968) і випустила з рук обидві ключові ідеї — DSM і TN.",
                  size=12.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "timeline.svg"), W, H, *f)


# ── hist-2. Динамічне розсіяння (DSM) ───────────────────────────────────────
def fig_hist_dsm():
    import math
    W, H = 820, 420
    f = [text(W / 2, 34, "Динамічне розсіяння (DSM) — те, що зробив Гайльмаєр у RCA", size=19, bold=True),
         text(W / 2, 55, "струм ганяє іони → турбулентність ламає порядок → прозоре скло мутніє",
              size=12.5, color=MUTED, italic=True)]

    def glass(x):
        return (rect(x, 100, 236, 9, fill="#a9c8dd", stroke=GLASS, sw=1.4, rx=2)
                + rect(x, 291, 236, 9, fill="#a9c8dd", stroke=GLASS, sw=1.4, rx=2))

    def light(xc):
        out = []
        for k in range(4):
            px = xc - 64 + k * 43
            out.append(arrow(px, 356, px, 304, color=FIELD, sw=2.2))
        out.append(text(xc, 372, "падаюче світло", size=11.5, color=FIELD))
        return "".join(out)

    # ── лівий бік: порядок (прозоро) ──
    f.append(glass(94))
    f.append(light(212))
    for ry in (140, 180, 220, 255):
        for k in range(7):
            f.append(rod(122 + k * 30, ry, 0))
    f.append(text(212, 84, "ПРОЗОРО", size=16, color=FIELD, bold=True))
    f.append(text(212, 320, "U = 0 — порядок", size=12, color=MUTED))
    f.append(rect(94, 110, 236, 180, fill="none", stroke="#e4e4e4", sw=1.4, rx=0))

    # ── правий бік: турбулентність (молочно-біло) ──
    f.append(rect(493, 111, 230, 178, fill="#cfd4d8", stroke="none", sw=0, rx=0))
    f.append(glass(490))
    f.append(light(608))
    f.append(plus(505, 104.5, 8.5))
    f.append(minus(505, 295.5, 8.5))
    f.append(line(520, 282, 708, 120, color=NEG, sw=1.5, dash="5 4"))
    # хаотичні палички
    rng = [(508 + (i % 7) * 30, 140 + (i // 7) * 39, (i * 53) % 180)
           for i in range(28)]
    for cx, cy, ang in rng:
        f.append(rod(cx, cy, ang))
    f.append(text(608, 84, "МОЛОЧНО-БІЛО", size=16, color="#6f767b", bold=True))
    f.append(text(608, 320, "U > 0 — потік іонів (СТРУМ)", size=12, color=NEG))
    f.append(rect(490, 110, 236, 180, fill="none", stroke="#e4e4e4", sw=1.4, rx=0))
    f.append(line(410, 78, 410, 320, color="#e4e4e4", sw=1.4, dash="4 5"))
    f.append(text(W / 2, 406, "DSM світить струмом і дає мутно-білі знаки на темному тлі; енергії — багато. Це був глухий кут.",
                  size=12.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "dsm.svg"), W, H, *f)


# ── hist-3. Твіст-нематик (TN) ──────────────────────────────────────────────
def fig_hist_tn():
    W, H = 820, 480
    f = [text(W / 2, 34, "Twisted nematic (TN) — ідея, що вийшла з RCA за двері й перемогла", size=19, bold=True),
         text(W / 2, 55, "90° закрут веде поляризацію крізь схрещені поляризатори; поле випрямляє закрут",
              size=12.5, color=MUTED, italic=True)]

    def polarizer_h(x, y):
        """Горизонтальний поляризатор (горизонтальні штрихи) → пропускає ↔."""
        out = [rect(x, y, 184, 14, fill="#f3f4f6", stroke=MUTED, sw=1.6, rx=3)]
        for k in range(3):
            out.append(line(x + 4, y + 2.3 + k * 4.7, x + 180, y + 2.3 + k * 4.7, color=MUTED, sw=1.1))
        return "".join(out)

    def polarizer_v(x, y):
        """Вертикальний поляризатор (вертикальні штрихи) → пропускає ↕."""
        out = [rect(x, y, 184, 14, fill="#f3f4f6", stroke=MUTED, sw=1.6, rx=3)]
        n = 26
        for k in range(n):
            px = x + 3.5 + k * (177.0 / (n - 1))
            out.append(line(px, y + 4, px, y + 10, color=MUTED, sw=1.1))
        return "".join(out)

    def glass(x):
        return (rect(x, 302, 184, 9, fill="#a9c8dd", stroke=GLASS, sw=1.4, rx=2)
                + rect(x, 121, 184, 9, fill="#a9c8dd", stroke=GLASS, sw=1.4, rx=2))

    # ── ЛІВО: поле вимкнено, закрут веде світло ──
    x = 122
    f.append(polarizer_h(x, 316))
    f.append(text(x + 192, 328, "↔", size=18, bold=True, anchor="start"))
    f.append(polarizer_v(x, 104))
    f.append(text(x + 192, 116, "↕", size=18, bold=True, anchor="start"))
    f.append(glass(x))
    f.append(arrow(214, 416, 214, 346, color=FIELD, sw=2.4))
    f.append(text(214, 432, "світло", size=11.5, color=FIELD))
    # п'ять «поверхів» закруту: 90° → 0°
    rows = [(292, 0), (253, 22.5), (214, 45), (175, 67.5), (136, 90)]
    for ry, ang in rows:
        for k in range(5):
            f.append(rod(154 + k * 30, ry, ang))
    f.append(text(316, 297, "↔", size=16, color=FIELD, bold=True, anchor="start"))
    f.append(text(316, 219, "⤢", size=16, color=FIELD, bold=True, anchor="start"))
    f.append(text(316, 141, "↕", size=16, color=FIELD, bold=True, anchor="start"))
    f.append(arrow(214, 102, 214, 96, color=FIELD, sw=2.4))
    f.append(text(214, 86, "ЯСКРАВО", size=16, color=FIELD, bold=True))
    f.append(text(214, 360, "поле вимкнено (U = 0)", size=12, color=MUTED))
    f.append(rect(x, 132, 184, 168, fill="none", stroke="#e4e4e4", sw=1.4, rx=0))

    # ── ПРАВО: поле увімкнено, закрут зник ──
    x = 514
    f.append(polarizer_h(x, 316))
    f.append(text(x + 192, 328, "↔", size=18, bold=True, anchor="start"))
    f.append(polarizer_v(x, 104))
    f.append(text(x + 192, 116, "↕", size=18, bold=True, anchor="start"))
    f.append(glass(x))
    f.append(arrow(606, 416, 606, 346, color=FIELD, sw=2.4))
    f.append(text(606, 432, "світло", size=11.5, color=FIELD))
    f.append(plus(526, 125.5, 8))
    f.append(minus(526, 307.5, 8))
    f.append(line(538, 138, 538, 294, color=FIELD, sw=1.7, dash="5 4"))
    f.append(text(547, 216, "E", size=13, color=FIELD, bold=True, anchor="start"))
    # молекули торцем (кружечки) — стоять уздовж поля
    for ry in (292, 253, 214, 175, 136):
        for k in range(5):
            cx = 546 + k * 30
            f.append(circle(cx, ry, 5.4, fill="none", stroke=INK, sw=1.4))
            f.append(circle(cx, ry, 3, fill=INK, stroke=INK, sw=1))
    f.append(text(708, 219, "↔", size=16, color=POS, bold=True, anchor="start"))
    # перекреслення (світло гасне)
    f.append(line(591, 92, 621, 116, color=POS, sw=3))
    f.append(line(621, 92, 591, 116, color=POS, sw=3))
    f.append(text(606, 80, "ТЕМНО", size=16, color="#33373b", bold=True))
    f.append(text(606, 360, "поле увімкнено (U > U₀)", size=12, color=MUTED))
    f.append(rect(x, 132, 184, 168, fill="none", stroke="#e4e4e4", sw=1.4, rx=0))
    f.append(line(410, 96, 410, 360, color="#e4e4e4", sw=1.4, dash="4 5"))
    f.append(text(W / 2, 462, "TN перемикає полем, майже без струму — годинник на ньому живе роками. Основа майже всіх LCD.",
                  size=12.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "tn.svg"), W, H, *f)


if __name__ == "__main__":
    fig_classes()
    fig_lcd_stack()
    fig_active_matrix()
    fig_oled_stack()
    fig_eink_capsule()
    fig_compare()
    fig_power()
    fig_hist_timeline()
    fig_hist_dsm()
    fig_hist_tn()
    print("OK: 10 figures ->", IMG)

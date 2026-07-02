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


# ════════════════════════════════════════════════════════════════════════════
#  ФІГУРИ ДЛЯ ДЕТАЛЬНОЇ (display-classes-d.md) — глибший шар
# ════════════════════════════════════════════════════════════════════════════

# ── D1. Три моди рідкого кристала: TN · VA · IPS ─────────────────────────────
def fig_lcd_modes():
    import math
    W, H = 840, 470
    f = [text(W / 2, 34, "Три моди LCD: та сама заслінка, різна геометрія молекул", size=19, bold=True),
         text(W / 2, 55, "як саме молекули стоять і повертаються — звідси й кути огляду, і чорний, і швидкість",
              size=12.5, color=MUTED, italic=True)]

    def panel(x0, name, sub):
        f.append(rect(x0, 78, 246, 288, fill="none", stroke="#e4e4e4", sw=1.4, rx=8))
        f.append(text(x0 + 123, 102, name, size=16, bold=True))
        f.append(text(x0 + 123, 121, sub, size=11, color=MUTED, italic=True))
        # два скельця
        f.append(rect(x0 + 30, 150, 186, 8, fill="#a9c8dd", stroke=GLASS, sw=1.2, rx=2))
        f.append(rect(x0 + 30, 300, 186, 8, fill="#a9c8dd", stroke=GLASS, sw=1.2, rx=2))

    # TN — 90° закрут
    panel(30, "TN — twisted nematic", "закрут 90° між скельцями")
    rows = [(292, 0), (256, 22.5), (220, 45), (184, 67.5), (166, 90)]
    for ry, ang in rows[:4]:
        for k in range(4):
            f.append(rod(90 + k * 34, ry, ang, ln=24))
    for k in range(4):
        f.append(rod(90 + k * 34, 168, 90, ln=8))
        f.append(circle(90 + k * 34, 168, 4, fill=INK, stroke=INK, sw=1))
    f.append(text(153, 340, "дешево, швидко, вузький кут:", size=11, color=MUTED))
    f.append(text(153, 356, "колір «пливе» під нахилом", size=11, color=POS))

    # VA — вертикальні, лягають
    panel(297, "VA — vertical alignment", "стоять сторч, лягають від поля")
    for k in range(4):
        cx = 357 + k * 34
        f.append(rod(cx, 228, 90, ln=64, color=INK, sw=4.6))
    f.append(text(420, 200, "U = 0 → сторч", size=10.5, color=MUTED, anchor="start"))
    f.append(text(420, 258, "→ чорний", size=10.5, color=INK, anchor="start"))
    f.append(text(420, 274, "глибокий", size=10.5, color=FIELD, anchor="start"))
    f.append(text(420, 340, "найкращий чорний із LCD;", size=11, color=FIELD, anchor="start"))
    f.append(text(420, 356, "кут кращий за TN, гірший IPS", size=11, color=MUTED, anchor="start"))

    # IPS — лежать, крутяться в площині
    panel(564, "IPS — in-plane switching", "лежать; крутяться В ПЛОЩИНІ скла")
    for k in range(4):
        cx = 624 + k * 34
        f.append(rod(cx, 214, 12, ln=26))
        f.append(rod(cx, 250, -12, ln=26))
    # електроди в площині (гребінка знизу)
    f.append(plus(600, 300, 6))
    f.append(minus(690, 300, 6))
    f.append(text(687, 340, "широкий кут, стабільний колір;", size=11, color=FIELD, anchor="end"))
    f.append(text(687, 356, "дорожче, чорний гірший за VA", size=11, color=MUTED, anchor="end"))

    f.append(text(W / 2, 398, "Молекули крутяться механічно й повільно (мілісекунди), і тим повільніше, чим холодніше:",
                  size=12.5, color=MUTED, italic=True))
    f.append(text(W / 2, 418, "звідси «шлейф» за рухом і чутливість LCD до морозу — на відміну від електронного OLED.",
                  size=12.5, color=MUTED, italic=True))
    f.append(text(W / 2, 448, "Одна фізика заслінки — три різні компроміси лише від того, як розставити ті самі молекули.",
                  size=12.5, color=INK, italic=True))
    render(os.path.join(IMG, "lcd-modes.svg"), W, H, *f)


# ── D2. Світловий бюджет підсвітки (водоспад втрат) ─────────────────────────
def fig_light_budget():
    W, H = 800, 430
    f = [text(W / 2, 34, "Куди дівається світло підсвітки: водоспад втрат", size=19, bold=True),
         text(W / 2, 55, "лампа світить на 100%, до ока доходять одиниці відсотків — решту з'їдає стос",
              size=12.5, color=MUTED, italic=True)]
    x0, base_y, top_y = 150, 360, 96
    full = base_y - top_y  # висота 100%
    # стадії: (підпис, частка ЩО ЛИШАЄТЬСЯ після стадії, підпис-втрата)
    stages = [
        ("підсвітка", 1.00, "100%"),
        ("поляризатор", 0.50, "−50% поляризації"),
        ("апертура TFT", 0.35, "×0.7 площі"),
        ("кольорофільтр", 0.117, "÷3 на R·G·B"),
        ("поляризатор", 0.094, "×0.8"),
        ("скло", 0.075, "≈7–8% до ока"),
    ]
    n = len(stages)
    bw = 96
    gap = (W - 2 * x0 + bw) / n
    prev = None
    for i, (lab, frac, loss) in enumerate(stages):
        cx = x0 + i * gap
        h = full * frac
        y = base_y - h
        col = FIELD if i == 0 else (POS if i in (1, 3) else MUTED)
        fillc = "#e7f5ea" if i == 0 else ("#fdeceb" if i in (1, 3) else "#eef0f2")
        f.append(rect(cx - bw / 2, y, bw, h, fill=fillc, stroke=col, sw=1.6, rx=3))
        f.append(text(cx, y - 8, "%d%%" % round(frac * 100), size=13, bold=True,
                      color=(FIELD if i == 0 else INK)))
        f.append(text(cx, base_y + 24, lab, size=10.5, color=INK))
        f.append(text(cx, base_y + 44, loss, size=9.5, color=col))
        if prev is not None:
            f.append(line(prev[0] + bw / 2, prev[1], cx - bw / 2, y, color="#c9ccd1", sw=1.2, dash="4 3"))
        prev = (cx, y)
    f.append(line(x0 - bw / 2 - 8, base_y, W - x0 + bw / 2 + 8, base_y, color=INK, sw=2))
    f.append(text(W / 2, 410, "Ось чому підсвітка мусить бути в РАЗИ яскравіша за картинку — і чому вона головний споживач.",
                  size=12.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "light-budget.svg"), W, H, *f)


# ── D3. Межа Альта–Плешка: чому пасивна матриця здувається ───────────────────
def fig_alt_pleshko():
    import math
    W, H = 820, 440
    f = [text(W / 2, 34, "Межа Альта–Плешка: чому без транзистора контраст помирає", size=19, bold=True),
         text(W / 2, 55, "найкращий можливий відрив «увімкнено/вимкнено» падає до 1, щойно рядків стає багато",
              size=12.5, color=MUTED, italic=True)]
    # осі
    ox, oy = 110, 350
    ax_w, ax_h = 600, 250
    f.append(arrow(ox, oy, ox + ax_w + 20, oy, color=INK, sw=2))
    f.append(arrow(ox, oy, ox, oy - ax_h - 14, color=INK, sw=2))
    f.append(text(ox + ax_w + 16, oy + 22, "рядків N →", size=12, anchor="end"))
    f.append(text(ox - 6, oy - ax_h - 4, "відрив Von/Voff", size=12, anchor="start"))
    # крива ratio = sqrt((sqrt(N)+1)/(sqrt(N)-1)); N від 2 до 260
    def ratio(N):
        s = math.sqrt(N)
        return math.sqrt((s + 1) / (s - 1))
    Nmax = 256
    RCEIL = 2.5  # стеля шкали (ratio(2) ≈ 2.41)
    # шкала: ratio 1..RCEIL → висота
    def X(N):
        return ox + ax_w * (N - 2) / (Nmax - 2)
    def Y(r):
        return oy - ax_h * (r - 1.0) / (RCEIL - 1.0)
    # сітка по y
    for r in (1.0, 1.5, 2.0, 2.5):
        f.append(line(ox, Y(r), ox + ax_w, Y(r), color="#eceef0", sw=1))
        f.append(text(ox - 10, Y(r) + 4, "%.2f" % r, size=10.5, color=MUTED, anchor="end"))
    # позначки N
    for N in (2, 16, 64, 128, 256):
        f.append(text(X(N), oy + 20, str(N), size=10.5, color=MUTED))
        f.append(line(X(N), oy, X(N), oy + 4, color=INK, sw=1.2))
    # крива
    pts = []
    N = 2.0
    while N <= Nmax:
        pts.append("%.1f,%.1f" % (X(N), Y(ratio(N))))
        N += 2
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(pts), NEG))
    # точки-приклади
    for N in (2, 16, 64, 256):
        f.append(circle(X(N), Y(ratio(N)), 4.5, fill=NEG, stroke=BG, sw=1.5))
    f.append(text(X(2) + 16, Y(ratio(2)) + 2, "N=2 → 2.41 (великий відрив)", size=11.5, color=NEG, anchor="start"))
    f.append(text(X(16) + 10, Y(ratio(16)) - 10, "16 → 1.29", size=11.5, color=MUTED, anchor="start"))
    f.append(text(X(64) + 8, Y(ratio(64)) - 10, "64 → лише 1.13", size=11.5, color=POS, anchor="start"))
    f.append(text(X(256) - 8, Y(ratio(256)) - 12, "256 → 1.07: контрасту нема", size=11.5, color=POS, anchor="end"))
    # формула
    f.append(text(ox + 300, oy - ax_h + 20, "(Von/Voff)ₘₐₖₛ = √((√N + 1)/(√N − 1))",
                  size=13, bold=True, color=INK))
    f.append(text(W / 2, 410, "Активна матриця обходить цю межу: транзистор тримає піксель весь кадр, і N уже не тисне.",
                  size=12.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "alt-pleshko.svg"), W, H, *f)


# ── D4. Піксель OLED: керування СТРУМОМ (2T1C) і дрейф порога ────────────────
def fig_oled_pixel():
    W, H = 800, 420
    f = [text(W / 2, 34, "Піксель AMOLED: транзистор задає СТРУМ, а не заслінку", size=19, bold=True),
         text(W / 2, 55, "яскравість = струм крізь органіку; тому дрейф порога транзистора прямо псує колір",
              size=12.5, color=MUTED, italic=True)]
    # ── схема 2T1C зліва ──
    # лінії
    f.append(line(70, 120, 250, 120, color=INK, sw=2.4))
    f.append(text(66, 114, "SCAN", size=11, bold=True, anchor="end"))
    f.append(line(150, 92, 150, 120, color=INK, sw=2.4))
    f.append(text(150, 86, "DATA", size=11, bold=True))
    # T1 (ключ вибору)
    f.append(rect(126, 130, 48, 26, fill="#eef2f5", stroke=INK, sw=1.6, rx=4))
    f.append(text(150, 148, "T1", size=12, bold=True))
    f.append(line(150, 120, 150, 130, color=INK, sw=2))
    f.append(line(150, 156, 150, 178, color=INK, sw=2))
    # вузол затвора + конденсатор
    f.append(circle(150, 178, 3, fill=INK, stroke=INK, sw=1))
    f.append(line(150, 178, 110, 178, color=INK, sw=2))
    f.append(line(110, 170, 110, 186, color=INK, sw=3))
    f.append(line(96, 170, 96, 186, color=INK, sw=3))
    f.append(text(88, 165, "Cs", size=11, bold=True, anchor="end"))
    f.append(text(103, 205, "тримає напругу", size=9.5, color=MUTED, anchor="middle"))
    f.append(line(96, 186, 96, 300, color=INK, sw=2))
    # T2 (керує струмом)
    f.append(line(150, 178, 210, 178, color=INK, sw=2))
    f.append(rect(210, 165, 30, 48, fill="#e7f5ea", stroke=FIELD, sw=2, rx=4))
    f.append(text(225, 194, "T2", size=12, bold=True, color=FIELD))
    f.append(text(225, 232, "струмовий", size=9.5, color=FIELD))
    # VDD зверху до T2
    f.append(line(225, 120, 225, 165, color=POS, sw=2))
    f.append(line(200, 120, 250, 120, color=POS, sw=2))
    f.append(text(258, 124, "VDD", size=11, color=POS, bold=True, anchor="start"))
    # OLED знизу
    f.append(line(225, 213, 225, 250, color=INK, sw=2))
    # діод-символ OLED
    f.append('<polygon points="212,250 238,250 225,270" fill="#eaf0fd" stroke="%s" stroke-width="1.6"/>' % NEG)
    f.append(line(212, 270, 238, 270, color=NEG, sw=2.4))
    f.append(text(250, 264, "OLED", size=11, color=NEG, anchor="start"))
    f.append(arrow(244, 256, 262, 244, color=FIELD, sw=1.8))
    f.append(text(268, 240, "світло", size=10, color=FIELD, anchor="start"))
    f.append(line(225, 270, 225, 300, color=INK, sw=2))
    f.append(line(96, 300, 225, 300, color=INK, sw=2))
    f.append(text(160, 316, "спільний катод", size=10, color=MUTED))
    f.append(text(150, 350, "T1 записав напругу в Cs → Cs тримає її на затворі T2 →", size=11, color=INK))
    f.append(text(150, 366, "T2 жене СТАЛИЙ струм крізь OLED увесь кадр.", size=11, color=INK))

    # ── праворуч: дрейф порога ──
    gx, gy, gw, gh = 470, 130, 280, 170
    f.append(text(gx + gw / 2, gy - 12, "Чому потрібна компенсація", size=14, bold=True))
    f.append(arrow(gx, gy + gh, gx + gw + 10, gy + gh, color=INK, sw=2))
    f.append(arrow(gx, gy + gh, gx, gy - 6, color=INK, sw=2))
    f.append(text(gx + gw + 6, gy + gh + 20, "напруга затвора", size=10.5, anchor="end"))
    f.append(text(gx + 2, gy - 4, "струм → яскравість", size=10.5, anchor="start"))
    # крива «свіжий»
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % ("480,290 520,286 560,270 600,235 650,180 720,140", FIELD))
    f.append(text(724, 138, "свіжий", size=10.5, color=FIELD, anchor="start"))
    # крива «постарілий» — зсув праворуч (більший Vth)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" stroke-dasharray="6 4"/>'
             % ("520,290 560,287 600,274 640,244 690,190 745,150", POS))
    f.append(text(745, 168, "постарілий", size=10.5, color=POS, anchor="end"))
    f.append(text(gx + gw / 2, gy + gh + 40, "той самий код DATA → менший струм → тьмяніший і зсунутий колір",
                  size=10.5, color=MUTED, italic=True))
    f.append(text(W / 2, 406, "Тому в AMOLED навколо пікселя ставлять не 2, а 4–7 транзисторів — щоб виміряти й скомпенсувати дрейф.",
                  size=12.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "oled-pixel.svg"), W, H, *f)


# ── D5. E-ink: баланс сил і хвиля оновлення ─────────────────────────────────
def fig_eink_dynamics():
    W, H = 830, 430
    f = [text(W / 2, 34, "E-ink зблизька: чому повільно і чому «блимає» при оновленні", size=19, bold=True),
         text(W / 2, 55, "частинка повзе в'язкою рідиною (звідси мілісекунди), а щоб прибрати привид — скидання",
              size=12.5, color=MUTED, italic=True)]

    # ── ЛІВО: баланс сил на частинці ──
    f.append(text(210, 92, "Баланс сил на частинці", size=14, bold=True))
    f.append(rect(90, 108, 240, 190, fill="#f4fbff", stroke="#7fa9c4", sw=1.6, rx=8))
    # частинка в центрі
    pcx, pcy = 210, 210
    f.append(circle(pcx, pcy, 20, fill="#2b2f33", stroke="#2b2f33", sw=1))
    f.append(minus(pcx + 10, pcy - 10, 6))
    # сила поля вгору
    f.append(arrow(pcx, pcy - 24, pcx, pcy - 74, color=FIELD, sw=3))
    f.append(text(pcx + 8, pcy - 60, "F = qE (поле тягне)", size=11, color=FIELD, anchor="start"))
    # опір в'язкості вниз
    f.append(arrow(pcx, pcy + 24, pcx, pcy + 66, color=POS, sw=3))
    f.append(text(pcx + 8, pcy + 52, "6πηr·v (в'язкість гальмує)", size=10.5, color=POS, anchor="start"))
    f.append(text(210, 288, "рівновага → стала швидкість v", size=11, color=MUTED))
    f.append(text(210, 322, "v = qE / (6πηr)   →   час ≈ d / v", size=12.5, bold=True, color=INK))
    f.append(text(210, 344, "в'язке середовище → v мале → десятки–сотні мс", size=10.5, color=MUTED, italic=True))

    # ── ПРАВО: хвиля оновлення (waveform) ──
    ox, oy = 430, 250
    f.append(text(620, 92, "Хвиля оновлення пікселя", size=14, bold=True))
    f.append(arrow(ox, oy, ox + 350, oy, color=INK, sw=2))
    f.append(text(ox + 348, oy + 20, "час →", size=11, anchor="end"))
    f.append(line(ox, oy - 44, ox, oy + 44, color=INK, sw=1.6))
    f.append(text(ox - 8, oy - 40, "+V", size=10, color=MUTED, anchor="end"))
    f.append(text(ox - 8, oy + 44, "−V", size=10, color=MUTED, anchor="end"))
    f.append(line(ox, oy, ox + 350, oy, color="#e4e4e4", sw=1))
    # фази: скидання (кілька інверсій) → активація → запис
    seg = [
        (0, 40, +36, "скид", NEG),
        (40, 80, -36, None, NEG),
        (80, 120, +36, None, NEG),
        (120, 160, -36, "→ білий/чорний блимає", NEG),
        (160, 210, 0, "пауза", MUTED),
        (210, 300, -36, "запис", POS),
    ]
    for x1, x2, lvl, lab, col in seg:
        yy = oy - lvl
        f.append(line(ox + x1, yy, ox + x2, yy, color=col, sw=3))
        # вертикальні переходи
        f.append(line(ox + x2, oy - lvl, ox + x2, oy, color=col, sw=1.4, dash="3 2"))
        if lab:
            f.append(text(ox + (x1 + x2) / 2, oy + (60 if lvl <= 0 else -48), lab, size=10, color=col))
    f.append(text(ox + 80, oy - 62, "інверсії стирають привид", size=10.5, color=NEG))
    f.append(text(620, oy + 96, "Тому повне оновлення «моргає» чорним/білим: інакше лишиться привид (ghosting).",
                  size=11, color=MUTED, italic=True))
    f.append(text(W / 2, 412, "Бістабільність — платня натурою: між кадрами струму 0, зате перемикання повільне і з ритуалом скидання.",
                  size=12, color=MUTED, italic=True))
    render(os.path.join(IMG, "eink-dynamics.svg"), W, H, *f)


def fig_pixel_shift():
    """proj: pixel-shift — статичний елемент гуляє в межах безпечного поля,
    тож жоден підпіксель не світить весь час у тій самій точці."""
    W, H = 720, 400
    f = []
    # ── ліворуч: панель зі статичним рядком і полем зсуву ──
    px, py, pw, ph = 60, 70, 300, 250
    f.append(rect(px, py, pw, ph, fill="#101418", stroke=INK, sw=2, rx=8))
    f.append(text(px + pw / 2, py - 14, "екран (темний UI)", size=12, color=MUTED))
    # безпечне поле зсуву (пунктир): куди може від'їхати картинка
    m = 16
    f.append(rect(px + m, py + m, pw - 2 * m, ph - 2 * m, fill="none",
                  stroke=FIELD, sw=1.4, rx=6))
    f.append(text(px + pw - m - 4, py + m + 14, "поле зсуву", size=10,
                  color=FIELD, anchor="end"))
    # три позиції одного статичного елемента (рядок статусу) у різні хвилини
    poss = [(0, 0, "#8a99a8", "0 хв"), (10, 6, "#b0c4d8", "20 хв"),
            (-8, 12, BG, "40 хв")]
    for dx, dy, col, lab in poss:
        bx, by = px + 40 + dx, py + 40 + dy
        f.append(rect(bx, by, 130, 20, fill="none", stroke=col, sw=2, rx=4))
        f.append(text(bx + 65, by + 14, "СТАТУС · 12:04", size=11, color=col))
        f.append(text(bx - 6, by + 14, lab, size=9, color=MUTED, anchor="end"))
    f.append(text(px + pw / 2, py + ph - 12,
                  "той самий рядок повільно кочує", size=11, color="#c9d4de"))
    # ── праворуч: чому це рятує — знос підпікселя в точці ──
    gx, gy, gw, gh = 430, 92, 230, 180
    f.append(text(gx + gw / 2, gy - 22, "знос люмінофора в одній точці",
                  size=12, color=INK))
    # осі
    f.append(line(gx, gy, gx, gy + gh, color=INK, sw=1.5))
    f.append(line(gx, gy + gh, gx + gw, gy + gh, color=INK, sw=1.5))
    f.append(text(gx - 8, gy + 6, "знос", size=10, color=MUTED, anchor="end"))
    f.append(text(gx + gw, gy + gh + 16, "час", size=10, color=MUTED, anchor="end"))
    # без зсуву — крута лінія (та сама точка світить завжди)
    f.append(line(gx, gy + gh, gx + gw, gy + 8, color=POS, sw=3))
    f.append(text(gx + gw - 4, gy + 4, "без зсуву", size=10.5, color=POS, anchor="end"))
    # зі зсувом — пилка (точка світить лише зрідка), нижчий нахил
    import math
    pts = []
    y = gy + gh
    for i in range(0, gw + 1, 6):
        # східчастий пологий підйом: світить ~третину часу
        rise = 0.42 if (i // 30) % 3 == 0 else 0.06
        y -= rise * 6
        pts.append("%.1f,%.1f" % (gx + i, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
             % (" ".join(pts), FIELD))
    f.append(text(gx + gw - 4, y - 6, "зі зсувом", size=10.5, color=FIELD, anchor="end"))
    f.append(text(W / 2, 384,
                  "Зсув на кілька пікселів раз на кілька хвилин «розмазує» знос по площі — привид не встигає впектися.",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "pixel-shift.svg"), W, H, *f)


def fig_wear_model():
    """proj: модель зносу — сині підпікселі старіють найшвидше; облік
    світло-годин і приглушення вирівнюють спрацювання каналів."""
    W, H = 720, 380
    f = []
    ox, oy, gw, gh = 90, 70, 540, 210
    # осі
    f.append(line(ox, oy, ox, oy + gh, color=INK, sw=1.5))
    f.append(line(ox, oy + gh, ox + gw, oy + gh, color=INK, sw=1.5))
    f.append(text(ox - 10, oy + 4, "яскравість", size=11, color=MUTED, anchor="end"))
    f.append(text(ox - 10, oy + 16, "каналу, %", size=11, color=MUTED, anchor="end"))
    f.append(text(ox + gw, oy + gh + 18, "світло-години", size=11, color=MUTED, anchor="end"))
    # сітка 100 / 70 %
    for frac, lab in [(0.0, "100"), (0.3, "70")]:
        yy = oy + gh * frac
        f.append(line(ox, yy, ox + gw, yy, color="#e2e6ea", sw=1))
        f.append(text(ox - 6, yy + 4, lab, size=9.5, color=MUTED, anchor="end"))
    import math
    def curve(tau, col, dash=None, lab=None, laby=0):
        pts = []
        for i in range(0, gw + 1, 6):
            t = i / gw
            v = math.exp(-t / tau)              # спад люмінофора
            y = oy + gh * (1 - v)
            pts.append("%.1f,%.1f" % (ox + i, y))
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"%s/>'
                 % (" ".join(pts), col, d))
        if lab:
            f.append(text(ox + gw + 6, oy + gh * (1 - math.exp(-1 / tau)) + laby,
                          lab, size=11, color=col, anchor="start"))
    # без обліку: синій падає круто, червоний/зелений повільно → колір «пливе»
    curve(2.2, POS, lab="синій", laby=4)          # найшвидший знос
    curve(4.5, FIELD, lab="зелений", laby=2)
    curve(6.0, NEG, lab="червоний", laby=2)
    # з обліком (приглушений синій): пунктир, знос вирівняний
    curve(4.0, "#7a4fd0", dash="5 3", lab="синій*", laby=16)
    f.append(text(ox + 150, oy + 24,
                  "* синій наперед приглушено → канали старіють в один темп",
                  size=10.5, color="#7a4fd0", anchor="start"))
    f.append(text(W / 2, 356,
                  "Без обліку синій вигоряє першим — біле з роками жовтіє; облік світло-годин дає привід приглушити синє заздалегідь.",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "wear-model.svg"), W, H, *f)


# ── Вставка math-alt-pleshko ────────────────────────────────────────────────
def fig_ap_waveforms():
    """math: що бачить піксель за кадр. Стовпець весь кадр качає ±Vc (дані),
    а рядок один-єдиний такт із N подає селект Vr. Різниця «увімк/вимк» —
    лише в тому одному такті, решту N−1 тактів обидва пікселі однакові."""
    import math
    W, H = 840, 470
    f = [text(W / 2, 32, "Що бачить комірка за один кадр із N рядків", size=19, bold=True),
         text(W / 2, 53, "різниця «увімкнено / вимкнено» живе лише в ОДНОМУ такті селекту з N — звідси й уся межа",
              size=12.5, color=MUTED, italic=True)]
    ox, oy = 95, 250          # нуль осі напруги
    slot = 74                 # ширина такту
    Ntacts = 6                # показуємо 6 тактів (один — селект, п'ять — ні)
    sel_i = 2                 # індекс такту, коли вибрано наш рядок
    Vr = 118.0                # висота селект-піка (умовні px)
    Vc = 40.0                 # висота дата-піка
    # осі
    f.append(line(ox - 20, oy, ox + Ntacts * slot + 30, oy, color=INK, sw=2))
    f.append(text(ox + Ntacts * slot + 26, oy - 8, "час →", size=12, anchor="end"))
    f.append(text(ox - 26, oy + 5, "0", size=11, color=MUTED, anchor="end"))
    # межі тактів + підписи
    for i in range(Ntacts + 1):
        x = ox + i * slot
        f.append(line(x, oy - 150, x, oy + 150, color="#eef0f2", sw=1))
    for i in range(Ntacts):
        cx = ox + i * slot + slot / 2
        lab = "рядок j\n(СЕЛЕКТ)" if i == sel_i else "інший\nрядок"
        col = FIELD if i == sel_i else MUTED
        f.append(mtext(cx, oy + 168, lab, size=10.5, color=col, anchor="middle"))
    f.append(text(ox + Ntacts * slot + 30, oy + 168, "…×N", size=11, color=MUTED, anchor="start"))

    def step(i, top, col, sw=3, dash=None):
        x0 = ox + i * slot + 4
        x1 = ox + (i + 1) * slot - 4
        return (line(x0, oy - top, x1, oy - top, color=col, sw=sw, dash=dash)
                + line(x0, oy, x0, oy - top, color=col, sw=1.4, dash="2,3")
                + line(x1, oy, x1, oy - top, color=col, sw=1.4, dash="2,3"))

    # ── верх: рядковий (селект) сигнал НАШОГО рядка ──
    f.append(text(ox - 30, oy - 128, "рядок", size=11.5, color=INK, anchor="end", bold=True))
    for i in range(Ntacts):
        if i == sel_i:
            f.append(step(i, Vr, FIELD, sw=3.4))
            f.append(text(ox + i * slot + slot / 2, oy - Vr - 8, "Vr", size=12, color=FIELD, bold=True))
        else:
            f.append(step(i, 0, MUTED, sw=2))   # 0 В на невибраному рядку
    # ── низ таблиці: два сценарії комірки в НАШОМУ рядку ──
    # (a) увімкнена комірка: дата протифазна селекту → сумарна напруга велика
    # (b) вимкнена: дата у фазі → у селект-такті напруги майже гасяться
    yA = oy + 250
    # Ми малюємо СТОВПЦЕВИЙ сигнал (дані) — він тече ВЕСЬ кадр, ±Vc.
    f.append(text(ox - 30, oy - 40, "стовпець", size=11.5, color=NEG, anchor="end", bold=True))
    patt = [+1, -1, +1, +1, -1, +1]   # умовна послідовність даних інших рядків
    for i in range(Ntacts):
        s = patt[i]
        top = Vc * s
        x0 = ox + i * slot + 4; x1 = ox + (i + 1) * slot - 4
        f.append(line(x0, oy - top, x1, oy - top, color=NEG, sw=2.6))
        f.append(line(x0, oy, x0, oy - top, color=NEG, sw=1.2, dash="2,3"))
        f.append(line(x1, oy, x1, oy - top, color=NEG, sw=1.2, dash="2,3"))
    f.append(text(ox + sel_i * slot + slot / 2, oy + Vc + 20, "±Vc", size=11.5, color=NEG, bold=True))

    # анотації: у селект-такті комірка бачить Vr∓Vc; у решті — лише ±Vc
    f.append(textbox(ox + sel_i * slot + slot / 2, oy - Vr - 40,
                     "селект-такт:\nкомірка бачить  Vr ∓ Vc", size=11, pad=7,
                     fill="#eafaf0", stroke=FIELD, color=INK)[0])
    f.append(textbox(ox + (Ntacts - 1) * slot + slot / 2 + 20, oy - 120,
                     "решта N−1 тактів:\nлише  ± Vc", size=11, pad=7,
                     fill="#eef2fd", stroke=NEG, color=INK)[0])
    f.append(text(W / 2, H - 16,
                  "Обидва пікселі стовпця однакові в N−1 тактах; вибір знака Vc в ОДНОМУ селект-такті — усе, чим «увімк» відрізняється від «вимк».",
                  size=12, color=MUTED, italic=True))
    render(os.path.join(IMG, "ap-waveforms.svg"), W, H, *f)


def fig_ap_bias():
    """math: селект-відношення Von/Voff як функція біаса b при кількох N.
    Кожна крива має ГОСТРИЙ максимум рівно при b = 1/√N — це й доводить, що
    оптимум не постулат, а справжня точка максимуму."""
    import math
    W, H = 840, 470
    f = [text(W / 2, 32, "Оптимальний біас: відрив має максимум рівно при b = 1/√N", size=19, bold=True),
         text(W / 2, 53, "не постулат, а вершина кривої — ліворуч селект слабне, праворуч дані «підтоплюють» вимкнений піксель",
              size=12.5, color=MUTED, italic=True)]
    ox, oy = 100, 360
    ax_w, ax_h = 620, 270

    # селект-відношення від b і N:  r(b,N) = sqrt( ((1/b)+... ) ) — беремо канонічний вираз
    # Von²/Voff² = ( (√N·b?  ) ) ... використовуємо перевірену форму через u=1/b:
    #   r² = ( (1 + (N-1)b²) + 2b·? )  — щоб не плутати, рахуємо через відому
    # параметризацію: селект-напруга ∝ 1, дата ∝ b; тоді
    #   Von² ∝ (1+b)² + (N-1)b² ,  Voff² ∝ (1−b)² + (N-1)b²   (з точністю до спільного множника)
    def r2(b, N):
        on = (1 + b) ** 2 + (N - 1) * b * b
        off = (1 - b) ** 2 + (N - 1) * b * b
        return on / off
    def ratio(b, N):
        return math.sqrt(r2(b, N))

    curves = [(4, "#2457d6", "N=4"), (16, "#c0392b", "N=16"), (64, FIELD, "N=64")]
    # шкала: b від 0 до 0.75; r від 1 до стелі
    bmax = 0.75
    rceil = 2.6
    def X(b): return ox + ax_w * (b / bmax)
    def Y(r): return oy - ax_h * (r - 1.0) / (rceil - 1.0)
    # осі
    f.append(arrow(ox, oy, ox + ax_w + 20, oy, color=INK, sw=2))
    f.append(arrow(ox, oy, ox, oy - ax_h - 14, color=INK, sw=2))
    f.append(text(ox + ax_w + 16, oy + 22, "біас b = Vc/Vr →", size=12, anchor="end"))
    f.append(text(ox - 6, oy - ax_h - 4, "відрив Von/Voff", size=12, anchor="start"))
    for r in (1.0, 1.5, 2.0, 2.5):
        f.append(line(ox, Y(r), ox + ax_w, Y(r), color="#eceef0", sw=1))
        f.append(text(ox - 10, Y(r) + 4, "%.1f" % r, size=10.5, color=MUTED, anchor="end"))
    for b in (0.0, 0.25, 0.5, 0.75):
        f.append(text(X(b), oy + 20, "%.2f" % b, size=10.5, color=MUTED))
        f.append(line(X(b), oy, X(b), oy + 4, color=INK, sw=1.2))
    # криві + позначка вершини
    for N, col, lab in curves:
        pts = []
        b = 0.001
        while b <= bmax:
            pts.append("%.1f,%.1f" % (X(b), Y(ratio(b, N))))
            b += 0.004
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(pts), col))
        bopt = 1.0 / math.sqrt(N)
        ry = ratio(bopt, N)
        f.append(line(X(bopt), oy, X(bopt), Y(ry), color=col, sw=1.2, dash="4,4"))
        f.append(circle(X(bopt), Y(ry), 5, fill=col, stroke=BG, sw=1.6))
        f.append(text(X(bopt), Y(ry) - 12, "b=1/√%d=%.2f" % (N, bopt), size=10.5, color=col, bold=True))
    # легенда
    lx, ly = ox + ax_w - 150, oy - ax_h + 6
    for k, (N, col, lab) in enumerate(curves):
        yy = ly + k * 20
        f.append(line(lx, yy, lx + 22, yy, color=col, sw=3))
        f.append(text(lx + 28, yy + 4, lab, size=11.5, color=col, anchor="start"))
    f.append(text(W / 2, H - 16,
                  "Що більше рядків N, то нижча й гостріша вершина: найкращий можливий відрив невблаганно повзе до 1.",
                  size=12, color=MUTED, italic=True))
    render(os.path.join(IMG, "ap-bias.svg"), W, H, *f)


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
    # детальна
    fig_lcd_modes()
    fig_light_budget()
    fig_alt_pleshko()
    fig_oled_pixel()
    fig_eink_dynamics()
    # вставка proj-oled-compensation
    fig_pixel_shift()
    fig_wear_model()
    # вставка math-alt-pleshko
    fig_ap_waveforms()
    fig_ap_bias()
    print("OK: 19 figures ->", IMG)

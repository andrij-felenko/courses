# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

LIVE_FILL = "#dfe8fc"      # дійсне / корисне
DEAD_FILL = "#fbe6e3"      # браковане / пошкоджене
FREE_FILL = "#ffffff"      # вільне / стерте
WARM_FILL = "#fff4e0"      # службове / OOB
COOL_FILL = "#dff0e6"      # резерв / перепризначене
WARM = "#b8860b"

# ── 1. Фабричний брак проти експлуатаційного зносу ─────────────────────────
def fig_factory_vs_grown():
    W, H = 1180, 520
    p = []
    p.append(text(W / 2, 38, "два джерела бракованих блоків: фабрика та експлуатація",
                  size=18, bold=True, color=INK))

    BW = 500
    BH = 410
    X1, X2 = 60, 620
    Y0 = 70

    # Ліва колонка: Фабричні дефекти
    p.append(rect(X1, Y0, BW, BH, fill=FILL, stroke=POS, sw=1.8, rx=8))
    p.append(text(X1 + BW / 2, Y0 + 36, "фабричні дефекти (Factory Bad Blocks)",
                  size=16, bold=True, color=POS))
    p.append(text(X1 + BW / 2, Y0 + 64, "наявні одразу після виготовлення кремнієвого кристала",
                  size=13.5, color=MUTED))

    f_items = [
        ("мікротріщини та домішки", "дефекти літографії та кристалічної решітки кремнію"),
        ("закорочені доріжки", "замикання ліній бітів (Bitline) або слів (Wordline)"),
        ("витік тунельного оксиду", "нездатність утримувати заряд або очищатися до 0xFF"),
        ("маркування виробником", "байт != 0xFF записано в OOB сторінки 0 на заводі"),
    ]
    for i, (head, desc) in enumerate(f_items):
        y = Y0 + 95 + i * 72
        p.append(rect(X1 + 20, y, BW - 40, 58, fill=DEAD_FILL, stroke=POS, sw=1.2, rx=4))
        p.append(text(X1 + 36, y + 24, head, size=14, bold=True, color=POS, anchor="start"))
        p.append(text(X1 + 36, y + 46, desc, size=12.5, color=INK, anchor="start"))

    # Права колонка: Експлуатаційні дефекти
    p.append(rect(X2, Y0, BW, BH, fill=FILL, stroke=NEG, sw=1.8, rx=8))
    p.append(text(X2 + BW / 2, Y0 + 36, "нарощені дефекти (Grown Bad Blocks)",
                  size=16, bold=True, color=NEG))
    p.append(text(X2 + BW / 2, Y0 + 64, "виникають динамічно під час роботи накопичувача",
                  size=13.5, color=MUTED))

    g_items = [
        ("деградація діелектрика", "накопичення пасток заряду від тисяч циклів P/E"),
        ("збій стирання (Erase Fail)", "високовольтний імпульс не скидає поріг комірок"),
        ("збій запису (Program Fail)", "комірка не досягає цільового рівня напруги за таймаут"),
        ("невиправні біти (UECC)", "помилки перевищують коригувальну здатність ECC-коду"),
    ]
    for i, (head, desc) in enumerate(g_items):
        y = Y0 + 95 + i * 72
        p.append(rect(X2 + 20, y, BW - 40, 58, fill=LIVE_FILL, stroke=NEG, sw=1.2, rx=4))
        p.append(text(X2 + 36, y + 24, head, size=14, bold=True, color=NEG, anchor="start"))
        p.append(text(X2 + 36, y + 46, desc, size=12.5, color=INK, anchor="start"))

    render(os.path.join(IMG, 'factory-vs-grown.svg'), W, H, *p)


# ── 2. Будова блоку, сторінки та OOB-маркера ──────────────────────────────
def fig_oob_marker():
    W, H = 1180, 560
    p = []
    p.append(text(W / 2, 38, "розміщення маркера бракованого блоку в області Spare (OOB)",
                  size=18, bold=True, color=INK))

    # Схема фізичного блоку
    BX, BY, BW, BH = 60, 80, 280, 440
    p.append(rect(BX, BY, BW, BH, fill=FILL, stroke=LINE, sw=1.6, rx=6))
    p.append(text(BX + BW / 2, BY + 30, "фізичний блок (Eraseblock)", size=15, bold=True, color=INK))
    p.append(text(BX + BW / 2, BY + 52, "64 або 128 сторінок (1–4 МБ)", size=12.5, color=MUTED))

    pages = [
        ("сторінка 0 (перша)", True, POS),
        ("сторінка 1 (друга)", True, POS),
        ("сторінка 2", False, MUTED),
        ("...", False, MUTED),
        ("сторінка N-1 (остання)", True, POS),
    ]
    for i, (name, is_crit, col) in enumerate(pages):
        py = BY + 75 + i * 66
        fill_col = DEAD_FILL if is_crit else FREE_FILL
        p.append(rect(BX + 18, py, BW - 36, 52, fill=fill_col, stroke=col, sw=1.4, rx=4))
        p.append(text(BX + BW / 2, py + 32, name, size=13.5, bold=is_crit, color=col))

    # Стрілка від сторінки 0 до розгорнутої структури сторінки
    p.append(arrow(BX + BW - 18, BY + 101, 400, BY + 101, color=POS, sw=2))

    # Розгорнута сторінка
    SX, SY, SW, SH = 410, 80, 710, 440
    p.append(rect(SX, SY, SW, SH, fill=FILL, stroke=LINE, sw=1.6, rx=6))
    p.append(text(SX + SW / 2, SY + 30, "структура сторінки Flash (Page = Data + Spare/OOB)",
                  size=15, bold=True, color=INK))

    # Основна область даних (4096 байтів)
    DX, DY, DW, DH = SX + 30, SY + 70, 430, 110
    p.append(rect(DX, DY, DW, DH, fill=LIVE_FILL, stroke=NEG, sw=1.8, rx=4))
    p.append(text(DX + DW / 2, DY + 46, "основна область даних (Main Area)", size=15, bold=True, color=NEG))
    p.append(text(DX + DW / 2, DY + 74, "4096 байтів (або 2048 / 8192)", size=13, color=MUTED))

    # Spare / OOB область (224 байти)
    OX, OY, OW, OH = DX + DW + 15, SY + 70, 205, 110
    p.append(rect(OX, OY, OW, OH, fill=WARM_FILL, stroke=WARM, sw=1.8, rx=4))
    p.append(text(OX + OW / 2, OY + 46, "резерв (OOB/Spare)", size=15, bold=True, color=WARM))
    p.append(text(OX + OW / 2, OY + 74, "224 байти (ECC + BBM)", size=13, color=MUTED))

    # Збільшений фрагмент OOB
    ZX, ZY, ZW, ZH = SX + 30, SY + 220, SW - 60, 180
    p.append(rect(ZX, ZY, ZW, ZH, fill="#ffffff", stroke=MUTED, sw=1.4, rx=4))
    p.append(text(ZX + 20, ZY + 28, "розподіл байтів усередині Spare Area:",
                  size=13.5, bold=True, color=INK, anchor="start"))

    # Байт 0 - Маркер
    p.append(rect(ZX + 20, ZY + 45, 180, 80, fill=DEAD_FILL, stroke=POS, sw=2, rx=4))
    p.append(text(ZX + 110, ZY + 75, "байт 0 (або 5)", size=14, bold=True, color=POS))
    p.append(text(ZX + 110, ZY + 102, "Bad Block Marker", size=12.5, bold=True, color=POS))

    # Байти 1..N - Службові дані файлової системи / FTL
    p.append(rect(ZX + 215, ZY + 45, 190, 80, fill=WARM_FILL, stroke=WARM, sw=1.5, rx=4))
    p.append(text(ZX + 310, ZY + 75, "байти 1 .. 31", size=13.5, bold=True, color=WARM))
    p.append(text(ZX + 310, ZY + 102, "метадані FTL / UBI", size=12.5, color=MUTED))

    # Байти ECC
    p.append(rect(ZX + 420, ZY + 45, 210, 80, fill=COOL_FILL, stroke=FIELD, sw=1.5, rx=4))
    p.append(text(ZX + 525, ZY + 75, "байти 32 .. 223", size=13.5, bold=True, color=FIELD))
    p.append(text(ZX + 525, ZY + 102, "коди захисту ECC", size=12.5, color=MUTED))

    # Пояснення значень
    p.append(text(ZX + 20, ZY + 155,
                  "0xFF = блок справний; будь-яке інше значення (0x00) = блок бракований",
                  size=13, bold=True, color=POS, anchor="start"))

    render(os.path.join(IMG, 'oob-bad-block-marker.svg'), W, H, *p)


# ── 3. Стратегії перепризначення блоків ─────────────────────────────────────
def fig_bbt_remapping():
    W, H = 1180, 580
    p = []
    p.append(text(W / 2, 38, "стратегії обходу дефектів: лінійний пропуск проти резервного пулу",
                  size=18, bold=True, color=INK))

    # 1. Linear Skip
    Y1 = 80
    p.append(text(60, Y1 + 22, "1. Лінійний пропуск (Skip Block):", size=15, bold=True, color=INK, anchor="start"))
    p.append(text(60, Y1 + 44, "логічні блоки підряд відображаються на справні фізичні зі зсувом",
                  size=13, color=MUTED, anchor="start"))

    # Ряд фізичних блоків
    blocks_1 = [
        ("Блок 0", "L0", LIVE_FILL, NEG),
        ("Блок 1", "L1", LIVE_FILL, NEG),
        ("Блок 2 (БРАК)", "✖", DEAD_FILL, POS),
        ("Блок 3", "L2", LIVE_FILL, NEG),
        ("Блок 4", "L3", LIVE_FILL, NEG),
        ("Блок 5 (БРАК)", "✖", DEAD_FILL, POS),
        ("Блок 6", "L4", LIVE_FILL, NEG),
        ("Блок 7", "L5", LIVE_FILL, NEG),
    ]
    for i, (p_name, l_name, fill_c, stroke_c) in enumerate(blocks_1):
        x = 60 + i * 132
        p.append(rect(x, Y1 + 60, 122, 60, fill=fill_c, stroke=stroke_c, sw=1.6, rx=4))
        p.append(text(x + 61, Y1 + 84, p_name, size=12, bold=True, color=stroke_c))
        p.append(text(x + 61, Y1 + 106, f"дані: {l_name}", size=12.5, bold=True, color=INK))

    # 2. Reserved Pool Remapping
    Y2 = 260
    p.append(text(60, Y2 + 22, "2. Перепризначення в резервний пул (Remapping Table / LUT):",
                  size=15, bold=True, color=INK, anchor="start"))
    p.append(text(60, Y2 + 44, "адресація користувача лишається фіксованою; збійний блок перенаправляється в кінець кристала",
                  size=13, color=MUTED, anchor="start"))

    # Основна зона
    p.append(rect(60, Y2 + 65, 620, 110, fill=FILL, stroke=LINE, sw=1.4, rx=6))
    p.append(text(370, Y2 + 88, "основний простір користувача (User Area)", size=13.5, bold=True, color=INK))

    user_blocks = [
        ("Блок 0", "L0", LIVE_FILL, NEG),
        ("Блок 1", "L1", LIVE_FILL, NEG),
        ("Блок 2 (БРАК)", "перенаправлено", DEAD_FILL, POS),
        ("Блок 3", "L3", LIVE_FILL, NEG),
    ]
    for i, (p_name, l_name, fill_c, stroke_c) in enumerate(user_blocks):
        x = 80 + i * 145
        p.append(rect(x, Y2 + 102, 132, 58, fill=fill_c, stroke=stroke_c, sw=1.5, rx=4))
        p.append(text(x + 66, Y2 + 124, p_name, size=12, bold=True, color=stroke_c))
        p.append(text(x + 66, Y2 + 146, l_name, size=11.5, bold=(l_name != "перенаправлено"), color=INK))

    # Резервний пул
    p.append(rect(730, Y2 + 65, 390, 110, fill=COOL_FILL, stroke=FIELD, sw=1.4, rx=6))
    p.append(text(925, Y2 + 88, "резервний пул (Reserved Pool)", size=13.5, bold=True, color=FIELD))

    pool_blocks = [
        ("Резерв 0", "дані L2", LIVE_FILL, FIELD),
        ("Резерв 1", "вільний", FREE_FILL, MUTED),
    ]
    for i, (p_name, l_name, fill_c, stroke_c) in enumerate(pool_blocks):
        x = 750 + i * 180
        p.append(rect(x, Y2 + 102, 165, 58, fill=fill_c, stroke=stroke_c, sw=1.5, rx=4))
        p.append(text(x + 82, Y2 + 124, p_name, size=12.5, bold=True, color=stroke_c))
        p.append(text(x + 82, Y2 + 146, l_name, size=12, color=INK))

    # Стрілка перепризначення
    p.append(arrow(436, Y2 + 131, 750, Y2 + 131, color=POS, sw=2))

    # Пояснення внизу
    p.append(fitbox(60, Y2 + 200, 1060, 80,
                    ["таблиця дефектів (BBT) зберігає відповідність «Блок 2 → Резерв 0» у RAM та на Flash;",
                     "верхній рівень звертається за адресою Блоку 2, а контролер прозоро читає Резерв 0"],
                    size=13.5, fill=WARM_FILL, stroke=WARM, sw=1.6))

    render(os.path.join(IMG, 'bbt-remapping.svg'), W, H, *p)


# ── 4. Життєвий цикл дефектного блоку ──────────────────────────────────────
def fig_lifecycle():
    W, H = 1180, 560
    p = []
    p.append(text(W / 2, 38, "життєвий цикл блоку: від виявлення збою до виведення з обігу",
                  size=18, bold=True, color=INK))

    X0 = 60
    BOX_W = 220
    BOX_H = 100
    GAP = 70

    stages = [
        ("1. Справний блок", ["робота в загальному пулі,", "читання, запис, стирання"], LIVE_FILL, NEG),
        ("2. Виявлення збою", ["Erase Fail / Program Fail", "або ліміт ECC (UECC)"], DEAD_FILL, POS),
        ("3. Евакуація даних", ["копіювання живих сторінок", "у свіжий резервний блок"], WARM_FILL, WARM),
        ("4. Виведення з обігу", ["позначка Grown Bad у BBT,", "виключення з пулу пулів"], COOL_FILL, FIELD),
    ]

    for i, (title, lines, fill_c, strk_c) in enumerate(stages):
        x = X0 + i * (BOX_W + GAP)
        y = 120
        p.append(rect(x, y, BOX_W, BOX_H, fill=fill_c, stroke=strk_c, sw=1.8, rx=6))
        p.append(text(x + BOX_W / 2, y + 30, title, size=14.5, bold=True, color=strk_c))
        for j, ln in enumerate(lines):
            p.append(text(x + BOX_W / 2, y + 58 + j * 20, ln, size=12.5, color=INK))

        if i < len(stages) - 1:
            p.append(arrow(x + BOX_W + 10, y + BOX_H / 2, x + BOX_W + GAP - 10, y + BOX_H / 2, color=LINE, sw=2))

    # Нижня гілка: Захист від втрати живлення під час оновлення BBT
    p.append(rect(X0, 270, 1060, 240, fill=FILL, stroke=LINE, sw=1.4, rx=6))
    p.append(text(X0 + 530, 302, "двоетапний запис таблиці BBT на Flash для захисту від збою живлення",
                  size=15, bold=True, color=INK))

    p.append(rect(X0 + 40, 330, 460, 150, fill=FREE_FILL, stroke=NEG, sw=1.5, rx=4))
    p.append(text(X0 + 270, 360, "основний блок BBT (Primary)", size=14, bold=True, color=NEG))
    p.append(text(X0 + 270, 390, "сигнатура: 'Bbt0' | версія: N+1", size=13, color=MUTED))
    p.append(text(X0 + 270, 420, "1. Стирається та записується першим", size=12.5, color=INK))
    p.append(text(X0 + 270, 445, "2. Якщо живлення зникне — діє дзеркало", size=12.5, color=POS))

    p.append(arrow(X0 + 510, 405, X0 + 550, 405, color=LINE, sw=2))

    p.append(rect(X0 + 560, 330, 460, 150, fill=FREE_FILL, stroke=FIELD, sw=1.5, rx=4))
    p.append(text(X0 + 790, 360, "дзеркальний блок BBT (Mirror)", size=14, bold=True, color=FIELD))
    p.append(text(X0 + 790, 390, "сигнатура: '1tbB' | версія: N+1", size=13, color=MUTED))
    p.append(text(X0 + 790, 420, "3. Оновлюється після успіху Primary", size=12.5, color=INK))
    p.append(text(X0 + 790, 445, "4. Завжди зберігає узгоджену копію", size=12.5, color=FIELD))

    render(os.path.join(IMG, 'bad-block-lifecycle.svg'), W, H, *p)


fig_factory_vs_grown()
fig_oob_marker()
fig_bbt_remapping()
fig_lifecycle()
print("All figures generated successfully.")

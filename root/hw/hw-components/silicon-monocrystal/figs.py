# -*- coding: utf-8 -*-
"""Фігури до теми «Кремній і монокристал».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Локальні відтінки понад палітру svgkit
SAND = "#d8c79a"     # пісок
GREY = "#9aa0a6"     # технічний кремній / метал
WAFER = "#aebfd8"    # кристал / пластина
GOLD = "#b9770e"     # «сонячний» рівень


# ── Тема 1. Ланцюг очищення: пісок → … → монокристал ─────────────────────────
def fig_chain():
    W, H = 760, 300
    f = [text(W / 2, 26, "Від піску до монокристала: ланцюг очищення", size=16, bold=True)]
    cols = [
        ("Кварцовий\nпісок SiO₂", "~98%", "кар'єр, пляж", SAND),
        ("Технічний\nкремній Si", "~99%", "піч + вуглець", GREY),
        ("Трихлорсилан\nSiHCl₃", "леткий", "дистиляція", "#cfe3f7"),
        ("Полікремній\n(стрижні)", "9N", "процес Сіменса", "#cdd3d9"),
        ("Монокристал\n(злиток)", "9N", "Чохральський", WAFER),
    ]
    n = len(cols)
    bw, bh, gap = 116, 92, 16
    total = n * bw + (n - 1) * gap
    x0 = (W - total) / 2
    cy = 150
    for i, (name, pur, sub, col) in enumerate(cols):
        x = x0 + i * (bw + gap)
        f.append(rect(x, cy - bh / 2, bw, bh, fill=col, stroke=INK, sw=2))
        f.append(mtext(x + bw / 2, cy - 18, name, size=13.5, bold=True))
        f.append(text(x + bw / 2, cy + 18, pur, size=14, color=POS, bold=True))
        f.append(text(x + bw / 2, cy + bh / 2 + 18, sub, size=11, color=MUTED))
        if i < n - 1:
            f.append(arrow(x + bw + 2, cy, x + bw + gap - 2, cy, color=INK, sw=2))
    f.append(text(W / 2, H - 14,
                  "Чистота росте зліва направо: домішок усе менше — від кар'єрного піску до «дев'яти дев'яток».",
                  size=12.5, color=MUTED, italic=True))
    return render(os.path.join(IMG, "chain.svg"), W, H, *f)


# ── Тема 2. Драбина чистоти: 2N / 6N / 9N ────────────────────────────────────
def fig_purity():
    W, H = 720, 330
    f = [text(W / 2, 26, "Що означає «чистота 9N» (nine nines)", size=16, bold=True)]
    rows = [
        ("2N — 99%", "технічний кремній", "1 чужий атом на 100", POS),
        ("6N — 99.9999%", "«сонячний», фотопанелі", "1 на мільйон", GOLD),
        ("9N — 99.9999999%", "електронний", "1 чужий атом на МІЛЬЯРД", FIELD),
    ]
    y = 70
    rh = 70
    for i, (head, use, note, col) in enumerate(rows):
        ry = y + i * (rh + 12)
        # ширина смуги «нечистоти» зменшується з рівнем (ілюстративно)
        f.append(rect(60, ry, 600, rh, fill=FILL, stroke=col, sw=2.5))
        f.append(text(80, ry + 28, head, size=16, color=col, anchor="start", bold=True))
        f.append(text(80, ry + 50, use, size=12.5, color=MUTED, anchor="start", italic=True))
        f.append(text(640, ry + 40, note, size=13.5, color=INK, anchor="end", bold=(i == 2)))
    f.append(text(W / 2, H - 12,
                  "Кожен крок очищення прибирає домішки на порядки; електроніці потрібен крайній рівень — 9N.",
                  size=12, color=MUTED, italic=True))
    return render(os.path.join(IMG, "purity.svg"), W, H, *f)


# ── Тема 3. Метод Чохральського ──────────────────────────────────────────────
def fig_czochralski():
    W, H = 720, 430
    f = [text(W / 2, 26, "Метод Чохральського: вирощування монокристала", size=16, bold=True)]
    # тигель
    f.append('<path d="M 140,210 L 140,300 Q 140,334 174,334 L 326,334 '
             'Q 360,334 360,300 L 360,210" fill="%s" stroke="%s" stroke-width="2.5"/>'
             % ("#efe7d2", INK))
    # розплав
    f.append('<path d="M 146,272 L 146,296 Q 146,326 176,326 L 324,326 '
             'Q 354,326 354,296 L 354,272 Z" fill="%s" stroke="%s" stroke-width="1.5"/>'
             % ("#f0a830", "#c07a10"))
    f.append(text(404, 300, "розплав кремнію", size=13, color=INK, anchor="start"))
    f.append(text(404, 320, "~1420 °C", size=12.5, color=POS, anchor="start"))
    # нагрівачі
    for yy in (230, 256, 282, 308):
        f.append(line(104, yy, 132, yy, color=POS, sw=5))
        f.append(line(368, yy, 396, yy, color=POS, sw=5))
    f.append(text(118, 360, "нагрівач", size=12, color=POS))
    # тримач + затравка
    f.append(line(250, 50, 250, 70, color=GREY, sw=3))
    f.append(circle(250, 44, 8, fill="#dddddd", stroke=INK, sw=2))
    f.append(rect(243, 70, 14, 48, fill="#cdd9ec", stroke=INK, sw=1.5))
    f.append(text(272, 88, "затравка (seed):", size=12, color=NEG, anchor="start"))
    f.append(text(272, 104, "потрібна орієнтація", size=11.5, color=NEG, anchor="start"))
    # шийка + тіло злитка (полігон з вузькою шийкою)
    f.append('<polygon points="246,118 254,118 254,150 296,170 296,272 204,272 204,170 246,150" '
             'fill="%s" stroke="%s" stroke-width="2"/>' % (WAFER, INK))
    f.append(text(300, 150, "шийка:", size=11.5, color=MUTED, anchor="start"))
    f.append(text(300, 165, "виганяє дефекти", size=11.5, color=MUTED, anchor="start"))
    f.append(text(404, 200, "монокристал", size=13, color=INK, anchor="start", bold=True))
    f.append(text(404, 218, "(boule, злиток)", size=12, color=INK, anchor="start"))
    f.append(text(404, 236, "діаметр 200–300 мм", size=11.5, color=MUTED, anchor="start"))
    # рухи
    f.append(line(180, 74, 180, 40, color=NEG, sw=2.2))
    f.append('<line x1="180" y1="40" x2="180" y2="36" stroke="%s" stroke-width="2.2" marker-end="url(#arrow)"/>' % LINE)
    f.append(text(172, 58, "тягнуть", size=11.5, color=NEG, anchor="end"))
    f.append(text(172, 74, "вгору", size=11.5, color=NEG, anchor="end"))
    f.append('<path d="M 322,42 a 16,16 0 1 1 -3,-11" fill="none" stroke="%s" stroke-width="2"/>' % FIELD)
    f.append('<line x1="319" y1="31" x2="324" y2="35" stroke="%s" stroke-width="2" marker-end="url(#arrow)"/>' % LINE)
    f.append(text(344, 42, "обертають", size=11.5, color=FIELD, anchor="start"))
    f.append(text(W / 2, H - 14,
                  "Затравку торкають до розплаву й повільно тягнуть угору, обертаючи: розплав застигає на ній, "
                  "копіюючи її ґратку.", size=11.5, color=MUTED, italic=True))
    return render(os.path.join(IMG, "czochralski.svg"), W, H, *f)


# ── Тема 4. Від злитка до пластини ───────────────────────────────────────────
def fig_wafer():
    W, H = 720, 320
    f = [text(W / 2, 26, "Від злитка до пластини", size=16, bold=True)]
    # злиток (циліндр) ліворуч
    cx, cy = 130, 165
    f.append('<ellipse cx="%d" cy="%d" rx="36" ry="14" fill="%s" stroke="%s" stroke-width="2"/>'
             % (cx, cy - 70, WAFER, INK))
    f.append(rect(cx - 36, cy - 70, 72, 140, fill=WAFER, stroke=INK, sw=2, rx=0))
    f.append('<ellipse cx="%d" cy="%d" rx="36" ry="14" fill="%s" stroke="%s" stroke-width="2"/>'
             % (cx, cy + 70, WAFER, INK))
    # лінії розрізу
    for k in range(-2, 3):
        yy = cy + k * 22
        f.append(line(cx - 36, yy, cx + 36, yy, color=BG, sw=1.2, dash="3,3"))
    f.append(text(cx, cy + 100, "злиток (boule)", size=12.5, bold=True))
    f.append(text(cx, cy + 118, "ріжуть дротом", size=11.5, color=MUTED))
    f.append(arrow(cx + 50, cy, cx + 110, cy, color=INK, sw=2))
    f.append(text(cx + 80, cy - 10, "зріз ~0.7 мм", size=11, color=MUTED))
    # шорсткий зріз → полірований
    midx = 350
    f.append(circle(midx, cy, 50, fill="#c8c8c8", stroke=INK, sw=2))
    f.append(text(midx, cy + 78, "зріз: шорсткий", size=12, color=MUTED))
    f.append(text(midx, cy + 95, "шліфують + полірують", size=11.5, color=MUTED))
    f.append(arrow(midx + 60, cy, midx + 120, cy, color=INK, sw=2))
    # готова пластина з notch і flat
    wx = 560
    f.append(circle(wx, cy, 60, fill=WAFER, stroke=INK, sw=2))
    f.append('<circle cx="%d" cy="%d" r="60" fill="none" stroke="#ffffff" stroke-width="6" opacity="0.35"/>' % (wx, cy))
    # flat (зрізаний край знизу)
    f.append(line(wx - 28, cy + 53, wx + 28, cy + 53, color=INK, sw=3))
    f.append(text(wx, cy + 88, "пластина (wafer):", size=12.5, bold=True))
    f.append(text(wx, cy + 105, "дзеркальна, орієнтована", size=11.5, color=MUTED))
    f.append(text(wx + 70, cy + 50, "flat / notch:", size=11, color=NEG, anchor="start"))
    f.append(text(wx + 70, cy + 64, "мітка орієнтації", size=11, color=NEG, anchor="start"))
    f.append(text(W / 2, H - 12,
                  "Злиток ріжуть на тонкі зрізи, шліфують і полірують до атомарно-гладеньких; "
                  "flat/notch на краю задає орієнтацію ґратки.", size=11.5, color=MUTED, italic=True))
    return render(os.path.join(IMG, "wafer.svg"), W, H, *f)


# ════════════════ ДЕТАЛЬНА ВЕРСІЯ (silicon-monocrystal-d.md) ════════════════

# ── D1. Три зони росту: шийка, конус, тіло (керування витягуванням) ───────────
def fig_growth_stages():
    W, H = 760, 360
    f = [text(W / 2, 26, "Три стадії росту злитка й чим керують", size=16, bold=True)]
    # силует злитка: затравка → тонка шийка → конус → циліндр → хвіст
    poly = ("248,60 264,60 264,96 "        # затравка
            "258,108 258,140 "             # шийка (вузька)
            "300,180 300,300 "             # конус → тіло (права)
            "212,300 212,180 "             # тіло (ліва)
            "254,140 254,108")            # шийка ліва
    f.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="2"/>' % (poly, WAFER, INK))
    f.append(rect(243, 50, 26, 12, fill="#cdd9ec", stroke=INK, sw=1.5))
    # підписи стадій праворуч зі стрілками
    stages = [
        (118, "затравка + ШИЙКА", "тягнуть ШВИДКО → вузько;\nдефекти «висипаються»", NEG),
        (200, "КОНУС (розширення)", "швидкість ↓ повільно →\nдіаметр росте плавно", GOLD),
        (270, "ТІЛО (циліндр)", "стала швидкість і темп. →\nрівний діаметр", FIELD),
    ]
    for yy, head, body, col in stages:
        f.append(line(304, yy, 470, yy, color=col, sw=1.4, dash="3,3"))
        f.append(text(478, yy - 6, head, size=12.5, color=col, anchor="start", bold=True))
        f.append(mtext(478 + 2, yy + 12, body, size=11, color=MUTED, anchor="start"))
    f.append(text(W / 2, H - 12,
                  "Швидкість витягування й температуру тримають у вузьких межах: швидше — дефекти й вузько, "
                  "повільніше — роздування.", size=11.5, color=MUTED, italic=True))
    return render(os.path.join(IMG, "growth-stages.svg"), W, H, *f)


# ── D2. CZ проти FZ (зонна плавка) ───────────────────────────────────────────
def fig_cz_vs_fz():
    W, H = 760, 380
    f = [text(W / 2, 26, "Два способи: Чохральський (CZ) і зонна плавка (FZ)", size=16, bold=True)]
    # ── CZ ліворуч ──
    f.append(text(195, 58, "Чохральський (CZ)", size=13.5, color=INK, bold=True))
    f.append('<path d="M 150,150 L 150,240 Q 150,270 178,270 L 282,270 '
             'Q 310,270 310,240 L 310,150" fill="#efe7d2" stroke="%s" stroke-width="2"/>' % INK)
    f.append('<path d="M 156,210 L 156,236 Q 156,262 180,262 L 280,262 '
             'Q 304,262 304,236 L 304,210 Z" fill="#f0a830" stroke="#c07a10" stroke-width="1.3"/>')
    f.append('<polygon points="222,90 238,90 270,130 270,210 190,210 190,130" fill="%s" stroke="%s" stroke-width="1.8"/>'
             % (WAFER, INK))
    f.append(text(195, 300, "розплав у тиглі (кварц)", size=11.5, color=MUTED))
    f.append(text(195, 320, "+ кисень із стінок тигля", size=11.5, color=POS))
    f.append(text(195, 340, "дешевше · до 300 мм · підкладки", size=11, color=FIELD, italic=True))
    # ── FZ праворуч ──
    f.append(text(575, 58, "Зонна плавка (FZ)", size=13.5, color=INK, bold=True))
    f.append(rect(560, 90, 30, 200, fill=WAFER, stroke=INK, sw=1.8, rx=4))
    # рухома розплавлена зона
    f.append(rect(560, 175, 30, 30, fill="#f0a830", stroke="#c07a10", sw=1.3, rx=0))
    # індуктор-кільце
    f.append('<ellipse cx="575" cy="190" rx="30" ry="11" fill="none" stroke="%s" stroke-width="3.5"/>' % POS)
    f.append(text(620, 192, "індуктор", size=11, color=POS, anchor="start"))
    f.append('<line x1="640" y1="205" x2="640" y2="160" stroke="%s" stroke-width="1.8" marker-end="url(#arrow)"/>' % NEG)
    f.append(text(648, 186, "зона", size=11, color=NEG, anchor="start"))
    f.append(text(648, 200, "повзе", size=11, color=NEG, anchor="start"))
    f.append(text(575, 312, "БЕЗ тигля: розплав ні з чим", size=11.5, color=MUTED))
    f.append(text(575, 330, "не контактує", size=11.5, color=MUTED))
    f.append(text(575, 350, "найчистіше · дорого · силова техніка", size=11, color=FIELD, italic=True))
    f.append(text(W / 2, H - 6,
                  "У CZ розплав торкається кварцового тигля й бере з нього кисень; у FZ розплавлена зона висить "
                  "без тигля — звідси гранична чистота.", size=11, color=MUTED, italic=True))
    return render(os.path.join(IMG, "cz-vs-fz.svg"), W, H, *f)


# ── D3. Дефекти кристала: точкові, дислокація, кисневі преципітати ────────────
def fig_defects():
    W, H = 792, 346
    f = [text(W / 2, 26, "Чим псується «ідеальний» кристал", size=16, bold=True)]
    panels = [
        (140, "вакансія / міжвузловина", "бракує атома або зайвий\nвтиснувся між вузли", NEG),
        (385, "дислокація", "ціла площина ґратки\nзсунута — лінія обриву", POS),
        (630, "кисневі преципітати", "кисень із тигля збивається\nв грудочки (CZ)", GOLD),
    ]
    gy = 70
    for cx, head, body, col in panels:
        # ґратка 4×4
        for i in range(4):
            for j in range(4):
                f.append(circle(cx - 45 + j * 30, gy + i * 26, 4.5, fill=FILL, stroke=MUTED, sw=1))
        f.append(text(cx, gy + 130, head, size=12.5, color=col, bold=True))
        f.append(mtext(cx, gy + 150, body, size=11, color=MUTED))
    # відмітки дефектів поверх ґраток
    # вакансія: прибрати один вузол (червоне коло-пропуск) + міжвузловина
    f.append(circle(140 - 45 + 1 * 30, 70 + 1 * 26, 6, fill=BG, stroke=NEG, sw=2))
    f.append(circle(140 - 45 + 2 * 30 + 14, 70 + 2 * 26 + 12, 4.5, fill="#eaf0fd", stroke=NEG, sw=2))
    # дислокація: вертикальна напівплощина
    f.append(line(385 - 45 + 1 * 30 + 14, 70 - 6, 385 - 45 + 1 * 30 + 14, 70 + 2 * 26 + 6, color=POS, sw=2.4))
    # преципітат: грудочка
    f.append(circle(630 - 45 + 2 * 30, 70 + 1 * 26 + 12, 9, fill="#fdf0d8", stroke=GOLD, sw=2))
    f.append(text(W / 2, H - 12,
                  "Будь-який обрив порядку розсіює носії й тече струмом не туди; кисневі грудочки в CZ-кремнії "
                  "буває й корисні — ловлять домішки далі від приладів.", size=11, color=MUTED, italic=True))
    return render(os.path.join(IMG, "defects.svg"), W, H, *f)


# ── D4. Сегрегація: чому домішка тікає в розплав (легування) ──────────────────
def fig_segregation():
    W, H = 794, 334
    f = [text(W / 2, 26, "Сегрегація: домішка не любить кристал", size=16, bold=True)]
    # кристал зліва, розплав справа, фронт посередині
    f.append(rect(60, 90, 280, 150, fill=WAFER, stroke=INK, sw=2, rx=0))
    f.append(rect(340, 90, 320, 150, fill="#f0a830", stroke="#c07a10", sw=2, rx=0))
    f.append(line(340, 84, 340, 246, color=POS, sw=2.5))
    f.append(text(200, 115, "твердий кристал", size=12.5, bold=True))
    f.append(text(500, 115, "розплав", size=12.5, bold=True))
    f.append(text(340, 262, "фронт кристалізації", size=11, color=POS))
    # домішкові атоми: рідко в кристалі, густо в розплаві
    import random
    random.seed(7)
    for _ in range(6):
        x = 70 + random.random() * 255; y = 130 + random.random() * 95
        f.append(circle(x, y, 4, fill="#fdecea", stroke=POS, sw=1.5))
    for _ in range(26):
        x = 350 + random.random() * 300; y = 130 + random.random() * 95
        f.append(circle(x, y, 4, fill="#fdecea", stroke=POS, sw=1.5))
    f.append('<line x1="355" y1="165" x2="325" y2="165" stroke="%s" stroke-width="1.8" marker-end="url(#arrow)"/>' % POS)
    f.append(text(W / 2, H - 14,
                  "На фронті більшість домішки відтісняється назад у розплав (k<1): тому розплав поступово "
                  "багатшає, а кінець злитка виходить більш легованим, ніж початок.", size=11, color=MUTED, italic=True))
    return render(os.path.join(IMG, "segregation.svg"), W, H, *f)


if __name__ == "__main__":
    fig_chain()
    fig_purity()
    fig_czochralski()
    fig_wafer()
    # детальна версія
    fig_growth_stages()
    fig_cz_vs_fz()
    fig_defects()
    fig_segregation()
    print("OK: 8 SVG -> ./img/")

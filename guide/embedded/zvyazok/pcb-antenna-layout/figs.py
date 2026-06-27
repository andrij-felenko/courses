# -*- coding: utf-8 -*-
"""Фігури до кроку курсу «Топологія антени на PCB».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

COPPER = "#b9770e"   # мідь / земля — тепле
HOT    = "#c0392b"   # гаряча точка живлення


# ── 1. Геометрія keep-out: де чисто, а де земля ──────────────────────────────
def fig_keepout():
    W, H = 940, 470
    f = [text(W / 2, 30, "Зона відступу: під антеною — порожньо, земля — позаду", size=18, bold=True),
         text(W / 2, 52, "мідь будь-якого шару під випромінювачем розладновує антену; під живленням потрібне суцільне дзеркало землі",
              size=11.3, color=MUTED, italic=True)]

    # контур плати
    bx, by, bw, bh = 70, 86, 800, 330
    f.append(rect(bx, by, bw, bh, fill="#fcfcfb", stroke=INK, sw=2, rx=10))
    f.append(text(bx + bw - 12, by + bh - 12, "плата", size=11, color=MUTED, anchor="end"))

    # суцільний полігон землі — права частина
    gx = bx + 300
    f.append(rect(gx, by + 14, bw - (gx - bx) - 14, bh - 28, fill="#f6ecd6", stroke=COPPER, sw=1.6, rx=6))
    f.append(text(gx + (bw - (gx - bx) - 14) / 2, by + 70, "суцільний полігон землі", size=13, color=COPPER, bold=True))
    f.append(text(gx + (bw - (gx - bx) - 14) / 2, by + 92, "(на всіх шарах) + густі перехідні отвори", size=10.5, color=MUTED))
    # точки перехідних отворів (via stitching)
    for i in range(7):
        for j in range(4):
            f.append(circle(gx + 40 + i * 66, by + 130 + j * 40, 3.2, fill=COPPER, stroke=COPPER, sw=0))

    # зона keep-out — ліва частина, без міді
    kx = bx + 14
    kw = (gx) - kx
    f.append(rect(kx, by + 14, kw, bh - 28, fill="#ffffff", stroke=FIELD, sw=2, rx=6))
    f.append(line(kx, by + 14, kx + kw, by + bh - 14, color=FIELD, sw=1, dash="4,5"))
    f.append(line(kx, by + bh - 14, kx + kw, by + 14, color=FIELD, sw=1, dash="4,5"))
    f.append(text(kx + kw / 2, by + 44, "ЗОНА ВІДСТУПУ (keep-out)", size=12.5, color=FIELD, bold=True))
    f.append(text(kx + kw / 2, by + 64, "жодної міді на жодному шарі", size=10.5, color=INK))

    # антена-меандр у зоні відступу, край плати
    mx, my = kx + 26, by + 150
    f.append('<path d="M %d,%d v -40 h 20 v 40 h 20 v -40 h 20 v 40 h 20 v -40 h 20 v 40 h 20 v -40 h 20" '
             'fill="none" stroke="%s" stroke-width="3"/>' % (mx, my, COPPER))
    f.append(text(mx + 70, my + 26, "антена-меандр", size=10.5, color=COPPER, bold=True))

    # точка живлення (feed) на межі зони й землі
    fx = gx
    fy = by + 150
    f.append(circle(fx, fy, 7, fill="#fdecea", stroke=HOT, sw=2.4))
    f.append(text(fx, fy - 16, "точка", size=9.5, color=HOT, bold=True))
    f.append(text(fx, fy + 28, "живлення", size=9.5, color=HOT, bold=True))
    # стрілка: земля підходить ДО точки живлення, але не далі
    f.append(arrow(gx + 120, fy + 70, fx + 12, fy + 16, color=COPPER, sw=1.8))
    f.append(text(gx + 130, fy + 84, "земля доходить лише до живлення", size=10, color=COPPER, anchor="start"))

    # розмір 15 мм
    f.append(line(kx, by + bh + 0, kx, by + bh + 18, color=MUTED, sw=1))
    f.append(line(gx, by + bh + 0, gx, by + bh + 18, color=MUTED, sw=1))
    f.append(line(kx, by + bh + 9, gx, by + bh + 9, color=MUTED, sw=1.2))
    f.append(text((kx + gx) / 2, by + bh + 34, "≥ 15 мм чисто", size=11, color=MUTED, bold=True))

    return render(os.path.join(IMG, 'keepout.svg'), W, H, *f)


# ── 2. Земля = протиполюс (counterpoise): дзеркало під живленням ──────────────
def fig_counterpoise():
    W, H = 900, 470
    f = [text(W / 2, 30, "Земля — другий полюс антени, не перешкода", size=18, bold=True),
         text(W / 2, 52, "λ/4-штир випромінює лише над дзеркалом землі; дзеркало добудовує другу чверть хвилі",
              size=11.3, color=MUTED, italic=True)]

    baseY = 280
    feedX = 450

    # площина землі
    f.append(rect(150, baseY, 600, 24, fill="#f6ecd6", stroke=COPPER, sw=2, rx=4))
    f.append(text(450, baseY + 16, "площина землі (протиполюс)", size=11.5, color=COPPER, bold=True))
    # штрихування «маси» вниз
    for x in range(160, 745, 24):
        f.append(line(x, baseY + 24, x - 10, baseY + 36, color=COPPER, sw=1))

    # штир λ/4 угору
    topY = baseY - 150
    f.append(line(feedX, baseY, feedX, topY, color=INK, sw=3.2))
    f.append(circle(feedX, topY, 4, fill=INK, stroke=INK, sw=0))
    f.append(text(feedX + 14, (baseY + topY) / 2, "λ/4 ≈ 30 мм", size=11.5, color=INK, anchor="start", bold=True))

    # дзеркальне продовження вниз (пунктир) — віддзеркалення
    mirY = baseY + 130
    f.append(line(feedX, baseY + 24, feedX, mirY, color=MUTED, sw=2, dash="6,6"))
    f.append(circle(feedX, mirY, 4, fill="none", stroke=MUTED, sw=1.6))
    f.append(text(feedX + 14, (baseY + 24 + mirY) / 2, "віддзеркалення (уявне)", size=10.5, color=MUTED, anchor="start", italic=True))

    # точка живлення
    f.append(circle(feedX, baseY, 7, fill="#fdecea", stroke=HOT, sw=2.4))
    f.append(text(feedX, topY - 14, "вільний кінець:", size=10, color=MUTED, bold=True))
    f.append(text(feedX, topY - 0, "струм = 0", size=10, color=MUTED))
    f.append(arrow(feedX - 70, baseY - 30, feedX - 12, baseY - 4, color=HOT, sw=1.8))
    f.append(text(feedX - 78, baseY - 36, "живлення: струм максимум", size=10, color=HOT, anchor="end"))

    # діаграма випромінювання — пелюстка над землею
    for r in (40, 70, 100):
        f.append('<path d="M %d,%d A %d,%d 0 0 1 %d,%d" fill="none" stroke="%s" stroke-width="1.6"/>'
                 % (feedX + 18, topY + 10, r, r, feedX + 18, topY + 10 + 2 * r, FIELD))

    return render(os.path.join(IMG, 'counterpoise.svg'), W, H, *f)


# ── 3. 50-омна живильна лінія: мікросмужка проти GCPW ─────────────────────────
def fig_feedline():
    W, H = 940, 410
    f = [text(W / 2, 30, "50-омна живильна лінія до антени чи роз'єму", size=18, bold=True),
         text(W / 2, 52, "переріз плати: ширина доріжки + відстань до землі задають 50 Ом; стик не на 50 Ом — відбиття",
              size=11.3, color=MUTED, italic=True)]

    def stack(x0, title):
        # верхній шар (сигнал) і нижній шар (земля) у перерізі
        topY, botY = 150, 250
        f.append(text(x0 + 200, 96, title, size=13.5, color=INK, bold=True))
        # діелектрик
        f.append(rect(x0 + 30, topY, 340, botY - topY, fill="#eef2f7", stroke=MUTED, sw=1.2, rx=2))
        f.append(text(x0 + 200, (topY + botY) / 2 + 4, "діелектрик (FR-4)", size=10, color=MUTED))
        # нижня суцільна земля
        f.append(rect(x0 + 30, botY, 340, 16, fill="#f6ecd6", stroke=COPPER, sw=1.4, rx=2))
        f.append(text(x0 + 200, botY + 12, "опорна земля (суцільна)", size=9.5, color=COPPER, bold=True))
        return topY

    # ── ліворуч: мікросмужка ──
    topY = stack(30, "Мікросмужка (microstrip)")
    f.append(rect(170, topY - 12, 60, 12, fill=HOT, stroke=HOT, sw=0, rx=2))
    f.append(text(200, topY - 20, "доріжка W", size=10, color=HOT, bold=True))
    f.append(arrow(200, topY + 6, 200, 250 - 4, color=NEG, sw=1.4))
    f.append(text(214, topY + 40, "висота h", size=9.5, color=NEG, anchor="start"))
    f.append(text(230, 300, "поле тягнеться до нижньої землі", size=10, color=MUTED))

    # ── праворуч: заземлена копланарна (GCPW) ──
    x1 = 470
    topY = stack(x1, "Заземлена копланарна (GCPW)")
    cx = x1 + 200
    f.append(rect(cx - 30, topY - 12, 60, 12, fill=HOT, stroke=HOT, sw=0, rx=2))
    f.append(text(cx, topY - 20, "доріжка", size=10, color=HOT, bold=True))
    # бічні землі на тому ж шарі
    f.append(rect(x1 + 40, topY - 12, 100, 12, fill=COPPER, stroke=COPPER, sw=0, rx=2))
    f.append(rect(cx + 60, topY - 12, 100, 12, fill=COPPER, stroke=COPPER, sw=0, rx=2))
    f.append(text(x1 + 90, topY - 20, "земля", size=9, color=COPPER, bold=True))
    f.append(text(cx + 110, topY - 20, "земля", size=9, color=COPPER, bold=True))
    f.append(text(cx - 56, topY - 4, "зазор", size=8.5, color=MUTED, anchor="end"))
    # перехідні отвори з боків (stitching) — вертикальні
    for vx in (x1 + 70, x1 + 120, cx + 80, cx + 130):
        f.append(line(vx, topY, vx, 266, color=COPPER, sw=2.2))
    f.append(text(cx, 300, "бічна земля + отвори тримають поле", size=10, color=MUTED))

    # підпис-висновок унизу
    f.append(text(W / 2, 372, "правило: отвори-зшивки вздовж лінії приблизно кожні λ/20, щоб земля лишалась єдиною",
                  size=10.5, color=INK, italic=True))

    return render(os.path.join(IMG, 'feedline.svg'), W, H, *f)


# ── 4. Звідки 50 Ом: дві криві, що тягнуть у різні боки (вставка hist) ────────
def fig_50ohm_tradeoff():
    """Якісні криві потужності й згасання від хвильового опору повітряного
    коаксіалу: потужність — пік ~30 Ом, згасання — мінімум ~77 Ом; 50 Ом —
    компроміс між ними. Числа якісні (форма кривих), позначки точні."""
    W, H = 900, 470
    f = [text(W / 2, 30, "Звідки 50 Ом: два оптимуми тягнуть у різні боки", size=18, bold=True),
         text(W / 2, 52, "повітряний коаксіал: найбільша потужність ~30 Ом, найменше згасання ~77 Ом — 50 Ом між ними",
              size=11.3, color=MUTED, italic=True)]

    # осі
    ox, oy = 120, 380          # початок осей (низ-ліво)
    ax_w, ax_h = 660, 250      # довжина осей
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.8))          # X
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.8))          # Y
    f.append(text(ox + ax_w / 2, oy + 40, "хвильовий опір лінії, Ом", size=12, color=INK))

    # шкала X: 20…90 Ом
    z0, z1 = 20.0, 90.0
    def X(z):
        return ox + (z - z0) / (z1 - z0) * ax_w
    for z in (20, 30, 40, 50, 60, 70, 80, 90):
        x = X(z)
        f.append(line(x, oy, x, oy + 5, color=INK, sw=1.2))
        f.append(text(x, oy + 20, str(z), size=10, color=MUTED))

    # крива ПОТУЖНОСТІ: пік біля 30 Ом, спадає в обидва боки (червона)
    import math
    pts_p = []
    for i in range(0, 141):
        z = z0 + (z1 - z0) * i / 140.0
        # дзвін із піком на 30 Ом
        v = math.exp(-((z - 30.0) / 26.0) ** 2)
        y = oy - 20 - v * (ax_h - 50)
        pts_p.append("%.1f,%.1f" % (X(z), y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
             % (" ".join(pts_p), POS))
    f.append(text(X(30), oy - 20 - (ax_h - 50) - 12, "потужність", size=11.5, color=POS, bold=True))

    # крива ЗГАСАННЯ-НАВПАКИ (що вище — то менше втрат): пік біля 77 Ом (зелена)
    pts_a = []
    for i in range(0, 141):
        z = z0 + (z1 - z0) * i / 140.0
        v = math.exp(-((z - 77.0) / 30.0) ** 2)
        y = oy - 20 - v * (ax_h - 50)
        pts_a.append("%.1f,%.1f" % (X(z), y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
             % (" ".join(pts_a), FIELD))
    f.append(text(X(77), oy - 20 - (ax_h - 50) - 12, "мала втрата", size=11.5, color=FIELD, bold=True))

    # вертикальні маркери 30 / 77 / 50
    def vmark(z, label, color, dash="4,5"):
        x = X(z)
        f.append(line(x, oy, x, oy - ax_h + 8, color=color, sw=1.4, dash=dash))
        f.append(text(x, oy - ax_h - 2, label, size=10.5, color=color, bold=True))

    vmark(30, "30 Ом", POS)
    vmark(77, "77 Ом", FIELD)

    # смуга компромісу 48…53.5 і лінія 50
    xa, xb = X(48), X(53.5)
    f.append(rect(xa, oy - ax_h + 14, xb - xa, ax_h - 22, fill="#fff6d6", stroke="none", sw=0, rx=3))
    x50 = X(50)
    f.append(line(x50, oy, x50, oy - ax_h + 8, color=COPPER, sw=2.6))
    f.append(circle(x50, oy - ax_h + 30, 6, fill="#fdf3d0", stroke=COPPER, sw=2.4))
    f.append(text(x50, oy - ax_h - 2, "50 Ом", size=12, color=COPPER, bold=True))
    f.append(text(x50, oy - ax_h + 50, "компроміс", size=10, color=COPPER, bold=True))

    # підписи середніх
    f.append(text(x50, oy - 14, "сер. геом. ≈48 · сер. ариф. ≈53.5", size=9.5, color=MUTED))

    # підпис осі Y (ротований): що вище — то ближче кожна крива до свого оптимуму
    f.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="10" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 %.1f %.1f)">ближче до оптимуму →</text>'
             % (ox - 22, oy - ax_h / 2, FONT, MUTED, ox - 22, oy - ax_h / 2))

    return render(os.path.join(IMG, '50ohm-tradeoff.svg'), W, H, *f)


# ── 5. Пастка шарів: галочки зони ловлять зовні; правило без шару — всюди ─────
def fig_layer_trap():
    """Чому правило БЕЗ (layer ...) надійніше за галочки зони-обмеження:
    зона-обмеження діє на шарах, де намальована (часто лише зовнішні);
    custom-rule без указаного шару накриває ВСІ мідні шари, зокрема внутрішні,
    де й ховається забута земля. Стек 4-шарової плати, переріз."""
    W, H = 940, 470
    f = [text(W / 2, 30, "Пастка шарів: галочки зони ловлять не все", size=18, bold=True),
         text(W / 2, 52, "зона-обмеження діє лише на своїх шарах; правило без (layer …) — на ВСІХ, де й ховається внутрішня земля",
              size=11.0, color=MUTED, italic=True)]

    layers = ["F.Cu  (верх)", "In1.Cu  (внутр.)", "In2.Cu  (внутр.)", "B.Cu  (низ)"]
    y0, lh, lw = 96, 78, 300
    # дві колонки: ліворуч — лише галочки зони; праворуч — правило без шару
    colx = {"L": 70, "R": 540}
    head = {"L": "Лише галочки зони-обмеження", "R": "Правило disallow без (layer …)"}
    # на яких шарах ловиться мідь
    caught = {"L": [True, False, False, True], "R": [True, True, True, True]}

    for side in ("L", "R"):
        x = colx[side]
        f.append(text(x + lw / 2, y0 - 16, head[side], size=12.5, color=INK, bold=True))
        for i, name in enumerate(layers):
            y = y0 + i * lh
            ok = caught[side][i]
            fill = "#eaf6ec" if ok else "#fdecea"
            edge = FIELD if ok else POS
            f.append(rect(x, y, lw, lh - 16, fill="#f6ecd6", stroke=COPPER, sw=1.4, rx=4))
            f.append(text(x + 12, y + 25, name, size=11.5, color=INK, anchor="start", bold=True))
            # мітка «під антеною»: маленький меандр-шматок міді на цьому шарі
            f.append(rect(x + lw - 86, y + 12, 70, lh - 40, fill="#f0d8a8", stroke=COPPER, sw=1, rx=2))
            f.append(text(x + lw - 51, y + 12 + (lh - 40) / 2 + 4, "мідь", size=9, color=COPPER))
            # бейдж — зловлено / пропущено
            bx = x + lw - 86 - 64
            f.append(rect(bx, y + 14, 56, lh - 44, fill=fill, stroke=edge, sw=1.6, rx=9))
            f.append(text(bx + 28, y + 14 + (lh - 44) / 2 + 4,
                          "ловить" if ok else "ПРОПУСК", size=8.6, color=edge, bold=True))

    # стрілка-акцент на внутрішні шари лівої колонки
    xL = colx["L"]
    f.append(arrow(xL - 14, y0 + lh + (lh - 16) / 2, xL - 14, y0 + 2 * lh + (lh - 16) / 2,
                   color=POS, sw=2.0))
    f.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="10.5" fill="%s" '
             'text-anchor="middle" font-weight="700" '
             'transform="rotate(-90 %.1f %.1f)">тут і ховається земля</text>'
             % (xL - 30, y0 + 1.5 * lh, FONT, POS, xL - 30, y0 + 1.5 * lh))

    f.append(text(W / 2, y0 + 4 * lh + 6,
                  "висновок: не вказуй (layer …) — відсутність шару робить заборону наскрізною по всіх мідних шарах",
                  size=10.5, color=INK, italic=True))
    return render(os.path.join(IMG, 'layer-trap.svg'), W, H, *f)


# ── 6. Конвеєр: іменована зона → правила (перше збіжне) → kicad-cli → брама ───
def fig_drc_pipeline():
    """Шлях від геометрії до коду виходу: зона ANT_KEEPOUT + клас RF_FEED →
    два правила (виняток ПЕРЕД забороною: перше збіжне виграє) → kicad-cli pcb
    drc дає JSON+код виходу → брама на C валить чи пускає збірку."""
    W, H = 960, 430
    f = [text(W / 2, 30, "Keep-out як перевірка: від зони до коду виходу", size=18, bold=True),
         text(W / 2, 52, "перше збіжне правило виграє, тож виняток для живлення стоїть ПЕРЕД загальною забороною",
              size=11.0, color=MUTED, italic=True)]

    # колонка 1 — геометрія
    b1 = fitbox(40, 90, 200, 96,
                "ЗОНА ANT_KEEPOUT\n(іменована геометрія)\n+ клас кіл RF_FEED\nна живильній лінії",
                size=11, fill="#f6ecd6", stroke=COPPER, sw=1.6, color=INK)
    f.append(b1)
    f.append(arrow(240, 138, 286, 138, color=INK, sw=1.8))

    # колонка 2 — два правила, перше збіжне
    f.append(text(390, 80, "Правила (згори вниз)", size=12, color=INK, bold=True))
    r1 = fitbox(290, 92, 200, 56,
                "1) ДОЗВІЛ: RF_FEED\nу зоні — пропустити",
                size=10.3, fill="#eaf6ec", stroke=FIELD, sw=1.6, color=INK, bold=True)
    r2 = fitbox(290, 156, 200, 56,
                "2) ЗАБОРОНА: будь-яка\nмідь у зоні (всі шари)",
                size=10.3, fill="#fdecea", stroke=POS, sw=1.6, color=INK, bold=True)
    f.append(r1)
    f.append(r2)
    f.append(text(390, 232, "перше збіжне виграє", size=9.5, color=MUTED, italic=True))
    f.append(arrow(490, 138, 536, 138, color=INK, sw=1.8))

    # колонка 3 — kicad-cli
    b3 = fitbox(540, 92, 200, 96,
                "kicad-cli pcb drc\n--format json\n--exit-code-violations\n→ drc.json + код",
                size=10.2, fill=FILL, stroke=INK, sw=1.6, color=INK)
    f.append(b3)
    f.append(arrow(740, 138, 786, 138, color=INK, sw=1.8))

    # колонка 4 — брама на C з двома виходами
    b4 = fitbox(790, 92, 150, 96,
                "брама на C\nрозбирає звіт\nпо полях",
                size=10.5, fill=FILL, stroke=INK, sw=1.6, color=INK)
    f.append(b4)

    # дві гілки результату
    yC = 250
    f.append(arrow(865, 188, 865, yC, color=INK, sw=1.6))
    pass_box = fitbox(560, yC, 180, 50, "код 0 → ЗБІРКА ЙДЕ",
                      size=11, fill="#eaf6ec", stroke=FIELD, sw=1.8, color=FIELD, bold=True)
    fail_box = fitbox(770, yC, 180, 50, "код ≠0 → ЗБІРКУ СПИНЕНО",
                      size=11, fill="#fdecea", stroke=POS, sw=1.8, color=POS, bold=True)
    f.append(line(865, yC, 650, yC - 6, color=FIELD, sw=1.6))
    f.append(line(865, yC, 860, yC - 6, color=POS, sw=1.6))
    f.append(pass_box)
    f.append(fail_box)
    f.append(text(650, yC + 70, "міді в зоні немає", size=9.5, color=FIELD))
    f.append(text(860, yC + 70, "мідь у зоні (часто внутр. земля)", size=9.5, color=POS))

    f.append(text(W / 2, 390,
                  "перевірка топології стає частиною збірки — невідворотною, як компіляція",
                  size=10.5, color=INK, italic=True))
    return render(os.path.join(IMG, 'drc-pipeline.svg'), W, H, *f)


if __name__ == '__main__':
    fig_keepout()
    fig_counterpoise()
    fig_feedline()
    fig_50ohm_tradeoff()
    fig_layer_trap()
    fig_drc_pipeline()
    print('OK: keepout, counterpoise, feedline, 50ohm-tradeoff, layer-trap, drc-pipeline')

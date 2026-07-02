# -*- coding: utf-8 -*-
"""Фігури до теми «Антена ESP32».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GOLD = "#b9770e"   # роз'єм/кабель — тепле, але читабельне


# ── 1. Три типи антен на модулі — і коли який ────────────────────────────────
def fig_antenna_types():
    W, H = 940, 430
    f = [text(W / 2, 30, "Три типи антен на модулі — і коли який", size=18, bold=True),
         text(W / 2, 52, "усі випромінюють ту саму хвилю 2.4 ГГц; різняться розміром, дальністю й ціною",
              size=11.5, color=MUTED, italic=True)]

    def card(x, accent, title, sub, bullets):
        cx = x + 135
        out = [rect(x, 88, 270, 304, fill="#fcfcfc", stroke=accent, sw=2, rx=12),
               text(cx, 116, title, size=14, color=accent, bold=True),
               text(cx, 134, sub, size=9.5, color=MUTED, italic=True)]
        by = 250
        for b in bullets:
            out.append(text(x + 22, by, "•", size=13, color=accent, anchor="start", bold=True))
            out.append(text(x + 36, by, b, size=10.2, color=INK, anchor="start"))
            by += 34
        return out, cx

    # PCB-доріжка — меандр
    out, cx = card(36, FIELD, "PCB-доріжка", "(trace antenna)",
                   ["витравлена прямо на платі", "майже безкоштовна",
                    "добра дальність + відступ", "типова для WROOM"])
    mx, my = cx - 49, 192
    f += out
    f.append('<path d="M %d,%d v -26 h 14 v 26 h 14 v -26 h 14 v 26 h 14 v -26 h 14 v 26 h 14 v -26 h 14" '
             'fill="none" stroke="%s" stroke-width="2.6"/>' % (mx, my, FIELD))

    # Керамічна — кубик
    out, cx = card(342, NEG, "Керамічна", "(chip antenna)",
                   ["крихітний SMD-компонент", "компактна, коли тісно",
                    "трохи гірша й дорожча", "де нема місця на доріжку"])
    f += out
    f.append(rect(cx - 34, 172, 68, 40, fill="#dfe7f5", stroke=NEG, sw=2, rx=4))
    f.append(text(cx, 196, "кераміка", size=9, color=NEG, bold=True))

    # IPEX / U.FL — гніздо + кабель
    out, cx = card(648, GOLD, "IPEX / U.FL", "+ зовнішня антена",
                   ["роз'єм під зовнішню антену", "найбільша дальність",
                    "для металевих корпусів", "треба роз'єм і кабель"])
    f += out
    f.append(circle(cx - 20, 198, 12, fill="#fbf7e3", stroke=GOLD, sw=2))
    f.append(circle(cx - 20, 198, 4, fill=GOLD, stroke=GOLD, sw=0))
    f.append(line(cx + 6, 210, cx + 30, 170, color=INK, sw=2.4))
    f.append(text(cx + 2, 228, "роз'єм + кабель", size=9, color=MUTED))

    return render(os.path.join(IMG, 'antenna-types.svg'), W, H, *f)


# ── 2. Чому корпус і рука «садять» зв'язок ───────────────────────────────────
def fig_detune():
    W, H = 900, 440
    f = [text(W / 2, 30, "Чому корпус і рука «садять» зв'язок", size=18, bold=True),
         text(W / 2, 52, "антені потрібен вільний простір; метал, земля, вода й рука поглинають і розладнують її",
              size=11.5, color=MUTED, italic=True)]

    # ── ліворуч: вільна антена, повна діаграма ──
    f.append(rect(44, 86, 390, 312, fill="#fbfdfb", stroke=FIELD, sw=2, rx=12))
    f.append(text(239, 112, "Вільна антена", size=13, color=FIELD, bold=True))
    f.append(line(150, 300, 150, 236, color=INK, sw=2.4))
    f.append(circle(150, 236, 3, fill=INK, stroke=INK, sw=0))
    for r in (26, 48, 70, 92):
        f.append('<path d="M 168,%d A %d,%d 0 0 1 168,%d" fill="none" stroke="%s" stroke-width="1.8"/>'
                 % (236 - r, r, r, 236 + r, FIELD))
    f.append(text(239, 336, "сигнал іде вільно", size=11, color=INK))
    f.append(rect(120, 352, 240, 16, fill="#eef6ef", stroke=FIELD, sw=1.4, rx=0))
    f.append(text(239, 388, "повна дальність", size=9.5, color=FIELD, bold=True))

    # ── праворуч: поруч провідник — діаграма обвалюється ──
    f.append(rect(466, 86, 390, 312, fill="#fffafa", stroke=POS, sw=2, rx=12))
    f.append(text(661, 112, "Поруч рука / метал / земля", size=12, color=POS, bold=True))
    f.append(line(560, 300, 560, 236, color=INK, sw=2.4))
    f.append(circle(560, 236, 3, fill=INK, stroke=INK, sw=0))
    for r in (22, 38):
        f.append('<path d="M 578,%d A %d,%d 0 0 1 578,%d" fill="none" stroke="%s" stroke-width="1.8"/>'
                 % (236 - r, r, r, 236 + r, POS))
    f.append('<ellipse cx="642" cy="244" rx="56" ry="78" fill="#d9d9de" stroke="%s" stroke-width="1.6"/>' % MUTED)
    f.append(text(642, 240, "рука /", size=10, color=INK, bold=True))
    f.append(text(642, 256, "метал", size=10, color=INK, bold=True))
    f.append(text(661, 336, "поглинається, розладнується", size=10.5, color=INK))
    f.append(rect(541, 352, 240, 16, fill="none", stroke=POS, sw=1.4, rx=0))
    f.append(rect(541, 352, 78, 16, fill="#fbecec", stroke=POS, sw=0, rx=0))
    f.append(text(661, 388, "дальність падає", size=9.5, color=POS, bold=True))

    return render(os.path.join(IMG, 'detune.svg'), W, H, *f)


# ── 3. Шлях сигналу: чип → U.FL → пігтейл → SMA → антена ─────────────────────
def fig_ufl_chain():
    W, H = 940, 300
    f = [text(W / 2, 30, "Шлях сигналу до зовнішньої антени — усе на 50 Ом", size=18, bold=True),
         text(W / 2, 52, "кожен стик мусить тримати ті самі 50 Ом, інакше на ньому хвиля частково відбивається",
              size=11.5, color=MUTED, italic=True)]

    # межа корпусу (вертикальна пунктирна лінія)
    wall_x = 700
    f.append(line(wall_x, 96, wall_x, 252, color=MUTED, sw=2, dash="7,6"))
    f.append(text(wall_x, 270, "стінка корпусу", size=10, color=MUTED))

    midy = 168
    # чип
    f.append(rect(40, midy - 34, 120, 68, fill="#dfe7f5", stroke=NEG, sw=2, rx=6))
    f.append(text(100, midy - 6, "чип ESP32", size=12, color=NEG, bold=True))
    f.append(text(100, midy + 14, "вихід 50 Ом", size=9.5, color=MUTED))

    # доріжка
    f.append(line(160, midy, 224, midy, color=INK, sw=2.6))
    f.append(text(192, midy - 12, "доріжка", size=9, color=MUTED))

    # гніздо U.FL
    f.append(circle(248, midy, 16, fill="#fbf7e3", stroke=GOLD, sw=2.4))
    f.append(circle(248, midy, 5, fill=GOLD, stroke=GOLD, sw=0))
    f.append(text(248, midy + 40, "гніздо U.FL", size=10, color=GOLD, bold=True))
    f.append(text(248, midy + 56, "(на платі)", size=9, color=MUTED))

    # пігтейл (коаксіал) до стінки
    f.append(line(264, midy, wall_x, midy, color=INK, sw=3.2))
    f.append(line(264, midy, wall_x, midy, color="#eef0f3", sw=1.2))
    f.append(text(480, midy - 12, "коаксіальний пігтейл (50 Ом)", size=10, color=INK))

    # SMA у стінці
    f.append(rect(wall_x - 14, midy - 22, 28, 44, fill="#eef6ef", stroke=FIELD, sw=2.2, rx=4))
    f.append(text(wall_x, midy + 44, "SMA у стінці", size=10, color=FIELD, bold=True))
    f.append(text(wall_x, midy + 60, "(різьба)", size=9, color=MUTED))

    # зовнішня антена-штир
    f.append(line(wall_x + 14, midy, 812, midy, color=INK, sw=2.6))
    f.append(line(848, midy + 18, 848, midy - 54, color=INK, sw=3))
    f.append(circle(848, midy - 54, 4, fill=INK, stroke=INK, sw=0))
    for r in (18, 34, 50):
        f.append('<path d="M 866,%d A %d,%d 0 0 1 866,%d" fill="none" stroke="%s" stroke-width="1.6"/>'
                 % (midy - 54 - r, r, r, midy - 54 + r, FIELD))
    f.append(text(848, midy + 40, "зовнішня антена", size=10, color=INK, bold=True))

    return render(os.path.join(IMG, 'ufl-chain.svg'), W, H, *f)


# ── 4. Стійна хвиля на λ/4-штирі: вузол струму / пучність напруги ─────────────
def fig_standing_wave():
    W, H = 900, 470
    f = [text(W / 2, 30, "Стійна хвиля на чвертьхвильовому штирі", size=18, bold=True),
         text(W / 2, 52, "резонанс = на живленні пучність струму, на вільному кінці — нуль струму й максимум напруги",
              size=11.5, color=MUTED, italic=True)]

    # вертикальний штир: низ = живлення (біля землі), верх = вільний кінець
    ax = 210               # вісь штиря
    y_feed = 400           # живлення (біля землі)
    y_tip = 130            # вільний кінець
    L = y_feed - y_tip     # довжина штиря на екрані = λ/4

    # земля-дзеркало
    f.append(line(120, y_feed, 300, y_feed, color=INK, sw=3))
    for gx in range(126, 300, 16):
        f.append(line(gx, y_feed, gx - 10, y_feed + 12, color=MUTED, sw=1.4))
    f.append(text(210, y_feed + 30, "площина землі (дзеркало)", size=10.5, color=MUTED))

    # сам штир
    f.append(line(ax, y_feed, ax, y_tip, color=INK, sw=3.4))
    f.append(circle(ax, y_tip, 4, fill=INK, stroke=INK, sw=0))
    f.append(text(ax, y_tip - 14, "вільний кінець", size=10, color=INK))
    f.append(minus(ax - 40, y_feed + 2, r=9))
    f.append(text(ax - 40, y_feed + 34, "живлення", size=9.5, color=MUTED))

    # струм I(z): косинус — max біля землі, 0 на кінці. вправо від осі
    import math
    curI = []
    for i in range(0, 61):
        z = i / 60.0                       # 0 — кінець, 1 — живлення (знизу вгору обернемо)
        yy = y_feed - z * L
        amp = math.cos((1 - z) * math.pi / 2)   # 1 біля живлення, 0 на кінці
        curI.append((ax + amp * 120, yy))
    f.append('<path d="M ' + ' L '.join('%.1f,%.1f' % p for p in curI) +
             '" fill="none" stroke="%s" stroke-width="2.6"/>' % NEG)
    f.append(text(ax + 150, y_feed - 24, "струм I(z)", size=11, color=NEG, bold=True))
    f.append(text(ax + 138, y_tip + 6, "I = 0", size=10, color=NEG))

    # напруга V(z): синус — 0 біля землі, max на кінці. вліво від осі
    curV = []
    for i in range(0, 61):
        z = i / 60.0
        yy = y_feed - z * L
        amp = math.sin((1 - z) * math.pi / 2) * (-1)   # 0 біля живлення, −1 на кінці → вліво
        curV.append((ax + amp * 110, yy))
    f.append('<path d="M ' + ' L '.join('%.1f,%.1f' % p for p in curV) +
             '" fill="none" stroke="%s" stroke-width="2.6" stroke-dasharray="6,4"/>' % POS)
    f.append(text(ax - 150, y_feed - 40, "напруга V(z)", size=11, color=POS, bold=True))
    f.append(text(ax - 128, y_tip + 6, "V = max", size=10, color=POS))

    # мітка довжини
    f.append(line(330, y_tip, 330, y_feed, color=FIELD, sw=1.6))
    f.append(line(324, y_tip, 336, y_tip, color=FIELD, sw=1.6))
    f.append(line(324, y_feed, 336, y_feed, color=FIELD, sw=1.6))
    f.append(text(360, (y_tip + y_feed) / 2, "λ/4", size=13, color=FIELD, bold=True, anchor="start"))
    f.append(text(360, (y_tip + y_feed) / 2 + 18, "≈ 30 мм", size=10, color=MUTED, anchor="start"))

    # пояснення праворуч
    box, _, _ = textbox(680, 235,
                        "Хвиля біжить угору,\nвідбивається від кінця\nй вертається у фазі —\nстоїть на місці.\n\nЦе й є резонанс:\nструм на живленні\nмаксимальний, опір\nвходу — суто активний.",
                        size=11, pad=14, fill="#f7faf7", stroke=FIELD, sw=1.6)
    f.append(box)

    return render(os.path.join(IMG, 'standing-wave.svg'), W, H, *f)


# ── 5. Узгодження: (30+j10) Ω чипа → 50 Ω антени через П-ланку (CLC) ──────────
def fig_pi_match():
    W, H = 940, 420
    f = [text(W / 2, 30, "Навіщо П-ланка: чип не 50 Ом, антена не 50 Ом", size=18, bold=True),
         text(W / 2, 52, "три деталі C–L–C підганяють комплексний опір виходу до 50 Ом — інакше частина хвилі відбивається",
              size=11.5, color=MUTED, italic=True)]

    midy = 210
    # чип
    f.append(rect(40, midy - 40, 130, 80, fill="#dfe7f5", stroke=NEG, sw=2, rx=6))
    f.append(text(105, midy - 8, "радіо ESP32", size=12, color=NEG, bold=True))
    f.append(text(105, midy + 12, "≈ (30 + j10) Ω", size=10.5, color=INK))

    # лінія до П-ланки
    f.append(line(170, midy, 250, midy, color=INK, sw=2.4))

    # П-ланка: два конденсатори на землю + котушка послідовно
    lx1, lx2 = 300, 470       # позиції шунтів
    # шунт-C1
    f.append(line(lx1, midy, lx1, midy + 40, color=INK, sw=2))
    f.append(line(lx1 - 12, midy + 40, lx1 + 12, midy + 40, color=INK, sw=2.4))
    f.append(line(lx1 - 12, midy + 48, lx1 + 12, midy + 48, color=INK, sw=2.4))
    f.append(text(lx1, midy + 70, "C1", size=11, color=GOLD, bold=True))
    # котушка L (послідовно)
    f.append(line(lx1, midy, lx1 + 30, midy, color=INK, sw=2.4))
    f.append('<path d="M %d,%d q 8,-16 16,0 q 8,-16 16,0 q 8,-16 16,0 q 8,-16 16,0 q 8,-16 16,0" '
             'fill="none" stroke="%s" stroke-width="2.6"/>' % (lx1 + 30, midy, GOLD))
    f.append(text((lx1 + lx2) / 2, midy - 20, "L", size=11, color=GOLD, bold=True))
    f.append(line(lx1 + 110, midy, lx2, midy, color=INK, sw=2.4))
    # шунт-C2
    f.append(line(lx2, midy, lx2, midy + 40, color=INK, sw=2))
    f.append(line(lx2 - 12, midy + 40, lx2 + 12, midy + 40, color=INK, sw=2.4))
    f.append(line(lx2 - 12, midy + 48, lx2 + 12, midy + 48, color=INK, sw=2.4))
    f.append(text(lx2, midy + 70, "C2", size=11, color=GOLD, bold=True))
    # земля під шунтами
    f.append(line(lx1, midy + 48, lx2, midy + 48, color=INK, sw=1.6))
    f.append(line(lx1, midy + 48, lx1, midy + 56, color=INK, sw=1.6))
    f.append(line(lx2, midy + 48, lx2, midy + 56, color=INK, sw=1.6))
    for gx in (lx1 - 14, lx1, lx1 + 14):
        pass
    f.append(line((lx1 + lx2) / 2 - 14, midy + 60, (lx1 + lx2) / 2 + 14, midy + 60, color=INK, sw=2))
    f.append(line((lx1 + lx2) / 2 - 8, midy + 66, (lx1 + lx2) / 2 + 8, midy + 66, color=INK, sw=2))
    f.append(line((lx1 + lx2) / 2 - 3, midy + 72, (lx1 + lx2) / 2 + 3, midy + 72, color=INK, sw=2))
    f.append(line((lx1 + lx2) / 2, midy + 56, (lx1 + lx2) / 2, midy + 60, color=INK, sw=1.6))
    f.append(text((lx1 + lx2) / 2, midy - 96, "П-ланка (C–L–C)", size=12, color=GOLD, bold=True))
    f.append(rect(lx1 - 34, midy - 84, lx2 - lx1 + 68, 150, fill="none", stroke=GOLD, sw=1.4, rx=10))

    # лінія до антени
    f.append(line(lx2, midy, 660, midy, color=INK, sw=2.4))
    f.append(text(600, midy - 12, "50 Ω", size=11, color=FIELD, bold=True))

    # антена
    f.append(line(690, midy, 720, midy, color=INK, sw=2.4))
    f.append(line(720, midy + 20, 720, midy - 44, color=INK, sw=3))
    for r in (16, 30, 44):
        f.append('<path d="M 738,%d A %d,%d 0 0 1 738,%d" fill="none" stroke="%s" stroke-width="1.6"/>'
                 % (midy - 44 - r, r, r, midy - 44 + r, FIELD))
    f.append(text(720, midy + 44, "антена 50 Ω", size=10.5, color=INK, bold=True))

    # підпис знизу
    box, _, _ = textbox(W / 2, midy + 128,
                        "C1 і C2 тягнуть опір по колу реактивностей, L зсуває його по активній осі —\n"
                        "так точку (30+j10) підводять до центру 50 Ω. Значення підбирають під плату;\n"
                        "частину позицій часто лишають незапаяними (0 Ом-перемичка чи «не встановлено»).",
                        size=10.5, pad=12, fill="#fcfcfc", stroke=MUTED, sw=1.3)
    f.append(box)

    return render(os.path.join(IMG, 'pi-match.svg'), W, H, *f)


# ── 6. Перевернута-F (IFA): та сама λ/4, але зігнута + відведення живлення ────
def fig_ifa():
    W, H = 900, 430
    f = [text(W / 2, 30, "Перевернута-F антена (IFA): чому саме її ставлять на WROOM", size=18, bold=True),
         text(W / 2, 52, "чвертьхвильовий провідник зігнуто над землею; точка живлення зсунута вздовж — це задає і резонанс, і опір",
              size=11.5, color=MUTED, italic=True)]

    gy = 330               # рівень землі
    # площина землі
    f.append(rect(120, gy, 640, 46, fill="#eef1f5", stroke=MUTED, sw=1.6, rx=0))
    f.append(text(440, gy + 28, "площина землі модуля (дзеркало-противага)", size=11, color=MUTED))

    # вертикальна стійка (коротке замикання на землю) + горизонтальне плече
    short_x = 220
    feed_x = 300
    top_y = 160
    end_x = 640
    # коротке замикання (ліва ніжка F)
    f.append(line(short_x, gy, short_x, top_y, color=INK, sw=3.2))
    f.append(text(short_x - 8, (gy + top_y) / 2, "коротке", size=10, color=INK, anchor="end"))
    f.append(text(short_x - 8, (gy + top_y) / 2 + 16, "замикання", size=10, color=INK, anchor="end"))
    # горизонтальне плече (верхня риска F) — випромінювач
    f.append(line(short_x, top_y, end_x, top_y, color=INK, sw=3.2))
    f.append(circle(end_x, top_y, 4, fill=INK, stroke=INK, sw=0))
    f.append(text(end_x + 10, top_y, "вільний кінець", size=10, color=INK, anchor="start"))
    f.append(text((short_x + end_x) / 2, top_y - 14, "випромінююче плече ≈ λ/4", size=11, color=FIELD, bold=True))

    # відведення живлення (коротка ніжка F)
    f.append(line(feed_x, top_y, feed_x, gy, color=NEG, sw=2.8))
    f.append(minus(feed_x, gy - 4, r=9))
    f.append(text(feed_x, gy - 22, "живлення (50 Ω)", size=10, color=NEG, bold=True))
    f.append(text(feed_x + 8, (top_y + gy) / 2, "відведення", size=9.5, color=NEG, anchor="start"))

    # відстань short↔feed — важіль опору
    f.append(line(short_x, top_y - 40, feed_x, top_y - 40, color=GOLD, sw=1.6))
    f.append(line(short_x, top_y - 46, short_x, top_y - 34, color=GOLD, sw=1.6))
    f.append(line(feed_x, top_y - 46, feed_x, top_y - 34, color=GOLD, sw=1.6))
    f.append(text((short_x + feed_x) / 2, top_y - 50, "d", size=12, color=GOLD, bold=True))

    # права колонка — що дає кожен елемент
    box, _, _ = textbox(770, 210,
                        "Довжина плеча\n→ задає резонанс\n(де струм у вузлі).\n\nВідстань d від\nзамикання до\nживлення →\nпідганяє опір\nвходу під 50 Ω.\n\nВисота над землею\n→ смуга частот.",
                        size=11, pad=13, fill="#f7faf7", stroke=FIELD, sw=1.6)
    f.append(box)

    return render(os.path.join(IMG, 'ifa.svg'), W, H, *f)


# ── 7. Рух робочої точки по колу Сміта: серія → по колу R, шунт → по колу G ──
def fig_smith_moves():
    """Спрощене коло Сміта: показуємо ЛИШЕ дві сім'ї дуг (сталий R, стала G)
    і як послідовна / шунтова реактивність жене точку вздовж них до центру 50 Ω."""
    import math
    W, H = 940, 500
    f = [text(W / 2, 30, "Як реактивність жене точку по колу Сміта до центру", size=18, bold=True),
         text(W / 2, 52, "послідовний елемент рухає вздовж кола сталого R; шунтовий — вздовж кола сталої G (провідності)",
              size=11.5, color=MUTED, italic=True)]

    # геометрія кола Сміта (нормовані опори z = Z/50)
    R0 = 175                       # радіус великого кола (|Γ|=1)
    cx, cy = 300, 300             # центр діаграми = узгоджені 50 Ω (Γ=0)

    # межове коло |Γ|=1
    f.append(circle(cx, cy, R0, fill="#fcfefc", stroke=MUTED, sw=1.6))
    # горизонтальна вісь дійсних опорів
    f.append(line(cx - R0, cy, cx + R0, cy, color=MUTED, sw=1.2))
    # центр — ціль
    f.append(circle(cx, cy, 5, fill=FIELD, stroke=FIELD, sw=0))
    f.append(text(cx, cy - 12, "50 Ω", size=11, color=FIELD, bold=True))
    # крайні точки осі
    f.append(text(cx - R0 - 4, cy + 4, "0", size=10, color=MUTED, anchor="end"))
    f.append(text(cx + R0 + 4, cy + 4, "∞", size=11, color=MUTED, anchor="start"))

    # кола СТАЛОГО R (нормованого r): центр (cx + R0*r/(1+r), cy), радіус R0/(1+r)
    def r_circle(r, color, sw=1.6, dash=None):
        rc = R0 / (1 + r)
        ccx = cx + R0 * r / (1 + r)
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        return ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
                'stroke-width="%.1f"%s/>' % (ccx, cy, rc, color, sw, d))

    # кола СТАЛОЇ G (нормованої g): дзеркальні — центр (cx − R0*g/(1+g), cy)
    def g_circle(g, color, sw=1.6, dash=None):
        rc = R0 / (1 + g)
        ccx = cx - R0 * g / (1 + g)
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        return ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
                'stroke-width="%.1f"%s/>' % (ccx, cy, rc, color, sw, d))

    # кілька фонових кіл сталого R (сині) і сталого G (червоні), бліді
    for r in (0.5, 1.0, 2.0):
        f.append(r_circle(r, "#c9d6f5", 1.3))
    for g in (0.5, 1.0, 2.0):
        f.append(g_circle(g, "#f2cfca", 1.3))

    # позначки: точка входу чипа z=(30+j10)/50 = 0.6 + j0.2
    # положення точки на діаграмі: Γ = (z−1)/(z+1)
    def pt(zr, zi):
        zden_r, zden_i = zr + 1, zi
        znum_r, znum_i = zr - 1, zi
        den = zden_r * zden_r + zden_i * zden_i
        gr = (znum_r * zden_r + znum_i * zden_i) / den
        gi = (znum_i * zden_r - znum_r * zden_i) / den
        return cx + gr * R0, cy - gi * R0     # y вниз

    # робоча точка чипа
    px, py = pt(0.6, 0.2)
    f.append(circle(px, py, 6, fill=NEG, stroke=NEG, sw=0))
    f.append(text(px - 10, py - 10, "(30+j10) Ω", size=10.5, color=NEG, bold=True, anchor="end"))

    # виділене коло сталого R через цю точку (r=0.6) — синє, товсте
    f.append(r_circle(0.6, NEG, 2.4))
    # виділене коло сталої G через центр (g=1) — червоне, товсте (по ньому доводимо до 50)
    f.append(g_circle(1.0, POS, 2.4))

    # стрілки-руху: 1) серія (по синьому колу R), 2) шунт (по червоному колу G) до центру
    # проміжна точка — перетин кола r=0.6 з колом g=1 (беремо приблизно на нижній півкулі)
    mx, my = pt(0.6, -0.49)       # та сама r=0.6, іде вниз реактивністю до кола g=1
    f.append(arrow(px, py, mx, my, color=NEG, sw=2.6))
    f.append(text(mx + 12, my + 6, "серія: вздовж кола R", size=10.5, color=NEG, anchor="start", bold=True))
    f.append(arrow(mx, my, cx, cy, color=POS, sw=2.6))
    f.append(text((mx + cx) / 2 + 8, (my + cy) / 2 + 18, "шунт: вздовж кола G", size=10.5, color=POS, anchor="start", bold=True))

    # легенда праворуч
    box, _, _ = textbox(720, 250,
                        "Дві сім'ї дуг:\n\n• коло СТАЛОГО R\n  (сине) — по ньому\n  жене ПОСЛІДОВНА\n  реактивність;\n\n• коло СТАЛОЇ G\n  (червоне) — по ньому\n  жене ШУНТОВА.\n\nЗадача — двома\nкроками дійти\nз точки чипа\nв центр (50 Ω).",
                        size=11, pad=14, fill="#fbfdff", stroke=NEG, sw=1.4)
    f.append(box)

    return render(os.path.join(IMG, 'smith-moves.svg'), W, H, *f)


# ── 8. П-ланка = дві Г-ланки навколо віртуального опору R_вірт < обох кінців ──
def fig_pi_as_two_l():
    W, H = 940, 470
    f = [text(W / 2, 30, "П-ланка = дві Г-ланки, склеєні через віртуальний опір", size=18, bold=True),
         text(W / 2, 52, "кожна половина знижує свій кінець до спільного R_вірт; що глибше R_вірт — то вища Q і вужча смуга",
              size=11.5, color=MUTED, italic=True)]

    # горизонтальна «драбина опорів»: R_дж — R_вірт (внизу) — R_н, з двома Г-ланками
    axy = 250
    x_src, x_v, x_load = 150, 470, 790

    # три вузли-опори
    def node(x, y, label, sub, color):
        return [circle(x, y, 30, fill="#fcfcfc", stroke=color, sw=2.2),
                text(x, y - 2, label, size=12, color=color, bold=True),
                text(x, y + 15, sub, size=9, color=MUTED)]

    f += node(x_src, axy, "R_дж", "≈ 30 Ω", NEG)
    f += node(x_load, axy, "R_н", "≈ 50 Ω", FIELD)
    # віртуальний вузол — нижче, підкреслено, бо R_вірт МЕНШИЙ за обидва
    f += node(x_v, axy + 120, "R_вірт", "< 30 Ω", GOLD)

    # ліва Г-ланка: R_дж → R_вірт
    f.append(arrow(x_src + 28, axy + 10, x_v - 22, axy + 108, color=NEG, sw=2.2))
    box, _, _ = textbox((x_src + x_v) / 2 - 20, axy + 30,
                        "Г-ланка №1\nзнижує 30 Ω\nдо R_вірт",
                        size=10.5, pad=10, fill="#f4f7ff", stroke=NEG, sw=1.3)
    f.append(box)

    # права Г-ланка: R_вірт → R_н
    f.append(arrow(x_v + 22, axy + 108, x_load - 28, axy + 10, color=FIELD, sw=2.2))
    box, _, _ = textbox((x_v + x_load) / 2 + 20, axy + 30,
                        "Г-ланка №2\nпіднімає R_вірт\nдо 50 Ω",
                        size=10.5, pad=10, fill="#f2fbf5", stroke=FIELD, sw=1.3)
    f.append(box)

    # вертикальна шкала «глибина R_вірт → Q»
    sx = 880
    f.append(line(sx, 110, sx, 400, color=MUTED, sw=1.6))
    f.append(text(sx + 6, 110, "Q мала", size=9.5, color=MUTED, anchor="start"))
    f.append(text(sx + 6, 122, "смуга широка", size=9.5, color=FIELD, anchor="start"))
    f.append(text(sx + 6, 392, "Q велика", size=9.5, color=MUTED, anchor="start"))
    f.append(text(sx + 6, 404, "смуга вузька", size=9.5, color=POS, anchor="start"))
    f.append('<path d="M %d,120 L %d,395" fill="none" stroke="%s" stroke-width="2" marker-end="url(#arrow)"/>'
             % (sx, sx, MUTED))

    # підпис-висновок знизу
    box, _, _ = textbox(W / 2 - 60, 430,
                        "Проміжний R_вірт — вільний параметр, якого в Г-ланці нема. Обираючи його ГЛИБШЕ за обидва кінці,\n"
                        "піднімаємо перепад кожної половини, а з ним і сумарну Q; вужчаючи, це і є плата за керовану смугу.\n"
                        "Виберемо R_вірт близько до кінців — П розширює смугу; заженемо глибоко — звужує й піднімає підсилення на краях.",
                        size=10.3, pad=12, fill="#fcfcfc", stroke=MUTED, sw=1.3)
    f.append(box)

    return render(os.path.join(IMG, 'pi-as-two-l.svg'), W, H, *f)


# ── 9. [ІСТОРІЯ] 50 Ом — компроміс між потужністю (~30) і згасанням (~77) ────
def fig_fifty_compromise():
    """Дві криві-навпаки для повітряного коаксіала: згасання мінімальне
    близько 77 Ом, потужність максимальна близько 30 Ом. 50 Ом лежить між
    середніми (геом. 48, ариф. 53.5) — «найменш погане» місце."""
    import math
    W, H = 900, 480
    f = [text(W / 2, 30, "Звідки взялися 50 Ом: дві вимоги тягнуть у різні боки", size=18, bold=True),
         text(W / 2, 52, "у повітряному коаксіалі потужність максимальна ≈ 30 Ом, згасання мінімальне ≈ 77 Ом — разом не буває",
              size=11.5, color=MUTED, italic=True)]

    # осі
    x0, x1 = 130, 720          # ліва/права межа по імпедансу
    y0, y1 = 400, 100          # низ/верх по «якості»
    Zmin, Zmax = 15.0, 100.0

    def X(Z):
        return x0 + (Z - Zmin) / (Zmax - Zmin) * (x1 - x0)

    # осі-лінії
    f.append(line(x0, y0, x1, y0, color=INK, sw=1.8))
    f.append(line(x0, y0, x0, y1, color=INK, sw=1.8))
    f.append(text((x0 + x1) / 2, y0 + 46, "хвильовий опір коаксіала, Ом", size=11.5, color=INK))
    f.append(text(x0 - 18, (y0 + y1) / 2, "краще →", size=10.5, color=MUTED, anchor="middle"))

    # позначки осі імпедансу
    for Z in (20, 30, 50, 77, 100):
        f.append(line(X(Z), y0, X(Z), y0 + 6, color=INK, sw=1.4))
        f.append(text(X(Z), y0 + 22, str(Z), size=10, color=INK))

    # крива «потужність» — росте до ~30, далі спадає (дзвіночок навколо 30)
    curP = []
    for i in range(0, 121):
        Z = Zmin + (Zmax - Zmin) * i / 120.0
        v = math.exp(-((Z - 30.0) / 30.0) ** 2)     # пік на 30
        curP.append((X(Z), y0 - v * (y0 - y1) * 0.92))
    f.append('<path d="M ' + ' L '.join('%.1f,%.1f' % p for p in curP) +
             '" fill="none" stroke="%s" stroke-width="2.8"/>' % POS)
    f.append(text(X(24) - 6, y1 + 26, "потужність", size=11.5, color=POS, bold=True, anchor="end"))
    f.append(text(X(24) - 6, y1 + 42, "(пік ≈ 30 Ом)", size=9.5, color=POS, anchor="end"))

    # крива «мале згасання» — росте до ~77 (дзвіночок навколо 77)
    curA = []
    for i in range(0, 121):
        Z = Zmin + (Zmax - Zmin) * i / 120.0
        v = math.exp(-((Z - 77.0) / 34.0) ** 2)     # пік на 77
        curA.append((X(Z), y0 - v * (y0 - y1) * 0.92))
    f.append('<path d="M ' + ' L '.join('%.1f,%.1f' % p for p in curA) +
             '" fill="none" stroke="%s" stroke-width="2.8" stroke-dasharray="7,5"/>' % NEG)
    f.append(text(X(90) + 6, y1 + 26, "мале згасання", size=11.5, color=NEG, bold=True, anchor="start"))
    f.append(text(X(90) + 6, y1 + 42, "(пік ≈ 77 Ом)", size=9.5, color=NEG, anchor="start"))

    # смуга компромісу 48…53.5 і лінія 50
    f.append(rect(X(48), y1 - 6, X(53.5) - X(48), y0 - y1 + 6, fill="#eef6ef", stroke=FIELD, sw=0, rx=0))
    f.append(line(X(50), y0, X(50), y1 - 6, color=FIELD, sw=2.4, dash="4,4"))
    f.append(circle(X(50), y0, 5, fill=FIELD, stroke=FIELD, sw=0))
    f.append(text(X(50), y1 - 16, "50 Ом", size=13, color=FIELD, bold=True))

    # підпис-висновок
    box, _, _ = textbox(W / 2, 448,
                        "Геометричне середнє √(30·77) ≈ 48 Ом; арифметичне (30+77)/2 ≈ 53.5 Ом.\n"
                        "50 — кругле число всередині вилки: не найкраще ні для чого, але й не найгірше ні для чого.",
                        size=10.6, pad=11, fill="#fcfcfc", stroke=MUTED, sw=1.3)
    f.append(box)

    return render(os.path.join(IMG, 'fifty-compromise.svg'), W, H, *f)


# ── 10. [ІСТОРІЯ] Дві нитки стандартів, що зійшлися в антені ESP32 ────────────
def fig_two_standards():
    W, H = 900, 430
    f = [text(W / 2, 30, "Дві нитки, що зійшлися в антені ESP32", size=18, bold=True),
         text(W / 2, 52, "одна дала опір 50 Ом, друга — форму випромінювача; обидві старші за сам чип на десятиліття",
              size=11.5, color=MUTED, italic=True)]

    def stripe(y, accent, title):
        return [rect(60, y - 26, 780, 4, fill=accent, stroke=accent, sw=0, rx=0),
                text(72, y - 34, title, size=12.5, color=accent, bold=True, anchor="start")]

    def mark(x, y, accent, year, cap):
        return [circle(x, y - 24, 6, fill="#fcfcfc", stroke=accent, sw=2.4),
                text(x, y - 44, year, size=11, color=accent, bold=True),
                text(x, y + 2, cap, size=9.6, color=INK)]

    # нитка 1 — імпеданс 50 Ом
    y1 = 150
    f += stripe(y1, NEG, "Опір 50 Ом")
    f += mark(150, y1, NEG, "1929", "коаксіал:")
    f.append(text(150, y1 + 16, "заявка Bell Labs", size=9.2, color=MUTED))
    f += mark(360, y1, NEG, "1931", "патент")
    f.append(text(360, y1 + 16, "US 1,835,031", size=9.2, color=MUTED))
    f += mark(560, y1, NEG, "~1930-ті", "вилка 30↔77")
    f.append(text(560, y1 + 16, "→ 50 як компроміс", size=9.2, color=MUTED))
    f += mark(760, y1, NEG, "1949", "MIL-C-17")
    f.append(text(760, y1 + 16, "закріплює стандарт", size=9.2, color=MUTED))

    # нитка 2 — форма антени
    y2 = 300
    f += stripe(y2, POS, "Форма випромінювача")
    f += mark(150, y2, POS, "1940-ві", "дротова F")
    f.append(text(150, y2 + 16, "низький штир", size=9.2, color=MUTED))
    f += mark(410, y2, POS, "1958", "перевернута-F")
    f.append(text(410, y2 + 16, "група Кінґа, ракети", size=9.2, color=MUTED))
    f += mark(680, y2, POS, "1990-ті", "PIFA")
    f.append(text(680, y2 + 16, "у мобільних", size=9.2, color=MUTED))

    # злиття
    f.append(arrow(760, y1 + 30, 470, 372, color=MUTED, sw=1.8))
    f.append(arrow(680, y2 + 30, 470, 372, color=MUTED, sw=1.8))
    box, _, _ = textbox(470, 388,
                        "ESP32 (2016): перевернута-F на краю плати, живлена лінією 50 Ом",
                        size=11, pad=11, fill="#f7faf7", stroke=FIELD, sw=1.8, bold=True, color=FIELD)
    f.append(box)

    return render(os.path.join(IMG, 'two-standards.svg'), W, H, *f)


if __name__ == '__main__':
    fig_antenna_types()
    fig_detune()
    fig_ufl_chain()
    fig_standing_wave()
    fig_pi_match()
    fig_ifa()
    fig_smith_moves()
    fig_pi_as_two_l()
    fig_fifty_compromise()
    fig_two_standards()
    print('OK: antenna-types, detune, ufl-chain, standing-wave, pi-match, ifa, smith-moves, pi-as-two-l, fifty-compromise, two-standards')

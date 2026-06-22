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


if __name__ == '__main__':
    fig_antenna_types()
    fig_detune()
    fig_ufl_chain()
    print('OK: antenna-types.svg, detune.svg, ufl-chain.svg')

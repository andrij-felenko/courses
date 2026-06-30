# -*- coding: utf-8 -*-
"""Фігури до теми «Відношення сигнал/шум» (аналогова електроніка, кутом теорії кіл).
П'ять фігур:
  signal-in-noise.svg — той самий сигнал на тлі трьох рівнів шуму (високе/середнє/низьке SNR)
  ratio-not-level.svg — підсилення піднімає і сигнал, і шум однаково: відношення стале
  snr-budget.svg      — підлога й стеля каналу; SNR = відстань між сигналом і шумовою полицею
  cascade-referred.svg— шум кожного каскаду, зведений до входу, ділиться на добуток попередніх підсилень
  cascade-weak-first.svg— слабке підсилення першого каскаду пропускає шум другого на вхід
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def _wiggle(seed):
    """Простий детермінований псевдошум у [-1,1] — без залежностей."""
    x = math.sin(seed * 12.9898) * 43758.5453
    return (x - math.floor(x)) * 2 - 1


def signal_in_noise():
    """Одна синусоїда на трьох рівнях шуму: тоне → видно → чисто."""
    W, H = 720, 360
    p = []
    panels = [
        ("низьке SNR", 1.0, POS, "сигнал тоне в шумі"),
        ("середнє SNR", 0.35, INK, "сигнал видно крізь шум"),
        ("високе SNR", 0.08, FIELD, "шум майже непомітний"),
    ]
    pw = (W - 40) / 3.0
    base_y = 200
    amp = 46
    for i, (lbl, nlev, col, note) in enumerate(panels):
        x0 = 20 + i * pw
        cx = x0 + pw / 2
        # рамка панелі
        p.append(rect(x0 + 8, 60, pw - 16, 220, fill=BG, stroke=MUTED, sw=1))
        p.append(text(cx, 50, lbl, size=14, bold=True, color=col))
        # сигнал + шум
        pts_sig = []
        pts_mix = []
        N = 90
        for k in range(N + 1):
            xx = x0 + 14 + (pw - 28) * k / N
            ph = 2 * math.pi * 2.2 * k / N
            s = math.sin(ph) * amp
            n = _wiggle(k * 1.7 + i * 100) * amp * nlev
            pts_sig.append((xx, base_y - s))
            pts_mix.append((xx, base_y - s - n))
        # чистий сигнал — тонка опорна лінія
        d_sig = "M" + " L".join("%.1f %.1f" % q for q in pts_sig)
        p.append('<path d="%s" fill="none" stroke="%s" stroke-width="1" stroke-dasharray="3 3"/>'
                 % (d_sig, MUTED))
        # сигнал+шум — жирна
        d_mix = "M" + " L".join("%.1f %.1f" % q for q in pts_mix)
        p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (d_mix, col))
        p.append(text(cx, 272, note, size=11, color=MUTED))
    b, _, _ = textbox(W / 2, 326,
                      "Той самий корисний сигнал (пунктир) — лише рівень шуму різний.\n"
                      "SNR — це не «гучність» сигналу, а наскільки він вищий за шум.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'signal-in-noise.svg'), W, H, *p,
           title="Що таке відношення сигнал/шум: сигнал на тлі трьох рівнів шуму")


def ratio_not_level():
    """Підсилення множить сигнал і шум однаково — відношення не міняється."""
    W, H = 700, 340
    p = []
    cy = 150
    # вхід: маленький стовпчик сигналу + маленький стовпчик шуму
    def stack(cx, sig_h, noise_h, scale_lbl):
        out = []
        bw = 46
        # шум знизу
        out.append(rect(cx - bw / 2, cy + 60 - noise_h, bw, noise_h, fill="#fdecea", stroke=POS, sw=1.5))
        # сигнал згори від шуму
        out.append(rect(cx - bw / 2, cy + 60 - noise_h - sig_h, bw, sig_h, fill="#eaf0fd", stroke=NEG, sw=1.5))
        out.append(text(cx, cy + 80, scale_lbl, size=12, bold=True))
        return out
    # вхід
    p += stack(120, 50, 16, "вхід")
    p.append(text(120, cy - 70, "сигнал", size=11, color=NEG))
    p.append(text(120, cy - 54, "шум", size=11, color=POS))
    # підсилювач-трикутник
    ax = 250
    p.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.8"/>'
             % (ax, cy - 30, ax, cy + 30, ax + 70, cy, FILL, LINE))
    p.append(text(ax + 24, cy + 5, "×G", size=17, bold=True))
    p.append(arrow(ax + 70, cy, ax + 120, cy, color=INK, sw=2))
    # вихід: усе вище в G разів — обидва стовпчики
    p += stack(470, 50 * 2.4, 16 * 2.4, "вихід")
    p.append(text(530, cy - 95, "×G вище", size=12, bold=True, color=MUTED, anchor="start"))
    # підпис рівності відношень
    p.append(text(120, cy + 102, "сигнал/шум = 3.1", size=12, bold=True, color=FIELD))
    p.append(text(470, cy + 102, "сигнал/шум = 3.1", size=12, bold=True, color=FIELD))
    p.append(text(295, cy + 102, "= те саме!", size=12, bold=True, color=FIELD))

    b, _, _ = textbox(W / 2, 310,
                      "Підсилення піднімає сигнал і шум на той самий множник G.\n"
                      "Відношення не зрушується — підсилення НЕ покращує SNR.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'ratio-not-level.svg'), W, H, *p,
           title="Чому підсилення не змінює SNR: росте і сигнал, і шум")


def snr_budget():
    """Стеля (макс. сигнал) і підлога (шум): SNR = відстань між ними; динамічний діапазон — уся щілина."""
    W, H = 700, 380
    p = []
    ox, oy = 110, 320
    ax_h = 250
    p.append(line(ox, oy, ox, oy - ax_h - 10, color=INK, sw=2))     # вісь рівнів
    p.append(text(ox - 70, oy - ax_h / 2, "рівень", size=13, bold=True))
    p.append(text(ox - 70, oy - ax_h / 2 + 18, "(дБ)", size=13, bold=True))

    bx = ox + 40
    bw = 360
    # стеля — максимальний неспотворений сигнал
    ceil_y = oy - ax_h + 10
    p.append(line(bx, ceil_y, bx + bw, ceil_y, color=POS, sw=2.6))
    p.append(text(bx + bw + 4, ceil_y + 4, "стеля: макс. сигнал (кліпінг вище)", size=12, color=POS, anchor="start"))
    # шумова полиця — підлога
    floor_y = oy - 40
    p.append(rect(bx, floor_y, bw, 40, fill="#fdecea", stroke=POS, sw=1, rx=2))
    p.append(text(bx + bw + 4, floor_y + 24, "шумова полиця (підлога)", size=12, color=MUTED, anchor="start"))
    # реальний сигнал десь усередині
    sig_y = oy - 150
    p.append(line(bx, sig_y, bx + bw, sig_y, color=NEG, sw=2.6))
    p.append(text(bx + bw + 4, sig_y + 4, "поточний сигнал", size=12, color=NEG, anchor="start"))

    # SNR = відстань сигнал → підлога
    arx = bx + 90
    p.append(line(arx, sig_y, arx, floor_y, color=FIELD, sw=2))
    p.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s"/>'
             % (arx - 4, sig_y + 6, arx + 4, sig_y + 6, arx, sig_y, FIELD))
    p.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s"/>'
             % (arx - 4, floor_y - 6, arx + 4, floor_y - 6, arx, floor_y, FIELD))
    p.append(text(arx + 8, (sig_y + floor_y) / 2, "SNR", size=13, bold=True, color=FIELD, anchor="start"))

    # динамічний діапазон = стеля → підлога
    drx = bx + 250
    p.append(line(drx, ceil_y, drx, floor_y, color=INK, sw=2, dash="5 4"))
    p.append(text(drx + 8, (ceil_y + floor_y) / 2 - 10, "динамічний", size=12, bold=True, anchor="start"))
    p.append(text(drx + 8, (ceil_y + floor_y) / 2 + 6, "діапазон", size=12, bold=True, anchor="start"))

    b, _, _ = textbox(W / 2, 356,
                      "SNR — відстань у дБ від ПОТОЧНОГО сигналу до шумової полиці.\n"
                      "Уся щілина від стелі до полиці — це динамічний діапазон каналу.",
                      size=12, fill="#f4f6f8", stroke=LINE)
    p.append(b)
    render(os.path.join(OUT, 'snr-budget.svg'), W, H, *p,
           title="SNR як відстань до шумової полиці; динамічний діапазон — уся щілина")


def cascade_referred():
    """Шум трьох каскадів, зведений до входу: кожен ділиться на добуток попередніх підсилень.
    Видно, чому перший каскад домінує — його шум не придушений нічим."""
    W, H = 720, 470
    p = []
    # ── верхній ряд: ланцюг трикутників-каскадів зі своїм шумом ──
    cy = 90
    stages = [("каскад 1", "G₁=100", "n₁"),
              ("каскад 2", "G₂=20", "n₂"),
              ("каскад 3", "G₃=10", "n₃")]
    x = 70
    for i, (lbl, glbl, nl) in enumerate(stages):
        p.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.8"/>'
                 % (x, cy - 26, x, cy + 26, x + 58, cy, FILL, LINE))
        p.append(text(x + 20, cy + 5, glbl, size=12, bold=True))
        p.append(text(x + 29, cy - 36, lbl, size=12, color=MUTED))
        # власний шум каскаду — стрілочка згори в його вхід
        p.append(text(x + 2, cy + 50, "+" + nl, size=12, bold=True, color=POS, anchor="start"))
        if i < 2:
            p.append(arrow(x + 58, cy, x + 92, cy, color=INK, sw=2))
        x += 92
    p.append(arrow(x - 34, cy, x + 4, cy, color=INK, sw=2))
    p.append(text(x + 40, cy + 5, "вихід", size=12, color=MUTED, anchor="start"))
    p.append(text(40, cy + 5, "вхід", size=12, color=MUTED, anchor="end"))
    p.append(arrow(8, cy, 40, cy, color=INK, sw=2))

    # ── нижній ряд: ті самі три шуми, ЗВЕДЕНІ ДО ВХОДУ (стовпчики різної висоти) ──
    base_y = 350
    bx0 = 120
    gap = 175
    bw = 64
    # відносні висоти ∝ внеску до входу:  n₁ : n₂/G₁ : n₃/(G₁G₂)
    bars = [
        ("n₁", 1.00, "повна сила", POS),
        ("n₂ / G₁", 0.20, "÷ 100", NEG),
        ("n₃ / (G₁·G₂)", 0.045, "÷ 2000", FIELD),
    ]
    maxh = 190
    for i, (lbl, frac, divlbl, col) in enumerate(bars):
        cx = bx0 + i * gap
        h = max(8, maxh * frac)
        fillc = {"#c0392b": "#fdecea", "#2457d6": "#eaf0fd", "#27ae60": "#eafaf0"}[col]
        p.append(rect(cx - bw / 2, base_y - h, bw, h, fill=fillc, stroke=col, sw=1.8))
        p.append(text(cx, base_y + 18, lbl, size=13, bold=True, color=col))
        p.append(text(cx, base_y + 36, divlbl, size=11, color=MUTED))
        if h > 22:
            p.append(text(cx, base_y - h - 6, "%.0f%%" % (frac * 100), size=11, bold=True, color=col))
        else:
            p.append(text(cx, base_y - h - 6, "%.1f%%" % (frac * 100), size=11, bold=True, color=col))
    p.append(line(bx0 - bw / 2 - 14, base_y, bx0 + 2 * gap + bw / 2 + 14, base_y, color=INK, sw=1.5))
    p.append(text(bx0 + gap, base_y + 56, "внесок у вхідний шум (зведено до входу)", size=12, bold=True, color=MUTED))

    b, _, _ = textbox(W / 2, 442,
                      "Шум каскаду, зведений до входу, ділиться на ДОБУТОК підсилень усіх попередніх.\n"
                      "Перший каскад не поділений нічим — його шум домінує над усім трактом.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'cascade-referred.svg'), W, H, *p,
           title="Шум каскадів, зведений до входу: перший важить найбільше")


def cascade_weak_first():
    """Той самий другий каскад, два перші підсилення: сильне топить його шум, слабке — пропускає."""
    W, H = 700, 390
    p = []
    base_y = 250
    bw = 70
    cases = [
        ("сильний 1-й каскад", 100, 0.012, FIELD, "G₁ = 100"),
        ("слабкий 1-й каскад", 3, 0.40, POS, "G₁ = 3"),
    ]
    centers = [185, 470]
    maxh = 170
    for (lbl, g1, frac, col, glbl), cx in zip(cases, centers):
        h = max(8, maxh * frac)
        fillc = "#eafaf0" if col == FIELD else "#fdecea"
        # стовпчик «шум 2-го каскаду на вході»
        p.append(rect(cx - bw / 2, base_y - h, bw, h, fill=fillc, stroke=col, sw=2))
        p.append(text(cx, base_y - h - 8, "n₂ / G₁", size=12, bold=True, color=col))
        p.append(text(cx, base_y + 22, lbl, size=13, bold=True))
        p.append(text(cx, base_y + 40, glbl, size=12, color=MUTED))
    p.append(line(120, base_y, 560, base_y, color=INK, sw=1.5))
    p.append(text(340, base_y - 150, "(той самий каскад 2: n₂ однаковий)", size=12, color=MUTED))

    b, _, _ = textbox(W / 2, 345,
                      "Шум другого каскаду доходить до входу як n₂ / G₁. Сильне G₁ топить його в нуль;\n"
                      "слабке G₁ майже не давить — шум другого пролазить у підсумковий SNR.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'cascade-weak-first.svg'), W, H, *p,
           title="Чому слабке підсилення першого каскаду пропускає шум другого")


if __name__ == '__main__':
    signal_in_noise()
    ratio_not_level()
    snr_budget()
    cascade_referred()
    cascade_weak_first()
    print("OK: 5 figures ->", OUT)

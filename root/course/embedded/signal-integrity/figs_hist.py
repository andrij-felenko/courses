# -*- coding: utf-8 -*-
"""Фігури для ІСТОРИЧНОЇ вставки hist-eye-diagram.md (крок «Цілісність сигналу»).
Окремий файл, щоб не змагатися за figs.py овнер-статті. Вивід — у той самий ./img/.
Запуск:  python figs_hist.py
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GOOD = FIELD        # «чистий» / зрілий
BAD  = POS          # око / спотворення
WAVE = NEG          # хвиля / фундамент


# ── 1. Родовід очної діаграми крізь епохи ────────────────────────────────────
def fig_history_timeline():
    """Від спотворення телеграфного імпульсу до багатогігабітного серіалу:
    одна ідея мандрує понад вісімдесят років."""
    W, H = 900, 450
    el = []
    el.append(text(W/2, 30, "Родовід очної діаграми: інструмент мандрує крізь епохи",
                   size=16, bold=True))

    axis_y = 372
    x0, x1 = 56, W - 40
    el.append(line(x0, axis_y, x1, axis_y, INK, 2.5))
    el.append(arrow(x1 - 1, axis_y, x1 + 18, axis_y, INK, 2.5))
    el.append(text(x1 + 6, axis_y + 26, "час", size=11, color=MUTED, italic=True))

    # (частка по осі, рік, заголовок, тіло, колір, заливка, висота стовпчика)
    miles = [
        (0.02, "1870-ті",   "ТЕЛЕГРАФ:\nрозмитий імпульс",
         "інженери б'ються з\nрозтіканням точок-тире;\nпроблему названо,\nприладу ще нема", MUTED, "#f2f3f5", 120),
        (0.21, "1928",      "НАЙКВІСТ:\nтеорія ISI",
         "H. Nyquist формалізує\nспотворення й умову без\nміжсимвольної завади\n— фундамент, не око", WAVE, "#eef2ff", 172),
        (0.43, "1943",      "SIGSALY:\nперше ОКО",
         "Bell Labs, шифрований\nголос: багаторівневе око\nналаштовує мить вибірки\n— задокументований дебют", BAD, "#fdecea", 228),
        (0.62, "1960-ті",   "PCM:\nстандартний прилад",
         "цифрова телефонія Bell:\nоко — буденний тест ISI\nу підручниках із передачі\n(Bennett, Lucky)", GOOD, "#eafaf0", 172),
        (0.80, "1980–90-ті", "ОПТИКА:\nмаска прийомки",
         "волоконний зв'язок: око\n+ «маска» як критерій\nвідповідності (SONET/SDH,\nGigabit Ethernet)", WAVE, "#eef2ff", 120),
        (0.965, "сьогодні", "СЕРІАЛ:\nоко в кремнії",
         "USB / PCIe / DDR / SerDes;\nоко рахують BERT-и й\nвбудовані eye-монітори\nпрямо в чипі", BAD, "#fdecea", 80),
    ]

    for frac, year, head, body, col, fill, stem in miles:
        x = x0 + (x1 - x0 - 36) * frac
        top = axis_y - stem
        el.append(line(x, axis_y, x, top, col, 1.6, dash="4,3"))
        el.append(circle(x, axis_y, 5, fill=col, stroke=col, sw=1))
        el.append(text(x, axis_y + 22, year, size=11, color=INK, bold=True))
        hbox, hw, hh = textbox(x, top - 24, head, size=10.5, bold=True,
                               color=col, fill=fill, stroke=col, sw=1.6)
        el.append(hbox)
        el.append(mtext(x, top - 24 + hh/2 + 14, body, size=8.5, color=MUTED, lh=1.28))

    el.append(text(W/2, H - 12,
                   "одна ідея — накласти багато бітів і глянути на «просвіт» — служить уже понад вісімдесят років",
                   size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "history-timeline.svg"), W, H, *el)


def _eye_bundle(cx, cy, half_w, levels, col):
    """Пучок переходів між сусідніми рівнями → візерунок ока(чей)."""
    frags = []
    for y in levels:                                   # тонкі рейки рівнів
        frags.append(line(cx - half_w, y, cx + half_w, y, "#d7dade", 1.0))
    n = len(levels)
    for a in range(n):
        for b in range(n):
            ya, yb = levels[a], levels[b]
            for k in range(3):
                jx = (k - 1) * (half_w * 0.05)         # розкид моменту перетину (jitter)
                na = (k - 1) * 2.4                       # легке розмиття рівня (шум)
                nb = (1 - k) * 2.4
                xL, xR = cx - half_w, cx + half_w
                xm = cx + jx
                d = ("M %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f "
                     "S %.1f %.1f, %.1f %.1f") % (
                    xL, ya + na,
                    xL + half_w * 0.5, ya + na,
                    xm - half_w * 0.25, (ya + yb) / 2,
                    xm, (ya + yb) / 2,
                    xR - half_w * 0.5, yb + nb,
                    xR, yb + nb)
                frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="1" '
                             'opacity="0.5"/>' % (d, col))
    return frags


# ── 2. Одне око чи п'ять: спадок багаторівневого SIGSALY ──────────────────────
def fig_history_levels():
    """Чому SIGSALY-око НЕ схоже на сучасне: 6 рівнів дають 5 очей одне над одним,
    бінар — одне велике око."""
    W, H = 860, 374
    el = []
    el.append(text(W/2, 30, "Одне око чи п'ять: спадок багаторівневого SIGSALY",
                   size=16, bold=True))

    hw = 150
    # ── ліва панель: бінарне око (сучасна цифра) ──
    cxL, cyL = 240, 207
    el.extend(_eye_bundle(cxL, cyL, hw, [cyL - 78, cyL + 78], WAVE))
    el.append('<ellipse cx="%.1f" cy="%.1f" rx="34" ry="34" fill="#eef2ff" '
              'stroke="%s" stroke-width="1.6" opacity="0.85"/>' % (cxL, cyL, WAVE))
    el.append(text(cxL, cyL + 5, "ОКО", size=12, color=WAVE, bold=True))
    el.append(text(cxL, 76, "Сучасна цифра: 2 рівні", size=12.5, bold=True))
    el.append(text(cxL, 95, "(«0» і «1») → одне око", size=10.5, color=MUTED))
    el.append(text(cxL, cyL + 122, "USB · SPI · DDR · Ethernet",
                   size=10, color=MUTED, italic=True))

    el.append(line(W/2, 66, W/2, H - 50, "#d0d4d8", 1.4, dash="5,4"))

    # ── права панель: 6-рівневе око SIGSALY ──
    cxR, cyR = 620, 207
    levR = [cyR - 95 + i * 38 for i in range(6)]        # рівні 0..5
    el.extend(_eye_bundle(cxR, cyR, hw, levR, BAD))
    for i in range(5):                                   # п'ять очей між сусідами
        ey = (levR[i] + levR[i + 1]) / 2
        el.append('<ellipse cx="%.1f" cy="%.1f" rx="22" ry="11" fill="#fdecea" '
                  'stroke="%s" stroke-width="1.3" opacity="0.9"/>' % (cxR, ey, BAD))
    el.append(text(cxR, 76, "SIGSALY: 6 рівнів (0…5)", size=12.5, bold=True))
    el.append(text(cxR, 95, "→ п'ять очей одне над одним", size=10.5, color=MUTED))
    el.append(text(cxR, cyR + 122, "шифрований голос, 1943",
                   size=10, color=MUTED, italic=True))

    el.append(text(W/2, H - 14,
                   "що більше рівнів сигналу, то більше очей — і то вужче кожне; саме тісноту цих очей "
                   "інженери SIGSALY вперше й читали приладом",
                   size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "history-levels.svg"), W, H, *el)


if __name__ == "__main__":
    fig_history_timeline()
    fig_history_levels()
    print("OK: 2 history figures ->", IMG)

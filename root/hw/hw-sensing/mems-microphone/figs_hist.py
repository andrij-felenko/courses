# -*- coding: utf-8 -*-
"""figs_hist.py — фігури до історичної вставки «кремнієвий мікрофон».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/.
Імена файлів — slug-only, без номерів (AUTHORING §2/§5)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)


# ── hist-timeline: дорога кремнієвого мікрофона від ідеї до конвеєра ─────────
# Дві смуги: спершу довгі десятиліття лабораторних спроб (сіре, розріджене),
# тоді щільна серія реальних подій після приходу в масове виробництво.
def fig_timeline():
    W, H = 940, 470
    parts = []

    x0, x1 = 80, 858
    axy = 200

    parts.append(text(W / 2, 34, "від першого кремнієвого мікрофона до масового чипа",
                      size=15, bold=True))

    # роки й підписи: (рік, підпис, dy-зверху-від-осі, колір-крапка)
    # dy<0 — підпис вище осі; dy>0 — нижче. Сусідні рознесено, щоб не злипались.
    events = [
        (1962, "електрет\n(Сесслер, Вест)", -54, MUTED),
        (1983, "перший кремнієвий\nмікрофон (Ройє)", 44, MUTED),
        (1990, "кремнієвий\nконденсатор", -54, MUTED),
        (2002, "платформа SiSonic\n(Knowles Acoustics)", -100, FIELD),
        (2003, "перші поставки\nу вироби", 44, FIELD),
        (2004, "доба тонких\nтелефонів", 100, NEG),
        (2009, "1 млрд\nчипів", -54, POS),
    ]

    def xof(year):
        # нелінійна вісь: 1958…2000 стиснено на ліву третину, 2000…2010 — на решту
        if year <= 2000:
            f = (year - 1958) / (2000 - 1958) * 0.40
        else:
            f = 0.40 + (year - 2000) / (2010 - 2000) * 0.60
        return x0 + f * (x1 - x0)

    # межа двох епох
    xmid = xof(2000)
    parts.append(line(xmid, axy - 130, xmid, axy + 130, color=MUTED, sw=1, dash="2,4"))

    # смуга «десятиліття спроб» ліворуч, тоненька сіра
    parts.append(line(x0, axy, xmid, axy, color=MUTED, sw=2))
    # смуга «переворот» праворуч, яскравіша
    parts.append(line(xmid, axy, x1, axy, color=INK, sw=2))

    for year, lab, dy, col in events:
        x = xof(year)
        parts.append(circle(x, axy, 6, fill=col, stroke=INK, sw=1.4))
        # рік — впритул до осі з боку підпису
        yr_y = axy + (-16 if dy < 0 else 24)
        parts.append(text(x, yr_y, str(year), size=13, bold=True, color=INK))
        # тонка виноска до групи підпису, якщо вона далеко
        parts.append(mtext(x, axy + dy, lab, size=10.5, color=col))

    # дужка «десятиліття спроб» під стисненою частиною
    parts.append(text((x0 + xmid) / 2, axy + 118,
                      "~40 років: працює в лабораторії, не йде у великий обсяг",
                      size=11, italic=True, color=MUTED))

    # дужка «переворот» над розтягнутою
    parts.append(text((xmid + x1) / 2, axy - 128,
                      "переворот: чип ліг у наявний конвеєр мікросхем",
                      size=11.5, bold=True, color=FIELD))

    box, bw, bh = textbox(W / 2, H - 32,
                          "виграла не найкраща акустика, а технологія, що витримала піч пайки й вийшла однаковою в мільйонах",
                          size=12.5, pad=12, fill=FILL, bold=True)
    parts.append(box)

    render("img/hist-timeline.svg", W, H, *parts, title=None)


if __name__ == "__main__":
    fig_timeline()
    print("OK: hist-timeline")

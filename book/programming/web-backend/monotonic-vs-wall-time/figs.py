# -*- coding: utf-8 -*-
"""Фігури до статті «Монотонний проти настінного часу».
Запуск із теки теми:  python figs.py   →   ./img/*.svg
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_two_clocks():
    """Показ годинника (y) проти справжнього часу, що минає (x).
    Монотонний — рівна пряма. Настінний стрибає назад під час заміру,
    тому різниця показів на відрізку A..B виходить від'ємною."""
    W, H = 860, 430
    PL, PR, PT, PB = 120, 760, 92, 340
    RX, RY = 8.0, 8.0                      # діапазони: real 0..8, reading 0..8

    def X(r): return PL + r * (PR - PL) / RX
    def Y(v): return PB - v * (PB - PT) / RY

    frags = []
    # осі
    frags.append(arrow(PL, PB, PR + 14, PB, color=INK, sw=1.8))
    frags.append(arrow(PL, PB, PL, PT - 14, color=INK, sw=1.8))
    frags.append(text((PL + PR) / 2, PB + 46, "справжній час, що минає →",
                      size=14, color=MUTED))
    frags.append(text(PL - 8, PT - 20, "показ годинника ↑", size=14,
                      color=MUTED, anchor="start"))

    # монотонний: пряма 0..8
    frags.append(line(X(0), Y(0), X(8), Y(8), color=FIELD, sw=3))
    frags.append(text(X(7.05), Y(7.4), "монотонний", size=14, color=FIELD,
                      bold=True, anchor="middle"))

    # настінний: росте до real=5, крок −5 назад, далі росте
    frags.append(line(X(0), Y(0), X(5), Y(5), color=POS, sw=3))
    frags.append(line(X(5), Y(5), X(5), Y(0), color=POS, sw=2, dash="5,4"))
    frags.append(line(X(5), Y(0), X(8), Y(3), color=POS, sw=3))
    frags.append(text(X(5.15), Y(2.0), "NTP-крок назад", size=13, color=POS,
                      anchor="start"))
    frags.append(text(X(7.15), Y(2.55), "настінний", size=14, color=POS,
                      bold=True, anchor="middle"))

    # вертикальні напрямні заміру A=4, B=6
    for r, lab in ((4.0, "A: старт"), (6.0, "B: кінець")):
        frags.append(line(X(r), PB, X(r), PT - 6, color=MUTED, sw=1.2, dash="3,4"))
        frags.append(text(X(r), PB + 22, lab, size=13, color=INK))
    # точки показів
    frags.append(circle(X(4), Y(4), 4.5, fill=INK, stroke=INK))       # спільний старт
    frags.append(circle(X(6), Y(6), 4.5, fill=FIELD, stroke=FIELD))   # монотонний кінець
    frags.append(circle(X(6), Y(1), 4.5, fill=POS, stroke=POS))       # настінний кінець

    # підсумкові плашки у вільному лівому-верхньому куті
    b1, _, _ = textbox(250, 120, "монотонний:  Δ = 6 − 4 = +2  ✓",
                       size=14, color=FIELD, bold=True, fill="#eafaf1",
                       stroke=FIELD, min_w=250)
    b2, _, _ = textbox(250, 158, "настінний:  Δ = 1 − 4 = −3  ✗",
                       size=14, color=POS, bold=True, fill="#fdecea",
                       stroke=POS, min_w=250)
    frags.append(b1)
    frags.append(b2)

    render(os.path.join(OUT, "two-clocks.svg"), W, H, *frags,
           title="Замір тривалості: настінний годинник може крокнути назад")


def fig_which_clock():
    """Дві колонки: тривалість → монотонний; момент за календарем → настінний."""
    W, H = 880, 476
    frags = []

    # банер із питанням-розв'язком
    frags.append(fitbox(70, 48, 740, 52,
                        "«Скільки минуло?»  →  монотонний\n"
                        "«Котра зараз за календарем?»  →  настінний",
                        size=16, bold=True, fill="#f4f6f8", stroke=LINE))

    cols = [
        dict(x=64, stroke=FIELD, fill="#eafaf1", head="Монотонний — міряй ТРИВАЛІСТЬ",
             hc=FIELD,
             items=["• таймаути й бюджет часу",
                    "• паузи між повторами (бекоф)",
                    "• вікна обмеження швидкості",
                    "• заміри латентності для метрик",
                    "• «мине 30 с» усередині процесу"],
             foot="локальний, не переживає рестарт —\nміж машинами беззмістовний"),
        dict(x=456, stroke=POS, fill="#fdecea", head="Настінний — фіксуй МОМЕНТ за календарем",
             hc=POS,
             items=["• коли спливає сесія / TTL",
                    "• поле exp у JWT-токені",
                    "• cron «щодня о 3:00»",
                    "• «підписка до 1 серпня»",
                    "• дата події в аудит-лозі"],
             foot="переживає рестарт, летить між машинами —\nале його підводять NTP та адмін"),
    ]
    CW, CY, CH = 360, 122, 286
    for c in cols:
        x = c["x"]
        frags.append(rect(x, CY, CW, CH, fill=c["fill"], stroke=c["stroke"], sw=2, rx=10))
        frags.append(fitbox(x + 12, CY + 12, CW - 24, 40, c["head"],
                            size=15, bold=True, color=c["hc"], fill=c["fill"],
                            stroke=c["fill"], sw=0))
        frags.append(mtext(x + 24, CY + 92, c["items"], size=15, color=INK,
                           anchor="start", lh=1.62))
        frags.append(fitbox(x + 12, CY + CH - 54, CW - 24, 44, c["foot"],
                            size=12, color=MUTED, fill="#ffffff", stroke=c["stroke"], sw=1))

    render(os.path.join(OUT, "which-clock.svg"), W, H, *frags,
           title="Який годинник для якої роботи")


def fig_suspend():
    """Дві родини монотонних лічильників на сні машини: один спиняється разом
    із нею, другий рахує далі. Під графіком — які виклики до якої родини."""
    W, H = 940, 560
    PL, PR, PT, PB = 96, 856, 96, 312
    RX, RY = 10.0, 8.0

    def X(r): return PL + r * (PR - PL) / RX
    def Y(v): return PB - v * (PB - PT) / RY

    frags = []

    # смуга сну
    frags.append(rect(X(4), PT - 4, X(7) - X(4), PB - PT + 4,
                      fill="#eef0f3", stroke="#d7dbe0", sw=1, rx=4))
    frags.append(text((X(4) + X(7)) / 2, PT - 14, "машина спить (suspend)",
                      size=14, color=MUTED))

    # осі
    frags.append(arrow(PL, PB, PR + 16, PB, color=INK, sw=1.8))
    frags.append(arrow(PL, PB, PL, PT - 34, color=INK, sw=1.8))
    frags.append(text((PL + PR) / 2, PB + 44, "справжній час, що минає →",
                      size=14, color=MUTED))
    frags.append(text(PL - 10, PT - 44, "показ лічильника ↑", size=14,
                      color=MUTED, anchor="start"))

    # рахує й уві сні: пряма 0..8
    frags.append(line(X(0), Y(0), X(10), Y(8), color=FIELD, sw=3))
    frags.append(text(X(2.6), Y(2.9), "рахує й уві сні", size=14, color=FIELD,
                      bold=True, anchor="start"))

    # спиняється: росте до 4, поличка до 7, далі знову росте
    frags.append(line(X(0), Y(0), X(4), Y(3.2), color=NEG, sw=3))
    frags.append(line(X(4), Y(3.2), X(7), Y(3.2), color=NEG, sw=3))
    frags.append(line(X(7), Y(3.2), X(10), Y(5.6), color=NEG, sw=3))
    frags.append(text((X(4) + X(7)) / 2, Y(3.2) + 26, "спинився разом із машиною",
                      size=14, color=NEG, bold=True))

    # прогалина праворуч
    frags.append(line(X(9.6), Y(5.28), X(9.6), Y(7.68), color=MUTED, sw=1.4, dash="4,4"))
    b, _, _ = textbox(X(6.4), Y(1.15), "прогалина = час, який машина проспала",
                      size=13, color=MUTED, fill="#ffffff", stroke="#d7dbe0")
    frags.append(b)

    # легенда: хто в якій родині
    CY, CH = 366, 168
    cols = [
        dict(x=48, w=418, stroke=NEG, fill="#eaf0fd",
             head="Спиняється разом із машиною",
             hc=NEG,
             items=["Linux:  CLOCK_MONOTONIC",
                    "macOS:  CLOCK_UPTIME_RAW, mach_absolute_time",
                    "Windows:  QueryUnbiasedInterruptTime",
                    "Swift:  SuspendingClock"]),
        dict(x=486, w=418, stroke=FIELD, fill="#eafaf1",
             head="Рахує й уві сні",
             hc=FIELD,
             items=["Linux:  CLOCK_BOOTTIME",
                    "macOS:  CLOCK_MONOTONIC, mach_continuous_time",
                    "Windows:  QueryPerformanceCounter, GetTickCount64",
                    "Swift:  ContinuousClock"]),
    ]
    for c in cols:
        x, w = c["x"], c["w"]
        frags.append(rect(x, CY, w, CH, fill=c["fill"], stroke=c["stroke"], sw=2, rx=10))
        frags.append(fitbox(x + 12, CY + 12, w - 24, 34, c["head"],
                            size=15, bold=True, color=c["hc"], fill=c["fill"],
                            stroke=c["fill"], sw=0))
        frags.append(mtext(x + 22, CY + 78, c["items"], size=13, color=INK,
                           anchor="start", lh=1.65))

    render(os.path.join(OUT, "clocks-suspend.svg"), W, H, *frags,
           title="Чи тікає монотонний лічильник, поки машина спить")


def fig_clock_history():
    """Вертикальна стрічка подій: як настінний годинник став рухомим і скільки
    разів індустрія платила, поки монотонний не став окремою сутністю."""
    ENTRIES = [
        ("1971", MUTED, "#f4f6f8",
         ["Unix: time() рахує 1/60 секунди від 1 січня 1971 у 32 бітах.",
          "Годинник один — переставляти його нікому, крім оператора."]),
        ("1985", POS, "#fdecea",
         ["RFC 958, Девід Міллз: NTP підганяє годинник темпом",
          "або миттєвим стрибком. Настінний час став рухомим."]),
        ("1993—2001", FIELD, "#eafaf1",
         ["POSIX: clock_gettime із реалтайм-розширень, далі CLOCK_MONOTONIC",
          "— але як необов'язкова опція реалізації."]),
        ("2004", FIELD, "#eafaf1",
         ["Java 5: System.nanoTime() поруч із currentTimeMillis(),",
          "з довідкою «лише для заміру тривалості»."]),
        ("2010", FIELD, "#eafaf1",
         ["C++, документ N3128: monotonic_clock замінено на steady_clock",
          "— «не йде назад» замало, треба «йде рівно й не підводиться»."]),
        ("17.12.2012", FIELD, "#eafaf1",
         ["W3C High Resolution Time: performance.now() зобов'язаний рости",
          "монотонно, різниця двох показів не сміє бути від'ємною."]),
        ("30.06.2012", POS, "#fdecea",
         ["Високосна секунда: ядро Linux не оновило зсув таймерів —",
          "очікування спливали миттєво. Reddit, Mozilla, Qantas."]),
        ("01.01.2017", POS, "#fdecea",
         ["Cloudflare: заміряний час відповіді став від'ємним, вибір",
          "резолвера впав у паніку — 0.2% DNS-запитів не пройшло."]),
        ("24.08.2017", FIELD, "#eafaf1",
         ["Go 1.9: time.Time несе монотонний відлік усередині,",
          "віднімання само бере його, а не календарний показ."]),
        ("07.04.2022", FIELD, "#eafaf1",
         ["Rust 1.60: віднімання Instant насичується до нуля замість",
          "паніки — бо монотонність порушує вже саме залізо."]),
    ]

    W = 820
    AX = 208
    TOP, STEP = 138, 76
    N = len(ENTRIES)
    H = TOP + (N - 1) * STEP + 62

    frags = []
    frags.append(text(W / 2, 34, "Як два годинники розділилися: ланцюг подій",
                      size=17, bold=True, color=INK))

    # легенда
    chips = [("передісторія", MUTED, "#f4f6f8"),
             ("збій, за який заплатили", POS, "#fdecea"),
             ("відповідь мови чи стандарту", FIELD, "#eafaf1")]
    ws = [text_width(lab, 13, True) + 26 for lab, _, _ in chips]
    gap = 18
    x = (W - (sum(ws) + gap * (len(chips) - 1))) / 2
    for (lab, c, f), w in zip(chips, ws):
        frags.append(rect(x, 56, w, 28, fill=f, stroke=c, sw=1.4, rx=8))
        frags.append(text(x + w / 2, 75, lab, size=13, color=c, bold=True))
        x += w + gap

    # вісь часу
    frags.append(line(AX, TOP - 36, AX, TOP + (N - 1) * STEP + 36,
                      color="#c8ccd2", sw=3))

    size, pad = 14, 10
    for i, (yr, c, f, lines) in enumerate(ENTRIES):
        y = TOP + i * STEP
        frags.append(text(AX - 28, y + 5, yr, size=14, color=c, bold=True,
                          anchor="end"))
        frags.append(circle(AX, y, 6.5, fill=f, stroke=c, sw=2.4))
        bw = max(text_width(ln, size) for ln in lines) + 2 * pad
        bh = len(lines) * size * 1.35 + 2 * pad
        bx = AX + 28
        frags.append(rect(bx, y - bh / 2, bw, bh, fill=f, stroke=c, sw=1.5, rx=8))
        ty = y - (len(lines) - 1) * size * 1.35 / 2 + size * 0.35
        frags.append(mtext(bx + pad, ty, lines, size=size, color=INK,
                           anchor="start", lh=1.35))

    render(os.path.join(OUT, "clock-history.svg"), W, H, *frags,
           title="Стрічка подій: як монотонний час став окремою сутністю")


if __name__ == "__main__":
    fig_two_clocks()
    fig_which_clock()
    fig_suspend()
    fig_clock_history()
    print("OK: img/two-clocks.svg, img/which-clock.svg, img/clocks-suspend.svg, "
          "img/clock-history.svg")

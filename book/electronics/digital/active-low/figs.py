# -*- coding: utf-8 -*-
"""Фігури до теми «Active-low: логіка "0 = увімкнено"» (цифрова електроніка).
Фігури теми:
  high-vs-low.svg     — один сигнал "увімкни" у двох домовленостях: active-high
                        (спокій=0, дія=стрибок угору) проти active-low (спокій=1,
                        дія=падіння вниз); підпис, де на осі напруги "активно".
  why-low-safe.svg    — active-low лінія з підтяжкою: спокій=HIGH; активна дія тягне
                        вниз; обрив дроту → підтяжка сама піднімає в пасивний HIGH
                        (збій = спокій, а не хибне спрацювання).
  mixed-polarity.svg  — один дріт "дозвіл" на active-high (EN) і active-low (EN̅) входи:
                        1 → перший увімкнено/другий вимкнено; протифаза.
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def _pullup_res(x, y0, y1, col=INK, sw=2.0):
    """Символ резистора-підтяжки (зигзаг) у вертикальному дроті між y0 (верх) і y1 (низ)."""
    out = [line(x, y0, x, y0 + 8, color=col, sw=sw)]
    n, top, bot = 6, y0 + 8, y1 - 8
    step = (bot - top) / n
    px, py = x, top
    for i in range(1, n + 1):
        nx = x + (7 if i % 2 else -7)
        ny = top + i * step
        out.append(line(px, py, nx, ny, color=col, sw=sw))
        px, py = nx, ny
    out.append(line(px, py, x, y1 - 8, color=col, sw=sw))
    out.append(line(x, y1 - 8, x, y1, color=col, sw=sw))
    return "".join(out)


# ── 1. active-high проти active-low ──────────────────────────────────────────
def high_vs_low():
    W, H = 720, 400
    p = []
    lo, hi = 300, 120          # рівні Y для LOW і HIGH
    xL, xR = 70, 440           # межі осі часу кожної діаграми
    xmid = 255                 # де відбувається подія

    def diagram(y0, title, waveform):
        out = [text((xL + xR) / 2, y0 - 78, title, size=15, bold=True)]
        base = y0
        # осі
        out.append(line(xL, base + 8, xL, base - 120, color=MUTED, sw=1.4))
        out.append(line(xL, base + 8, xR, base + 8, color=MUTED, sw=1.4))
        out.append(text(xL - 10, base - 118 + 4, "1", size=12, color=MUTED, anchor="end"))
        out.append(text(xL - 10, base + 12, "0", size=12, color=MUTED, anchor="end"))
        out.append(text(xR + 6, base + 12, "t", size=12, color=MUTED, anchor="start"))
        # межі рівнів у координатах цієї діаграми
        yHI, yLO = base - 120, base
        out.append(waveform(yHI, yLO, out))
        return out

    def wf_high(yHI, yLO, sink):
        # спокій=0 (низ), подія → стрибок угору до 1
        parts = [
            line(xL, yLO, xmid, yLO, color=FIELD, sw=3),
            line(xmid, yLO, xmid, yHI, color=FIELD, sw=3),
            line(xmid, yHI, xR, yHI, color=FIELD, sw=3),
        ]
        sink.append(text(xmid, yLO + 26, "спокій (0)", size=12, color=MUTED))
        sink.append(text((xmid + xR) / 2, yHI - 10, "активно (1)", size=12, color=FIELD, bold=True))
        sink.append('<polygon points="%.0f,%.0f %.0f,%.0f %.0f,%.0f" fill="%s"/>'
                    % (xmid - 7, yHI + 20, xmid + 7, yHI + 20, xmid, yHI + 6, FIELD))
        return "".join(parts)

    def wf_low(yHI, yLO, sink):
        # спокій=1 (верх), подія → падіння вниз до 0
        parts = [
            line(xL, yHI, xmid, yHI, color=NEG, sw=3),
            line(xmid, yHI, xmid, yLO, color=NEG, sw=3),
            line(xmid, yLO, xR, yLO, color=NEG, sw=3),
        ]
        sink.append(text((xL + xmid) / 2, yHI - 10, "спокій (1)", size=12, color=MUTED))
        sink.append(text((xmid + xR) / 2, yLO - 12, "активно (0)", size=12, color=NEG, bold=True))
        sink.append('<polygon points="%.0f,%.0f %.0f,%.0f %.0f,%.0f" fill="%s"/>'
                    % (xmid - 7, yLO - 20, xmid + 7, yLO - 20, xmid, yLO - 6, NEG))
        return "".join(parts)

    p += diagram(150, "active-high: одиниця = увімкнено", wf_high)
    p += diagram(340, "active-low: нуль = увімкнено", wf_low)

    # права колонка-підказка
    box, bw, bh = textbox(600, 240, "Змінюється\nне залізо,\nа домовленість:\nякий рівень\nвважаємо «дій».",
                          size=13, fill=FILL, stroke=MUTED)
    p.append(box)

    render(os.path.join(OUT, 'high-vs-low.svg'), W, H, *p,
           title="Один сигнал «увімкни» — дві домовленості про рівень")


# ── 2. чому нуль безпечний: підтяжка тримає спокій ───────────────────────────
def why_low_safe():
    W, H = 720, 430
    p = []
    vdd_y, gnd_y = 74, 360
    railL, railR = 90, 630
    # шини
    p.append(line(railL, vdd_y, railR, vdd_y, color=POS, sw=2.5))
    p.append(text(railL - 6, vdd_y - 8, "VDD", size=13, color=POS, anchor="start", bold=True))
    p.append(line(railL, gnd_y, railR, gnd_y, color=INK, sw=2.5))
    p.append(text(railL - 6, gnd_y + 20, "GND", size=13, color=INK, anchor="start", bold=True))

    lineY = 210            # рівень сигнальної лінії
    # три сценарії — три колонки
    def scenario(cx, headline, low_pulled, broken, hcol):
        out = [text(cx, 118, headline, size=13, bold=True, color=hcol)]
        # підтяжка від VDD до лінії
        out.append(_pullup_res(cx, vdd_y, lineY - 22, col=MUTED, sw=2))
        out.append(text(cx + 14, (vdd_y + lineY) / 2 - 6, "pull-up", size=11, color=MUTED, anchor="start"))
        # вузол лінії
        out.append(circle(cx, lineY - 22, 3.5, fill=INK, stroke=INK))
        # горизонтальний "дріт" сигналу
        out.append(line(cx - 46, lineY - 22, cx + 46, lineY - 22, color=INK, sw=2))
        # джерело (нижнє плече), що може тягнути вниз
        drv_top = lineY + 6
        if broken:
            # обрив: розрив у дроті вниз
            out.append(line(cx, lineY - 22, cx, drv_top - 6, color=INK, sw=2))
            out.append(line(cx - 8, drv_top - 4, cx + 8, drv_top - 12, color=POS, sw=2.4))
            out.append(line(cx - 8, drv_top + 2, cx + 8, drv_top - 6, color=POS, sw=2.4))
            out.append(text(cx + 14, drv_top, "обрив", size=11, color=POS, anchor="start", bold=True))
            state, scol = "лінія = HIGH", FIELD
            sub = "(підтяжка тримає\nспокій)"
        else:
            out.append(line(cx, lineY - 22, cx, gnd_y, color=(NEG if low_pulled else MUTED),
                            sw=(3 if low_pulled else 1.6),
                            dash=(None if low_pulled else "5 4")))
            if low_pulled:
                out.append(text(cx + 14, (lineY + gnd_y) / 2, "тягне ↓", size=11, color=NEG,
                                anchor="start", bold=True))
                state, scol = "лінія = LOW", NEG
                sub = "(активна дія)"
            else:
                state, scol = "лінія = HIGH", FIELD
                sub = "(спокій)"
        # мітка стану під лінією
        out.append(text(cx, lineY + 8, state, size=13, color=scol, bold=True))
        out.append(mtext(cx, lineY + 26, sub, size=11, color=MUTED))
        return out

    p += scenario(210, "Спокій", False, False, MUTED)
    p += scenario(370, "Активна дія", True, False, NEG)
    p += scenario(545, "Обрив дроту", False, True, POS)

    p.append(fitbox(40, gnd_y + 34, W - 80, 40,
                    "Збій за замовчуванням = спокій: обрив або знеструмлення лишає HIGH, "
                    "а не хибне спрацювання. Тому скидання й вибір чипа роблять активними на нулі.",
                    size=12, fill="#eefaf0", stroke=FIELD))

    render(os.path.join(OUT, 'why-low-safe.svg'), W, H, *p,
           title="Чому нуль: підтяжка тримає спокій, обрив = безпечний спокій")


# ── 3. змішані полярності працюють у протифазі ───────────────────────────────
def mixed_polarity():
    W, H = 720, 380
    p = []
    wireY = 150
    srcX = 90
    # спільний дріт "дозвіл"
    p.append(text(srcX, wireY - 22, "«дозвіл»", size=13, bold=True))
    p.append(line(srcX, wireY, 560, wireY, color=INK, sw=2.5))
    p.append(text(srcX, wireY + 22, "подаємо 1", size=12, color=FIELD, bold=True))

    # відгалуження до двох чипів
    xA, xB = 300, 480
    for x in (xA, xB):
        p.append(circle(x, wireY, 3.5, fill=INK, stroke=INK))
        p.append(line(x, wireY, x, wireY + 40, color=INK, sw=2))

    # чип A: active-high EN
    ax, ay, aw, ah = xA - 70, wireY + 40, 140, 74
    p.append(rect(ax, ay, aw, ah, fill=FILL, stroke=LINE))
    p.append(text(xA, ay + 20, "Чіп A", size=13, bold=True))
    p.append(text(xA, ay + 40, "EN (active-high)", size=12, color=INK))
    p.append(text(xA, ay + 60, "1 → УВІМКНЕНО", size=12, color=FIELD, bold=True))

    # чип B: active-low EN̅
    bx, by, bw, bh = xB - 70, wireY + 40, 140, 74
    p.append(rect(bx, by, bw, bh, fill=FILL, stroke=LINE))
    p.append(text(xB, by + 20, "Чіп B", size=13, bold=True))
    p.append(text(xB, by + 40, "EN̅ (active-low)", size=12, color=INK))
    p.append(text(xB, by + 60, "1 → ВИМКНЕНО", size=12, color=POS, bold=True))

    p.append(fitbox(40, 300, W - 80, 44,
                    "Один дріт — дві полярності: подаєш 1, і A увімкнено, а B вимкнено; "
                    "подаєш 0 — навпаки. Разом вони не працюють ніколи. Полярність кожної "
                    "ніжки погоджують свідомо: інвертором або чіткою обробкою в коді.",
                    size=12, fill="#fdecea", stroke=POS))

    render(os.path.join(OUT, 'mixed-polarity.svg'), W, H, *p,
           title="Змішані полярності на одному дроті — протифаза")


if __name__ == "__main__":
    high_vs_low()
    why_low_safe()
    mixed_polarity()
    print("OK: figures written to", OUT)

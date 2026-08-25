# -*- coding: utf-8 -*-
"""Фігури до теми «Тіньовий регістр».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).
Рамки з текстом — лише через textbox()/fitbox() (§5). Підпис несе .md."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Дві половини: видимий регістр і тіньова копія, обмін на межі ──────────
def fig_two_halves():
    W, H = 720, 340
    p = [rect(0, 0, W, H, fill=BG, stroke=BG)]

    fx, fy, fw, fh = 60, 78, 250, 74
    p.append(fitbox(fx, fy, fw, fh,
                    "ВИДИМИЙ РЕГІСТР\nсюди пише процесор будь-коли",
                    size=15, bold=True, fill="#eaf0fd", stroke=NEG))
    p.append(text(fx + fw / 2, fy - 14, "процесор пише сюди", size=13, color=NEG))
    p.append(arrow(fx + fw / 2, fy - 9, fx + fw / 2, fy - 2, color=NEG))

    sx, sy = 60, 214
    p.append(fitbox(sx, sy, fw, fh,
                    "ТІНЬОВА КОПІЯ\nсюди дивиться апаратура",
                    size=15, bold=True, fill="#eafaf0", stroke=FIELD))
    p.append(text(sx + fw / 2, sy + fh + 22, "апаратура читає звідси", size=13, color=FIELD))
    p.append(arrow(sx + fw / 2, sy + fh + 3, sx + fw / 2, sy + fh + 10, color=FIELD))

    mx = fx + fw / 2
    midy = (fy + fh + sy) / 2
    p.append(line(mx, fy + fh, mx, sy, color=INK, sw=2.4))
    p.append(arrow(mx, fy + fh + 6, mx, sy - 6, color=INK, sw=2.4))
    b, bw, bh = textbox(mx + 120, midy, "перенос\nу мить події",
                        size=14, bold=True, fill="#fdf6ec", stroke=POS)
    p.append(line(mx, midy, mx + 120 - bw / 2, midy, color=POS, sw=1.6, dash="4 3"))
    p.append(b)

    ex, ew = 470, 200
    p.append(fitbox(ex, 100, ew, 60, "МЕЖА ПЕРІОДУ\n(подія оновлення)",
                    size=15, bold=True, fill=FILL, stroke=LINE))
    p.append(arrow(ex + ew / 2, 160, ex + ew / 2, 198, color=POS, sw=2))
    p.append(fitbox(ex, 198, ew, 78,
                    "лише тут копія разом\nбере нове значення —\nне посеред роботи",
                    size=14, fill="#fdf6ec", stroke=POS))

    render(os.path.join(IMG, "two-halves.svg"), W, H, *p)


# ── 2. Розрив без буфера проти чистого переходу з тіньовим регістром ─────────
def pwm_row(x, y, w, glitch):
    """Один рядок ШІМ: n періодів, у другому періоді процесор змінює ширину.
    glitch=True — нове значення діє миттєво (рваний імпульс); False — з межі періоду."""
    out = []
    top, bot = y, y + 62
    n = 4
    pw = w / n
    lo, hi = 0.32, 0.70              # стара й нова ширина (частка періоду)
    write_at = x + 1.5 * pw          # запис припадає на середину 2-го періоду
    col_f = NEG if glitch else FIELD
    col_bg = "#eaf0fd" if glitch else "#eafaf0"
    out.append(line(x, bot, x + w, bot, color=MUTED, sw=1))
    for i in range(n):
        x0 = x + i * pw
        out.append(line(x0, top - 6, x0, bot, color=MUTED, sw=0.8, dash="2 3"))
        if i < 1:
            wpx = pw * lo               # ще стара ширина
        elif i == 1 and glitch:
            wpx = write_at - x0         # без буфера: імпульс обірваний записом посеред періоду
        elif i == 1:
            wpx = pw * lo               # з тінню: 2-й період ще старий
        else:
            wpx = pw * hi               # усталена нова ширина
        if wpx > 0:
            out.append(rect(x0, top + 8, wpx, bot - top - 8, fill=col_bg, stroke=col_f, sw=1.8))
    out.append(line(x + w, top - 6, x + w, bot, color=MUTED, sw=0.8, dash="2 3"))
    out.append(line(write_at, top - 14, write_at, bot, color=INK, sw=1.4, dash="4 3"))
    out.append(text(write_at, top - 18, "процесор записав нове", size=12, color=INK))
    return out


def fig_pwm_glitch():
    W, H = 720, 400
    p = [rect(0, 0, W, H, fill=BG, stroke=BG)]

    p.append(text(60, 44, "БЕЗ буфера: значення діє миттєво", size=15, bold=True, color=NEG, anchor="start"))
    p.extend(pwm_row(60, 68, 600, glitch=True))
    p.append(fitbox(60, 156, 600, 36,
                    "запис припав на середину періоду → один імпульс вийшов рваний (глітч)",
                    size=13, fill="#eaf0fd", stroke=NEG))

    p.append(text(60, 248, "З тіньовим регістром: перенос лише на межі", size=15, bold=True, color=FIELD, anchor="start"))
    p.extend(pwm_row(60, 272, 600, glitch=False))
    p.append(fitbox(60, 360, 600, 36,
                    "запис чекає в тіні; апаратура бере його з наступної цілої межі → кожен імпульс цілий",
                    size=13, fill="#eafaf0", stroke=FIELD))

    render(os.path.join(IMG, "pwm-glitch.svg"), W, H, *p)


# ── 3. Тіньовий банк регістрів під швидкий вхід у переривання ────────────────
def fig_context_bank():
    W, H = 720, 320
    p = [rect(0, 0, W, H, fill=BG, stroke=BG)]

    ax, ay, aw, ah = 60, 96, 230, 118
    p.append(rect(ax, ay, aw, ah, fill="#eaf0fd", stroke=NEG, sw=2))
    p.append(text(ax + aw / 2, ay - 12, "РОБОЧИЙ БАНК", size=15, bold=True, color=NEG))
    for i, nm in enumerate(["R0", "R1", "R2", "…"]):
        yy = ay + 28 + i * 24
        p.append(text(ax + 24, yy, nm, size=13, color=INK, anchor="start"))
        p.append(text(ax + aw - 20, yy, "зайнятий програмою", size=12, color=MUTED, anchor="end"))

    bx = 430
    p.append(rect(bx, ay, aw, ah, fill="#eafaf0", stroke=FIELD, sw=2))
    p.append(text(bx + aw / 2, ay - 12, "ТІНЬОВИЙ БАНК", size=15, bold=True, color=FIELD))
    for i, nm in enumerate(["R0'", "R1'", "R2'", "…"]):
        yy = ay + 28 + i * 24
        p.append(text(bx + 24, yy, nm, size=13, color=INK, anchor="start"))
        p.append(text(bx + aw - 20, yy, "чистий, напоготові", size=12, color=MUTED, anchor="end"))

    my = ay + ah / 2
    p.append(line(ax + aw, my, bx, my, color=INK, sw=2.2))
    p.append(arrow(ax + aw + 6, my, bx - 6, my, color=INK, sw=2.2))
    b, bw, bh = textbox((ax + aw + bx) / 2, my - 46, "переривання:\nбанки міняються\nза 1 такт",
                        size=13, bold=True, fill="#fdf6ec", stroke=POS)
    p.append(line((ax + aw + bx) / 2, my - 46 + bh / 2, (ax + aw + bx) / 2, my,
                  color=POS, sw=1.6, dash="4 3"))
    p.append(b)

    p.append(fitbox(60, 252, 600, 44,
                    "перерваний код лишається недоторканим у своєму банку; обробник одразу працює в чистому — "
                    "нема куди зберігати регістри в стек",
                    size=13, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, "context-bank.svg"), W, H, *p)


if __name__ == "__main__":
    fig_two_halves()
    fig_pwm_glitch()
    fig_context_bank()
    print("OK: figures written to", IMG)

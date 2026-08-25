# -*- coding: utf-8 -*-
"""Фігури до теми «Аналогове відео» (FPV).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def polyline(pts, color=INK, sw=2.4):
    d = " ".join("%.1f,%.1f" % p for p in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"/>' % (d, color, sw))


def hline(x1, x2, y, color=MUTED, sw=1.0, dash="5,4"):
    return line(x1, y, x2, y, color=color, sw=sw, dash=dash)


# ── фіг. 1: один рядок як осцилограма ───────────────────────────────────────
def fig_line_waveform():
    W, H = 760, 360
    x0, x1 = 70, 690
    y_white, y_black, y_sync = 110, 250, 300
    # рівні
    parts = [
        hline(x0, x1, y_white), text(x1 + 6, y_white + 4, "білий", size=11, color=MUTED, anchor="start"),
        hline(x0, x1, y_black), text(x1 + 6, y_black + 4, "чорний", size=11, color=MUTED, anchor="start"),
        hline(x0, x1, y_sync), text(x1 + 6, y_sync + 4, "синхро", size=11, color=MUTED, anchor="start"),
    ]
    # сигнал: чорний → синхро(вниз) → гасіння(чорний) → активне відео(крива) → чорний
    pts = [(x0, y_black), (90, y_black), (90, y_sync), (140, y_sync),
           (140, y_black), (175, y_black)]
    # активне відео — плавна яскравісна крива
    ax0, ax1 = 175, 640
    n = 90
    for i in range(n + 1):
        t = i / n
        x = ax0 + (ax1 - ax0) * t
        # кілька «деталей картинки» уздовж рядка
        v = (0.5 + 0.42 * math.sin(t * 9.0) * math.exp(-((t - 0.45) ** 2) / 0.12)
             + 0.18 * math.sin(t * 3.0 + 0.6))
        v = max(0.02, min(0.98, v))
        y = y_black - v * (y_black - y_white)
        pts.append((x, y))
    pts += [(ax1, y_black), (x1, y_black)]
    parts.append(polyline(pts, color=NEG, sw=2.4))
    # підписи зон
    parts += [
        text(115, y_sync + 22, "синхро", size=11, color=POS, bold=True),
        text(157, y_black + 22, "гасіння", size=10, color=MUTED),
        text((ax0 + ax1) / 2, y_white - 18, "активне відео = яскравість уздовж рядка",
             size=12, color=NEG, bold=True),
        text((ax0 + ax1) / 2, H - 18, "час уздовж рядка →", size=11, color=MUTED),
        text(x0 - 6, y_white - 16, "напруга", size=11, color=MUTED, anchor="end", bold=True),
    ]
    render(os.path.join(IMG, "line-waveform.svg"), W, H, *parts)


# ── фіг. 2: із синхро / без синхро ──────────────────────────────────────────
def fig_sync():
    W, H = 760, 360
    # дві панелі: ліворуч рівно, праворуч «їде»
    def screen( ox, oy, w, h, shift):
        out = [rect(ox, oy, w, h, fill=BG, stroke=LINE, sw=1.8)]
        rows = 9
        for r in range(rows):
            y = oy + (r + 0.5) * h / rows
            dx = 0 if shift == 0 else ((r * shift) % w)
            # рядок «розрізаний» зсувом — малюємо двома відрізками
            out.append(line(ox + dx, y, ox + w, y, color=NEG, sw=3))
            if dx > 0:
                out.append(line(ox, y, ox + dx, y, color=POS, sw=3))
        return out
    lx, rx, oy, w, h = 70, 430, 90, 260, 200
    parts = []
    parts += screen(lx, oy, w, h, 0)
    parts += screen(rx, oy, w, h, 26)
    parts += [
        text(lx + w / 2, oy - 16, "із синхро — рядки на місці", size=13, color=FIELD, bold=True),
        text(rx + w / 2, oy - 16, "без синхро — картинка «їде»", size=13, color=POS, bold=True),
        text(lx + w / 2, oy + h + 28, "H-синхро тримає рядок,", size=11, color=MUTED),
        text(lx + w / 2, oy + h + 44, "V-синхро — початок кадру", size=11, color=MUTED),
        text(rx + w / 2, oy + h + 28, "розгортка втратила такт —", size=11, color=MUTED),
        text(rx + w / 2, oy + h + 44, "рядки повзуть навскіс", size=11, color=MUTED),
    ]
    render(os.path.join(IMG, "sync.svg"), W, H, *parts)


# ── фіг. 3: черезрядковість ─────────────────────────────────────────────────
def fig_interlace():
    W, H = 760, 360
    oy, h = 80, 210
    rows = 10
    def field(ox, w, parity, label, color):
        out = [text(ox + w / 2, oy - 14, label, size=12, color=color, bold=True)]
        for r in range(rows):
            y = oy + (r + 0.5) * h / rows
            c = color if (r % 2 == parity) else "#dfe3e8"
            sw = 3 if (r % 2 == parity) else 1.4
            out.append(line(ox, y, ox + w, y, color=c, sw=sw))
        out.append(rect(ox, oy, w, h, fill="none", stroke=LINE, sw=1.4))
        return out
    w = 180
    f1x, f2x, sumx = 60, 300, 540
    parts = []
    parts += field(f1x, w, 0, "поле 1 — непарні", POS)
    parts += field(f2x, w, 1, "поле 2 — парні", NEG)
    # сума = повний кадр
    out = [text(sumx + w / 2, oy - 14, "кадр", size=12, color=FIELD, bold=True)]
    for r in range(rows):
        y = oy + (r + 0.5) * h / rows
        out.append(line(sumx, y, sumx + w, y, color=INK, sw=2.6))
    out.append(rect(sumx, oy, w, h, fill="none", stroke=LINE, sw=1.4))
    parts += out
    parts += [
        text((f2x + sumx) / 2 + w / 2 - 18, oy + h / 2 + 5, "=", size=26, color=MUTED, bold=True),
        text(W / 2, oy + h + 34, "поля міняються вдвічі частіше за кадри — рух плавний за половини смуги",
             size=11, color=MUTED),
        text(W / 2, oy + h + 54, "NTSC: 525 рядків, ~30 кадрів    ·    PAL: 625 рядків, 25 кадрів",
             size=11, color=INK, bold=True),
    ]
    render(os.path.join(IMG, "interlace.svg"), W, H, *parts)


# ── фіг. 4: аналог проти цифри ──────────────────────────────────────────────
def fig_analog_vs_digital():
    W, H = 760, 380
    x0, x1 = 80, 560
    y_top, y_bot = 90, 250
    parts = [
        text((x0 + x1) / 2, 40, "якість картинки в міру слабшання сигналу", size=13, color=MUTED),
        line(x0, y_bot, x1, y_bot, color=LINE, sw=1.5),
        line(x0, y_top, x0, y_bot, color=LINE, sw=1.5),
        text((x0 + x1) / 2, y_bot + 26, "сигнал слабшає →", size=11, color=MUTED),
        text(x0 - 8, y_top - 6, "якість", size=11, color=MUTED, anchor="end", bold=True),
    ]
    n = 80
    # аналог — плавний спад
    ap = []
    for i in range(n + 1):
        t = i / n
        v = 1.0 - 0.85 * t ** 1.7
        ap.append((x0 + (x1 - x0) * t, y_bot - v * (y_bot - y_top)))
    parts.append(polyline(ap, color=FIELD, sw=2.8))
    # цифра — плато, тоді обрив
    dp = []
    knee = 0.62
    for i in range(n + 1):
        t = i / n
        if t < knee:
            v = 0.98
        else:
            v = max(0.0, 0.98 - (t - knee) / 0.10)
        dp.append((x0 + (x1 - x0) * t, y_bot - v * (y_bot - y_top)))
    parts.append(polyline(dp, color=POS, sw=2.8))
    parts += [
        text(x1 + 6, y_top + 4, "цифра", size=11, color=POS, anchor="start", bold=True),
        text(x1 + 6, y_top + 70, "аналог", size=11, color=FIELD, anchor="start", bold=True),
        line(x0 + (x1 - x0) * knee, y_top - 4, x0 + (x1 - x0) * knee, y_bot, color=POS, sw=1.0, dash="4,4"),
        text(x0 + (x1 - x0) * knee, y_top - 12, "поріг → обрив", size=10, color=POS),
    ]
    # дві підписи-картки
    b1 = fitbox(80, y_bot + 50, 320, 56,
                "Аналог: майже нуль затримки;\nслабне → «сніг», та видно — попередження",
                size=11, fill="#eafaf1", stroke=FIELD, color=INK)
    b2 = fitbox(420, y_bot + 50, 260, 56,
                "Цифра: чіткіше, але лаг\n(кодування→передача→декодування) і різкий обрив",
                size=11, fill="#fdeceb", stroke=POS, color=INK)
    parts += [b1, b2]
    render(os.path.join(IMG, "analog-vs-digital.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_line_waveform()
    fig_sync()
    fig_interlace()
    fig_analog_vs_digital()
    print("OK: 4 SVG у", IMG)

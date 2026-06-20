# -*- coding: utf-8 -*-
"""Фігури для вставки comp-wall-adapter.md (мережевий адаптер зсередини).
svgkit імпортуємо зі scripts/, не переписуємо (AUTHORING §5).

    python figs.py    # вивід у ./img/
"""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *  # noqa: E402,F403

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


def fig_safety_zones():
    """Дві зони адаптера й бар'єр між ними: гаряча первинна (325 В) ліворуч,
    холодна вторинна (5 В) праворуч; фізична щілина в платі по центру;
    бар'єр перетинають лише оптопара (світло) і Y-конденсатор (шум)."""
    W, H = 900, 500
    f = []

    bx = W / 2  # лінія бар'єра
    zone_bottom = 442  # низ кольорових зон

    # ── фон двох зон ──
    f.append(rect(20, 70, bx - 20 - 14, zone_bottom - 70, fill="#fdecea", stroke=POS, sw=2))
    f.append(rect(bx + 14, 70, W - 20 - (bx + 14), zone_bottom - 70, fill="#e9f7ef", stroke=FIELD, sw=2))

    # ── фізична щілина в платі (наскрізний проріз) ──
    f.append(rect(bx - 13, 70, 26, zone_bottom - 70, fill="#ffffff", stroke=MUTED, sw=2, rx=4))
    f.append(line(bx, 78, bx, zone_bottom - 8, color=MUTED, sw=2, dash="6 6"))
    f.append(text(bx, zone_bottom + 28, "проріз у платі + трансформатор = бар'єр", size=12, color=MUTED))

    # ── заголовки зон ──
    f.append(text((20 + bx - 14) / 2, 56, "ПЕРВИННА — небезпечна", size=15, color=POS, bold=True))
    f.append(text((bx + 14 + W - 20) / 2, 56, "ВТОРИННА — безпечна", size=15, color=FIELD, bold=True))

    # ── вузли первинної (гарячої) ──
    cxL = (20 + bx - 14) / 2
    b, w, h = textbox(cxL, 120, "мережа 110–230 В\n→ міст → 325 В", size=13,
                      fill="#ffffff", stroke=POS, sw=1.8)
    f.append(b)
    f.append(plus(cxL, 168, r=11))
    f.append(text(cxL, 196, "325 В пост.", size=13, color=POS, bold=True))
    b, w, h = textbox(cxL, 250, "контролер + ключ\n(MOSFET)", size=13,
                      fill="#ffffff", stroke=POS, sw=1.8)
    f.append(b)
    f.append(text(cxL, 320, "дотик = смерть", size=14, color=POS, bold=True))

    # ── вузли вторинної (холодної) ──
    cxR = (bx + 14 + W - 20) / 2
    b, w, h = textbox(cxR, 120, "випрямляч\n+ конденсатор", size=13,
                      fill="#ffffff", stroke=FIELD, sw=1.8)
    f.append(b)
    f.append(minus(cxR - 30, 168, r=11))
    f.append(plus(cxR + 30, 168, r=11))
    f.append(text(cxR, 196, "5 В пост.", size=13, color=FIELD, bold=True))
    b, w, h = textbox(cxR, 250, "роз'єм USB\n(пальці, кабель)", size=13,
                      fill="#ffffff", stroke=FIELD, sw=1.8)
    f.append(b)
    f.append(text(cxR, 320, "безпечно для рук", size=14, color=FIELD, bold=True))

    # ── два містки через бар'єр ──
    yb1, yb2 = 364, 410
    # оптопара
    f.append(line(cxL, yb1, cxR, yb1, color=NEG, sw=2.4))
    bb, ww, hh = textbox(bx, yb1, "оптопара\n(світло)", size=12,
                         fill="#eaf0fd", stroke=NEG, sw=1.8)
    f.append(bb)
    # Y-конденсатор
    f.append(line(cxL, yb2, cxR, yb2, color=INK, sw=2.4, dash="4 4"))
    bb, ww, hh = textbox(bx, yb2, "Y-конд.\n(тільки шум)", size=12,
                         fill="#fff7e6", stroke="#b8860b", sw=1.8)
    f.append(bb)

    return render(os.path.join(IMG, "safety-zones.svg"), W, H, *f)


if __name__ == "__main__":
    out = fig_safety_zones()
    print("written:", out)

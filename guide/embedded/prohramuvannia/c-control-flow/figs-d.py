# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def diamond(cx, cy, w, h, s, size=13, fill="#eef7f0", stroke=FIELD, sw=2, color=INK):
    pts = "%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" % (
        cx, cy - h / 2, cx + w / 2, cy, cx, cy + h / 2, cx - w / 2, cy)
    body = ('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>'
            % (pts, fill, stroke, sw))
    fs = fit_font(s, w * 0.72, size, bold=True)
    body += text(cx, cy + fs * 0.35, s, size=fs, color=color, bold=True)
    return body


# ── Фігура 1: дві стратегії компіляції switch ────────────────────────────────
def fig_switch_dispatch():
    W, H = 760, 470
    parts = [text(W / 2, 26, "Як компілятор розкладає switch: дві стратегії", size=16, bold=True)]

    # ── ЛІВА КОЛОНКА: щільні мітки → таблиця переходів ──
    lx = 30
    parts.append(text(lx + 165, 60, "мітки щільні (0,1,2,3)", size=13, bold=True, color=FIELD))
    parts.append(fitbox(lx + 60, 74, 210, 34, "case 0,1,2,3 поспіль", size=12,
                        fill="#f4f6f8", stroke=MUTED))
    # index box
    parts.append(fitbox(lx + 95, 122, 140, 32, "value  →  індекс", size=12,
                        fill="#eef7f0", stroke=FIELD, bold=True))
    parts.append(arrow(lx + 165, 108, lx + 165, 122))
    # jump table
    ty = 168
    cells = ["→ code0", "→ code1", "→ code2", "→ code3"]
    cw = 78
    tx0 = lx + 165 - (len(cells) * cw) / 2
    parts.append(arrow(lx + 165, 154, lx + 165, ty - 6))
    parts.append(text(lx + 165, ty - 12, "таблиця адрес", size=11, color=MUTED))
    for i, c in enumerate(cells):
        parts.append(fitbox(tx0 + i * cw, ty, cw - 4, 34, c, size=11,
                            fill="#eef7f0", stroke=FIELD))
    # one lookup arrow
    parts.append(arrow(tx0 + 2 * cw + cw / 2 - 2, ty + 34, tx0 + 2 * cw + cw / 2 - 2, ty + 60))
    parts.append(fitbox(lx + 60, ty + 60, 210, 40,
                        "один перехід за адресою\nодин крок — байдуже скільки міток",
                        size=11, fill="#fff", stroke=FIELD, color=FIELD, bold=True))

    # ── ПРАВА КОЛОНКА: розкидані мітки → дерево порівнянь ──
    rx = 430
    parts.append(text(rx + 165, 60, "мітки розкидані (1, 40, 9000)", size=13, bold=True, color=NEG))
    parts.append(fitbox(rx + 60, 74, 210, 34, "case 1, 40, 9000 …", size=12,
                        fill="#f4f6f8", stroke=MUTED))
    # comparison tree
    root_y = 132
    parts.append(diamond(rx + 165, root_y, 150, 52, "v < 40 ?", size=12, fill="#fdecea", stroke=NEG))
    parts.append(arrow(rx + 165, 108, rx + 165, root_y - 26))
    # left child
    lcx, rcx = rx + 70, rx + 262
    ch_y = 232
    parts.append(diamond(lcx, ch_y, 120, 48, "v == 1 ?", size=11, fill="#fdecea", stroke=NEG))
    parts.append(diamond(rcx, ch_y, 130, 48, "v == 40 ?", size=11, fill="#fdecea", stroke=NEG))
    parts.append(arrow(rx + 140, root_y + 26, lcx + 14, ch_y - 24))
    parts.append(arrow(rx + 190, root_y + 26, rcx - 14, ch_y - 24))
    parts.append(text(rx + 96, root_y + 44, "так", size=10, color=FIELD, bold=True))
    parts.append(text(rx + 232, root_y + 44, "ні", size=10, color=POS, bold=True))
    # leaves
    leaf_y = 312
    parts.append(fitbox(lcx - 55, leaf_y, 110, 30, "code1 / default", size=10,
                        fill="#eef7f0", stroke=FIELD))
    parts.append(fitbox(rcx - 60, leaf_y, 120, 30, "code40 / v==9000", size=10,
                        fill="#eef7f0", stroke=FIELD))
    parts.append(arrow(lcx, ch_y + 24, lcx, leaf_y - 4))
    parts.append(arrow(rcx, ch_y + 24, rcx, leaf_y - 4))
    parts.append(fitbox(rx + 55, leaf_y + 48, 220, 40,
                        "кілька порівнянь поспіль\nкроків росте з числом міток (log)",
                        size=11, fill="#fff", stroke=NEG, color=NEG, bold=True))

    # divider
    parts.append(line(410, 52, 410, 400, color="#dfe3e8", sw=1))
    return render(os.path.join(IMG, 'switch-dispatch.svg'), W, H, *parts)


# ── Фігура 2: коротке замикання && і || як керування потоком ─────────────────
def fig_short_circuit():
    W, H = 780, 430
    parts = [text(W / 2, 26, "Логічне «і» / «або» — це прихована розвилка", size=16, bold=True)]

    # ── ЛІВА: && ── центр гілок навколо cxL
    cxL = 190
    parts.append(text(cxL, 62, "A && B", size=15, bold=True, color=FIELD))
    parts.append(diamond(cxL, 118, 150, 54, "A істинне?", size=12))
    parts.append(arrow(cxL, 78, cxL, 92))
    # false (left) -> whole false, skip B
    parts.append(arrow(cxL - 70, 130, cxL - 110, 206))
    parts.append(text(cxL - 108, 172, "ні", size=11, color=POS, bold=True, anchor="end"))
    parts.append(fitbox(cxL - 175, 208, 130, 46, "усе = хибне\nB не рахують", size=11,
                        fill="#fdecea", stroke=POS, bold=True))
    # true (right) -> eval B
    parts.append(arrow(cxL + 70, 130, cxL + 100, 206))
    parts.append(text(cxL + 102, 172, "так", size=11, color=FIELD, bold=True, anchor="start"))
    parts.append(diamond(cxL + 100, 230, 116, 46, "B?", size=12))
    parts.append(arrow(cxL + 100, 253, cxL + 100, 300))
    parts.append(fitbox(cxL + 35, 300, 130, 40, "результат = B", size=11,
                        fill="#eef7f0", stroke=FIELD, bold=True))

    # ── ПРАВА: || ── центр навколо cxR
    cxR = 590
    parts.append(text(cxR, 62, "A || B", size=15, bold=True, color=NEG))
    parts.append(diamond(cxR, 118, 150, 54, "A істинне?", size=12))
    parts.append(arrow(cxR, 78, cxR, 92))
    # true (right) -> whole true, skip B
    parts.append(arrow(cxR + 70, 130, cxR + 110, 206))
    parts.append(text(cxR + 108, 172, "так", size=11, color=FIELD, bold=True, anchor="start"))
    parts.append(fitbox(cxR + 45, 208, 130, 46, "усе = істинне\nB не рахують", size=11,
                        fill="#eef7f0", stroke=FIELD, bold=True))
    # false (left) -> eval B
    parts.append(arrow(cxR - 70, 130, cxR - 100, 206))
    parts.append(text(cxR - 102, 172, "ні", size=11, color=POS, bold=True, anchor="end"))
    parts.append(diamond(cxR - 100, 230, 116, 46, "B?", size=12))
    parts.append(arrow(cxR - 100, 253, cxR - 100, 300))
    parts.append(fitbox(cxR - 165, 300, 130, 40, "результат = B", size=11,
                        fill="#fdecea", stroke=POS, bold=True))

    parts.append(line(390, 52, 390, 356, color="#dfe3e8", sw=1))
    parts.append(fitbox(W / 2 - 270, 376, 540, 34,
                        "порядок зліва направо — гарантія мови: A рахують першим, і лише як треба, тоді B",
                        size=11, fill="#f4f6f8", stroke=MUTED, color=MUTED))
    return render(os.path.join(IMG, 'short-circuit.svg'), W, H, *parts)


# ── Фігура 3: анатомія завершення циклу ──────────────────────────────────────
def fig_loop_termination():
    W, H = 680, 440
    parts = [text(W / 2, 26, "Чому цикл коли-небудь спиниться: три речі, що мусять збігтися", size=15, bold=True)]
    cx = W / 2 + 30   # зсув праворуч — лишаємо поле зліва під зворотну петлю

    # init
    parts.append(fitbox(cx - 120, 56, 240, 34, "старт: i = 0  (початковий стан)", size=12,
                        fill="#f4f6f8", stroke=MUTED))
    parts.append(arrow(cx, 90, cx, 112))
    # test
    dcy = 152
    parts.append(diamond(cx, dcy, 224, 66, "умова ще істинна?", size=13))
    # exit branch (праворуч)
    parts.append(arrow(cx + 112, dcy, cx + 150, dcy))
    parts.append(text(cx + 132, dcy - 12, "хибна", size=11, color=POS, bold=True))
    parts.append(fitbox(cx + 150, dcy - 20, 118, 40, "вихід із циклу\nдалі — код нижче", size=10,
                        fill="#fdecea", stroke=POS, bold=True))
    # body
    parts.append(arrow(cx, dcy + 33, cx, dcy + 60))
    parts.append(text(cx + 66, dcy + 50, "істинна", size=11, color=FIELD, bold=True))
    by = dcy + 60
    parts.append(fitbox(cx - 120, by, 240, 42, "тіло: робить корисне\n(інваріант тримається)", size=12,
                        fill="#eef7f0", stroke=FIELD, bold=True))
    # progress
    py = by + 70
    parts.append(arrow(cx, by + 42, cx, py))
    parts.append(fitbox(cx - 120, py, 240, 42, "крок: i++  ← рух до виходу\n(саме це веде умову до хибності)",
                        size=11, fill="#fff", stroke=NEG, color=NEG, bold=True))
    # loop back — вертикаль у лівому полі, підпис ЛІВОРУЧ від неї
    back_x = cx - 200
    parts.append(line(cx - 120, py + 21, back_x, py + 21, color=NEG, sw=2))
    parts.append(line(back_x, py + 21, back_x, dcy, color=NEG, sw=2))
    parts.append(arrow(back_x, dcy, cx - 112, dcy, color=NEG, sw=2))
    parts.append(text(back_x - 8, (dcy + py) / 2, "назад", size=11, color=NEG, bold=True, anchor="end"))
    # caption box
    parts.append(fitbox(W / 2 - 265, py + 64, 530, 34,
                        "нема кроку, що веде умову до хибності → петля не рветься → зависання",
                        size=11, fill="#fdecea", stroke=POS, color=POS, bold=True))
    return render(os.path.join(IMG, 'loop-termination.svg'), W, H, *parts)


if __name__ == "__main__":
    fig_switch_dispatch()
    fig_short_circuit()
    fig_loop_termination()
    print("detailed figures written to", IMG)

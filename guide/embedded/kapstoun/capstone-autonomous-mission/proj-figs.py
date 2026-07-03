# -*- coding: utf-8 -*-
# Фігури для вставки proj-mission-upload-verify.md — окремий файл, щоб не
# заважати figs.py / figs-d.py статей. Вивід — у той самий ./img.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. Один пункт як стан-машина з таймаутом і лічильником повторів ──────────
def fig_upload_loop():
    W, H = 900, 470
    p = []
    p.append(text(W / 2, 30,
                  "завантаження ОДНОГО пункту: запит → чекай 250 мс → прийшов? далі : повтори",
                  size=13, color=MUTED))

    # три вузли-стани в ряд
    y = 130
    nodes = [
        (150, y, "#eaf3ff", NEG, "ЗАПИТ", "надіслати\nREQUEST_INT(seq)"),
        (450, y, "#fff8ee", "#b56c12", "ЧЕКАЮ", "recv_match, timeout 250 мс\ntries += 1"),
        (750, y, "#eef7ee", FIELD, "ПРИЙНЯВ", "потрібний seq?\nзберегти, seq += 1"),
    ]
    nx = {}
    r = 66
    for cx, cy, fill, st, cap, body in nodes:
        p.append(circle(cx, cy, r, fill=fill, stroke=st, sw=2.2))
        p.append(text(cx, cy - 14, cap, size=14, color=st, bold=True))
        p.append(mtext(cx, cy + 6, body, size=10.5, color=INK))
        nx[cap] = (cx, cy)

    # ЗАПИТ → ЧЕКАЮ
    p.append(arrow(nx["ЗАПИТ"][0] + r, y, nx["ЧЕКАЮ"][0] - r, y, color=LINE, sw=2))
    # ЧЕКАЮ → ПРИЙНЯВ  (успіх)
    p.append(arrow(nx["ЧЕКАЮ"][0] + r, y, nx["ПРИЙНЯВ"][0] - r, y, color=FIELD, sw=2.2))
    p.append(text((nx["ЧЕКАЮ"][0] + nx["ПРИЙНЯВ"][0]) / 2, y - 16,
                  "прийшов, той самий seq", size=11, color=FIELD, bold=True))

    # ЧЕКАЮ → ЗАПИТ  (таймаут / не той seq) — дуга знизу
    x1, x2 = nx["ЧЕКАЮ"][0], nx["ЗАПИТ"][0]
    yb = y + r + 66
    p.append(line(x1, y + r, x1, yb, color=POS, sw=2, dash="5,4"))
    p.append(line(x1, yb, x2, yb, color=POS, sw=2, dash="5,4"))
    p.append(arrow(x2, yb, x2, y + r + 2, color=POS, sw=2))
    p.append(text((x1 + x2) / 2, yb + 20,
                  "таймаут (тиша) АБО прийшов не той seq  →  повторити той самий запит",
                  size=11.5, color=POS, bold=True))

    # ПРИЙНЯВ → ЗАПИТ (наступний seq) — дуга зверху
    xa, xb = nx["ПРИЙНЯВ"][0], nx["ЗАПИТ"][0]
    yt = y - r - 42
    p.append(line(xa, y - r, xa, yt, color=NEG, sw=1.8))
    p.append(line(xa, yt, xb, yt, color=NEG, sw=1.8))
    p.append(arrow(xb, yt, xb, y - r - 2, color=NEG, sw=1.8))
    p.append(text((xa + xb) / 2, yt - 8,
                  "seq < count  →  просити наступний пункт", size=11.5, color=NEG, bold=True))

    # аварійний вихід із ЧЕКАЮ: tries == 5
    xc = nx["ЧЕКАЮ"][0]
    b, bw, bh = textbox(xc, y + r + 138,
                        "tries == 5 (5 повторів марно)  →  СКАСУВАТИ операцію,\nстара місія на борту лишається цілою — не піврозібраною",
                        size=11.5, pad=11, fill="#fdf1f0", stroke=POS, color="#a5281b", bold=False)
    p.append(b)
    p.append(line(xc, y + r + 30, xc, y + r + 88, color=POS, sw=1.6, dash="3,3"))

    return render(os.path.join(OUT, "upload-loop.svg"), W, H, *p)


# ── 2. Три пастки поруч: float-координата, брак таймауту, звірка частки ──────
def fig_three_traps():
    W, H = 940, 430
    p = []
    p.append(text(W / 2, 28, "три тихі пастки завантажувача — і як їх обходить робочий код",
                  size=13, color=MUTED))

    colw = (W - 40 - 2 * 20) / 3
    y = 60
    ch = H - y - 30
    x0 = 20

    def panel(i, title, tcol, bad_lines, good_line):
        x = x0 + i * (colw + 20)
        p.append(rect(x, y, colw, ch, fill=BG, stroke="#dfe3e8", sw=1.3, rx=10))
        p.append(text(x + colw / 2, y + 28, title, size=13.5, color=tcol, bold=True))
        # «погано» — червоний блок
        by = y + 46
        p.append(rect(x + 12, by, colw - 24, 132, fill="#fdf1f0", stroke=POS, sw=1.4, rx=7))
        p.append(text(x + 22, by + 20, "✗ пастка", size=11, color="#a5281b", anchor="start", bold=True))
        yy = by + 40
        for ln in bad_lines:
            p.append(text(x + 22, yy, ln, size=10.5, color=INK, anchor="start"))
            yy += 17
        # «добре» — зелений блок
        gy = by + 148
        gh = ch - (gy - y) - 14
        p.append(rect(x + 12, gy, colw - 24, gh, fill="#eef7ee", stroke=FIELD, sw=1.4, rx=7))
        p.append(text(x + 22, gy + 20, "✓ ліки", size=11, color="#1e7d42", anchor="start", bold=True))
        p.append(fitbox(x + 18, gy + 30, colw - 36, gh - 40, good_line,
                        size=10.5, pad=6, fill="#eef7ee", stroke="none", color=INK))

    panel(0, "координата у float", POS,
          ["lat = float(row[0])", "→ округлення до ~1 м", "на самій землі,", "ще до передачі"],
          "тримай int 10⁻⁷°\nвід CSV до відправки;\nу градуси — лише\nдля друку людині")

    panel(1, "немає таймауту", POS,
          ["recv_match(blocking=", "  True)  # без timeout", "загубився пакет →", "висне НАЗАВЖДИ"],
          "timeout=0.25 на кожен\nrecv_match; порожньо →\nповтор; tries==5 →\nскасувати, не висіти")

    panel(2, "звірка частки", POS,
          ["зчитав 3 з 6,", "звірив 3 —", "«усе збіглося»,", "а місія неповна"],
          "спершу переконайся\nlen(got) == count;\nінакше НЕ звіряй —\nчастковий список бреше")

    return render(os.path.join(OUT, "three-traps.svg"), W, H, *p)


if __name__ == "__main__":
    fig_upload_loop()
    fig_three_traps()
    print("ok")

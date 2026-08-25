# -*- coding: utf-8 -*-
"""Фігури до теми «DroneCAN».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. 29-бітний CAN-ID: як DroneCAN розкладає в нього зміст ──────────────────
def fig_can_id_layout():
    W, H = 760, 430
    f = [text(W / 2, 26, "DroneCAN укладає адресу й зміст у 29-бітний ідентифікатор кадру",
              size=15, bold=True)]

    x0, wtot = 40, 680
    # Поля повідомлення (message): priority5 | type16 | svc1=0 | src7  = 29
    row_y = 90
    rh = 54
    msg = [("Пріоритет", 5, "#eaf0fd", NEG),
           ("Тип повідомлення", 16, "#eafaf0", FIELD),
           ("0", 1, "#f0f0f0", MUTED),
           ("ID вузла-джерела", 7, "#fdecea", POS)]
    total = sum(b for _, b in [(n, b) for n, b, _, _ in msg])
    x = x0
    f.append(text(x0, row_y - 12, "Повідомлення (широкомовне):", size=12, bold=True, anchor="start"))
    for name, bits, fill, col in msg:
        w = wtot * bits / total
        f.append(rect(x, row_y, w, rh, fill=fill, stroke=col, sw=1.6))
        fs = fit_font(name, w - 8, 12, True)
        f.append(text(x + w / 2, row_y + rh / 2 - 2, name, size=fs, bold=True, color=col))
        f.append(text(x + w / 2, row_y + rh - 8, "%d біт" % bits if bits > 1 else "1 біт",
                      size=10, color=MUTED))
        x += w

    # Поля сервісу (service): priority5 | type8 | reqresp1 | dst7 | svc1=1 | src7 = 29
    row2 = 215
    svc = [("Пріоритет", 5, "#eaf0fd", NEG),
           ("Тип сервісу", 8, "#eafaf0", FIELD),
           ("R", 1, "#fff6e5", "#b8860b"),
           ("ID призначення", 7, "#f3e8ff", "#7c3aed"),
           ("1", 1, "#f0f0f0", MUTED),
           ("ID джерела", 7, "#fdecea", POS)]
    total2 = sum(b for _, b, _, _ in svc)
    x = x0
    f.append(text(x0, row2 - 12, "Сервіс (запит/відповідь між двома вузлами):", size=12, bold=True, anchor="start"))
    for name, bits, fill, col in svc:
        w = wtot * bits / total2
        f.append(rect(x, row2, w, rh, fill=fill, stroke=col, sw=1.6))
        fs = fit_font(name, w - 6, 11, True)
        f.append(text(x + w / 2, row2 + rh / 2 - 2, name, size=fs, bold=True, color=col))
        f.append(text(x + w / 2, row2 + rh - 8, "%d" % bits, size=10, color=MUTED))
        x += w

    # Підсумок — чому саме так
    b, bw, bh = textbox(W / 2, 345,
                        "Пріоритет — старші біти → менший ID виграє арбітраж → терміновіший кадр іде першим.\n"
                        "ID вузла-джерела — молодші 7 біт (1…127): кожен кадр підписаний тим, хто його послав.",
                        size=12, pad=12, fill="#f7fbff", stroke=NEG)
    f.append(b)
    return render(os.path.join(IMG, "can-id-layout.svg"), W, H, *f)


# ── 2. Кадр DroneCAN: 7 байт корисного + хвостовий байт ───────────────────────
def fig_tail_byte():
    W, H = 760, 400
    f = [text(W / 2, 26, "Кожен CAN-кадр несе 7 байт даних і один хвостовий байт складання",
              size=15, bold=True)]

    # 8 байтів поля даних
    x0, y0 = 55, 70
    bw, bh = 78, 52
    for i in range(8):
        x = x0 + i * bw
        is_tail = (i == 7)
        fill = "#fff6e5" if is_tail else "#eafaf0"
        col = "#b8860b" if is_tail else FIELD
        f.append(rect(x, y0, bw, bh, fill=fill, stroke=col, sw=1.8))
        if is_tail:
            f.append(text(x + bw / 2, y0 + bh / 2 - 3, "хвіст", size=12, bold=True, color=col))
            f.append(text(x + bw / 2, y0 + bh / 2 + 13, "tail", size=10, color=MUTED))
        else:
            f.append(text(x + bw / 2, y0 + bh / 2 + 4, "дані", size=12, color=INK))
    f.append(text(x0 + 3.5 * bw, y0 - 12, "7 байт корисного вантажу", size=12, bold=True, color=FIELD))

    # Розкладка хвостового байта на біти
    tx = x0 + 7 * bw
    ty = 200
    # лінії-виноски від хвоста до розкладки
    f.append(line(tx + bw / 2, y0 + bh, tx + bw / 2, ty - 6, color=MUTED, dash="4,3"))

    bits = [("SOT", 1, "#eaf0fd", NEG, "початок"),
            ("EOT", 1, "#eaf0fd", NEG, "кінець"),
            ("T", 1, "#f3e8ff", "#7c3aed", "перемикач"),
            ("Transfer ID", 5, "#fdecea", POS, "лічильник передачі")]
    bstart = 70
    bx = bstart
    for name, nb, fill, col, note in bits:
        w = 232 if nb == 5 else 92
        f.append(rect(bx, ty, w, 46, fill=fill, stroke=col, sw=1.7))
        f.append(text(bx + w / 2, ty + 20, name, size=13, bold=True, color=col))
        f.append(text(bx + w / 2, ty + 38, "%d біт" % nb if nb > 1 else "1 біт", size=10, color=MUTED))
        f.append(text(bx + w / 2, ty + 66, note, size=10.5, color=MUTED))
        bx += w + 10

    b, bw2, bh2 = textbox(W / 2, 340,
                          "Один кадр (7 байт) → SOT=1, EOT=1: усе вмістилось.  Не влізло → ланцюг кадрів,\n"
                          "перемикач T чергується 0/1 (ловить загублений кадр), Transfer ID (0…31) в'яже їх в одну передачу.",
                          size=12, pad=12, fill="#fffaf0", stroke="#b8860b")
    f.append(b)
    return render(os.path.join(IMG, "tail-byte.svg"), W, H, *f)


# ── 3. Стек DroneCAN: від DSDL-опису до дротів CAN ────────────────────────────
def fig_stack():
    W, H = 700, 440
    f = [text(W / 2, 26, "DroneCAN — тонкий шар над CAN-шиною: типи, адреси, складання",
              size=15, bold=True)]

    cx = W / 2
    layers = [
        ("Прикладні дані", "NodeStatus · esc.RawCommand · gnss.Fix2 · GetNodeInfo", "#eafaf0", FIELD),
        ("DSDL — опис типів", "поля й підпис типу (CRC-64): збіг ⇒ вузли розуміють одне одного", "#f3e8ff", "#7c3aed"),
        ("DroneCAN-транспорт", "ID вузла · пріоритет · Transfer ID · хвостовий байт · CRC складання", "#fff6e5", "#b8860b"),
        ("CAN 2.0B — шина", "29-бітний ID · арбітраж без зіткнень · 1 Мбіт/с · дві виті пари", "#eaf0fd", NEG),
    ]
    y = 62
    lw, lh = 560, 74
    x = cx - lw / 2
    for i, (title, sub, fill, col) in enumerate(layers):
        f.append(rect(x, y, lw, lh, fill=fill, stroke=col, sw=1.9))
        f.append(text(cx, y + 27, title, size=15, bold=True, color=col))
        fs = fit_font(sub, lw - 24, 11.5, False)
        f.append(text(cx, y + 50, sub, size=fs, color=INK))
        if i < len(layers) - 1:
            f.append(arrow(cx, y + lh + 2, cx, y + lh + 16, color=MUTED, sw=2))
        y += lh + 18

    return render(os.path.join(IMG, "stack.svg"), W, H, *f)


if __name__ == "__main__":
    fig_can_id_layout()
    fig_tail_byte()
    fig_stack()
    print("figs written to", IMG)

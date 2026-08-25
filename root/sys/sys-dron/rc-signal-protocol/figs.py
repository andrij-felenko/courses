# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «RC-сигнал: PWM, PPM і S.BUS».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/.
Запуск:  python figs.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── допоміжне: цифровий сигнал прямокутними сходинками ────────────────────────
def steps(pts, color=INK, sw=2.2):
    """pts — список (x, рівень 0/1); малює прямокутну лінію між ними."""
    out = []
    for i in range(len(pts) - 1):
        x1, l1 = pts[i]
        x2, l2 = pts[i + 1]
        y1 = l1
        y2 = l2
        out.append(line(x1, y1, x2, y1, color=color, sw=sw))   # горизонталь
        if y1 != y2:
            out.append(line(x2, y1, x2, y2, color=color, sw=sw))  # вертикаль-фронт
    return "".join(out)


# ── 1. PWM: ширина імпульсу = число каналу ───────────────────────────────────
# Ідея: значення каналу закодоване САМОЮ тривалістю високого рівня (1000..2000 мкс),
# а весь кадр повторюється кожні ~20 мс. Показуємо три положення стіка.
def fig_pwm():
    W, H = 900, 380
    HI, LO = 120, 190          # рівні у пікселях (верх — «1», низ — «0»)
    x0 = 90
    P = [text(W / 2, 30, "PWM: ширина імпульсу кодує канал", size=17, bold=True)]

    def row(cy_hi, cy_lo, w_px, label_us, caption):
        # один імпульс: низько-високо(w_px)-низько, потім довга пауза до 20 мс
        seg = []
        x = x0
        seg.append(steps([(x, cy_lo), (x, cy_hi), (x + w_px, cy_hi),
                          (x + w_px, cy_lo), (x + 470, cy_lo)], color=POS))
        # позначка ширини
        seg.append(line(x, cy_hi - 16, x + w_px, cy_hi - 16, color=MUTED, sw=1.2, dash="3,3"))
        seg.append(text(x + w_px / 2, cy_hi - 22, label_us, size=12, color=MUTED))
        seg.append(text(x - 12, (cy_hi + cy_lo) / 2 + 4, caption, size=12,
                        color=INK, anchor="end"))
        return "".join(seg)

    P.append(row(70, 130, 90, "1000 мкс", "стік у краю"))
    P.append(row(160, 220, 145, "1500 мкс", "нейтраль"))
    P.append(row(250, 310, 200, "2000 мкс", "інший край"))

    # шкала «один кадр ~20 мс, окремий дріт на канал» унизу
    P.append(line(x0, 345, x0 + 470, 345, color=INK, sw=1.4))
    P.append(text(x0 + 235, 366, "період кадру ≈ 20 мс · окремий дріт на кожен канал",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "pwm.svg"), W, H, *P)


# ── 2. PPM: усі канали один за одним по одному дроту + синхропауза ────────────
# Ідея: кожен канал — це проміжок між двома короткими розділювачами (~0.3-0.5 мс);
# після останнього — довга синхропауза, що позначає межу кадру.
def fig_ppm():
    W, H = 980, 320
    HI, LO = 150, 210
    x0 = 40
    P = [text(W / 2, 30, "PPM: канали один за одним по одному дроту", size=17, bold=True)]

    # серія розділювачів (маркерів). Проміжок між сусідніми = значення каналу.
    gaps = [95, 150, 120, 170, 60]     # ширини «слотів» каналів (у px)
    names = ["К1", "К2", "К3", "К4", "К5"]
    marker = 14                        # ширина короткого розділового імпульсу
    pts = [(x0, LO)]
    x = x0
    slot_centers = []
    for g in gaps:
        # короткий маркер угору
        pts += [(x, HI), (x + marker, HI), (x + marker, LO)]
        slot_centers.append((x + marker + (g - marker) / 2, x, x + g))
        x += g
    # ще один маркер — кінець останнього слота
    pts += [(x, HI), (x + marker, HI), (x + marker, LO)]
    # довга синхропауза
    sync_end = x + marker + 210
    pts += [(sync_end, LO), (sync_end, HI), (sync_end + marker, HI), (sync_end + marker, LO),
            (sync_end + 90, LO)]

    P.append(steps(pts, color=NEG, sw=2.4))

    # підписи слотів каналів
    for (cx, a, b), nm in zip(slot_centers, names):
        P.append(line(a, HI - 14, b, HI - 14, color=MUTED, sw=1.1, dash="3,3"))
        P.append(text(cx, HI - 20, nm, size=12, color=INK, bold=True))
        P.append(text(cx, LO + 20, "1–2 мс", size=10, color=MUTED))

    # позначка синхропаузи
    P.append(line(x + marker, 250, sync_end, 250, color=FIELD, sw=1.6))
    P.append(text((x + marker + sync_end) / 2, 244, "синхропауза (> 3 мс) — межа кадру",
                  size=12, color=FIELD, bold=True))
    P.append(text(x0, 288, "один дріт на всі канали · ~8 каналів у кадрі ≈ 22.5 мс",
                  size=12, color=MUTED, anchor="start"))
    render(os.path.join(IMG, "ppm.svg"), W, H, *P)


# ── 3. S.BUS: 25-байтовий кадр по інвертованому UART ──────────────────────────
# Ідея: значення — вже не тривалість, а БАЙТИ. Кадр фіксований: старт 0x0F,
# 22 байти даних (16×11 біт), байт прапорців, стоп 0x00.
def fig_sbus_frame():
    W, H = 940, 300
    P = [text(W / 2, 30, "Кадр S.BUS: 25 байтів фіксованої довжини", size=17, bold=True)]

    y = 70
    h = 66
    x = 40
    # блоки кадру (ширина ~ пропорційна ролі, не байтам)
    blocks = [
        (70,  "0x0F", "старт", "#eaf0fd", NEG),
        (470, "22 байти даних", "16 каналів × 11 біт", FILL, INK),
        (150, "прапорці", "ch17 ch18\nframe_lost\nfailsafe", "#eafaf0", FIELD),
        (70,  "0x00", "стоп", "#fdecea", POS),
    ]
    for w, top, bottom, fill, stroke in blocks:
        P.append(rect(x, y, w, h, fill=fill, stroke=stroke, sw=2, rx=6))
        P.append(text(x + w / 2, y + 24, top, size=13, color=stroke, bold=True))
        # нижній підпис (може бути багаторядковий)
        lines = bottom.split("\n")
        for i, ln in enumerate(lines):
            P.append(text(x + w / 2, y + 42 + i * 13, ln, size=11, color=INK))
        x += w + 6

    # брекет під байтами даних → показ пакування бітів
    dx0, dx1 = 40 + 70 + 6, 40 + 70 + 6 + 470
    P.append(line(dx0, y + h + 12, dx1, y + h + 12, color=MUTED, sw=1.3))
    P.append(text((dx0 + dx1) / 2, y + h + 30,
                  "11-бітні канали спаковано щільно, «поперек» байтових меж",
                  size=12, color=MUTED))

    # параметри лінії
    P.append(text(W / 2, 250,
                  "інвертований UART · 100 000 бод · 8E2 (парність + 2 стоп-біти)",
                  size=13, color=INK, bold=True))
    P.append(text(W / 2, 272,
                  "кадр летить ~3 мс, повторюється кожні 7 або 14 мс",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "sbus-frame.svg"), W, H, *P)


# ── 4. Порівняння: де живе число (тривалість → позиція → байти) ───────────────
def fig_where_number():
    W, H = 900, 300
    P = [text(W / 2, 30, "Де закодоване число каналу", size=17, bold=True)]

    cols = [
        ("PWM", "тривалість імпульсу", "аналогова: наводка зсуває значення напряму",
         "окремий дріт / канал", POS),
        ("PPM", "проміжок між маркерами", "аналогова: спільна для всіх похибка часу",
         "один дріт, ~8 каналів", NEG),
        ("S.BUS", "біти в байтах кадру", "цифрова: парність ловить збій, failsafe-прапорець",
         "один дріт, 16 каналів", FIELD),
    ]
    cw = 280
    gap = 10
    total = 3 * cw + 2 * gap
    x = (W - total) / 2
    for name, where, robust, wires, col in cols:
        P.append(rect(x, 60, cw, 200, fill=FILL, stroke=col, sw=2.2, rx=8))
        P.append(text(x + cw / 2, 92, name, size=18, color=col, bold=True))
        P.append(fitbox(x + 16, 110, cw - 32, 40, where, size=13, fill="#ffffff",
                        stroke=col, sw=1.2, bold=True))
        P.append(fitbox(x + 16, 158, cw - 32, 54, robust, size=11, fill=BG,
                        stroke=MUTED, sw=1))
        P.append(text(x + cw / 2, 244, wires, size=11, color=MUTED))
        x += cw + gap
    render(os.path.join(IMG, "where-number.svg"), W, H, *P)


# ── 5. Автомат синхронізації парсера (для вставки proj-sbus-frame-parser) ─────
# Ідея: байти течуть по одному; парсер має «зловити» початок кадру (0x0F),
# набрати рівно 25, перевірити хвіст (0x00) — і на будь-якому збої вернутись
# у пошук старту, а не з'їсти зсунутий кадр.
def fig_sbus_fsm():
    W, H = 900, 460
    P = [text(W / 2, 30, "Автомат збирання кадру S.BUS із байтового потоку", size=17, bold=True)]

    # два стани-кола
    sx, sy = 250, 150      # SEEK
    cx, cy = 650, 150      # COLLECT
    r = 62
    P.append(circle(sx, sy, r, fill="#eaf0fd", stroke=NEG, sw=2.4))
    P.append(mtext(sx, sy - 4, ["SEEK", "шукаю 0x0F"], size=14, color=NEG, bold=True))
    P.append(circle(cx, cy, r, fill="#eafaf0", stroke=FIELD, sw=2.4))
    P.append(mtext(cx, cy - 4, ["COLLECT", "набираю 25"], size=14, color=FIELD, bold=True))

    # SEEK → COLLECT : побачив 0x0F
    P.append(arrow(sx + r, sy - 18, cx - r, cy - 18, color=INK, sw=2))
    P.append(text((sx + cx) / 2, sy - 30, "байт == 0x0F  (n ← 1)", size=12, color=INK, bold=True))

    # SEEK самопетля: інший байт — ігнор
    P.append(arrow(sx - r + 8, sy - r + 20, sx - r - 30, sy - 6, color=MUTED, sw=1.6))
    P.append(arrow(sx - r - 30, sy - 6, sx - r + 8, sy + r - 20, color=MUTED, sw=1.6))
    P.append(text(sx - r - 78, sy - 2, "байт ≠ 0x0F\nвикинути", size=11, color=MUTED))

    # COLLECT самопетля: ще не 25
    P.append(arrow(cx + r - 8, cy - r + 20, cx + r + 30, cy - 6, color=MUTED, sw=1.6))
    P.append(arrow(cx + r + 30, cy - 6, cx + r - 8, cy + r - 20, color=MUTED, sw=1.6))
    P.append(text(cx + r + 78, cy - 2, "n < 25\nкласти в буфер\n(n ← n+1)", size=11, color=MUTED))

    # COLLECT → перевірка (унизу)
    px, py = 650, 340
    box = fitbox(px - 120, py - 34, 240, 68,
                 "n == 25 ?\nбуфер[24] == 0x00 ?", size=13, fill=FILL, stroke=INK, sw=1.6, bold=True)
    P.append(arrow(cx, cy + r, px, py - 36, color=INK, sw=2))
    P.append(box)

    # так → кадр готовий
    P.append(arrow(px - 120, py, 220, py, color=FIELD, sw=2.2))
    ok = textbox(150, py, "кадр валідний\n→ розпакувати", size=12, fill="#eafaf0",
                 stroke=FIELD, sw=2, color=FIELD, bold=True)
    P.append(ok[0])
    P.append(text(px - 175, py - 10, "так", size=12, color=FIELD, bold=True))

    # ні → назад у SEEK (десинхронізація)
    P.append(arrow(px, py + 34, px, py + 66, color=POS, sw=2))
    P.append(arrow(px, py + 66, sx, py + 66, color=POS, sw=2))
    P.append(arrow(sx, py + 66, sx, sy + r, color=POS, sw=2))
    P.append(text(px + 90, py + 60, "хвіст не 0x00 → десинхрон:\nусе назад у SEEK", size=12, color=POS))

    P.append(text(W / 2, 440,
                  "будь-який збій повертає в SEEK — зсунутий кадр краще викинути, ніж з'їсти",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "sbus-fsm.svg"), W, H, *P)


# ── 6. Пакування бітів: як канал збирається «поперек» байтів (зсуви й маски) ──
# Ідея: показати РІВНО ті зсуви й маски, що в коді. Байти йдуть молодшим бітом
# уперед, тож ch1 = усі біти байта0 + три молодші байта1, і т.д.
def fig_sbus_bitpack():
    W, H = 940, 470
    P = [text(W / 2, 30, "Пакування каналів «поперек» байтів (перші три канали)", size=17, bold=True)]

    # три байти по 8 клітинок; підпишемо, якому каналу належить кожен біт
    bw, bh = 92, 40           # клітинка біта
    y = 90
    x0 = 60
    # для кожного байта — 8 міток (біт7..біт0 зліва направо), звідки й куди йде
    # байт0: усе ch1 (біти 0..7)
    # байт1: біти0..2 = ch1[8..10]; біти3..7 = ch2[0..4]
    # байт2: біти0..5 = ch2[5..10]; біти6..7 = ch3[0..1]
    bytes_map = [
        ("байт 0", [("ch1", i) for i in range(7, -1, -1)]),
        ("байт 1", [("ch2", i) for i in (7, 6, 5, 4, 3)] + [("ch1", i) for i in (10, 9, 8)]),
        ("байт 2", [("ch3", i) for i in (1, 0)] + [("ch2", i) for i in (10, 9, 8, 7, 6, 5)]),
    ]
    col = {"ch1": NEG, "ch2": FIELD, "ch3": POS}
    fillc = {"ch1": "#eaf0fd", "ch2": "#eafaf0", "ch3": "#fdecea"}

    for bi, (bname, cells) in enumerate(bytes_map):
        bx = x0
        by = y + bi * 96
        P.append(text(x0 - 12, by + bh / 2 + 5, bname, size=13, color=INK, anchor="end", bold=True))
        for ch, bit in cells:
            P.append(rect(bx, by, bw, bh, fill=fillc[ch], stroke=col[ch], sw=1.6, rx=4))
            P.append(text(bx + bw / 2, by + 17, ch, size=12, color=col[ch], bold=True))
            P.append(text(bx + bw / 2, by + 33, "b%d" % bit, size=11, color=MUTED))
            bx += bw + 2
        # позначка «молодший біт праворуч»
        P.append(text(bx + 10, by + bh / 2 + 5, "→ b0", size=10, color=MUTED, anchor="start"))

    # праворуч — рецепт коду для ch1/ch2
    rx = 60
    ry = y + 3 * 96 + 4
    recipe = ("ch1 = ( байт0        | байт1 << 8 ) & 0x7FF\n"
              "ch2 = ( байт1 >> 3   | байт2 << 5 ) & 0x7FF")
    P.append(fitbox(rx, ry, W - 2 * rx, 60, recipe, size=13, fill=FILL, stroke=INK, sw=1.4, bold=True))
    render(os.path.join(IMG, "sbus-bitpack.svg"), W, H, *P)


if __name__ == "__main__":
    fig_pwm()
    fig_ppm()
    fig_sbus_frame()
    fig_where_number()
    fig_sbus_fsm()
    fig_sbus_bitpack()
    print("OK: figs у", IMG)

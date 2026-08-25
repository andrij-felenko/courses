# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «Семисегментний індикатор 5641AS (4 розряди)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

RED = "#c0392b"   # засвічений сегмент
GRY = "#c9ced6"   # згаслий сегмент


# ── 1. Розкладка сегментів і спільний катод 5641AS ────────────────────────────
def fig_anatomy():
    W, H = 820, 470
    f = [text(W / 2, 30, "5641AS: сім сегментів + крапка на кожен із чотирьох розрядів",
              size=16, bold=True)]

    # ── ліва панель: одна «вісімка» з підписаними сегментами ──
    cx, cy = 175, 235
    seg_w, seg_t = 70, 12
    on_col, lbl_col = RED, INK
    # координати кутів «вісімки»
    L = cx - seg_w / 2
    Rr = cx + seg_w / 2
    yT, yM, yB = cy - 78, cy, cy + 78

    def hseg(xl, y, lab, labpos):
        poly = ('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" '
                'fill="%s" stroke="%s" stroke-width="1"/>'
                % (xl, y, xl + seg_t, y - seg_t / 1.4, xl + seg_w - seg_t, y - seg_t / 1.4,
                   xl + seg_w, y, xl + seg_w - seg_t, y + seg_t / 1.4, xl + seg_t, y + seg_t / 1.4,
                   RED, "#7a1f14"))
        return poly

    def vseg(x, ytop, lab):
        h = 70
        poly = ('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" '
                'fill="%s" stroke="%s" stroke-width="1"/>'
                % (x, ytop, x + seg_t / 1.4, ytop + seg_t, x + seg_t / 1.4, ytop + h - seg_t,
                   x, ytop + h, x - seg_t / 1.4, ytop + h - seg_t, x - seg_t / 1.4, ytop + seg_t,
                   RED, "#7a1f14"))
        return poly

    # сегменти
    f.append(hseg(L, yT, 'a', 0))            # a — верх
    f.append(hseg(L, yM, 'g', 0))            # g — середина
    f.append(hseg(L, yB, 'd', 0))            # d — низ
    f.append(vseg(L, yT, 'e'))               # f — лівий верх
    f.append(vseg(Rr, yT, 'b'))              # b — правий верх
    f.append(vseg(L, yM, 'ee'))              # e — лівий низ
    f.append(vseg(Rr, yM, 'c'))              # c — правий низ
    # крапка
    f.append(circle(Rr + 22, yB, 7, fill=RED, stroke="#7a1f14", sw=1))

    # підписи сегментів (з запасом, поза рисками)
    f.append(text(cx, yT - 22, "a", size=15, bold=True, color=lbl_col))
    f.append(text(cx, yM - 20, "g", size=15, bold=True, color=lbl_col))
    f.append(text(cx, yB + 30, "d", size=15, bold=True, color=lbl_col))
    f.append(text(L - 26, (yT + yM) / 2 + 4, "f", size=15, bold=True, color=lbl_col))
    f.append(text(Rr + 26, (yT + yM) / 2 + 4, "b", size=15, bold=True, color=lbl_col))
    f.append(text(L - 26, (yM + yB) / 2 + 4, "e", size=15, bold=True, color=lbl_col))
    f.append(text(Rr + 26, (yM + yB) / 2 + 4, "c", size=15, bold=True, color=lbl_col))
    f.append(text(Rr + 22, yB + 28, "dp", size=13, bold=True, color=lbl_col))

    b, _, _ = textbox(cx, cy + 165,
                      "вісім світлодіодів однієї цифри:\nсім рисок a…g + крапка dp",
                      size=12, fill="#fdecea", stroke=RED)
    f.append(b)

    # ── права панель: внутрішнє з'єднання спільного катода ──
    px = 470
    f.append(text(px + 155, 70, "Усередині: розряди на спільній шині сегментів",
                  size=13, bold=True, color=NEG))

    # спільна шина 8 сегментних ліній — угорі, з підписом НАД нею
    dcx = [px + 45, px + 135, px + 225, px + 315]
    dy = 200
    busY = 120
    f.append(text((dcx[0] + dcx[3]) / 2, busY - 10,
                  "8 спільних сегментних ліній (a…g, dp)", size=10.5, color=MUTED))
    f.append(line(dcx[0], busY, dcx[3], busY, color=MUTED, sw=1.6))

    # чотири цифри-квадратики в ряд; DIG-підпис — під квадратиком, катод — ще нижче
    for i, x in enumerate(dcx):
        f.append(line(x, busY, x, dy - 32, color=MUTED, sw=1.4))     # шина → цифра (згори)
        f.append(rect(x - 26, dy - 32, 52, 74, fill=BG, stroke=INK, sw=1.6, rx=6))
        f.append(text(x, dy + 6, "8.", size=26, bold=True, color=RED))
        f.append(line(x, dy + 42, x, dy + 60, color=NEG, sw=2.2))    # катод-нога вниз (коротка)
        f.append(text(x, dy + 80, "DIG%d" % (i + 1), size=11, bold=True, color=NEG))
    # спільний підпис катодів під рядом
    f.append(text((dcx[0] + dcx[3]) / 2, dy + 104,
                  "кожен розряд — свій катод (DIG1…DIG4)", size=10.5, color=NEG))

    b2, _, _ = textbox(px + 155, dy + 150,
                       "сегменти a…g спільні для всіх чотирьох розрядів;\n"
                       "розряди різняться лише окремим катодом — тому цифри\n"
                       "не світяться всі водночас, а по черзі",
                       size=11, fill="#eaf0fd", stroke=NEG)
    f.append(b2)

    render(os.path.join(IMG, "anatomy.svg"), W, H, *f)


# ── 2. Підключення до МК: сегментні резистори + ключі розрядів, розгортка ──────
def fig_wiring():
    W, H = 860, 560
    f = [text(W / 2, 30, "Підключення 5641AS: 8 сегментів через резистори, 4 розряди через ключі",
              size=15.5, bold=True)]

    # МК ліворуч
    mcx, mcy = 95, 250
    f.append(rect(mcx - 55, mcy - 150, 110, 300, fill="#eef2f8", stroke=INK, sw=1.8, rx=10))
    f.append(text(mcx, mcy - 165, "Мікроконтролер", size=12, bold=True))
    f.append(text(mcx, mcy - 130, "8 виводів", size=10, color=MUTED))
    f.append(text(mcx, mcy - 116, "сегментів", size=10, color=MUTED))
    f.append(text(mcx, mcy + 108, "4 виводи", size=10, color=MUTED))
    f.append(text(mcx, mcy + 122, "розрядів", size=10, color=MUTED))

    # індикатор праворуч
    dx, dy = 690, 250
    f.append(rect(dx - 95, dy - 150, 190, 300, fill="#fafbfc", stroke=MUTED, sw=1.7, rx=12))
    f.append(text(dx, dy - 165, "5641AS", size=13, bold=True, color=RED))
    # чотири цифри
    qx = [dx - 66, dx - 22, dx + 22, dx + 66]
    for i, x in enumerate(qx):
        f.append(rect(x - 17, dy - 118, 34, 60, fill=BG, stroke=INK, sw=1.3, rx=4))
        f.append(text(x, dy - 74, "8.", size=20, bold=True, color=RED))
        f.append(text(x, dy - 128, "%d" % (i + 1), size=10, bold=True, color=NEG))

    # 8 сегментних ліній: МК → резистори → верх індикатора
    rx = 300                     # колонка резисторів
    seg_names = ["a", "b", "c", "d", "e", "f", "g", "dp"]
    y0 = mcy - 118
    dyv = 20
    for i, nm in enumerate(seg_names):
        ly = y0 + i * dyv
        # від МК до резистора
        f.append(line(mcx + 55, ly, rx - 26, ly, color=INK, sw=1.6))
        # резистор (прямокутник)
        f.append(rect(rx - 26, ly - 6, 52, 12, fill="#fff3d9", stroke="#b8860b", sw=1.3, rx=3))
        # від резистора до шини сегментів індикатора (заходить згори)
        f.append(line(rx + 26, ly, dx - 95, ly, color=RED, sw=1.5))
        f.append(text((mcx + 55 + rx - 26) / 2, ly - 5, nm, size=10, bold=True, color=INK))
    f.append(text(rx, y0 - 22, "8 × R  (≈220 Ом)", size=11.5, bold=True, color="#b8860b"))
    f.append(text(rx, y0 - 8, "по одному на сегмент", size=9.5, color=MUTED))

    # 4 лінії розрядів: МК → ключі (транзистори) → катоди індикатора
    ky = mcy + 40
    dyk = 30
    kcolx = 300
    for i in range(4):
        ly = ky + i * dyk
        f.append(line(mcx + 55, ly, kcolx - 22, ly, color=NEG, sw=1.6))
        # ключ-транзистор (кружечок з Q)
        f.append(circle(kcolx, ly, 13, fill="#eaf0fd", stroke=NEG, sw=1.6))
        f.append(text(kcolx, ly + 4, "Q", size=11, bold=True, color=NEG))
        # від ключа до катода розряду
        f.append(line(kcolx + 13, ly, dx - 95, ly, color=NEG, sw=1.5))
        f.append(text((mcx + 55 + kcolx) / 2, ly - 5, "DIG%d" % (i + 1), size=9.5, bold=True, color=NEG))
    f.append(text(kcolx, ky - 20, "4 ключі на катоди", size=11.5, bold=True, color=NEG))
    f.append(text(kcolx, ky - 6, "тягнуть струм 4 цифр у землю", size=9.5, color=MUTED))

    # катодна шина вниз від індикатора
    f.append(text(dx, dy + 175, "GND", size=11, bold=True, color=INK))
    f.append(line(dx, dy + 150, dx, dy + 165, color=INK, sw=2))

    b, _, _ = textbox(W / 2, H - 26,
                      "у кожну мить світиться лише ОДИН розряд (його ключ відкритий); "
                      "МК швидко перебирає розряди — око зливає їх у ціле число",
                      size=11.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)

    render(os.path.join(IMG, "wiring.svg"), W, H, *f)


# ── 3. put_segments(): один байт → вісім РОЗКИДАНИХ ніг через таблицю SEG[] ────
def fig_bitmap():
    W, H = 820, 470
    f = [text(W / 2, 30, "put_segments(): байт цифри → вісім реальних ніг через таблицю SEG[]",
              size=15, bold=True)]

    # ── байт «5» угорі: вісім клітин-бітів ──
    seg_names = ["a", "b", "c", "d", "e", "f", "g", "dp"]
    bit_no    = ["0", "1", "2", "3", "4", "5", "6", "7"]
    val5      = [1, 0, 1, 1, 0, 1, 1, 0]   # цифра «5»: a c d f g  (0b01101101)
    cellw = 66
    x0 = W / 2 - 8 * cellw / 2
    byteY = 118
    f.append(text(W / 2, byteY - 62, "байт цифри «5» = 0b01101101   (1 = сегмент горить)",
                  size=12, bold=True, color=RED))
    for i in range(8):
        cx = x0 + i * cellw + cellw / 2
        on = val5[i]
        # підпис сегмента — НАД клітиною (щоб не лежав на стрілці вниз)
        f.append(text(cx, byteY - 24, seg_names[i], size=12, bold=True, color=INK))
        f.append(text(cx, byteY - 10, "біт %s" % bit_no[i], size=9, color=MUTED))
        f.append(rect(x0 + i * cellw, byteY, cellw - 4, 40,
                      fill=("#fdecea" if on else "#eef2f8"),
                      stroke=(RED if on else MUTED), sw=1.6, rx=4))
        f.append(text(cx, byteY + 27, str(on), size=18, bold=True,
                      color=(RED if on else MUTED)))

    # ── таблиця SEG[]: кожен біт → свій порт+нога (навмисно розкидані) ──
    port_of = ["PB0", "PB1", "PB2", "PD5", "PD6", "PD7", "PC0", "PC1"]
    tY = 258
    # пояснення таблиці — ЛІВОРУЧ угорі, поза коридором стрілок
    f.append(text(x0, byteY - 44, "SEG[i] = { порт, нога }:", size=11.5, bold=True,
                  color=NEG, anchor="start"))
    f.append(text(x0, byteY - 30, "місток «логічний біт → фізична ніжка»", size=10,
                  color=MUTED, anchor="start"))
    for i in range(8):
        cx = x0 + i * cellw + cellw / 2
        on = val5[i]
        # стрілка від клітини байта вниз до ніжки (чистий коридор — жодних написів на шляху)
        f.append(line(cx, byteY + 44, cx, tY - 10,
                      color=(RED if on else "#c9ced6"), sw=(1.8 if on else 1.2)))
        # плашка «порт+нога»
        col = RED if on else MUTED
        f.append(rect(cx - 30, tY, 60, 34, fill=BG, stroke=col, sw=1.5, rx=5))
        f.append(text(cx, tY + 15, port_of[i], size=11, bold=True, color=INK))
        f.append(text(cx, tY + 29, ("↑1" if on else "↓0"), size=10, bold=True, color=col))

    b, _, _ = textbox(W / 2, 400,
                      "біт i горить → ногу SEG[i] піднімаємо в «1»; біт погас → опускаємо в «0».\n"
                      "ноги навмисно розкидані по портах PB/PC/PD — перепаяв сегмент,\n"
                      "правиш ОДИН рядок таблиці, а логіка драйвера не міняється",
                      size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b)

    render(os.path.join(IMG, "bitmap.svg"), W, H, *f)


# ── 4. Ghosting: неправильний vs правильний порядок трьох дій у часі ───────────
def fig_scan_timing():
    W, H = 820, 470
    f = [text(W / 2, 30, "Ghosting: чому порядок «погасити → виставити → відкрити» — священний",
              size=15, bold=True)]

    laneW = 330
    lx = 70          # ліва (неправильна) колонка
    rx = 460         # права (правильна) колонка
    topY = 70

    # заголовки колонок
    f.append(text(lx + laneW / 2, topY, "НЕПРАВИЛЬНО: виставив → відкрив", size=12.5, bold=True, color=RED))
    f.append(text(rx + laneW / 2, topY, "ПРАВИЛЬНО: погасив → виставив → відкрив", size=12, bold=True, color=FIELD))

    # осі часу
    axY = topY + 30
    f.append(line(lx, axY, lx + laneW, axY, color=INK, sw=1.4))
    f.append(line(rx, axY, rx + laneW, axY, color=INK, sw=1.4))
    f.append(text(lx + laneW, axY - 8, "час →", size=10, color=MUTED, anchor="end"))
    f.append(text(rx + laneW, axY - 8, "час →", size=10, color=MUTED, anchor="end"))

    # ── ЛІВА колонка: три кроки, у проміжку 2 — примара ──
    def step(colx, i, label, sub, col):
        sw = laneW / 3
        sx = colx + i * sw
        f.append(rect(sx + 4, axY + 12, sw - 8, 44, fill="#f7f9fb", stroke=col, sw=1.4, rx=5))
        f.append(text(sx + sw / 2, axY + 30, label, size=10.5, bold=True, color=col))
        f.append(text(sx + sw / 2, axY + 47, sub, size=9, color=MUTED))

    step(lx, 0, "put_segments(«2»)", "нові сегменти", INK)
    step(lx, 1, "digit_on(next)", "перемкнули розряд", INK)
    step(lx, 2, "чекаємо тик", "", MUTED)
    # маркер примари між кроком 0 і 1
    ghostX = lx + laneW / 3
    f.append(line(ghostX, axY + 12, ghostX, axY + 92, color=RED, sw=1.6, dash="4,3"))
    b1, _, _ = textbox(lx + laneW / 2, axY + 118,
                       "тут DIG1 ще відкритий, а сегменти вже «2»\n→ на 1-й цифрі мигнула ЧУЖА «2» блідою тінню",
                       size=10, fill="#fdecea", stroke=RED)
    f.append(b1)

    # ── ПРАВА колонка: три кроки, екран чистий ──
    step(rx, 0, "all_digits_off()", "усе погасили", FIELD)
    step(rx, 1, "put_segments(«2»)", "міняємо в темряві", INK)
    step(rx, 2, "digit_on(next)", "відкрили потрібний", INK)
    b2, _, _ = textbox(rx + laneW / 2, axY + 118,
                       "доки міняємо сегменти, ЖОДЕН розряд не світить\n→ на екран не потрапляє нічого чужого",
                       size=10, fill="#eef6ef", stroke=FIELD)
    f.append(b2)

    # нижній підсумок
    b3, _, _ = textbox(W / 2, H - 40,
                       "різниця — лише в тому, що «погасити все» стоїть ПЕРШИМ:\n"
                       "перекриття «старий розряд відкритий + нові сегменти» зникає, а з ним і примара",
                       size=11, fill=FILL, stroke=INK)
    f.append(b3)

    render(os.path.join(IMG, "scan-timing.svg"), W, H, *f)


if __name__ == "__main__":
    fig_anatomy()
    fig_wiring()
    fig_bitmap()
    fig_scan_timing()
    print("OK: 4 figures ->", IMG)

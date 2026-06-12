# -*- coding: utf-8 -*-
"""
Фігури для вставки ch23-s3-a-reentrancy.md
Рис. 4.5.3a.3 — Механізм нереентерабельності: два потоки входять в одну функцію
Рис. 4.5.3a.4 — Таблиця-класифікатор: небезпечні функції в ISR і їх заміни

Чистий Python, без сторонніх залежностей. Вивід → ./img/.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.5.3a.3 — Механізм нереентерабельності
# loop() (синій) і ISR (червоний) входять в ОДНУ функцію зі СПІЛЬНИМ станом
# ══════════════════════════════════════════════════════════════════════════════
def fig3a3_reentrancy():
    W, H = 780, 400
    frags = []

    # ── Заголовок ─────────────────────────────────────────────────────────────
    frags.append(text(W / 2, 28, "Нереентерабельність: один стан — два проходи", size=16, bold=True))

    # ── Часові доріжки ────────────────────────────────────────────────────────
    Y_LOOP = 95   # горизонталь loop()
    Y_ISR  = 215  # горизонталь ISR

    frags.append(text(54, Y_LOOP - 2, "loop()", size=12, bold=True, color=NEG, anchor="middle"))
    frags.append(text(54, Y_ISR  - 2, "ISR",    size=12, bold=True, color=POS, anchor="middle"))

    # Горизонтальні лінії — від 90 до 690
    frags.append(line(90, Y_LOOP, 690, Y_LOOP, color=NEG, sw=2.2))
    frags.append(line(90, Y_ISR,  690, Y_ISR,  color=POS, sw=2.2))

    # ── loop() входить у функцію (синій прямокутник) ──────────────────────────
    LX_S, LX_E = 130, 370     # початок і кінець «входу loop()»
    frags.append(rect(LX_S, Y_LOOP - 14, LX_E - LX_S, 28,
                      fill="#eaf0fd", stroke=NEG, sw=2, rx=6))
    frags.append(text((LX_S + LX_E) / 2, Y_LOOP + 5,
                      "strtok / malloc (в loop)", size=11, color=NEG, anchor="middle"))

    # ── ISR влітає ПОСЕРЕД виконання loop-функції ─────────────────────────────
    X_BREAK = 260   # момент переривання
    frags.append(line(X_BREAK, Y_LOOP, X_BREAK, Y_ISR - 14, color=POS, sw=1.8, dash="5,4"))
    frags.append(text(X_BREAK, (Y_LOOP + Y_ISR) / 2 - 6,
                      "↯ ISR влітає", size=10, color=POS, anchor="middle", bold=True))

    # ── ISR теж входить у ту саму функцію (червоний прямокутник) ─────────────
    IX_S, IX_E = 260, 460
    frags.append(rect(IX_S, Y_ISR - 14, IX_E - IX_S, 28,
                      fill="#fdecea", stroke=POS, sw=2, rx=6))
    frags.append(text((IX_S + IX_E) / 2, Y_ISR + 5,
                      "та сама strtok / malloc", size=11, color=POS, anchor="middle"))

    # ── Блок «Спільний внутрішній стан» по центру між доріжками ──────────────
    SX, SY = 390, (Y_LOOP + Y_ISR) / 2
    tb, sw_tb, sh_tb = textbox(SX, SY, "Спільний стан:\nстатичний *ptr\n(замок купи)",
                               size=11, fill="#fff6e0", stroke="#c0a020", sw=2)
    frags.append(tb)

    # Стрілки від обох прямокутників до спільного стану
    frags.append(arrow((LX_S + LX_E) / 2, Y_LOOP + 14,
                       SX, SY - sh_tb / 2 - 4, color=NEG, sw=1.6))
    frags.append(arrow((IX_S + IX_E) / 2, Y_ISR - 14,
                       SX, SY + sh_tb / 2 + 4, color=POS, sw=1.6))

    # ── loop() повертається — але стан уже зіпсований ─────────────────────────
    # Після IX_E — loop() «продовжує», але пунктирна лінія (битий стан)
    frags.append(line(IX_E, Y_ISR, 690, Y_ISR, color=POS, sw=2.2))   # ISR завершується

    # loop() «прокидається» після ISR
    frags.append(line(IX_E, Y_LOOP, 690, Y_LOOP, color=NEG, sw=2.2, dash="6,5"))
    frags.append(text(580, Y_LOOP - 16, "стан затерто!", size=10, color=POS, bold=True, anchor="middle"))

    # Підпис-результат — плашка
    tb2, _, _ = textbox(W / 2, 310,
                        "Зіпсовані дані / краш: не два примірники стану, а ОДИН на двох",
                        size=11, fill="#fdecea", stroke=POS, sw=2)
    frags.append(tb2)

    # Підсумок унизу
    frags.append(text(W / 2, 368,
                      "Та сама прихована гонка, що §4.5.6, — але захована всередині чужого коду.",
                      size=10, color=MUTED, anchor="middle"))

    render(os.path.join(OUT, "fig-23-3a-3-reentrancy.svg"), W, H, *frags,
           title=None)
    print("OK: fig-23-3a-3-reentrancy.svg")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.5.3a.4 — Таблиця-класифікатор
# Функція | Чому небезпечна в ISR | ISR-безпечна заміна
# ══════════════════════════════════════════════════════════════════════════════
def fig3a4_unsafe_table():
    W, H = 820, 370
    frags = []

    # ── Заголовок ─────────────────────────────────────────────────────────────
    frags.append(text(W / 2, 28, "Чому популярні виклики небезпечні в ISR — і чим їх замінити",
                      size=15, bold=True))

    # ── Колонки ───────────────────────────────────────────────────────────────
    COL_X   = [30, 220, 500]    # x-початки трьох стовпців
    COL_W   = [188, 278, 290]   # ширини
    HEADERS = ["Функція", "Чому небезпечна в ISR", "ISR-безпечна заміна"]
    COL_C   = [INK, POS, FIELD]  # кольори заголовків

    ROW_H   = 56     # висота рядка (крім заголовка)
    HEAD_Y  = 50     # y-центр заголовків
    FIRST_Y = 95     # y-центр першого рядка даних

    # Рядок заголовка
    for i, (hdr, col) in enumerate(zip(HEADERS, COL_C)):
        frags.append(rect(COL_X[i], HEAD_Y - 20, COL_W[i], 34,
                          fill="#f4f6f8", stroke=col, sw=2, rx=5))
        frags.append(text(COL_X[i] + COL_W[i] / 2, HEAD_Y + 4,
                          hdr, size=12, color=col, anchor="middle", bold=True))

    # ── Дані рядків ───────────────────────────────────────────────────────────
    rows = [
        ("strtok",
         "Статичний буфер:\nзберігає *ptr між викликами",
         "Парсити в loop();\nабо strtok_r (лише в loop)"),
        ("malloc / new / String",
         "Замок купи (heap lock):\nISR на FreeRTOS = краш",
         "Буфер фікс. розміру,\nвиділений у setup()"),
        ("printf / Serial.print",
         "Внутр. буфер + malloc,\nдо того ж повільно",
         "Прапорець/черга в ISR,\nдрук у loop()"),
        ("gmtime / localtime",
         "Статичний буфер\n(errno, результат)",
         "localtime_r / gmtime_r\nв loop(), не в ISR"),
    ]

    FILL_ROW  = "#fdf8f8"
    FILL_GOOD = "#f3faf4"

    for ri, (fn, why, fix) in enumerate(rows):
        cy = FIRST_Y + ri * ROW_H
        alt = ri % 2 == 1

        # Стовпець «Функція»
        frags.append(rect(COL_X[0], cy - ROW_H // 2 + 4, COL_W[0], ROW_H - 6,
                          fill="#f4f6f8" if alt else "#ebebeb", stroke=INK, sw=1, rx=4))
        frags.append(text(COL_X[0] + COL_W[0] / 2, cy + 5,
                          fn, size=12, color=INK, anchor="middle", bold=True))

        # Стовпець «Чому небезпечна» — червоний відтінок
        frags.append(fitbox(COL_X[1], cy - ROW_H // 2 + 4,
                            COL_W[1], ROW_H - 6, why,
                            size=11, fill=FILL_ROW, stroke=POS, sw=1, rx=4, color=INK))

        # Стовпець «ISR-безпечна заміна» — зелений відтінок
        frags.append(fitbox(COL_X[2], cy - ROW_H // 2 + 4,
                            COL_W[2], ROW_H - 6, fix,
                            size=11, fill=FILL_GOOD, stroke=FIELD, sw=1, rx=4, color=INK))

    # ── Підпис унизу ──────────────────────────────────────────────────────────
    tb, _, _ = textbox(W / 2, 335,
                       "Дивись не на швидкість, а на середній стовпець: прихований стан між викликами — ось небезпека.",
                       size=10, fill="#fff6e0", stroke="#c0a020", sw=1.5)
    frags.append(tb)

    render(os.path.join(OUT, "fig-23-3a-4-unsafe-table.svg"), W, H, *frags,
           title=None)
    print("OK: fig-23-3a-4-unsafe-table.svg")


if __name__ == "__main__":
    fig3a3_reentrancy()
    fig3a4_unsafe_table()

# -*- coding: utf-8 -*-
# Фігури теми «Пристрій керування: hardwired і мікропрограмний».
# svgkit імпортуємо (не копіюємо) — §5 AUTHORING.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Спільні відтінки (узгоджені з палітрою svgkit і сусідньою темою control-unit)
RED_F, RED = "#fdf4f4", POS          # логіка / АЛП-сигнали
GRN_F, GRN = "#f4f7f4", FIELD        # пам'ять / сховище
BLU_F, BLU = "#eef3fd", NEG          # адреса / керування послідовністю
GRY_F      = "#eef1f4"


# ── Фігура 1: внутрішня будова ЗАШИТОГО пристрою керування ──────────────────
def fig_hardwired():
    W, H = 720, 430
    frags = []

    # вхід: опкод з IR
    b, w1, h1 = textbox(110, 90, "опкод\n(з IR)", size=13, fill=RED_F, stroke=RED, bold=True)
    frags.append(b)

    # регістр стадії (лічильник кроків)
    b, w2, h2 = textbox(110, 250, "регістр\nстадії\n(крок 1..k)", size=13, fill=BLU_F, stroke=BLU, bold=True)
    frags.append(b)

    # велика комбінаційна сітка посередині
    gx, gy, gw, gh = 300, 60, 200, 300
    frags.append(rect(gx, gy, gw, gh, fill=RED_F, stroke=RED, sw=2))
    frags.append(text(gx + gw / 2, gy + 26, "комбінаційна логіка", size=14, bold=True, color=RED))
    frags.append(text(gx + gw / 2, gy + 48, "(сітка вентилів)", size=12, color=MUTED))
    # булеві рівняння всередині
    eqs = ["ALU_add = opcode·стадія3",
           "reg_wr  = (add+load)·стадіяK",
           "mem_rd  = load·стадія2",
           "…"]
    for i, e in enumerate(eqs):
        frags.append(text(gx + 14, gy + 90 + i * 34, e, size=11, color=INK, anchor="start"))

    # виходи: керувальні лінії
    b, w3, h3 = textbox(630, 130, "керувальні\nлінії\n(до АЛП,\nрегістрів,\nшини)", size=12, fill=GRY_F, stroke=LINE, bold=True)
    frags.append(b)

    # зворотний зв'язок: прапорці
    b, w4, h4 = textbox(630, 320, "прапорці\nZ C N V", size=12, fill=GRN_F, stroke=GRN, bold=True)
    frags.append(b)

    # стрілки
    frags.append(arrow(110 + w1 / 2, 90, gx, 110))                 # опкод -> сітка
    frags.append(arrow(110 + w2 / 2, 250, gx, 250))               # стадія -> сітка
    frags.append(arrow(gx + gw, 150, 630 - w3 / 2, 130))          # сітка -> сигнали
    # такт просуває стадію
    frags.append(arrow(110, 250 - h2 / 2, 110, 90 + h1 / 2, color=BLU))
    frags.append(text(70, 175, "+1 щотакту", size=11, color=BLU, anchor="middle"))
    # прапорці назад у сітку (для умовних)
    frags.append(arrow(630 - w4 / 2, 320, gx + gw, 300, color=GRN))
    frags.append(text(560, 300, "стан → умовні", size=10, color=GRN, anchor="middle"))

    frags.append(text(W / 2, H - 16,
                      "Сигнали = булеві функції від опкоду й номера стадії — застиглі у вентилях.",
                      size=12, color=MUTED))
    render(os.path.join(OUT, "hardwired-internal.svg"), W, H, *frags,
           title="Зашитий пристрій керування зсередини")


# ── Фігура 2: внутрішня будова МІКРОПРОГРАМНОГО пристрою керування ──────────
def fig_micro():
    W, H = 760, 470
    frags = []

    # μPC (адреса мікрокоманди)
    b, wpc, hpc = textbox(110, 110, "μPC\n(адреса\nмікрокоманди)", size=12, fill=BLU_F, stroke=BLU, bold=True)
    frags.append(b)

    # опкод -> початкова адреса
    b, wop, hop = textbox(110, 260, "опкод\n→ старт-адреса", size=12, fill=RED_F, stroke=RED, bold=True)
    frags.append(b)

    # сховище мікрокоманд (control store)
    sx, sy, sw, sh = 270, 70, 190, 260
    frags.append(rect(sx, sy, sw, sh, fill=GRN_F, stroke=GRN, sw=2))
    frags.append(text(sx + sw / 2, sy + 24, "сховище", size=14, bold=True, color=GRN))
    frags.append(text(sx + sw / 2, sy + 42, "мікрокоманд (ROM)", size=11, color=MUTED))
    # рядки-мікрокоманди
    for i in range(5):
        yy = sy + 70 + i * 36
        hl = (i == 2)
        frags.append(rect(sx + 14, yy, sw - 28, 26,
                          fill="#fff7e6" if hl else BG,
                          stroke=RED if hl else LINE, sw=1.6 if hl else 1))
        frags.append(text(sx + sw / 2, yy + 17, "1011·010·+", size=11,
                          color=INK, bold=hl))
    frags.append(text(sx + sw / 2, sy + sh - 8, "поточний рядок ▲", size=10, color=RED))

    # регістр мікрокоманди — розкладений на поля
    rx, ry = 520, 120
    fields = [("керувальні біти", RED_F, RED, 150),
              ("вибір умови", GRN_F, GRN, 100),
              ("наступна адреса", BLU_F, BLU, 130)]
    yy = ry
    for name, fl, st, ww in fields:
        frags.append(rect(rx, yy, ww, 42, fill=fl, stroke=st, sw=1.6))
        frags.append(fitbox(rx, yy, ww, 42, name, size=11, bold=True, fill=fl, stroke=st))
        yy += 52

    # виходи
    b, wsig, hsig = textbox(700, 141, "сигнали\nкерування", size=11, fill=GRY_F, stroke=LINE, bold=True)
    frags.append(b)

    # стрілки потоку
    frags.append(arrow(110 + wpc / 2, 110, sx, 150, color=BLU))       # μPC -> сховище (адреса)
    frags.append(arrow(110 + wop / 2, 260, sx, 250, color=RED))       # опкод -> сховище (старт)
    frags.append(arrow(sx + sw, 190, rx, ry + 20, color=INK))         # рядок -> регістр
    frags.append(arrow(rx + 150, ry + 21, 700 - wsig / 2, 141, color=RED))  # керувальні -> сигнали
    # наступна адреса назад у μPC (петля послідовності)
    frags.append(line(rx + 130, ry + 104 + 21, rx + 130, 400, color=BLU, sw=1.8))
    frags.append(line(rx + 130, 400, 110, 400, color=BLU, sw=1.8))
    frags.append(arrow(110, 400, 110, 110 + hpc / 2, color=BLU))
    frags.append(text(300, 392, "наступна адреса → μPC (крок за кроком)", size=11, color=BLU, anchor="start"))

    frags.append(text(W / 2, H - 14,
                      "Набір команд заданий ВМІСТОМ сховища; μPC читає мікрокоманди рядок за рядком.",
                      size=12, color=MUTED))
    render(os.path.join(OUT, "micro-internal.svg"), W, H, *frags,
           title="Мікропрограмний пристрій керування зсередини")


# ── Фігура 3: горизонтальна проти вертикальної мікрокоманди ─────────────────
def fig_hv():
    W, H = 720, 380
    frags = []

    # горизонтальна: багато вузьких бітів, кожен = один дріт
    frags.append(text(W / 2, 60, "Горизонтальна: 1 біт = 1 керувальна лінія (широке слово)",
                      size=13, bold=True, color=RED))
    hx, hy, cell = 60, 80, 44
    labels = ["ALU+", "ALU−", "wrR", "rdM", "wrM", "selA", "selB", "…"]
    for i, lb in enumerate(labels):
        on = i in (0, 2)
        frags.append(rect(hx + i * cell, hy, cell, 40,
                          fill="#fdecea" if on else BG, stroke=RED if on else LINE,
                          sw=1.8 if on else 1))
        frags.append(text(hx + i * cell + cell / 2, hy + 17, "1" if on else "0",
                          size=13, bold=True, color=RED if on else MUTED))
        frags.append(text(hx + i * cell + cell / 2, hy + 33, lb, size=9, color=MUTED))
    frags.append(text(W / 2, hy + 66, "прямо на дроти — без декодера, широко (десятки–сотні бітів)",
                      size=11, color=MUTED))

    # вертикальна: кілька закодованих полів + малий декодер
    frags.append(text(W / 2, 220, "Вертикальна: закодовані поля + малий декодер (вузьке слово)",
                      size=13, bold=True, color=BLU))
    vy = 240
    b, wf1, hf1 = textbox(150, vy + 20, "оп-код\n0110", size=12, fill=BLU_F, stroke=BLU, bold=True, min_w=90)
    frags.append(b)
    b, wf2, _ = textbox(280, vy + 20, "джерело\n010", size=12, fill=BLU_F, stroke=BLU, bold=True, min_w=90)
    frags.append(b)
    b, wf3, _ = textbox(410, vy + 20, "приймач\n011", size=12, fill=BLU_F, stroke=BLU, bold=True, min_w=90)
    frags.append(b)
    b, wd, hd = textbox(600, vy + 20, "декодер\n→ дроти", size=12, fill=RED_F, stroke=RED, bold=True)
    frags.append(b)
    frags.append(arrow(410 + wf3 / 2, vy + 20, 600 - wd / 2, vy + 20))
    frags.append(text(W / 2, vy + 78,
                      "компактно, але потрібен зайвий крок розкодування полів у сигнали",
                      size=11, color=MUTED))

    render(os.path.join(OUT, "horizontal-vertical.svg"), W, H, *frags,
           title="Дві форми мікрокоманди")


# ── Фігура 4: одна ISA на двох різних трактах (Model 30 vs Model 50) ─────────
def fig_family_datapaths():
    W, H = 760, 470
    frags = []

    # спільна команда згори
    b, wc, hc = textbox(W / 2, 78, "одна машинна команда: A(32) + B(32) → S(32)",
                        size=13, fill=GRY_F, stroke=LINE, bold=True, min_w=430)
    frags.append(b)

    # ── ЛІВА колонка: Model 30, байтовий тракт ──
    lx = 60
    frags.append(text(lx + 150, 140, "Model 30 — дешева, повільна", size=13, bold=True, color=NEG))
    frags.append(rect(lx, 155, 300, 250, fill=BLU_F, stroke=NEG, sw=1.6))
    # сховище + довга мікропрограма
    frags.append(fitbox(lx + 20, 175, 120, 46, "сховище\n(CCROS)", size=11, bold=True, fill=BG, stroke=NEG))
    frags.append(text(lx + 150, 198, "8-бітний суматор", size=12, bold=True, color=INK, anchor="start"))
    # чотири байтові проходи
    for i in range(4):
        yy = 235 + i * 34
        frags.append(rect(lx + 20, yy, 260, 26, fill=BG, stroke=LINE, sw=1))
        frags.append(text(lx + 30, yy + 17,
                          "прохід %d: байт %d + байт %d + перенос" % (i + 1, i, i),
                          size=10, color=INK, anchor="start"))
    frags.append(text(lx + 150, 235 + 4 * 34 + 12,
                      "32 біти = 4 проходи по 8 → довга мікропрограма",
                      size=10, color=NEG))

    # ── ПРАВА колонка: Model 50, широкий тракт ──
    rx = 400
    frags.append(text(rx + 150, 140, "Model 50 — дорога, швидка", size=13, bold=True, color=POS))
    frags.append(rect(rx, 155, 300, 250, fill=RED_F, stroke=POS, sw=1.6))
    frags.append(fitbox(rx + 20, 175, 120, 46, "сховище\n(BCROS)", size=11, bold=True, fill=BG, stroke=POS))
    frags.append(text(rx + 150, 198, "32-бітний суматор", size=12, bold=True, color=INK, anchor="start"))
    frags.append(rect(rx + 20, 240, 260, 40, fill=BG, stroke=POS, sw=1.4))
    frags.append(text(rx + 150, 265, "один прохід: усі 32 біти разом", size=11, bold=True, color=INK))
    frags.append(rect(rx + 20, 295, 260, 30, fill="#fff7e6", stroke=POS, sw=1))
    frags.append(text(rx + 150, 315, "+ окремий байтовий mover паралельно", size=10, color=INK))
    frags.append(text(rx + 150, 235 + 4 * 34 + 12,
                      "коротка мікропрограма → менше тактів на ту саму команду",
                      size=10, color=POS))

    # стрілки від спільної команди вниз до обох
    frags.append(arrow(W / 2 - 120, 78 + hc / 2, lx + 150, 155, color=INK))
    frags.append(arrow(W / 2 + 120, 78 + hc / 2, rx + 150, 155, color=INK))

    frags.append(text(W / 2, H - 16,
                      "Та сама ISA лежить мікропрограмою — тож різне залізо виконує однакову команду.",
                      size=12, color=MUTED))
    render(os.path.join(OUT, "family-datapaths.svg"), W, H, *frags,
           title="Одна система команд на двох різних трактах")


# ── Фігура 5: родина System/360 — спектр заліза, спільна мова ────────────────
def fig_family_spectrum():
    W, H = 740, 360
    frags = []

    # спільна ISA — стрічка згори
    frags.append(rect(80, 60, 580, 40, fill=GRN_F, stroke=GRN, sw=2))
    frags.append(text(W / 2, 85, "СПІЛЬНА система команд System/360 (одна мова)",
                      size=13, bold=True, color=GRN))

    # вісь ціна/швидкість
    frags.append(line(80, 150, 660, 150, color=MUTED, sw=1.4))
    frags.append(text(90, 138, "дешево · повільно", size=11, color=NEG, anchor="start"))
    frags.append(text(650, 138, "дорого · швидко", size=11, color=POS, anchor="end"))

    # чотири моделі-стовпчики різної «висоти» (потужності)
    models = [("Model 30", "8-біт тракт\nCCROS", 60, NEG, BLU_F),
              ("Model 40", "TROS", 95, MUTED, GRY_F),
              ("Model 50", "32-біт тракт\nBCROS ~85 біт", 130, POS, RED_F),
              ("Model 65", "широкий\nшвидкий", 165, POS, RED_F)]
    x0, gap, bw = 130, 150, 96
    for i, (name, note, h, col, fl) in enumerate(models):
        cx = x0 + i * gap
        by = 300 - h
        frags.append(rect(cx - bw / 2, by, bw, h, fill=fl, stroke=col, sw=1.6))
        frags.append(text(cx, by - 8, name, size=12, bold=True, color=col))
        frags.append(fitbox(cx - bw / 2 + 4, 300 - 44, bw - 8, 40, note,
                            size=9, fill="none", stroke="none", color=INK))
        # кожна модель тягне мову зі спільної стрічки
        frags.append(arrow(cx, 100, cx, by, color=GRN, sw=1.4))

    frags.append(text(W / 2, H - 14,
                      "Мова — одна (мікрокод зводить до неї будь-яке залізо); реалізацій — багато.",
                      size=12, color=MUTED))
    render(os.path.join(OUT, "family-spectrum.svg"), W, H, *frags,
           title="Родина System/360: спектр заліза, спільна мова")


if __name__ == "__main__":
    fig_hardwired()
    fig_micro()
    fig_hv()
    fig_family_datapaths()
    fig_family_spectrum()
    print("OK: figures written to", OUT)

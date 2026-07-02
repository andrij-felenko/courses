# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

C_PROG = "#fdecea"; S_PROG = POS      # пам'ять програми — гаряча
C_DATA = "#eaf0fd"; S_DATA = NEG      # пам'ять даних — холодна
C_MAC  = "#eaf6ef"; S_MAC  = FIELD    # блок множення-накопичення
C_COEF = "#fef6e9"; S_COEF = "#b8860b"  # коефіцієнти


def blk(cx, cy, label, fill, stroke, w=150, h=48, size=13):
    x, y = cx - w / 2, cy - h / 2
    lines = label.split("\n")
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.8, rx=7)
    out += mtext(cx, cy - (len(lines) - 1) * size * 0.65 + size * 0.35, lines,
                 size=size, color=stroke, bold=True)
    return out


# ── 1. von Neumann vs Harvard: одна шина проти двох ──────────────────────────
def fig_vn_vs_harvard():
    W, H = 780, 340
    p = []
    p.append(text(W / 2, 28, "Одна шина (фон Нейман) проти двох (Гарвард)", size=16, bold=True))

    # ліва панель — фон Нейман: одна пам'ять, одна шина
    p.append(rect(40, 52, 330, 250, fill="#f7f8fb", stroke=MUTED, sw=1.6, rx=10))
    p.append(text(205, 76, "Фон Нейман", size=14, color=INK, bold=True))
    p.append(blk(205, 120, "Процесор", FILL, INK, w=150, h=44))
    p.append(blk(205, 240, "Пам'ять\n(програма + дані)", C_DATA, S_DATA, w=210, h=52, size=12))
    # одна шина
    p.append(line(205, 142, 205, 214, color=INK, sw=3))
    p.append(text(224, 182, "одна шина", size=11, color=POS, bold=True, anchor="start"))
    p.append(text(205, 288, "команда АБО дані — по черзі (вузьке місце)",
                  size=10.5, color=POS, italic=True))

    # права панель — Гарвард: дві пам'яті, дві шини
    p.append(rect(410, 52, 330, 250, fill="#f7fbf8", stroke=FIELD, sw=1.6, rx=10))
    p.append(text(575, 76, "Гарвард", size=14, color=INK, bold=True))
    p.append(blk(575, 120, "Процесор", FILL, INK, w=150, h=44))
    p.append(blk(490, 240, "Пам'ять\nпрограми", C_PROG, S_PROG, w=118, h=52, size=12))
    p.append(blk(662, 240, "Пам'ять\nданих", C_DATA, S_DATA, w=118, h=52, size=12))
    p.append(line(540, 142, 500, 214, color=S_PROG, sw=3))
    p.append(line(610, 142, 652, 214, color=S_DATA, sw=3))
    p.append(text(575, 182, "дві шини", size=11, color=FIELD, bold=True))
    p.append(text(575, 288, "команду І дані — одночасно",
                  size=10.5, color=FIELD, italic=True))
    render(os.path.join(OUT, "vn-vs-harvard.svg"), W, H, *p)


# ── 2. Три шини DSP: годують MAC щотакту ─────────────────────────────────────
def fig_three_bus():
    W, H = 780, 360
    p = []
    p.append(text(W / 2, 28, "Чому DSP має кілька шин: нагодувати MAC щотакту", size=15.5, bold=True))

    # три банки пам'яті вгорі
    p.append(blk(160, 90, "Пам'ять\nпрограми", C_PROG, S_PROG, w=150, h=52, size=12))
    p.append(blk(390, 90, "Дані X\n(вибірка)", C_DATA, S_DATA, w=150, h=52, size=12))
    p.append(blk(620, 90, "Дані Y\n(коеф.)", C_COEF, S_COEF, w=150, h=52, size=12))

    # блок MAC у центрі
    p.append(blk(390, 250, "MAC:  acc ← acc + x · h", C_MAC, S_MAC, w=320, h=64, size=15))

    # три стрілки вниз до MAC
    p.append(arrow(160, 116, 300, 222, color=S_PROG, sw=2.2))
    p.append(arrow(390, 116, 390, 218, color=S_DATA, sw=2.2))
    p.append(arrow(620, 116, 480, 222, color=S_COEF, sw=2.2))
    p.append(text(214, 168, "команда", size=10.5, color=S_PROG, bold=True))
    p.append(text(405, 170, "відлік x", size=10.5, color=S_DATA, bold=True, anchor="start"))
    p.append(text(566, 168, "коеф. h", size=10.5, color=S_COEF, bold=True, anchor="end"))

    p.append(text(W / 2, 312, "За один такт: дістати команду + два операнди й помножити-додати.",
                  size=12, color=INK, bold=True))
    p.append(text(W / 2, 334, "На одній шині це забрало б три-чотири такти — тому шин кілька.",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "three-bus.svg"), W, H, *p)


# ── 3. MAC-конвеєр на FIR: один відлік за такт ───────────────────────────────
def fig_mac_pipeline():
    W, H = 800, 320
    p = []
    p.append(text(W / 2, 28, "MAC-цикл фільтра: одне множення-додавання за такт", size=15.5, bold=True))
    cols0, cw = 150, 128
    ty = 66
    for i in range(5):
        p.append(text(cols0 + i * cw, ty, "такт %d" % (i + 1), size=11, color=MUTED, bold=True))
    steps = ["acc += x₀·h₀", "acc += x₁·h₁", "acc += x₂·h₂", "acc += x₃·h₃", "…"]
    y = 108
    for i, s in enumerate(steps):
        fc = C_MAC if i < 4 else "#f0f0f0"
        sc = S_MAC if i < 4 else MUTED
        cx = cols0 + i * cw
        x = cx - (cw - 16) / 2
        p.append(rect(x, y - 24, cw - 16, 48, fill=fc, stroke=sc, sw=1.6, rx=6))
        p.append(text(cx, y + 5, s, size=13, color=sc, bold=True))
        if i < 4:
            p.append(arrow(cx + (cw - 16) / 2, y, cx + cw - (cw - 16) / 2, y, color=MUTED, sw=1.6))

    p.append(text(W / 2, 176, "Кожен такт: узяти наступний відлік і коефіцієнт, помножити, додати до суми.",
                  size=12, color=INK, bold=True))
    # порівняння з GPU/CPU
    p.append(rect(90, 200, 620, 96, fill=FILL, stroke=MUTED, sw=1.4, rx=8))
    p.append(text(W / 2, 226, "На звичайному процесорі те саме — це LOAD, LOAD, MUL, ADD, лічильник, стрибок:",
                  size=11, color=INK, bold=True))
    p.append(text(W / 2, 248, "кілька команд на відлік. DSP робить усе це однією командою в апаратному циклі.",
                  size=11, color=INK, bold=True))
    p.append(text(W / 2, 274, "Саме тому фільтр на 256 коефіцієнтів іде ≈ 256 тактів, а не тисячу з гаком.",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "mac-pipeline.svg"), W, H, *p)


# ── 4. Кільцевий буфер: адреса сама завертається ─────────────────────────────
def fig_circular():
    W, H = 760, 340
    p = []
    p.append(text(W / 2, 28, "Кільцевий буфер: покажчик сам завертається на початок", size=15, bold=True))
    import math
    cx, cy, R = 380, 168, 92
    n = 8
    p.append(circle(cx, cy, R, fill="none", stroke=MUTED, sw=1.4))
    # клітинки по колу; «найновіша» — праворуч зверху, щоб підпис ліг у вільне поле
    newest = 1
    for i in range(n):
        ang = -math.pi / 2 + i * 2 * math.pi / n
        x = cx + R * math.cos(ang)
        y = cy + R * math.sin(ang)
        is_new = (i == newest)
        fc = C_MAC if is_new else C_DATA
        sc = S_MAC if is_new else S_DATA
        p.append(circle(x, y, 20, fill=fc, stroke=sc, sw=1.8))
        p.append(text(x, y + 4, "x%d" % i, size=11, color=sc, bold=True))
    # покажчик запису — назовні від «найновішої» клітинки
    ang = -math.pi / 2 + newest * 2 * math.pi / n
    px = cx + (R + 40) * math.cos(ang); py = cy + (R + 40) * math.sin(ang)
    p.append(text(px, py, "← запис", size=11, color=S_MAC, bold=True, anchor="start"))
    p.append(text(cx, cy - 4, "адреса++", size=12, color=INK, bold=True))
    p.append(text(cx, cy + 15, "по колу", size=11, color=MUTED))

    p.append(text(W / 2, 296, "Дійшовши кінця, адреса апаратно стає початком — без if і без модуля в циклі.",
                  size=11.5, color=INK, bold=True))
    p.append(text(W / 2, 320, "Новий відлік затирає найдавніший; вікно фільтра «їде» по сигналу задарма.",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "circular.svg"), W, H, *p)


# ── 5. Насичення проти загортання ────────────────────────────────────────────
def fig_saturate():
    W, H = 760, 340
    p = []
    p.append(text(W / 2, 28, "Переповнення: загорнути (звичайний CPU) чи насити (DSP)", size=15, bold=True))

    # ліва: загортання
    p.append(rect(50, 56, 330, 210, fill="#fdecea", stroke=POS, sw=1.7, rx=10))
    p.append(text(215, 82, "Загортання (wrap)", size=13, color=POS, bold=True))
    p.append(text(215, 108, "127 + 5  →  −124", size=14, color=INK, bold=True))
    p.append(text(215, 132, "макс. «перескакує» у мінус", size=10.5, color=INK))
    # мінізигзаг
    p.append(line(80, 200, 180, 160, color=POS, sw=2.2))
    p.append(line(180, 160, 182, 236, color=POS, sw=2.2, dash="4 3"))
    p.append(line(182, 236, 350, 196, color=POS, sw=2.2))
    p.append(text(215, 256, "у звуці — гучний тріск, сигнал зіпсовано",
                  size=10.5, color=POS, italic=True))

    # права: насичення
    p.append(rect(410, 56, 300, 210, fill="#eef7ef", stroke=FIELD, sw=1.7, rx=10))
    p.append(text(560, 82, "Насичення (saturate)", size=13, color=FIELD, bold=True))
    p.append(text(560, 108, "127 + 5  →  127", size=14, color=INK, bold=True))
    p.append(text(560, 132, "залипає на межі, не перескакує", size=10.5, color=INK))
    p.append(line(440, 200, 540, 160, color=FIELD, sw=2.2))
    p.append(line(540, 160, 680, 160, color=FIELD, sw=2.2))
    p.append(text(560, 256, "у звуці — м'яке обрізання, слух терпить",
                  size=10.5, color=FIELD, italic=True))

    p.append(text(W / 2, 296, "DSP насичує апаратно — межу тримає залізо, без жодної перевірки в коді.",
                  size=11.5, color=INK, bold=True))
    p.append(text(W / 2, 320, "Тому гучний звук на DSP не обертається на шум, а лише впирається у стелю.",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "saturate.svg"), W, H, *p)


# ── 6. Народження однокристального DSP: три чипи однієї гонки ─────────────────
def fig_first_dsp():
    W, H = 820, 430
    p = []
    p.append(text(W / 2, 28, "Хто перший: народження однокристального DSP (1978–1984)", size=15.5, bold=True))

    # спільний корінь — телефонія й мова
    root, rw, rh = textbox(W / 2, 66, "Корінь усіх трьох: телефонія й обробка мовлення —\nпотік відліків крізь фільтри, MAC щотакту",
                           size=11.5, pad=9, fill=C_COEF, stroke=S_COEF, color=INK)
    p.append(root)

    # вісь часу
    axy = 150
    p.append(line(60, axy, W - 60, axy, color=MUTED, sw=1.6))
    for yr, xx in [("1978", 120), ("1979", 250), ("1980", 400), ("1982", 600), ("1984", 740)]:
        p.append(line(xx, axy - 5, xx, axy + 5, color=MUTED, sw=1.4))
        p.append(text(xx, axy - 12, yr, size=11, color=MUTED, bold=True))

    # три головні картки під віссю, кожна зі своєю роллю
    b1, w1, h1 = textbox(250, 250,
                         "Bell Labs DSP-1\nтравень 1979 — перші зразки\nперший справжній однокристальний\nз апаратним MAC · лише всередині AT&T",
                         size=10.5, pad=9, fill=C_PROG, stroke=S_PROG, color=INK)
    p.append(b1)
    p.append(arrow(250, axy + 4, 250, 250 - h1 / 2, color=S_PROG, sw=1.8))

    b2, w2, h2 = textbox(430, 340,
                         "NEC µPD7720\nISSCC, лютий 1980\nперший, який можна купити\n(у продажу з 1981–82)",
                         size=10.5, pad=9, fill=C_DATA, stroke=S_DATA, color=INK)
    p.append(b2)
    p.append(arrow(400, axy + 4, 430, 340 - h2 / 2, color=S_DATA, sw=1.8))

    b3, w3, h3 = textbox(680, 250,
                         "TI TMS32010\nанонс 1982, поставки 1983–84\nринковий еталон · множення 200 нс\nпочаток родини TMS320",
                         size=10.5, pad=9, fill=C_MAC, stroke=S_MAC, color=INK)
    p.append(b3)
    p.append(arrow(680, axy + 4, 680, 250 - h3 / 2, color=S_MAC, sw=1.8))

    p.append(text(W / 2, 400, "Три різні «перші»: перший з апаратним MAC (DSP-1), перший у продажу (7720), перший еталон ринку (TMS32010).",
                  size=11, color=INK, bold=True))
    p.append(text(W / 2, 420, "Усіх трьох штовхала та сама потреба — гнати мову крізь фільтри в реальному часі.",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "first-dsp-timeline.svg"), W, H, *p)


# ── 7. Ціна завертання індексу кільцевого буфера (для proj-fir-mac) ──────────
def fig_wrap_cost():
    W, H = 820, 380
    p = []
    p.append(text(W / 2, 28, "Ціна завертання індексу кільцевого буфера", size=16, bold=True))
    p.append(text(W / 2, 50, "той самий крок «назад по кільцю» коштує зовсім різне",
                  size=11.5, color=MUTED, italic=True))

    rows = [
        ("(i - 1 + N) % N",
         "оператор %  —  апаратне ДІЛЕННЯ",
         "десятки тактів у гарячому циклі",
         C_PROG, S_PROG, "★★★  дорого"),
        ("(i - 1) & (N - 1)",
         "маска  —  одна дешева команда",
         "лише коли довжина N = 2ᵏ",
         C_COEF, S_COEF, "★  дешево"),
        ("hw-модульна адресація",
         "апаратне кільце DSP",
         "0 команд у циклі, будь-яке N",
         C_MAC, S_MAC, "◦  безкоштовно"),
    ]
    y0, rh, gap = 78, 82, 14
    lx, lw = 56, 250            # ліва колонка — код
    mx = lx + lw + 26          # опис
    mw = 300
    tx = mx + mw + 22          # цінник
    for i, (code, what, cond, fc, sc, tag) in enumerate(rows):
        y = y0 + i * (rh + gap)
        # код
        p.append(rect(lx, y, lw, rh, fill=fc, stroke=sc, sw=1.8, rx=8))
        p.append(text(lx + lw / 2, y + rh / 2 + 5, code, size=14, color=sc, bold=True))
        # опис + умова
        p.append(rect(mx, y, mw, rh, fill=FILL, stroke=MUTED, sw=1.4, rx=8))
        p.append(text(mx + 14, y + 32, what, size=12, color=INK, bold=True, anchor="start"))
        p.append(text(mx + 14, y + 56, cond, size=11, color=MUTED, italic=True, anchor="start"))
        # стрілка код → опис
        p.append(arrow(lx + lw, y + rh / 2, mx, y + rh / 2, color=sc, sw=2.0))
        # цінник
        p.append(text(tx, y + rh / 2 + 5, tag, size=12.5, color=sc, bold=True, anchor="start"))

    p.append(text(W / 2, H - 16,
                  "Що ближче до DSP — то дешевше завертання; апаратне кільце тримає темп «один MAC за такт».",
                  size=11, color=INK, bold=True))
    render(os.path.join(OUT, "wrap-cost.svg"), W, H, *p)


if __name__ == "__main__":
    fig_vn_vs_harvard()
    fig_three_bus()
    fig_mac_pipeline()
    fig_circular()
    fig_saturate()
    fig_first_dsp()
    fig_wrap_cost()
    print("OK: figs written to", OUT)

# -*- coding: utf-8 -*-
"""Фігури до статті «Як читати DC Characteristics у даташиті».
Три SVG у ./img/:
  anatomy.svg   — анатомія одного рядка таблиці (символ · умови · min/typ/max · одиниця)
  table.svg     — реальна таблиця 74HC00 на VCC=4.5 В із поясненням стовпців і рядків
  condition.svg — чому VOH залежить від умови: та сама «1» за різного струму IOH
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: anatomy.svg ───────────────────────────────────────────────────
# Один рядок таблиці, розібраний на частини: що означає кожна колонка.
def fig_anatomy():
    W, H = 880, 380
    f = [text(W / 2, 30, "Анатомія одного рядка DC-таблиці", size=17, bold=True)]
    f.append(text(W / 2, 52, "кожна клітинка — окреме питання; разом вони кажуть «що гарантовано і за яких умов»",
                  size=12, color=MUTED, italic=True))

    # ── сам рядок ──
    row_y = 96
    cells = [
        (60, 150, "VOH", "символ"),
        (210, 250, "VCC = 4.5 В\nIOH = −4 мА", "умови тесту"),
        (460, 90, "3.84", "Min"),
        (550, 90, "—", "Typ"),
        (640, 90, "—", "Max"),
        (730, 90, "В", "одиниця"),
    ]
    f.append(rect(60, row_y - 20, 760, 44, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=6))
    x = 60
    for cx, cw, val, _ in cells:
        f.append(line(cx, row_y - 20, cx, row_y + 24, color="#b9c7ea", sw=1.0))
        vlines = val.split("\n")
        fs = 13 if len(vlines) == 1 else 11
        f.append(mtext(cx + cw / 2, row_y - (len(vlines) - 1) * fs * 0.65 + 4,
                       vlines, size=fs, color=INK, bold=True))

    # ── підписи-виноски під кожною клітинкою ──
    notes = [
        (135, "ЩО міряємо:\nнапруга «1» на виході", NEG),
        (335, "ЗА ЯКИХ умов:\nживлення й струм\nнавантаження", "#8a5a1d"),
        (505, "гарантована\nмежа —\nбрати ЇЇ", FIELD),
        (595, "«типово»:\nдовідково,\nне гарантія", MUTED),
        (685, "тут порожньо:\nдля VOH стеля\nне задається", MUTED),
        (775, "у чому\nчисло", INK),
    ]
    for cx, s, col in notes:
        f.append(line(cx, row_y + 24, cx, row_y + 44, color=col, sw=1.2))
        f.append(mtext(cx, row_y + 58, s, size=10, color=col))

    # ── два висновки внизу ──
    f.append(fitbox(70, 250, 360, 96,
                    "«Min» для ВИХОДУ «1» і ВХОДУ «1» — це підлога:\n"
                    "драйвер дасть не менше, приймач вимагає не менше.\n"
                    "Беремо саме межу, ніколи «Typ».",
                    size=11, fill="#eafaf0", stroke=FIELD, color=INK))
    f.append(fitbox(450, 250, 370, 96,
                    "Число без умови — не число.\n"
                    "VOH = 3.84 В дійсне ЛИШЕ доти, доки з виходу\n"
                    "витягають не більше 4 мА. Інший струм — інша межа.",
                    size=11, fill="#fff6e0", stroke="#b5732e", color=INK))
    render(os.path.join(IMG, "anatomy.svg"), W, H, *f)


# ── Фігура 2: table.svg ─────────────────────────────────────────────────────
# Реальна (скорочена) таблиця DC для 74HC00 на VCC = 4.5 В.
def fig_table():
    W, H = 900, 470
    f = [text(W / 2, 30, "DC Characteristics 74HC (CMOS-логіка), VCC = 4.5 В", size=17, bold=True)]
    f.append(text(W / 2, 52, "скорочено до суті — реальні гарантовані числа й що кожне з них каже",
                  size=12, color=MUTED, italic=True))

    x0, y0 = 40, 74
    colx = [x0 + 8, x0 + 250, x0 + 355, x0 + 445, x0 + 520, x0 + 730]
    heads = ["символ", "параметр", "Min", "Max", "од.", "умови тесту"]
    tw = 820

    # ── шапка ──
    f.append(rect(x0, y0, tw, 30, fill="#dfe7fb", stroke=NEG, sw=1.6, rx=6))
    for i, h in enumerate(heads):
        anc = "start"
        f.append(text(colx[i], y0 + 20, h, size=12, color=NEG, bold=True, anchor=anc))

    rows = [
        ("VIH", "вхід читає «1» від", "3.15", "—", "В", "VI на межі спрацювання", "#eaf3ff"),
        ("VIL", "вхід читає «0» до", "—", "1.35", "В", "VI на межі спрацювання", "#ffffff"),
        ("VOH", "вихід «1» не нижче", "4.4", "—", "В", "IOH = −20 мкА (майже без струму)", "#eaf3ff"),
        ("VOH", "вихід «1» не нижче", "3.84", "—", "В", "IOH = −4 мА (під навантаженням)", "#ffffff"),
        ("VOL", "вихід «0» не вище", "—", "0.1", "В", "IOL = 20 мкА (майже без струму)", "#eaf3ff"),
        ("VOL", "вихід «0» не вище", "—", "0.33", "В", "IOL = 4 мА (під навантаженням)", "#ffffff"),
        ("II", "струм витоку входу", "—", "±1", "мкА", "VI = VCC або GND", "#eaf3ff"),
        ("ICC", "струм спокою чипа", "—", "20", "мкА", "входи на VCC/GND, виходи без струму", "#ffffff"),
    ]
    ry = y0 + 30
    rh = 30
    for sym, par, mn, mx, u, cond, bg in rows:
        f.append(rect(x0, ry, tw, rh, fill=bg, stroke="#e2e8f0", sw=1.0))
        f.append(text(colx[0], ry + 20, sym, size=12, color=INK, bold=True, anchor="start"))
        f.append(text(colx[1], ry + 20, par, size=11, color=INK, anchor="start"))
        mncol = FIELD if mn != "—" else MUTED
        mxcol = POS if mx != "—" else MUTED
        f.append(text(colx[2], ry + 20, mn, size=12, color=mncol, bold=(mn != "—"), anchor="start"))
        f.append(text(colx[3], ry + 20, mx, size=12, color=mxcol, bold=(mx != "—"), anchor="start"))
        f.append(text(colx[4], ry + 20, u, size=11, color=INK, anchor="start"))
        f.append(text(colx[5], ry + 20, cond, size=10, color="#8a5a1d", anchor="start"))
        ry += rh
    f.append(rect(x0, y0, tw, 30 + len(rows) * rh, fill="none", stroke=NEG, sw=1.6, rx=6))

    # ── дві виноски внизу ──
    ny = ry + 18
    f.append(fitbox(x0, ny, 400, 78,
                    "Два рядки VOH (і два VOL) — не помилка.\n"
                    "Той самий вихід дає РІЗНУ «1» залежно від струму:\n"
                    "майже без навантаження — 4.4 В, під 4 мА — уже 3.84 В.",
                    size=10, fill="#fff6e0", stroke="#b5732e", color=INK))
    f.append(fitbox(x0 + 420, ny, 400, 78,
                    "II (±1 мкА) — вхід майже нічого не тягне: один вихід\n"
                    "живить сотні входів. ICC (20 мкА) — увесь чип у спокої\n"
                    "п'є мікроампери: CMOS платить струмом лише за перемикання.",
                    size=10, fill="#eafaf0", stroke=FIELD, color=INK))
    render(os.path.join(IMG, "table.svg"), W, H, *f)


# ── Фігура 3: condition.svg ─────────────────────────────────────────────────
# Чому VOH «пливе»: та сама «1» просідає, коли з виходу тягнуть більший струм.
def fig_condition():
    W, H = 820, 400
    f = [text(W / 2, 30, "Чому в таблиці два рядки VOH: рівень залежить від струму", size=17, bold=True)]
    f.append(text(W / 2, 52, "вихід — не ідеальне джерело, а транзистор з опором; більший струм — більше падіння",
                  size=12, color=MUTED, italic=True))

    # ── осі ──
    ox, oy = 120, 320          # початок осей
    ax_w, ax_h = 560, 220
    f.append(arrow(ox, oy, ox + ax_w, oy, color=INK, sw=1.6))          # X: струм IOH
    f.append(arrow(ox, oy, ox, oy - ax_h, color=INK, sw=1.6))          # Y: напруга VOH
    f.append(text(ox + ax_w - 10, oy + 30, "струм навантаження |IOH|, мА", size=11, color=INK, anchor="end"))
    f.append(text(ox - 100, oy - ax_h - 4, "VOH на виході, В", size=11, color=INK, anchor="start"))

    # рівень живлення VCC = 4.5 В (стеля)
    vcc_y = oy - ax_h + 10
    f.append(line(ox, vcc_y, ox + ax_w, vcc_y, color=MUTED, sw=1.2, dash="5,4"))
    f.append(text(ox + ax_w, vcc_y - 6, "VCC = 4.5 В", size=11, color=MUTED, anchor="end"))

    # поріг приймача VIH = 3.15 В
    vih_y = oy - ax_h * (3.15 - 0.0) / 5.0 * (ax_h / ax_h)  # мапимо 0..5 В на висоту
    def vy(volts):
        return oy - ax_h * volts / 5.0
    vih_y = vy(3.15)
    f.append(line(ox, vih_y, ox + ax_w, vih_y, color=POS, sw=1.3, dash="6,4"))
    f.append(text(ox + 6, vih_y - 6, "VIH приймача = 3.15 В — нижче цього «1» вже не читається",
                  size=10, color=POS, anchor="start"))

    # крива спадання VOH зі струмом (спрощена, монотонна)
    def ix(ma):
        return ox + ax_w * ma / 8.0
    pts = [(0.02, 4.4), (1.0, 4.2), (2.0, 4.05), (4.0, 3.84), (6.0, 3.5), (8.0, 3.0)]
    d = "M %.1f %.1f" % (ix(pts[0][0]), vy(pts[0][1]))
    for ma, v in pts[1:]:
        d += " L %.1f %.1f" % (ix(ma), vy(v))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, NEG))
    f.append(text(ix(0.02) + 4, vy(4.4) - 8, "VOH", size=12, color=NEG, bold=True, anchor="start"))

    # дві контрольні точки з даташита
    for ma, v, lab in [(0.02, 4.4, "−20 мкА → 4.4 В"), (4.0, 3.84, "−4 мА → 3.84 В")]:
        f.append(circle(ix(ma), vy(v), 5, fill=NEG, stroke=BG, sw=1.5))
        f.append(text(ix(ma) + 8, vy(v) + 4, lab, size=10, color=NEG, anchor="start"))

    # мітки струму на осі X
    for ma in [0, 2, 4, 6, 8]:
        f.append(line(ix(ma), oy, ix(ma), oy + 5, color=INK, sw=1.0))
        f.append(text(ix(ma), oy + 20, str(ma), size=10, color=INK))

    # ── висновок ──
    f.append(fitbox(ox + 300, oy - 150, 250, 96,
                    "Тягнеш більше струму —\n«1» просідає до порога.\n"
                    "За ~8 мА VOH падає до 3.0 В —\nзапас над VIH майже з'їдено.\n"
                    "Тому межу беруть за СВІЙ струм.",
                    size=10, fill="#eafaf0", stroke=FIELD, color=INK))
    render(os.path.join(IMG, "condition.svg"), W, H, *f)


# ── Фігура 4: pick-column.svg (для вставки proj-read-datasheet) ──────────────
# Як вибрати стовпець живлення: бери найнижчий, що накриває твоє VCC у допуску.
def fig_pick_column():
    W, H = 900, 430
    f = [text(W / 2, 30, "Який стовпець живлення брати: найнижчий у робочому вікні", size=17, bold=True)]
    f.append(text(W / 2, 52, "номінал ± допуск дає вікно; читаємо стовпець за НАЙНИЖЧИМ краєм вікна — там виходи найслабші",
                  size=12, color=MUTED, italic=True))

    def mini_table(x0, y0, title, cols, chosen_idx, window_txt):
        g = [text(x0 + 150, y0 - 10, title, size=13, color=INK, bold=True)]
        cw, ch = 100, 30
        # шапка стовпців (напруги живлення)
        for i, c in enumerate(cols):
            cx = x0 + i * cw
            picked = (i == chosen_idx)
            bg = "#eafaf0" if picked else "#eef2f9"
            stk = FIELD if picked else "#c8d2e6"
            g.append(rect(cx, y0, cw, ch, fill=bg, stroke=stk, sw=2.0 if picked else 1.0))
            g.append(text(cx + cw / 2, y0 + 20, c, size=13, color=(FIELD if picked else INK),
                          bold=picked))
        # рядок-приклад VOH під кожним стовпцем (найгірше — у найнижчому)
        vals = ["слабший", "…", "кращий"] if len(cols) == 3 else ["слабший", "кращий"]
        for i in range(len(cols)):
            cx = x0 + i * cw
            picked = (i == chosen_idx)
            g.append(rect(cx, y0 + ch, cw, ch, fill=("#f6fdf9" if picked else BG),
                          stroke="#e2e8f0", sw=1.0))
            g.append(text(cx + cw / 2, y0 + ch + 19, "VOH " + vals[i], size=10,
                          color=(FIELD if picked else MUTED)))
        # позначка обраного
        cx = x0 + chosen_idx * cw
        g.append(arrow(cx + cw / 2, y0 + 2 * ch + 40, cx + cw / 2, y0 + 2 * ch + 12,
                       color=FIELD, sw=2.0))
        g.append(text(cx + cw / 2, y0 + 2 * ch + 56, "твій стовпець", size=11, color=FIELD, bold=True))
        # напис про вікно живлення
        g.append(fitbox(x0, y0 + 2 * ch + 74, len(cols) * cw, 44, window_txt,
                        size=10, fill="#f4f6f8", stroke="#c8d2e6", color=INK))
        return g

    f += mini_table(70, 110, "74HC — стовпці 2 / 4.5 / 6 В",
                    ["2.0 В", "4.5 В", "6.0 В"], 1,
                    "живлення 5 В ± 10 % → вікно 4.5…5.5 В\nнайнижчий край 4.5 В → стовпець 4.5 В")
    f += mini_table(520, 110, "LVCMOS — стовпці 3.0 / 3.3 / 3.6 В",
                    ["3.0 В", "3.3 В", "3.6 В"], 0,
                    "живлення 3.3 В ± 5 % → вікно 3.135…3.465 В\nнайнижчий край 3.135 В → стовпець 3.0 В")
    render(os.path.join(IMG, "pick-column.svg"), W, H, *f)


# ── Фігура 5: cross-family.svg (для вставки proj-read-datasheet) ─────────────
# Той самий 3.3 В драйвер у два різні 5 В входи: HCT проходить, HC — ні.
def fig_cross_family():
    W, H = 820, 470
    f = [text(W / 2, 30, "Той самий 3.3 В драйвер → два різні 5 В входи", size=17, bold=True)]
    f.append(text(W / 2, 52, "«1» драйвера одна (VOH ≈ 2.8 В); проходить вона чи ні — вирішує ПОРІГ входу приймача",
                  size=12, color=MUTED, italic=True))

    # спільна вертикальна шкала напруг 0..3.5 В
    sx, sy0, sy1 = 120, 360, 90     # x осі, низ (0 В), верх
    vmax = 3.5

    def vy(v):
        return sy0 - (sy0 - sy1) * v / vmax

    # вісь
    f.append(arrow(sx, sy0, sx, sy1 - 6, color=INK, sw=1.6))
    f.append(text(sx - 60, sy1 - 10, "напруга, В", size=11, color=INK, anchor="start"))
    for v in [0, 1, 2, 3]:
        f.append(line(sx - 5, vy(v), sx, vy(v), color=INK, sw=1.0))
        f.append(text(sx - 12, vy(v) + 4, str(v), size=10, color=INK, anchor="end"))

    # рівень «1» драйвера — спільна пунктирна лінія через усю фігуру
    voh = 2.8
    f.append(line(sx, vy(voh), W - 40, vy(voh), color=NEG, sw=1.8, dash="6,4"))
    f.append(circle(sx, vy(voh), 5, fill=NEG, stroke=BG, sw=1.5))
    f.append(text(sx + 8, vy(voh) - 8, "VOH драйвера ≈ 2.8 В  («1» з 3.3 В LVCMOS)",
                  size=11, color=NEG, bold=True, anchor="start"))

    # два приймачі: HCT (поріг 2.0) і HC (поріг 3.15)
    def receiver(cx, name, vih, ok, note):
        col = FIELD if ok else POS
        g = [text(cx, sy0 + 34, name, size=13, color=INK, bold=True)]
        # поріг VIH приймача — горизонтальна риска на своїй висоті
        g.append(line(cx - 70, vy(vih), cx + 70, vy(vih), color=col, sw=2.2))
        g.append(text(cx, vy(vih) + (16 if ok else -8),
                      "VIH = %.2f В" % vih, size=11, color=col, bold=True))
        # стрілка запасу/розриву між VOH драйвера і порогом
        ay = vy(voh); by = vy(vih)
        g.append(arrow(cx, ay, cx, by, color=col, sw=2.0))
        gap = voh - vih
        lab = ("запас +%.2f В" % gap) if ok else ("розрив %.2f В" % gap)
        midy = (ay + by) / 2
        g.append(text(cx + 78, midy + 4, lab, size=11, color=col, bold=True, anchor="start"))
        g.append(fitbox(cx - 90, sy0 + 46, 180, 40, note, size=10,
                        fill=("#eafaf0" if ok else "#fdecea"),
                        stroke=col, color=INK))
        return g

    f += receiver(340, "приймач 74HCT", 2.0, True,
                  "поріг 2.0 В нижчий за 2.8 В\n→ «1» проходить")
    f += receiver(620, "приймач 74HC", 3.15, False,
                  "поріг 3.15 В вищий за 2.8 В\n→ «1» НЕ дотягується")
    render(os.path.join(IMG, "cross-family.svg"), W, H, *f)


if __name__ == "__main__":
    fig_anatomy()
    fig_table()
    fig_condition()
    fig_pick_column()
    fig_cross_family()
    print("OK: anatomy, table, condition, pick-column, cross-family -> img/")

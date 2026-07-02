# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольори стадій — узгоджені з темою «Конвеєр» у цій же галузі
C_FETCH = "#fdecea"; S_FETCH = POS          # Виб
C_DEC   = "#eef1f4"; S_DEC   = MUTED        # Дек
C_EXE   = "#eaf6ef"; S_EXE   = FIELD        # Вик
C_MEM   = "#eaf0fd"; S_MEM   = NEG          # Пам
C_WB    = "#f0f0f0"; S_WB    = INK          # Зап
DEAD    = "#fbe9e7"

FIVE = [("Виб", C_FETCH, S_FETCH), ("Дек", C_DEC, S_DEC), ("Вик", C_EXE, S_EXE),
        ("Пам", C_MEM, S_MEM), ("Зап", C_WB, S_WB)]


def stage(cx, cy, label, fill, stroke, w=64, h=30):
    x, y = cx - w / 2, cy - h / 2
    return (rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.5, rx=5)
            + text(cx, cy + 5, label, size=11, color=stroke, bold=True))


def bubble(cx, cy, w=64, h=30):
    x, y = cx - w / 2, cy - h / 2
    return (rect(x, y, w, h, fill="#f7f7f7", stroke=MUTED, sw=1.3, rx=5)
            + text(cx, cy + 5, "бульб.", size=10, color=MUTED, italic=True))


# ── 1. Проблема: результат записується пізно, а потрібен рано ─────────────────
def fig_problem():
    W, H = 820, 340
    p = []
    p.append(text(W / 2, 28, "Проблема: запис у регістр пізно, а читання потрібне рано", size=15, bold=True))
    cols0, cw = 170, 66
    for i in range(7):
        p.append(text(cols0 + i * cw, 66, "т%d" % (i + 1), size=10, color=MUTED, bold=True))
    # ДОДАЙ R3 ← ... : пише R3 у стадії Зап (т5)
    y1 = 92
    p.append(text(cols0 - 16, y1 + 4, "ДОДАЙ R3←…", size=10.5, color=INK, bold=True, anchor="end"))
    for s, (lab, fc, sc) in enumerate(FIVE):
        p.append(stage(cols0 + s * cw, y1, lab, fc, sc, w=cw - 8))
    # ВІДНІМИ ← R3 : читає R3 у стадії Дек (т3) — а він ще не записаний
    y2 = 150
    p.append(text(cols0 - 16, y2 + 4, "ВІДНІМИ ←R3", size=10.5, color=POS, bold=True, anchor="end"))
    for s, (lab, fc, sc) in enumerate(FIVE):
        p.append(stage(cols0 + (s + 1) * cw, y2, lab, fc, sc, w=cw - 8))
    # маркер «пише R3» на т5 (Зап першої)
    xw = cols0 + 4 * cw
    p.append(circle(xw, y1, 5, fill=INK, stroke=INK))
    p.append(text(xw, y1 - 12, "R3 записано аж тут (т5)", size=10, color=INK, bold=True))
    # маркер «читає R3» на т3 (Дек другої)
    xr = cols0 + 2 * cw
    p.append(circle(xr, y2, 5, fill=POS, stroke=POS))
    p.append(text(xr, y2 + 22, "а R3 потрібне вже тут (т3)", size=10, color=POS, bold=True))
    # стрілка «назад у часі» — так не можна
    p.append(line(xw, y1 + 8, xr, y2 - 8, color=POS, sw=1.8, dash="5 4"))
    p.append(text((xw + xr) / 2 + 70, (y1 + y2) / 2, "дані мали б «поїхати назад у часі»", size=10, color=POS, italic=True, anchor="start"))
    p.append(text(W / 2, 250, "Наївно: чекати запису — це 2 порожні такти (бульбашки) на кожну таку пару.",
                  size=12, color=INK, bold=True))
    p.append(text(W / 2, 274, "Але ж результат уже полічений на виході АЛП у т3 — просто ще не доїхав до регістрів.",
                  size=11, color=MUTED, italic=True))
    p.append(text(W / 2, 298, "Навіщо ганяти його в регістр і назад, якщо можна подати прямо?",
                  size=11, color=FIELD, bold=True))
    render(os.path.join(OUT, "problem.svg"), W, H, *p)


# ── 2. Розв'язок: проброс із виходу АЛП назад на її вхід ─────────────────────
def fig_forward():
    W, H = 820, 340
    p = []
    p.append(text(W / 2, 28, "Проброс: результат із виходу АЛП — прямо на її вхід", size=15, bold=True))
    cols0, cw = 170, 66
    for i in range(7):
        p.append(text(cols0 + i * cw, 66, "т%d" % (i + 1), size=10, color=MUTED, bold=True))
    y1 = 96
    p.append(text(cols0 - 16, y1 + 4, "ДОДАЙ R3←…", size=10.5, color=INK, bold=True, anchor="end"))
    for s, (lab, fc, sc) in enumerate(FIVE):
        p.append(stage(cols0 + s * cw, y1, lab, fc, sc, w=cw - 8))
    y2 = 158
    p.append(text(cols0 - 16, y2 + 4, "ВІДНІМИ ←R3", size=10.5, color=FIELD, bold=True, anchor="end"))
    for s, (lab, fc, sc) in enumerate(FIVE):
        p.append(stage(cols0 + (s + 1) * cw, y2, lab, fc, sc, w=cw - 8))
    # проброс: кінець Вик першої (т3) → початок Вик другої (т4)
    x_from = cols0 + 2 * cw + (cw - 8) / 2          # правий край Вик першої
    x_to = cols0 + 3 * cw - (cw - 8) / 2            # лівий край Вик другої
    p.append(arrow(x_from, y1 + 16, x_to, y2 - 16, color=FIELD, sw=2.2))
    p.append(text((x_from + x_to) / 2 + 4, (y1 + y2) / 2 + 4, "проброс", size=11, color=FIELD, bold=True, anchor="start"))
    p.append(text(x_from, y1 - 12, "результат готовий на виході АЛП (т3)", size=10, color=INK, bold=True))
    p.append(text(x_to + 30, y2 + 22, "подано прямо на вхід АЛП (т4)", size=10, color=FIELD, bold=True, anchor="start"))
    p.append(text(W / 2, 250, "Жодної бульбашки: залежна команда рахує в т4 без затримки.",
                  size=12, color=INK, bold=True))
    p.append(text(W / 2, 274, "Регістровий файл теж оновиться (у т5), але чекати на це вже не треба —",
                  size=11, color=MUTED, italic=True))
    p.append(text(W / 2, 292, "свіже значення прийшло коротшим шляхом, в обхід (bypass) регістрів.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "forward.svg"), W, H, *p)


# ── 3. Межа: load-use — проброс не встигає, одна бульбашка неминуча ───────────
def fig_loaduse():
    W, H = 840, 360
    p = []
    p.append(text(W / 2, 28, "Межа пробросу: завантаження з пам'яті (load-use)", size=15, bold=True))
    cols0, cw = 180, 66
    for i in range(8):
        p.append(text(cols0 + i * cw, 66, "т%d" % (i + 1), size=10, color=MUTED, bold=True))
    # ВАНТАЖ R3 ← [пам] : дані з'являються лише в кінці Пам (т4)
    y1 = 96
    p.append(text(cols0 - 16, y1 + 4, "ВАНТАЖ R3←[…]", size=10, color=INK, bold=True, anchor="end"))
    for s, (lab, fc, sc) in enumerate(FIVE):
        p.append(stage(cols0 + s * cw, y1, lab, fc, sc, w=cw - 8))
    p.append(circle(cols0 + 3 * cw + (cw - 8) / 2, y1, 5, fill=NEG, stroke=NEG))
    p.append(text(cols0 + 3 * cw, y1 - 12, "дані з пам'яті готові лише тут (кінець т4)", size=10, color=NEG, bold=True))
    # залежна: одна бульбашка, тоді Вик у т5
    y2 = 176
    p.append(text(cols0 - 16, y2 + 4, "ВІДНІМИ ←R3", size=10, color=POS, bold=True, anchor="end"))
    p.append(stage(cols0 + 1 * cw, y2, "Виб", C_FETCH, S_FETCH, w=cw - 8))
    p.append(stage(cols0 + 2 * cw, y2, "Дек", C_DEC, S_DEC, w=cw - 8))
    p.append(bubble(cols0 + 3 * cw, y2, w=cw - 8))                 # вимушена затримка на т4
    p.append(stage(cols0 + 4 * cw, y2, "Вик", C_EXE, S_EXE, w=cw - 8))
    p.append(stage(cols0 + 5 * cw, y2, "Пам", C_MEM, S_MEM, w=cw - 8))
    p.append(stage(cols0 + 6 * cw, y2, "Зап", C_WB, S_WB, w=cw - 8))
    # проброс уже з кінця Пам (т4) на вхід Вик (т5) — але лише після однієї бульбашки
    x_from = cols0 + 3 * cw + (cw - 8) / 2
    x_to = cols0 + 4 * cw - (cw - 8) / 2
    p.append(arrow(x_from, y1 + 16, x_to, y2 - 16, color=FIELD, sw=2.2))
    p.append(text(x_to + 24, y2 - 20, "проброс — але вже після 1 бульбашки", size=10, color=FIELD, bold=True, anchor="start"))
    p.append(text(W / 2, 264, "АЛП хоче R3 на вході в т4, а пам'ять віддає його лише в кінці т4 — назад у часі знову не можна.",
                  size=11.5, color=INK, bold=True))
    p.append(text(W / 2, 288, "Тому load-use коштує рівно одну бульбашку, яку проброс прибрати не може: він скорочує затримку, не скасовує її.",
                  size=11, color=POS, bold=True))
    p.append(text(W / 2, 312, "Практичний висновок: не став команду, що читає завантажене значення, одразу за завантаженням.",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "loaduse.svg"), W, H, *p)


# ── 4. Мережа пробросу: звідки й куди ────────────────────────────────────────
def fig_network():
    W, H = 720, 380
    p = []
    p.append(text(W / 2, 28, "Мережа пробросу: результати ловлять на виходах і подають на вхід АЛП", size=13.5, bold=True))
    # АЛП у центрі
    alu_x, alu_y, alu_w, alu_h = 300, 150, 130, 70
    p.append(rect(alu_x, alu_y, alu_w, alu_h, fill=C_EXE, stroke=S_EXE, sw=2, rx=8))
    p.append(text(alu_x + alu_w / 2, alu_y + alu_h / 2 + 5, "АЛП (вхід)", size=13, color=S_EXE, bold=True))
    # джерела результатів праворуч
    src_x = 560
    srcs = [("вихід АЛП\n(попередня команда)", 90, FIELD),
            ("виведене з пам'яті\n(завантаження)", 170, NEG),
            ("готовий результат\nу стадії запису", 250, INK)]
    for lab, sy, col in srcs:
        b, w, h = textbox(src_x, sy, lab, size=10, pad=8, fill=FILL, stroke=col, sw=1.6)
        p.append(b)
        p.append(arrow(src_x - w / 2, sy, alu_x + alu_w + 6, alu_y + alu_h / 2, color=col, sw=1.8))
    # мультиплексор-вибирач ліворуч від АЛП
    mux_x = 190
    p.append(text(mux_x, alu_y + alu_h / 2 - 14, "вибирач", size=10.5, color=MUTED, bold=True))
    p.append(text(mux_x, alu_y + alu_h / 2 + 2, "(що подати:", size=9.5, color=MUTED))
    p.append(text(mux_x, alu_y + alu_h / 2 + 16, "регістр чи проброс)", size=9.5, color=MUTED))
    # звичайний шлях: регістровий файл знизу
    rf_x, rf_y = alu_x + alu_w / 2, 320
    b, w, h = textbox(rf_x, rf_y, "регістровий файл\n(звичайний, довший шлях)", size=10, pad=8, fill="#f6f8fb", stroke=MUTED, sw=1.5)
    p.append(b)
    p.append(arrow(rf_x, rf_y - h / 2, alu_x + alu_w / 2, alu_y + alu_h + 4, color=MUTED, sw=1.6))
    p.append(text(W / 2, 358, "Логіка щотакту питає: чи потрібне значення вже полічене «попереду»? Так — бере коротший шлях, ні — з регістра.",
                  size=10.5, color=INK, bold=True))
    render(os.path.join(OUT, "network.svg"), W, H, *p)


if __name__ == "__main__":
    fig_problem()
    fig_forward()
    fig_loaduse()
    fig_network()
    print("OK: figs written to", OUT)

# -*- coding: utf-8 -*-
"""Фігури до кроку «Пара Дарлінгтона проти Sziklai».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── символи транзисторів (база ліворуч, колектор/емітер праворуч) ────────────
def npn(cx, cy, label=None, lab_color=MUTED):
    """NPN: вертикальна планка бази, колектор угору-праворуч, емітер униз-праворуч (стрілка назовні)."""
    out = []
    bt, bb = cy - 20, cy + 20
    out.append(line(cx, bt, cx, bb, color=INK, sw=2.4))          # планка бази
    out.append(line(cx - 24, cy, cx, cy, color=INK, sw=1.8))     # вивід бази
    out.append(line(cx, bt + 5, cx + 20, bt - 11, color=INK, sw=1.8))   # до колектора
    out.append(line(cx + 20, bt - 11, cx + 20, bt - 24, color=INK, sw=1.8))
    out.append(line(cx, bb - 5, cx + 20, bb + 11, color=INK, sw=1.8))   # до емітера
    out.append(line(cx + 20, bb + 11, cx + 20, bb + 24, color=INK, sw=1.8))
    out.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>' % (
        cx + 11, bb + 2, cx + 20, bb + 11, cx + 10, bb + 10, INK))   # стрілка емітера (назовні)
    if label:
        out.append(text(cx - 6, cy - 2, label, size=12, color=lab_color, anchor="end", bold=True))
    return "".join(out)


def pnp(cx, cy, label=None, lab_color=MUTED):
    """PNP: планка бази, емітер угору-праворуч (стрілка ДО бази), колектор униз-праворуч."""
    out = []
    bt, bb = cy - 20, cy + 20
    out.append(line(cx, bt, cx, bb, color=INK, sw=2.4))          # планка бази
    out.append(line(cx - 24, cy, cx, cy, color=INK, sw=1.8))     # вивід бази
    out.append(line(cx, bt + 5, cx + 20, bt - 11, color=INK, sw=1.8))   # до емітера (вгору)
    out.append(line(cx + 20, bt - 11, cx + 20, bt - 24, color=INK, sw=1.8))
    out.append(line(cx, bb - 5, cx + 20, bb + 11, color=INK, sw=1.8))   # до колектора (вниз)
    out.append(line(cx + 20, bb + 11, cx + 20, bb + 24, color=INK, sw=1.8))
    # стрілка емітера PNP — вістрям ДО бази (всередину)
    out.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>' % (
        cx + 2, bt - 1, cx + 11, bt - 9, cx + 12, bt + 2, INK))
    if label:
        out.append(text(cx - 6, cy - 2, label, size=12, color=lab_color, anchor="end", bold=True))
    return "".join(out)


def dot(x, y):
    return '<circle cx="%.1f" cy="%.1f" r="3.2" fill="%s"/>' % (x, y, INK)


def gnd(x, y):
    return (line(x, y, x, y + 7, color=INK, sw=1.8)
            + line(x - 13, y + 7, x + 13, y + 7, color=INK, sw=2.2)
            + line(x - 8, y + 12, x + 8, y + 12, color=INK, sw=2.0)
            + line(x - 3, y + 17, x + 3, y + 17, color=INK, sw=1.8))


def rail(x1, x2, y, label):
    out = line(x1, x2, y, y, color=POS, sw=2.2) if False else line(x1, y, x2, y, color=POS, sw=2.2)
    out += text((x1 + x2) / 2, y - 8, label, size=12, color=POS, bold=True)
    return out


# ════════════════════════════════════════════════════════════════════════════
# Фіг.1 — дві топології поряд: Дарлінгтон (NPN+NPN) vs Sziklai (NPN+PNP, ЗЗ)
# ════════════════════════════════════════════════════════════════════════════
def fig_topologies():
    W, H = 820, 470
    f = [text(W / 2, 28, "Два способи зліпити «супертранзистор» із двох",
              size=17, bold=True)]

    # ── ЛІВО: пара Дарлінгтона (обидва NPN) ──
    cap1y = 60
    f.append(text(210, cap1y, "Пара Дарлінгтона  (NPN + NPN)", size=14, bold=True, color=NEG))
    Bx = 70                       # спільний вхід (база складеного)
    by = 250
    f.append(text(Bx - 4, by + 5, "B", size=13, bold=True, anchor="end"))
    f.append(line(Bx, by, Bx + 30, by, color=INK, sw=1.8))   # вхід → база T1
    t1x, t1y = 124, by
    t2x, t2y = 250, by + 30
    f.append(npn(t1x, t1y, "T1", NEG))
    f.append(npn(t2x, t2y, "T2", NEG))
    # емітер T1 → база T2
    e1x = t1x + 20
    f.append(line(e1x, t1y + 44, e1x, t2y, color=INK, sw=1.8))
    f.append(line(e1x, t2y, t2x - 24, t2y, color=INK, sw=1.8))
    f.append(dot(e1x, t2y))
    f.append(text((e1x + t2x) / 2, t2y + 16, "E1→B2", size=10, color=MUTED))
    # колектори разом → C
    c_top = 120
    c1x = t1x + 20
    c2x = t2x + 20
    f.append(line(c1x, t1y - 44, c1x, c_top, color=INK, sw=1.8))
    f.append(line(c2x, t2y - 44, c2x, c_top, color=INK, sw=1.8))
    f.append(line(c1x, c_top, c2x, c_top, color=INK, sw=1.8))
    f.append(dot(c2x, c_top))
    f.append(line(c2x, c_top, c2x + 40, c_top, color=INK, sw=1.8))
    f.append(text(c2x + 50, c_top + 5, "C", size=13, bold=True, anchor="start"))
    # спільний емітер униз → E
    e_bot = t2y + 70
    f.append(line(c2x, t2y + 44, c2x, e_bot, color=INK, sw=1.8))
    f.append(line(c2x, e_bot, 70, e_bot, color=INK, sw=1.8))
    f.append(text(60, e_bot + 4, "E", size=13, bold=True, anchor="end"))
    # підпис суті
    f.append(fitbox(40, e_bot + 24, 320, 52,
                    "β ≈ β₁·β₂  (тисячі)\nВхід «тягнуть» ДВА переходи поспіль → відкриття від ~1.2 В",
                    size=11, fill="#eaf0fd", stroke=NEG, color=INK))

    # розділова лінія
    f.append(line(W / 2, 48, W / 2, H - 20, color="#d0d4da", sw=1.4, dash="4,5"))

    # ── ПРАВО: пара Sziklai (NPN + PNP) ──
    # NPN-тип: T1 — вхідний NPN, T2 — вихідний PNP. Спільний КОЛЕКТОР = колектор PNP;
    # спільний ЕМІТЕР = емітер PNP (туди ж — емітер T1). Вхід «тягне» лише перехід T1.
    ox = 430
    f.append(text(ox + 175, cap1y, "Пара Sziklai  (NPN + PNP)", size=14, bold=True, color=POS))
    by2 = 250
    s1x, s1y = ox + 130, by2          # вхідний NPN (ліворуч)
    s2x, s2y = ox + 250, by2 - 50     # вихідний PNP (вище праворуч)
    # B → база T1
    f.append(text(ox + 56, by2 + 5, "B", size=13, bold=True, anchor="end"))
    f.append(line(ox + 60, by2, s1x - 24, by2, color=INK, sw=1.8))
    f.append(npn(s1x, s1y, "T1", POS))
    f.append(pnp(s2x, s2y, "T2", POS))
    # колектор T1 → база T2 (саме це й робить пару петлею зворотного зв'язку)
    c1x2 = s1x + 20
    f.append(line(c1x2, s1y - 44, c1x2, s2y, color=POS, sw=2.2))
    f.append(line(c1x2, s2y, s2x - 24, s2y, color=POS, sw=2.2))
    f.append(dot(c1x2, s2y))
    f.append(text((c1x2 + s2x) / 2, s2y - 9, "C1→B2", size=10, color=POS, bold=True))
    # спільний ЕМІТЕР: емітер PNP (верх) і емітер T1 (низ) сходяться праворуч і йдуть нагору до E.
    e1x2 = s1x + 20                  # емітер T1 (правий вивід униз)
    eep_x = s2x + 20                 # емітер PNP — верхній вивід
    e_riser_x = eep_x + 36           # права колонка-стояк для E (правіше за все)
    e_top_y = 90                     # верхній рівень шини E
    e_bot_y = s1y + 70               # вузол злиття емітерів (під T1)
    f.append(line(e1x2, s1y + 44, e1x2, e_bot_y, color=INK, sw=1.8))       # емітер T1 униз
    f.append(line(e1x2, e_bot_y, e_riser_x, e_bot_y, color=INK, sw=1.8))   # праворуч до стояка
    f.append(line(eep_x, s2y - 44, e_riser_x, s2y - 44, color=INK, sw=1.8))  # емітер PNP праворуч
    f.append(dot(e_riser_x, s2y - 44))
    f.append(line(e_riser_x, e_bot_y, e_riser_x, e_top_y, color=INK, sw=1.8))  # стояк E
    f.append(line(e_riser_x, e_top_y, e_riser_x + 40, e_top_y, color=INK, sw=1.8))
    f.append(text(e_riser_x + 50, e_top_y + 5, "E", size=13, bold=True, anchor="start"))
    # спільний КОЛЕКТОР = колектор PNP (нижній вивід) — окремо вниз
    cc2x = s2x + 20
    c_out_y = s2y + 90
    f.append(line(cc2x, s2y + 44, cc2x, c_out_y, color=INK, sw=1.8))
    f.append(line(cc2x, c_out_y, cc2x + 40, c_out_y, color=INK, sw=1.8))
    f.append(text(cc2x + 50, c_out_y + 5, "C", size=13, bold=True, anchor="start"))
    # підпис петлі
    f.append(text(ox + 150, e_bot_y + 24, "T1 КЕРУЄ струмом бази T2 — петля зворотного зв'язку",
                  size=10, color=POS))
    f.append(fitbox(ox + 10, e_bot + 24, 350, 52,
                    "β ≈ β₁·β₂  (теж тисячі)\nВхід «тягне» ОДИН перехід (T1) → відкриття від ~0.6 В",
                    size=11, fill="#fdecea", stroke=POS, color=INK))

    render(os.path.join(IMG, "two-topologies.svg"), W, H, *f)
    print("OK two-topologies.svg")


# ════════════════════════════════════════════════════════════════════════════
# Фіг.2 — стек падінь напруги: чому 1.2 В проти 0.6 В на вході
# ════════════════════════════════════════════════════════════════════════════
def fig_vbe():
    W, H = 760, 360
    f = [text(W / 2, 28, "Скільки напруги треба на вхід, щоб складений відкрився",
              size=17, bold=True)]

    def stack(cx, title, drops, total, color):
        out = [text(cx, 64, title, size=14, bold=True, color=color)]
        # «термометр» переходів, що стоять у вхідному ланцюзі
        top = 96
        seg_h = 54
        y = top
        for i, lab in enumerate(drops):
            out.append(rect(cx - 78, y, 156, seg_h, fill="#f4f6f8", stroke=color, sw=1.8, rx=5))
            out.append(text(cx, y + seg_h / 2 - 5, lab, size=12, bold=True))
            out.append(text(cx, y + seg_h / 2 + 13, "≈ 0.6 В", size=11, color=MUTED))
            y += seg_h + 8
        # сумарна стрілка збоку
        out.append(arrow(cx - 104, y - 8, cx - 104, top, color=color))
        out.append(text(cx - 116, (top + y) / 2, "вхід", size=11, color=color, anchor="end"))
        # підсумок
        out.append(rect(cx - 78, y + 6, 156, 34, fill=("#fdecea" if color == POS else "#eaf0fd"),
                        stroke=color, sw=2, rx=6))
        out.append(text(cx, y + 28, total, size=14, bold=True, color=color))
        return out, y

    s1, _ = stack(210, "Дарлінгтон: ДВА переходи поспіль",
                  ["Vbe(T1)", "Vbe(T2)"], "≈ 1.2 В", NEG)
    f += s1
    s2, _ = stack(550, "Sziklai: лише ОДИН перехід на вході",
                  ["Vbe(T1)"], "≈ 0.6 В", POS)
    f += s2
    f.append(line(W / 2, 56, W / 2, H - 56, color="#d0d4da", sw=1.4, dash="4,5"))
    f.append(fitbox(150, H - 42, 460, 30,
                    "Менший поріг входу = більший розмах виходу на тому ж живленні. Це головна перевага Sziklai.",
                    size=11, fill="#f0f7f1", stroke=FIELD, color=INK))
    render(os.path.join(IMG, "vbe-stack.svg"), W, H, *f)
    print("OK vbe-stack.svg")


# ════════════════════════════════════════════════════════════════════════════
# Фіг.3 — резистор «стоку» B–E: швидке закриття й чіткий поріг
# ════════════════════════════════════════════════════════════════════════════
def fig_bleed():
    W, H = 780, 360
    f = [text(W / 2, 28, "Навіщо резистор між базою й емітером вихідного транзистора",
              size=17, bold=True)]

    # зліва — без резистора: «застряглий» заряд
    lx = 120
    f.append(text(lx + 70, 62, "Без резистора", size=14, bold=True, color=POS))
    f.append(npn(lx + 70, 150, "Tвих", INK))
    f.append(text(lx - 10, 150, "база", size=11, color=MUTED, anchor="end"))
    f.append(line(lx, 150, lx + 46, 150, color=INK, sw=1.8))
    f.append(gnd(lx + 90, 230))
    f.append(line(lx + 90, 194, lx + 90, 230, color=INK, sw=1.8))
    f.append(fitbox(lx - 40, 264, 280, 64,
                    "Коли вхід зник, заряд у базі нікуди стікати — лише повільно розсмоктується сам.\nТранзистор закривається ЛІНИВО → завал на високих частотах.",
                    size=11, fill="#fdecea", stroke=POS, color=INK))

    f.append(line(W / 2, 50, W / 2, H - 16, color="#d0d4da", sw=1.4, dash="4,5"))

    # справа — з резистором: швидкий стік + чіткий поріг
    rx = 470
    f.append(text(rx + 70, 62, "З резистором R (100 Ом…1 кОм)", size=14, bold=True, color=FIELD))
    f.append(npn(rx + 70, 150, "Tвих", INK))
    f.append(line(rx, 150, rx + 46, 150, color=INK, sw=1.8))
    f.append(dot(rx + 20, 150))
    # резистор B→E
    f.append(rect(rx + 4, 176, 32, 44, fill="#eef1f5", stroke=INK, sw=1.6, rx=3))
    f.append(text(rx + 20, 202, "R", size=12, bold=True))
    f.append(line(rx + 20, 150, rx + 20, 176, color=INK, sw=1.8))
    f.append(line(rx + 20, 220, rx + 20, 250, color=INK, sw=1.8))
    f.append(line(rx + 90, 194, rx + 90, 250, color=INK, sw=1.8))
    f.append(line(rx + 20, 250, rx + 90, 250, color=INK, sw=1.8))
    f.append(dot(rx + 90, 250))
    f.append(gnd(rx + 90, 250))
    f.append(fitbox(rx - 40, 264, 300, 64,
                    "R дає заряду куди стекти → швидке закриття.\nІ задає чіткий поріг: поки спад на R < 0.6 В, вихідний ще закритий (гасить витоки й шум).",
                    size=11, fill="#f0f7f1", stroke=FIELD, color=INK))
    render(os.path.join(IMG, "bleed-resistor.svg"), W, H, *f)
    print("OK bleed-resistor.svg")


# ════════════════════════════════════════════════════════════════════════════
# Фіг.4 — квазікомплементарний вихід: NPN, «перевдягнений» у PNP
# ════════════════════════════════════════════════════════════════════════════
def fig_quasi():
    W, H = 820, 470
    f = [text(W / 2, 28, "Sziklai вдягає силовий NPN у «маску» PNP",
              size=17, bold=True)]
    top_y, mid_y, bot_y = 100, 210, 360

    # ліворуч — ідеальний комплементарний вихід (NPN зверху, PNP знизу)
    f.append(text(200, 64, "Ідеал: справжня пара NPN+PNP", size=13, bold=True))
    f.append(rail(120, 280, top_y, "+V"))
    f.append(npn(180, 152, "NPN", NEG))
    f.append(pnp(180, 268, "PNP", POS))
    f.append(line(200, 128, 200, top_y, color=INK, sw=1.8))    # колектор NPN → +V
    f.append(line(200, 292, 200, bot_y, color=INK, sw=1.8))    # колектор PNP → −V
    f.append(rail(120, 280, bot_y, "−V"))
    # вихід із середньої точки
    f.append(line(200, 176, 200, 244, color=INK, sw=1.8))
    f.append(dot(200, mid_y))
    f.append(line(200, mid_y, 300, mid_y, color=INK, sw=1.8))
    f.append(text(312, mid_y + 4, "вихід", size=12, bold=True, anchor="start"))
    f.append(fitbox(64, 392, 290, 56,
                    "Верх «штовхає», низ «тягне».\nГарно, та потужний PNP колись був дорогий і повільний.",
                    size=11, fill="#f4f6f8", stroke=MUTED, color=INK))

    f.append(line(W / 2, 52, W / 2, H - 14, color="#d0d4da", sw=1.4, dash="4,5"))

    # праворуч — квазікомплементарний: низ = Sziklai (PNP-драйвер + NPN-силовий)
    f.append(text(620, 64, "Квазі: низ — Sziklai з NPN-силовим", size=13, bold=True))
    f.append(rail(520, 760, top_y, "+V"))
    f.append(npn(600, 152, "NPN", NEG))
    f.append(line(620, 128, 620, top_y, color=INK, sw=1.8))
    f.append(line(620, 176, 620, mid_y, color=INK, sw=1.8))    # емітер NPN → вихід
    # нижнє плече: PNP-драйвер + NPN-силовий = Sziklai, що поводиться як PNP
    box_x, box_y, box_w, box_h = 558, 244, 156, 78
    f.append(rect(box_x, box_y, box_w, box_h, fill="#fdecea", stroke=POS, sw=1.6, rx=8))
    f.append(text(box_x + box_w / 2, box_y + 16, "Sziklai = «ніби PNP»", size=11, bold=True, color=POS))
    f.append(pnp(box_x + 44, box_y + 52, "драйв", POS))
    f.append(npn(box_x + 116, box_y + 52, "сила", NEG))
    f.append(line(620, mid_y, 620, box_y, color=INK, sw=1.8))            # вихід-точка → у блок
    f.append(line(box_x + box_w / 2, box_y + box_h, box_x + box_w / 2, bot_y, color=INK, sw=1.8))
    f.append(rail(520, 760, bot_y, "−V"))
    # вихід
    f.append(dot(620, mid_y))
    f.append(line(620, mid_y, 720, mid_y, color=INK, sw=1.8))
    f.append(text(732, mid_y + 4, "вихід", size=12, bold=True, anchor="start"))
    f.append(fitbox(498, 392, 304, 56,
                    "Обидва силові — дешеві NPN.\nДрайвер-PNP керує силовим NPN — знизу він «ніби» великий PNP.",
                    size=11, fill="#f0f7f1", stroke=FIELD, color=INK))

    render(os.path.join(IMG, "quasi-complementary.svg"), W, H, *f)
    print("OK quasi-complementary.svg")


if __name__ == "__main__":
    fig_topologies()
    fig_vbe()
    fig_bleed()
    fig_quasi()
    print("ALL DONE")

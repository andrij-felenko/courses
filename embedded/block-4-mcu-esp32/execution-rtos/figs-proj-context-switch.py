# -*- coding: utf-8 -*-
"""
Фігури для вставки ⚙️ 4.10.4a «Перемикання контексту зсередини».
Вивід → ./img/
Стиль: той самий локальний стиль розділу 27 (header/footer/палітра).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── Палітра розділу 27 ──────────────────────────────────────────────────────
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
AMBER = "#b87c00"
RED_  = "#c0271e"
INK_  = "#1b1b1b"
GREY_ = "#8a8a8a"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
LAMB  = "#fff6e0"
LRED  = "#fbecec"
FAINT = "#e4e4e4"
FONT_ = "Segoe UI, Arial, Helvetica, sans-serif"

def _esc(s):
    return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def hdr(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" font-family="{FONT_}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="10" markerHeight="10" refX="7" refY="3" '
        f'orient="auto" markerUnits="strokeWidth">'
        f'<path d="M0,0 L8,3 L0,6 Z" fill="{INK_}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="10" markerHeight="10" refX="7" refY="3" '
        f'orient="auto" markerUnits="strokeWidth">'
        f'<path d="M0,0 L8,3 L0,6 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="10" markerHeight="10" refX="7" refY="3" '
        f'orient="auto" markerUnits="strokeWidth">'
        f'<path d="M0,0 L8,3 L0,6 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aAmber" markerWidth="10" markerHeight="10" refX="7" refY="3" '
        f'orient="auto" markerUnits="strokeWidth">'
        f'<path d="M0,0 L8,3 L0,6 Z" fill="{AMBER}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="10" markerHeight="10" refX="7" refY="3" '
        f'orient="auto" markerUnits="strokeWidth">'
        f'<path d="M0,0 L8,3 L0,6 Z" fill="{RED_}"/></marker>\n'
        f'</defs>\n'
    )

def ftr():
    return "</svg>\n"

def tx(x, y, s, size=13, color=INK_, anchor="middle", bold=False, italic=False):
    w = ' font-weight="bold"' if bold else ''
    it = ' font-style="italic"' if italic else ''
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{color}" '
            f'text-anchor="{anchor}"{w}{it}>{_esc(s)}</text>\n')

def bx(x, y, w, h, fill="none", stroke=INK_, sw=1.5, rx=5):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')

def ln(x1, y1, x2, y2, color=INK_, sw=1.5, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{sw}"{d} stroke-linecap="round"/>\n')

def arr(x1, y1, x2, y2, color=INK_, sw=1.8, marker=None):
    m = marker or {"#1f47b5": "aBlue", "#1f8a3b": "aGreen",
                   "#b87c00": "aAmber", "#c0271e": "aRed"}.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{sw}" marker-end="url(#{m})"/>\n')

def save(name, body):
    body += ftr()
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ═══════════════════════════════════════════════════════════════════════════════
# Рис. 4.10.4a.1 — Три кроки перемикання контексту
# ═══════════════════════════════════════════════════════════════════════════════
def fig_4a1_switch_steps():
    W, H = 1000, 620
    s = hdr(W, H)

    # Заголовок
    s += tx(W/2, 28, "Три кроки перемикання контексту: зупинити → сховати → підмінити",
            17, INK_, "middle", bold=True)
    s += tx(W/2, 47, "SP — єдина «ручка» до збереженого стану; кожна задача відновлюється точно там, де її спинили",
            10.5, GREY_, "middle", italic=True)

    # ── Колонки: стек задачі A (синій), планувальник (янтарний), стек задачі B (зелений) ──
    col_a  = 140    # центр стека A
    col_sc = 500    # центр планувальника (scheduler)
    col_b  = 860    # центр стека B

    stk_w, stk_h_cell = 160, 24
    stk_x_a = col_a - stk_w//2
    stk_x_b = col_b - stk_w//2
    sc_w    = 200
    sc_x    = col_sc - sc_w//2

    # Заголовки колонок
    s += tx(col_a,  70, "ЗАДАЧА A", 13, BLUE, "middle", bold=True)
    s += tx(col_sc, 70, "ПЛАНУВАЛЬНИК", 13, AMBER, "middle", bold=True)
    s += tx(col_b,  70, "ЗАДАЧА B", 13, GREEN, "middle", bold=True)

    # ── ФАЗА 1: Задача A біжить ──────────────────────────────────────────────
    y0 = 90
    s += bx(stk_x_a, y0, stk_w, 32, LBLUE, BLUE, 2, 6)
    s += tx(col_a, y0+20, "A БІЖИТЬ (PC, регістри — в CPU)", 10.5, BLUE, "middle", bold=True)

    # стрілка: A → планувальник (тік або vTaskDelay)
    trigger_y = y0 + 16
    s += arr(stk_x_a + stk_w, trigger_y, sc_x - 4, trigger_y, AMBER, 1.8)
    s += tx(col_a + (col_sc - col_a)//2, trigger_y - 8,
            "тік-переривання або vTaskDelay", 9.5, AMBER, "middle", italic=True)

    # Блок планувальника — крок 1
    sc_y1 = y0
    s += bx(sc_x, sc_y1, sc_w, 32, LAMB, AMBER, 2, 6)
    s += tx(col_sc, sc_y1+13, "① Привід: час перемкнутись", 10, AMBER, "middle", bold=True)
    s += tx(col_sc, sc_y1+26, "(тік виявив — або A сама поступилась)", 8.5, AMBER, "middle")

    # ── ФАЗА 2: Зберегти контекст A ──────────────────────────────────────────
    y1 = y0 + 60
    # Стек A — клітинки регістрів
    regs_a = ["R14..R0", "PC", "прапорці (PSW)"]
    s += tx(stk_x_a - 8, y1 - 10, "стек задачі A ↓", 9.5, GREY_, "end", italic=True)
    for i, r in enumerate(regs_a):
        ry = y1 + i * stk_h_cell
        fill_ = LBLUE if i < len(regs_a)-1 else "#d8e6fb"
        s += bx(stk_x_a, ry, stk_w, stk_h_cell - 2, fill_, BLUE, 1.5, 3)
        s += tx(col_a, ry + 13, r, 10, BLUE, "middle")
    sp_a_y = y1 + len(regs_a) * stk_h_cell

    # SP_A мітка
    s += ln(stk_x_a - 32, sp_a_y, stk_x_a, sp_a_y, BLUE, 2, "4,3")
    s += tx(stk_x_a - 35, sp_a_y + 4, "SP_A", 10, BLUE, "end", bold=True)

    # стрілка від планувальника — push регістрів
    push_y = y1 + 12
    s += arr(sc_x, push_y, stk_x_a + stk_w + 4, push_y, BLUE, 1.8)
    s += tx(col_a + (col_sc - col_a)//2, push_y - 8,
            "② push: R0..Rn, PC, прапорці", 9.5, BLUE, "middle", italic=True)

    # Блок планувальника — крок 2
    sc_y2 = y1
    s += bx(sc_x, sc_y2, sc_w, 64, LAMB, AMBER, 2, 6)
    s += tx(col_sc, sc_y2+14, "② Зберегти контекст A:", 10, AMBER, "middle", bold=True)
    s += tx(col_sc, sc_y2+29, "push R0..Rn, PC, PSW → стек A", 9.5, AMBER, "middle")
    s += tx(col_sc, sc_y2+44, "TCB_A.sp ← SP_A", 9.5, AMBER, "middle", italic=True)
    s += tx(col_sc, sc_y2+58, "(SP — ручка до всього контексту)", 8.5, GREY_, "middle", italic=True)

    # ── ФАЗА 3: Відновити B ───────────────────────────────────────────────────
    y2 = y1 + len(regs_a) * stk_h_cell + 28
    regs_b = ["прапорці (PSW)", "PC", "R14..R0"]
    s += tx(stk_x_b + stk_w + 8, y2 - 10, "стек задачі B ↓", 9.5, GREY_, "start", italic=True)
    for i, r in enumerate(regs_b):
        ry = y2 + i * stk_h_cell
        fill_ = LGRN if i > 0 else "#c8ecda"
        s += bx(stk_x_b, ry, stk_w, stk_h_cell - 2, fill_, GREEN, 1.5, 3)
        s += tx(col_b, ry + 13, r, 10, GREEN, "middle")
    sp_b_y = y2 + len(regs_b) * stk_h_cell

    # SP_B мітка
    s += ln(stk_x_b + stk_w, sp_b_y, stk_x_b + stk_w + 32, sp_b_y, GREEN, 2, "4,3")
    s += tx(stk_x_b + stk_w + 35, sp_b_y + 4, "SP_B", 10, GREEN, "start", bold=True)

    # Блок планувальника — крок 3
    sc_y3 = y2
    s += bx(sc_x, sc_y3, sc_w, 64, LAMB, AMBER, 2, 6)
    s += tx(col_sc, sc_y3+14, "③ Відновити контекст B:", 10, AMBER, "middle", bold=True)
    s += tx(col_sc, sc_y3+29, "SP ← TCB_B.sp", 9.5, AMBER, "middle", italic=True)
    s += tx(col_sc, sc_y3+44, "pop PC, Rn..R0 зі стека B", 9.5, AMBER, "middle")
    s += tx(col_sc, sc_y3+58, "«повернутись з переривання» → B", 8.5, GREY_, "middle", italic=True)

    # стрілка від планувальника → стек B (pop)
    pop_y = y2 + 30
    s += arr(sc_x + sc_w + 4, pop_y, stk_x_b - 4, pop_y, GREEN, 1.8)
    s += tx(col_b - (col_b - col_sc)//2, pop_y - 8,
            "③ pop: PC, Rn..R0 зі стека B", 9.5, GREEN, "middle", italic=True)

    # ── ФАЗА 4: B біжить ────────────────────────────────────────────────────
    y3 = sp_b_y + 20
    s += bx(stk_x_b, y3, stk_w, 32, LGRN, GREEN, 2, 6)
    s += tx(col_b, y3+20, "B БІЖИТЬ (з місця, де спинили)", 10.5, GREEN, "middle", bold=True)

    # ── Вертикальна вісь часу ────────────────────────────────────────────────
    time_x = 26
    s += ln(time_x, y0, time_x, y3+32, INK_, 2)
    s += arr(time_x, y3+20, time_x, y3+36, INK_, 2)
    s += tx(time_x, y0 - 5, "час", 10, GREY_, "middle", italic=True)

    # ── Підсумкова рамка ─────────────────────────────────────────────────────
    note_y = y3 + 52
    nb_w, nb_h = 820, 40
    nb_x = (W - nb_w) // 2
    s += bx(nb_x, note_y, nb_w, nb_h, LAMB, AMBER, 1.5, 8)
    s += tx(W/2, note_y + 16, "SP — єдина «ручка» до контексту задачі: знаючи SP, планувальник повністю відновлює"
            " її стан зі стека.", 10.5, INK_, "middle")
    s += tx(W/2, note_y + 32, "Задача A «не знає», що щось сталося: її регістри жили на її стеку весь час.",
            10, GREY_, "middle", italic=True)

    save("fig-27-4a-1-switch-steps.svg", s)


# ═══════════════════════════════════════════════════════════════════════════════
# Рис. 4.10.4a.2 — Вміст стека задачі: локальні змінні, ланцюг викликів, кадр контексту
# ═══════════════════════════════════════════════════════════════════════════════
def fig_4a2_stack_frame():
    W, H = 900, 600
    s = hdr(W, H)

    s += tx(W/2, 28, "Що займає стек задачі: роботи + КАДР ПЕРЕМИКАННЯ + межа",
            17, INK_, "middle", bold=True)
    s += tx(W/2, 47,
            "надто малий стек валить систему під час перемикання — саме тоді, коли кадр кладеться на переповнений стек",
            10.5, GREY_, "middle", italic=True)

    # ── Ліва колонка: «проста задача» ────────────────────────────────────────
    cx_simple = 230
    stk_w = 190
    stk_x = cx_simple - stk_w // 2
    y_top = 68

    def draw_stack(cx, stk_x, y_top, frame_thick, label, color, lcolor):
        """Намалювати стовпчик-стек (зверху вниз — від SP до дна)."""
        segs = [
            ("локальні змінні\n(поточних функцій)", 68, FAINT, INK_),
            ("ланцюг викликів\n(return addresses)", 52, FAINT, INK_),
            ("ЗБЕРЕЖЕНИЙ КАДР\nконтексту R0..Rn, PC,\nпрапорці", frame_thick, "#fff3c4", AMBER),
        ]
        y = y_top
        for text_, h, fill_, tcol in segs:
            is_frame = text_.startswith("ЗБЕРЕЖЕНИЙ")
            brd = AMBER if is_frame else INK_
            brd_w = 2.5 if is_frame else 1.2
            s_out = bx(stk_x, y, stk_w, h, fill_, brd, brd_w, 4)
            lines = text_.split("\n")
            ty = y + h/2 - (len(lines)-1)*10 + 4
            for li, ln_ in enumerate(lines):
                s_out += tx(cx, ty + li*14, ln_, 9.5 if is_frame else 9, tcol, "middle",
                            bold=is_frame)
            y += h
        return s_out, y   # y — дно видимого стека (перед межею)

    # проста задача
    s_simple, y_bot_s = draw_stack(cx_simple, stk_x, y_top, 56, "проста", BLUE, INK_)
    s += s_simple

    # ── Права колонка: «задача з плаваючою комою» ────────────────────────────
    cx_fpu = 660
    stk_x_f = cx_fpu - stk_w // 2

    segs_fpu = [
        ("локальні змінні\n(поточних функцій)", 68, FAINT, INK_),
        ("ланцюг викликів\n(return addresses)", 52, FAINT, INK_),
        ("ЗБЕРЕЖЕНИЙ КАДР\nконтексту R0..Rn, PC,\nпрапорці", 56, "#fff3c4", AMBER),
        ("КАДР FPU\n(регістри співпроцесора\nплаваючої коми)", 52, "#ffe8b0", AMBER),
    ]
    y_fpu = y_top
    for text_, h, fill_, tcol in segs_fpu:
        is_frame = "КАДР" in text_
        brd = AMBER if is_frame else INK_
        brd_w = 2.5 if is_frame else 1.2
        s += bx(stk_x_f, y_fpu, stk_w, h, fill_, brd, brd_w, 4)
        lines = text_.split("\n")
        ty_c = y_fpu + h/2 - (len(lines)-1)*10 + 4
        for li, ln_ in enumerate(lines):
            s += tx(cx_fpu, ty_c + li*14, ln_, 9.5 if is_frame else 9, tcol, "middle",
                    bold=is_frame)
        y_fpu += h

    y_bot_f = y_fpu

    # ── Межа стека (червона лінія) ────────────────────────────────────────────
    border_y_s = y_bot_s + 14
    border_y_f = y_bot_f + 14

    # проста задача
    s += ln(stk_x - 8, border_y_s, stk_x + stk_w + 8, border_y_s, RED_, 3)
    s += tx(cx_simple, border_y_s + 14, "МЕЖА СТЕКА / OVERFLOW", 9.5, RED_, "middle", bold=True)

    # FPU задача
    s += ln(stk_x_f - 8, border_y_f, stk_x_f + stk_w + 8, border_y_f, RED_, 3)
    s += tx(cx_fpu, border_y_f + 14, "МЕЖА СТЕКА / OVERFLOW", 9.5, RED_, "middle", bold=True)

    # ── Водяний знак (high-water mark) ───────────────────────────────────────
    hwm_y_s = y_top + 68 + 8   # десь між локальними змінними й ланцюгом
    hwm_y_f = y_top + 68 + 8

    s += ln(stk_x - 24, hwm_y_s, stk_x + stk_w + 4, hwm_y_s, GREY_, 1.5, "5,4")
    s += tx(stk_x - 26, hwm_y_s + 4, "water\nmark", 8, GREY_, "end", italic=True)

    s += ln(stk_x_f - 24, hwm_y_f, stk_x_f + stk_w + 4, hwm_y_f, GREY_, 1.5, "5,4")
    s += tx(stk_x_f - 26, hwm_y_f + 4, "water\nmark", 8, GREY_, "end", italic=True)

    # ── Зазор між кадром і межею ─────────────────────────────────────────────
    # проста задача: зазор великий (безпечно)
    gap_s = border_y_s - y_bot_s
    s += bx(stk_x, y_bot_s, stk_w, gap_s, "#e6f7ec", GREEN, 1, 2)
    s += tx(cx_simple, y_bot_s + gap_s/2 + 4, f"вільно ({gap_s} px)", 8.5, GREEN, "middle")

    # FPU задача: зазор малий (небезпечно)
    gap_f = border_y_f - y_bot_f
    s += bx(stk_x_f, y_bot_f, stk_w, gap_f, LRED, RED_, 1, 2)
    s += tx(cx_fpu, y_bot_f + gap_f/2 + 4, f"майже немає ({gap_f} px)!", 8.5, RED_, "middle")

    # ── Заголовки стовпців ───────────────────────────────────────────────────
    s += tx(cx_simple, border_y_s + 34, "«Проста задача»", 12, BLUE, "middle", bold=True)
    s += tx(cx_simple, border_y_s + 50, "тонкий кадр — великий запас", 9.5, GREY_, "middle", italic=True)

    s += tx(cx_fpu, border_y_f + 34, "«Задача з плаваючою комою»", 12, AMBER, "middle", bold=True)
    s += tx(cx_fpu, border_y_f + 50, "товстий кадр — менше запасу", 9.5, GREY_, "middle", italic=True)

    # ── Пояснення кадру (стрілка + виноска) ─────────────────────────────────
    # у простої задачі: вказівник на сегмент «ЗБЕРЕЖЕНИЙ КАДР»
    frame_y_s = y_top + 68 + 52 + 56/2   # середина кадру простої задачі
    s += arr(stk_x + stk_w + 6, frame_y_s, stk_x + stk_w + 110, frame_y_s, AMBER, 1.8)
    note_x = stk_x + stk_w + 115
    s += tx(note_x, frame_y_s - 12, "↑ ось що додає", 9, AMBER, "start", italic=True)
    s += tx(note_x, frame_y_s + 2,  "ПЕРЕМИКАННЯ", 9.5, AMBER, "start", bold=True)
    s += tx(note_x, frame_y_s + 16, "(при кожному)", 9, AMBER, "start", italic=True)

    # ── Підсумкова рамка ─────────────────────────────────────────────────────
    note_y = max(border_y_s, border_y_f) + 68
    nb_w, nb_h = 760, 44
    nb_x = (W - nb_w) // 2
    s += bx(nb_x, note_y, nb_w, nb_h, LAMB, AMBER, 1.5, 8)
    s += tx(W/2, note_y + 16,
            "Стек мусить вміщати локальні змінні + ланцюг викликів + ПОВНИЙ кадр перемикання.",
            11, INK_, "middle", bold=True)
    s += tx(W/2, note_y + 32,
            "Надто малий стек валить систему саме під час перемикання. uxTaskGetStackHighWaterMark() покаже запас.",
            9.5, GREY_, "middle", italic=True)

    save("fig-27-4a-2-stack-frame.svg", s)


if __name__ == "__main__":
    fig_4a1_switch_steps()
    fig_4a2_stack_frame()
    print("done.")

# -*- coding: utf-8 -*-
"""
Фігури до 🧮-вставки §3.9.4m — «Математика CRC: многочлени над GF(2),
де XOR — і плюс, і мінус».
Окремий скрипт (головний figs.py розділу не чіпаємо). Чистий Python, без залежностей.
Вивід → ./img/ тієї ж папки розділу.

Стиль (AUTHORING §9): білий фон; червоний — акцент/«1»/несе вагу,
синій — нейтральні дані/біти, зелене — результат/висновок, бурштин — те, на що дивимось.
Шрифт sans-serif. Нумерація підписів — за темою-вставкою «Рис. 3.9.4m.k».
Імена SVG містять суфікс s4m, щоб не змішуватися ні з рисунками тем розділу,
ні з s3a (контрольні суми) чи s8i (Вояджери).
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── палітра (єдина з figs.py розділу) ───────────────────────────────────────
RED    = "#c0271e"   # акцент / «1» / результат, на який дивимось
BLUE   = "#1f47b5"   # нейтральні дані / біти
GREEN  = "#1f8a3b"   # висновок / лишок / «ок»
INK    = "#1b1b1b"
GREY   = "#8a8a8a"
FAINT  = "#e4e4e4"
AMBER  = "#caa24a"   # на що дивимось
PALE_R = "#fbeceb"
PALE_B = "#eef2fb"
PALE_G = "#eef7f0"
PALE_A = "#faf3e0"
MONO   = "Consolas, 'DejaVu Sans Mono', 'Courier New', monospace"
FONT   = "Segoe UI, Arial, Helvetica, sans-serif"
GLYPH_W = 11.4   # приблизна ширина моногліфа при 19px — для вирівнювання рисок під стовпчиком


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="mInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="mRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="mGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = {GREEN: "mGreen", RED: "mRed"}.get(color, "mInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal", mono=False):
    fam = MONO if mono else FONT
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def cell(x, y, w, h, s, fill="none", stroke=FAINT, sw=1.4, rx=4,
         tcol=INK, size=14, weight="bold", mono=True):
    out = rect(x, y, w, h, fill, stroke, sw, rx)
    out += text(x + w / 2, y + h * 0.64, s, size, tcol, "middle", weight, mono=mono)
    return out


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ════════════════════════════════════════════════════════════════════════════
# Рис. 3.9.4m.1 — Поле GF(2): таблиці двох дій на {0,1}.
# Додавання збігається з XOR; множення — з AND; і головне: рядок «+» та рядок «−»
# тотожні, бо 1+1=0 ⇒ кожен елемент сам собі протилежний.
# ════════════════════════════════════════════════════════════════════════════
def fig_gf2_tables():
    W, H = 940, 540
    s = header(W, H)
    s += text(W / 2, 32, "Поле GF(2): уся арифметика — на двох числах {0, 1}",
              19.5, INK, "middle", "bold")
    s += text(W / 2, 53,
              "додавання — це XOR, множення — це AND; віднімання окремо не існує — воно збігається з додаванням",
              12, GREY, "middle", style="italic")

    def op_table(x, ytop, title, sym, fn, tcol, fillcol):
        nonlocal s
        s += text(x + 96, ytop - 12, title, 14.5, tcol, "middle", "bold")
        c = 56          # розмір клітинки
        ox, oy = x + 40, ytop      # початок сітки значень
        # кутова клітинка з символом дії
        s += cell(ox - c, oy - c, c, c, sym, PALE_A, AMBER, 1.6, 6, INK, 18)
        # шапки рядків/стовпців
        for k, v in enumerate((0, 1)):
            s += cell(ox + k * c, oy - c, c, c, str(v), PALE_B, BLUE, 1.4, 6, BLUE, 16)   # стовпець
            s += cell(ox - c, oy + k * c, c, c, str(v), PALE_B, BLUE, 1.4, 6, BLUE, 16)   # рядок
        # тіло
        for r, a in enumerate((0, 1)):
            for col, b in enumerate((0, 1)):
                val = fn(a, b)
                fc = fillcol if val == 1 else "#ffffff"
                sc = tcol if val == 1 else FAINT
                tc = tcol if val == 1 else INK
                s += cell(ox + col * c, oy + r * c, c, c, str(val), fc, sc, 1.6, 6, tc, 17)

    # ── додавання (XOR) ────────────────────────────────────────────────────
    op_table(70, 110, "Додавання   a + b   (= XOR)", "+",
             lambda a, b: a ^ b, RED, PALE_R)
    # ── множення (AND) ─────────────────────────────────────────────────────
    op_table(370, 110, "Множення   a · b   (= AND)", "·",
             lambda a, b: a & b, GREEN, PALE_G)
    # ── віднімання — той самий рядок, що й додавання ───────────────────────
    op_table(670, 110, "Віднімання   a − b   (те саме!)", "−",
             lambda a, b: a ^ b, RED, PALE_R)

    # підпис-зв'язка під таблицями + та − : вони збігаються поклітинно
    s += text(166, 250, "↑ та сама таблиця, що й «−» праворуч", 11.5, AMBER, "middle", "bold")
    s += text(766, 250, "↑ поклітинно збігається з «+» ліворуч", 11.5, AMBER, "middle", "bold")

    # нижній блок-висновок: чому віднімання зайве
    by = 300
    s += rect(60, by, W - 120, 100, "#ffffff", INK, 1.6, 12)
    s += text(W / 2, by + 28, "Чому віднімання не потрібне окремо",
              15, INK, "middle", "bold")
    s += text(90, by + 56,
              "У звичайних числах a − b = a + (−b), і знак мінус указує «протилежне» число. У GF(2) протилежного шукати",
              12.5, INK, "start", mono=False)
    s += text(90, by + 76,
              "не доводиться: з таблиці «+» видно, що 1 + 1 = 0, тобто кожне число САМЕ СОБІ протилежне (−1 = 1, −0 = 0).",
              12.5, INK, "start", mono=False)

    # формульний акцент
    fy = 432
    s += rect(60, fy, W - 120, 64, PALE_R, RED, 1.6, 12)
    s += text(W / 2, fy + 26, "a + a = 0      ⇒      −a = a      ⇒      a − b  =  a + b  =  a ⊕ b",
              17, RED, "middle", "bold", mono=True)
    s += text(W / 2, fy + 50,
              "Один знак ⊕ виконує і плюс, і мінус — звідси вся простота арифметики CRC.",
              12, INK, "middle", "bold")
    save("fig-r09-s4m-1-gf2-tables.svg", s)


# ════════════════════════════════════════════════════════════════════════════
# Рис. 3.9.4m.2 — Бітовий рядок ↔ многочлен. Кожен біт — коефіцієнт степеня x.
# Показуємо байт 0b1101 0011 як многочлен і поліном-генератор CRC (приклад CRC-8).
# ════════════════════════════════════════════════════════════════════════════
def fig_bits_as_poly():
    W, H = 940, 470
    s = header(W, H)
    s += text(W / 2, 32, "Біти — це коефіцієнти многочлена над GF(2)",
              19.5, INK, "middle", "bold")
    s += text(W / 2, 53,
              "позиція біта = степінь x; одиниця означає «доданок є», нуль — «доданка немає»",
              12, GREY, "middle", style="italic")

    bits = [1, 1, 0, 1, 0, 0, 1, 1]      # 0xD3
    n = len(bits)
    cw = 78
    x0 = (W - n * cw) / 2
    yb = 110
    # сітка бітів зі степенями зверху
    for i, b in enumerate(bits):
        deg = n - 1 - i
        cx = x0 + i * cw
        s += text(cx + cw / 2, yb - 14, f"x{_sup(deg)}" if deg > 1 else ("x" if deg == 1 else "1"),
                  14, GREY, "middle", "bold")
        fc = PALE_R if b else "#ffffff"
        sc = RED if b else FAINT
        tc = RED if b else GREY
        s += cell(cx, yb, cw - 8, 50, str(b), fc, sc, 1.8, 7, tc, 22)
        # індекс степеня дрібним
        s += text(cx + (cw - 8) / 2, yb + 68, f"степінь {deg}", 10.5, GREY, "middle", mono=False)

    # підпис «байт = 0xD3»
    s += text(x0 - 14, yb + 32, "байт:", 13, BLUE, "end", "bold")
    s += text(W / 2, yb + 96, "= 0b1101 0011 = 0xD3", 13, BLUE, "middle", "bold", mono=True)

    # відповідний многочлен (лишаємо тільки одиничні доданки)
    py = 250
    s += rect(60, py, W - 120, 58, PALE_B, BLUE, 1.6, 12)
    s += text(W / 2, py + 24, "цьому байту відповідає многочлен", 12.5, INK, "middle", "bold")
    s += text(W / 2, py + 46,
              "M(x) = x⁷ + x⁶ + x⁴ + x + 1",
              18, BLUE, "middle", "bold", mono=True)

    # поліном-генератор
    gy = 332
    s += rect(60, gy, W - 120, 110, PALE_A, AMBER, 1.6, 12)
    s += text(W / 2, gy + 26, "Поліном-дільник (generator polynomial) CRC задають так само — рядком бітів",
              13, INK, "middle", "bold")
    s += text(W / 2, gy + 54,
              "приклад: CRC-8 з поліномом 0x07  →  G(x) = x⁸ + x² + x + 1",
              16, RED, "middle", "bold", mono=True)
    s += text(W / 2, gy + 82,
              "Степінь G(x) = 8 (старший біт x⁸ домовлено не пишуть у байті 0x07) ⇒ лишок займає 8 біт = CRC-8.",
              11.5, INK, "middle", mono=False)
    s += text(W / 2, gy + 100,
              "Саме степінь дільника задає ширину контрольної суми: степінь 16 → CRC-16, степінь 32 → CRC-32.",
              11.5, INK, "middle", mono=False)
    save("fig-r09-s4m-2-bits-as-poly.svg", s)


def _sup(n):
    """Юнікодні надрядкові цифри для невеликих степенів (для підписів сітки)."""
    table = {"0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
             "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹"}
    return "".join(table[d] for d in str(n))


# ════════════════════════════════════════════════════════════════════════════
# Рис. 3.9.4m.3 — Ділення многочленів над GF(2) «стовпчиком»: і є обчислення CRC.
# Беремо повідомлення, дописуємо нулі під лишок, ділимо на G(x); віднімання = XOR;
# залишок і є CRC. Показуємо кілька кроків XOR-вирівнювання.
# ════════════════════════════════════════════════════════════════════════════
def fig_long_division():
    W, H = 940, 620
    s = header(W, H)
    s += text(W / 2, 32, "Ділення многочленів над GF(2) «стовпчиком» — це і є обчислення CRC",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 53,
              "на кожному кроці віднімаємо (XOR) зсунутий дільник; жодних переносів і позик — кожен стовпчик сам по собі",
              12, GREY, "middle", style="italic")

    # Приклад: повідомлення 1010, дільник G = 1011 (x³+x+1, степінь 3 ⇒ CRC-3).
    # Дописуємо 3 нулі: ділене = 1010 000. Перевірено: лишок = 011, кадр 1010011
    # ділиться на G націло. У трасі є і кроки XOR, і два «пропуски» (старший біт 0).
    x0 = 250
    fs = 19
    lh = 30
    # підпис дільника ліворуч від «куточка»
    s += text(x0 - 18, 110 + 0 * lh, "G = 1011", fs - 3, AMBER, "end", "bold", mono=True)
    s += text(x0 - 18, 110 + 0 * lh + 18, "(x³+x+1)", 11, GREY, "end", mono=False)

    # Рядки ділення. Дільник показуємо у повній 7-розрядній «вирівняній» формі
    # (з провідними нулями), щоб стовпчики чесно збігалися без зсувів пробілами.
    steps = [
        ("1010000", INK,  "ділене: повідомлення 1010 + три нулі під майбутній лишок"),
        ("1011000", RED,  "⊕ G, підведений під старшу 1 (позиція x⁶)"),
        ("0001000", INK,  "= проміжок (старша 1 згасла)"),
        ("0001000", GREY, "старший біт = 0 ⇒ G не віднімаємо, зсуваємось далі"),
        ("0001000", GREY, "знову 0 ⇒ пропуск"),
        ("0001011", RED,  "⊕ G, підведений під наступну 1 (позиція x³)"),
        ("0000011", GREEN, "= лишок: коротший за G, ділити більше нічим"),
    ]
    yb = 96
    for i, (bitstr, col, note) in enumerate(steps):
        yy = yb + i * lh
        # рядок бітів моноширинно, вирівняний по лівому краю «під куточком»
        s += text(x0, yy, bitstr, fs, col, "start", "bold", mono=True)
        # риска під рядком-дільником (XOR) на всю ширину розрядної сітки
        if col == RED:
            s += line(x0 - 2, yy + 6, x0 + len(bitstr) * GLYPH_W, yy + 6, col, 1.4)
        ncol = {RED: RED, GREY: GREY, GREEN: GREEN}.get(col, INK)
        s += text(x0 + 190, yy, note, 11.5, ncol,
                  "start", "bold" if col in (RED, GREEN) else "normal", mono=False)

    # підсумок: три молодші біти лишка і є CRC
    ry = yb + len(steps) * lh + 10
    s += text(x0, ry, "CRC-3 = 011", fs, GREEN, "start", "bold", mono=True)
    s += text(x0 + 190, ry, "лишок коротший за дільник — це і є контрольна сума повідомлення 1010", 12, GREEN, "start", "bold", mono=False)

    # бічна панель: правило та зв'язок із передачею
    bx = 600
    s += rect(bx, 88, 312, 360, PALE_B, BLUE, 1.6, 12)
    s += text(bx + 156, 116, "Що тут відбувається", 14, INK, "middle", "bold")
    rows = [
        "1. До повідомлення дописуємо стільки",
        "   нулів, який степінь у дільника G",
        "   (тут 3) — це місце під майбутній CRC.",
        "",
        "2. Ділимо стовпчиком: де старший біт",
        "   проміжку = 1 — віднімаємо (XOR) G,",
        "   зсунутий під цю одиницю; де 0 —",
        "   просто йдемо до наступного біта.",
        "",
        "3. Що лишилось коротше за G — і є",
        "   лишок R(x). Це й є контрольна сума.",
    ]
    for i, t in enumerate(rows):
        s += text(bx + 18, 142 + i * 21, t, 11.5, INK, "start",
                  "bold" if t[:2] in ("1.", "2.", "3.") else "normal", mono=False)

    s += rect(bx + 18, 374, 276, 60, PALE_G, GREEN, 1.6, 10)
    s += text(bx + 156, 396, "Передаємо: 1010 011", 13.5, GREEN, "middle", "bold", mono=True)
    s += text(bx + 156, 416, "(повідомлення + лишок замість дописаних нулів)", 10, INK, "middle", mono=False)

    # нижня смуга — головна теза
    s += rect(60, 470, W - 120, 120, PALE_R, RED, 1.6, 12)
    s += text(W / 2, 496, "Ключ до всього: «віднімання» тут — це XOR біт-у-біт",
              15, RED, "middle", "bold")
    s += text(90, 524,
              "У звичайному стовпчику віднімання тягне позики між розрядами. Над GF(2) позик немає: кожен стовпчик —",
              12.5, INK, "start", mono=False)
    s += text(90, 544,
              "окреме 1−1=0, 1−0=1, 0−1=1 — тобто рівно XOR. Тому весь поділ зводиться до зсувів і XOR, і його легко",
              12.5, INK, "start", mono=False)
    s += text(90, 564,
              "робить як кілька вентилів у залізі, так і кілька рядків коду на МК (бітовий цикл — це буквально ці кроки).",
              12.5, INK, "start", mono=False)
    save("fig-r09-s4m-3-long-division.svg", s)


# ════════════════════════════════════════════════════════════════════════════
# Рис. 3.9.4m.4 — Чому CRC ловить помилки: помилка E(x) додається до кадру,
# і приймач бачить її, якщо G(x) не ділить E(x). Карта «який G ловить які помилки».
# ════════════════════════════════════════════════════════════════════════════
def fig_error_polynomial():
    W, H = 940, 514
    s = header(W, H)
    s += text(W / 2, 32, "Мова многочленів пояснює, ЯКІ помилки CRC гарантовано ловить",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 53,
              "перешкода додає до кадру свій многочлен помилки E(x); CRC пропустить її лише тоді, коли G(x) ділить E(x)",
              12, GREY, "middle", style="italic")

    # верх: T(x) переданий, R(x) прийнятий = T(x) + E(x)
    y = 96
    s += rect(70, y, 250, 56, PALE_G, GREEN, 1.6, 10)
    s += text(195, y + 22, "передано T(x)", 12.5, INK, "middle", "bold")
    s += text(195, y + 44, "ділиться на G(x) націло", 11, GREEN, "middle", "bold")

    s += text(360, y + 34, "+", 24, RED, "middle", "bold")

    s += rect(400, y, 250, 56, PALE_R, RED, 1.6, 10)
    s += text(525, y + 22, "помилка E(x)", 12.5, INK, "middle", "bold")
    s += text(525, y + 44, "одиниці там, де біти злетіли", 11, RED, "middle", "bold")

    s += text(690, y + 34, "=", 24, INK, "middle", "bold")

    s += rect(720, y, 190, 56, PALE_B, BLUE, 1.6, 10)
    s += text(815, y + 22, "прийнято R(x)", 12.5, INK, "middle", "bold")
    s += text(815, y + 44, "= T(x) + E(x)", 11, BLUE, "middle", "bold", mono=True)

    # центральна теза
    cy = 178
    s += rect(60, cy, W - 120, 70, "#ffffff", INK, 1.6, 12)
    s += text(W / 2, cy + 26, "Приймач ділить R(x) на G(x). Оскільки T(x) ділиться без лишку, лишок дає сама лише E(x):",
              12.5, INK, "middle", "bold")
    s += text(W / 2, cy + 52,
              "R(x) mod G(x) = E(x) mod G(x)   →   помилка непомітна  ⇔  G(x) ділить E(x)",
              15, RED, "middle", "bold", mono=True)

    # таблиця: які класи помилок гарантовано ловить добре підібраний G(x)
    tx, ty = 70, 282
    label_w = 360
    cw2 = 250
    rh = 40
    s += rect(tx, ty, label_w, 34, PALE_A, AMBER, 1.4, 6)
    s += text(tx + 12, ty + 23, "Клас помилки E(x)", 13, INK, "start", "bold", mono=False)
    s += rect(tx + label_w, ty, cw2, 34, PALE_A, AMBER, 1.4, 6)
    s += text(tx + label_w + cw2 / 2, ty + 23, "Чому G(x) її не ділить", 13, INK, "middle", "bold", mono=False)
    s += rect(tx + label_w + cw2, ty, W - 70 - (tx + label_w + cw2), 34, PALE_A, AMBER, 1.4, 6)
    s += text(tx + label_w + cw2 + (W - 70 - (tx + label_w + cw2)) / 2, ty + 23,
              "Гарантія", 13, INK, "middle", "bold", mono=False)

    rows = [
        ("Будь-який 1 перевернутий біт", "E(x) = xⁱ, а дільник має ≥ 2 доданки", "завжди"),
        ("Будь-які 2 перевернуті біти", "беруть примітивний G(x) із ≥ 3 доданками", "у межах кадру"),
        ("Непарне число помилок", "беруть G(x), кратний (x + 1)", "завжди"),
        ("Серія (burst) завдовжки ≤ степінь G", "коротша за G ⇒ не ділиться на G націло", "завжди"),
    ]
    for i, (cls, why, guar) in enumerate(rows):
        ry = ty + 34 + i * rh
        s += rect(tx, ry, label_w, rh, "#fafafa", FAINT, 1.2, 6)
        s += text(tx + 12, ry + rh * 0.62, cls, 12.5, INK, "start", "bold", mono=False)
        s += rect(tx + label_w, ry, cw2, rh, "#ffffff", FAINT, 1.2, 6)
        s += text(tx + label_w + cw2 / 2, ry + rh * 0.62, why, 11, INK, "middle", mono=False)
        ww = W - 70 - (tx + label_w + cw2)
        s += rect(tx + label_w + cw2, ry, ww, rh, PALE_G, GREEN, 1.4, 6)
        s += text(tx + label_w + cw2 + ww / 2, ry + rh * 0.62, guar, 12.5, GREEN, "middle", "bold")

    s += text(W / 2, ty + 34 + len(rows) * rh + 26,
              "Саме тому поліноми CRC (CRC-8/16/32) не випадкові: їх добирають так, щоб E(x) найчастіших помилок не ділилось на G(x).",
              11.5, GREY, "middle", style="italic", mono=False)
    save("fig-r09-s4m-4-error-polynomial.svg", s)


if __name__ == "__main__":
    fig_gf2_tables()
    fig_bits_as_poly()
    fig_long_division()
    fig_error_polynomial()
    print("r09-s4m (gf2-polynomials) figures done.")

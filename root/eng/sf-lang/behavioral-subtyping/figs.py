# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

WARN = "#c07000"   # бурштин — інваріант / застереження
WFILL = "#fff3cd"


# ── substitution: суть LSP — підставити підтип, поведінка не міняється ─────────
# Ідея: є код, написаний у термінах базового типу T. Якщо в БУДЬ-ЯКОМУ такому
# коді замінити об'єкт T на об'єкт підтипу S і поведінка не зміниться — S є
# підтипом T. Підтипізація тут про ПОВЕДІНКУ, не про збіг полів/сигнатур.

def fig_substitution():
    W, H = 760, 360
    p = []

    # код, написаний під базовий тип
    cx = W / 2
    code, cw, ch = textbox(cx, 84,
                           "код, написаний у термінах БАЗОВОГО типу T\n"
                           "(знає лише обіцянки T)",
                           size=12, bold=True, color=INK, fill=FILL, stroke=INK, sw=2, min_w=440)
    p.append(code)

    # дві коробки-обʼєкти, що входять у той самий отвір
    slot_y = 196
    sx_t, sx_s = 250, 510

    base_o, bw, bh = textbox(sx_t, slot_y, "обʼєкт T\n(базовий)", size=11,
                             fill="#eaf0fd", stroke=NEG, sw=1.8, min_w=150)
    sub_o, sw_, sh = textbox(sx_s, slot_y, "обʼєкт S\n(підтип)", size=11,
                             fill="#e8f5e9", stroke=FIELD, sw=1.8, min_w=150)
    p.append(base_o); p.append(sub_o)

    # обидва підходять у той самий «отвір» коду
    p.append(arrow(sx_t, slot_y - bh / 2, cx - 70, 84 + ch / 2, color=NEG, sw=1.6))
    p.append(arrow(sx_s, slot_y - sh / 2, cx + 70, 84 + ch / 2, color=FIELD, sw=1.6))
    p.append(text(sx_s, slot_y + sh / 2 + 22, "підставляємо S замість T", size=11,
                  color=FIELD, bold=True))

    # висновок
    verdict, vw, vh = textbox(cx, 296,
                              "поведінка коду не змінилась  →  S Є ПІДТИПОМ T",
                              size=12, bold=True, color=FIELD, fill="#e8f5e9", stroke=FIELD, sw=2, min_w=460)
    p.append(verdict)

    p.append(text(W / 2, H - 12,
                  "підтипізація — про збіг ПОВЕДІНКИ, а не лише полів і сигнатур",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "substitution.svg"), W, H, *p,
           title="Підстановка Лісков: підтип придатний усюди, де чекають базовий")


# ── square-rectangle: чому Квадрат не є підтипом Прямокутника ──────────────────
# Ідея: викликач під Прямокутник припускає, що setWidth міняє ЛИШЕ ширину.
# Квадрат має сильніший інваріант w==h, тож його setWidth ЗМУШЕНИЙ міняти й
# висоту — і припущення викликача про незалежні сторони тихо ламається.

def fig_square_rectangle():
    W, H = 780, 400
    p = []

    # очікування викликача (під Прямокутник)
    exp, ew, eh = textbox(200, 84,
                          "ВИКЛИКАЧ під Прямокутник:\n"
                          "setWidth(5) міняє лише ширину\n"
                          "→ площа = 5 × стара_висота",
                          size=11, bold=True, color=NEG, fill="#eaf0fd", stroke=NEG, sw=1.8, min_w=300)
    p.append(exp)

    # реальність із Квадратом
    real, rw, rh = textbox(580, 84,
                           "А підставили КВАДРАТ:\n"
                           "інваріант w == h\n"
                           "→ setWidth ЗМУШЕНИЙ змінити й висоту",
                           size=11, bold=True, color=POS, fill="#fdecea", stroke=POS, sw=1.8, min_w=300)
    p.append(real)

    # маленька наочність: прямокутник 2×3 → setWidth(5)
    # ліворуч (прямокутник): висота лишається 3
    bx, by = 130, 196
    p.append(rect(bx, by, 70, 60, fill="#eef2ff", stroke=NEG, sw=1.8))
    p.append(text(bx + 35, by + 34, "5 × 3", size=12, color=NEG, bold=True))
    p.append(text(bx + 35, by + 78, "висота ціла", size=10, color=NEG))

    # праворуч (квадрат): висота тихо поповзла до 5
    qx, qy = 560, 176
    p.append(rect(qx, qy, 90, 90, fill="#fdecea", stroke=POS, sw=1.8))
    p.append(text(qx + 45, qy + 50, "5 × 5", size=12, color=POS, bold=True))
    p.append(text(qx + 45, qy + 108, "висота тихо змінилась", size=10, color=POS))

    # стрілка-висновок «постумова послаблена»
    p.append(arrow(290, 230, 470, 230, color=POS, sw=1.8))
    brk, brw, brh = textbox(W / 2, 230,
                            "постумова «висота не змінилась»\nтихо ПОРУШЕНА",
                            size=11, bold=True, color=POS, fill=WFILL, stroke=WARN, sw=1.8, min_w=210)
    p.append(brk)

    verdict, vw, vh = textbox(W / 2, 320,
                              "Квадрат успадкував поля Прямокутника, але НЕ його поведінку → не підтип",
                              size=12, bold=True, color=INK, fill=FILL, stroke=INK, sw=2, min_w=560)
    p.append(verdict)

    p.append(text(W / 2, H - 12,
                  "сильніший інваріант нащадка ламає те, на що розраховував код під батька",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "square-rectangle.svg"), W, H, *p,
           title="Квадрат і Прямокутник: класичне порушення LSP")


# ── four-rules: чотири правила поведінкової підтипізації ───────────────────────
# Ідея: щоб підтип був ВЗАЄМОЗАМІННИМ, під успадкуванням діють чотири правила.
# Передумову лише послабити, постумову лише посилити, інваріанти зберегти,
# історичне правило — нащадок не міняє стан способом, забороненим для батька.

def fig_four_rules():
    W, H = 760, 430
    p = []

    head, hw, hh = textbox(W / 2, 70, "ПІДТИП ВЗАЄМОЗАМІННИЙ із базовим, якщо:",
                           size=13, bold=True, color=INK, fill=FILL, stroke=INK, sw=2, min_w=460)
    p.append(head)

    rows = [
        ("1. Передумову — лише ПОСЛАБИТИ", "приймати не менше входів, ніж батько", FIELD, "#e8f5e9"),
        ("2. Постумову — лише ПОСИЛИТИ", "гарантувати не менше, ніж батько", FIELD, "#e8f5e9"),
        ("3. Інваріанти батька — ЗБЕРЕГТИ", "жодного не скасувати (свої — можна додати)", WARN, WFILL),
        ("4. Історичне правило", "не міняти стан способом, забороненим батькові", NEG, "#eaf0fd"),
    ]
    y = 128
    for title, sub, col, fill in rows:
        b, bw, bh = textbox(W / 2, y, title + "\n" + sub, size=11, bold=False,
                            color=INK, fill=fill, stroke=col, sw=1.8, min_w=520)
        # перший рядок жирним кольором — імітуємо окремим написом
        p.append(b)
        y += 66

    p.append(text(W / 2, H - 14,
                  "порушив бодай одне — формально «успадкував», а насправді тихо рве чужий код",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "four-rules.svg"), W, H, *p,
           title="Чотири правила поведінкової підтипізації")


if __name__ == "__main__":
    fig_substitution()
    fig_square_rectangle()
    fig_four_rules()
    print("OK: figures written to", OUT)

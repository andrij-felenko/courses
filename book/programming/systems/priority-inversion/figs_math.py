# -*- coding: utf-8 -*-
# Фігури для вставки math-protocols.md (окремий файл, щоб не заважати figs.py).
# Пише у ту саму ./img/. Стиль і кольори — як у сусідньому figs.py.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

C_HIGH = "#c0392b"   # висока задача
C_LOW  = "#2457d6"   # нижча (S1)
C_ALT  = "#7d3cc0"   # ще нижча (S2)
C_MED  = "#e08a1e"
HOLD   = "#27ae60"   # тримає замок (зелена рамка)


def lane(x0, y, w, label, color):
    out = text(x0 - 14, y + 5, label, size=13, color=color, anchor="end", bold=True)
    out += line(x0, y, x0 + w, y, color="#c9ced6", sw=1)
    return out


def run(x, y, w, color, h=18, hold=False):
    out = rect(x, y - h/2, w, h, fill=color, stroke=color, sw=1, rx=3)
    if hold:
        out += ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" '
                'fill="none" stroke="%s" stroke-width="2.5"/>'
                % (x, y - h/2 - 3, w, h + 6, HOLD))
    return out


def tick(x, y_top, y_bot, lab):
    out = line(x, y_top, x, y_bot, color="#c9ced6", sw=1, dash="3 3")
    out += text(x, y_bot + 16, lab, size=11, color=MUTED)
    return out


def blocked(x, y, w):
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" '
            'fill="none" stroke="%s" stroke-width="1.4" stroke-dasharray="4 3"/>'
            % (x, y - 9, w, 18, C_HIGH))


# ── Фігура: ланцюжок блокувань під голим успадкуванням ──────────────────────
def fig_chain():
    """Голе успадкування: висока задача блокується раз на КОЖНУ нижчу/семафор.
    Сумарний блокувальний член = B₁+B₂+… — до min(n,m) критичних секцій."""
    W, H = 800, 360
    x0 = 168
    w  = W - x0 - 34
    yH, yA, yB = 74, 150, 214
    frags = []
    frags.append(lane(x0, yH, w, "J (висока)", C_HIGH))
    frags.append(lane(x0, yA, w, "Ja · S1", C_LOW))
    frags.append(lane(x0, yB, w, "Jb · S2", C_ALT))

    def X(t): return x0 + t * (w / 10.0)
    for t, lab in [(0,"0"),(1,"1"),(3,"3"),(5,"5"),(9,"9")]:
        frags.append(tick(X(t), 58, 232, lab))

    # Ja тримає S1 (t0..1)
    frags.append(run(X(0), yA, X(1)-X(0), C_LOW, hold=True))
    # J прокидається на t1, хоче S1 -> чекає Ja до t3
    frags.append(blocked(X(1), yH, X(3)-X(1)))
    frags.append(text((X(1)+X(3))/2, yH-19, "чекає S1", size=11, color=C_HIGH))
    # Ja добігає з успадкованим високим (t1..3)
    frags.append(run(X(1), yA, X(3)-X(1), C_LOW, hold=True))
    frags.append(text((X(1)+X(3))/2, yA+33, "критична секція Ja  =  β₁", size=11, color=C_LOW))
    # t3: Ja віддала S1; тепер J хоче S2, який тримає Jb -> чекає знову t3..5
    frags.append(blocked(X(3), yH, X(5)-X(3)))
    frags.append(text((X(3)+X(5))/2, yH-19, "чекає S2", size=11, color=C_ALT))
    frags.append(run(X(3), yB, X(5)-X(3), C_ALT, hold=True))
    frags.append(text((X(3)+X(5))/2, yB+33, "критична секція Jb  =  β₂", size=11, color=C_ALT))
    # t5..9: нарешті J біжить
    frags.append(run(X(5), yH, X(9)-X(5), C_HIGH))
    frags.append(text((X(5)+X(9))/2, yH-19, "J нарешті працює", size=11, color=C_HIGH))

    # Дужка сумарного блокування під віссю
    by = 262
    frags.append(line(X(1), by, X(5), by, color=INK, sw=1.6))
    frags.append(line(X(1), by-5, X(1), by+5, color=INK, sw=1.6))
    frags.append(line(X(5), by-5, X(5), by+5, color=INK, sw=1.6))
    frags.append(text((X(1)+X(5))/2, by+18, "сумарне блокування J  =  β₁ + β₂",
                      size=12, color=INK, bold=True))

    box, _, _ = textbox(W/2, 326,
                        "Голе успадкування: блокування СУМУЄТЬСЯ — аж до min(n, m) критичних секцій",
                        size=12, bold=True, fill="#fdecea", stroke=C_HIGH, color=C_HIGH)
    frags.append(box)
    render(os.path.join(OUT, "chain.svg"), W, H, *frags,
           title="Ланцюжок блокувань під базовим успадкуванням")


# ── Фігура: блокувальний член у перевірці планованості ──────────────────────
def fig_schedbound():
    """Стос завантаження: як Bᵢ «надуває» Cᵢ до (Cᵢ+Bᵢ) і штовхає стіс
    до межі Ляна–Лейленда. Перевірка для τ₂: C1/T1 + C2/T2 + B2/T2 ≤ межа."""
    W, H = 720, 430
    ax, ay = 108, 58
    ah = 288
    base = ay + ah
    aw = 300
    frags = []

    # Вісь завантаження 0..1
    frags.append(line(ax, ay, ax, base, color=INK, sw=1.6))
    frags.append(line(ax, base, ax + aw + 40, base, color=INK, sw=1.6))
    for u, lab in [(0.0,"0"),(0.25,"0.25"),(0.5,"0.5"),(0.75,"0.75"),(1.0,"1.0")]:
        yy = base - u * ah
        frags.append(line(ax-6, yy, ax, yy, color=INK, sw=1.4))
        frags.append(text(ax-11, yy+4, lab, size=11, color=MUTED, anchor="end"))
    frags.append('<g transform="translate(%.1f,%.1f) rotate(-90)">%s</g>'
                 % (ax-56, ay+ah/2, text(0, 0, "завантаження", size=12, color=INK)))

    # Значення прикладу (з worked-прикладу у тексті), для τ2:
    #   C1/T1 ≈ 0.267, C2/T2 ≈ 0.267, B2/T2 = 0.20 → сума ≈ 0.734
    #   межа для i=2: 2(2^0.5 − 1) ≈ 0.828
    U1, U2, B2 = 0.267, 0.267, 0.20
    bound2 = 0.828
    bw = 118
    bx = ax + 78

    def seg(y_lo, val, color, lab, labcolor=None):
        yy = base - (y_lo + val) * ah
        hh = val * ah
        out = rect(bx, yy, bw, hh, fill=color, stroke="#ffffff", sw=1.2, rx=0)
        out += text(bx + bw + 14, yy + hh/2 + 4, lab, size=11,
                    color=labcolor or INK, anchor="start")
        return out

    # Стос: C1/T1, тоді C2/T2, згори блок B2/T2 (заштрихований червоним)
    frags.append(seg(0.0, U1, C_MED, "C₁/T₁ = 0.27", "#a5640f"))
    frags.append(seg(U1, U2, C_LOW, "C₂/T₂ = 0.27", "#1b3fa0"))
    yb = base - (U1 + U2 + B2) * ah
    hb = B2 * ah
    frags.append(rect(bx, yb, bw, hb, fill="#fdecea", stroke=C_HIGH, sw=1.8, rx=0))
    frags.append(text(bx + bw + 14, yb + hb/2 + 4, "B₂/T₂ = 0.20", size=11, color=C_HIGH, anchor="start"))
    frags.append(text(bx + bw/2, yb - 9, "блокувальний член", size=11, color=C_HIGH, anchor="middle"))

    # Лінія межі планованості
    ybound = base - bound2 * ah
    frags.append(line(ax, ybound, ax + aw + 40, ybound, color="#1e8449", sw=2, dash="6 4"))
    frags.append(text(ax + aw + 38, ybound - 8, "межа  2(√2 − 1) ≈ 0.83",
                      size=11, color="#1e8449", anchor="end"))

    # Підпис стовпця й сума
    frags.append(text(bx + bw/2, base + 22, "перевірка для τ₂", size=12, color=INK, bold=True))
    frags.append(text(bx + bw/2, yb - 30, "сума ≈ 0.73", size=12, color=INK, bold=True))

    box, _, _ = textbox(ax + aw/2 + 40, base + 66,
                        "0.73 ≤ 0.83  →  τ₂ укладається у строк навіть із блокуванням",
                        size=12, bold=True, fill="#eafaf0", stroke="#1e8449", color="#1e8449")
    frags.append(box)
    render(os.path.join(OUT, "schedbound.svg"), W, H, *frags,
           title="Блокувальний член у перевірці планованості")


if __name__ == "__main__":
    fig_chain()
    fig_schedbound()
    print("OK: chain.svg, schedbound.svg")

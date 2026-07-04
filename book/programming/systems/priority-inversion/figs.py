# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

# Кольори смуг виконання
C_HIGH = "#c0392b"   # високий пріоритет
C_MED  = "#e08a1e"   # середній
C_LOW  = "#2457d6"   # низький
HOLD   = "#27ae60"   # тримає м'ютекс (зелена рамка навколо смуги)


def lane(x0, y, w, label, color):
    """Порожня доріжка задачі: підпис ліворуч + базова лінія часу."""
    out = text(x0 - 14, y + 5, label, size=13, color=color, anchor="end", bold=True)
    out += line(x0, y, x0 + w, y, color="#c9ced6", sw=1)
    return out


def run(x, y, w, color, h=18, hold=False):
    """Смуга «задача виконується» на доріжці (центр по y)."""
    out = rect(x, y - h/2, w, h, fill=color, stroke=color, sw=1, rx=3)
    if hold:  # зелена облямівка = у цей час тримає м'ютекс
        out += ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" '
                'fill="none" stroke="%s" stroke-width="2.5"/>'
                % (x, y - h/2 - 3, w, h + 6, HOLD))
    return out


def tick(x, y_top, y_bot, lab):
    out = line(x, y_top, x, y_bot, color="#c9ced6", sw=1, dash="3 3")
    out += text(x, y_bot + 16, lab, size=11, color=MUTED)
    return out


def blocked(x, y, w):
    """Заштрихована зона: висока задача заблокована/чекає."""
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" '
            'fill="none" stroke="%s" stroke-width="1.4" stroke-dasharray="4 3"/>'
            % (x, y - 9, w, 18, C_HIGH))


# ── Фігура 1: неконтрольована інверсія ──────────────────────────────────────
def fig_inversion():
    W, H = 760, 340
    x0 = 150            # ліва межа доріжок
    w  = W - x0 - 30
    yH, yM, yL = 70, 130, 190
    frags = []
    frags.append(lane(x0, yH, w, "Висока", C_HIGH))
    frags.append(lane(x0, yM, w, "Середня", C_MED))
    frags.append(lane(x0, yL, w, "Низька", C_LOW))

    # Часова шкала (умовні одиниці)
    def X(t): return x0 + t * (w / 10.0)
    for t, lab in [(0,"0"),(1,"1"),(2,"2"),(6,"…"),(9,"9")]:
        frags.append(tick(X(t), 55, 210, lab))

    # t0..1: низька захопила м'ютекс і працює
    frags.append(run(X(0), yL, X(1)-X(0), C_LOW, hold=True))
    # t1: висока прокидається, хоче м'ютекс -> блокована увесь час
    frags.append(blocked(X(1), yH, X(9)-X(1)))
    frags.append(text((X(1)+X(9))/2, yH-18, "хоче м'ютекс — заблокована", size=11, color=C_HIGH))
    # t1..9: середня витісняє низьку і крутиться довго (низька не може добігти й віддати м'ютекс)
    frags.append(run(X(1), yM, X(9)-X(1), C_MED))
    frags.append(text((X(1)+X(9))/2, yM-16, "довга робота, м'ютекса не торкається", size=11, color=C_MED))
    # низька застигла з м'ютексом (тонка зелена рамка на порожній ділянці)
    frags.append(('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" '
                  'fill="none" stroke="%s" stroke-width="2" stroke-dasharray="2 3"/>'
                  % (X(1), yL-11, X(9)-X(1), 22, HOLD)))
    frags.append(text((X(1)+X(9))/2, yL+30, "тримає м'ютекс, але не виконується", size=11, color=HOLD))

    # Легенда й вивід
    lx, ly = x0, 250
    frags.append(('<rect x="%.1f" y="%.1f" width="18" height="12" rx="2" fill="none" '
                  'stroke="%s" stroke-width="2.5"/>' % (lx, ly, HOLD)))
    frags.append(text(lx+26, ly+11, "зелена рамка = тримає м'ютекс", size=11, color=INK, anchor="start"))
    box, _, _ = textbox(W/2, 300, "Середня блокує високу як завгодно довго — інверсія НЕ обмежена",
                        size=12, bold=True, fill="#fdecea", stroke=C_HIGH, color=C_HIGH)
    frags.append(box)

    render(os.path.join(OUT, "inversion.svg"), W, H, *frags,
           title="Неконтрольована інверсія пріоритетів")


# ── Фігура 2: успадкування пріоритету рятує ─────────────────────────────────
def fig_inheritance():
    W, H = 760, 340
    x0 = 150
    w  = W - x0 - 30
    yH, yM, yL = 70, 130, 190
    frags = []
    frags.append(lane(x0, yH, w, "Висока", C_HIGH))
    frags.append(lane(x0, yM, w, "Середня", C_MED))
    frags.append(lane(x0, yL, w, "Низька", C_LOW))

    def X(t): return x0 + t * (w / 10.0)
    for t, lab in [(0,"0"),(1,"1"),(3,"3"),(4,"4"),(9,"9")]:
        frags.append(tick(X(t), 55, 210, lab))

    # t0..1: низька тримає м'ютекс, працює на своєму пріоритеті
    frags.append(run(X(0), yL, X(1)-X(0), C_LOW, hold=True))
    # t1: висока хоче м'ютекс -> блокована t1..3
    frags.append(blocked(X(1), yH, X(3)-X(1)))
    frags.append(text((X(1)+X(3))/2, yH-18, "чекає (коротко)", size=11, color=C_HIGH))
    # t1..3: низька УСПАДКУВАЛА високий пріоритет — біжить далі й на доріжці «Висока»
    frags.append(run(X(1), yH, X(3)-X(1), C_LOW, hold=True))
    frags.append(text((X(1)+X(3))/2, yH+34, "низька біжить із високим пріоритетом", size=11, color=C_LOW))
    # середня НЕ може витіснити — чекає
    frags.append(text((X(1)+X(3))/2, yM, "витіснена — чекає", size=11, color=C_MED, anchor="middle"))
    # t3: низька віддала м'ютекс -> пріоритет спав; висока хапає й біжить t3..4
    frags.append(run(X(3), yH, X(4)-X(3), C_HIGH, hold=True))
    frags.append(text((X(3)+X(4))/2, yH-18, "висока працює", size=11, color=C_HIGH))
    # t4..9: висока звільнила -> тепер середня
    frags.append(run(X(4), yM, X(9)-X(4), C_MED))
    frags.append(text((X(4)+X(9))/2, yM-16, "потім середня", size=11, color=C_MED))

    lx, ly = x0, 250
    frags.append(('<rect x="%.1f" y="%.1f" width="18" height="12" rx="2" fill="none" '
                  'stroke="%s" stroke-width="2.5"/>' % (lx, ly, HOLD)))
    frags.append(text(lx+26, ly+11, "зелена рамка = тримає м'ютекс", size=11, color=INK, anchor="start"))
    box, _, _ = textbox(W/2, 300, "Затримка високої = лише одна критична секція низької — інверсія ОБМЕЖЕНА",
                        size=12, bold=True, fill="#eafaf0", stroke=HOLD, color="#1e8449")
    frags.append(box)

    render(os.path.join(OUT, "inheritance.svg"), W, H, *frags,
           title="Успадкування пріоритету обмежує інверсію")


# ── Фігура 3: лінія часу поняття (для вставки hist-pathfinder) ───────────────
def cardbox(x, y, w, lines, col, size=11.5, pad=9, head=None):
    """Картка з фіксованою лівою-верхньою (x,y) і шириною w; висота — під рядки.
    Перший рядок (head) — жирний кольоровий заголовок. Повертає (svg, h)."""
    n = len(lines)
    lh = size * 1.32
    h = pad * 2 + n * lh
    out = rect(x, y, w, h, fill=FILL, stroke=col, sw=1.6, rx=6)
    ty = y + pad + size
    for i, ln in enumerate(lines):
        bold = (i == 0)
        color = col if i == 0 else INK
        out += text(x + w / 2, ty + i * lh, ln, size=size, color=color, bold=bold)
    return out, h


def fig_history():
    """Три віхи в один ряд під віссю часу: 1980 — вперше названо;
    1990 — строга теорія й теорема; 1997 — Марс: збій і лік."""
    W, H = 860, 430
    ax0, ax1 = 60, W - 40         # межі осі часу
    ay = 96                       # рівень осі
    frags = []

    # Вісь часу
    frags.append(line(ax0, ay, ax1, ay, color=INK, sw=2))
    frags.append(arrow(ax1 - 1, ay, ax1 + 14, ay, color=INK, sw=2))
    frags.append(text(ax1 + 6, ay - 10, "час", size=12, color=MUTED, anchor="start"))

    # Три віхи: центр колонки, колір, рядки картки
    cw = 236                      # ширина картки
    centers = [190, 430, 670]     # центри трьох колонок (широкі проміжки)
    cols   = [NEG, FIELD, POS]
    years  = ["1980", "1990", "1997"]
    texts  = [
        ["1980 — уперше названо",
         "Lampson і Redell (Xerox):",
         "монітори в мові Mesa —",
         "інверсію описано як",
         "справжню ваду планування"],
        ["1990 — строга теорія",
         "Sha · Rajkumar · Lehoczky,",
         "IEEE Trans. Computers:",
         "названо «неконтрольовану",
         "інверсію», лік і теореми"],
        ["4 липня 1997 — Марс",
         "Pathfinder сідає; за дні —",
         "рестарти від сторожа.",
         "Причина — інверсія у VxWorks;",
         "лік залито з Землі"],
    ]

    card_top = ay + 46           # верх карток (спільний для всіх трьох)
    for cx, col, yr, lines in zip(centers, cols, years, texts):
        # вузол на осі + рік
        frags.append(circle(cx, ay, 6, fill=col, stroke=col))
        frags.append(text(cx, ay - 14, yr, size=14, color=col, bold=True))
        # «ніжка» від осі до картки
        frags.append(line(cx, ay + 6, cx, card_top, color=col, sw=1.3, dash="3 3"))
        # картка
        box, bh = cardbox(cx - cw / 2, card_top, cw, lines, col)
        frags.append(box)

    # Підсумковий рядок унизу — на всю ширину, з великим запасом від карток
    sub, _, _ = textbox(W / 2, H - 30,
                        "Ваду знали 17 років до посадки, теорію ліку — 7: бракувало не ідеї, а ввімкненого прапорця",
                        size=12.5, bold=True, fill="#eef2ff", stroke=NEG, color=INK, pad=12)
    frags.append(sub)

    render(os.path.join(OUT, "history.svg"), W, H, *frags,
           title="Від замітки до Марса: як визрівала інверсія пріоритетів")


if __name__ == "__main__":
    fig_inversion()
    fig_inheritance()
    fig_history()
    print("OK: inversion.svg, inheritance.svg, history.svg")

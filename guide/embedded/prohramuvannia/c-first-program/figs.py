# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

CODEBG = "#0f1b14"   # темне тло код-плашки
CODEHU = "#9ec5ff"   # текст людини (блакитний на темному)
CODEMA = "#7fe0a0"   # машинний код (зелений на темному)


def mono(x, y, s, size=12, color=CODEHU, anchor="middle", bold=False):
    w = ' font-weight="700"' if bold else ''
    return ('<text x="%.1f" y="%.1f" font-family="Consolas, \'DejaVu Sans Mono\', monospace" '
            'font-size="%d" fill="%s" text-anchor="%s"%s>%s</text>'
            % (x, y, size, color, anchor, w, esc(s)))


def codeplate(cx, cy, w, h, accent, fill=CODEBG):
    return rect(cx - w / 2, cy - h / 2, w, h, fill=fill, stroke="#0a120d", sw=1.4, rx=8)


# ── 1. pipeline: текст → компілятор → машинний код → виконання ────────────────
def fig_pipeline():
    W, H = 780, 320
    p = []
    y = 150

    # ── ліворуч: вихідний код (текст для людини) ──
    sx = 138
    sw, sh = 210, 96
    p.append(codeplate(sx, y, sw, sh, CODEHU))
    p.append(mono(sx, y - 26, "int main(void) {", 12, CODEHU, bold=True))
    p.append(mono(sx, y - 6, '  printf("Привіт");', 11, CODEHU))
    p.append(mono(sx, y + 14, "  return 0;", 11, CODEHU))
    p.append(mono(sx, y + 32, "}", 12, CODEHU, bold=True))
    p.append(text(sx, y - sh / 2 - 26, "вихідний код  hello.c", size=12, color=INK, bold=True))
    p.append(text(sx, y - sh / 2 - 10, "текст для людини", size=10, color=MUTED, italic=True))

    # ── по центру: компілятор ──
    cx = W / 2 + 6
    cbw, cbh = 150, 66
    b, bw, bh = textbox(cx, y, "КОМПІЛЯТОР\n(gcc)", size=14, bold=True, color=NEG,
                        fill="#eef3ff", stroke=NEG, sw=2, pad=14, min_w=cbw)
    p.append(b)
    p.append(text(cx, y + bh / 2 + 16, "перекладає текст → числа", size=10, color=MUTED, italic=True))
    p.append(arrow(sx + sw / 2 + 6, y, cx - bw / 2 - 6, y, color=INK, sw=2.2))

    # ── праворуч: машинний код + виконання ──
    mx = W - 150
    mw, mh = 210, 96
    p.append(codeplate(mx, y, mw, mh, CODEMA))
    for i, ln in enumerate(["01001000 10111111", "11101000 ...", "LEA  rdi, [рядок]", "CALL puts"]):
        col = CODEMA if i < 2 else MUTED
        p.append(mono(mx, y - 28 + i * 20, ln, 11 if i < 2 else 10, col))
    p.append(text(mx, y - mh / 2 - 26, "машинний код  hello", size=12, color=INK, bold=True))
    p.append(text(mx, y - mh / 2 - 10, "числа для процесора", size=10, color=MUTED, italic=True))
    p.append(arrow(cx + bw / 2 + 6, y, mx - mw / 2 - 6, y, color=INK, sw=2.2))

    # ── знизу: результат виконання ──
    p.append(text(mx, y + mh / 2 + 24, "процесор виконує →", size=11, color=FIELD, bold=True))
    p.append(fitbox(mx - 105, y + mh / 2 + 34, 210, 30, "Привіт, світе!", size=13,
                    fill="#eafaf0", stroke=FIELD, sw=1.6))

    render(os.path.join(OUT, "pipeline.svg"), W, H, *p,
           title="Від тексту людини до чисел машини — і до результату")


# ── 2. loop: коло «змінив → зібрав → подивився» ──────────────────────────────
def fig_loop():
    W, H = 780, 340
    p = []

    # три вузли ланцюга: пишеш код → компілятор → (гілка)
    yc = 150
    x_code = 150
    x_comp = 400

    # 1) пишеш код
    b1, w1, h1 = textbox(x_code, yc, "ПИШЕШ КОД\nhello.c", size=13, bold=True, color=INK,
                         fill="#f4f6f8", stroke=INK, sw=1.8, pad=14, min_w=150)
    p.append(b1)

    # 2) компілятор
    b2, w2, h2 = textbox(x_comp, yc, "КОМПІЛЯТОР", size=13, bold=True, color=NEG,
                         fill="#eef3ff", stroke=NEG, sw=2, pad=14, min_w=150)
    p.append(b2)
    p.append(arrow(x_code + w1 / 2 + 6, yc, x_comp - w2 / 2 - 6, yc, color=INK, sw=2.2))
    p.append(text((x_code + x_comp) / 2, yc - 14, "зібрати", size=10, color=MUTED, italic=True))

    # 3a) помилка → назад до коду (верхня дуга)
    y_err = 66
    be, we, he = textbox(x_comp, y_err, "ПОМИЛКА\nerror: expected ';'", size=11, bold=True, color=POS,
                         fill="#fdecea", stroke=POS, sw=1.8, pad=10, min_w=200)
    p.append(be)
    p.append(arrow(x_comp, yc - h2 / 2 - 4, x_comp, y_err + he / 2 + 4, color=POS, sw=2))
    # дуга повернення до коду
    p.append(('<path d="M %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" fill="none" '
              'stroke="%s" stroke-width="2" marker-end="url(#arrow)"/>'
              % (x_comp - we / 2, y_err, x_code, y_err - 30, x_code, yc - h1 / 2 - 40,
                 x_code, yc - h1 / 2 - 6, POS)))
    p.append(text((x_code + x_comp) / 2 - 20, y_err - 30, "показує, ДЕ спіткнувся — правиш і знову",
                  size=10.5, color=POS, italic=True))

    # 3b) чисто → робоча програма → запуск (праворуч)
    x_run = 650
    y_ok = yc
    bok, wok, hok = textbox(x_run, y_ok, "РОБОЧА\nПРОГРАМА", size=13, bold=True, color=FIELD,
                            fill="#eafaf0", stroke=FIELD, sw=2, pad=14, min_w=150)
    p.append(bok)
    p.append(arrow(x_comp + w2 / 2 + 6, yc, x_run - wok / 2 - 6, yc, color=FIELD, sw=2.2))
    p.append(text((x_comp + x_run) / 2, yc - 14, "чисто", size=10, color=FIELD, italic=True, bold=True))

    # запуск під робочою програмою
    p.append(arrow(x_run, y_ok + hok / 2 + 4, x_run, y_ok + hok / 2 + 30, color=INK, sw=2))
    p.append(fitbox(x_run - 100, y_ok + hok / 2 + 34, 200, 30, "./hello  →  Привіт, світе!",
                    size=11, fill="#0f1b14", stroke="#0a120d", sw=1.4, color=CODEMA))

    p.append(mtext(W / 2, H - 26,
                   "коло «змінив → зібрав → подивився» крутиться секундами;\nпомилка компіляції — не провал, а вказівник на рядок",
                   size=11, color=INK))

    render(os.path.join(OUT, "loop.svg"), W, H, *p,
           title="Головний ритм: змінив → зібрав → подивився")


# ── 3. hist: дві переплетені історії на одній осі часу ───────────────────────
#     (для вставки hist-c-and-hello.md — «створив» проти «популяризував»)
CREATE = "#2457d6"   # хто СТВОРИВ / задумав — синій
SPREAD = "#c0392b"   # хто ПОПУЛЯРИЗУВАВ / розкрутив — червоний


def _milestone(x, y, up, year, who, role, color):
    """Позначка на осі: рисочка від осі, кружок, підпис року й ролі.
    up=True — гілка вгору (нитка C), up=False — вниз (нитка bug)."""
    p = []
    tip = y - 64 if up else y + 64
    p.append(line(x, y, x, tip, color=color, sw=1.6))
    p.append(circle(x, y, 5.5, fill=color, stroke=color, sw=1))
    ty = tip - 6 if up else tip + 14
    p.append(text(x, ty, year, size=12, color=INK, bold=True))
    ry = ty - 15 if up else ty + 15
    b, bw, bh = textbox(x, ry, who, size=10.5, pad=6, fill="#ffffff",
                        stroke=color, sw=1.4, color=color, bold=True)
    p.append(b)
    ry2 = ry - bh / 2 - 8 if up else ry + bh / 2 + 8
    p.append(text(x, ry2, role, size=9.5, color=MUTED, italic=True))
    return "".join(p)


def fig_two_stories():
    W, H = 820, 400
    p = []
    axy = H / 2
    x0, x1 = 70, W - 40
    # вісь часу
    p.append(line(x0, axy, x1, axy, color=INK, sw=2.4))
    p.append(text(x1, axy - 10, "час →", size=12, color=INK, bold=True, anchor="end"))

    # позиції за роками (нелінійно — щоб 1947→1972 не давило; рівномірні слоти)
    def slot(i, n=6):
        return x0 + 24 + (x1 - x0 - 48) * i / (n - 1)

    # ── нитка «bug» (вниз) ──
    p.append(text(x0 - 4, axy + 150, "«BUG»", size=12, color=INK, bold=True, anchor="start"))
    p.append(_milestone(slot(0), axy, False, "1878", "Едісон", "уживає як звичне", CREATE))
    p.append(_milestone(slot(1), axy, False, "1947", "міль у Mark II", "жарт — не народження", MUTED))
    p.append(_milestone(slot(2), axy, False, "по тому", "Ґрейс Гоппер", "розкручує bug/debug", SPREAD))

    # ── нитка «C / hello, world» (вгору) ──
    p.append(text(x0 - 4, axy - 150, "C · «HELLO, WORLD»", size=12, color=INK, bold=True, anchor="start"))
    p.append(_milestone(slot(3), axy, True, "1972", "Керніґан: посібник B", "перший «hello, world»", CREATE))
    p.append(_milestone(slot(4), axy, True, "1973", "Рітчі й Томпсон", "ядро Unix на C", CREATE))
    p.append(_milestone(slot(5), axy, True, "1978", "книжка K&R", "робить обрядом", SPREAD))

    # легенда
    lx = W / 2
    p.append(circle(lx - 150, H - 20, 5.5, fill=CREATE, stroke=CREATE))
    p.append(text(lx - 140, H - 16, "хто СТВОРИВ / задумав", size=10.5, color=CREATE, anchor="start", bold=True))
    p.append(circle(lx + 30, H - 20, 5.5, fill=SPREAD, stroke=SPREAD))
    p.append(text(lx + 40, H - 16, "хто ПОПУЛЯРИЗУВАВ", size=10.5, color=SPREAD, anchor="start", bold=True))

    render(os.path.join(OUT, "two-stories.svg"), W, H, *p,
           title="Дві історії, одна нитка: створив — це не популяризував")


if __name__ == "__main__":
    fig_pipeline()
    fig_loop()
    fig_two_stories()
    print("OK: figures written to", OUT)

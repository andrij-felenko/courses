# -*- coding: utf-8 -*-
"""
Фігури до ⚙️-вставки §3.6.5 — «Скільки стека з'їдено: заповнення патерном
і high-water mark (як це робить FreeRTOS)».
Окремий генератор (головний figs.py розділу не чіпаємо). Чистий Python, без залежностей.
Вивід → ./img/. Підписи — за темою: Рис. 3.6.5a.k. Імена файлів: fig-19-5a-*.svg.

Стиль (AUTHORING §9): білий фон; «1» червоний, «0» синій; поле зелене; стрілки через marker;
шрифт sans-serif. Допоміжні функції — копія зі спільного figs.py, щоб вигляд був єдиний.
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
AMBER = "#caa24a"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" font-style="{style}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ── один «байт» стека: клітинка з підписом значення ────────────────────────
def _byte(x, y, w, h, val, bg, col, lab_col=INK, fs=11.5):
    out = rect(x, y, w, h, bg, col, 1.3, 3)
    out += text(x + w / 2, y + h * 0.69, val, fs, lab_col, "middle", "bold")
    return out


# ═══════════ Рис. 3.6.5a.1 — заповнення стека патерном при створенні ════════
def fig_paint():
    W, H = 900, 524
    s = header(W, H)
    s += text(W / 2, 34, "Крок 1: щойно створений стек ЗАЛИВАЮТЬ відомим патерном", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "FreeRTOS заповнює всю виділену під задачу пам'ять байтом 0xA5 — «фарбою», по якій потім видно сліди",
              11.5, GREY, "middle", style="italic")

    # вертикальний стовпчик стека (16 байтів), вершина зверху
    bx, by, bw, bh = 250, 86, 150, 22
    n = 16
    for i in range(n):
        y = by + i * bh
        s += _byte(bx, y, bw, bh, "0xA5", "#fff4f4", RED, RED, 11)
    # межі стека
    s += text(bx - 12, by + 14, "вершина (SP старту)", 10, GREY, "end", "bold")
    s += text(bx - 12, by + n * bh - 6, "межа стека (дно)", 10, GREY, "end", "bold")
    s += line(bx - 8, by, bx + bw + 8, by, INK, 2)
    s += line(bx - 8, by + n * bh, bx + bw + 8, by + n * bh, INK, 2)
    # дужка «увесь стек = 0xA5»
    s += line(bx + bw + 16, by, bx + bw + 16, by + n * bh, RED, 2)
    s += line(bx + bw + 16, by, bx + bw + 26, by, RED, 2)
    s += line(bx + bw + 16, by + n * bh, bx + bw + 26, by + n * bh, RED, 2)
    s += text(bx + bw + 34, by + n * bh / 2 - 8, "увесь стек задачі —", 12, RED, "start", "bold")
    s += text(bx + bw + 34, by + n * bh / 2 + 10, "суцільний 0xA5", 12, RED, "start", "bold")
    s += text(bx + bw + 34, by + n * bh / 2 + 30, "(жоден байт ще не", 10, GREY, "start")
    s += text(bx + bw + 34, by + n * bh / 2 + 44, "торкнутий програмою)", 10, GREY, "start")

    # бокова панель «чому 0xA5»
    s += rect(610, 110, 250, 150, "#f4f7f4", GREEN, 1.6, 10)
    s += text(735, 134, "Чому саме 0xA5?", 12.5, GREEN, "middle", "bold")
    for i, t in enumerate(["• рідкісне в реальних даних", "  значення → малий шанс збігу",
                           "• 1010 0101 — чергування бітів,", "  помітне й «на око» в дампі",
                           "• у коді — tskSTACK_FILL_BYTE", "  (інші РТОС беруть 0xAA, 0x99)"]):
        s += text(628, 158 + i * 18, t, 10, INK, "start")

    s += rect(60, 452, W - 120, 64, "#f6f8f6", GREY, 1.4, 10)
    s += text(W / 2, 476, "Ідея проста, як сліди на свіжому снігу: засипати порожнечу відомою «фарбою», а потім дивитися, ДОКУДИ її стерли.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 500, "Заливку роблять лише раз — при створенні задачі (й тільки якщо ввімкнено облік стека), тож вона майже безкоштовна.",
              10.5, GREY, "middle", style="italic")
    save("fig-19-5a-1-paint.svg", s)


# ═══════════ Рис. 3.6.5a.2 — скан і пошук high-water mark ═══════════════════
def fig_scan():
    W, H = 900, 524
    s = header(W, H)
    s += text(W / 2, 34, "Крок 2: програма попрацювала — скануємо знизу, шукаємо межу «фарби»", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "виклики писали на стек згори вниз і стерли частину 0xA5; перший уцілілий 0xA5 від дна = найглибша точка за весь час",
              11, GREY, "middle", style="italic")

    bx, by, bw, bh = 250, 86, 150, 22
    n = 16
    used = 9          # верхні 9 байтів стерті (програма ними скористалась)
    hwm_idx = used    # перший уцілілий 0xA5 від вершини = індекс used
    used_vals = ["0x3F", "0x00", "0x12", "0xE4", "0x44", "0x45", "0x7A", "0x01", "0xC8"]
    for i in range(n):
        y = by + i * bh
        if i < used:
            s += _byte(bx, y, bw, bh, used_vals[i], "#eef3fb", BLUE, INK, 10.5)
        else:
            s += _byte(bx, y, bw, bh, "0xA5", "#fff4f4", RED, RED, 11)
    s += line(bx - 8, by, bx + bw + 8, by, INK, 2)
    s += line(bx - 8, by + n * bh, bx + bw + 8, by + n * bh, INK, 2)
    s += text(bx - 12, by + 14, "вершина", 10, GREY, "end", "bold")
    s += text(bx - 12, by + n * bh - 6, "дно (звідси скан →)", 10, GREY, "end", "bold")

    # напрям сканування: від дна вгору
    s += arrow(bx + bw + 70, by + n * bh - 6, bx + bw + 70, by + used * bh + 4, GREEN, 2.4)
    s += text(bx + bw + 80, by + (used + n) * bh / 2, "скан", 10.5, GREEN, "start", "bold")
    s += text(bx + bw + 80, by + (used + n) * bh / 2 + 16, "знизу", 10.5, GREEN, "start", "bold")

    # лінія HWM
    hy = by + hwm_idx * bh
    s += line(bx - 30, hy, bx + bw + 200, hy, AMBER, 2.2, "6 4")
    s += text(bx + bw + 210, hy + 4, "HIGH-WATER MARK", 11.5, "#9a7322", "start", "bold")
    s += text(bx + bw + 210, hy + 22, "(найглибша точка)", 10, GREY, "start")

    # дужки: використано / лишилось
    s += line(bx - 26, by, bx - 26, hy, BLUE, 2)
    s += text(bx - 34, by + used * bh / 2 + 4, "макс. використано", 10.5, BLUE, "end", "bold")
    s += line(bx - 26, hy, bx - 26, by + n * bh, GREEN, 2)
    s += text(bx - 34, hy + (n - used) * bh / 2 + 4, "вільний запас", 10.5, GREEN, "end", "bold")
    s += text(bx - 34, hy + (n - used) * bh / 2 + 20, "(уцілілі 0xA5)", 9.5, GREY, "end")

    s += rect(60, 448, W - 120, 64, "#fff8e8", AMBER, 1.6, 10)
    s += text(W / 2, 472, "Це і повертає uxTaskGetStackHighWaterMark: скільки байтів стека НІКОЛИ не торкались — найменший вільний запас за весь час.",
              11, INK, "middle", "bold")
    s += text(W / 2, 496, "Близько до нуля — стек майже переповнювався (§3.6.7): час дати задачі більший стек. Багато 0xA5 — стек завеликий, можна вкоротити.",
              10.5, GREY, "middle", style="italic")
    save("fig-19-5a-2-scan.svg", s)


# ═══════════ Рис. 3.6.5a.3 — пастка: «діра» в патерні + запас ═══════════════
def fig_trap():
    W, H = 900, 526
    s = header(W, H)
    s += text(W / 2, 34, "Пастка watermark: непрочитаний буфер лишає 0xA5 — і метод його «не бачить»", 17.5, INK, "middle", "bold")
    s += text(W / 2, 56, "патерн стирається лише там, де реально ПИСАЛИ; виділене, але незаписане місце метод порахує вільним",
              11, GREY, "middle", style="italic")

    bx, by, bw, bh = 250, 88, 150, 22
    n = 16
    # верх: 5 байтів реально записані; далі 4 байти — «діра» 0xA5 всередині буфера; далі знов записаний край; решта вільна
    layout = [
        ("0x3F", "w"), ("0x00", "w"), ("0x12", "w"), ("0xE4", "w"), ("0x44", "w"),
        ("0xA5", "hole"), ("0xA5", "hole"), ("0xA5", "hole"), ("0xA5", "hole"),
        ("0x7A", "w"), ("0xC8", "w"),
        ("0xA5", "free"), ("0xA5", "free"), ("0xA5", "free"), ("0xA5", "free"), ("0xA5", "free"),
    ]
    for i, (val, kind) in enumerate(layout):
        y = by + i * bh
        if kind == "w":
            s += _byte(bx, y, bw, bh, val, "#eef3fb", BLUE, INK, 10.5)
        elif kind == "hole":
            s += _byte(bx, y, bw, bh, val, "#fdeef0", RED, RED, 11)
        else:
            s += _byte(bx, y, bw, bh, val, "#fff4f4", RED, RED, 11)
    s += line(bx - 8, by, bx + bw + 8, by, INK, 2)
    s += line(bx - 8, by + n * bh, bx + bw + 8, by + n * bh, INK, 2)
    s += text(bx - 12, by + 14, "вершина", 10, GREY, "end", "bold")
    s += text(bx - 12, by + n * bh - 6, "дно", 10, GREY, "end", "bold")

    # позначка «діра» всередині використаного діапазону
    s += line(bx + bw + 16, by + 5 * bh, bx + bw + 16, by + 9 * bh, RED, 2)
    s += text(bx + bw + 24, by + 7 * bh + 4, "виділений буфер,", 10.5, RED, "start", "bold")
    s += text(bx + bw + 24, by + 7 * bh + 20, "але НЕ ввесь записаний", 10.5, RED, "start", "bold")
    s += text(bx + bw + 24, by + 7 * bh + 38, "→ тут уцілів 0xA5", 10, GREY, "start", style="italic")

    # де метод поставить «межу»: на найнижчому стертому байті (індекс 11 — край буфера 0xC8)
    real_idx = 11    # перший 0xA5 від дна = справжня межа торкання
    ry = by + real_idx * bh
    s += line(bx - 30, ry, bx + bw + 220, ry, AMBER, 2.2, "6 4")
    s += text(bx + bw + 226, ry + 4, "сюди метод ставить межу", 10.5, "#9a7322", "start", "bold")
    s += text(bx + bw + 226, ry + 21, "(перший 0xA5 від дна)", 9.5, GREY, "start")

    s += rect(60, 452, W - 120, 66, "#f6f8f6", GREY, 1.4, 10)
    s += text(W / 2, 476, "Метод чесний лише знизу: він знаходить ПЕРШИЙ 0xA5 від дна. «Діра» 0xA5 у вже використаному буфері його не бентежить —",
              11, INK, "middle", "bold")
    s += text(W / 2, 498, "та якби сплеск стека торкнувся стека ЛИШЕ раз і коротко, межа могла б недооцінити пік. Тому залишають ЗАПАС (×1.5–2), а не «впритул».",
              10.5, GREY, "middle", style="italic")
    save("fig-19-5a-3-trap.svg", s)


if __name__ == "__main__":
    fig_paint()
    fig_scan()
    fig_trap()
    print("done: 3 figs for §3.6.5a")

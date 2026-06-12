# -*- coding: utf-8 -*-
"""
Фігури для ⚙️-вставки §27.7a — «Ловимо переповнення стека: канарки, watermark,
заповнення патерном».

Стиль: той самий, що й figs.py розділу 27 — чистий Python, без сторонніх
залежностей; ті самі примітиви header/footer/text/rect/arrow/line.
Вивід → ./img/ (поряд із fig-27-7-*.svg).

Нумерація: Рис. 4.10.7a.1 і Рис. 4.10.7a.2.
Файли: fig-27-7a-1-paint-and-watermark.svg, fig-27-7a-2-freertos-check-methods.svg
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── палітра (та сама, що в figs.py) ─────────────────────────────────────────
RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
LAMB  = "#fff6e0"
GOLD  = "#caa24a"
PURP  = "#7a4fb0"
LPURP = "#efe9f7"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"

ORANGE  = "#d06c00"
LORANGE = "#fff3e4"
TEAL    = "#1a7a6e"
LTEAL   = "#e4f5f3"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'  <marker id="aOrange" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{ORANGE}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {
    INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen",
    GREY: "aGrey", ORANGE: "aOrange",
}


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
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ═════════════════════════════════════════════════════════════════════════════
# §27.7a ⚙️ stack-overflow detection
# ═════════════════════════════════════════════════════════════════════════════

# ── Рис. 4.10.7a.1 — фарбування стека патерном і водяний знак ────────────────
def fig7a1_paint_and_watermark():
    """
    Два вертикальні стеки поряд: «нормальний запас» і «майже переповнення».
    Стек росте донизу (адреси вгору), але на малюнку верх — «межа стека»
    (найнижча адреса), низ — «дно» (найвища адреса, перший push).
    Зона 0xA5 — від дна догори; watermark = де закінчується незаймана зона.
    """
    W, H = 960, 500
    s = header(W, H)

    # ── Заголовок ─────────────────────────────────────────────────────────────
    s += text(W / 2, 32, "Фарбування патерном 0xA5 і водяний знак (high-water mark)", 16, INK, "middle", "bold")
    s += text(W / 2, 54, "уцілілий хвіст візерунка від дна = стек, якого ніколи не торкались; його й рахує uxTaskGetStackHighWaterMark", 9.4, GREY, "middle", style="italic")

    # ── Спільні параметри стовпця ─────────────────────────────────────────────
    STACK_W   = 170    # ширина стовпця стека
    STACK_TOP = 90     # y верхнього краю (межа стека / guard)
    STACK_BOT = 420    # y нижнього краю (дно, перший push)
    STACK_H   = STACK_BOT - STACK_TOP   # = 330

    def draw_stack(cx, used_frac, label, col_used, col_free, col_border):
        """
        cx       — центр стовпця
        used_frac — частка висоти, яку «затерто» (від межі вниз)
        """
        bx = cx - STACK_W / 2
        used_h = STACK_H * used_frac
        free_h = STACK_H - used_h

        # Фон — весь стек
        s_loc = rect(bx, STACK_TOP, STACK_W, STACK_H, "#f8f8f8", col_border, 2, 4)

        # Зона «затертого» (кадри викликів, локальні)
        s_loc += rect(bx, STACK_TOP, STACK_W, used_h, col_used, col_border, 0, 0)
        s_loc += text(cx, STACK_TOP + used_h / 2 - 8, "кадри викликів,", 9, "#ffffff" if col_used != LAMB else INK, "middle")
        s_loc += text(cx, STACK_TOP + used_h / 2 + 8, "локальні змінні", 9, "#ffffff" if col_used != LAMB else INK, "middle")

        # Зона незайманого патерну 0xA5
        free_y = STACK_TOP + used_h
        s_loc += rect(bx, free_y, STACK_W, free_h, col_free, col_border, 0, 0)
        # Штриховані рядки всередині вільної зони (намалювати 0xA5 як паттерн)
        num_lines = max(2, int(free_h / 20))
        for i in range(num_lines):
            yy = free_y + 4 + i * (free_h - 8) / max(1, num_lines - 1)
            s_loc += text(cx, yy + 4, "0xA5", 7.5, GREEN, "middle", "normal", "italic")

        return s_loc

    # ── Стовпець 1 — нормальний запас (≈ 55% зайнято) ───────────────────────
    cx1 = 220
    used1 = 0.55
    s += draw_stack(cx1, used1, "нормальний запас", BLUE, LGRN, BLUE)

    # Мітки зліва
    s += text(cx1 - STACK_W / 2 - 12, STACK_TOP + 8, "межа стека", 8.5, INK, "end", "bold")
    s += text(cx1 - STACK_W / 2 - 12, STACK_BOT + 8, "дно (перший push)", 8.5, GREY, "end")

    # Горизонтальні лінії-межі
    s += line(cx1 - STACK_W / 2 - 24, STACK_TOP, cx1 - STACK_W / 2, STACK_TOP, INK, 1.8)
    s += line(cx1 - STACK_W / 2 - 24, STACK_BOT, cx1 - STACK_W / 2, STACK_BOT, GREY, 1.4)

    # Watermark: де закінчується незаймана зона
    wm_y1 = STACK_TOP + STACK_H * used1
    s += line(cx1 - STACK_W / 2 - 10, wm_y1, cx1 + STACK_W / 2 + 80, wm_y1, RED, 2.2, dash="6,3")
    s += text(cx1 + STACK_W / 2 + 86, wm_y1 + 4, "watermark", 8.5, RED, "start", "bold")
    # Стрілка-розмір від watermark до дна = free
    s += arrow(cx1 + STACK_W / 2 + 36, STACK_BOT, cx1 + STACK_W / 2 + 36, wm_y1 + 6, GREEN, 1.6)
    s += arrow(cx1 + STACK_W / 2 + 36, wm_y1, cx1 + STACK_W / 2 + 36, STACK_BOT - 6, GREEN, 1.6)
    free_label_y = (wm_y1 + STACK_BOT) / 2
    s += text(cx1 + STACK_W / 2 + 46, free_label_y, "вільний", 8, GREEN, "start", "bold")
    s += text(cx1 + STACK_W / 2 + 46, free_label_y + 14, "запас", 8, GREEN, "start", "bold")

    # Підпис знизу
    s += text(cx1, STACK_BOT + 28, "нормальний запас", 9.5, BLUE, "middle", "bold")
    s += text(cx1, STACK_BOT + 44, "watermark далеко від межі", 8.2, GREY, "middle")

    # ── Стовпець 2 — «майже переповнення» (≈ 95% зайнято) ───────────────────
    cx2 = 570
    used2 = 0.95
    s += draw_stack(cx2, used2, "майже переповнення", RED, LGRN, RED)

    # Watermark — майже вгорі
    wm_y2 = STACK_TOP + STACK_H * used2
    s += line(cx2 - STACK_W / 2 - 10, wm_y2, cx2 + STACK_W / 2 + 80, wm_y2, RED, 2.2, dash="6,3")
    s += text(cx2 + STACK_W / 2 + 86, wm_y2 + 4, "watermark ≈ 0", 8.5, RED, "start", "bold")

    # Попереджальна стрілка знизу
    s += arrow(cx2, STACK_TOP + 70, cx2, STACK_TOP + 16, RED, 2.2)
    s += text(cx2, STACK_TOP + 84, "межа поряд!", 8.5, RED, "middle", "bold")

    # Підпис знизу
    s += text(cx2, STACK_BOT + 28, "mayже переповнення", 9.5, RED, "middle", "bold")
    s += text(cx2, STACK_BOT + 44, "патерну майже не лишилось", 8.2, GREY, "middle")

    # ── Пояснення: що рахує uxTaskGetStackHighWaterMark ─────────────────────
    s += rect(100, STACK_BOT + 60, W - 200, 50, LGRN, GREEN, 1.5, 10)
    s += text(W / 2, STACK_BOT + 82, "uxTaskGetStackHighWaterMark сканує хвіст 0xA5 від дна:", 9.8, INK, "middle", "bold")
    s += text(W / 2, STACK_BOT + 98, "скільки байтів поспіль незаймані — такий і watermark (запас у словах на Xtensa/ARM).", 9, GREY, "middle")

    # ── Легенда у правому куті ───────────────────────────────────────────────
    lx, ly = 760, STACK_TOP
    s += rect(lx, ly, 175, 82, "#fbfcff", GREY, 1.2, 8)
    s += text(lx + 88, ly + 18, "Легенда", 9, GREY, "middle", "bold")
    s += rect(lx + 12, ly + 28, 18, 14, BLUE, BLUE, 0)
    s += text(lx + 36, ly + 40, "= затертий стек", 8.5, INK, "start")
    s += rect(lx + 12, ly + 48, 18, 14, LGRN, GREEN, 0)
    s += text(lx + 36, ly + 60, "= незайманий 0xA5", 8.5, INK, "start")
    s += line(lx + 12, ly + 74, lx + 30, ly + 74, RED, 2, dash="6,3")
    s += text(lx + 36, ly + 78, "= watermark", 8.5, INK, "start")

    save("fig-27-7a-1-paint-and-watermark.svg", s)


# ── Рис. 4.10.7a.2 — два методи перевірки FreeRTOS ──────────────────────────
def fig7a2_freertos_check_methods():
    """
    Ліворуч — метод 1 (перевірка SP): таймлайн із «миттєвим» вистрибком,
    який метод 1 пропускає.
    Праворуч — метод 2 (патерн): той самий вистрибок лишає слід у зоні 0xA5,
    і метод 2 його ловить.
    Момент перевірки = перемикання контексту.
    """
    W, H = 980, 480
    s = header(W, H)

    # ── Заголовок ─────────────────────────────────────────────────────────────
    s += text(W / 2, 32, "Метод 1 vs Метод 2: як FreeRTOS перевіряє стек при перемиканні контексту", 15, INK, "middle", "bold")
    s += text(W / 2, 54, "обидва спрацьовують лише в момент перемикання (§4.10.4); різниця — що саме перевіряється", 9.2, GREY, "middle", style="italic")

    # ── Спільний «часовий» ряд стека (y-вісь = глибина стека, x = час) ──────
    # Ліворуч — метод 1
    # Праворуч — метод 2
    # Розмір кожної половини ~ 440 пікселів по ширині
    LEFT_CX  = 235
    RIGHT_CX = 730

    def draw_half(cx, method_num, method_title, method_desc,
                  col_header, col_body, catches):
        """
        Малює «таймлайн глибини стека» + вертикальні лінії перемикання + спайк.
        catches: True = метод ловить спайк, False = пропускає.
        """
        bx = cx - 200

        # -- блок-заголовок методу --
        s_loc = rect(bx, 72, 400, 52, col_body, col_header, 2, 10)
        s_loc += text(cx, 92, method_title, 11, col_header, "middle", "bold")
        s_loc += text(cx, 112, method_desc, 8.6, INK, "middle")

        # -- «зона стека» (вертикальна вісь) --
        AX_X = bx + 44        # x осі глибини
        AX_TOP = 144           # y = межа стека
        AX_BOT = 370           # y = дно (free zone)
        AXIS_W = 360           # довжина часової осі

        # Рамка «стека»
        s_loc += rect(AX_X, AX_TOP, AXIS_W, AX_BOT - AX_TOP, "#f4f8f4", GREY, 1.2, 4)

        # Мітки
        s_loc += text(AX_X - 6, AX_TOP + 6, "межа", 7.5, INK, "end")
        s_loc += text(AX_X - 6, AX_TOP + 18, "стека", 7.5, INK, "end")
        s_loc += text(AX_X - 6, AX_BOT + 4, "дно", 7.5, GREY, "end")

        # Зона патерну 0xA5 знизу (ЗАВЖДИ малюємо; метод 2 перевіряє її збереженість)
        PATTERN_H = 60   # висота зони патерну
        pattern_y = AX_BOT - PATTERN_H
        pattern_col = LGRN if not catches else LGRN
        s_loc += rect(AX_X, pattern_y, AXIS_W, PATTERN_H, pattern_col, GREEN, 0.8, 0)
        s_loc += text(AX_X + AXIS_W / 2, pattern_y + 20, "0xA5 (зона патерну)", 7.5, GREEN, "middle", "bold")
        s_loc += text(AX_X + AXIS_W / 2, pattern_y + 36, "перевіряє метод 2", 7.5, GREEN, "middle")

        # Лінія-«нормальний рівень» стека
        NORMAL_Y = AX_TOP + (AX_BOT - AX_TOP) * 0.45   # нормальна глибина
        s_loc += line(AX_X, NORMAL_Y, AX_X + AXIS_W, NORMAL_Y, BLUE, 2, dash="4,3")
        s_loc += text(AX_X + AXIS_W + 6, NORMAL_Y + 4, "SP норма", 7.5, BLUE, "start")

        # 4 вертикальні лінії перемикання контексту (рівномірно)
        sw_xs = [AX_X + AXIS_W * f for f in [0.22, 0.46, 0.69, 0.91]]
        for xsw in sw_xs:
            s_loc += line(xsw, AX_TOP, xsw, AX_BOT, GREY, 1.2, dash="3,3")

        s_loc += text(AX_X + AXIS_W * 0.06, AX_TOP - 10, "час →", 8, INK, "start", "bold")

        # Мітка «перемикання» під першою лінією
        s_loc += text(sw_xs[0], AX_BOT + 14, "перем.", 7.5, GREY, "middle")
        s_loc += text(sw_xs[0], AX_BOT + 26, "контексту", 7.5, GREY, "middle")

        # Спайк між sw_xs[1] і sw_xs[2] — миттєвий вистрибок стека за межу
        SPIKE_X1 = sw_xs[1] + (sw_xs[2] - sw_xs[1]) * 0.3
        SPIKE_X2 = sw_xs[1] + (sw_xs[2] - sw_xs[1]) * 0.7
        SPIKE_Y  = AX_TOP - 22   # вище за межу = переповнення

        # Полілінія: нормальний рівень → вистрибок → нормальний
        pts = [
            (AX_X, NORMAL_Y),
            (sw_xs[1], NORMAL_Y),
            (SPIKE_X1, NORMAL_Y),
            (SPIKE_X1, SPIKE_Y),
            (SPIKE_X2, SPIKE_Y),
            (SPIKE_X2, NORMAL_Y),
            (AX_X + AXIS_W, NORMAL_Y),
        ]
        pts_str = " ".join(f"{px:.1f},{py:.1f}" for px, py in pts)
        s_loc += (
            f'<polyline points="{pts_str}" fill="none" stroke="{RED}" '
            f'stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round"/>\n'
        )

        # Мітка «вистрибок»
        spike_cx = (SPIKE_X1 + SPIKE_X2) / 2
        s_loc += text(spike_cx, SPIKE_Y - 10, "вистрибок", 7.5, RED, "middle", "bold")
        s_loc += text(spike_cx, SPIKE_Y + 3, "(переповнення)", 7.5, RED, "middle")

        # Результат
        if catches:
            # Метод 2 ловить: помічає затертий патерн
            s_loc += rect(AX_X, pattern_y, AXIS_W, PATTERN_H, LRED, RED, 1.6, 0)
            s_loc += text(AX_X + AXIS_W / 2, pattern_y + 20, "0xA5 ЗАТЕРТО!", 7.5, RED, "middle", "bold")
            s_loc += text(AX_X + AXIS_W / 2, pattern_y + 36, "хук спрацьовує ✓", 7.5, RED, "middle")
            # позначка на моменті перевірки (sw_xs[2])
            s_loc += arrow(sw_xs[2], AX_BOT + 48, sw_xs[2], AX_BOT + 2, GREEN, 1.8)
            s_loc += text(sw_xs[2], AX_BOT + 62, "ловить!", 8, GREEN, "middle", "bold")
        else:
            # Метод 1 пропускає: SP повернувся до норми, перевірка нічого не бачить
            s_loc += text(AX_X + AXIS_W / 2, pattern_y + 20, "0xA5 (зона патерну)", 7.5, GREEN, "middle", "bold")
            s_loc += text(AX_X + AXIS_W / 2, pattern_y + 36, "НЕ перевіряє метод 1", 7.5, GREY, "middle")
            # позначка на моменті перевірки (sw_xs[2])
            s_loc += text(sw_xs[2], AX_BOT + 48, "SP у нормі →", 7.5, GREY, "middle")
            s_loc += text(sw_xs[2], AX_BOT + 62, "пропускає ✗", 8, RED, "middle", "bold")

        return s_loc

    # ── Ліва половина (Метод 1) ───────────────────────────────────────────────
    s += text(LEFT_CX, 68, "configCHECK_FOR_STACK_OVERFLOW = 1", 8.8, BLUE, "middle", "bold")
    s += draw_half(
        LEFT_CX,
        method_num=1,
        method_title="Метод 1: перевіряє лише SP",
        method_desc="при перемиканні: чи SP ≥ межі стека?",
        col_header=BLUE,
        col_body=LBLUE,
        catches=False,
    )

    # ── Розділювач ────────────────────────────────────────────────────────────
    s += line(490, 64, 490, 440, FAINT, 2)
    s += text(490, 456, "vs", 11, GREY, "middle", "bold")

    # ── Права половина (Метод 2) ──────────────────────────────────────────────
    s += text(RIGHT_CX, 68, "configCHECK_FOR_STACK_OVERFLOW = 2", 8.8, GREEN, "middle", "bold")
    s += draw_half(
        RIGHT_CX,
        method_num=2,
        method_title="Метод 2: SP + перевірка патерну",
        method_desc="+ перевіряє, чи зона 0xA5 у межі ціла",
        col_header=GREEN,
        col_body=LGRN,
        catches=True,
    )

    # ── Підсумковий блок внизу ───────────────────────────────────────────────
    s += rect(60, 418, W - 120, 50, LAMB, GOLD, 1.5, 10)
    s += text(W / 2, 438, "Метод 1: дешевий, але пропускає «миттєвий вистрибок» між двома перемиканнями.", 9.4, INK, "middle", "bold")
    s += text(W / 2, 456, "Метод 2: перевіряє слід у патерні — ловить навіть короткочасний прокол. На час налагодження лишайте метод 2.", 9, GREY, "middle")

    save("fig-27-7a-2-freertos-check-methods.svg", s)


if __name__ == "__main__":
    fig7a1_paint_and_watermark()
    fig7a2_freertos_check_methods()
    print("OK — figures for §27.7a (stack overflow detection) generated in", OUT)

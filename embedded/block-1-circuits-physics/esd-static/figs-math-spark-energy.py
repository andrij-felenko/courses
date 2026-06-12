# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для математичної вставки до теми 1.10.5 —
«Енергія іскри: ½·Q·V і чому мікроджоуля досить» (Модуль 1, Розділ 1.10).
Чистий Python, без залежностей. Вивід → ./img/ (УНІКАЛЬНІ імена; головний figs.py розділу не чіпаємо).
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Спільні хелпери скопійовано з figs.py розділу (за §9 — кожен скрипт самодостатній).
Нумерація: вставка 🧮 до теми 1.10.5 → Рис. 1.10.5m.N.
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED = "#c0271e"
BLUE = "#1f47b5"
GREEN = "#1f8a3b"
INK = "#1b1b1b"
GREY = "#8a8a8a"
FAINT = "#e4e4e4"
COPPER = "#cf8b5e"
ORANGE = "#e08030"
PURPLE = "#7a3fae"
FONT = "Segoe UI, Arial, Helvetica, sans-serif"


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
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'  <marker id="aOrange" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{ORANGE}"/></marker>\n'
        f'  <marker id="aPurple" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{PURPLE}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen",
         GREY: "aGrey", ORANGE: "aOrange", PURPLE: "aPurple"}


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


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def polygon(points, fill=INK, stroke="none", sw=0):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n'


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# ════════════════════════════════════════════════════════════════════════════
#  Вставка 🧮 до теми 1.10.5 — енергія іскри ½·Q·V.  Рис. 1.10.5m.N
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 1.10.5m.1 — звідки ½: площа трикутника під лінією напруги ───────────
def fig_half_qv():
    W, H = 1000, 480
    s = header(W, H)
    s += text(W / 2, 32, "Звідки береться ½: енергія — це площа під лінією напруги",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "заряд заходить порціями проти дедалі вищої напруги (V = q/C росте від 0 до V)",
              11.5, GREY, "middle", style="italic")

    # осі
    ox, oy = 130, 410
    aw, ah = 560, 300
    s += line(ox, oy, ox + aw, oy, INK, 2)
    s += polygon([(ox + aw, oy), (ox + aw - 12, oy - 5), (ox + aw - 12, oy + 5)], INK)
    s += line(ox, oy, ox, oy - ah, INK, 2)
    s += polygon([(ox, oy - ah), (ox - 5, oy - ah + 12), (ox + 5, oy - ah + 12)], INK)
    s += text(ox + aw / 2, oy + 42, "накопичений заряд  q  →  Q", 13, INK, "middle", "bold")
    s += (f'<text x="48" y="{oy - ah/2:.1f}" font-family="{FONT}" font-size="13" '
          f'fill="{INK}" text-anchor="middle" font-weight="bold" '
          f'transform="rotate(-90 48 {oy - ah/2:.1f})">напруга на тілі  V</text>\n')

    # координати кутових точок
    qx = ox + aw - 90          # x при повному заряді Q
    vy = oy - ah + 60          # y при повній напрузі V

    # сірий прямокутник Q·V (наївна оцінка)
    s += rect(ox, vy, qx - ox, oy - vy, "#f0f0f0", GREY, 1.3, 0)
    # верхній трикутник — «чого не довелося платити» (заштрихуємо світло-сірим)
    s += polygon([(ox, vy), (qx, vy), (ox, oy)], "#e8e8e8", GREY, 0)
    # нижній трикутник — реальна енергія ½QV
    s += polygon([(ox, oy), (qx, vy), (qx, oy)], "#dfeede", GREEN, 0)
    # лінія напруги V = q/C
    s += line(ox, oy, qx, vy, GREEN, 3.2)

    # пунктири до повних Q і V
    s += line(qx, oy, qx, vy, INK, 1.4, "5,4")
    s += line(ox, vy, qx, vy, INK, 1.4, "5,4")
    s += text(qx, oy + 20, "Q", 14, INK, "middle", "bold")
    s += text(ox - 12, vy + 4, "V", 14, INK, "end", "bold")

    # підписи площ
    s += text(ox + (qx - ox) * 0.62, oy - (oy - vy) * 0.28,
              "W = ½·Q·V", 17, GREEN, "middle", "bold")
    s += text(ox + (qx - ox) * 0.62, oy - (oy - vy) * 0.28 + 20,
              "(площа трикутника)", 10.5, GREEN, "middle", style="italic")
    s += text(ox + (qx - ox) * 0.30, vy + (oy - vy) * 0.30,
              "цього не платимо:", 10.5, GREY, "middle")
    s += text(ox + (qx - ox) * 0.30, vy + (oy - vy) * 0.30 + 15,
              "спочатку V була низькою", 10.5, GREY, "middle")

    # точка-маркер «поточна порція»
    midx = ox + (qx - ox) * 0.45
    midy = oy + (vy - oy) * 0.45
    s += circle(midx, midy, 5, "#ffffff", RED, 2)
    s += arrow(midx + 70, midy - 46, midx + 8, midy - 6, RED, 1.8)
    s += text(midx + 74, midy - 52, "порція dq заходить", 10.5, RED, "start", "bold")
    s += text(midx + 74, midy - 38, "проти напруги q/C", 10.5, RED, "start")

    # права панель — три записи формули
    px = ox + aw + 60
    pw = W - px - 40
    s += rect(px, 95, pw, 300, "#ffffff", INK, 1.6, 12)
    s += text(px + pw / 2, 124, "Одна енергія — три записи", 14, INK, "middle", "bold")

    rows = [
        ("W = ½·Q·V", "коли відомі заряд і напруга", GREEN),
        ("W = ½·C·V²", "робочий: ємність × напруга²", BLUE),
        ("W = Q²/(2·C)", "коли фіксований заряд", PURPLE),
    ]
    yy = 162
    for f, note, col in rows:
        s += rect(px + 18, yy - 22, pw - 36, 44, "#fafafa", col, 1.4, 7)
        s += text(px + pw / 2, yy, f, 17, col, "middle", "bold")
        s += text(px + pw / 2, yy + 17, note, 9.8, GREY, "middle", style="italic")
        yy += 60
    s += line(px + 18, yy - 6, px + pw - 18, yy - 6, FAINT, 1.4)
    s += text(px + pw / 2, yy + 14, "підстав Q = C·V —", 10.5, INK, "middle")
    s += text(px + pw / 2, yy + 30, "і одне переходить в інше", 10.5, INK, "middle")
    s += text(px + pw / 2, yy + 50, "той самий ½, що в ½·m·v² і ½·k·x²",
              10, RED, "middle", "bold")

    save("fig-r10-s5m-1-half-qv.svg", s)


# ── Рис. 1.10.5m.2 — та сама енергія: розкидана в палець vs у затвор ──────────
def fig_density():
    W, H = 1000, 470
    s = header(W, H)
    s += text(W / 2, 32, "Та сама енергія — протилежний наслідок: вирішує концентрація",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "≈ 1 мДж однаково; різниця в тому, у який ОБ'ЄМ і за який ЧАС вона вливається",
              11.5, GREY, "middle", style="italic")

    # спільна «торба енергії» вгорі по центру
    cx = W / 2
    s += rect(cx - 95, 78, 190, 40, "#fff4e6", ORANGE, 1.8, 10)
    s += text(cx, 104, "одна порція ≈ 1 мДж", 13, ORANGE, "middle", "bold")
    s += arrow(cx - 70, 122, 245, 175, INK, 2)
    s += arrow(cx + 70, 122, 755, 175, INK, 2)

    # ── ліва панель: розряд у палець ──
    lx, ly, lw, lh = 70, 150, 360, 280
    s += rect(lx, ly, lw, lh, "#f7f9ff", BLUE, 1.6, 12)
    s += text(lx + lw / 2, ly + 26, "Розряд у ПАЛЕЦЬ", 14, BLUE, "middle", "bold")
    # схематична рука/тіло — великий об'єм
    bx = lx + lw / 2
    s += rect(bx - 70, ly + 60, 140, 150, "#e6edff", BLUE, 1.4, 16)
    s += text(bx, ly + 130, "великий об'єм", 12, BLUE, "middle", "bold")
    s += text(bx, ly + 150, "(усе тіло)", 11, GREY, "middle", style="italic")
    # маленька іскра в палець
    s += polyline([(bx, ly + 60), (bx - 8, ly + 48), (bx + 6, ly + 40),
                   (bx - 4, ly + 30)], RED, 2.4)
    s += text(lx + lw / 2, ly + 232, "повільно, на великий об'єм", 11, INK, "middle")
    s += text(lx + lw / 2, ly + 252, "густина мізерна → лише легкий укол",
              11, GREEN, "middle", "bold")

    # ── права панель: розряд у затвор ──
    rx, ry, rw, rh = W - 430, 150, 360, 280
    s += rect(rx, ry, rw, rh, "#fff5f5", RED, 1.6, 12)
    s += text(rx + rw / 2, ry + 26, "Розряд у ЗАТВОР мікросхеми", 14, RED, "middle", "bold")
    # збільшене скло — мікроскопічна плямка ізолятора
    gx = rx + rw / 2
    gy = ry + 120
    # ніжка/доріжка
    s += line(rx + 40, gy, gx - 46, gy, COPPER, 4)
    s += text(rx + 40, gy - 10, "ніжка", 10.5, COPPER, "start")
    # «лупа» — кружок із тонким шаром ізолятора
    s += circle(gx, gy, 46, "#ffffff", INK, 2)
    s += rect(gx - 34, gy - 4, 68, 8, "#ffe0e0", RED, 1.4, 1)  # тонкий ізолятор
    s += text(gx, gy + 30, "ізолятор", 9.5, RED, "middle", "bold")
    s += text(gx, gy + 42, "одиниці нм", 8.8, GREY, "middle", style="italic")
    # пробій — зигзаг крізь ізолятор
    s += polyline([(gx - 6, gy - 22), (gx + 4, gy - 8), (gx - 4, gy),
                   (gx + 6, gy + 10), (gx - 2, gy + 22)], RED, 2.6)
    # ручка лупи
    s += line(gx + 33, gy + 33, gx + 60, gy + 60, INK, 3)

    s += text(rx + rw / 2, ry + 200, "крихітний об'єм, за наносекунди", 11, INK, "middle")
    s += text(rx + rw / 2, ry + 222, "P = W/t величезна → пробій і плавлення",
              11, RED, "middle", "bold")
    s += text(rx + rw / 2, ry + 244, "0.2 мДж / 10 нс = 20 кВт (пік)",
              11.5, RED, "middle", "bold")

    # нижня смуга-висновок
    s += rect(120, H - 40, W - 240, 30, "#eef6ee", GREEN, 1.6, 8)
    s += text(W / 2, H - 19,
              "вирішує не джоуль, а джоуль на кубічний мікрометр за наносекунду",
              12.5, GREEN, "middle", "bold")

    save("fig-r10-s5m-2-density.svg", s)


if __name__ == "__main__":
    fig_half_qv()
    fig_density()
    print("OK")

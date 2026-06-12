# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для 🔌-вставки «Майстерня з нуля: три рівні бюджету верстака»
(до Розділу 1.6, Модуль 1). Чистий Python, без залежностей. Вивід → ./img/.
УНІКАЛЬНІ імена файлів (префікс fig-6-0c-), головний figs.py розділу не чіпаємо.
Стиль (AUTHORING §9): білий фон; sans-serif; '+' червоний, '−' синій; поле зелене.
"""
import os

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
FONT = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2):
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}" marker-end="url(#aInk)"/>\n')


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# --- Рис. 1.6.0.1 — три рівні бюджету верстака ----------------------------
def fig_tiers():
    W, H = 880, 470
    s = header(W, H)
    s += text(W / 2, 30, "Верстак: три рівні бюджету", 19, INK, "middle", "bold")
    s += text(W / 2, 50, "кожен рівень добудовується на попередньому",
              13, GREY, "middle", "normal", "italic")

    cols = [
        {
            "x": 24, "name": "1 · МІНІМУМ", "sub": "щоб щось ожило",
            "tint": "#eef7ef", "edge": GREEN,
            "items": ["USB / 2×AA (5 В)", "дешевий мультиметр", "макетка + перемички",
                      "бокорізи, LED, R"],
            "alive": "ожив: світлодіод,", "alive2": "дільник напруги",
        },
        {
            "x": 314, "name": "2 · РОБОЧИЙ", "sub": "щоб бачити сигнал",
            "tint": "#eef2fb", "edge": BLUE,
            "items": ["+ блок живлення", "   (CC/CV, ліміт струму)", "+ осцилограф",
                      "   (форма в часі)"],
            "alive": "видно: заряд C,", "alive2": "форма живлення",
        },
        {
            "x": 604, "name": "3 · КОМФОРТНИЙ", "sub": "щоб працювати швидко",
            "tint": "#fdf3ea", "edge": ORANGE,
            "items": ["+ паяльна станція", "+ генератор сигналів", "+ логічний аналізатор",
                      "+ щупи 1×/10×, світло"],
            "alive": "швидкість + паяні", "alive2": "плати, шини даних",
        },
    ]
    cw, top, ch = 252, 78, 320
    for c in cols:
        x = c["x"]
        s += rect(x, top, cw, ch, c["tint"], c["edge"], 2.5, 12)
        s += rect(x, top, cw, 40, c["edge"], c["edge"], 0, 12)
        s += rect(x, top + 24, cw, 16, c["edge"], c["edge"], 0, 0)
        s += text(x + cw / 2, top + 26, c["name"], 15, "#ffffff", "middle", "bold")
        s += text(x + cw / 2, top + 60, c["sub"], 13.5, c["edge"], "middle", "bold", "italic")

        # перелік набору
        iy = top + 92
        for it in c["items"]:
            s += text(x + 18, iy, it, 13, INK, "start")
            iy += 26

        # роздільна риска
        s += line(x + 16, top + 218, x + cw - 16, top + 218, FAINT, 1.6)
        s += text(x + 18, top + 244, "перший байт:", 12, GREY, "start", "bold")
        s += text(x + 18, top + 266, c["alive"], 13, c["edge"], "start", "bold")
        s += text(x + 18, top + 286, c["alive2"], 13, c["edge"], "start", "bold")

    # стрілки «добудова»
    for x0 in (276 + 24 - 24, 314 + cw):
        pass
    s += arrow(24 + cw + 4, top + ch / 2, 314 - 4, top + ch / 2, INK, 2.4)
    s += arrow(314 + cw + 4, top + ch / 2, 604 - 4, top + ch / 2, INK, 2.4)
    s += text(24 + cw + 19, top + ch / 2 - 10, "+", 22, INK, "middle", "bold")
    s += text(314 + cw + 19, top + ch / 2 - 10, "+", 22, INK, "middle", "bold")

    s += text(W / 2, H - 14,
              "усе з Модуля 1 — низьковольтні кола (USB / батарейки): безпечно, CAT I–II",
              12.5, GREY, "middle", "normal", "italic")
    save("fig-6-0c-1-tiers.svg", s)


if __name__ == "__main__":
    fig_tiers()
    print("done")

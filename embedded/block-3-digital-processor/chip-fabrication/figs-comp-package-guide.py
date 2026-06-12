# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для 🔌-вставки «Гід по корпусах на платі» (до §3.10.7, Модуль 3).
Окремий скрипт вставки (головний figs.py розділу не чіпаємо). Чистий Python, без залежностей.
Вивід → ./img/. Імена файлів — з токеном "r10-s7c", щоб не конфліктувати з фігурами теми
й з іншими вставками розділу.

Стиль (AUTHORING §9): білий фон; «+» червоний, «−» синій; поле зелене; стрілки через marker;
шрифт sans-serif; єдиний вигляд з рештою розділів. Хелпери — копія зі спільного набору розділу
(за §9 кожен скрипт самодостатній).
Нумерація підписів у тексті — Рис. 3.10.7c.k (на диску імена не перенумеровуються).
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
COPP  = "#b5762e"   # мідь/виводи
GOLD  = "#d8b24a"   # золотий дріт bond
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


def mono(x, y, s, size=13, color=INK, anchor="start", weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="Consolas, monospace" '
            f'font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def path(d, fill="none", stroke=INK, w=2):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ═══════════════════════════════════════════════════════════════════════════
# Рис. 3.10.7c.1 — родовід корпусів за тим, ЯК кристал з'єднано всередині.
# Дві гілки back-end (§3.10.7): дротяний монтаж (wire bond) → виводи по периметру
# (DIP, SOIC, QFN); перевертання кристала (flip-chip) → кульки масивом під низом (BGA).
# Праворуч — наслідок для рук: чим робиш на столі.
# ═══════════════════════════════════════════════════════════════════════════
def fig_family():
    W, H = 940, 560
    s = header(W, H)
    s += text(W / 2, 32, "Родовід корпусів: спосіб з'єднання кристала вирішує форму ніжок",
              19, INK, "middle", "bold")
    s += text(W / 2, 54, "те, що в §3.10.7 робить back-end, визначає і вигляд на платі, і чим це паяти вдома",
              12.5, GREY, "middle", style="italic")

    # корінь: кристал
    rootx, rooty = 150, 110
    s += rect(rootx - 64, rooty - 18, 128, 38, "#eef3fb", BLUE, 1.6, 8)
    s += text(rootx, rooty + 1, "голий кристал", 13.5, INK, "middle", "bold")
    s += text(rootx, rooty + 16, "(die, §3.10.6)", 10.5, GREY, "middle")

    # дві гілки back-end
    bx1, by1 = 150, 196     # wire bond
    bx2, by2 = 150, 386     # flip-chip
    s += arrow(rootx, rooty + 20, bx1, by1 - 18, INK, 1.8)
    s += arrow(rootx, rooty + 20, bx2, by2 - 18, INK, 1.8)

    s += rect(bx1 - 92, by1 - 18, 184, 40, "#fdf7ee", AMBER, 1.6, 8)
    s += text(bx1, by1 - 1, "дротяний монтаж", 13, INK, "middle", "bold")
    s += text(bx1, by1 + 15, "wire bond — золотий дротик", 10.3, GREY, "middle")

    s += rect(bx2 - 92, by2 - 18, 184, 40, "#f1f8f3", GREEN, 1.6, 8)
    s += text(bx2, by2 - 1, "перевернутий кристал", 12.5, INK, "middle", "bold")
    s += text(bx2, by2 + 15, "flip-chip — кульки під низом", 10.3, GREY, "middle")

    # ── мініатюри корпусів від кожної гілки ──
    # DIP
    def mini_dip(cx, cy):
        ss = rect(cx - 30, cy - 16, 60, 32, "#2b2b2b", "#000", 1.2, 3)
        for i in range(4):
            xx = cx - 21 + i * 14
            ss += line(xx, cy + 16, xx, cy + 28, COPP, 3)
            ss += line(xx, cy - 16, xx, cy - 28, COPP, 3)
        ss += circle(cx - 22, cy - 8, 2.4, "#fff", "#fff", 0)
        return ss

    # SOIC (gull-wing)
    def mini_soic(cx, cy):
        ss = rect(cx - 30, cy - 13, 60, 26, "#2b2b2b", "#000", 1.2, 3)
        for i in range(5):
            xx = cx - 24 + i * 12
            ss += path(f"M {xx:.0f},{cy-13:.0f} q -6,7 0,13 q 6,4 10,4", "none", COPP, 2.4)
            ss += path(f"M {xx:.0f},{cy+13:.0f} q -6,-7 0,-13 q 6,-4 10,-4", "none", COPP, 2.4)
        return ss

    # QFN (no-lead: майданчики під низом + thermal pad)
    def mini_qfn(cx, cy):
        ss = rect(cx - 28, cy - 22, 56, 44, "#2b2b2b", "#000", 1.4, 5)
        ss += rect(cx - 12, cy - 10, 24, 20, "#444", COPP, 1.2, 2)  # thermal pad натяк
        for i in range(5):
            yy = cy - 16 + i * 8
            ss += rect(cx - 30, yy, 6, 4, COPP, COPP, 0, 1)
            ss += rect(cx + 24, yy, 6, 4, COPP, COPP, 0, 1)
        return ss

    # BGA (масив кульок під низом)
    def mini_bga(cx, cy):
        ss = rect(cx - 30, cy - 20, 60, 30, "#2b2b2b", "#000", 1.4, 4)
        for i in range(5):
            for j in range(2):
                bx = cx - 22 + i * 11
                byy = cy + 14 + j * 11
                ss += circle(bx, byy, 4.2, GOLD, COPP, 1)
        return ss

    # дерево wire bond → DIP / SOIC / QFN
    leafs_wb = [
        (430, 130, "DIP", "крізь дірку · крок 2.54 мм", GREEN, mini_dip, "стіл, паяльник за 2 хв"),
        (430, 230, "SOIC", "крила назовні · крок 1.27 мм", GREEN, mini_soic, "паяльник + drag-solder"),
        (430, 330, "QFN", "майданчики під низом · 0.4–0.5 мм", AMBER, mini_qfn, "фен / піч / паста"),
    ]
    for lx, ly, name, sub, col, mini, tool in leafs_wb:
        s += arrow(bx1 + 92, by1, lx - 78, ly, GREY, 1.5)
        s += rect(lx - 78, ly - 32, 290, 64, "#ffffff", col, 1.6, 9)
        s += mini(lx - 40, ly)
        s += text(lx + 8, ly - 10, name, 15, INK, "start", "bold")
        s += text(lx + 8, ly + 7, sub, 10.8, GREY, "start")
        s += text(lx + 8, ly + 24, "вдома: " + tool, 10.8, col, "start", "bold")

    # flip-chip → BGA
    s += arrow(bx2 + 92, by2, 430 - 78, 430, GREY, 1.5)
    s += rect(430 - 78, 430 - 32, 290, 64, "#ffffff", RED, 1.6, 9)
    s += mini_bga(430 - 40, 430 - 2)
    s += text(430 + 8, 430 - 10, "BGA", 15, INK, "start", "bold")
    s += text(430 + 8, 430 + 7, "кульки масивом під низом · 0.5–1 мм", 10.5, GREY, "start")
    s += text(430 + 8, 430 + 24, "вдома: лише піч/фен, реболл, X-ray", 10.5, RED, "start", "bold")

    # вертикальна шкала «дружності до рук» справа
    sx = 760
    s += text(sx + 70, 96, "наскільки дружній", 12, INK, "middle", "bold")
    s += text(sx + 70, 112, "до паяльника на столі", 12, INK, "middle", "bold")
    s += line(sx, 130, sx, 470, GREY, 1.6)
    s += arrow(sx, 470, sx, 126, GREEN, 1.8)
    bands = [
        (140, 200, GREEN, "легко", "DIP, SOIC", "паяльник, флюс, обплетення"),
        (210, 300, AMBER, "з фокусом", "QFN", "фен або піч; паста + трафарет"),
        (310, 460, RED, "майже ні", "BGA", "реболл, контроль рентгеном"),
    ]
    for y0, y1, col, lab, who, how in bands:
        s += rect(sx + 12, y0, 158, y1 - y0, "#fcfcfc", col, 1.4, 8)
        s += text(sx + 22, y0 + 20, lab, 13, col, "start", "bold")
        s += text(sx + 22, y0 + 38, who, 12, INK, "start", "bold")
        s += text(sx + 22, y0 + 55, how, 10, GREY, "start")
    s += text(sx + 70, 490, "↑ ширші виводи назовні", 10.5, GREEN, "middle")
    s += text(sx + 70, 505, "↓ контакти ховаються під корпус", 10.5, RED, "middle")

    # підсумкова стрічка
    s += rect(60, H - 30, W - 120, 22, "#eef3fb", BLUE, 0, 6)
    s += text(W / 2, H - 15,
              "Форма ніжок — це не примха: дротяний монтаж виводить контакти по краю, flip-chip ховає їх масивом під кристалом.",
              11.3, INK, "middle")
    save("fig-r10-s7c-1-family.svg", s)


# ═══════════════════════════════════════════════════════════════════════════
# Рис. 3.10.7c.2 — два способи з'єднати кристал, у розрізі (саме матеріал §3.10.7).
# Ліворуч: кристал лицем угору на леді (leadframe), золоті дротики від площадок
# до виводів — звідси DIP/SOIC/QFN. Праворуч: кристал перевернуто, кульки припою
# прямо з'єднують його з підкладкою — звідси BGA. Видно, чому BGA коротший і
# чому до його з'єднань не дотягтись жалом.
# ═══════════════════════════════════════════════════════════════════════════
def fig_bond():
    W, H = 940, 470
    s = header(W, H)
    s += text(W / 2, 32, "Звідки беруться «ніжки»: дротяний монтаж проти перевернутого кристала",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "розріз корпуса — те, що §3.10.7 робить на back-end; ліворуч кристал лицем угору, праворуч — лицем униз",
              12, GREY, "middle", style="italic")

    # ── ЛІВО: wire bond ──
    Lx = 235
    base = 300
    s += text(Lx, 92, "Дротяний монтаж (wire bond)", 14.5, INK, "middle", "bold")
    s += text(Lx, 108, "→ DIP · SOIC · QFN", 12, AMBER, "middle", "bold")

    # компаунд-корпус (контур)
    s += path(f"M {Lx-150},{base} L {Lx-150},{base-60} Q {Lx-150},{base-78} {Lx-132},{base-78} "
              f"L {Lx+132},{base-78} Q {Lx+150},{base-78} {Lx+150},{base-60} L {Lx+150},{base} Z",
              "#f5efe6", "#2b2b2b", 1.6)
    # леда (leadframe) — площадка + виводи
    s += rect(Lx - 60, base - 18, 120, 12, COPP, "#7a4e1c", 1.2, 2)  # die paddle
    s += text(Lx, base - 4, "леда (leadframe), мідь", 10, GREY, "middle")
    # кристал лицем угору
    s += rect(Lx - 38, base - 46, 76, 28, "#3a5fa0", BLUE, 1.4, 2)
    s += text(Lx, base - 30, "кристал", 11, "#fff", "middle", "bold")
    s += text(Lx, base - 30 + 13, "лицем угору", 8.6, "#cfe0ff", "middle")
    # контактні площадки на кристалі + золоті дроти до окремих виводів.
    # Чотири пари (площадка кристала → край леди → нога назовні); внутрішня
    # площадка йде до ближчого виводу, зовнішня — до дальшого, тож дроти не зливаються.
    ay = base - 46
    wires = [
        (-30, -1, 150, 30),   # (зсув площадки, бік, виліт ноги, точка приземлення на леді)
        (-16, -1, 118, 12),
        (16,  1, 118, 12),
        (30,  1, 150, 30),
    ]
    for pxd, side, foot, land in wires:
        ax = Lx + pxd
        landx = Lx + side * land          # де дріт сідає на леду
        # золотий дріт: дуга від площадки кристала до контакту на леді
        midx = (ax + landx) / 2
        s += path(f"M {ax:.0f},{ay:.0f} Q {midx:.0f},{ay-30:.0f} {landx:.0f},{base-18:.0f}",
                  "none", GOLD, 2.2)
        # вивід-нога (gull-wing) від леди назовні корпуса вниз
        s += path(f"M {landx:.0f},{base-18:.0f} L {Lx+side*foot:.0f},{base-18:.0f} "
                  f"q {side*8},0 {side*8},8 L {Lx+side*(foot+8):.0f},{base+8:.0f}", "none", COPP, 3)
    s += text(Lx - 104, base - 74, "золотий дротик", 10, AMBER, "middle", "bold")
    s += arrow(Lx - 104, base - 68, Lx - 30, base - 44, AMBER, 1.4)
    s += text(Lx, base + 26, "виводи виходять по ПЕРИМЕТРУ — їх видно й (якщо назовні) дістати жалом",
              10.6, GREEN, "middle")

    # ── ПРАВО: flip-chip ──
    Rx = 700
    s += text(Rx, 92, "Перевернутий кристал (flip-chip)", 14.5, INK, "middle", "bold")
    s += text(Rx, 108, "→ BGA", 12, RED, "middle", "bold")

    # підкладка (substrate, мініплата)
    s += rect(Rx - 150, base - 14, 300, 14, "#1f6b3a", "#0f3d20", 1.4, 2)
    s += text(Rx, base - 2, "підкладка корпуса (substrate)", 10, "#e9f6ed", "middle")
    # кристал лицем УНИЗ
    s += rect(Rx - 70, base - 56, 140, 28, "#3a5fa0", BLUE, 1.4, 2)
    s += text(Rx, base - 40, "кристал лицем УНИЗ", 10.5, "#fff", "middle", "bold")
    # мікрокульки між кристалом і підкладкою (flip-chip bumps)
    for i in range(7):
        bx = Rx - 54 + i * 18
        s += circle(bx, base - 22, 4.6, GOLD, "#7a4e1c", 1)
    s += text(Rx + 86, base - 22, "мікрокульки", 10, AMBER, "start", "bold")
    s += text(Rx + 86, base - 9, "(прямо з кристала)", 9.2, GREY, "start")
    # великі кульки BGA знизу підкладки — масивом
    for i in range(9):
        bx = Rx - 120 + i * 30
        s += circle(bx, base + 14, 7.5, GOLD, "#7a4e1c", 1.2)
    s += text(Rx, base + 40, "кульки BGA — МАСИВ під низом, з'єднань збоку не видно",
              10.6, RED, "middle")

    # порівняльна стрічка під обома
    s += rect(60, H - 60, W - 120, 40, "#fbfbfb", FAINT, 1.4, 8)
    s += text(80, H - 40, "Коротший шлях сигналу:", 11.5, INK, "start", "bold")
    s += text(285, H - 40, "flip-chip прибирає довгий дротик — менше індуктивності, краще на ВЧ;",
              11.2, INK, "start")
    s += text(80, H - 22, "Розплата для рук:", 11.5, RED, "start", "bold")
    s += text(285, H - 22, "усі з'єднання — під кристалом/корпусом, паяльник туди не дотягнеться (лише розплав знизу).",
              11.2, INK, "start")
    save("fig-r10-s7c-2-bond.svg", s)


# ═══════════════════════════════════════════════════════════════════════════
# Рис. 3.10.7c.3 — практичний бік: як насправді посадити QFN на стіл.
# Три кроки drag/hot-air-маршруту + ключова пастка теплового майданчика (thermal
# pad / EP). Це «перший контакт» зі складним корпусом і типові граблі.
# ═══════════════════════════════════════════════════════════════════════════
def fig_solder():
    W, H = 940, 500
    s = header(W, H)
    s += text(W / 2, 32, "QFN на столі: робочий маршрут і головна пастка — тепловий майданчик",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "виводи сховані під корпусом, тож паяємо знизу або «протягуванням» по краю — і не забуваємо про майданчик-землю",
              11.8, GREY, "middle", style="italic")

    # три панелі-кроки
    panels = [
        (60,  "1 · флюс і центрування", GREEN,
         ["Густо флюсу на майданчики.",
          "Поставити корпус по ключу",
          "(скошений кут = вивід 1).",
          "Притримати — він «сяде»",
          "сам, коли припій потече."]),
        (350, "2 · пройти ряди", AMBER,
         ["Жало + крапля припою",
          "ведуть уздовж ряду —",
          "drag soldering.",
          "Надлишок прибрати мідним",
          "обплетенням (wick)."]),
        (640, "3 · тепловий майданчик", RED,
         ["Велике поле під корпусом",
          "(EP) — і земля, і тепловід.",
          "Без перехідних отворів",
          "знизу його НЕ прогріти.",
          "Часто — причина «холодної»."]),
    ]
    py = 84
    pw, ph = 250, 250
    for px, title, col, lines in panels:
        s += rect(px, py, pw, ph, "#fcfcfc", col, 1.6, 10)
        s += rect(px, py, pw, 30, col, col, 0, 10)
        s += text(px + pw / 2, py + 20, title, 13, "#fff", "middle", "bold")
        # схематичний QFN зверху
        cx, cy = px + pw / 2, py + 96
        s += rect(cx - 46, cy - 40, 92, 72, "#2b2b2b", "#000", 1.6, 7)
        # вивід 1 — скошений кут + точка
        s += path(f"M {cx-46},{cy-40+12} L {cx-46+12},{cy-40} ", "none", "#777", 2)
        s += circle(cx - 30, cy - 24, 3, "#eee", "#eee", 0)
        # майданчики по периметру
        for i in range(5):
            yy = cy - 32 + i * 16
            s += rect(cx - 56, yy, 8, 6, COPP, COPP, 0, 1)
            s += rect(cx + 48, yy, 8, 6, COPP, COPP, 0, 1)
        for i in range(4):
            xx = cx - 30 + i * 20
            s += rect(xx, cy - 50, 6, 8, COPP, COPP, 0, 1)
            s += rect(xx, cy + 32, 6, 8, COPP, COPP, 0, 1)

        if px == 60:
            # стрілки центрування
            s += arrow(cx - 70, cy, cx - 58, cy, GREEN, 1.6)
            s += arrow(cx + 70, cy, cx + 58, cy, GREEN, 1.6)
            s += text(cx, cy - 2, "ключ", 9, "#eee", "middle", "bold")
        if px == 350:
            # крапля + рух жала
            s += circle(cx - 60, cy - 32, 5, AMBER, "#7a4e1c", 1)
            s += arrow(cx - 60, cy - 28, cx - 60, cy + 30, AMBER, 2)
            s += text(cx - 60, cy + 46, "ведемо", 9, AMBER, "middle", "bold")
        if px == 640:
            # тепловий майданчик + via
            s += rect(cx - 22, cy - 18, 44, 36, "#5a3a16", AMBER, 1.4, 3)
            for vx in (-12, 0, 12):
                for vy in (-9, 9):
                    s += circle(cx + vx, cy + vy, 2.6, "#111", AMBER, 1)
            s += text(cx, cy + 52, "EP + via", 9.5, RED, "middle", "bold")

        ty = py + 162
        for ln in lines:
            s += text(px + 16, ty, ln, 11, INK, "start")
            ty += 17

    # нижня стрічка: інструмент-мінімум і вердикт
    s += rect(60, H - 56, W - 120, 38, "#eef3fb", BLUE, 1.4, 8)
    s += text(80, H - 36, "Мінімум на столі:", 11.8, INK, "start", "bold")
    s += text(245, H - 36, "флюс + тонке жало + мідне обплетення дають SOIC і навіть QFN; для BGA цього вже мало.",
              11.3, INK, "start")
    s += text(80, H - 18, "Золоте правило:", 11.8, GREEN, "start", "bold")
    s += text(245, H - 18, "бачиш у даташиті лише BGA — або фен/піч і досвід, або шукай плату-перехідник на ширший крок.",
              11.3, INK, "start")
    save("fig-r10-s7c-3-solder.svg", s)


if __name__ == "__main__":
    fig_family()
    fig_bond()
    fig_solder()
    print("r10-s7-c package-guide figures done.")

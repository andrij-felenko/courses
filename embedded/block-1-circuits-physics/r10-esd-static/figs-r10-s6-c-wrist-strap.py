# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для компонентної вставки §1.10.6c
«Браслет, мат і тестер браслетів зблизька».
Чистий Python, без залежностей. Вивід → ./img/.
Імена файлів УНІКАЛЬНІ (префікс fig-r10-s6c-*); головний figs.py розділу
не чіпається. Стиль за AUTHORING §9: білий фон, sans-serif, спільні кольори,
«+» червоний, «−» синій, поле/земля — зелене.
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#eef1f4"
AMBER = "#caa24a"
SAND  = "#fbf7ec"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"
MONO  = "Consolas, 'DejaVu Sans Mono', monospace"


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
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", GREY: "aGrey", GREEN: "aGreen", RED: "aRed", BLUE: "aBlue"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal", font=FONT):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def circle(cx, cy, r, fill="none", stroke=INK, sw=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def polyline(pts, color=INK, w=2.5, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    p = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
    return (f'<polyline points="{p}" fill="none" stroke="{color}" '
            f'stroke-width="{w}"{d} stroke-linejoin="round"/>\n')


def polygon(pts, fill="none", stroke=INK, sw=2):
    p = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
    return (f'<polygon points="{p}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{sw}" stroke-linejoin="round"/>\n')


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


def resistor(x, y, w, h, color=INK, sw=2.4):
    """Зигзаг-резистор IEC/американський, горизонтальний, центр (x,y)."""
    n = 6
    x0 = x - w / 2
    step = w / n
    pts = [(x0, y)]
    for i in range(n):
        xa = x0 + step * (i + 0.5)
        ya = y - h / 2 if i % 2 == 0 else y + h / 2
        pts.append((xa, ya))
    pts.append((x0 + w, y))
    return polyline(pts, color, sw)


def gnd_symbol(x, y, color=GREEN, sw=2.4):
    """Символ заземлення під точкою (x,y): три риски, що звужуються."""
    s = line(x, y, x, y + 14, color, sw)
    s += line(x - 16, y + 14, x + 16, y + 14, color, sw)
    s += line(x - 10, y + 20, x + 10, y + 20, color, sw)
    s += line(x - 5, y + 26, x + 5, y + 26, color, sw)
    return s


# ── Рис. 1.10.6c.1 — топологія: браслет + мат → спільна земля, де стоїть 1 МОм ──
def fig_topology():
    W, H = 940, 600
    s = header(W, H)
    s += text(W / 2, 32, "Антистатичне місце: усе стікає в одну точку через 1 МОм", 21, INK, "middle", "bold")
    s += text(W / 2, 54, "людина, мат і виріб — на спільному потенціалі; резистор гальмує СТРУМ, не заряд",
              13, GREY, "middle", style="italic")

    # ── рука/зап'ясток (ліворуч угорі) ──
    hand_x, hand_y = 150, 150
    s += circle(hand_x, hand_y, 30, FAINT, INK, 2)        # схематична долоня/зап'ясток
    s += text(hand_x, hand_y + 5, "🖐", 26, INK, "middle")
    # манжета браслета на зап'ястку
    s += rect(hand_x - 36, hand_y + 26, 72, 18, "#dfe6ee", BLUE, 2.4, rx=6)
    s += text(hand_x, hand_y + 60, "манжета на шкірі", 12, BLUE, "middle", "bold")
    s += text(hand_x, hand_y + 76, "(контакт із тілом)", 10.5, GREY, "middle", style="italic")

    # ── мат на столі (праворуч угорі) ──
    mat_x, mat_y, mat_w, mat_h = 470, 120, 320, 70
    s += rect(mat_x, mat_y, mat_w, mat_h, "#e9f3ec", GREEN, 2.4, rx=8)
    s += text(mat_x + mat_w / 2, mat_y + 26, "робочий мат (dissipative)", 13, GREEN, "middle", "bold")
    s += text(mat_x + mat_w / 2, mat_y + 45, "поверхня ~10⁶…10⁹ Ω/кв.", 11.5, "#2c6b3f", "middle", font=MONO)
    # виріб на маті
    s += rect(mat_x + 40, mat_y - 30, 70, 30, "#fff", INK, 2, rx=4)
    s += text(mat_x + 75, mat_y - 10, "плата", 11.5, INK, "middle")
    s += text(mat_x + 75, mat_y - 38, "виріб (DUT)", 10.5, GREY, "middle", style="italic")

    # ── спільна точка заземлення (common point ground) ──
    cpg_x, cpg_y = W / 2, 470
    s += rect(cpg_x - 95, cpg_y - 26, 190, 52, SAND, AMBER, 2.4, rx=10)
    s += text(cpg_x, cpg_y - 6, "спільна точка", 13, "#8a6a14", "middle", "bold")
    s += text(cpg_x, cpg_y + 12, "(common point ground)", 11, "#8a6a14", "middle", style="italic")
    s += gnd_symbol(cpg_x, cpg_y + 26, GREEN, 2.6)
    s += text(cpg_x + 30, cpg_y + 50, "захисний провідник розетки (PE) / земля", 11, GREEN, "start")

    # ── шлях від браслета: манжета → 1 МОм → спільна точка ──
    # провід від манжети вниз
    s += line(hand_x, hand_y + 44, hand_x, 300, BLUE, 2.6)
    # резистор 1 МОм у провідному шнурі
    s += resistor(hand_x, 330, 60, 26, RED, 2.8)
    s += text(hand_x - 70, 326, "1 МОм", 14, RED, "end", "bold")
    s += text(hand_x - 70, 344, "у шнурі", 11, RED, "end")
    s += line(hand_x, 343, hand_x, 420, BLUE, 2.6)
    # до спільної точки
    s += line(hand_x, 420, cpg_x - 95 + 30, 420, BLUE, 2.6)
    s += line(cpg_x - 95 + 30, 420, cpg_x - 95 + 30, cpg_y - 26, BLUE, 2.6)
    s += text(hand_x + 12, 392, "браслет: шнур + кнопка", 11.5, BLUE, "start")

    # ── шлях від мата: точка-кнопка мата → (свій резистор у шнурі) → спільна точка ──
    s += line(mat_x + mat_w - 30, mat_y + mat_h, mat_x + mat_w - 30, 360, GREEN, 2.6)
    s += resistor(mat_x + mat_w - 30, 390, 60, 26, AMBER, 2.8)
    s += text(mat_x + mat_w - 30 + 44, 386, "1 МОм", 13, "#8a6a14", "start", "bold")
    s += text(mat_x + mat_w - 30 + 44, 404, "у шнурі мата", 10.5, "#8a6a14", "start")
    s += line(mat_x + mat_w - 30, 403, mat_x + mat_w - 30, 446, GREEN, 2.6)
    s += line(cpg_x + 95 - 30, 446, mat_x + mat_w - 30, 446, GREEN, 2.6)
    s += line(cpg_x + 95 - 30, 446, cpg_x + 95 - 30, cpg_y - 26, GREEN, 2.6)
    s += text(mat_x + 8, 350, "мат: окремий шнур до тієї ж точки", 11, GREEN, "start")

    # ── напрям стікання заряду (зелені стрілки) ──
    s += arrow(hand_x + 18, 250, hand_x + 18, 300, GREEN, 2.0, dash="3 4")
    s += text(hand_x + 26, 276, "заряд стікає", 11, GREEN, "start", style="italic")

    # ── вставка: чому НЕ напряму (порівняння) ──
    bx, by, bw, bh = 700, 250, 220, 250
    s += rect(bx, by, bw, bh, "#fff", GREY, 1.8, rx=10)
    s += text(bx + bw / 2, by + 24, "Чому через резистор,", 12.5, INK, "middle", "bold")
    s += text(bx + bw / 2, by + 41, "а не дротом «у нуль»?", 12.5, INK, "middle", "bold")
    s += line(bx + 14, by + 52, bx + bw - 14, by + 52, FAINT, 1.4)
    s += text(bx + 14, by + 74, "Якщо рука торкнеться", 11, INK, "start")
    s += text(bx + 14, by + 90, "230 В, прямий дріт", 11, INK, "start")
    s += text(bx + 14, by + 106, "пустив би крізь тіло", 11, INK, "start")
    s += text(bx + 14, by + 122, "сотні мА — смертельно.", 11.5, RED, "start", "bold")
    s += line(bx + 14, by + 134, bx + bw - 14, by + 134, FAINT, 1.4)
    s += text(bx + 14, by + 156, "Через 1 МОм той самий", 11, INK, "start")
    s += text(bx + 14, by + 172, "дотик дає лише:", 11, INK, "start")
    s += text(bx + bw / 2, by + 196, "230 В / 1 МОм", 12.5, GREEN, "middle", font=MONO)
    s += text(bx + bw / 2, by + 216, "= 0.23 мА", 14, GREEN, "middle", "bold", font=MONO)
    s += text(bx + 14, by + 238, "нижче порога відчуття.", 11, "#2c6b3f", "start", style="italic")

    save("fig-r10-s6c-1-topology.svg", s)


# ── Рис. 1.10.6c.2 — тестер браслета: вікно «годен», два краї відмови ──
def fig_tester():
    W, H = 940, 540
    s = header(W, H)
    s += text(W / 2, 32, "Тестер браслета: одним натиском перевіряє весь шлях", 21, INK, "middle", "bold")
    s += text(W / 2, 54, "повний опір тіло+манжета+шнур+1 МОм має влучити у «вікно годен»",
              13, GREY, "middle", style="italic")

    # ── ліва панель: коло вимірювання ──
    s += text(175, 92, "Що міряє тестер", 14, INK, "middle", "bold")
    # рука
    s += circle(80, 150, 22, FAINT, INK, 2)
    s += text(80, 156, "🖐", 18, INK, "middle")
    s += rect(58, 168, 44, 12, "#dfe6ee", BLUE, 2, rx=4)       # манжета
    # палець на пластині тестера
    s += line(80, 128, 80, 110, INK, 2)
    s += rect(60, 96, 40, 16, "#dde3ea", INK, 2, rx=3)
    s += text(80, 108, "кнопка", 9.5, INK, "middle")
    # шлях: манжета → шнур → резистор → тестер
    s += line(80, 180, 80, 230, BLUE, 2.4)
    s += resistor(80, 252, 50, 22, RED, 2.6)
    s += text(80, 290, "1 МОм", 12, RED, "middle", "bold")
    s += line(80, 252 + 11 + 4, 80, 320, BLUE, 2.4)
    # коробочка тестера
    s += rect(140, 300, 150, 90, "#fff", INK, 2.2, rx=8)
    s += text(215, 322, "ТЕСТЕР", 13, INK, "middle", "bold")
    s += circle(170, 352, 9, "#e6f4ea", GREEN, 2)
    s += circle(215, 352, 9, "#fdeceb", RED, 2)
    s += circle(260, 352, 9, "#fdeceb", RED, 2)
    s += text(170, 378, "GOOD", 9, GREEN, "middle", "bold")
    s += text(170, 388, "(зел.)", 8, GREY, "middle")
    s += text(215, 378, "LOW", 9, RED, "middle", "bold")
    s += text(260, 378, "HIGH", 9, RED, "middle", "bold")
    # провід від резистора в тестер
    s += line(80, 320, 80, 345, BLUE, 2.4)
    s += line(80, 345, 140, 345, BLUE, 2.4)
    # друга клема — на палець (замикає коло крізь тіло)
    s += arrow(140, 322, 100, 104, GREY, 1.8, dash="4 4")
    s += text(126, 200, "коло замикається", 10.5, GREY, "start", style="italic")
    s += text(126, 214, "крізь тіло й манжету", 10.5, GREY, "start", style="italic")

    # ── права панель: числова вісь-вікно ──
    AX = 380
    axL, axR = AX + 70, W - 50
    axY = 250
    s += text((axL + axR) / 2, 92, "Вікно «годен» по опору (типовий тестер)", 14, INK, "middle", "bold")

    # лог-вісь опору 100 кΩ … 100 МΩ
    import math
    lo, hi = math.log10(1e5), math.log10(1e8)

    def X(r):
        return axL + (math.log10(r) - lo) / (hi - lo) * (axR - axL)

    # сама вісь
    s += line(axL, axY, axR, axY, INK, 2.4)
    for r, lab in [(1e5, "100к"), (1e6, "1М"), (1e7, "10М"), (1e8, "100М")]:
        x = X(r)
        s += line(x, axY - 6, x, axY + 6, INK, 2)
        s += text(x, axY + 24, lab, 12, GREY, "middle", font=MONO)
    s += text(axR, axY + 48, "опір усього шляху, Ω (лог)", 11.5, INK, "end", "bold")

    # зони
    # LOW FAIL < 750 кΩ
    s += rect(axL, axY - 40, X(7.5e5) - axL, 30, "#fdeceb", RED, 1.6, rx=4)
    # GOOD 750 кΩ … 10 МΩ
    s += rect(X(7.5e5), axY - 40, X(1e7) - X(7.5e5), 30, "#e6f4ea", GREEN, 1.8, rx=4)
    # HIGH FAIL > 10 МΩ
    s += rect(X(1e7), axY - 40, axR - X(1e7), 30, "#fdeceb", RED, 1.6, rx=4)

    s += text((axL + X(7.5e5)) / 2, axY - 20, "LOW", 12, RED, "middle", "bold")
    s += text((X(7.5e5) + X(1e7)) / 2, axY - 20, "GOOD", 13, GREEN, "middle", "bold")
    s += text((X(1e7) + axR) / 2, axY - 20, "HIGH", 12, RED, "middle", "bold")

    # межі з підписами
    s += line(X(7.5e5), axY - 44, X(7.5e5), axY + 8, GREEN, 1.8, dash="3 3")
    s += text(X(7.5e5), axY - 52, "≈750 кΩ", 11, GREEN, "middle", "bold", font=MONO)
    s += line(X(1e7), axY - 44, X(1e7), axY + 8, GREEN, 1.8, dash="3 3")
    s += text(X(1e7), axY - 52, "≈10 МΩ", 11, GREEN, "middle", "bold", font=MONO)

    # де лежить справний браслет: ~1 МΩ + тіло/контакт
    s += circle(X(1.1e6), axY, 6, "#fff", GREEN, 2.6)
    s += arrow(X(1.1e6), axY + 70, X(1.1e6), axY + 12, GREEN, 2.0)
    s += text(X(1.1e6), axY + 88, "справний браслет", 11.5, GREEN, "middle", "bold")
    s += text(X(1.1e6), axY + 104, "≈1 МΩ (+ контакт)", 11, "#2c6b3f", "middle", font=MONO)

    # причини країв
    s += text(axL, axY + 150, "LOW (замало опору):", 12, RED, "start", "bold")
    s += text(axL, axY + 168, "• резистор пробитий або в обхід", 11, INK, "start")
    s += text(axL, axY + 184, "• манжета мокра/із фольги без 1 МОм", 11, INK, "start")
    s += text(axL, axY + 200, "  → захисту від струму НЕМАЄ", 11, RED, "start", "bold")

    s += text(X(3e6), axY + 150, "HIGH (забагато опору):", 12, RED, "start", "bold")
    s += text(X(3e6), axY + 168, "• обрив шнура, тріснута жила", 11, INK, "start")
    s += text(X(3e6), axY + 184, "• суха шкіра, манжета не прилягає", 11, INK, "start")
    s += text(X(3e6), axY + 200, "  → заряд НЕ стікає", 11, RED, "start", "bold")

    save("fig-r10-s6c-2-tester.svg", s)


if __name__ == "__main__":
    fig_topology()
    fig_tester()
    print("done.")

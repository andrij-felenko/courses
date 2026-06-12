# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для математичної вставки §1.10.2m
«Модель людського тіла (HBM): 100 пФ і 1.5 кОм».
Чистий Python, без залежностей. Вивід → ./img/.
Імена файлів УНІКАЛЬНІ (префікс fig-10-2m-hbm-*), головний figs.py розділу
не чіпається. Стиль за AUTHORING §9: білий фон, sans-serif, спільні кольори.
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#eef1f4"
AMBER = "#caa24a"
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
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", GREY: "aGrey", RED: "aRed", GREEN: "aGreen"}


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


def polyline(pts, color=INK, w=2, fill="none", dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    sp = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
    return (f'<polyline points="{sp}" fill="{fill}" stroke="{color}" '
            f'stroke-width="{w}"{d} stroke-linejoin="round" stroke-linecap="round"/>\n')


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# ── Рис. 1.10.2m.1 — еквівалентна схема HBM + крива розрядного струму ─────────
# Зліва: ємність тіла Cb=100 пФ заряджена до V; ключ замикає її через опір тіла
# Rb=1.5 кОм на пристрій (DUT). Справа: i(t) = (V/Rb)·e^(−t/τ), τ=Rb·Cb=150 нс.
def fig_circuit():
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 34, "Модель людського тіла (HBM): заряджена ємність тіла розряджається крізь опір тіла",
              19, INK, "middle", "bold")
    s += text(W / 2, 56, "Cб = 100 пФ (накопичений заряд) · Rб = 1.5 кОм (рука/шкіра) · стала часу τ = Rб·Cб = 150 нс",
              13, GREY, "middle", style="italic")

    # ── ліва частина: схема ──────────────────────────────────────────────
    Lx = 60
    top, bot = 150, 372
    # рамка «ТІЛО» (модель тіла = ємність Cб ПЛЮС послідовний опір Rб)
    s += rect(Lx, top - 20, 360, bot - top + 60, "#f6f8fb", GREY, 1.6, rx=12)
    s += text(Lx + 12, top - 28, "ТІЛО людини  (Cб + Rб)", 14, GREY, "start", "bold")

    # конденсатор Cb (дві пластини) — джерело заряду
    capx = Lx + 60
    s += line(capx, top, capx, top + 26, INK, 2.4)            # верхній вивід
    s += line(capx - 26, top + 26, capx + 26, top + 26, INK, 3.2)  # верхня пластина
    s += line(capx - 26, top + 40, capx + 26, top + 40, INK, 3.2)  # нижня пластина
    s += line(capx, top + 40, capx, bot, INK, 2.4)            # нижній вивід
    s += text(capx - 36, top + 22, "+", 22, RED, "end", "bold")
    s += text(capx - 36, top + 52, "−", 22, BLUE, "end", "bold")
    s += text(capx + 36, top + 30, "Cб", 18, INK, "start", "bold")
    s += text(capx + 36, top + 48, "100 пФ", 12.5, GREY, "start", font=MONO)
    s += text(capx + 36, top + 64, "заряджена до V", 12, GREY, "start", style="italic")

    # верхній провід до ключа
    s += line(capx, top, capx + 96, top, INK, 2.4)
    # ключ (контакт, що зараз замкнувся — палець/предмет торкнувся виводу)
    swx = capx + 96
    s += f'<circle cx="{swx:.1f}" cy="{top:.1f}" r="3.2" fill="{INK}"/>\n'
    s += f'<circle cx="{swx + 44:.1f}" cy="{top:.1f}" r="3.2" fill="{INK}"/>\n'
    s += line(swx, top, swx + 44, top - 14, GREEN, 2.8)   # важіль (момент дотику)
    s += text(swx + 2, top - 22, "дотик", 12, GREEN, "start", "bold")
    s += line(swx + 44, top, swx + 44, top, INK, 2.4)

    # резистор Rb (опір тіла) — горизонтальний зигзаг після ключа
    rx0 = swx + 44
    rx1 = rx0 + 120
    s += _resistor_h(rx0, top, rx1, top)
    s += text((rx0 + rx1) / 2, top - 14, "Rб", 17, INK, "middle", "bold")
    s += text((rx0 + rx1) / 2, top - 30, "1.5 кОм", 12.5, GREY, "middle", font=MONO)

    # ── права частина: пристрій (DUT) ────────────────────────────────────
    dutx = rx1 + 56
    s += rect(dutx, top - 24, 96, 96, "#fff4f3", RED, 2.2, rx=10)
    s += text(dutx + 48, top + 8, "DUT", 16, RED, "middle", "bold")
    s += text(dutx + 48, top + 28, "вхід", 12, GREY, "middle")
    s += text(dutx + 48, top + 44, "мікросхеми", 11.5, GREY, "middle")
    # нижній провід (повернення) від DUT назад до нижньої пластини
    s += line(dutx + 48, top + 72, dutx + 48, bot, INK, 2.4)
    s += line(dutx + 48, bot, capx, bot, INK, 2.4)
    # стрілка струму вздовж верхнього проводу
    s += arrow(rx1 + 6, top, dutx - 4, top, RED, 2.6)
    s += text((rx1 + dutx) / 2, top + 18, "i(t)", 15, RED, "middle", "bold", style="italic")
    # «земля» під нижнім проводом
    gx = (dutx + 48 + capx) / 2
    s += line(gx, bot, gx, bot + 14, INK, 2)
    s += line(gx - 12, bot + 14, gx + 12, bot + 14, INK, 2.4)
    s += line(gx - 7, bot + 19, gx + 7, bot + 19, INK, 2.2)
    s += line(gx - 3, bot + 24, gx + 3, bot + 24, INK, 2)

    # ── права частина: крива струму i(t) ─────────────────────────────────
    gx0, gy0 = 560, 430       # початок осей
    gw, gh = 300, 250
    axtop = gy0 - gh
    s += text(gx0 + gw / 2, axtop - 18, "Розрядний струм у часі", 15, INK, "middle", "bold")
    # осі
    s += arrow(gx0, gy0, gx0 + gw + 12, gy0, INK, 2)        # t
    s += arrow(gx0, gy0, gx0, axtop - 6, INK, 2)            # i
    s += text(gx0 + gw + 14, gy0 + 16, "t", 14, INK, "start", style="italic")
    s += text(gx0 - 10, axtop - 8, "i", 14, INK, "end", style="italic")

    # крива i(t) = Ipk·e^(−t/τ); по осі t — у одиницях τ (0..5τ)
    Ipk_y = axtop + 18
    base = gy0
    def yof(frac):  # frac у [0..1] від Ipk
        return base - frac * (base - Ipk_y)
    pts = []
    n = 80
    for k in range(n + 1):
        tt = 5.0 * k / n          # 0..5 τ
        frac = math.exp(-tt)
        x = gx0 + (tt / 5.0) * gw
        pts.append((x, yof(frac)))
    # вертикальний фронт від 0 до піку
    s += line(gx0, base, gx0, yof(1.0), RED, 3)
    s += polyline(pts, RED, 3)

    # пік
    s += line(gx0 - 5, yof(1.0), gx0 + 5, yof(1.0), INK, 2)
    s += text(gx0 - 10, yof(1.0) + 5, "Iпік", 13, RED, "end", "bold")
    s += text(gx0 - 10, yof(1.0) + 21, "= V/Rб", 11.5, GREY, "end", font=MONO)

    # позначка τ (63 % спаду → лишилось 37 %)
    xt = gx0 + (1.0 / 5.0) * gw
    s += line(xt, base, xt, yof(math.exp(-1)), GREY, 1.6, dash="4,4")
    s += line(gx0, yof(math.exp(-1)), xt, yof(math.exp(-1)), GREY, 1.6, dash="4,4")
    s += text(xt, base + 18, "τ", 14, GREEN, "middle", "bold")
    s += text(xt + 6, yof(math.exp(-1)) - 6, "0.37·Iпік", 11.5, GREEN, "start", font=MONO)
    # 5τ
    s += text(gx0 + gw, base + 18, "5τ ≈ 0.75 мкс", 11.5, GREY, "middle", font=MONO)

    save("fig-10-2m-hbm-circuit.svg", s)


def _resistor_h(x1, y, x2, y2):
    # горизонтальний резистор-зигзаг між (x1,y) і (x2,y)
    seg = (x2 - x1)
    pts = [(x1, y)]
    n = 6
    amp = 9
    for k in range(1, n):
        xx = x1 + seg * k / n
        yy = y - amp if k % 2 else y + amp
        pts.append((xx, yy))
    pts.append((x2, y))
    return polyline(pts, INK, 2.4)


# ── Рис. 1.10.2m.2 — три рядки чисел: напруга → пік струму, енергія ───────────
# Для V = 2/4/8 кВ показуємо Iпік=V/Rб і E=½·Cб·V² — щоб модель стала числом.
def fig_numbers():
    W, H = 880, 480
    s = header(W, H)
    s += text(W / 2, 34, "Що дають 100 пФ і 1.5 кОм у числах", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "однакові Cб і Rб; змінюється лише напруга, до якої заряджене тіло",
              13, GREY, "middle", style="italic")

    # стовпці
    cols = ["Напруга тіла V", "Пік струму  Iпік = V/Rб", "Енергія  E = ½·Cб·V²"]
    cxs = [70, 350, 615]
    cws = [260, 245, 235]
    ytop = 92
    rowh = 78
    # шапка
    s += rect(cxs[0], ytop, sum(cws), 40, FAINT, GREY, 1.6, rx=8)
    for cx, cw, cap in zip(cxs, cws, cols):
        s += text(cx + cw / 2, ytop + 26, cap, 14.5, INK, "middle", "bold")

    rows = [
        ("2 кВ", "1.3 А", "0.2 мДж", "ледь відчутно як іскра"),
        ("4 кВ", "2.7 А", "0.8 мДж", "типовий «дотик» узимку"),
        ("8 кВ", "5.3 А", "3.2 мДж", "помітна іскра й тріск"),
    ]
    y = ytop + 40
    for i, (v, ipk, e, note) in enumerate(rows):
        bg = "#ffffff" if i % 2 == 0 else "#f7f9fb"
        s += rect(cxs[0], y, sum(cws), rowh, bg, GREY, 1.2)
        s += text(cxs[0] + cws[0] / 2, y + 34, v, 22, INK, "middle", "bold", font=MONO)
        s += text(cxs[1] + cws[1] / 2, y + 34, ipk, 22, RED, "middle", "bold", font=MONO)
        s += text(cxs[2] + cws[2] / 2, y + 34, e, 22, GREEN, "middle", "bold", font=MONO)
        s += text(cxs[0] + sum(cws) / 2, y + 60, note, 12.5, GREY, "middle", style="italic")
        y += rowh

    # нижня плашка-висновок
    by = y + 16
    s += rect(cxs[0], by, sum(cws), 78, "#fbf7ec", AMBER, 2, rx=10)
    s += text(cxs[0] + sum(cws) / 2, by + 26,
              "Пік струму росте лінійно з напругою (I = V/Rб), а енергія — квадратично (E ~ V²).",
              14, INK, "middle", "bold")
    s += text(cxs[0] + sum(cws) / 2, by + 50,
              "Заряду тут мізерно (нанокулони), але крізь тонкий ізолятор входу ці ампери б'ють руйнівно.",
              13, "#7a5a14", "middle")
    s += text(cxs[0] + sum(cws) / 2, by + 70,
              "Поріг відчуття людиною (≈3 кВ) — у рази вищий за поріг загибелі мікросхеми.",
              12.5, GREY, "middle", style="italic")

    save("fig-10-2m-hbm-numbers.svg", s)


if __name__ == "__main__":
    fig_circuit()
    fig_numbers()
    print("done.")

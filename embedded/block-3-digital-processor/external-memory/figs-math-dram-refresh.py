# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для математичної вставки §3.8.2m
«Чому DRAM "тече": RC-оцінка комірки й мілісекунди до втрати біта».
Розділ 3.8 «Зовнішня пам'ять» (Модуль 3). Чистий Python, без залежностей.
Вивід → ./img/. Головний figs.py розділу НЕ чіпаємо — це самодостатній скрипт.

Стиль (AUTHORING §9): білий фон; «1» червоний, «0» синій; поле зелене;
стрілки через marker; шрифт sans-serif. Допоміжні функції — копія спільних,
щоб вигляд збігався з рештою розділів.

Нумерація підписів — за темою/вставкою: «Рис. 3.8.2m.k».
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
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", GREY: "aGrey"}


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


def _wrap(s, n):
    words = s.split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= n:
            cur = (cur + " " + w).strip()
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _cap(x, y, w=44, gap=9):
    """Дві пластини конденсатора (горизонтальні), вивід зверху в (x,y)."""
    out = line(x, y, x, y + 14, INK, 2)
    out += line(x - w / 2, y + 14, x + w / 2, y + 14, INK, 3)
    out += line(x - w / 2, y + 14 + gap, x + w / 2, y + 14 + gap, INK, 3)
    out += line(x, y + 14 + gap, x, y + 14 + gap + 14, INK, 2)
    return out


# ════════════════ Рис. 3.8.2m.1 — комірка 1T1C як RC-розряд ═════════════════
def fig_cell():
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 34, "Комірка DRAM — це конденсатор за «нещільним» вимикачем", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "один транзистор (ключ) + один конденсатор Cₛ тримають біт як ЗАРЯД; закритий ключ тече, тож заряд поволі стікає",
              11.5, GREY, "middle", style="italic")

    # ── ліворуч: схема 1T1C ────────────────────────────────────────────────
    # розрядна лінія (bit line) згори
    blx = 250
    s += line(blx, 96, blx, 150, INK, 2)
    s += text(blx, 90, "розрядна лінія (bit line)", 10.5, GREY, "middle", "bold")
    # транзистор-ключ (спрощено: канал + затвор від word line)
    s += rect(blx - 30, 150, 60, 40, "#f3f5fd", BLUE, 1.8, 6)
    s += text(blx, 168, "ключ", 11, BLUE, "middle", "bold")
    s += text(blx, 184, "(1 транзистор)", 8.5, GREY, "middle")
    # word line — затвор
    s += arrow(blx - 120, 170, blx - 32, 170, GREEN, 2)
    s += text(blx - 125, 166, "адресна лінія (word line) → відкриває ключ", 9.5, GREEN, "end", "bold")
    # вузол зберігання
    s += line(blx, 190, blx, 226, INK, 2)
    s += circle(blx, 226, 3.2, INK, INK, 1)
    s += text(blx + 12, 222, "вузол зберігання", 9.5, RED, "start", "bold")
    s += text(blx + 12, 236, "Q = Cₛ·V", 11, RED, "start", "bold")
    # конденсатор Cs
    s += _cap(blx, 226, 50, 10)
    s += text(blx + 38, 252, "Cₛ ≈ 20–30 фФ", 10.5, INK, "start", "bold")
    s += text(blx + 38, 268, "(femtofarad)", 9, GREY, "start", style="italic")
    # земля
    gy = 226 + 14 + 10 + 14
    s += line(blx, gy, blx, gy + 12, INK, 2)
    s += line(blx - 16, gy + 12, blx + 16, gy + 12, INK, 2.4)
    s += line(blx - 10, gy + 17, blx + 10, gy + 17, INK, 2)
    s += line(blx - 4, gy + 22, blx + 4, gy + 22, INK, 2)
    # «1» = заряджено, «0» = розряджено
    s += text(blx, 300, "«1» = заряджено   ·   «0» = розряджено", 10.5, INK, "middle", "bold")

    # ── праворуч: те саме як RC-розряд ──────────────────────────────────────
    ox = 600
    s += text(ox, 96, "Те саме — як RC-коло, що розряджається:", 12, INK, "middle", "bold")
    # верхній вузол
    topx, topy = ox, 130
    s += line(topx - 90, topy, topx + 90, topy, INK, 2)
    s += text(topx, topy - 8, "+V (заряд біта)", 10, RED, "middle", "bold")
    # ліва вітка: конденсатор Cs
    s += _cap(topx - 70, topy, 44, 9)
    s += text(topx - 70, topy + 58, "Cₛ", 12, INK, "middle", "bold")
    # права вітка: витоковий «резистор» R_leak (зигзаг)
    rx = topx + 70
    s += line(rx, topy, rx, topy + 10, INK, 2)
    zig = [(rx, topy + 10)]
    for i in range(6):
        dx = 9 if i % 2 == 0 else -9
        zig.append((rx + dx, topy + 16 + i * 7))
    zig.append((rx, topy + 16 + 6 * 7))
    s += polyline(zig, RED, 2.2)
    s += line(rx, topy + 16 + 6 * 7, rx, topy + 16 + 6 * 7 + 12, INK, 2)
    s += text(rx + 14, topy + 36, "R_leak", 11, RED, "start", "bold")
    s += text(rx + 14, topy + 51, "≈ 10¹²–10¹³ Ом", 9.5, RED, "start", "bold")
    s += text(rx + 14, topy + 65, "(закритий ключ", 8.5, GREY, "start", style="italic")
    s += text(rx + 14, topy + 77, "не ідеальний)", 8.5, GREY, "start", style="italic")
    # нижня шина — земля
    boty = topy + 16 + 6 * 7 + 12
    s += line(topx - 70, topy + 14 + 9 + 14, topx - 70, boty, INK, 2)
    s += line(topx - 90, boty, topx + 90, boty, INK, 2)
    s += line(topx - 14, boty + 6, topx + 14, boty + 6, INK, 2.4)
    s += line(topx - 9, boty + 11, topx + 9, boty + 11, INK, 2)
    s += line(topx - 4, boty + 16, topx + 4, boty + 16, INK, 2)
    # стрілка струму витоку
    s += arrow(rx + 30, topy + 96, rx + 30, topy + 130, RED, 1.8, "4 3")
    s += text(rx + 36, topy + 116, "I_leak", 9.5, RED, "start", "bold")

    # ── нижня плашка: три шляхи витоку ──────────────────────────────────────
    s += rect(60, 332, W - 120, 122, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 356, "Куди тече заряд: жоден ізолятор не ідеальний, тож із вузла зберігання струм сочиться трьома шляхами —",
              11.5, INK, "middle", "bold")
    paths = [
        "• підпороговий струм закритого ключа (transistor leakage) — головний винуватець",
        "• струм витоку p–n-переходу вузла в підкладку (junction leakage)",
        "• витік крізь тонкий діелектрик самого конденсатора (dielectric leakage)",
    ]
    for i, p in enumerate(paths):
        s += text(110, 378 + i * 19, p, 10.5, INK, "start")
    s += text(W / 2, 446, "Усі три разом — це і є той «нещільний вимикач»: великий, але СКІНЧЕННИЙ опір R_leak паралельно до Cₛ.",
              10, GREY, "middle", style="italic")
    save("fig-3-8-2m-1-cell.svg", s)


# ═══════════ Рис. 3.8.2m.2 — експонента розряду й вікно регенерації ═════════
def fig_decay():
    W, H = 900, 500
    s = header(W, H)
    s += text(W / 2, 34, "Як біт «тане»: V(t) = V₀·e^(−t/τ) і вікно до регенерації", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "напруга на Cₛ спадає по експоненті зі сталою часу τ = R_leak·Cₛ; біт «втрачено», щойно вона впаде нижче порога підсилювача",
              11, GREY, "middle", style="italic")

    # осі
    ax0, ay0 = 110, 380          # початок координат
    axw, ayh = 680, 250          # довжина осей
    s += arrow(ax0, ay0, ax0 + axw + 20, ay0, INK, 2)
    s += arrow(ax0, ay0, ax0, ay0 - ayh - 20, INK, 2)
    s += text(ax0 + axw + 22, ay0 + 16, "час t", 12, INK, "start", "bold")
    s += text(ax0 - 16, ay0 - ayh - 26, "напруга на Cₛ", 12, INK, "start", "bold")

    V0 = ay0 - ayh + 10          # рівень V0 (верх)
    Vh = ay0 - ayh * 0.5         # половина
    Vth = ay0 - ayh * 0.5 + 6    # поріг ≈ трохи нижче половини (рівень опорної комірки)

    # τ у пікселях; час утрати: V0·e^(−t/τ)=0.5·V0 → t=τ·ln2
    tau_px = axw * 0.34
    t_lost = tau_px * math.log(2.0)

    # ── ФОН: зона «втрачено» (праворуч від t_retain) — малюємо ПЕРШОЮ, під кривою
    s += rect(ax0 + t_lost, ay0 - ayh, axw - t_lost, ayh, "#fdeeee", "none", 0, 0)
    # ── ФОН: зелене вікно на регенерацію (ліворуч від t_retain)
    s += rect(ax0, ay0 - ayh, t_lost, ayh, "#eef7ee", "none", 0, 0)

    # рівні V0, поріг
    s += line(ax0, V0, ax0 + axw, V0, GREY, 1.2, "5 4")
    s += text(ax0 - 8, V0 + 4, "V₀", 12, RED, "end", "bold")
    s += text(ax0 + 6, V0 - 6, "повний заряд («1»)", 10, RED, "start", "bold")

    # експонента V(t) = V0 * e^(-t/tau)
    pts = []
    for i in range(0, 241):
        t = (i / 240) * axw
        v = (V0 - ay0) * math.exp(-t / tau_px) + ay0
        pts.append((ax0 + t, v))
    s += polyline(pts, RED, 2.6)

    # точка τ (63% спаду → лишилось 37%)
    v_tau = (V0 - ay0) * math.exp(-1.0) + ay0
    s += line(ax0 + tau_px, ay0, ax0 + tau_px, v_tau, GREEN, 1.4, "4 3")
    s += circle(ax0 + tau_px, v_tau, 3.4, GREEN, GREEN, 1)
    s += text(ax0 + tau_px, ay0 + 18, "τ", 13, GREEN, "middle", "bold")
    s += text(ax0 + tau_px + 6, v_tau - 8, "лишилось 37 %", 9.5, GREEN, "start", "bold")

    # поріг підсилювача читання
    s += line(ax0, Vth, ax0 + axw, Vth, BLUE, 1.6, "6 4")
    s += text(ax0 + axw, Vth - 6, "поріг підсилювача (sense amp)", 10, BLUE, "end", "bold")
    # межа t_retain — де крива перетинає поріг
    s += line(ax0 + t_lost, ay0, ax0 + t_lost, ay0 - ayh, AMBER, 1.6)
    s += circle(ax0 + t_lost, Vth, 4, "#fff", AMBER, 2)
    s += text(ax0 + t_lost, ay0 + 36, "t_retain", 11, "#9a7322", "middle", "bold")
    s += text(ax0 + t_lost, ay0 + 50, "≈ 0.7·τ", 9.5, GREY, "middle")

    # підпис зони втрати
    s += text(ax0 + t_lost + (axw - t_lost) / 2, V0 + 16, "нижче порога → біт ВТРАЧЕНО", 10.5, RED, "middle", "bold")

    # стрілка: регенерація мусить встигнути ДО t_retain
    s += arrow(ax0 + t_lost - 6, V0 - 22, ax0 + 10, V0 - 22, GREEN, 2)
    s += text(ax0 + 8 + (t_lost) / 2, V0 - 28, "вікно на регенерацію: перечитати й дозарядити", 9.5, GREEN, "middle", "bold")

    # плашка-висновок
    s += rect(60, 416, W - 120, 70, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 440, "Регенерація (refresh) — це примусово прочитати кожен рядок і записати назад ДО того, як V впаде нижче порога.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 462, "Стандарт JEDEC: оновити кожну комірку щонайменше раз на 64 мс (за спеки понад ~85 °C — удвічі частіше, ~32 мс).",
              10.5, GREY, "middle", style="italic")
    save("fig-3-8-2m-2-decay.svg", s)


# ═══════ Рис. 3.8.2m.3 — спектр утримання: DRAM vs SRAM vs Flash ════════════
def fig_spectrum():
    W, H = 900, 452
    s = header(W, H)
    s += text(W / 2, 34, "Чому тече саме DRAM: яка «герметичність» у трьох видів пам'яті", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "час утримання біта без оновлення тягнеться на 18+ порядків — і вирішує його якість «вимикача» на вузлі зберігання",
              11, GREY, "middle", style="italic")

    # три рядки: DRAM, SRAM, Flash
    rows = [
        ("DRAM (1T1C)",
         "конденсатор за нещільним ключем",
         "≈ десятки мс",
         "ПОТРІБНА регенерація: заряд стікає за мілісекунди",
         RED, "#fdf4f4"),
        ("SRAM (6T)",
         "два інвертори тримають стан активно",
         "поки є живлення",
         "регенерація НЕ потрібна — петля сама поновлює рівень (§3.6.8)",
         BLUE, "#f3f5fd"),
        ("Flash (floating gate)",
         "заряд замкнений в ізоляторі",
         "≈ роки (10+)",
         "майже ідеальна ізоляція; заряд нікуди тікати (§3.6.8)",
         GREEN, "#eef7ee"),
    ]
    y = 92
    for name, mech, hold, note, col, bg in rows:
        s += rect(70, y, 760, 96, bg, col, 1.8, 10)
        s += text(92, y + 30, name, 14, col, "start", "bold")
        s += text(92, y + 52, mech, 10.5, GREY, "start", style="italic")
        s += text(92, y + 78, note, 10.5, INK, "start", "bold")
        # права колонка — час утримання, великим
        s += line(560, y + 12, 560, y + 84, FAINT, 1.4)
        s += text(695, y + 44, "тримає біт:", 10, GREY, "middle")
        s += text(695, y + 70, hold, 14.5, col, "middle", "bold")
        y += 108
    s += text(W / 2, y + 18, "Один транзистор робить DRAM найдешевшою (мала площа на біт) — і водночас «дірявою»: за це й платимо регенерацією.",
              11, INK, "middle", "bold")
    save("fig-3-8-2m-3-spectrum.svg", s)


if __name__ == "__main__":
    fig_cell()
    fig_decay()
    fig_spectrum()
    print("OK — 3 SVG згенеровано у", OUT)

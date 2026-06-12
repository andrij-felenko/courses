# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для математично-фізичної вставки §3.9.1m
«SEU/SEL: біт-фліпи від частинок (LET, переріз, чому на висоті й у космосі гірше)».
Розділ 3.9 «Коди виявлення й корекції помилок» (Модуль 3).
Чистий Python, без залежностей. Вивід → ./img/.
Головний figs.py розділу НЕ чіпаємо — це самодостатній скрипт.

Стиль (AUTHORING §9): білий фон; «1» червоний, «0» синій; поле/безпека зелене;
стрілки через marker; шрифт sans-serif. Допоміжні функції — копія спільних,
щоб вигляд збігався з рештою розділів.

Нумерація підписів — за вставкою: «Рис. 3.9.1m.k».
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
VIOLET = "#6a3fa0"
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
        f'  <marker id="aAmber" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{AMBER}"/></marker>\n'
        f'  <marker id="aViolet" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{VIOLET}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen",
         GREY: "aGrey", AMBER: "aAmber", VIOLET: "aViolet"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal", mono=False):
    fam = "Cascadia Mono, Consolas, monospace" if mono else FONT
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" font-style="{style}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def path(d, fill="none", stroke=INK, w=2, dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"{da}/>\n'


def polyline(pts, color=INK, w=2, dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<polyline points="{p}" fill="none" stroke="{color}" stroke-width="{w}"{da} stroke-linecap="round" stroke-linejoin="round"/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ════════════ Рис. 3.9.1m.1 — механізм SEU і SEL ════════════════════════════
def fig_mechanism():
    """Один трек частинки → слід заряду в кремнії → дві різні біди:
    SEU (зібраний заряд > критичного Qcrit → біт перекинувся) і
    SEL (паразитний тиристор «засувся» → потрібне перезавантаження живлення)."""
    W, H = 960, 560
    s = header(W, H)
    s += text(W / 2, 32, "Як одна частинка перекидає біт (SEU) — і коли вона ще й «замикає» кристал (SEL)",
              19, INK, "middle", "bold")
    s += text(W / 2, 53,
              "спільний початок один: заряджена частинка лишає в кремнії тонкий слід вільного заряду; далі — два дуже різні наслідки",
              11.5, GREY, "middle", style="italic")

    # ── СПІЛЬНИЙ ПОЧАТОК: трек частинки крізь комірку ───────────────────────
    bx, by, bw, bh = 60, 92, 300, 250
    s += rect(bx, by, bw, bh, "#f4f7fb", BLUE, 1.6, 10)
    s += text(bx + bw / 2, by + 22, "СПІЛЬНИЙ ПОЧАТОК", 12.5, BLUE, "middle", "bold")
    s += text(bx + bw / 2, by + 40, "слід заряду в кремнії", 10.5, GREY, "middle", style="italic")

    # кремнієва підкладка
    sub_y = by + 150
    s += rect(bx + 24, sub_y, bw - 48, 70, "#eef0f3", GREY, 1.4, 4)
    s += text(bx + 30, sub_y + 64, "кремній (підкладка)", 9, GREY, "start", style="italic")
    # «комірка» — чутливий вузол зверху
    node_cx = bx + bw / 2
    s += rect(node_cx - 34, sub_y - 18, 68, 18, "#dfe7f5", BLUE, 1.4, 3)
    s += text(node_cx, sub_y - 5, "вузол комірки", 8.5, BLUE, "middle")

    # трек частинки (похила червона стрілка крізь вузол у підкладку)
    px1, py1 = bx + 40, by + 58
    px2, py2 = node_cx + 26, sub_y + 58
    s += arrow(px1, py1, px2, py2, RED, 2.6)
    s += text(px1 - 4, py1 - 6, "частинка", 10.5, RED, "start", "bold")
    s += text(px1 - 4, py1 + 9, "(іон / протон / вторинна", 8.3, RED, "start")
    s += text(px1 - 4, py1 + 20, "від нейтрона)", 8.3, RED, "start")

    # хмарка зарядів уздовж треку (+ червоні, − сині)
    import random
    random.seed(7)
    for t in range(11):
        f = 0.18 + 0.07 * t
        cx = px1 + (px2 - px1) * f
        cy = py1 + (py2 - py1) * f
        ox = (random.random() - 0.5) * 16
        oy = (random.random() - 0.5) * 10
        if t % 2 == 0:
            s += text(cx + ox + 6, cy + oy, "+", 11, RED, "middle", "bold")
        else:
            s += text(cx + ox - 6, cy + oy, "−", 11, BLUE, "middle", "bold")
    s += text(bx + bw / 2, sub_y + 40, "трек = доріжка з пар «електрон–дірка»", 9, INK, "middle", style="italic")

    # підпис густини треку → LET
    s += text(bx + bw / 2, by + bh - 8, "скільки заряду на міліметр треку — це і є LET", 9.5, VIOLET, "middle", "bold")

    # роздвоєння
    s += arrow(bx + bw + 4, by + 80, bx + bw + 70, by + 50, GREEN, 2.4)
    s += arrow(bx + bw + 4, by + 180, bx + bw + 70, by + 230, RED, 2.4)
    s += text(bx + bw + 12, by + 56, "малий", 9, GREY, "start")
    s += text(bx + bw + 12, by + 214, "великий", 9, GREY, "start")

    # ── ГІЛКА 1: SEU — м'яка помилка (біт перекинувся) ──────────────────────
    ux, uy, uw, uh = 438, 92, 482, 118
    s += rect(ux, uy, uw, uh, "#fdf4f4", RED, 1.8, 10)
    s += text(ux + 16, uy + 24, "SEU — single event UPSET (м'яка помилка)", 13, RED, "start", "bold")
    s += text(ux + 16, uy + 44, "зібраний заряд Q  >  критичного заряду Qcrit  →  біт перекинувся", 11, INK, "start")
    # 0 → 1
    s += text(ux + 40, uy + 90, "0", 22, BLUE, "middle", "bold", mono=True)
    s += arrow(ux + 58, uy + 84, ux + 104, uy + 84, RED, 2.4)
    s += text(ux + 122, uy + 90, "1", 22, RED, "middle", "bold", mono=True)
    s += text(ux + 168, uy + 80, "дані спотворені, але залізо ЦІЛЕ:", 10.5, INK, "start", "bold")
    s += text(ux + 168, uy + 96, "перезапис комірки лікує (тому й «м'яка»)", 10, GREY, "start", style="italic")

    # ── ГІЛКА 2: SEL — засув (паразитний тиристор) ──────────────────────────
    lx, ly, lw, lh = 438, 232, 482, 132
    s += rect(lx, ly, lw, lh, "#fff8ec", AMBER, 1.8, 10)
    s += text(lx + 16, ly + 24, "SEL — single event LATCH-UP (засув)", 13, "#8a6d1f", "start", "bold")
    s += text(lx + 16, ly + 43, "у CMOS «дрімає» паразитний тиристор (p-n-p-n); удар його ВВІМКНУВ —", 10.3, INK, "start")
    s += text(lx + 16, ly + 58, "коротке коло живлення, струм тече, доки не зняти й знову подати живлення", 10.3, INK, "start")
    # схемка тиристора-засувки
    tcx = lx + 70
    tcy = ly + 100
    for i, lab in enumerate(["p", "n", "p", "n"]):
        col = RED if lab == "p" else BLUE
        s += rect(tcx - 60 + i * 30, tcy - 12, 28, 24, "#ffffff", col, 1.6, 3)
        s += text(tcx - 60 + i * 30 + 14, tcy + 5, lab, 12, col, "middle", "bold")
    s += text(tcx - 46, tcy + 30, "паразитний p-n-p-n", 8.5, GREY, "start", style="italic")
    s += text(lx + 250, ly + 92, "загроза НЕ лише даним:", 10.5, RED, "start", "bold")
    s += text(lx + 250, ly + 108, "перегрів і вигоряння, якщо струм", 10, INK, "start")
    s += text(lx + 250, ly + 122, "не обірвати — рятунок: скинути живлення", 10, INK, "start")

    # ── нижня плашка-висновок ───────────────────────────────────────────────
    s += rect(60, 384, W - 120, 156, "#f6f6f6", GREY, 1.4, 10)
    s += text(W / 2, 408, "Що з цього випливає для Розділу 3.9", 12.5, INK, "middle", "bold")
    concl = [
        ("SEU", RED, "перекинутий біт — це саме той «м'який» збій, проти якого працюють парність (§3.9.2), CRC (§3.9.4)",
         "і коди, що виправляють (§3.9.6–3.9.7): дані псуються, але кристал справний, тож надлишковість їх рятує."),
        ("SEL", "#8a6d1f", "засув кодом не виправиш — це вже електрична аварія живлення; тут рятують схемні засоби",
         "(захист по струму, скидання живлення), а не контрольні суми. Звідси межа: коди лікують дані, не залізо."),
    ]
    yy = 432
    for tag, col, l1, l2 in concl:
        s += rect(80, yy - 14, 56, 30, "#ffffff", col, 1.6, 6)
        s += text(108, yy + 6, tag, 12, col, "middle", "bold")
        s += text(150, yy, l1, 10.3, INK, "start")
        s += text(150, yy + 16, l2, 10.3, GREY, "start")
        yy += 56
    save("fig-r09-s1m-1-seu-sel-mechanism.svg", s)


# ════════════ Рис. 3.9.1m.2 — LET, Qcrit і крива перерізу ════════════════════
def fig_let_cross_section():
    """Два пов'язані поняття: LET (густина заряду вздовж треку) і
    переріз σ(LET) — імовірнісна «мішень» комірки. Крива має поріг LETth
    і насичення σsat; площа під добутком зі спектром дає темп збоїв."""
    W, H = 960, 560
    s = header(W, H)
    s += text(W / 2, 32, "Дві величини, якими міряють чутливість: LET частинки і переріз σ комірки",
              19, INK, "middle", "bold")
    s += text(W / 2, 53,
              "LET каже, наскільки «важко б'є» частинка; переріз σ каже, яка ймовірність, що удар спричинить збій",
              11.5, GREY, "middle", style="italic")

    # ── ЛІВО: означення LET і Qcrit (стовпчик) ──────────────────────────────
    lx, ly, lw, lh = 56, 84, 322, 300
    s += rect(lx, ly, lw, lh, "#faf7fd", VIOLET, 1.6, 10)
    s += text(lx + lw / 2, ly + 24, "LET — linear energy transfer", 13, VIOLET, "middle", "bold")
    s += text(lx + lw / 2, ly + 42, "(лінійна передача енергії)", 10, GREY, "middle", style="italic")
    s += text(lx + lw / 2, ly + 70, "скільки енергії частинка лишає", 10.5, INK, "middle")
    s += text(lx + lw / 2, ly + 86, "на одиницю довжини треку", 10.5, INK, "middle")
    # одиниця
    s += rect(lx + 30, ly + 100, lw - 60, 30, "#ffffff", VIOLET, 1.4, 6)
    s += text(lx + lw / 2, ly + 120, "[ MeV · cm² / мг ]", 13, VIOLET, "middle", "bold", mono=True)
    # ланцюжок LET → заряд → порівняння з Qcrit
    s += text(lx + lw / 2, ly + 152, "більший LET → густіший слід заряду:", 10, INK, "middle", "bold")
    s += text(lx + lw / 2, ly + 172, "Q  ≈  (LET / E_пари) · q · довжина", 11, INK, "middle", mono=True)
    s += text(lx + lw / 2, ly + 188, "(E_пари ≈ 3.6 еВ на пару в кремнії)", 8.8, GREY, "middle", style="italic")
    # критерій SEU
    s += rect(lx + 22, ly + 204, lw - 44, 78, "#fdf4f4", RED, 1.6, 8)
    s += text(lx + lw / 2, ly + 226, "критерій перевертання біта:", 10.5, RED, "middle", "bold")
    s += text(lx + lw / 2, ly + 250, "Q  >  Q_crit", 17, RED, "middle", "bold", mono=True)
    s += text(lx + lw / 2, ly + 270, "Q_crit — найменший заряд, що перекидає вузол", 8.6, GREY, "middle", style="italic")

    # стрілка-зв'язка до графіка
    s += arrow(lx + lw + 6, ly + lh / 2, lx + lw + 44, ly + lh / 2, INK, 2.2)
    s += text(lx + lw + 26, ly + lh / 2 - 8, "тому", 8.5, GREY, "middle")

    # ── ПРАВО: крива перерізу σ(LET) ────────────────────────────────────────
    gx, gy = 470, 360      # початок осей (низ-ліво)
    gw, gh = 440, 248
    s += text(gx + gw / 2, gy - gh - 26, "Переріз σ(LET): «ефективна мішень» комірки", 13, INK, "middle", "bold")
    # осі
    s += arrow(gx, gy, gx + gw + 14, gy, INK, 2)
    s += arrow(gx, gy, gx, gy - gh - 14, INK, 2)
    s += text(gx + gw + 8, gy + 22, "LET", 12, INK, "middle", "bold")
    s += text(gx + gw + 8, gy + 36, "(сила удару)", 8.5, GREY, "middle")
    s += text(gx - 36, gy - gh - 2, "σ", 14, INK, "middle", "bold")
    s += text(gx - 36, gy - gh + 14, "[см²/біт]", 8.5, GREY, "middle")

    # порогова крива Вейбулла-подібна: 0 до LETth, тоді росте до насичення
    LETth_x = gx + 0.30 * gw     # поріг
    sat_y = gy - 0.82 * gh       # рівень насичення
    pts = []
    N = 60
    for i in range(N + 1):
        fx = i / N
        x = gx + fx * gw
        if x <= LETth_x:
            y = gy  # нуль до порога
        else:
            u = (x - LETth_x) / (gx + gw - LETth_x)
            val = 1 - math.exp(-(3.1 * u) ** 1.8)   # плавне насичення
            y = gy - val * 0.82 * gh
        pts.append((x, y))
    s += polyline(pts, RED, 2.8)

    # лінія насичення
    s += line(gx, sat_y, gx + gw, sat_y, GREY, 1.2, "5,4")
    s += text(gx + gw - 4, sat_y - 6, "σ_sat — насичення (усі чутливі вузли «беруться»)", 9, GREY, "end", style="italic")
    # поріг LETth
    s += line(LETth_x, gy, LETth_x, gy - 0.82 * gh - 6, AMBER, 1.6, "4,3")
    s += text(LETth_x, gy + 18, "LET_th", 10.5, "#8a6d1f", "middle", "bold")
    s += text(LETth_x, gy - 0.82 * gh - 12, "поріг: нижче — збоїв немає", 9, "#8a6d1f", "middle", "bold")
    # зона до порога
    s += rect(gx + 1, gy - 0.82 * gh - 4, LETth_x - gx - 1, 0.82 * gh + 4, "#eef7ee", "none", 0, 0)
    s += text((gx + LETth_x) / 2, gy - 0.40 * gh, "тут σ≈0", 9.5, GREEN, "middle", "bold")
    s += text((gx + LETth_x) / 2, gy - 0.40 * gh + 15, "«не пробиває»", 8.4, GREEN, "middle", style="italic")

    # стрілка зростання
    s += text(gx + 0.62 * gw, gy - 0.55 * gh, "сильніший удар →", 9.5, RED, "middle", "bold")
    s += text(gx + 0.62 * gw, gy - 0.55 * gh + 14, "вища ймовірність збою", 8.6, RED, "middle")

    # ── низ: як із цих двох виходить ТЕМП збоїв ──────────────────────────────
    s += rect(56, 392, 322, 148, "#f6f6f6", GREY, 1.4, 10)
    s += text(56 + 161, 416, "Звідки береться ТЕМП збоїв (event rate)", 11.5, INK, "middle", "bold")
    rate = [
        "Темп = скільки частинок прилетить × яка частка",
        "з них спрацює. Формально це згортка:",
        "",
        "   R  =  ∫  σ(LET) · Φ(LET) · dLET",
        "",
        "Φ(LET) — потік частинок такого LET у даному",
        "середовищі. Тому одна й та сама комірка σ(LET)",
        "збоїть РІДКО на землі й ЧАСТО в космосі —",
        "змінюється не комірка, а спектр Φ (Рис. 3.9.1m.3).",
    ]
    yy = 436
    for ln in rate:
        mono = ln.strip().startswith("R")
        s += text(72, yy, ln, 9.6, INK if not mono else VIOLET, "start", "bold" if mono else "normal", mono=mono)
        yy += 15.6
    save("fig-r09-s1m-2-let-cross-section.svg", s)


# ════════════ Рис. 3.9.1m.3 — чому на висоті й у космосі гірше ═══════════════
def fig_altitude_space():
    """Потік нейтронів проти висоти: кремнієвий екран атмосфери, максимум
    Пфотцера ~18 км, тоді LEO/далекий космос (де екрана нема зовсім).
    Праворуч — порядкова шкала «у скільки разів гірше»."""
    W, H = 960, 580
    s = header(W, H)
    s += text(W / 2, 32, "Чому на висоті й у космосі біти перекидаються частіше: тоншає щит атмосфери",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 53,
              "на рівні моря нас прикриває ~10 м водяного еквівалента повітря; що вище — то тонший щит і густіший потік частинок",
              11, GREY, "middle", style="italic")

    # ── ЛІВО: профіль «потік нейтронів vs висота» ───────────────────────────
    gx, gy = 96, 470          # низ-ліво осей
    gw, gh = 360, 360
    s += arrow(gx, gy, gx, gy - gh - 14, INK, 2)            # вісь висоти ↑
    s += arrow(gx, gy, gx + gw + 14, gy, INK, 2)            # вісь потоку →
    s += text(gx - 60, gy - gh - 2, "висота", 11.5, INK, "start", "bold")
    s += text(gx - 60, gy - gh + 13, "(км)", 8.5, GREY, "start")
    s += text(gx + gw + 8, gy + 22, "потік нейтронів", 11, INK, "middle", "bold")
    s += text(gx + gw + 8, gy + 36, "(лог-шкала →)", 8.5, GREY, "middle")

    # позначки висот на вертикалі
    alts = [(0, "0  рівень моря"), (3, "3  гора"), (12, "12  ешелон літака"),
            (18, "18  максимум Пфотцера"), (30, "30  стратостат")]
    amax = 34.0
    def ay(a):
        return gy - (a / amax) * gh
    for a, lab in alts:
        yy = ay(a)
        s += line(gx - 4, yy, gx + 4, yy, INK, 1.4)
        s += text(gx - 10, yy + 4, lab, 9, GREY, "end")

    # крива потоку: росте від рівня моря, пік ~18 км (Пфотцер), далі спад
    # горизонталь у «логарифмічних» умовних одиницях 0..1 від ширини
    def fx(rel):   # rel у 0..1
        return gx + rel * gw
    curve = []
    # будуємо знизу (0 км) вгору (34 км)
    samples = [
        (0,  0.10),
        (3,  0.24),
        (6,  0.42),
        (9,  0.60),
        (12, 0.74),
        (15, 0.86),
        (18, 0.94),   # максимум Пфотцера
        (22, 0.86),
        (26, 0.74),
        (30, 0.62),
        (34, 0.52),
    ]
    for a, rel in samples:
        curve.append((fx(rel), ay(a)))
    s += polyline(curve, RED, 3)
    s += text(fx(0.10) + 8, ay(0) - 4, "рівень моря", 8.6, GREY, "start")

    # підсвітити максимум Пфотцера
    s += circle(fx(0.94), ay(18), 4.5, RED, RED, 0)
    s += text(fx(0.94) + 10, ay(18) - 6, "пік ~18 км:", 9.2, RED, "start", "bold")
    s += text(fx(0.94) + 10, ay(18) + 8, "далі повітря замало,", 8.3, GREY, "start")
    s += text(fx(0.94) + 10, ay(18) + 19, "каскад згасає", 8.3, GREY, "start")

    # правило ~2× на 1.5 км у нижній атмосфері
    s += rect(gx + 6, ay(9) - 14, 150, 40, "#fff8ec", AMBER, 1.4, 6)
    s += text(gx + 81, ay(9) + 2, "у нижніх шарах:", 8.8, "#8a6d1f", "middle", "bold")
    s += text(gx + 81, ay(9) + 16, "≈ ×2 на кожні ~1.5 км", 9.2, "#8a6d1f", "middle", "bold")

    # позначка «атмосфера = щит»
    s += text(gx + gw * 0.5, gy - gh - 2, "тонший щит → густіший потік", 10, INK, "middle", "bold")

    # ── ПРАВО: порядкова драбина «у скільки разів гірше» ────────────────────
    rx, ry, rw = 540, 96, 372
    s += text(rx + rw / 2, ry - 8, "Порядок темпу збоїв відносно рівня моря (×)", 12.5, INK, "middle", "bold")
    rows = [
        ("рівень моря", "× 1", "опорна точка (NYC, JEDEC)", GREY, "#f6f6f6"),
        ("гора ~3 км", "× ~10", "порядок величини більше", BLUE, "#f4f7fb"),
        ("літак ~12 км", "× ~300", "сотні разів (за висотою/широтою)", AMBER, "#fff8ec"),
        ("низька орбіта (LEO)", "× ~10²–10³", "над атмосферою; додаються прямі іони", VIOLET, "#faf7fd"),
        ("далекий космос", "× значно більше", "ні атмосфери, ні магнітосфери Землі", RED, "#fdf4f4"),
    ]
    bh = 64
    yy = ry + 12
    for name, mult, note, col, bg in rows:
        s += rect(rx, yy, rw, bh - 10, bg, col, 1.6, 9)
        s += text(rx + 16, yy + 24, name, 12, INK, "start", "bold")
        s += text(rx + 16, yy + 43, note, 9.3, GREY, "start")
        s += text(rx + rw - 16, yy + 33, mult, 16, col, "end", "bold", mono=True)
        yy += bh
    s += text(rx + rw / 2, yy + 6, "числа — порядкові орієнтири; точний множник залежить",
              8.8, GREY, "middle", style="italic")
    s += text(rx + rw / 2, yy + 19, "від висоти, широти, фази сонячного циклу й екранування (перевірити)",
              8.8, GREY, "middle", style="italic")

    # ── низ: практичний висновок ────────────────────────────────────────────
    s += rect(96, 494, W - 152, 70, "#eef7ee", GREEN, 1.5, 10)
    s += text(W / 2, 517, "Практичний висновок для розробника", 12, GREEN, "middle", "bold")
    s += text(W / 2, 537,
              "Та сама плата, що роками не збоїть на столі, в авіоніці чи аеростаті ловитиме перевернуті біти помітно частіше, а на орбіті — постійно.",
              10.6, INK, "middle")
    s += text(W / 2, 555,
              "Тому висотна й космічна техніка не сподівається на «рідкість», а закладає коди корекції (§3.9.6–3.9.7) і захист живлення від SEL як норму.",
              10.2, GREY, "middle")
    save("fig-r09-s1m-3-altitude-space.svg", s)


if __name__ == "__main__":
    fig_mechanism()
    fig_let_cross_section()
    fig_altitude_space()
    print("OK — 3 SVG згенеровано у", OUT)

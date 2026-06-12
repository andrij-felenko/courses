# -*- coding: utf-8 -*-
"""
SVG-фігури для історичної вставки §3.7.5i — «Народження VHDL і Verilog».
Окремий генератор (головний figs.py не чіпаємо). Чистий Python, без залежностей.
Вивід → ./img/.  Імена: fig-r07-s5i-k-<slug>.svg.  Підписи у тексті: Рис. 3.7.5i.k.

Стиль (AUTHORING §9): білий фон; стрілки через marker; шрифт sans-serif;
єдиний вигляд із рештою розділу (допоміжні функції — копія з figs-...-history-riscv.py).
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


def _wrap(txt, width=26):
    words = txt.split()
    lines, cur = [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if len(t) > width:
            lines.append(cur); cur = wd
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines


# ═══════════ Рис. 3.7.5i.1 — дві колиски, що зійшлися ═══════════════════════
def fig_two_cradles():
    W, H = 920, 540
    s = header(W, H)
    s += text(W / 2, 34, "Дві колиски HDL: замовлення Пентагону й чип стартапу", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "майже одночасно, з протилежних світів — а вийшли двома половинами однієї ідеї",
              12.5, GREY, "middle", style="italic")

    # ── ліва колонка: VHDL (держава) ───────────────────────────────────────
    lx = 70
    s += rect(lx, 80, 360, 116, "#eef3fb", BLUE, 2.4, 10)
    s += text(lx + 180, 108, "VHDL", 22, BLUE, "middle", "bold")
    s += text(lx + 180, 130, "мова на замовлення Пентагону", 12.5, INK, "middle", style="italic")
    s += text(lx + 20, 154, "програма VHSIC міністерства оборони США", 11.5, INK)
    s += text(lx + 20, 172, "контракт ВПС 1983 р.: Intermetrics + TI + IBM", 11.5, INK)
    s += text(lx + 20, 189, "мета — ОПИСАТИ й документувати поведінку чипів", 11.5, INK)

    # ── права колонка: Verilog (бізнес) ────────────────────────────────────
    rx = 490
    s += rect(rx, 80, 360, 116, "#fbeeec", RED, 2.4, 10)
    s += text(rx + 180, 108, "Verilog", 22, RED, "middle", "bold")
    s += text(rx + 180, 130, "мова стартапу", 12.5, INK, "middle", style="italic")
    s += text(rx + 20, 154, "Gateway Design Automation, зима 1983/84", 11.5, INK)
    s += text(rx + 20, 172, "Філ Мурбі, Прабгу Ґоел, Чі-Лай Хуанг", 11.5, INK)
    s += text(rx + 20, 189, "мета — ПРОСИМУЛЮВАТИ схему, поки не спаяли", 11.5, INK)

    # ── спадні риси, що тягнуться вниз до спільної точки ───────────────────
    rowsL = ["синтаксис — як в Ada (наказ DoD)", "стандарт IEEE 1076 — 1987 р.",
             "сувора, багатослівна, з типами"]
    rowsR = ["синтаксис — у дусі C", "стандарт IEEE 1364 — 1995 р.",
             "стисла, гнучка, ближча до коду"]
    for i in range(3):
        yy = 226 + i * 30
        s += text(lx + 180, yy, "• " + rowsL[i], 12, BLUE, "middle")
        s += text(rx + 180, yy, "• " + rowsR[i], 12, RED, "middle")

    # ── стрілки сходяться ──────────────────────────────────────────────────
    midx, midy = W / 2, 470
    s += arrow(lx + 180, 320, midx - 70, midy - 26, BLUE, 2.4)
    s += arrow(rx + 180, 320, midx + 70, midy - 26, RED, 2.4)
    s += rect(midx - 168, midy - 22, 336, 66, "#eafaee", GREEN, 2.6, 10)
    s += text(midx, midy + 2, "ОДНА ідея: описати залізо текстом,", 14.5, GREEN, "middle", "bold")
    s += text(midx, midy + 24, "а машина зі слів збере схему (синтез)", 13.5, INK, "middle")
    return save("fig-r07-s5i-1-two-cradles.svg", s)


# ═══════════ Рис. 3.7.5i.2 — спільний таймлайн ─────────────────────────────
def fig_timeline():
    W, H = 920, 560
    s = header(W, H)
    s += text(W / 2, 34, "Дві мови, один шлях: від креслення до тексту", 21, INK, "middle", "bold")
    s += text(W / 2, 55, "сині віхи — VHDL (держава), червоні — Verilog (бізнес), зелена — спільне майбутнє",
              12, GREY, "middle", style="italic")

    spine = 250
    top, bot = 92, H - 30
    s += line(spine, top, spine, bot, GREY, 3)
    nodes = [
        ("1980", BLUE, "Програма VHSIC", "Міноборони США починає проєкт надшвидких чипів — і впирається: кожен постачальник ОПИСУЄ свій чип по-своєму, паперу не звести докупи"),
        ("1983", BLUE, "Контракт на VHDL", "ВПС наймають Intermetrics, TI та IBM зробити СПІЛЬНУ мову опису; синтаксис наказано взяти від Ada"),
        ("1983/84", RED, "Verilog у Gateway", "Незалежно й майже водночас Філ Мурбі з колегами пишуть Verilog та симулятор Verilog-XL — щоб ПЕРЕВІРИТИ схему до кремнію"),
        ("1987", BLUE, "VHDL → IEEE 1076", "Військову мову відкривають промисловості; вона стає першим стандартом HDL"),
        ("1987", GREEN, "Перший синтез", "З'являються інструменти, що з ОПИСУ автоматично будують схему вентилів — мова перестає лише документувати (перевірити рік)"),
        ("1989/90", RED, "Cadence купує Gateway", "Verilog стає власністю великої фірми (точний рік — перевірити)"),
        ("1990/91", RED, "Verilog у відкритий світ", "Під тиском ринку Cadence віддає мову спільноті Open Verilog International (OVI)"),
        ("1995", RED, "Verilog → IEEE 1364", "Друга мова теж стає офіційним стандартом — тепер їх дві рівні"),
        ("донині", GREEN, "Обидві живі", "VHDL і Verilog ділять світ; з Verilog виросла SystemVerilog. У навчанні й хобі (як iCE40-плати) частіше беруть Verilog"),
    ]
    n = len(nodes)
    for i, (yr, col, who, q) in enumerate(nodes):
        y = top + 22 + (bot - top - 44) * i / (n - 1)
        s += circle(spine, y, 7.5, "#fff", col, 2.8)
        s += circle(spine, y, 3, col, col, 1)
        s += text(spine - 20, y + 5, yr, 13, col, "end", "bold")
        s += text(spine + 22, y - 3, who, 14.5, col, "start", "bold")
        for j, ln in enumerate(_wrap(q, 64)):
            s += text(spine + 22, y + 14 + j * 14, ln, 11, GREY, "start")
    return save("fig-r07-s5i-2-timeline.svg", s)


# ═══════════ Рис. 3.7.5i.3 — чому «синтез ≠ виконання» ─────────────────────
def fig_synthesis():
    W, H = 920, 470
    s = header(W, H)
    s += text(W / 2, 34, "Що насправді винайшли: текст, з якого РОСТЕ схема", 20, INK, "middle", "bold")
    s += text(W / 2, 55, "те саме, що §3.7.5 зве «синтез ≠ виконання» — ось звідки ця ідея взялася історично",
              12, GREY, "middle", style="italic")

    # верхня доріжка — програма для процесора (контраст)
    py = 120
    s += text(40, py - 22, "ПРОГРАМА (звичний код, §3.5):", 13, GREY, "start", "bold")
    s += rect(40, py, 150, 46, "#f2f2f2", GREY, 2, 8)
    s += text(115, py + 28, "текст коду", 12.5, INK, "middle")
    s += arrow(196, py + 23, 268, py + 23, GREY, 2)
    s += rect(274, py, 150, 46, "#f2f2f2", GREY, 2, 8)
    s += text(349, py + 28, "інструкції", 12.5, INK, "middle")
    s += arrow(430, py + 23, 502, py + 23, GREY, 2)
    s += rect(508, py, 200, 46, "#f2f2f2", GREY, 2, 8)
    s += text(608, py + 21, "процесор виконує", 12.5, INK, "middle")
    s += text(608, py + 37, "ПО ЧЕРЗІ, такт за тактом", 10.5, GREY, "middle")
    s += text(728, py + 28, "→ дії в часі", 12, GREY, "start", "bold")

    # нижня доріжка — опис заліза (HDL)
    hy = 270
    s += text(40, hy - 22, "ОПИС ЗАЛІЗА (HDL: VHDL / Verilog):", 13, GREEN, "start", "bold")
    s += rect(40, hy, 150, 46, "#eafaee", GREEN, 2.4, 8)
    s += text(115, hy + 21, "текст ОПИСУ", 12.5, INK, "middle")
    s += text(115, hy + 37, "(що з чим з'єднано)", 10, GREY, "middle")
    s += arrow(196, hy + 23, 268, hy + 23, GREEN, 2.2)
    s += text(232, hy - 4, "СИНТЕЗ", 11, GREEN, "middle", "bold")
    s += rect(274, hy, 150, 46, "#eafaee", GREEN, 2.4, 8)
    s += text(349, hy + 21, "схема вентилів", 12.5, INK, "middle")
    s += text(349, hy + 37, "і тригерів (§3.2–3.3)", 10, GREY, "middle")
    s += arrow(430, hy + 23, 502, hy + 23, GREEN, 2.2)
    s += rect(508, hy, 200, 46, "#eafaee", GREEN, 2.4, 8)
    s += text(608, hy + 21, "усе працює РАЗОМ", 12.5, INK, "middle")
    s += text(608, hy + 37, "одночасно, у залізі", 10.5, GREY, "middle")
    s += text(728, hy + 28, "→ схема в просторі", 12, GREEN, "start", "bold")

    s += rect(60, 372, 800, 72, "#fff", INK, 1.6, 10)
    s += text(80, 396, "Ключ історії: спершу обидві мови вміли лише ОПИСАТИ й ПРОСИМУЛЮВАТИ схему (перевірити її на екрані).",
              12.5, INK, "start")
    s += text(80, 416, "Пізніше додався СИНТЕЗ — і той самий текст почав не лише описувати, а й БУДУВАТИ реальне залізо.",
              12.5, INK, "start")
    s += text(80, 434, "Тому «написати на Verilog» — це не «написати програму», а накреслити схему словами.",
              12.5, GREEN, "start", "bold")
    return save("fig-r07-s5i-3-synthesis.svg", s)


# ═══════════ Рис. 3.7.5i.4 — колективна атрибуція й чесний підсумок ────────
def fig_credit():
    W, H = 920, 430
    s = header(W, H)
    s += text(W / 2, 34, "Чия заслуга: дві команди, жодного одинокого генія", 20, INK, "middle", "bold")
    s += text(W / 2, 55, "за кожною мовою — колектив і ціла попередня традиція опису схем",
              12, GREY, "middle", style="italic")

    cols = [
        ("Програма VHSIC + ВПС США", "замовник і гроші", "поставили задачу: одна мова опису для всіх постачальників", BLUE),
        ("Intermetrics, TI, IBM", "виконавці контракту 1983", "спроєктували VHDL; синтаксис — від Ada, на вимогу DoD", BLUE),
        ("Філ Мурбі (Gateway)", "+ Ґоел, Хуанг", "придумали Verilog і симулятор Verilog-XL — серцем стартапу", RED),
        ("Спільноти й IEEE", "OVI; 1076 та 1364", "відкрили обидві мови та зробили їх стандартами для всіх", GREEN),
    ]
    cw = 200
    gap = (W - 60 - cw * 4) / 3
    y = 92
    for i, (name, role, did, col) in enumerate(cols):
        x = 30 + i * (cw + gap)
        s += rect(x, y, cw, 248, "#fff", col, 2.4, 10)
        s += rect(x, y, cw, 8, col, col, 0, 0)
        # значок: для людей — портрет, для організацій — будівля/документ
        hcx, hcy = x + cw / 2, y + 56
        if i == 2:  # Мурбі — особа
            s += circle(hcx, hcy, 16, "#fff", col, 2.6)
            s += path(f"M{hcx-26},{hcy+44} Q{hcx},{hcy+14} {hcx+26},{hcy+44}", "none", col, 2.6)
        else:       # організації — проста «будівля»
            s += rect(hcx - 24, hcy - 14, 48, 40, "#fff", col, 2.4, 3)
            s += line(hcx - 24, hcy - 14, hcx, hcy - 30, col, 2.4)
            s += line(hcx + 24, hcy - 14, hcx, hcy - 30, col, 2.4)
            s += line(hcx - 10, hcy + 26, hcx - 10, hcy + 4, col, 2)
            s += line(hcx + 10, hcy + 26, hcx + 10, hcy + 4, col, 2)
        s += text(hcx, y + 128, name, 13.5, INK, "middle", "bold")
        yy = y + 150
        for ln in _wrap(role, 26):
            s += text(hcx, yy, ln, 11, GREY, "middle", style="italic")
            yy += 16
        yy += 4
        for ln in _wrap(did, 25):
            s += text(hcx, yy, ln, 11, col, "middle")
            yy += 16
        if i < 3:
            ax = x + cw + gap / 2
            s += arrow(ax - 12, y + 124, ax + 12, y + 124, INK, 2)
    s += text(W / 2, H - 12, "Велике в техніці майже завжди колективне — і тут їх одразу дві колективні історії, що зрослися",
              12, GREY, "middle", style="italic")
    return save("fig-r07-s5i-4-credit.svg", s)


if __name__ == "__main__":
    fig_two_cradles()
    fig_timeline()
    fig_synthesis()
    fig_credit()
    print("r07-s5 history (VHDL/Verilog) figures done.")

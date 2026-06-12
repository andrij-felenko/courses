# -*- coding: utf-8 -*-
"""
SVG-фігури для історичної вставки §3.5.4i — «RISC-V: відкрита ISA з Берклі».
Окремий генератор (головний figs.py не чіпаємо). Чистий Python, без залежностей.
Вивід → ./img/.  Імена: fig-18-4i-k-<slug>.svg.  Підписи у тексті: Рис. 3.5.4i.k.

Стиль (AUTHORING §9): білий фон; стрілки через marker; шрифт sans-serif;
єдиний вигляд із рештою розділу (допоміжні функції — копія з figs.py).
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


# ═══════════ Рис. 3.5.4i.1 — таймлайн: п'ять поколінь Берклі ════════════════
def fig_timeline():
    W, H = 900, 690
    s = header(W, H)
    s += text(W / 2, 36, "П'ять поколінь RISC у Берклі — і вихід ISA у відкритий світ", 21, INK, "middle", "bold")
    s += text(W / 2, 58, "«V» — це і римська П'ЯТІРКА (п'яте покоління), і Vector, і Variations (варіанти-розширення)",
              12.5, GREY, "middle", style="italic")
    spine = 250
    top, bot = 96, H - 24
    s += line(spine, top, spine, bot, GREY, 3)
    nodes = [
        ("1981", "RISC-I, RISC-II", "Паттерсон зі студентами: прості команди — простий і швидкий кремній. Народження ідеї RISC", False),
        ("1984", "SOAR (≈ «RISC-III»)", "Наступний дослідницький чип лабораторії — лінія Берклі триває", False),
        ("1988", "SPUR (≈ «RISC-IV»)", "Четверте покоління; усе це — навчально-дослідні ISA, не для продажу", False),
        ("2010", "RISC-V — старт у Par Lab", "Асанович, Вотерман, Лі (дир. Паттерсон): чиста ISA з нуля, щоб НЕ платити за чужу мову", True),
        ("2011", "перший том специфікації", "Опубліковано опис базового набору — RISC-V виходить за межі однієї лабораторії", False),
        ("2015", "RISC-V Foundation + SiFive", "Стандарт віддали незалежній спільноті; трійця засновує першу RISC-V-компанію", False),
        ("донині", "у мільярдах чипів", "Від крихітних МК (ESP32-C) до серверів — і все на ОДНІЙ відкритій, безплатній ISA", False),
    ]
    n = len(nodes)
    for i, (yr, who, q, hot) in enumerate(nodes):
        y = top + 26 + (bot - top - 52) * i / (n - 1)
        if hot:
            s += circle(spine, y, 11, "#fff", RED, 0)
            s += circle(spine, y, 10, "none", RED, 3.2)
            s += circle(spine, y, 4.5, RED, RED, 1)
        else:
            s += circle(spine, y, 7, "#fff", INK, 2.6)
        s += text(spine - 22, y + 5, yr, 14, (RED if hot else INK), "end", "bold")
        col = RED if hot else INK
        s += text(spine + 24, y - 4, who, 15.5, col, "start", "bold")
        s += text(spine + 24, y + 16, q, 12, GREY, "start")
    return save("fig-18-4i-1-timeline.svg", s)


# ═══════════ Рис. 3.5.4i.2 — закрита ISA проти відкритої ════════════════════
def fig_open_vs_closed():
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 34, "Дві моделі однієї й тієї самої речі — мови процесора (ISA)", 20, INK, "middle", "bold")

    # ліва панель — закрита ISA
    lx, ly, lw, lh = 40, 70, 380, 360
    s += rect(lx, ly, lw, lh, "#fbeceb", RED, 2.4, 10)
    s += text(lx + lw / 2, ly + 30, "ЗАКРИТА (пропрієтарна) ISA", 16, RED, "middle", "bold")
    s += text(lx + lw / 2, ly + 50, "власник тримає мову й бере плату", 12, GREY, "middle", style="italic")
    s += text(lx + 24, ly + 88, "• належить одній фірмі (напр. ARM, x86)", 13, INK)
    s += text(lx + 24, ly + 114, "• щоб робити чипи — купуєш ліцензію", 13, INK)
    s += text(lx + 24, ly + 140, "• роялті: невеликий платіж із кожного", 13, INK)
    s += text(lx + 38, ly + 158, "проданого чипа (перевірити суми)", 12, GREY)
    s += text(lx + 24, ly + 184, "• не можна вільно додати свою команду", 13, INK)
    s += text(lx + 24, ly + 210, "• порядок узгоджуєш із власником мови", 13, INK)
    # замок
    s += rect(lx + lw / 2 - 26, ly + 252, 52, 44, "#fff", RED, 2.6, 6)
    s += path(f"M{lx+lw/2-16},{ly+252} v-14 a16,16 0 0 1 32,0 v14", "none", RED, 2.6)
    s += circle(lx + lw / 2, ly + 274, 6, RED, RED, 1)
    s += text(lx + lw / 2, ly + 326, "вхід — за гроші й дозволом", 12.5, RED, "middle", "bold")

    # права панель — відкрита ISA
    rx, ry = 480, 70
    s += rect(rx, ry, lw, lh, "#eafaee", GREEN, 2.4, 10)
    s += text(rx + lw / 2, ry + 30, "ВІДКРИТА ISA (RISC-V)", 16, GREEN, "middle", "bold")
    s += text(rx + lw / 2, ry + 50, "мова — спільне надбання, без роялті", 12, GREY, "middle", style="italic")
    s += text(rx + 24, ry + 88, "• специфікація вільна (ліцензія BSD-типу)", 13, INK)
    s += text(rx + 24, ry + 114, "• робити чипи може будь-хто — без плати", 13, INK)
    s += text(rx + 24, ry + 140, "• базовий набір «заморожено» — стабільний", 13, INK)
    s += text(rx + 24, ry + 166, "• решта — модульні розширення (M, A, C, F…)", 13, INK)
    s += text(rx + 24, ry + 192, "• стандарт веде незалежна спільнота", 13, INK)
    s += text(rx + 24, ry + 218, "• можна додати власні команди під задачу", 13, INK)
    # відчинений замок
    s += rect(rx + lw / 2 - 26, ry + 252, 52, 44, "#fff", GREEN, 2.6, 6)
    s += path(f"M{rx+lw/2-16},{ry+252} v-14 a16,16 0 0 1 32,0", "none", GREEN, 2.6)
    s += circle(rx + lw / 2, ry + 274, 6, GREEN, GREEN, 1)
    s += text(rx + lw / 2, ry + 326, "вхід вільний для всіх", 12.5, GREEN, "middle", "bold")

    return save("fig-18-4i-2-open-vs-closed.svg", s)


# ═══════════ Рис. 3.5.4i.3 — модульність: ядро + розширення ═════════════════
def fig_modular():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 34, "Чому з однієї ISA виходять і крихітний МК, і сервер: ядро + розширення", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "обов'язкове — лише мала цілочислова основа; усе інше домовляєшся ДОДАВАТИ за потребою",
              12.5, GREY, "middle", style="italic")

    # центральне ядро
    cx, cy, cr = W / 2, 250, 64
    s += circle(cx, cy, cr, "#eef4ff", BLUE, 3)
    s += text(cx, cy - 8, "RV32I", 22, BLUE, "middle", "bold")
    s += text(cx, cy + 14, "базове ядро", 12.5, INK, "middle")
    s += text(cx, cy + 31, "(заморожене)", 11.5, GREY, "middle", style="italic")
    s += text(cx, cy + cr + 26, "≈ 40 цілочислових команд — спільний фундамент УСІХ RISC-V", 12.5, INK, "middle")

    # розширення-пелюстки
    ext = [
        ("M", "множення / ділення", -150, -120),
        ("A", "атомарні (багатоядерні)", 150, -120),
        ("C", "стислі 16-біт команди", -210, 10),
        ("F / D", "числа з комою", 210, 10),
        ("V", "вектори (масиви даних)", -150, 130),
        ("своє", "власні команди під задачу", 150, 130),
    ]
    for label, desc, dx, dy in ext:
        ex, ey = cx + dx, cy + dy
        s += arrow(cx + (dx * 0.34), cy + (dy * 0.34), ex - (dx * 0.16), ey - (dy * 0.16), GREEN, 2, dash="4,3")
        col = GREEN if label != "своє" else AMBER
        s += rect(ex - 64, ey - 22, 128, 44, "#fff", col, 2.4, 8)
        s += text(ex, ey - 2, label, 15, col, "middle", "bold")
        s += text(ex, ey + 16, desc, 11, INK, "middle")
    s += text(W / 2, H - 16, "Бере чип лише те, що йому треба: ESP32-C тягне RV32I + M + C; великий процесор — ще A, F, D, V",
              12, GREY, "middle", style="italic")
    return save("fig-18-4i-3-modular.svg", s)


# ═══════════ Рис. 3.5.4i.4 — чому це змінило ринок МК ══════════════════════
def fig_market():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 34, "Чому відкрита ISA зрушила саме ринок мікроконтролерів", 20, INK, "middle", "bold")

    boxes = [
        ("Нуль роялті", "За саму мову не платять. У копійчаному МК, де кожен цент рахують, зекономлений роялті — це вже перевага в ціні.", BLUE),
        ("Своє ядро без дозволу", "Виробник робить власний RISC-V-процесор сам, не питаючи власника ISA й не чекаючи його умов.", GREEN),
        ("Спільні інструменти", "Один компілятор, один асемблер, одна документація — для чипів різних фірм. Не треба городити власну мову з нуля.", AMBER),
        ("Свобода від геополітики", "Відкритий стандарт важче перекрити санкціями — тому 2020-го його стандарт-орган переїхав у нейтральну Швейцарію.", RED),
    ]
    bw, bh, gap = 410, 132, 24
    x0 = (W - (bw * 2 + gap)) / 2
    y0 = 70
    for i, (title, body, col) in enumerate(boxes):
        bx = x0 + (i % 2) * (bw + gap)
        by = y0 + (i // 2) * (bh + gap)
        s += rect(bx, by, bw, bh, "#fff", col, 2.4, 10)
        s += rect(bx, by, 8, bh, col, col, 0, 0)
        s += text(bx + 26, by + 32, title, 16, col, "start", "bold")
        # перенесення тексту вручну
        words = body.split()
        lines, cur = [], ""
        for wd in words:
            t = (cur + " " + wd).strip()
            if len(t) > 52:
                lines.append(cur)
                cur = wd
            else:
                cur = t
        if cur:
            lines.append(cur)
        for j, ln in enumerate(lines[:4]):
            s += text(bx + 26, by + 58 + j * 19, ln, 12.5, INK, "start")
    return save("fig-18-4i-4-market.svg", s)


# ═══════════ Рис. 3.5.4i.5 — колективна атрибуція ══════════════════════════
def fig_credit():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 34, "RISC-V — праця багатьох рук, а не одне ім'я", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "точна атрибуція: хто заклав ідею RISC, хто зробив саму ISA, хто доніс її до залізного світу",
              12.5, GREY, "middle", style="italic")

    cols = [
        ("Девід Паттерсон", "ідея RISC (1980-ті) + директор Par Lab", "заклав напрям; «дідусь» лінії RISC у Берклі", BLUE),
        ("Крсте Асанович", "очолив проєкт RISC-V (2010)", "повів розробку нової відкритої ISA", GREEN),
        ("Е. Вотерман, Ю. Лі", "автори перших специфікацій", "написали й виточили сам набір команд", GREEN),
        ("Спільнота й SiFive", "Foundation (2015) → Int'l (2020)", "перетворили ISA на світовий стандарт", AMBER),
    ]
    cw = 200
    gap = (W - 60 - cw * 4) / 3
    y = 96
    for i, (name, role, did, col) in enumerate(cols):
        x = 30 + i * (cw + gap)
        s += rect(x, y, cw, 250, "#fff", col, 2.4, 10)
        # портрет
        hcx, hcy = x + cw / 2, y + 52
        s += circle(hcx, hcy, 16, "#ffffff", col, 2.6)
        s += path(f"M{hcx-26},{hcy+44} Q{hcx},{hcy+14} {hcx+26},{hcy+44}", "none", col, 2.6)
        s += text(hcx, y + 132, name, 14, INK, "middle", "bold")
        # роль (сіра, курсив) і внесок (колір) — кожне переноситься на потрібну к-сть рядків
        yy = y + 156
        for ln in _wrap(role, 26):
            s += text(hcx, yy, ln, 11.5, GREY, "middle", style="italic")
            yy += 18
        yy += 4
        for ln in _wrap(did, 26):
            s += text(hcx, yy, ln, 11.5, col, "middle")
            yy += 18
        if i < 3:
            ax = x + cw + gap / 2
            s += arrow(ax - 12, y + 125, ax + 12, y + 125, INK, 2)
    s += text(W / 2, H - 14, "Велике в техніці майже завжди колективне — пам'ять лише зручно чіпляється за одне ім'я",
              12, GREY, "middle", style="italic")
    return save("fig-18-4i-5-credit.svg", s)


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


if __name__ == "__main__":
    fig_timeline()
    fig_open_vs_closed()
    fig_modular()
    fig_market()
    fig_credit()
    print("ch18-s4 history (RISC-V) figures done.")

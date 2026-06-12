# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для історичної вставки до теми 3.10.8 —
«Морріс Чанг і TSMC (1987): фабрика, що працює на всіх» (Модуль 3).

Чистий Python, без сторонніх залежностей. Вивід → ./img/.
Цей скрипт обслуговує ЛИШЕ цю історію; головний figs.py розділу не чіпаємо.

Стиль (AUTHORING §9): білий фон; «1»/«+» червоний, «0»/«−» синій; поле зелене;
стрілки через marker; шрифт sans-serif. Нумерація у підписах — за історією до теми:
Рис. 3.10.8i.k. Імена SVG унікальні: fig-r10-s8h-k-*.svg.
Допоміжні функції — спільні з рештою розділів (копія), щоб вигляд був єдиний.
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
DARKAMBER = "#9a7322"
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
        f'  <marker id="aAmber" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{AMBER}"/></marker>\n'
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", AMBER: "aAmber", GREY: "aGrey", FAINT: "aGrey"}


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


def wedge(cx, cy, r, a0, a1, fill, stroke="#ffffff", sw=2):
    import math
    x0 = cx + r * math.cos(math.radians(a0))
    y0 = cy + r * math.sin(math.radians(a0))
    x1 = cx + r * math.cos(math.radians(a1))
    y1 = cy + r * math.sin(math.radians(a1))
    large = 1 if (a1 - a0) % 360 > 180 else 0
    d = f"M{cx:.1f},{cy:.1f} L{x0:.1f},{y0:.1f} A{r:.1f},{r:.1f} 0 {large} 1 {x1:.1f},{y1:.1f} Z"
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


def caption_box(s, W, lines, y0, col=GREEN, bg="#f4f7f4"):
    """Зелена рамка-висновок унизу фігури з кількома рядками (перший — жирний)."""
    h = 18 + 24 * len(lines)
    s += rect(60, y0, W - 120, h, bg, col, 1.7, 10)
    for i, (t, bold) in enumerate(lines):
        s += text(W / 2, y0 + 26 + i * 24, t,
                  11.5 if bold else 10.5, INK if bold else GREY,
                  "middle", "bold" if bold else "normal",
                  "normal" if bold else "italic")
    return s


# ═══════════════════════════════════════════════════════════════════════════
# Рис. 3.10.8i.1 — Дві бізнес-моделі: IDM «усе сам» vs розрив ланцюга
# ═══════════════════════════════════════════════════════════════════════════

def fig_1_idm_vs_split():
    W, H = 940, 556
    s = header(W, H)
    s += text(W / 2, 34, "Що насправді придумав Чанг: розрізати ланцюг «чипа» навпіл", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "не нову фізику й не нову машину, а нову МЕЖУ фірми — хто проєктує, а хто варить кремній",
              11.5, GREY, "middle", style="italic")

    stages = ["ідея й\nархітектура", "проєкт\nсхеми", "маски", "виробництво\nна пластині",
              "корпус і\nтест", "бренд і\nпродаж"]

    def chain(x0, y0, col, dims):
        out = ""
        bw, gap = 118, 14
        for i, lab in enumerate(stages):
            x = x0 + i * (bw + gap)
            dim = dims[i]
            fill = "#f6f6f6" if dim else "#fafafa"
            bc = FAINT if dim else col
            out += rect(x, y0, bw, 56, fill, bc, 1.6 if not dim else 1.1, 8)
            for j, ln in enumerate(lab.split("\n")):
                out += text(x + bw / 2, y0 + 24 + j * 16, ln, 10,
                            FAINT if dim else INK, "middle", "bold" if not dim else "normal")
            if i < len(stages) - 1:
                ax = x + bw
                out += arrow(ax, y0 + 28, ax + gap, y0 + 28, GREY if not dim else FAINT, 2)
        return out

    # ── IDM: усе своє ──
    s += text(70, 96, "Класична модель IDM (Intel, тоді й TI): одна фірма робить ВСЕ", 13, BLUE, "start", "bold")
    s += rect(54, 108, W - 108, 84, "#f3f5fd", BLUE, 1.8, 10)
    s += chain(70, 122, BLUE, [False] * 6)
    s += text(W / 2, 206, "щоб увійти в гру, треба мільярди на власну фабрику — тож проєктувати чипи можуть лише гіганти",
              10.5, GREY, "middle", style="italic")

    # розділова лінія-ножиці
    s += line(60, 228, W - 60, 228, AMBER, 2, "6 5")
    s += text(W / 2, 246, "✂  розріз Чанга: проєкт окремо, виробництво окремо  ✂", 12.5, DARKAMBER, "middle", "bold")

    # ── Fabless + foundry ──
    s += text(70, 280, "Модель «fabless + foundry»: ланцюг ділять дві різні фірми", 13, GREEN, "start", "bold")
    # верхня половина — fabless проєктує
    s += rect(54, 292, W - 108, 84, "#f4f7f4", GREEN, 1.8, 10)
    s += text(70, 312, "FABLESS — проєктує, але НЕ варить кремнію (своя сила — у схемах)", 11, GREEN, "start", "bold")
    s += chain(70, 320, GREEN, [False, False, False, True, True, False])
    # нижня половина — foundry виробляє
    s += rect(54, 388, W - 108, 84, "#fdf4f4", RED, 1.8, 10)
    s += text(70, 408, "FOUNDRY (TSMC) — лише виробляє чужі проєкти, СВОГО бренду не має", 11, RED, "start", "bold")
    s += chain(70, 416, RED, [True, True, True, False, False, True])

    s = caption_box(s, W, [
        ("Ключ історії — не технологія, а проведена межа. Доти проєктувати чип міг лише той, у кого є фабрика на мільярди.", True),
        ("Чанг віддав фабрику в спільне користування: десятки малих фірм проєктують (fabless), а TSMC варить кремній для всіх і ні з ким не конкурує брендом.", False),
    ], 480)
    save("fig-r10-s8h-1-idm-vs-split.svg", s)


# ═══════════════════════════════════════════════════════════════════════════
# Рис. 3.10.8i.2 — Хто заплатив за TSMC у 1987: уряд + Philips + приватні
# ═══════════════════════════════════════════════════════════════════════════

def fig_2_cap_table():
    W, H = 940, 500
    s = header(W, H)
    s += text(W / 2, 34, "TSMC, 1987: чий насправді був капітал і технологія", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "«фабрика однієї людини» — міф: гроші дали держава й приватні родини, а ключову технологію ліцензував Philips",
              11.5, GREY, "middle", style="italic")

    # ── кругова діаграма часток ──
    cx, cy, r = 250, 250, 120
    # сектори: уряд 48.3, Philips 27.6, приватні ~24.1
    s += wedge(cx, cy, r, -90, -90 + 360 * 0.483, GREEN)
    s += wedge(cx, cy, r, -90 + 360 * 0.483, -90 + 360 * (0.483 + 0.276), BLUE)
    s += wedge(cx, cy, r, -90 + 360 * (0.483 + 0.276), 270, AMBER)
    s += circle(cx, cy, r, "none", "#ffffff", 0)
    # підписи часток
    s += text(cx, cy - 40, "Уряд Тайваню", 13, "#ffffff", "middle", "bold")
    s += text(cx, cy - 22, "(Фонд розвитку)", 10.5, "#eafaef", "middle")
    s += text(cx, cy - 4, "48.3 %", 16, "#ffffff", "middle", "bold")
    s += text(cx + 52, cy + 36, "Philips", 12.5, "#ffffff", "middle", "bold")
    s += text(cx + 52, cy + 52, "27.6 %", 13, "#ffffff", "middle", "bold")
    s += text(cx - 64, cy + 44, "приватні", 11, INK, "middle", "bold")
    s += text(cx - 64, cy + 60, "≈ 24 %", 12, INK, "middle", "bold")

    # ── права колонка: що кожен дав ──
    bx = 470
    rows = [
        (GREEN, "Держава (Фонд розвитку)",
         ["майже половина грошей; промислову політику", "вів прем'єр Сун Юньсюань і радник К. Т. Лі —", "вони ж покликали Чанга очолити ITRI"]),
        (BLUE, "Philips (Нідерланди)",
         ["передача виробничої технології + ліцензії на", "патенти в обмін на частку. Без чужого процесу", "молода фабрика не запустилася б"]),
        (AMBER, "Приватні інвестори Тайваню",
         ["заможні місцеві родини з промисловості —", "решта капіталу; держава наполягла, щоб і свій", "бізнес уклав гроші в ризиковану затію"]),
        (RED, "Морріс Чанг (Morris Chang)",
         ["не гаманець, а задум і досвід: 25 років у TI,", "де подібну ідею «фабрики на всіх» свого часу", "відхилили. Тут її нарешті дали збудувати"]),
    ]
    y = 96
    for col, hd, lines in rows:
        s += rect(bx, y, 420, 86, "#fafafa", col, 1.7, 9)
        s += rect(bx, y, 9, 86, col, col, 0, 0)
        s += text(bx + 22, y + 24, hd, 12.5, col, "start", "bold")
        for j, ln in enumerate(lines):
            s += text(bx + 22, y + 44 + j * 15, ln, 10, INK, "start")
        y += 96

    s = caption_box(s, W, [
        ("За «дивом однієї людини» стоїть колективний пакет: гроші держави, приватний капітал і чужа технологія Philips.",  True),
        ("Внесок Чанга — задум і репутація, а не капітал. Корисний урок: гучний винахід майже завжди спирається на державу, партнера й чийсь готовий процес.", False),
    ], 422)
    save("fig-r10-s8h-2-cap-table.svg", s)


# ═══════════════════════════════════════════════════════════════════════════
# Рис. 3.10.8i.3 — Не «перший, хто робив чужі чипи», а перший НАДІЙНИЙ
# ═══════════════════════════════════════════════════════════════════════════

def fig_3_who_was_first():
    W, H = 940, 510
    s = header(W, H)
    s += text(W / 2, 34, "Чим саме TSMC була «першою»: розводимо два різні твердження", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "«виробляти чужі чипи» вміли й до 1987; новим було робити це як ОСНОВНУ справу — й нікому не конкурувати",
              11.5, GREY, "middle", style="italic")

    # ── ліва колонка: що БУЛО до TSMC ──
    s += text(250, 96, "Що вже існувало до 1987", 13.5, BLUE, "middle", "bold")
    s += rect(60, 110, 380, 250, "#f3f5fd", BLUE, 1.8, 10)
    pre = [
        ("Fujitsu, IBM, NEC, TI, Toshiba",
         "гіганти-IDM іноді варили чужі чипи —", "але як побічну послугу, у вільний час фабрики"),
        ("≈ 50 «fabless»-фірм (сер. 1980-х)",
         "уже проєктували чипи без власної фабрики", "й шукали, де їх замовити"),
        ("Chips & Technologies, 1985",
         "Ґордон Кемпбелл і Дадо Банатао —", "часто звана першою суто fabless-фірмою"),
    ]
    yy = 132
    for hd, l1, l2 in pre:
        s += rect(76, yy, 348, 66, "#fff", BLUE, 1.4, 7)
        s += text(84, yy + 20, hd, 11, INK, "start", "bold")
        s += text(84, yy + 38, l1, 9.5, GREY, "start")
        s += text(84, yy + 53, l2, 9.5, GREY, "start")
        yy += 76
    s += text(250, 350, "проблема: побічна послуга — ненадійна, а IDM ще й конкурент", 9.8, RED, "middle", style="italic")

    # стрілка
    s += arrow(448, 235, 492, 235, AMBER, 2.4)
    s += text(470, 224, "чого", 9, DARKAMBER, "middle", style="italic")
    s += text(470, 252, "бракувало", 9, DARKAMBER, "middle", style="italic")

    # ── права колонка: що додала TSMC ──
    s += text(690, 96, "Що додала TSMC (1987)", 13.5, GREEN, "middle", "bold")
    s += rect(500, 110, 380, 250, "#f4f7f4", GREEN, 1.8, 10)
    add = [
        ("Виробництво — ОСНОВНА справа",
         "не побічний підробіток фабрики, а весь", "сенс фірми: потужність завжди для клієнта"),
        ("«Ми не конкуруємо з клієнтом»",
         "TSMC не має власних чипів-брендів —", "тож клієнт сміливо віддає свій проєкт"),
        ("Спільна фабрика для всіх",
         "одна дорога лінія обслуговує десятки", "малих фірм — кожній порізно було б не під силу"),
    ]
    yy = 132
    for hd, l1, l2 in add:
        s += rect(516, yy, 348, 66, "#fff", GREEN, 1.4, 7)
        s += text(524, yy + 20, hd, 11, INK, "start", "bold")
        s += text(524, yy + 38, l1, 9.5, GREY, "start")
        s += text(524, yy + 53, l2, 9.5, GREY, "start")
        yy += 76
    s += text(690, 350, "результат: проєктувати чипи змогли навіть малі команди", 9.8, GREEN, "middle", style="italic")

    s = caption_box(s, W, [
        ("Точне формулювання: TSMC — не перший, хто виробляв чужі чипи, і не вона придумала fabless. Вона перша зробила виробництво на замовлення",  True),
        ("надійною, головною справою фірми, яка нікому не конкурує. Саме ця обіцянка довіри, а не сам факт «варимо чуже», запустила цілу fabless-індустрію.", False),
    ], 432)
    save("fig-r10-s8h-3-who-was-first.svg", s)


if __name__ == "__main__":
    fig_1_idm_vs_split()
    fig_2_cap_table()
    fig_3_who_was_first()
    print("OK: 3 figures written to", OUT)

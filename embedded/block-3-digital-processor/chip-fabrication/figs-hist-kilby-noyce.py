# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для історичної вставки до Розділу 3.10 —
«Кілбі проти Нойса: хто винайшов інтегральну схему» (Модуль 3).

Чистий Python, без сторонніх залежностей. Вивід → ./img/.
Цей скрипт обслуговує ЛИШЕ цю історію; головний figs.py розділу не чіпаємо.

Стиль (AUTHORING §9): білий фон; «1»/«+» червоний, «0»/«−» синій; поле зелене;
стрілки через marker; шрифт sans-serif. Нумерація у підписах — за історією:
Рис. 3.10.0.k. Імена SVG: fig-3-10-0-k-*.svg.
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


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", AMBER: "aAmber", GREY: "aGrey"}


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
# Рис. 3.10.0.1 — Хронологія: як ідея визрівала й здійснювалася (1957–1966)
# ═══════════════════════════════════════════════════════════════════════════

def fig_1_timeline():
    W, H = 940, 500
    s = header(W, H)
    s += text(W / 2, 34, "Як народилася інтегральна схема: ланцюг подій 1957–1966", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "не один стрибок одного генія, а кілька внесків, що зійшлися — і довгий суд за те, чий же це винахід",
              11.5, GREY, "middle", style="italic")
    # горизонтальна вісь часу
    y = 130
    s += line(80, y, 860, y, GREY, 2)
    for xt, lab in [(110, "1957"), (250, "1958"), (430, "1959"), (640, "1961"), (820, "1966")]:
        s += line(xt, y - 5, xt, y + 5, GREY, 2)
        s += text(xt, y - 12, lab, 11, GREY, "middle", "bold")
    # вузли подій: (x, напрям(+1 вниз/-1 вгору), колір, заголовок, рядки)
    nodes = [
        (110, -1, GREEN, "Грудень 1957", ["Ерні (Hoerni) занотовує", "планарну ідею: лишити", "оксид на поверхні"]),
        (250, +1, BLUE, "Вересень 1958", ["Кілбі (Kilby) у TI: перша", "робоча схема в одному", "шматку — на «вусах»"]),
        (430, -1, RED, "Січень 1959", ["Нойс (Noyce): монолітна", "ІС — плаский метал по", "оксиду Ерні"]),
        (640, +1, AMBER, "1961", ["перші ІС у продажу;", "обидві фірми патентують", "своє → починається суд"]),
        (820, -1, GREEN, "1966", ["мир: TI й Fairchild", "перехресно ліцензують", "патенти одне одному"]),
    ]
    for x, dirn, col, hd, lines in nodes:
        s += circle(x, y, 8, "#fff", col, 3)
        boxh = 16 + 17 * len(lines)
        by = y - 28 - boxh if dirn < 0 else y + 28
        s += line(x, y + (-9 if dirn < 0 else 9), x, by + (boxh if dirn < 0 else 0), col, 1.5, "3 3")
        s += rect(x - 92, by, 184, boxh, "#fafafa", col, 1.7, 8)
        s += text(x, by + 17, hd, 11, col, "middle", "bold")
        for j, ln in enumerate(lines):
            s += text(x, by + 34 + j * 16, ln, 9.3, INK, "middle")
    s = caption_box(s, W, [
        ("Червоний вузол — суть історії: монолітна ІС Нойса (січень 1959), що поклала плаский метал на оксид Ерні.", True),
        ("Але до неї вже були й планарна ідея Ерні (1957), і працююча схема Кілбі (1958). Три внески — одне диво, і довгий суд за авторство.", False),
    ], 420)
    save("fig-3-10-0-1-timeline.svg", s)


# ═══════════════════════════════════════════════════════════════════════════
# Рис. 3.10.0.2 — Три внески, а не «один винахідник»
# ═══════════════════════════════════════════════════════════════════════════

def fig_2_three_contributions():
    W, H = 940, 470
    s = header(W, H)
    s += text(W / 2, 34, "Три різні внески — три різні люди (і всі необхідні)", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "«придумати фундамент», «зробити перший зразок» і «зробити так, щоб це масово виготовлялося» — це три різні справи",
              11.5, GREY, "middle", style="italic")
    cards = [
        (GREEN, "Жан Ерні", "(Jean Hoerni)", "ФУНДАМЕНТ",
         ["планарний процес (1957–59):", "оксид лишають на пластині —", "він і захищає переходи,", "і служить ізолятором під метал.", "без нього монолітної ІС нема"]),
        (BLUE, "Джек Кілбі", "(Jack Kilby)", "ПЕРШИЙ ЗРАЗОК",
         ["перша працююча ІС (1958):", "усі деталі в одному шматку", "напівпровідника. Але з'єднані", "тонкими дротиками-«вусами» —", "так серійно не зробиш"]),
        (RED, "Роберт Нойс", "(Robert Noyce)", "СПОСІБ ВИРОБЛЯТИ",
         ["монолітна ІС (1959): метал", "напиляний просто по оксиду", "Ерні замість дротиків.", "Саме цю форму й можна", "друкувати тисячами"]),
    ]
    for i, (col, name, en, role, lines) in enumerate(cards):
        x = 50 + i * 295
        s += rect(x, 86, 270, 300, "#fafafa", col, 2, 12)
        s += text(x + 135, 116, name, 16, col, "middle", "bold")
        s += text(x + 135, 136, en, 11, GREY, "middle", style="italic")
        s += rect(x + 55, 150, 160, 26, "#fff", col, 1.6, 6)
        s += text(x + 135, 168, role, 11.5, col, "middle", "bold")
        for j, ln in enumerate(lines):
            s += text(x + 18, 200 + j * 22, ln, 10, INK, "start")
    # стрілки залежності між картками
    s += arrow(322, 236, 343, 236, GREY, 2)
    s += arrow(617, 236, 638, 236, GREY, 2)
    s += text(332, 224, "+", 16, GREY, "middle", "bold")
    s += text(627, 224, "+", 16, GREY, "middle", "bold")
    s = caption_box(s, W, [
        ("Підручник любить одне ім'я, та насправді ІС стоїть на трьох внесках: основа (Ерні) + перший зразок (Кілбі) + придатна до серії форма (Нойс).", True),
        ("Прибери будь-який — і дива не буде: без планарного оксиду нема куди класти метал, без метала зразок не серійний, без зразка немає що серіїти.", False),
    ], 404)
    save("fig-3-10-0-2-three-contributions.svg", s)


# ═══════════════════════════════════════════════════════════════════════════
# Рис. 3.10.0.3 — «Вуса» Кілбі проти плаского метала Нойса
# ═══════════════════════════════════════════════════════════════════════════

def fig_3_wires_vs_planar():
    W, H = 940, 480
    s = header(W, H)
    s += text(W / 2, 34, "Чому зразка Кілбі було замало: дротики проти друкованого метала", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "обидва склали схему в одному шматку — різниця в тому, ЯК з'єднані деталі, і саме вона вирішила, що піде в серію",
              11.5, GREY, "middle", style="italic")

    # ── ЛІВОРУЧ: гібрид Кілбі з навісними дротиками ──
    s += text(245, 92, "Кілбі, 1958: «вуса» вручну", 13, BLUE, "middle", "bold")
    s += rect(80, 110, 330, 150, "#f3f5fd", BLUE, 1.8, 10)
    # підкладка
    s += rect(110, 210, 270, 30, "#e7ecf7", BLUE, 1.4, 3)
    s += text(245, 230, "шматок германію", 9.5, GREY, "middle")
    # «острівці» деталей
    comp = [(150, "T"), (215, "R"), (280, "C"), (340, "T")]
    for cx, lab in comp:
        s += rect(cx - 16, 178, 32, 26, "#fff", BLUE, 1.5, 3)
        s += text(cx, 196, lab, 10, INK, "middle", "bold")
    # навісні золоті дротики (дуги зверху)
    for (x1, _), (x2, _) in zip(comp[:-1], comp[1:]):
        midx = (x1 + x2) / 2
        s += path(f"M{x1},178 Q{midx},130 {x2},178", "none", AMBER, 2.2)
    s += text(245, 126, "тонкі золоті дротики, припаяні поодинці", 9.5, DARKAMBER, "middle", "bold")
    s += rect(95, 272, 300, 70, "#fff", RED, 1.6, 8)
    s += text(245, 292, "Граблі серії:", 10.5, RED, "middle", "bold")
    for j, ln in enumerate([
        "кожен «вус» садить людина під мікроскопом —",
        "повільно, ламко, тисячами штук не зробиш",
    ]):
        s += text(245, 310 + j * 17, ln, 9.8, INK, "middle")

    # ── ПРАВОРУЧ: монолітна ІС Нойса, плаский метал ──
    s += text(695, 92, "Нойс, 1959: метал по оксиду", 13, RED, "middle", "bold")
    s += rect(530, 110, 330, 150, "#fdf4f4", RED, 1.8, 10)
    # шари: кремній → оксид → метал
    s += rect(560, 210, 270, 30, "#eef7ee", GREEN, 1.4, 3)
    s += text(695, 230, "кремній з переходами", 9.5, GREY, "middle")
    # оксидний шар (тонка зелена смуга) із вікнами
    s += rect(560, 196, 270, 12, "#dff0df", GREEN, 1.2, 2)
    s += text(845, 204, "", 8, GREEN, "end")
    s += text(695, 252, "оксид Ерні — суцільний ізолятор зверху", 9, GREEN, "middle", "bold")
    # плаский напилений метал (червоні доріжки по поверхні)
    s += polyline([(585, 184), (640, 184), (640, 196)], RED, 2.4)
    s += polyline([(700, 184), (760, 184), (760, 196)], RED, 2.4)
    s += line(640, 184, 700, 184, RED, 2.4)
    s += line(760, 184, 815, 184, RED, 2.4)
    for vx in (585, 815):
        s += line(vx, 184, vx, 196, RED, 2.4)
    s += text(695, 134, "доріжки алюмінію надруковані разом з усім чипом", 9.5, RED, "middle", "bold")
    s += rect(545, 272, 300, 70, "#fff", GREEN, 1.6, 8)
    s += text(695, 292, "Чому це перемогло:", 10.5, GREEN, "middle", "bold")
    for j, ln in enumerate([
        "з'єднання наносять світлом і хімією — за раз,",
        "на цілу пластину; жодного ручного паяння",
    ]):
        s += text(695, 310 + j * 17, ln, 9.8, INK, "middle")

    s += arrow(415, 185, 525, 185, INK, 2.2)
    s += text(470, 176, "та сама", 9, GREY, "middle", style="italic")
    s += text(470, 200, "ідея, інше", 9, GREY, "middle", style="italic")
    s = caption_box(s, W, [
        ("Кілбі довів, що цілу схему можна вмістити в один кристал — але з'єднав деталі навісними дротиками, і серійно це не виходило.", True),
        ("Нойс прибрав дротики: метал друкують просто по оксиду Ерні, разом з рештою чипа. Ось чому масова ІС виросла саме з планарного процесу.", False),
    ], 404)
    save("fig-3-10-0-3-wires-vs-planar.svg", s)


# ═══════════════════════════════════════════════════════════════════════════
# Рис. 3.10.0.4 — «Єресь» Ерні: оксид лишають на місці
# ═══════════════════════════════════════════════════════════════════════════

def fig_4_hoerni_oxide():
    W, H = 940, 500
    s = header(W, H)
    s += text(W / 2, 34, "Здогад Ерні, в який не вірили: не змивати оксид, а лишити його", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "усі змивали захисний оксид після травлення, оголюючи переходи; Ерні лишив його — і той став і бронею, і ізолятором",
              11.5, GREY, "middle", style="italic")

    def silicon(x0, y0, w):
        out = rect(x0, y0, w, 64, "#eef7ee", GREEN, 1.6, 4)
        out += text(x0 + w / 2, y0 + 38, "кремній", 10, GREY, "middle")
        return out

    # ── ЛІВОРУЧ: «меза», оксид змито, перехід оголений ──
    lx = 110
    s += text(lx + 150, 96, "Старий шлях («меза»): оксид змили", 12.5, BLUE, "middle", "bold")
    s += silicon(lx, 150, 300)
    # припіднята «гора» транзистора
    s += path(f"M{lx+110},150 L{lx+130},112 L{lx+190},112 L{lx+210},150 Z", "#e7ecf7", BLUE, 1.6)
    s += text(lx + 160, 132, "транзистор", 9, INK, "middle", "bold")
    # лінія переходу, що виходить НА ПОВЕРХНЮ збоку
    s += line(lx + 130, 150, lx + 130, 112, RED, 2.4)
    s += line(lx + 190, 150, lx + 190, 112, RED, 2.4)
    s += circle(lx + 130, 131, 7, "none", RED, 2.2)
    s += circle(lx + 190, 131, 7, "none", RED, 2.2)
    s += text(lx + 150, 235, "перехід виходить на голу поверхню", 9.5, RED, "middle", "bold")
    s += rect(lx + 10, 250, 280, 64, "#fff", RED, 1.6, 8)
    for j, ln in enumerate([
        "Голий перехід беззахисний: бруд, волога, заряди",
        "на поверхні псують його — транзистор «пливе»",
        "за параметрами й ненадійний. І метал класти ніяк.",
    ]):
        s += text(lx + 150, 270 + j * 16, ln, 9.5, INK, "middle")

    # ── ПРАВОРУЧ: планар, оксид на місці ──
    rx = 540
    s += text(rx + 150, 96, "Планар Ерні: оксид залишено", 12.5, GREEN, "middle", "bold")
    s += silicon(rx, 150, 300)
    # суцільний оксидний шар поверх
    s += rect(rx, 138, 300, 14, "#dff0df", GREEN, 1.4, 2)
    s += text(rx + 150, 120, "суцільний шар оксиду (SiO₂)", 9.5, GREEN, "middle", "bold")
    # перехід тепер закінчується ПІД оксидом (плаский, втоплений)
    s += line(rx + 110, 150, rx + 110, 178, RED, 2.4)
    s += line(rx + 190, 150, rx + 190, 178, RED, 2.4)
    s += line(rx + 110, 178, rx + 190, 178, RED, 2.4, "3 3")
    s += text(rx + 150, 200, "перехід захований під оксидом", 9.5, GREEN, "middle", "bold")
    # вікно в оксиді + доріжка метала
    s += line(rx + 60, 145, rx + 95, 145, INK, 3)
    s += line(rx + 205, 145, rx + 245, 145, INK, 3)
    s += text(rx + 150, 138, "↑ у вікнах кладуть метал ↑", 8.5, INK, "middle", "bold")
    s += rect(rx + 10, 250, 280, 64, "#fff", GREEN, 1.6, 8)
    for j, ln in enumerate([
        "Оксид робить ДВІ справи разом: захищає перехід",
        "(надійність, стабільність) — і служить ізолятором,",
        "по якому можна вести металеві доріжки. Звідси ІС.",
    ]):
        s += text(rx + 150, 270 + j * 16, ln, 9.5, INK, "middle")

    s += arrow(415, 180, 535, 180, INK, 2.2)
    s += text(475, 172, "одна зміна", 9, GREY, "middle", style="italic")
    s = caption_box(s, W, [
        ("Уся хитрість — у тому, чого Ерні НЕ зробив: не змив оксид. Той самий шар, що всі вважали сміттям, виявився і бронею для переходу,", True),
        ("і рівною ізоляційною підлогою для металевих з'єднань. Саме на цю «підлогу» Нойс і поклав доріжки своєї монолітної ІС.", False),
    ], 424)
    save("fig-3-10-0-4-hoerni-oxide.svg", s)


# ═══════════════════════════════════════════════════════════════════════════
# Рис. 3.10.0.5 — Як вужчала й ширшала атрибуція винаходу
# ═══════════════════════════════════════════════════════════════════════════

def fig_5_attribution_history():
    W, H = 940, 470
    s = header(W, H)
    s += text(W / 2, 34, "Хто винайшов ІС: як сама ВІДПОВІДЬ мінялася з десятиліттями", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "наочний приклад, як історія техніки спершу спрощує колективний винахід до зручної легенди, а потім відновлює правду",
              11.5, GREY, "middle", style="italic")
    cols = [
        ("1960-ті", "називали ЧОТИРЬОХ",
         ["Кілбі (Kilby)", "Леговець (Lehovec)", "Нойс (Noyce)", "Ерні (Hoerni)"],
         GREEN, [True, True, True, True]),
        ("1970–90-ті", "звузили до ДВОХ",
         ["Кілбі (Kilby)", "—", "Нойс (Noyce)", "—"],
         RED, [True, False, True, False]),
        ("2000-ні →", "історики відновлюють",
         ["Кілбі (Kilby)", "Леговець (Lehovec)", "Нойс (Noyce)", "Ерні (Hoerni)"],
         GREEN, [True, True, True, True]),
    ]
    names_full = ["Кілбі", "Леговець", "Нойс", "Ерні"]
    for i, (era, sub, names, col, on) in enumerate(cols):
        x = 60 + i * 290
        s += rect(x, 88, 265, 270, "#fafafa", col, 2, 12)
        s += text(x + 132, 116, era, 14.5, col, "middle", "bold")
        s += text(x + 132, 138, sub, 11, GREY, "middle", style="italic")
        s += line(x + 20, 150, x + 245, 150, FAINT, 1.4)
        for j in range(4):
            yy = 172 + j * 42
            shown = on[j]
            c = INK if shown else FAINT
            bg = "#fff" if shown else "#f6f6f6"
            bc = col if shown else FAINT
            s += rect(x + 30, yy, 205, 32, bg, bc, 1.5 if shown else 1.1, 6)
            label = names[j] if shown else f"({names_full[j]} — забуто)"
            s += text(x + 132, yy + 21, label, 10.5 if shown else 9.5,
                      c, "middle", "bold" if shown else "normal",
                      "normal" if shown else "italic")
        if i == 1:
            s += text(x + 132, 348, "зручно, та неправдиво", 9.5, RED, "middle", "bold")
        if i == 2:
            s += text(x + 132, 348, "Берлін, Лоєк та ін.", 9.5, GREEN, "middle", "bold")
    # стрілки переходу
    s += arrow(326, 220, 348, 220, GREY, 2.2)
    s += arrow(616, 220, 638, 220, GREY, 2.2)
    s += text(337, 208, "↓2", 11, RED, "middle", "bold")
    s += text(627, 208, "+2", 11, GREEN, "middle", "bold")
    s = caption_box(s, W, [
        ("Спочатку винахід чесно ділили на кількох; потім переказ для зручності стиснув його до «Кілбі й Нойс», викинувши Ерні й Леговця.",  True),
        ("Сучасні історики (Леслі Берлін, Бо Лоєк) повернули імена назад. Урок: коли підручник називає одного «винахідника» — питай, кого забули.", False),
    ], 392)
    save("fig-3-10-0-5-attribution-history.svg", s)


if __name__ == "__main__":
    fig_1_timeline()
    fig_2_three_contributions()
    fig_3_wires_vs_planar()
    fig_4_hoerni_oxide()
    fig_5_attribution_history()
    print("OK: 5 figures written to", OUT)

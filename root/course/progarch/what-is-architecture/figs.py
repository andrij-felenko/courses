# -*- coding: utf-8 -*-
"""Фігури для кроку «Архітектура» (guide progarch / mindset).
Вивід — ./img/*.svg. svgkit імпортуємо, не переписуємо."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_spectrum():
    """Континуум вартості зміни: ті самі за формою рішення коштують по-різному
    відкотити. Ліворуч — дешеві (деталь), праворуч — дорогі (архітектура).
    Три зони — не жорсткі відсіки, а ділянки одного спектра."""
    W, H = 900, 470
    ax_y = 250
    x0, x1 = 80, 820
    els = []
    els.append(text(W / 2, 34, "Архітектура — це дорогий у відкоті кінець спектра рішень",
                    size=16, bold=True))

    # --- фонові зони (малюємо першими, під усім) ---
    bands = [
        (80, 320, "#eef2fb"),   # деталь
        (320, 540, "#f4f6f8"),  # дизайн
        (540, 820, "#eafaf0"),  # архітектура
    ]
    for bx0, bx1, tone in bands:
        els.append(rect(bx0, 62, bx1 - bx0, 366, fill=tone, stroke="none", sw=0, rx=0))
    # заголовки зон — над смугами
    els.append(text(200, 52, "ДЕТАЛЬ РЕАЛІЗАЦІЇ", size=13, bold=True, color=NEG))
    els.append(text(430, 52, "ДИЗАЙН", size=13, bold=True, color=MUTED))
    els.append(text(680, 52, "АРХІТЕКТУРА", size=14, bold=True, color=FIELD))

    # --- вісь зі стрілкою ---
    els.append(line(x0, ax_y, x1, ax_y, color=INK, sw=2))
    els.append(arrow(x1 - 6, ax_y, x1 + 10, ax_y, color=INK, sw=2))

    # --- приклади рішень уздовж осі, поперемінно вгору/вниз ---
    ticks = [
        (150, "below", "назва змінної"),
        (250, "above", "локальний алгоритм"),
        (400, "below", "межа модуля"),
        (560, "above", "публічний контракт API"),
        (670, "below", "формат даних на диску"),
        (770, "above", "межі процесів і сервісів"),
    ]
    for x, side, label in ticks:
        els.append(circle(x, ax_y, 5, fill=BG, stroke=INK, sw=1.8))
        cy = 160 if side == "above" else 330
        col = NEG if x < 320 else (MUTED if x < 540 else FIELD)
        b, bw, bh = textbox(x, cy, label, size=12.5, color=INK,
                            stroke=col, fill=BG, sw=1.4, pad=9)
        # конектор від осі до краю рамки — поза написом
        edge = cy + bh / 2 if side == "above" else cy - bh / 2
        els.append(line(x, ax_y, x, edge, color=col, sw=1.2, dash="4,3"))
        els.append(b)

    # висновок під архітектурною зоною і напрям осі
    els.append(text(680, 415, "= рішення, які дорого відкотити", size=12,
                    italic=True, color=FIELD))
    els.append(text(W / 2, 456, "що правіше — то більше довелося б переписати, "
                    "щоб вирішити інакше", size=12, color=MUTED))
    render(os.path.join(IMG, "spectrum.svg"), W, H, *els)


def fig_dh_decisions():
    """DH v0: той самий крихітний скрипт, але його рішення не рівні за ціною
    відкоту. Ліва панель — дешеві (деталь), права — дорогі (архітектура)."""
    W, H = 820, 470
    els = []
    els.append(text(W / 2, 34, "Ті самі двадцять рядків — але рішення в них не рівні",
                    size=16, bold=True))

    # --- конвеєр: датчик → хаб → реле ---
    els.append(rect(90, 98, 120, 48, fill=FILL, stroke=LINE, sw=1.5))
    els.append(text(150, 127, "датчик t°", size=13, color=INK))
    els.append(rect(330, 88, 160, 68, fill="#fff7e6", stroke="#b8860b", sw=2))
    els.append(mtext(410, 116, "хаб-скрипт\n(один процес)", size=13, color=INK, lh=1.3))
    els.append(rect(610, 98, 120, 48, fill=FILL, stroke=LINE, sw=1.5))
    els.append(text(670, 127, "реле обігрівача", size=12, color=INK))
    els.append(arrow(214, 122, 326, 122, color=INK, sw=1.8))
    els.append(arrow(494, 122, 606, 122, color=INK, sw=1.8))

    # --- дві панелі рішень ---
    P_top, P_h = 196, 244
    # ліва: дешеві
    els.append(rect(64, P_top, 344, P_h, fill="#eef2fb", stroke=NEG, sw=1.6))
    els.append(text(236, P_top + 30, "дешево змінити — деталь", size=14, bold=True, color=NEG))
    els.append(mtext(90, P_top + 66,
                     "•  поріг спрацювання: 25 °C\n"
                     "•  період опитування: 2 с\n"
                     "•  назви змінних, стиль коду\n"
                     "•  текст повідомлення в журналі",
                     size=13.5, color=INK, anchor="start", lh=1.55))
    els.append(mtext(90, P_top + 196,
                     "правиш за хвилину —\nніхто інший не зачеплений",
                     size=12, color=MUTED, anchor="start", lh=1.35))
    # права: дорогі
    els.append(rect(412, P_top, 344, P_h, fill="#fdecea", stroke=POS, sw=1.6))
    els.append(text(584, P_top + 30, "дорого змінити — архітектура", size=14, bold=True, color=POS))
    els.append(mtext(438, P_top + 66,
                     "•  усе в одному процесі\n"
                     "•  стан лише у файлі на диску\n"
                     "•  формат даних на диску\n"
                     "•  нема межі «пристрій ↔ хмара»",
                     size=13.5, color=INK, anchor="start", lh=1.55))
    els.append(mtext(438, P_top + 196,
                     "зміниш пізніше — переписуєш\nі мігруєш геть усе",
                     size=12, color=MUTED, anchor="start", lh=1.35))
    render(os.path.join(IMG, "dh-decisions.svg"), W, H, *els)


def fig_mud_lineage():
    """Родовід терміна «велика грудка болота»: від жарту про Lisp (спірне
    походження) через іллінойську групу й Маріка до роботи Фута й Йодера
    на PLoP '97 і книжки 2000-го. Штрихове/сіре — недоведене."""
    W, H = 1040, 300
    ax_y = 150
    els = []
    els.append(text(W / 2, 32, "Родовід терміна «велика грудка болота»",
                    size=17, bold=True))
    els.append(text(W / 2, 54, "сіре й штрихове — походження не доведене; "
                    "кольорове й суцільне — задокументовані події",
                    size=12, italic=True, color=MUTED))

    # вісь часу
    els.append(line(50, ax_y, 985, ax_y, color=INK, sw=2))
    els.append(arrow(985, ax_y, 1002, ax_y, color=INK, sw=2))

    nodes = [
        (150, "1970-ті", MUTED, True,
         ["MIT: мову Lisp", "жартома звуть", "«грудкою болота»",
          "(хто перший — спірно)"]),
        (400, "початок 1990-х", NEG, False,
         ["Група архітектури ПЗ,", "Університет Іллінойсу:",
          "Браян Марік дає назву", "цілому класу систем"]),
        (650, "вересень 1997", FIELD, False,
         ["PLoP '97, Монтічелло:", "Фут і Йодер", "представляють",
          "однойменну роботу"]),
        (900, "2000", INK, False,
         ["Розділ 29 у «Pattern", "Languages of Program", "Design 4»",
          "— стає класикою"]),
    ]
    bw, bh, btop = 220, 96, 172
    for x, year, col, dashed, lines in nodes:
        els.append(text(x, 118, year, size=13, bold=True, color=col))
        els.append(circle(x, ax_y, 7, fill=BG, stroke=col, sw=2.2))
        els.append(line(x, ax_y + 7, x, btop, color=col, sw=1.4,
                        dash="4,3" if dashed else None))
        els.append(fitbox(x - bw / 2, btop, bw, bh, "\n".join(lines),
                          size=12.5, fill=BG, stroke=col, sw=1.6, color=INK))
    render(os.path.join(IMG, "mud-lineage.svg"), W, H, *els)


def fig_definition_timeline():
    """Дрейф означення «архітектури»: від структурного «поділу системи на частини»
    (IEEE/RUP, PoEAA) до означення через вартість зміни (Джонсон, Фаулер, Буч).
    Колір вузлів зсувається від холодного (структура) до зеленого (вартість зміни)."""
    W, H = 960, 650
    els = []
    els.append(text(W / 2, 34, "Дрейф означення: від «поділу системи на частини» до «вартості зміни»",
                    size=16, bold=True))

    sx = 205                       # вертикальна стрічка часу
    y_top, y_bot = 96, 584
    els.append(line(sx, y_top, sx, y_bot, color=MUTED, sw=2.5))
    els.append(arrow(sx, y_bot, sx, y_bot + 20, color=MUTED, sw=2.5))

    # два полюси (поза рядами віх)
    els.append(text(120, 86, "СТРУКТУРА", size=11.5, bold=True, color=NEG))
    els.append(text(120, 622, "ВАРТІСТЬ ЗМІНИ", size=11.5, bold=True, color=FIELD))

    box_cx = 610
    milestones = [
        (128, "≈2000", "IEEE 1471 · RUP",
         "структура: поділ на значущі\nкомпоненти та їх інтерфейси", NEG),
        (232, "2002", "Фаулер · PoEAA",
         "три означення поруч; серед них —\n«рішення, які важко змінити»", MUTED),
        (350, "2003", "Ральф Джонсон · список XP",
         "«архітектура — про важливі речі.\nХай там які вони»", FIELD),
        (458, "2003", "Фаулер · «Who Needs an Architect?»",
         "«те, що вважають\nважким для зміни»", FIELD),
        (562, "2006", "Ґрейді Буч · «On design»",
         "«значущість міряють\nвартістю зміни»", FIELD),
    ]
    for y, year, who, what, col in milestones:
        els.append(circle(sx, y, 7, fill=BG, stroke=col, sw=2.4))
        els.append(text(120, y + 4, year, size=13, bold=True, color=col))
        b, bw, bh = textbox(box_cx, y, who + "\n" + what, size=12.5,
                            color=INK, stroke=col, fill=BG, sw=1.5, pad=10)
        els.append(line(sx + 7, y, box_cx - bw / 2, y, color=col, sw=1.2, dash="4,3"))
        els.append(b)
    render(os.path.join(IMG, "definition-timeline.svg"), W, H, *els)


def fig_removing_architecture():
    """«Позбутися архітектури» (Фаулер, 2003): те саме рішення — схема БД —
    перестає бути архітектурним, коли хтось здешевлює його зміну (еволюційні
    міграції Прамода Садалиджа). Отже архітектура — не список тем, а погляд."""
    W, H = 900, 380
    els = []
    els.append(text(W / 2, 34, "Здешеви зміну — і рішення покидає «архітектуру»",
                    size=16, bold=True))

    y = 196
    lb, lw, lh = textbox(175, y, "схема бази даних\nважко змінити", size=13.5,
                         color=INK, stroke=POS, fill="#fdecea", sw=1.8, pad=12)
    rb, rw, rh = textbox(725, y, "схема бази даних\nлегко змінити", size=13.5,
                         color=INK, stroke=FIELD, fill="#eafaf0", sw=1.8, pad=12)

    # втручання — над стрілкою, у проміжку між рамками
    els.append(mtext(450, 112, "еволюційні міграції схеми\n(Прамод Садалаге):\nзміна стає дешевою",
                     size=12.5, color=INK, lh=1.35))
    els.append(arrow(175 + lw / 2, y, 725 - rw / 2, y, color=INK, sw=2))
    els.append(lb)
    els.append(rb)
    els.append(text(175, y + lh / 2 + 26, "⇒ архітектурне рішення", size=12.5,
                    bold=True, color=POS))
    els.append(text(725, y + rh / 2 + 26, "⇒ вже не архітектурне", size=12.5,
                    bold=True, color=FIELD))

    els.append(text(W / 2, 350,
                    "вартість зміни — не властивість теми: її можна знизити, і тема покидає архітектуру",
                    size=11.5, italic=True, color=MUTED))
    render(os.path.join(IMG, "removing-architecture.svg"), W, H, *els)


if __name__ == "__main__":
    fig_spectrum()
    fig_dh_decisions()
    fig_mud_lineage()
    fig_definition_timeline()
    fig_removing_architecture()
    print("OK: figures written to", IMG)

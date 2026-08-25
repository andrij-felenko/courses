# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE  = "#eef4ff"
GREEN = "#eaf7ef"
AMBER = "#fff6e6"
GREY  = "#f2f2f5"
RED   = "#fdecea"


def box3(cx, cy, w, h, title, l2=None, l3=None, fill=FILL):
    """Рамка з 1–3 центрованими рядками (заголовок + до двох підписів)."""
    x, y = cx - w / 2, cy - h / 2
    out = rect(x, y, w, h, fill=fill, stroke=INK, sw=1.8, rx=9)
    if l2 is None and l3 is None:
        out += text(cx, cy + 5, title, size=15, bold=True)
    elif l3 is None:
        out += text(cx, cy - 5, title, size=15, bold=True)
        out += text(cx, cy + 16, l2, size=11.5, color=MUTED)
    else:
        out += text(cx, cy - 14, title, size=15, bold=True)
        out += text(cx, cy + 6, l2, size=11.5, color=MUTED)
        out += text(cx, cy + 24, l3, size=11.5, color=MUTED)
    return out


def dashed_arrow(x1, y1, x2, y2, color=LINE, sw=2.0):
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
            'stroke-width="%.1f" stroke-dasharray="7 5" '
            'marker-end="url(#arrow)"/>' % (x1, y1, x2, y2, color, sw))


def biarrow(x1, y1, x2, y2, color=LINE, sw=1.9):
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
            'stroke-width="%.1f" marker-start="url(#arrow)" '
            'marker-end="url(#arrow)"/>' % (x1, y1, x2, y2, color, sw))


def arc(x1, y1, x2, y2, ctrl_y, color=LINE, sw=2.0, dash=False, head=True):
    cx = (x1 + x2) / 2
    d = ' stroke-dasharray="7 5"' if dash else ''
    m = ' marker-end="url(#arrow)"' if head else ''
    return ('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" '
            'stroke="%s" stroke-width="%.1f"%s%s/>'
            % (x1, y1, cx, ctrl_y, x2, y2, color, sw, d, m))


# ── Фігура 1: MVP — презентер як єдиний посередник ───────────────────────────
def fig_mediator():
    W, H = 920, 420
    f = []

    # три рамки в ряд
    f.append(box3(160, 265, 175, 86, "Подання",
                  "пасивне: показує,", "що звелено", fill=GREEN))
    f.append(box3(455, 265, 205, 92, "Презентер",
                  "єдиний посередник", "читає модель, керує екраном", fill=BLUE))
    f.append(box3(760, 265, 175, 86, "Модель",
                  "дані + правило", "не знає про екран", fill=AMBER))

    # подання ⇄ презентер: два боки діалогу
    f.append(arrow(247.5, 250, 352.5, 250))
    f.append(text(300, 236, "мене торкнули", size=12))
    f.append(('<line x1="352.5" y1="288" x2="247.5" y2="288" stroke="%s" '
              'stroke-width="1.8" marker-end="url(#arrow)"/>' % MUTED))
    f.append(text(300, 305, "показую X", size=12, color=MUTED))

    # презентер ⇄ модель: читає й змінює
    f.append(biarrow(557.5, 265, 672.5, 265))
    f.append(text(615, 250, "читає й змінює", size=12))

    # відрізаний прямий зв'язок подання↔модель
    f.append(arc(160, 222, 760, 222, 66, color=MUTED, sw=1.8, dash=True, head=False))
    cx = 460
    f.append(line(cx - 10, 136, cx + 10, 152, color=POS, sw=3.2))
    f.append(line(cx + 10, 136, cx - 10, 152, color=POS, sw=3.2))
    f.append(text(cx, 122, "прямого зв'язку нема — подання не бачить моделі",
                  size=12, anchor="middle"))

    render(os.path.join(IMG, 'presenter-mediator.svg'), W, H, *f,
           title="MVP: презентер — єдиний посередник між екраном і даними")


# ── Фігура 2: пасивне подання за інтерфейсом — справжнє й фальшиве ────────────
def fig_fake_view():
    W, H = 940, 545
    f = []

    # презентер угорі
    f.append(box3(470, 90, 300, 66, "Презентер",
                  "однаково працює з будь-яким поданням", fill=BLUE))

    # інтерфейс подання — контракт екрана (пунктирна рамка = абстракція)
    ix, iy, iw, ih = 470 - 160, 225 - 60, 320, 120
    f.append(rect(ix, iy, iw, ih, fill=GREEN, stroke=INK, sw=1.8, rx=9))
    f.append(text(470, 190, "Подання — інтерфейс екрана", size=13.5, bold=True))
    f.append(line(340, 202, 600, 202, color=MUTED, sw=1.0))
    f.append(mtext(470, 222, ["showTemperature(text)", "showColor(hex)", "onNudge(handler)"],
                   size=12.5, color=INK, lh=1.5))

    # презентер → інтерфейс
    f.append(arrow(470, 123, 470, 163))
    f.append(text(486, 147, "керує через інтерфейс", size=12, anchor="start"))

    # дві реалізації того самого інтерфейсу
    f.append(box3(245, 432, 250, 96, "Справжнє подання",
                  "малює на віджетах", "(у застосунку)", fill=GREEN))
    f.append(box3(695, 432, 250, 96, "Фальшиве подання",
                  "запам'ятовує виклики", "(у тесті)", fill=RED))

    # інтерфейс → реалізації (пунктир «реалізує»)
    f.append(dashed_arrow(470, 285, 258, 384, color=MUTED, sw=1.9))
    f.append(dashed_arrow(470, 285, 682, 384, color=MUTED, sw=1.9))
    f.append(text(330, 322, "реалізує", size=11.5, color=MUTED))
    f.append(text(610, 322, "реалізує", size=11.5, color=MUTED))

    # підсумок унизу
    f.append(text(470, 505, "Той самий інтерфейс — презентер не бачить різниці між ними.",
                  size=12, color=INK, anchor="middle"))
    f.append(text(470, 526, "У тесті «натискаємо +» і звіряємо, що подання почуло «23°» — без жодного віджета.",
                  size=11.5, color=MUTED, anchor="middle"))

    render(os.path.join(IMG, 'fake-view-test.svg'), W, H, *f,
           title="Пасивне подання за інтерфейсом: справжнє в застосунку, фальшиве в тесті")


# ── Фігура 3 (вставка hist): дорога назви MVP у часі ─────────────────────────
def fig_timeline():
    W, H = 1240, 300
    f = []

    events = [
        ("1988", ["рожеві картки в Apple:", "начерк системи-мрії"]),
        ("1992", ["Taligent — спільне", "підприємство Apple та IBM"]),
        ("1995", ["CommonPoint виходить —", "і не знаходить покупця"]),
        ("1996", ["стаття Потела:", "ім'я MVP закріплено"]),
        ("1998", ["Taligent розчинено", "в IBM"]),
        ("2000", ["Dolphin Smalltalk:", "трикутник повертають"]),
        ("2006", ["Фаулер ділить назву", "надвоє"]),
        ("2009", ["GWT: подання роблять", "надто дурним для тестів"]),
    ]

    x0, x1, axis_y = 110.0, 1130.0, 180.0
    step = (x1 - x0) / (len(events) - 1)

    f.append(line(60, axis_y, 1180, axis_y, color=MUTED, sw=1.6))

    for i, (year, lines) in enumerate(events):
        x = x0 + i * step
        above = (i % 2 == 0)
        f.append(circle(x, axis_y, 6, fill=BLUE, stroke=INK, sw=1.8))
        if above:
            f.append(mtext(x, 100, lines, size=11.5, color=MUTED, lh=1.45))
            f.append(text(x, 148, year, size=14, bold=True))
            f.append(line(x, 156, x, 173, color=MUTED, sw=1.2))
        else:
            f.append(line(x, 187, x, 194, color=MUTED, sw=1.2))
            f.append(text(x, 210, year, size=14, bold=True))
            f.append(mtext(x, 236, lines, size=11.5, color=MUTED, lh=1.45))

    render(os.path.join(IMG, 'mvp-timeline.svg'), W, H, *f,
           title="Порядок подій: звідки взялася назва MVP і що з нею робили далі")


# ── Фігура 4 (вставка hist): три різні схеми під однією назвою ───────────────
def fig_three_wirings():
    W, H = 1180, 510
    f = []

    panels = [
        ("Taligent, 1996", "як описав Майк Потел", "A"),
        ("Dolphin Smalltalk, 2000", "Енді Бауер і Блер Мак-Ґлешен", "B"),
        ("Пасивне подання, 2006", "як назвав Мартін Фаулер", "C"),
    ]
    captions = {
        "A": ["Презентер збирає застосунок і тримає логіку,",
              "але подання малює те, що прочитало з моделі."],
        "B": ["Модель сповіщає подання (спостерігач),",
              "а презентер уперше чіпає екран напряму."],
        "C": ["Подання не бачить моделі зовсім:",
              "усе, що воно знає, кладе туди презентер."],
    }

    for px, (name, who, kind) in zip((20, 405, 790), panels):
        f.append(rect(px, 52, 370, 390, fill="#fbfbfd", stroke="#d9d9e3", sw=1.2, rx=12))
        f.append(text(px + 185, 86, name, size=15, bold=True))
        f.append(text(px + 185, 108, who, size=11.5, color=MUTED))

        f.append(box3(px + 185, 175, 190, 50, "Презентер", fill=BLUE))
        f.append(box3(px + 85, 305, 140, 50, "Подання", fill=GREEN))
        f.append(box3(px + 285, 305, 140, 50, "Модель", fill=AMBER))

        # права діагональ — презентер змінює модель (є в усіх трьох)
        f.append(arrow(px + 230, 202, px + 275, 277))

        if kind == "A":
            f.append(dashed_arrow(px + 140, 202, px + 95, 277, color=MUTED, sw=1.8))
            f.append(arrow(px + 157, 305, px + 213, 305, color=POS, sw=2.4))
        elif kind == "B":
            f.append(arrow(px + 140, 202, px + 95, 277, color=POS, sw=2.4))
            f.append(dashed_arrow(px + 213, 305, px + 157, 305, color=MUTED, sw=1.8))
        else:
            f.append(arrow(px + 140, 202, px + 95, 277))
            f.append(line(px + 157, 305, px + 213, 305, color=MUTED, sw=1.6, dash="6 5"))
            mx = px + 185
            f.append(line(mx - 9, 296, mx + 9, 314, color=POS, sw=3.0))
            f.append(line(mx + 9, 296, mx - 9, 314, color=POS, sw=3.0))

        f.append(mtext(px + 185, 372, captions[kind], size=11.5, color=MUTED, lh=1.5))

    f.append(text(590, 478,
                  "червоним — те, чим схема відрізняється; пунктир — сповіщення або складання",
                  size=11.5, color=MUTED))

    render(os.path.join(IMG, 'mvp-three-wirings.svg'), W, H, *f,
           title="Три різні схеми, які в різні роки називали однаково — MVP")


# ── Фігура 5 (вставка proj): латка проти кадру ───────────────────────────────
def _screen(cx, top, plus_dead, status_text, status_color, plus_wrong):
    """Макет екрана термостата: цифра, смужка, дві кнопки, рядок стану."""
    f = []
    f.append(rect(cx - 195, top, 390, 270, fill="#ffffff", stroke=MUTED, sw=1.6, rx=10))

    f.append(text(cx, top + 68, "30°", size=40, bold=True))
    f.append(rect(cx - 155, top + 98, 310, 16, fill=POS, stroke=POS, sw=1.0, rx=6))

    # «−» жива в обох випадках
    f.append(rect(cx - 150, top + 133, 110, 46, fill=GREY, stroke=INK, sw=1.6, rx=8))
    f.append(text(cx - 95, top + 165, "−", size=22, bold=True, color=NEG))

    # «+» — або згасла (правильно), або жива (помилка)
    if plus_dead:
        f.append(rect(cx + 40, top + 133, 110, 46, fill="#f0f0f3", stroke=MUTED, sw=1.6, rx=8))
        f.append(text(cx + 95, top + 165, "+", size=22, bold=True, color="#c9ccd1"))
    else:
        f.append(rect(cx + 40, top + 133, 110, 46, fill=GREY,
                      stroke=POS if plus_wrong else INK,
                      sw=2.6 if plus_wrong else 1.6, rx=8))
        f.append(text(cx + 95, top + 165, "+", size=22, bold=True, color=POS))

    f.append(text(cx, top + 228, status_text, size=15, color=status_color))
    return f


def fig_frame_vs_patch():
    W, H = 980, 462
    f = []
    LCX, RCX, TOP = 255, 725, 82

    f.append(text(LCX, 64, "Латка: обробник поправив, що згадав", size=14, bold=True, color=POS))
    f.append(text(RCX, 64, "Кадр: render() малює все з одного числа", size=14, bold=True))

    f += _screen(LCX, TOP, plus_dead=False, status_text="Тримає 29°",
                 status_color=POS, plus_wrong=True)
    f += _screen(RCX, TOP, plus_dead=True, status_text="Вище не можна: 30°",
                 status_color=INK, plus_wrong=False)

    f.append(text(64, 398, "✗  кнопка «+» жива — а вище 30° нікуди",
                  size=12.5, color=POS, anchor="start"))
    f.append(text(64, 422, "✗  рядок стану відстав на один дотик",
                  size=12.5, color=POS, anchor="start"))
    f.append(text(534, 398, "✓  усі п'ять фактів виведено з одного t = 30",
                  size=12.5, color=MUTED, anchor="start"))
    f.append(text(534, 422, "✓  забути поле нема де: дорога до екрана одна",
                  size=12.5, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'frame-vs-patch.svg'), W, H, *f,
           title="Той самий дотик «+» на 29°: латка проти кадру")


# ── Фігура 6 (вставка proj): луна — подання чує власний голос ────────────────
def fig_echo_loop():
    W, H = 900, 462
    f = []

    f.append(box3(200, 130, 300, 74, "Презентер", "render() кладе «23» у поле", fill=BLUE))
    f.append(box3(680, 130, 320, 74, "Подання", "field.setText(\"23\")", fill=GREEN))
    f.append(box3(680, 320, 320, 74, "Віджет", "піднімає «текст змінився»", fill=GREY))
    f.append(box3(200, 320, 300, 74, "Обробник onTargetTyped",
                  "просить модель змінитися", fill=AMBER))

    f.append(arrow(350, 130, 520, 130))
    f.append(text(435, 112, "команда екрана", size=12))

    f.append(arrow(680, 167, 680, 283))
    f.append(mtext(662, 214, ["віджет не розрізняє,", "хто змінив текст"],
                   size=11.5, color=MUTED, anchor="end", lh=1.5))

    f.append(arrow(520, 320, 350, 320))
    f.append(text(435, 302, "доповідає назовні", size=12))

    # сторож усередині подання розриває коло
    f.append(line(425, 308, 445, 332, color=POS, sw=3.0))
    f.append(line(445, 308, 425, 332, color=POS, sw=3.0))
    f.append(text(435, 353, "сторож pushing", size=12, color=POS))

    f.append(arrow(200, 283, 200, 167))
    f.append(text(218, 225, "і все спочатку", size=12, anchor="start"))

    f.append(text(450, 410, "Swing: setText() будить DocumentListener. "
                            "WinForms: присвоєння Text піднімає TextChanged.",
                  size=12, color=MUTED))
    f.append(text(450, 432, "У DOM присвоєння input.value подій не піднімає — "
                            "і того самого кола там не виникає.",
                  size=12, color=MUTED))

    render(os.path.join(IMG, 'echo-loop.svg'), W, H, *f,
           title="Луна: подання чує власний голос")


if __name__ == "__main__":
    fig_mediator()
    fig_fake_view()
    fig_timeline()
    fig_three_wirings()
    fig_frame_vs_patch()
    fig_echo_loop()
    print("OK: presenter-mediator.svg, fake-view-test.svg, "
          "mvp-timeline.svg, mvp-three-wirings.svg, "
          "frame-vs-patch.svg, echo-loop.svg")

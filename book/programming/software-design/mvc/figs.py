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


# ── Фігура 1: класичний триадний MVC (живе коло зі спостерігачем) ────────────
def fig_classic():
    W, H = 840, 580
    f = []

    # Вузли
    f.append(box3(410, 82, 190, 54, "Користувач", fill=GREY))
    f.append(box3(215, 205, 210, 92, "Контролер",
                  "перекладає ввід", "у команду моделі", fill=BLUE))
    f.append(box3(615, 205, 210, 92, "Подання",
                  "читає модель і малює", "(їх може бути кілька)", fill=GREEN))
    f.append(box3(410, 445, 220, 96, "Модель",
                  "дані + правило", "не знає про подання", fill=AMBER))

    # 1) Користувач → Контролер
    f.append(arrow(358, 106, 258, 159))
    f.append(text(300, 128, "натискає", size=12))
    # 2) Подання → Користувач (бачить)
    f.append(arrow(566, 159, 500, 108))
    f.append(text(566, 126, "бачить", size=12))

    # 3) Контролер → Модель (змінює стан)
    f.append(arrow(250, 251, 362, 400))
    f.append(text(232, 336, "змінює", size=12.5, anchor="end"))
    f.append(text(232, 353, "стан", size=12.5, anchor="end"))

    # 4) Модель → Подання: сповіщення (observer, зелений пунктир) — верхня діагональ
    f.append(dashed_arrow(452, 400, 576, 250, color=FIELD, sw=2.2))
    f.append(text(486, 316, "сповіщає", size=12.5, color=FIELD, anchor="middle"))
    f.append(text(486, 333, "(observer)", size=11.5, color=FIELD, anchor="middle"))

    # 5) Подання → Модель: читання свіжого стану — нижня діагональ (пул)
    f.append(('<line x1="600.0" y1="256.0" x2="476.0" y2="404.0" stroke="%s" '
              'stroke-width="1.5" marker-end="url(#arrow)"/>' % MUTED))
    f.append(text(618, 342, "читає", size=12, color=MUTED, anchor="start"))
    f.append(text(618, 359, "стан", size=12, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'classic-mvc.svg'), W, H, *f,
           title="Класичний MVC: живе коло")


# ── Фігура 2: вебовий MVC (Model 2) — однопрохідний конвеєр ──────────────────
def fig_web():
    W, H = 960, 470
    f = []

    f.append(box3(130, 235, 150, 90, "Браузер", "клієнт", fill=GREY))
    f.append(box3(400, 235, 190, 90, "Контролер", "обробник маршруту", fill=BLUE))
    f.append(box3(720, 150, 230, 82, "Модель", "дані + правила", fill=AMBER))
    f.append(box3(720, 330, 230, 82, "Подання", "шаблон сторінки", fill=GREEN))

    # 1) Браузер → Контролер
    f.append(arrow(205, 218, 305, 218))
    f.append(text(255, 205, "1. запит", size=12.5))

    # 2) Контролер → Модель  (верхня лінія)
    f.append(arrow(492, 208, 604, 172))
    f.append(text(548, 176, "2. дай / зміни дані", size=12, anchor="middle"))
    # 3) Модель → Контролер  (нижня лінія, паралельна)
    f.append(('<line x1="604.0" y1="192.0" x2="494.0" y2="228.0" stroke="%s" '
              'stroke-width="1.8" marker-end="url(#arrow)"/>' % MUTED))
    f.append(text(548, 246, "3. дані", size=12, color=MUTED, anchor="middle"))

    # 4) Контролер → Подання (обрати шаблон + дані)
    f.append(arrow(430, 281, 604, 320))
    f.append(text(452, 322, "4. шаблон + дані", size=12, anchor="start"))

    # 5) Подання → Браузер: довга відповідь низом
    f.append(line(720, 371, 720, 430, color=INK, sw=1.9))
    f.append(line(720, 430, 130, 430, color=INK, sw=1.9))
    f.append(arrow(130, 430, 130, 282))
    f.append(text(415, 418, "5. готовий HTML", size=12.5, anchor="middle"))

    render(os.path.join(IMG, 'web-mvc.svg'), W, H, *f,
           title="Вебовий MVC (Model 2): запит → відповідь")


# ── Фігура 3: рід MVC — MVC → MVP → MVVM ─────────────────────────────────────
def fig_family():
    W, H = 900, 600
    f = []

    def panel(yc, tag, mediator, note, mode):
        vx, mx, dx = 265, 480, 695     # центри: Подання, Посередник, Модель
        bw, bh = 150, 58
        # заголовок роду ліворуч
        f.append(text(48, yc - 4, tag, size=19, bold=True, anchor="start"))
        # три рамки
        f.append(box3(vx, yc, bw, bh, "Подання", fill=GREEN))
        med_fill = GREEN if mode == "mvvm" else BLUE
        f.append(box3(mx, yc, bw, bh, mediator, fill=med_fill))
        f.append(box3(dx, yc, bw, bh, "Модель", fill=AMBER))
        # центральні двобічні звʼязки
        c1 = FIELD if mode == "mvvm" else LINE
        sw1 = 3.0 if mode == "mvvm" else 1.9
        f.append(biarrow(vx + bw / 2 + 4, yc, mx - bw / 2 - 4, yc, color=c1, sw=sw1))
        f.append(biarrow(mx + bw / 2 + 4, yc, dx - bw / 2 - 4, yc))
        # верхня дуга Подання↔Модель
        top = yc - bh / 2
        if mode == "mvc":
            f.append(arc(vx, top, dx, top, yc - 82, color=INK, sw=2.0, head=True))
            f.append(text((vx + dx) / 2, yc - 66,
                          "подання читає модель напряму", size=12, anchor="middle"))
        elif mode == "mvp":
            f.append(arc(vx, top, dx, top, yc - 82, color=MUTED, sw=1.8,
                         dash=True, head=False))
            cx = (vx + dx) / 2
            f.append(line(cx - 9, yc - 62, cx + 9, yc - 46, color=POS, sw=3.2))
            f.append(line(cx + 9, yc - 62, cx - 9, yc - 46, color=POS, sw=3.2))
            f.append(text(cx, yc - 74, "прямого звʼязку нема", size=12, anchor="middle"))
        else:  # mvvm
            f.append(text((vx + mx) / 2, yc - 30,
                          "двобічне звʼязування", size=12, color=FIELD, anchor="middle"))
        # підпис-нота під рядком
        f.append(text(480, yc + bh / 2 + 26, note, size=12, color=MUTED, anchor="middle"))

    panel(120, "MVC", "Контролер",
          "Подання читає модель напряму; контролер лише обробляє ввід.", "mvc")
    panel(320, "MVP", "Презентер",
          "Пасивне подання говорить тільки з презентером — моделі не знає.", "mvp")
    panel(510, "MVVM", "Модель подання",
          "Рушій звʼязування синхронізує подання й модель подання сам.", "mvvm")

    render(os.path.join(IMG, 'mvc-family.svg'), W, H, *f,
           title="Рід MVC: хто-посередник між екраном і даними")


RED = "#fdecea"


# ── Фігура 4: розплутування обробника — БУЛО / СТАЛО ─────────────────────────
def fig_untangle():
    W, H = 1000, 610
    f = []

    # роздільник між «було» і «стало»
    f.append(line(500, 78, 500, 560, color=MUTED, sw=1.2, dash="4 6"))

    # ── ЛІВОРУЧ: один обробник робить усе ──
    f.append(text(250, 54, "БУЛО: усе в одному обробнику", size=16, bold=True))
    f.append(rect(55, 92, 390, 386, fill=RED, stroke=INK, sw=1.8, rx=10))
    f.append(text(250, 124, "on_plus_clicked()", size=15, bold=True))

    rows = [("1 · ввід — читає число з ЕКРАНА", GREY),
            ("2 · правило — межа 5–30", AMBER),
            ("3 · рендер — поле + смужка", GREEN),
            ("4 · збереження — на диск", BLUE)]
    y = 146
    for label, fill in rows:
        f.append(fitbox(80, y, 340, 46, label, size=13, fill=fill, sw=1.4))
        y += 56
    f.append(text(250, 410, "on_minus_clicked() — майже копія всього", size=12, color=MUTED))
    f.append(text(250, 434, "стан живе у віджеті, не в моделі", size=12, color=MUTED))
    f.append(text(250, 460, "правило межі не перевірити без екрана", size=12, color=POS))

    # ── ПРАВОРУЧ: тонкий шов + спостерігач ──
    f.append(text(748, 54, "СТАЛО: тонкий шов + спостерігач", size=16, bold=True))
    f.append(box3(605, 140, 178, 70, "Контролер", "переклад вводу", fill=BLUE))
    f.append(box3(605, 300, 202, 96, "Модель", "target + clamp 5–30", "не знає про подання", fill=AMBER))
    f.append(arrow(605, 176, 605, 250))
    f.append(text(622, 218, "nudge(±1)", size=12, anchor="start"))

    f.append(box3(882, 176, 152, 62, "DigitView", "читає target", fill=GREEN))
    f.append(box3(882, 300, 152, 62, "BarView", "читає target", fill=GREEN))
    f.append(box3(882, 424, 152, 62, "FileStore", "пише target", fill=GREY))

    f.append(dashed_arrow(708, 286, 804, 180, color=FIELD, sw=2.2))
    f.append(dashed_arrow(710, 300, 804, 300, color=FIELD, sw=2.2))
    f.append(dashed_arrow(708, 314, 804, 420, color=FIELD, sw=2.2))
    f.append(text(748, 200, "сповіщає", size=12.5, color=FIELD, anchor="middle"))

    f.append(text(748, 536, "один сигнал «змінилася» — хто підписаний, той і читає",
                  size=12, color=MUTED, anchor="middle"))

    render(os.path.join(IMG, 'untangle-before-after.svg'), W, H, *f,
           title="Розплутування: обробник-спрут → три частини")


# ── Фігура 5: пастка «розумного подання» — цикл, що не спиниться ─────────────
def fig_smart_loop():
    W, H = 820, 470
    f = []

    f.append(text(410, 48, "Пастка: подання, що пише в модель, зациклюється",
                  size=16, bold=True))

    f.append(box3(205, 150, 214, 74, "BarView.render()", "містить model.nudge()", fill=RED))
    f.append(box3(620, 150, 190, 74, "Модель змінилась", "(бо render писав)", fill=AMBER))
    f.append(box3(412, 340, 236, 74, "Модель сповіщає", "всіх підписників", fill=RED))

    # цикл: render → зміна → сповіщення → render …
    f.append(arrow(312, 138, 525, 138, color=POS, sw=2.4))
    f.append(text(418, 122, "1 · рендер міняє модель", size=12, color=POS, anchor="middle"))

    f.append(arrow(602, 187, 470, 305, color=POS, sw=2.4))
    f.append(text(590, 258, "2 · зміна", size=12, color=POS, anchor="start"))
    f.append(text(590, 275, "кличе", size=12, color=POS, anchor="start"))

    f.append(arrow(352, 305, 232, 187, color=POS, sw=2.4))
    f.append(text(238, 262, "3 · рендер", size=12, color=POS, anchor="end"))
    f.append(text(238, 279, "знову", size=12, color=POS, anchor="end"))

    f.append(text(410, 430, "читач, що пише в модель, сам себе будить — коло не спиняється",
                  size=13, color=MUTED, anchor="middle"))

    render(os.path.join(IMG, 'smart-view-loop.svg'), W, H, *f,
           title="Розумне подання: цикл render → зміна → render")


# ── Фігура 6 (вставка hist): чотири частини стали трьома ─────────────────────
def fig_tmve_reduction():
    W, H = 900, 470
    f = []

    f.append(text(450, 62, "Травень 1979: «Thing-Model-View-Editor» — чотири частини",
                  size=14.5, bold=True))

    # Верхній ряд — чотири частини травневої нотатки
    f.append(box3(180, 150, 150, 50, "Thing", fill=GREY))
    f.append(box3(380, 150, 150, 50, "Model", fill=AMBER))
    f.append(box3(580, 150, 150, 50, "View", fill=GREEN))
    f.append(box3(760, 150, 150, 50, "Editor", fill=BLUE))

    # Стрілки вниз — що з чим сталося
    f.append(arrow(380, 176, 380, 304))
    f.append(text(398, 246, "без змін", size=11, color=MUTED, anchor="start"))
    f.append(arrow(580, 176, 580, 304))
    f.append(text(598, 246, "без змін", size=11, color=MUTED, anchor="start"))
    f.append(arrow(760, 176, 760, 304))
    f.append(text(778, 238, "перейменований,", size=11, color=MUTED, anchor="start"))
    f.append(text(778, 254, "ширший за Editor", size=11, color=MUTED, anchor="start"))

    # «Thing» випадає з коду у світ
    f.append(dashed_arrow(180, 176, 180, 298, color=MUTED, sw=1.8))
    f.append(text(180, 320, "«Thing» лишається у світі", size=11.5, color=MUTED, italic=True))
    f.append(text(180, 337, "— поза кодом застосунку", size=11.5, color=MUTED, italic=True))

    # Нижній ряд — трійця, що лишилася
    f.append(box3(380, 330, 150, 50, "Model", fill=AMBER))
    f.append(box3(580, 330, 150, 50, "View", fill=GREEN))
    f.append(box3(760, 330, 150, 50, "Controller", fill=BLUE))

    f.append(text(573, 408, "Грудень 1979: «Model-View-Controller» — трійця коду",
                  size=14.5, bold=True))

    render(os.path.join(IMG, 'tmve-reduction.svg'), W, H, *f,
           title="Від чотирьох частин до трьох")


# ── Фігура 7 (вставка hist): мандрівне слово «контролер» ─────────────────────
def fig_controller_drift():
    W, H = 1000, 500
    f = []

    # Вісь часу зі стрілкою
    f.append(arrow(90, 150, 915, 150, color=INK, sw=2.2))
    f.append(text(902, 138, "час", size=11, color=MUTED, anchor="end"))

    # Віхи над віссю
    marks = [
        (150, "1979 · Xerox PARC", "нотатка Реенскауга"),
        (330, "1980 · Smalltalk-80", "класи MVC (команда)"),
        (540, "1988 · Cookbook", "Krasner & Pope, JOOP"),
        (830, "2000 · Apache Struts", "веб · McClanahan"),
    ]
    for x, top, sub in marks:
        f.append(circle(x, 150, 4.5, fill=INK, stroke=INK))
        f.append(text(x, 100, top, size=13, bold=True))
        f.append(text(x, 120, sub, size=11, color=MUTED))

    # З'єднувачі осі з панелями
    f.append(line(150, 156, 185, 230, color=MUTED, sw=1.2, dash="4 4"))
    f.append(line(330, 156, 495, 230, color=MUTED, sw=1.2, dash="4 4"))
    f.append(line(540, 156, 505, 230, color=MUTED, sw=1.2, dash="4 4"))
    f.append(line(830, 156, 835, 230, color=MUTED, sw=1.2, dash="4 4"))

    # Панелі-значення (що означав «контролер» у кожну добу)
    def panel(cx, w, fill, title, lines):
        y, h = 232, 138
        f.append(rect(cx - w / 2, y, w, h, fill=fill, stroke=INK, sw=1.6, rx=10))
        f.append(text(cx, y + 28, title, size=12.5, bold=True))
        f.append(line(cx - w / 2 + 16, y + 42, cx + w / 2 - 16, y + 42, color=MUTED, sw=1.0))
        f.append(mtext(cx, y + 66, lines, size=11.5, color=INK, lh=1.35))

    panel(185, 270, GREY, "Координатор подань",
          ["розставляє подання на екрані,",
           "показує меню, ловить команди,",
           "шле повідомлення до подань"])
    panel(500, 300, BLUE, "Обробник вводу однієї view",
          ["миша й клавіші однієї view",
           "(майже колишній «Editor»)",
           "цю версію рознесла Cookbook"])
    panel(835, 300, AMBER, "Диспетчер запиту",
          ["ловить увесь HTTP-запит,",
           "гукає модель, обирає шаблон,",
           "один HTML — і кінець"])

    render(os.path.join(IMG, 'controller-drift.svg'), W, H, *f,
           title="Мандрівне слово «контролер»: три роботи за двадцять років")


if __name__ == "__main__":
    fig_classic()
    fig_web()
    fig_family()
    fig_untangle()
    fig_smart_loop()
    fig_tmve_reduction()
    fig_controller_drift()
    print("OK: classic-mvc.svg, web-mvc.svg, mvc-family.svg, "
          "untangle-before-after.svg, smart-view-loop.svg, "
          "tmve-reduction.svg, controller-drift.svg")

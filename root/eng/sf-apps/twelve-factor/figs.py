# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_build_release_run():
    """Код (одна база) → build → артефакт; артефакт + конфіг середовища → release → run.
    Три середовища — окремі релізи з ТОГО САМОГО артефакту, різняться лише конфігом.
    Розкладка: конвеєр build згори ліворуч; три середовища — рядами праворуч, кожен
    зі своїм конфігом; стрілки короткі й не перетинають чужих написів."""
    W, H = 880, 470
    p = []

    # ── лівий стовпчик: код → build → артефакт ──
    cx = 130
    y_code = 70
    y_build = 180
    y_art = 300

    b, wc, hc = textbox(cx, y_code, ["код", "(одна база", "у git)"],
                        size=14, bold=True, fill="#eef2ff", stroke=NEG, min_w=150)
    p.append(b)
    b, wb, hb = textbox(cx, y_build, ["build", "(збірка — раз)"], size=14, bold=True,
                        fill=FILL, min_w=150)
    p.append(b)
    b, wa, ha = textbox(cx, y_art, ["артефакт", "незмінний", "(байт у байт)"],
                        size=13, fill="#f0fff4", stroke=FIELD, min_w=150)
    p.append(b)
    p.append(arrow(cx, y_code + hc / 2 + 3, cx, y_build - hb / 2 - 3))
    p.append(arrow(cx, y_build + hb / 2 + 3, cx, y_art - ha / 2 - 3))

    # ── праворуч три ряди: (артефакт + конфіг_i) → release_i/run_i ──
    rows = [
        ("dev",     "localhost",        NEG, 90),
        ("staging", "stg-db:5432",      MUTED, 230),
        ("prod",    "prod-db + секрет", POS, 370),
    ]
    x_cfg = 470
    x_run = 720
    for name, sub, col, ry in rows:
        # конфіг цього середовища
        b, wcfg, hcfg = textbox(x_cfg, ry, ["конфіг: " + name, sub],
                                size=13, fill="#fff7e6", stroke=POS, min_w=200)
        p.append(b)
        # реліз/запуск цього середовища
        b, wr, hr = textbox(x_run, ry, ["release + run", name], size=13, bold=True,
                            fill=FILL, stroke=col, min_w=180)
        p.append(b)
        # артефакт → цей конфіг (спільний артефакт живить усі три)
        p.append(arrow(cx + wa / 2 + 3, y_art, x_cfg - wcfg / 2 - 3, ry))
        # конфіг + артефакт → release
        p.append(arrow(x_cfg + wcfg / 2 + 3, ry, x_run - wr / 2 - 3, ry))

    p.append(text(W / 2, H - 22,
                  "той самий артефакт у всіх середовищах · різниця лише в конфігу, "
                  "доданому на release",
                  size=13, color=MUTED, italic=True))

    render(os.path.join(IMG, "build-release-run.svg"), W, H, *p)


def fig_stateless_backing():
    """Кілька однакових процесів без стану + спільні backing-сервіси.
    Показує, чому процес одноразовий (disposable) і чому масштабування —
    це просто «додати ще один такий самий процес»."""
    W, H = 780, 440
    p = []

    # ряд однакових процесів угорі
    py = 90
    xs = [150, 310, 470, 630]
    for i, x in enumerate(xs, 1):
        b, w, h = textbox(x, py, ["процес %d" % i, "без стану"], size=13, bold=True,
                          fill="#eef2ff", stroke=NEG, min_w=130)
        p.append(b)

    # балансувальник над процесами
    b, w, h = textbox(390, 30, "вхідні запити → балансувальник", size=13,
                      fill=FILL, min_w=320)
    p.append(b)
    for x in xs:
        p.append(arrow(390, 44, x, py - 26))

    # backing-сервіси внизу (спільний стан назовні процесів)
    by = 330
    svcs = [("база даних", 150, FIELD),
            ("кеш / черга", 360, FIELD),
            ("сховище файлів", 590, FIELD)]
    for name, x, col in svcs:
        b, w, h = textbox(x, by, name, size=13, bold=True, fill="#f0fff4",
                          stroke=col, min_w=170)
        p.append(b)

    # кожен процес однаково під'єднаний до кожного backing-сервісу
    # (щоб не плутати лініями — ведемо від кожного процесу до найближчого сервісу
    #  плюс до бази, показуючи спільність)
    for x in xs:
        p.append(line(x, py + 26, 150, by - 20, color=MUTED, sw=1.1, dash="4 4"))
        p.append(line(x, py + 26, 360, by - 20, color=MUTED, sw=1.1, dash="4 4"))
        p.append(line(x, py + 26, 590, by - 20, color=MUTED, sw=1.1, dash="4 4"))

    p.append(text(W / 2, H - 20,
                  "стан живе в backing-сервісах · процеси однакові й одноразові · "
                  "більше навантаження = ще один процес",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "stateless-backing.svg"), W, H, *p)


def fig_history_timeline():
    """Горизонтальна вісь часу народження й еволюції методики.
    Чотири віхи: 2007 (Heroku як PaaS), 2011 (маніфест), ~2013–2023 (де-факто
    стандарт), 2024 (відкриття коду спільноті). Підписи чергуються над/під віссю,
    щоб не накладалися; колонки широкі з запасом."""
    W, H = 940, 340
    p = []

    axis_y = 170
    x0, x1 = 70, W - 70
    p.append(line(x0, axis_y, x1, axis_y, color=INK, sw=2.2))
    # вістря вправо (плин часу)
    p.append(arrow(x1 - 24, axis_y, x1, axis_y, color=INK, sw=2.2))

    # (частка_по_осі, рік, рядки підпису, зверху?, колір)
    marks = [
        (0.06, "2007", ["Heroku", "як платформа-", "як-послуга (PaaS)"], True,  NEG),
        (0.34, "2011", ["маніфест", "12 факторів", "на 12factor.net"], False, POS),
        (0.63, "2013–2023", ["де-факто стандарт", "хмарної розробки"], True,  MUTED),
        (0.93, "12 лист. 2024", ["відкрито спільноті", "(GitHub, спільний", "супровід)"], False, FIELD),
    ]

    for frac, year, lines, top, col in marks:
        x = x0 + (x1 - x0) * frac
        # вузол на осі
        p.append(circle(x, axis_y, 8, fill="#ffffff", stroke=col, sw=2.4))
        # рік — впритул до осі (маленька мітка)
        if top:
            p.append(text(x, axis_y + 26, year, size=13, color=col, bold=True))
            by = axis_y - 78
            # хвостик від осі до рамки
            p.append(line(x, axis_y - 9, x, by + 34, color=col, sw=1.4))
            b, w, h = textbox(x, by, lines, size=12, fill=FILL, stroke=col, min_w=180)
            p.append(b)
        else:
            p.append(text(x, axis_y - 20, year, size=13, color=col, bold=True))
            by = axis_y + 84
            p.append(line(x, axis_y + 9, x, by - 40, color=col, sw=1.4))
            b, w, h = textbox(x, by, lines, size=12, fill=FILL, stroke=col, min_w=180)
            p.append(b)

    p.append(text(W / 2, H - 18,
                  "принципи виявилися довговічними · застаріли лише приклади й деталі "
                  "— їх і оновлюють від 2024 року",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "history-timeline.svg"), W, H, *p)


if __name__ == "__main__":
    fig_build_release_run()
    fig_stateless_backing()
    fig_history_timeline()
    print("figures written to", IMG)

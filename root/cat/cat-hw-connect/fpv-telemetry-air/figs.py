# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

RADIO = "#e8f0ff"   # блок радіомодуля
UART  = "#eafaf0"   # лінія UART
AIRC  = "#fff4e6"   # ефір / радіоканал


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 1: канал «повітряний ↔ наземний», з нутром повітряного модуля
# ─────────────────────────────────────────────────────────────────────────────
def fig_link():
    W, H = 900, 470
    frags = []

    # --- Борт (ліворуч) ------------------------------------------------------
    frags.append(text(215, 58, "БОРТ (у повітрі)", size=15, bold=True, color=MUTED))

    # Політний контролер
    fc = fitbox(40, 90, 130, 78, "Політний\nконтролер\n(MAVLink по UART)",
                size=13, fill=FILL, bold=False)
    frags.append(fc)

    # Повітряний модуль — велика рамка з нутром
    mx, my, mw, mh = 210, 82, 250, 300
    frags.append(rect(mx, my, mw, mh, fill=RADIO, stroke="#3b6fd4", sw=2))
    frags.append(text(mx + mw / 2, my + 24, "ПОВІТРЯНИЙ МОДУЛЬ", size=13, bold=True, color="#274b8f"))

    # нутро: MCU, радіочип, PA/LNA, кварц
    b1 = fitbox(mx + 22, my + 46, 92, 58, "MCU\nSi1000\n(8051 + AT)", size=11)
    b2 = fitbox(mx + 136, my + 46, 92, 58, "радіочип\nSi4432\n(модем)", size=11)
    frags.append(b1)
    frags.append(b2)
    frags.append(arrow(mx + 114, my + 75, mx + 136, my + 75, color=INK))

    b3 = fitbox(mx + 22, my + 128, 92, 50, "PA / LNA\nпідсил.", size=11)
    b4 = fitbox(mx + 136, my + 128, 92, 50, "кварц\nоп. частота", size=11)
    frags.append(b3)
    frags.append(b4)
    frags.append(arrow(mx + 182, my + 104, mx + 182, my + 128, color=INK))
    frags.append(arrow(mx + 114, my + 153, mx + 136, my + 153, color=INK))

    # живлення 5В → 3.3В
    b5 = fitbox(mx + 22, my + 200, 206, 40, "стабілізатор 5 В → 3.3 В  (внутр.)", size=11, fill="#fdeeee")
    frags.append(b5)

    # антена бортова
    ax, ay = mx + mw, my + 150
    frags.append(line(ax, ay, ax + 34, ay, color=INK, sw=2))
    frags.append(line(ax + 34, ay, ax + 34, ay - 40, color=INK, sw=2))
    frags.append(text(ax + 34, ay - 48, "ANT", size=12, bold=True))

    # UART FC ↔ модуль (двобічний)
    frags.append(text(190, 118, "TX/RX", size=11, color=FIELD, bold=True))
    frags.append(arrow(170, 129, 210, 129, color=FIELD, sw=2.2))
    frags.append(arrow(210, 145, 170, 145, color=FIELD, sw=2.2))

    # --- Ефір (посередині) ---------------------------------------------------
    ex = ax + 34
    gx = 720   # ліва межа наземного блоку
    midy = my + 150
    # хвилі туди-сюди
    frags.append(rect(ex + 6, midy - 74, gx - ex - 12, 148, fill=AIRC, stroke="#e0a04a", sw=1.4))
    frags.append(text((ex + gx) / 2, midy - 52, "РАДІОКАНАЛ", size=13, bold=True, color="#b06f1e"))
    frags.append(text((ex + gx) / 2, midy - 32, "433 / 868 / 915 МГц (ISM)", size=11, color="#8a5a1a"))
    frags.append(arrow(ex + 18, midy + 4, gx - 18, midy + 4, color="#b06f1e", sw=2.4))
    frags.append(text((ex + gx) / 2, midy - 6, "телеметрія вниз →", size=11, color="#8a5a1a"))
    frags.append(arrow(gx - 18, midy + 40, ex + 18, midy + 40, color="#b06f1e", sw=2.4))
    frags.append(text((ex + gx) / 2, midy + 30, "← команди вгору", size=11, color="#8a5a1a"))
    frags.append(text((ex + gx) / 2, midy + 62, "одна пара, півдуплекс (TDM)", size=11, color="#8a5a1a"))

    # --- Земля (праворуч) ----------------------------------------------------
    frags.append(text(795, 58, "ЗЕМЛЯ (оператор)", size=15, bold=True, color=MUTED))

    # антена наземна
    frags.append(line(gx, midy, gx + 26, midy, color=INK, sw=2))
    frags.append(line(gx + 26, midy, gx + 26, midy - 40, color=INK, sw=2))
    frags.append(text(gx + 26, midy - 48, "ANT", size=12, bold=True))

    gm = fitbox(760, 100, 108, 150, "НАЗЕМНИЙ\nМОДУЛЬ\n(той самий\nтрансивер)", size=12, fill=RADIO, stroke="#3b6fd4", sw=2, bold=False)
    frags.append(gm)
    # USB до ноутбука
    frags.append(text(814, 300, "USB / UART", size=11, color=FIELD, bold=True))
    frags.append(arrow(814, 250, 814, 285, color=FIELD, sw=2.2))
    gcs = fitbox(752, 315, 124, 60, "наземна станція\n(Mission Planner /\nQGroundControl)", size=11, fill=FILL)
    frags.append(gcs)

    # підказка «пара однакових»
    frags.append(text(W / 2, H - 22, "Обидва модулі однакові й взаємозамінні — «повітряний» лише той, що на борту.",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, 'link.svg'), W, H, *frags)


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 2: розводка 6-контактного роз'єму пін-у-пін до польотного контролера
# ─────────────────────────────────────────────────────────────────────────────
def fig_pinout():
    W, H = 820, 470
    frags = []
    frags.append(text(W / 2, 34, "6-контактний роз'єм модуля → TELEM-порт польотного контролера", size=15, bold=True))

    # два стовпці
    modx = 150     # центр стовпця модуля
    fcx = 640      # центр стовпця FC
    top = 78
    dy = 58

    pins = [
        ("1", "+5V",  "живлення модуля 5 В", "5V",  POS,  "#fdeeee"),
        ("2", "TX",   "дані з модуля →",     "RX",  FIELD, UART),
        ("3", "RX",   "дані в модуль ←",     "TX",  FIELD, UART),
        ("4", "CTS",  "апаратний потік",     "RTS", MUTED, FILL),
        ("5", "RTS",  "апаратний потік",     "CTS", MUTED, FILL),
        ("6", "GND",  "спільна земля",       "GND", NEG,  "#eef2fe"),
    ]

    # заголовки стовпців
    frags.append(text(modx, top - 22, "ПОВІТРЯНИЙ МОДУЛЬ", size=12, bold=True, color="#274b8f"))
    frags.append(text(fcx, top - 22, "ПОЛЬОТНИЙ КОНТРОЛЕР (TELEM)", size=12, bold=True, color="#274b8f"))

    # рамки-роз'єми
    frags.append(rect(modx - 78, top - 8, 156, dy * 6 + 4, fill="none", stroke="#3b6fd4", sw=1.6))
    frags.append(rect(fcx - 78, top - 8, 156, dy * 6 + 4, fill="none", stroke="#3b6fd4", sw=1.6))

    for i, (num, ml, desc, fl, col, fill) in enumerate(pins):
        y = top + i * dy + dy / 2

        # контакт модуля
        frags.append(rect(modx - 74, y - 20, 148, 40, fill=fill, stroke=col, sw=1.6))
        frags.append(text(modx - 60, y + 5, num, size=13, bold=True, color=MUTED))
        frags.append(text(modx + 6, y + 5, ml, size=14, bold=True, color=col))

        # контакт FC
        frags.append(rect(fcx - 74, y - 20, 148, 40, fill=fill, stroke=col, sw=1.6))
        frags.append(text(fcx + 6, y + 5, fl, size=14, bold=True, color=col))

        # провід із підписом посередині (розставлено з запасом, повз написи)
        frags.append(line(modx + 74, y, fcx - 74, y, color=col, sw=2))
        frags.append(text((modx + fcx) / 2, y - 8, desc, size=11, color=MUTED))

    # виноска про перехрест TX/RX
    note_y = top + dy * 6 + 26
    frags.append(text(W / 2, note_y, "TX ↔ RX і RX ↔ TX — лінії ПЕРЕХРЕЩЕНО (вихід одного на вхід іншого).",
                      size=12, color=INK, bold=True))
    frags.append(text(W / 2, note_y + 22, "CTS/RTS часто не з'єднують; рівні лінійок — 3.3 В (живлення 5 В).",
                      size=11.5, color=MUTED, italic=True))

    render(os.path.join(IMG, 'pinout.svg'), W, H, *frags)


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 3: життєвий цикл AT-режиму — «труба» ⇄ «пульт», збереження й перезапуск
# (саме тут родяться три головні пастки конфігурації з коду)
# ─────────────────────────────────────────────────────────────────────────────
def fig_atmode():
    W, H = 900, 560
    frags = []
    frags.append(text(W / 2, 34, "Життєвий цикл AT-режиму SiK-модуля (де саме ламається конфіг із коду)",
                      size=15, bold=True))

    CMD = "#e8f0ff"    # режим команд
    PIPE = "#eafaf0"   # прозора труба
    WARN = "#fdeeee"   # пастка

    # --- Стан 1: прозора труба (згори) --------------------------------------
    s1x, s1y, s1w, s1h = 300, 66, 300, 74
    frags.append(rect(s1x, s1y, s1w, s1h, fill=PIPE, stroke=FIELD, sw=2))
    frags.append(text(s1x + s1w / 2, s1y + 28, "ПРОЗОРА ТРУБА", size=13, bold=True, color="#1e6b3a"))
    frags.append(text(s1x + s1w / 2, s1y + 50, "байти летять наскрізь; AT не діють", size=11, color="#2f6b47"))

    # --- Стан 2: режим команд (посередині) ----------------------------------
    s2x, s2y, s2w, s2h = 300, 250, 300, 96
    frags.append(rect(s2x, s2y, s2w, s2h, fill=CMD, stroke="#3b6fd4", sw=2))
    frags.append(text(s2x + s2w / 2, s2y + 26, "РЕЖИМ КОМАНД", size=13, bold=True, color="#274b8f"))
    frags.append(text(s2x + s2w / 2, s2y + 48, "ATI / ATI5 — читати", size=11, color="#33517f"))
    frags.append(text(s2x + s2w / 2, s2y + 68, "ATSn=… — міняти в RAM", size=11, color="#33517f"))
    frags.append(text(s2x + s2w / 2, s2y + 88, "RT… — той самий набір на віддалений", size=11, color="#33517f"))

    # перехід труба → команди (ліворуч, униз)
    frags.append(arrow(s1x + 70, s1y + s1h, s2x + 70, s2y, color=FIELD, sw=2.4))
    frags.append(text(150, (s1y + s1h + s2y) / 2 - 10, "1 с тиші  →  +++  →  1 с тиші", size=12, bold=True, color="#1e6b3a"))
    frags.append(text(150, (s1y + s1h + s2y) / 2 + 10, "модуль відповідає «OK»", size=11, color=MUTED))

    # перехід команди → труба (праворуч, угору) — ATO
    frags.append(arrow(s2x + s2w - 70, s2y, s1x + s1w - 70, s1y + s1h, color="#3b6fd4", sw=2.2))
    frags.append(text(760, (s1y + s1h + s2y) / 2, "ATO — вихід", size=12, bold=True, color="#274b8f"))

    # --- Стан 3: збереження + перезапуск (знизу) ----------------------------
    s3x, s3y, s3w, s3h = 300, 452, 300, 74
    frags.append(rect(s3x, s3y, s3w, s3h, fill=PIPE, stroke=FIELD, sw=2))
    frags.append(text(s3x + s3w / 2, s3y + 28, "ЗБЕРЕЖЕНО + ПЕРЕЗАПУЩЕНО", size=12.5, bold=True, color="#1e6b3a"))
    frags.append(text(s3x + s3w / 2, s3y + 50, "нові параметри діють; лінія піднялась заново", size=11, color="#2f6b47"))

    frags.append(arrow(s2x + s2w / 2, s2y + s2h, s3x + s3w / 2, s3y, color=FIELD, sw=2.4))
    frags.append(text(s2x + s2w / 2 - 82, (s2y + s2h + s3y) / 2 + 5, "AT&W → ATZ", size=12, bold=True, color="#1e6b3a", anchor="end"))

    # --- Три пастки — виноски збоку, повз лінії ------------------------------
    tx = 632
    p1 = fitbox(tx, 78, 250, 70, "ПАСТКА 1: +++ у трубі\nне вийшли з потоку — +++\nсприймуться як дані, «OK» нема",
                size=11, fill=WARN, stroke=POS, sw=1.6)
    frags.append(p1)

    p2 = fitbox(18, 250, 250, 70, "ПАСТКА 2: забули AT&W\nATSn змінив лише RAM;\nбез запису ATZ усе поверне назад",
                size=11, fill=WARN, stroke=POS, sw=1.6)
    frags.append(p2)

    p3 = fitbox(632, 452, 250, 74, "ПАСТКА 3: ATZ рве зв'язок\nпорт відкриється заново;\nстарий serial-об'єкт треба закрити",
                size=11, fill=WARN, stroke=POS, sw=1.6)
    frags.append(p3)

    render(os.path.join(IMG, 'atmode.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_link()
    fig_pinout()
    fig_atmode()
    print("ok")

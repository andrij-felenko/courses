# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def data_vs_meaning():
    # Ліворуч — брокер із топіком і сирим числом (самі байти).
    # Праворуч — осмислена картка застосунку.
    # Посередині — прірва з питанням «хто пояснить?».
    W, H = 720, 400
    p = []

    # --- ліва частина: брокер + сирий топік ---
    lx = 60
    p.append(text(lx + 110, 40, "БРОКЕР MQTT: самі байти", size=15, color=NEG, bold=True))

    # хмара-брокер
    p.append(circle(lx + 42, 96, 34, fill="#eaf0fd", stroke=NEG, sw=2.2))
    p.append(text(lx + 42, 100, "☁", size=22, color=NEG))

    # гілка топіка
    p.append(fitbox(lx + 6, 150, 210, 30, "home/livingroom/thermostat/state",
                    size=11, fill=FILL, stroke=MUTED))
    # сире число
    p.append(fitbox(lx + 40, 210, 140, 44, "21.4", size=26, fill="#ffffff",
                    stroke=INK))
    p.append(text(lx + 110, 274, "рядок і число — без", size=12, color=MUTED))
    p.append(text(lx + 110, 292, "типу, без одиниць, без змісту", size=12, color=MUTED))
    p.append(line(lx + 42, 130, lx + 110, 150, color=MUTED, sw=1.2))
    p.append(line(lx + 110, 180, lx + 110, 210, color=MUTED, sw=1.2))

    # --- права частина: осмислена картка ---
    rx = 470
    p.append(text(rx + 110, 40, "ЗАСТОСУНОК: осмислена картка", size=15,
                  color=FIELD, bold=True))
    # рамка картки
    p.append(rect(rx + 18, 70, 184, 210, fill="#eafaf0", stroke=FIELD, sw=2, rx=10))
    p.append(text(rx + 110, 104, "🌡", size=30, color=FIELD))
    p.append(text(rx + 110, 140, "Термостат вітальні", size=13, color=INK, bold=True))
    p.append(text(rx + 110, 178, "21.4 °C", size=24, color=INK, bold=True))
    # повзунок
    p.append(line(rx + 44, 214, rx + 176, 214, color=MUTED, sw=3))
    p.append(circle(rx + 128, 214, 8, fill=FIELD, stroke="#ffffff", sw=2))
    p.append(text(rx + 110, 250, "тип · назва · одиниці · керування", size=11,
                  color=MUTED))

    # --- прірва посередині ---
    gx = W / 2
    # два краї прірви
    p.append(line(lx + 220, 96, gx - 26, 96, color=NEG, sw=1.5, dash="4 4"))
    p.append(line(gx + 26, 175, rx + 18, 175, color=FIELD, sw=1.5, dash="4 4"))
    # зубчаста щілина
    zx = gx
    p.append('<path d="M %.0f 60 L %.0f 120 L %.0f 150 L %.0f 210 L %.0f 250 L %.0f 320" '
             'fill="none" stroke="%s" stroke-width="2"/>'
             % (zx - 10, zx + 10, zx - 10, zx + 10, zx - 10, zx + 10, POS))
    bb, bw, bh = textbox(gx, 300, "хто пояснить,", size=12, bold=True,
                         fill="#fdecea", stroke=POS, min_w=150)
    p.append(bb)
    p.append(text(gx, 322, "що це означає?", size=12, color=POS, bold=True))

    render(os.path.join(IMG, 'data-vs-meaning.svg'), W, H, *p,
           title="Розрив між сирими даними в брокері й осмисленою карткою")


def two_roads():
    # Угорі — MQTT: вузол шле візитівку лише до Home Assistant.
    # Унизу — Matter: вузол каже «я термостат», стандарт розгалужує до всіх.
    W, H = 740, 470
    p = []

    node_x = 80

    # ================= ВЕРХ: дорога MQTT =================
    ny = 110
    p.append(text(200, 34, "Дорога MQTT: своя візитівка — одній системі",
                  size=15, color=NEG, bold=True))
    p.append(circle(node_x, ny, 36, fill="#eafaf0", stroke=FIELD, sw=2.2))
    p.append(mtext(node_x, ny - 4, ["ВУЗОЛ", "термостат"], size=11, color=FIELD, bold=True))

    # візитівка
    p.append(fitbox(node_x + 60, ny - 18, 150, 36,
                    "докладна JSON-візитівка", size=11, fill=FILL, stroke=NEG))
    p.append(arrow(node_x + 36, ny, node_x + 60, ny, color=NEG, sw=2))

    # тільки Home Assistant
    ha_x = 560
    p.append(arrow(node_x + 210, ny, ha_x - 70, ny, color=NEG, sw=2))
    p.append(rect(ha_x - 70, ny - 26, 150, 52, fill="#eaf0fd", stroke=NEG, sw=2, rx=8))
    p.append(text(ha_x + 5, ny + 4, "Home Assistant", size=13, color=NEG, bold=True))

    # інші системи — недосяжні
    p.append(fitbox(ha_x - 70, ny + 44, 68, 26, "Apple", size=11,
                    fill="#ffffff", stroke="#cccccc"))
    p.append(fitbox(ha_x + 12, ny + 44, 68, 26, "Google", size=11,
                    fill="#ffffff", stroke="#cccccc"))
    p.append(text(ha_x + 5, ny + 92, "інші не бачать — чужа мова", size=11,
                  color=MUTED, italic=True))

    # роздільник
    p.append(line(40, 250, W - 40, 250, color="#dddddd", sw=1))

    # ================= НИЗ: дорога Matter =================
    my = 340
    p.append(text(200, 288, "Дорога Matter: спільна мова — усім системам одразу",
                  size=15, color=FIELD, bold=True))
    p.append(circle(node_x, my, 36, fill="#eafaf0", stroke=FIELD, sw=2.2))
    p.append(mtext(node_x, my - 4, ["ВУЗОЛ", "термостат"], size=11, color=FIELD, bold=True))

    # коротке «я термостат»
    p.append(fitbox(node_x + 58, my - 15, 116, 30, "«я термостат»", size=12,
                    fill="#eafaf0", stroke=FIELD))
    p.append(arrow(node_x + 36, my, node_x + 58, my, color=FIELD, sw=2))

    # шар стандарту Matter
    std_x = 330
    p.append(rect(std_x, my - 44, 104, 88, fill="#fff7e6", stroke="#b8860b", sw=2.2, rx=8))
    p.append(mtext(std_x + 52, my - 10, ["стандарт", "Matter"], size=12,
                   color="#8a6d00", bold=True))
    p.append(text(std_x + 52, my + 26, "типи наперед", size=10, color="#8a6d00"))
    p.append(arrow(node_x + 174, my, std_x, my, color=FIELD, sw=2))

    # розгалуження до всіх систем
    sys_x = 560
    targets = [("Apple", my - 66), ("Google", my - 22),
               ("Amazon", my + 22), ("Home Assistant", my + 66)]
    for name, ty in targets:
        p.append(arrow(std_x + 104, my, sys_x - 4, ty, color=FIELD, sw=1.8))
        w = 150 if name == "Home Assistant" else 92
        p.append(rect(sys_x, ty - 15, w, 30, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=6))
        p.append(text(sys_x + w / 2, ty + 4, name, size=11, color=NEG, bold=True))

    render(os.path.join(IMG, 'two-roads.svg'), W, H, *p,
           title="Дві дороги інтеграції: візитівка для однієї системи проти спільної мови для всіх")


def matter_timeline():
    # Три віхи, які легко сплутати: консорціум (2019) → бренд (2021) → стандарт (2022).
    # Ліворуч — зоопарк несумісних систем, що штовхнув до злиття.
    W, H = 760, 430
    p = []

    p.append(text(W / 2, 34, "Від зоопарку систем до одного стандарту", size=16,
                  color=INK, bold=True))

    # --- ліворуч: чотири несумісні острови до 2019 ---
    islands = [("Alexa", 92, NEG), ("HomeKit", 150, POS),
               ("Google", 208, FIELD), ("SmartThings", 266, "#8a6d00")]
    p.append(text(150, 70, "до 2019: острови-екосистеми", size=12,
                  color=MUTED, italic=True))
    for name, iy, col in islands:
        p.append(rect(64, iy - 15, 172, 30, fill="#ffffff", stroke=col, sw=1.8, rx=6))
        p.append(text(150, iy + 4, name, size=12, color=col, bold=True))
    # хрест-несумісність між островами
    p.append(text(150, 300, "свій хаб · своя мова · не бачать одне одного",
                  size=10, color=MUTED))

    # --- вісь часу праворуч ---
    ax = 470
    top, bot = 92, 300
    p.append(line(ax, top, ax, bot, color=INK, sw=2.5))
    p.append(arrow(150, 200, ax - 96, 200, color=MUTED, sw=1.6))
    p.append(text((150 + ax - 96) / 2, 190, "втома від воєн", size=10,
                  color=MUTED, italic=True))

    milestones = [
        (top,        "18 груд. 2019", "Project CHIP",
         "Amazon · Apple · Google · Zigbee-альянс", NEG),
        ((top + bot) / 2, "11 трав. 2021", "перейм. на Matter",
         "Zigbee-альянс → CSA", FIELD),
        (bot,        "4 жовт. 2022", "специфікація 1.0",
         "≈280+ компаній · сертифікація", POS),
    ]
    for my, date, headline, sub, col in milestones:
        p.append(circle(ax, my, 9, fill=col, stroke="#ffffff", sw=2.5))
        p.append(text(ax + 22, my - 8, date, size=12, color=col, bold=True,
                      anchor="start"))
        p.append(text(ax + 22, my + 9, headline, size=13, color=INK, bold=True,
                      anchor="start"))
        p.append(text(ax + 22, my + 26, sub, size=10, color=MUTED, anchor="start"))

    # підпис-розрізнення внизу
    p.append(fitbox(40, 350, 680, 44,
                    "консорціум ≠ бренд ≠ опублікований стандарт — три різні події",
                    size=12, fill=FILL, stroke=MUTED))

    render(os.path.join(IMG, 'matter-timeline.svg'), W, H, *p,
           title="Хронологія Matter: консорціум 2019, бренд 2021, стандарт 2022")


def ha_timeline():
    # Часова смуга Home Assistant: від особистого скрипта під лампи Hue
    # до стандарту де-факто. Кожна віха несе одну думку — чому виріс.
    W, H = 760, 470
    p = []

    p.append(text(W / 2, 30, "Home Assistant: від скрипта під лампу до стандарту",
                  size=17, color=INK, bold=True))

    ax = 118          # вертикальна вісь-лінія
    top, bot = 82, 428
    p.append(line(ax, top, ax, bot, color=MUTED, sw=2.5))

    # (рік, підпис-віха, рядки-пояснення, колір крапки)
    events = [
        ("2012", "Особистий скрипт",
         ["Паулюс Схаутсен купує Philips Hue; у хабі — локальний",
          "API. Пише на Python скрипт, що вмикає лампи вдома."], FIELD),
        ("2013", "Перший коміт на GitHub",
         ["17 вересня — виклав Home Assistant у відкритий доступ,",
          "щоб код налаштовували без Python. Ліцензія Apache 2.0."], NEG),
        ("2018", "Nabu Casa — сталість",
         ["Компанія на добровільну підписку: гроші на розробку є,",
          "локальне ядро лишається безкоштовним і без чужої хмари."], MUTED),
        ("2024", "#1 проєкт на GitHub",
         ["~21 000 дописувачів за рік — вершина Octoverse.",
          "Open Home Foundation: «не продати, не купити»."], POS),
    ]

    n = len(events)
    ys = [top + 20 + i * (bot - top - 34) / (n - 1) for i in range(n)]
    for (yr, milestone, rows, col), y in zip(events, ys):
        p.append(circle(ax, y, 9, fill=col, stroke="#ffffff", sw=2.5))
        p.append(text(ax - 24, y + 5, yr, size=15, color=col, bold=True, anchor="end"))
        p.append(text(ax + 26, y - 14, milestone, size=14, color=INK,
                      bold=True, anchor="start"))
        for j, r in enumerate(rows):
            p.append(text(ax + 26, y + 6 + j * 17, r, size=11, color=MUTED,
                          anchor="start"))

    render(os.path.join(IMG, 'ha-timeline.svg'), W, H, *p, title=None)


def discovery_anatomy():
    # ДЕТАЛЬНА: дві речі, яких немає в базовій —
    # (1) розбір самого топіка config на сегменти;
    # (2) машина доступності: retain-візитівка + LWT-заповіт + birth-топік HA.
    W, H = 780, 560
    p = []

    p.append(text(W / 2, 30, "Анатомія автовиявлення: топік config і машина доступності",
                  size=16, color=INK, bold=True))

    # ---- ВЕРХ: розбір топіка на сегменти ----
    seg_y = 92
    p.append(text(W / 2, 64, "1. Розбір описового топіка на сегменти", size=13,
                  color=MUTED, bold=True))
    segs = [("homeassistant", "префікс:\nтут HA слухає", "#fff7e6", "#b8860b", 132),
            ("climate", "тип сутності", "#eafaf0", FIELD, 96),
            ("livingroom_th", "ід вузла", "#eaf0fd", NEG, 118),
            ("config", "«це опис,\nне значення»", "#fdecea", POS, 96)]
    x = 40
    for name, note, fill, col, w in segs:
        p.append(rect(x, seg_y, w, 40, fill=fill, stroke=col, sw=2, rx=6))
        p.append(text(x + w / 2, seg_y + 25, name, size=12, color=col, bold=True))
        p.append(mtext(x + w / 2, seg_y + 62, note.split("\n"), size=10, color=MUTED))
        if x > 40:
            p.append(text(x - 12, seg_y + 25, "/", size=18, color=INK, bold=True))
        x += w + 24

    p.append(line(40, 172, W - 40, 172, color="#dddddd", sw=1))

    # ---- НИЗ: машина доступності ----
    p.append(text(W / 2, 200, "2. Три топіки тримають картку живою", size=13,
                  color=MUTED, bold=True))

    # вузол
    nx, ny = 92, 300
    p.append(circle(nx, ny, 40, fill="#eafaf0", stroke=FIELD, sw=2.2))
    p.append(mtext(nx, ny - 4, ["ВУЗОЛ", "термостат"], size=11, color=FIELD, bold=True))

    # брокер посередині
    bx, by = 380, 300
    p.append(rect(bx - 80, by - 96, 160, 192, fill="#eaf0fd", stroke=NEG, sw=2, rx=10))
    p.append(text(bx, by - 74, "БРОКЕР MQTT", size=13, color=NEG, bold=True))
    # три топіки в брокері
    rows = [
        (by - 44, "…/config", "retain=1", "притримано назавжди", "#fff7e6", "#b8860b"),
        (by,      "…/status", "LWT / birth", "online ⇄ offline", "#eafaf0", FIELD),
        (by + 46, "…/state",  "qos=1",       "число тече", "#f4f6f8", MUTED),
    ]
    for ry, topic, flag, note, fill, col in rows:
        p.append(rect(bx - 68, ry - 15, 136, 30, fill=fill, stroke=col, sw=1.6, rx=5))
        p.append(text(bx, ry - 1, topic, size=11, color=col, bold=True))
        p.append(text(bx, ry + 12, flag, size=9, color=MUTED))

    # стрілки вузол -> брокер
    p.append(arrow(nx + 40, ny - 40, bx - 80, by - 44, color=FIELD, sw=1.8))
    p.append(arrow(nx + 40, ny, bx - 80, by, color=FIELD, sw=1.8))
    p.append(arrow(nx + 40, ny + 40, bx - 80, by + 46, color=FIELD, sw=1.8))

    # HA праворуч
    hx, hy = 664, 300
    p.append(rect(hx - 64, hy - 60, 128, 120, fill="#eaf0fd", stroke=NEG, sw=2, rx=10))
    p.append(mtext(hx, hy - 30, ["Home", "Assistant"], size=13, color=NEG, bold=True))
    p.append(text(hx, hy + 12, "будує картку", size=10, color=MUTED))
    p.append(text(hx, hy + 30, "стежить за", size=10, color=MUTED))
    p.append(text(hx, hy + 45, "availability", size=10, color=MUTED))
    # брокер -> HA
    p.append(arrow(bx + 80, by - 20, hx - 64, hy - 20, color=NEG, sw=1.8))
    # birth: HA -> брокер (зворотний, пунктир)
    p.append(line(hx - 64, hy + 40, bx + 80, by + 70, color=POS, sw=1.6, dash="5 4"))
    p.append(text((hx + bx) / 2 + 6, by + 92, "homeassistant/status: HA кричить «online» —",
                  size=10, color=POS, italic=True))
    p.append(text((hx + bx) / 2 + 6, by + 106, "вузол переоголошується", size=10,
                  color=POS, italic=True))

    render(os.path.join(IMG, 'discovery-anatomy.svg'), W, H, *p,
           title=None)


def matter_data_model():
    # ДЕТАЛЬНА: «зміст живе в моделі» зроблено конкретним —
    # дерево node→endpoint→cluster→attribute з реальними ID і кодуванням 0.01°C.
    W, H = 780, 540
    p = []

    p.append(text(W / 2, 30, "Модель даних Matter: де насправді живе «зміст»",
                  size=16, color=INK, bold=True))

    # NODE
    nx = W / 2
    p.append(rect(nx - 120, 52, 240, 40, fill="#fff7e6", stroke="#b8860b", sw=2.2, rx=8))
    p.append(text(nx, 77, "ВУЗОЛ (node) — один пристрій", size=13, color="#8a6d00", bold=True))

    # два endpoint
    ep0x, ep1x = 210, 570
    epy = 150
    # endpoint 0
    p.append(rect(ep0x - 130, epy - 26, 260, 52, fill="#eaf0fd", stroke=NEG, sw=2, rx=8))
    p.append(text(ep0x, epy - 6, "endpoint 0 — корінь", size=12, color=NEG, bold=True))
    p.append(text(ep0x, epy + 12, "службові кластери: діагностика, OTA", size=10, color=MUTED))
    # endpoint 1
    p.append(rect(ep1x - 130, epy - 26, 260, 52, fill="#eafaf0", stroke=FIELD, sw=2, rx=8))
    p.append(text(ep1x, epy - 6, "endpoint 1 — термостат", size=12, color=FIELD, bold=True))
    p.append(text(ep1x, epy + 12, "device type 0x0301", size=10, color=MUTED))
    # лінії node->endpoints
    p.append(line(nx, 92, ep0x, epy - 26, color=MUTED, sw=1.5))
    p.append(line(nx, 92, ep1x, epy - 26, color=MUTED, sw=1.5))

    # кластери під endpoint 1 (ID — всередині рамки другим рядком, щоб лінія
    # до атрибутів не перетинала жодного напису)
    cy = 250
    clusters = [
        (430, "Thermostat", "cluster 0x0201", "#eafaf0", FIELD),
        (640, "Temp. Measurement", "cluster 0x0402", "#fff7e6", "#b8860b"),
    ]
    for cx, name, cid, fill, col in clusters:
        p.append(rect(cx - 92, cy - 26, 184, 54, fill=fill, stroke=col, sw=1.8, rx=6))
        p.append(text(cx, cy - 6, name, size=12, color=col, bold=True))
        p.append(text(cx, cy + 14, cid, size=10.5, color=MUTED))
        p.append(line(ep1x, epy + 26, cx, cy - 26, color=MUTED, sw=1.4))

    # атрибути під кластерами
    ay = 372
    # під Thermostat
    thermo_attrs = [
        "LocalTemperature 0x0000",
        "OccupiedHeatingSetpoint 0x0012",
        "SystemMode 0x001C",
    ]
    for i, a in enumerate(thermo_attrs):
        yy = ay + i * 30
        p.append(rect(300, yy - 13, 260, 26, fill="#ffffff", stroke=FIELD, sw=1.4, rx=5))
        p.append(text(430, yy + 4, a, size=11, color=INK))
    p.append(line(430, cy + 28, 430, ay - 13, color=MUTED, sw=1.3))

    # під Temperature Measurement — з кодуванням
    meas_attrs = [
        "MeasuredValue 0x0000",
        "int16 · крок 0.01 °C",
        "2100 → 21.00 °C",
    ]
    yy0 = ay
    for i, a in enumerate(meas_attrs):
        yy = yy0 + i * 30
        stroke = "#b8860b" if i == 0 else "#dddddd"
        fill = "#ffffff" if i == 0 else "#fbf7ee"
        p.append(rect(566, yy - 13, 200, 26, fill=fill, stroke=stroke, sw=1.4, rx=5))
        col = INK if i == 0 else "#8a6d00"
        p.append(text(666, yy + 4, a, size=11, color=col,
                      bold=(i == 2)))
    p.append(line(640, cy + 28, 666, yy0 - 13, color=MUTED, sw=1.3))

    # підсумковий рядок (два рядки — щоб напис лишався великим)
    p.append(fitbox(40, 488, W - 80, 44,
                    ["ID кластера й атрибута однакові в усіх виробників світу —",
                     "тому системі не потрібна візитівка: «термостат» вона вже знає напам'ять"],
                    size=12, fill=FILL, stroke=MUTED))

    render(os.path.join(IMG, 'matter-data-model.svg'), W, H, *p, title=None)


def commissioning_crypto():
    # ДЕТАЛЬНА: чотири фази приєднання з криптографією й тим,
    # ЯКИМ каналом що летить (BLE проти робочої мережі).
    W, H = 800, 430
    p = []

    p.append(text(W / 2, 28, "Приєднання Matter: чотири фази й що в кожній летить",
                  size=16, color=INK, bold=True))

    # підсумок — ЗВЕРХУ, щоб вертикальні лінії-канали внизу його не перетинали
    p.append(fitbox(60, 46, W - 120, 44,
                    ["секрет (passcode) працює лише у фазі 2 і НІКОЛИ не йде дротом:",
                     "обидва рахують спільний ключ, знаючи його; далі — операційні сертифікати"],
                    size=12, fill=FILL, stroke=MUTED))

    phases = [
        (150, "1. Виявлення", ["скан QR-коду", "→ discriminator", "12 біт (0..4095)"], "#eaf0fd", NEG, "ble"),
        (330, "2. PASE", ["SPAKE2+ з passcode", "27 біт (1..99999998)", "на пристрої — лише", "verifier, не сам код"], "#fdecea", POS, "ble"),
        (510, "3. Атестація", ["пристрій показує DAC", "ланцюг DAC←PAI←PAA", "«я справжній,", "не підробка»"], "#fff7e6", "#b8860b", "ble"),
        (690, "4. CASE", ["видано NOC у фабрику", "fabric-id + node-id", "далі — робоча", "мережа, не BLE"], "#eafaf0", FIELD, "op"),
    ]
    box_top, box_h = 116, 150
    # стрілки між фазами (малюємо ПЕРШИМИ, щоб рамки лягли поверх)
    for i in range(len(phases) - 1):
        x1 = phases[i][0] + 84
        x2 = phases[i + 1][0] - 84
        p.append(arrow(x1, box_top + box_h / 2, x2, box_top + box_h / 2,
                       color=INK, sw=1.8))
    for cx, title, rows, fill, col, chan in phases:
        p.append(rect(cx - 84, box_top, 168, box_h, fill=fill, stroke=col, sw=2, rx=8))
        p.append(text(cx, box_top + 26, title, size=13, color=col, bold=True))
        for i, r in enumerate(rows):
            p.append(text(cx, box_top + 50 + i * 20, r, size=10.5, color=INK))

    # дві доріжки-канали — ВНИЗУ, під рамками
    ble_y, op_y = 336, 380
    p.append(line(60, ble_y - 16, W - 40, ble_y - 16, color="#dddddd", sw=1, dash="3 3"))
    p.append(text(70, ble_y + 4, "канал BLE", size=11, color=NEG, bold=True, anchor="start"))
    p.append(text(70, op_y + 4, "робоча мережа", size=11, color=FIELD, bold=True, anchor="start"))
    for cx, title, rows, fill, col, chan in phases:
        cyl = ble_y if chan == "ble" else op_y
        ccol = NEG if chan == "ble" else FIELD
        p.append(line(cx, box_top + box_h, cx, cyl - 8, color=ccol, sw=1.4, dash="2 3"))
        p.append(circle(cx, cyl - 2, 6, fill=ccol, stroke="#ffffff", sw=1.5))

    render(os.path.join(IMG, 'commissioning-crypto.svg'), W, H, *p, title=None)


def shared_device():
    # Три окремі discovery-повідомлення (температура, режим, заряд), кожне зі
    # СВОЇМ uniq_id і stat_t, але зі СПІЛЬНИМ блоком dev.ids — і всі троє
    # збираються під ОДНІЄЮ карткою пристрою в панелі.
    W, H = 760, 470
    p = []

    p.append(text(W / 2, 34, "Спільний dev.ids збирає сутності під одну картку",
                  size=16, color=INK, bold=True))

    # --- три повідомлення зліва ---
    ents = [
        (96,  "sensor",  "th_livingroom_temp", "…/temp",    "🌡", "температура"),
        (216, "select",  "th_livingroom_mode", "…/mode",    "⚙",  "режим"),
        (336, "sensor",  "th_livingroom_batt", "…/batt",    "🔋", "заряд"),
    ]
    bx, bw, bh = 40, 250, 96
    for cy, etype, uid, stt, icon, label in ents:
        p.append(rect(bx, cy, bw, bh, fill=FILL, stroke=MUTED, sw=1.5, rx=8))
        p.append(text(bx + 14, cy + 24, icon + "  " + label, size=13, color=INK,
                      bold=True, anchor="start"))
        p.append(text(bx + 14, cy + 46, '"uniq_id": "' + uid + '"', size=10.5,
                      color=NEG, anchor="start"))
        p.append(text(bx + 14, cy + 64, '"stat_t":  "' + stt + '"', size=10.5,
                      color=INK, anchor="start"))
        p.append(text(bx + 14, cy + 84, '"dev": { "ids": "th_livingroom" }',
                      size=10.5, color=FIELD, anchor="start"))

    # спільний ключ — підкреслимо зеленим, що dev.ids однаковий у всіх трьох
    keyx = bx + bw + 34
    p.append(line(keyx - 20, ents[0][0] + 84, keyx - 20, ents[2][0] + 84,
                  color=FIELD, sw=2))
    kb, kw, kh = textbox(keyx + 70, H / 2, ['спільний', 'dev.ids =', '"th_livingroom"'],
                         size=12, bold=True, fill="#eafaf0", stroke=FIELD, min_w=150)
    p.append(kb)

    # стрілки від кожного повідомлення до картки
    cardx = 560
    for cy, *_ in ents:
        p.append(arrow(keyx + 148, H / 2, cardx - 6, cy + bh / 2 if cy != 216 else H / 2,
                       color=FIELD, sw=1.6))

    # --- одна картка пристрою праворуч ---
    p.append(rect(cardx, 120, 168, 250, fill="#eafaf0", stroke=FIELD, sw=2.2, rx=12))
    p.append(text(cardx + 84, 150, "Термостат", size=14, color=INK, bold=True))
    p.append(text(cardx + 84, 170, "вітальні", size=14, color=INK, bold=True))
    p.append(line(cardx + 16, 184, cardx + 152, 184, color=MUTED, sw=1))
    rows = [("🌡", "21.4 °C"), ("⚙", "нагрів"), ("🔋", "82 %")]
    for i, (icon, val) in enumerate(rows):
        ry = 214 + i * 44
        p.append(text(cardx + 32, ry, icon, size=18))
        p.append(text(cardx + 150, ry, val, size=15, color=INK, bold=True, anchor="end"))
    p.append(text(cardx + 84, 356, "одна картка · три сутності", size=10.5, color=MUTED))

    render(os.path.join(IMG, 'shared-device.svg'), W, H, *p, title=None)


def silent_typos():
    # Чотири одруки, що ламають розбір МОВЧКИ: зайва кома, неекранована лапка,
    # неунікальний uniq_id, забутий availability. Для кожної — що видно в коді
    # й що станеться в панелі. Дві колонки: «одрук» → «наслідок».
    W, H = 780, 520
    p = []
    p.append(text(W / 2, 34, "Чотири мовчазні вбивці розбору", size=16,
                  color=INK, bold=True))
    p.append(text(W / 2, 56, "жодної помилки в лозі — картка просто не постає",
                  size=12, color=MUTED))

    col1x, col1w = 40, 380
    col2x, col2w = 448, 292
    p.append(text(col1x + col1w / 2, 84, "ОДРУК У РЯДКУ", size=12, color=POS, bold=True))
    p.append(text(col2x + col2w / 2, 84, "ЩО СТАНЕТЬСЯ", size=12, color=NEG, bold=True))

    cases = [
        ('"max_temp":35,}',
         "зайва кома перед }",
         "весь JSON недійсний —", "картка не постає зовсім"),
        ('"name":"Термостат "вітальні""',
         "неекранована лапка",
         "рядок обірвано на 2-й лапці —", "розбір падає, картки нема"),
        ('"uniq_id":"thermostat"',
         "той самий у двох вузлів",
         "другий вузол зливається", "з першим — одна картка на двох"),
        ('(немає avty_t)',
         "забутий availability",
         "картка «завжди в мережі» —", "мертвий вузол показує старе"),
    ]
    top, rh, gap = 104, 88, 12
    for i, (code, badlabel, res1, res2) in enumerate(cases):
        y = top + i * (rh + gap)
        # ліва: код-одрук
        p.append(rect(col1x, y, col1w, rh, fill="#fdecea", stroke=POS, sw=1.8, rx=8))
        p.append(fitbox(col1x + 12, y + 12, col1w - 24, 30, code, size=13,
                        fill="#ffffff", stroke=MUTED))
        p.append(text(col1x + 12, y + 72, "✗ " + badlabel, size=12, color=POS,
                      bold=True, anchor="start"))
        # стрілка
        p.append(arrow(col1x + col1w + 6, y + rh / 2, col2x - 6, y + rh / 2,
                       color=INK, sw=1.6))
        # права: наслідок
        p.append(rect(col2x, y, col2w, rh, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=8))
        p.append(text(col2x + col2w / 2, y + 36, res1, size=11.5, color=INK))
        p.append(text(col2x + col2w / 2, y + 58, res2, size=11.5, color=INK))

    render(os.path.join(IMG, 'silent-typos.svg'), W, H, *p, title=None)


def spake2_exchange():
    # Дві сторони виводять СПІЛЬНИЙ ключ із passcode, обмінявшись лише
    # точками X, Y на кривій; підслуховувач бачить X, Y — і сліпий.
    W, H = 820, 470
    p = []

    p.append(text(W / 2, 26, "SPAKE2+: спільний ключ із пароля, самого пароля в ефірі немає",
                  size=15, color=INK, bold=True))

    # координати колонок
    lx, rx = 150, 670          # центри «телефона» й «пристрою»
    top = 60

    # заголовки сторін
    p.append(fitbox(lx - 118, top, 236, 34, "ТЕЛЕФОН (prover) — знає passcode",
                    size=12, fill="#eaf0fd", stroke=NEG, bold=True))
    p.append(fitbox(rx - 118, top, 236, 34, "ПРИСТРІЙ (verifier) — знає w0, L",
                    size=12, fill="#eafaf0", stroke=FIELD, bold=True))

    # що кожен має на старті
    p.append(text(lx, top + 62, "w0, w1  ←  PBKDF(passcode)", size=12, color=INK))
    p.append(text(rx, top + 62, "w0,  L = w1·P", size=12, color=INK))
    p.append(text(rx, top + 80, "(w1 і passcode НЕ зберігає)", size=10, color=MUTED))

    # секретні скаляри
    p.append(text(lx, top + 104, "тягне випадкове x", size=11.5, color=NEG))
    p.append(text(rx, top + 104, "тягне випадкове y", size=11.5, color=FIELD))

    # обчислені точки для обміну
    by = top + 132
    lb = fitbox(lx - 100, by, 200, 34, "X = x·P + w0·M", size=13, fill=FILL, stroke=NEG, bold=True)
    rb = fitbox(rx - 100, by, 200, 34, "Y = y·P + w0·N", size=13, fill=FILL, stroke=FIELD, bold=True)
    p.append(lb); p.append(rb)

    # стрілки обміну через ефір
    mid_y1, mid_y2 = by + 8, by + 26
    p.append(arrow(lx + 104, mid_y1, rx - 104, mid_y1, color=NEG, sw=1.8))     # X →
    p.append(arrow(rx - 104, mid_y2, lx + 104, mid_y2, color=FIELD, sw=1.8))   # ← Y
    p.append(text(W / 2, by - 6, "публічний обмін точками", size=10.5, color=MUTED))

    # спільний секрет — кожен виводить СВОЄЮ формулою, а виходить те саме
    sy = by + 70
    p.append(fitbox(lx - 118, sy, 236, 52,
                    ["Z = h·x·(Y − w0·N)", "V = h·w1·(Y − w0·N)"],
                    size=12, fill="#eaf0fd", stroke=NEG))
    p.append(fitbox(rx - 118, sy, 236, 52,
                    ["Z = h·y·(X − w0·M)", "V = h·y·L"],
                    size=12, fill="#eafaf0", stroke=FIELD))

    # знак рівності між двома результатами
    p.append(text(W / 2, sy + 20, "=", size=26, color=INK, bold=True))
    p.append(text(W / 2, sy + 42, "ті самі Z, V", size=10.5, color=MUTED))

    # спільний ключ
    ky = sy + 78
    p.append(fitbox(W / 2 - 190, ky, 380, 40,
                    "K = Hash(транскрипт із Z, V) → ключ каналу + підтвердження",
                    size=12, fill="#fff7e6", stroke="#b8860b", bold=True))

    # --- підслуховувач унизу ---
    ey = ky + 66
    p.append(line(40, ey - 12, W - 40, ey - 12, color="#dddddd", sw=1, dash="4 4"))
    p.append(circle(90, ey + 20, 22, fill="#fdecea", stroke=POS, sw=2))
    p.append(text(90, ey + 26, "👂", size=20))
    p.append(text(150, ey + 8, "ПІДСЛУХОВУВАЧ бачить лише:", size=12, color=POS,
                  bold=True, anchor="start"))
    p.append(text(150, ey + 30, "точки X і Y на кривій P-256 — і все.", size=11.5,
                  color=INK, anchor="start"))
    p.append(text(150, ey + 48,
                  "Щоб добути passcode, треба обернути P-256 (задача дискретного логарифма) — не по кишені.",
                  size=10.5, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'spake2-exchange.svg'), W, H, *p, title=None)


def endpoint_build():
    # PROJ: пристрій складено з готових цеглинок-кластерів.
    # Ліворуч — те, що SDK робить САМ (endpoint 0, Descriptor).
    # Праворуч — те, що складаєш ТИ: endpoint 1 = дві цеглинки-кластери.
    W, H = 800, 470
    p = []

    p.append(text(W / 2, 30, "Термостат складено з готових цеглинок-кластерів",
                  size=16, color=INK, bold=True))

    # NODE згори
    nx = W / 2
    p.append(rect(nx - 160, 50, 320, 38, fill="#fff7e6", stroke="#b8860b", sw=2.2, rx=8))
    p.append(text(nx, 74, "node — увесь пристрій, одна прошивка", size=12,
                  color="#8a6d00", bold=True))

    # endpoint 0 — SDK робить сам (ліворуч, приглушено)
    e0x = 190
    p.append(rect(e0x - 128, 140, 256, 96, fill="#f4f6f8", stroke=MUTED, sw=1.8, rx=8))
    p.append(text(e0x, 164, "endpoint 0 — корінь", size=12, color=MUTED, bold=True))
    p.append(text(e0x, 186, "діагностика · OTA · Basic Info", size=10, color=MUTED))
    p.append(fitbox(e0x - 112, 202, 224, 24, "SDK створює САМ — не чіпаєш",
                    size=10.5, fill="#ffffff", stroke=MUTED))
    p.append(line(nx, 88, e0x, 140, color=MUTED, sw=1.4, dash="4 3"))

    # endpoint 1 — ти складаєш (праворуч, яскраво)
    e1x = 580
    p.append(rect(e1x - 168, 128, 336, 254, fill="#eafaf0", stroke=FIELD, sw=2.2, rx=10))
    p.append(text(e1x, 152, "endpoint 1 — це складаєш ТИ", size=13, color=FIELD, bold=True))
    p.append(text(e1x, 172, "device type 0x0301 (термостат)", size=10.5, color="#1a7a44"))
    p.append(line(nx, 88, e1x, 128, color=FIELD, sw=1.6))

    # дві цеглинки-кластери всередині endpoint 1
    bricks = [
        (e1x - 84, 194, "Thermostat", "0x0201", "#eaf0fd", NEG),
        (e1x + 84, 194, "Temp. Meas.", "0x0402", "#fdecea", POS),
    ]
    for bx, by, name, cid, fill, col in bricks:
        p.append(rect(bx - 72, by, 144, 44, fill=fill, stroke=col, sw=2, rx=7))
        p.append(text(bx, by + 19, name, size=11.5, color=col, bold=True))
        p.append(text(bx, by + 35, "cluster " + cid, size=9.5, color=MUTED))
    # атрибути-підписи під цеглинками, кожен у своєму стовпці з ЗАПАСОМ
    ta = ["LocalTemperature  0x0000", "OccupiedHeatingSetpoint  0x0012",
          "SystemMode  0x001C"]
    for i, a in enumerate(ta):
        yy = 260 + i * 24
        p.append(fitbox(e1x - 164, yy, 190, 21, a, size=9.5,
                        fill="#ffffff", stroke=NEG))
    ma = ["MeasuredValue  0x0000", "int16 · крок 0.01 °C", "2100 → 21.00 °C"]
    for i, a in enumerate(ma):
        yy = 260 + i * 24
        p.append(fitbox(e1x + 34, yy, 130, 21, a, size=9,
                        fill="#ffffff" if i == 0 else "#fdf4f2",
                        stroke=POS if i == 0 else "#e8b4ac"))

    # Descriptor — SDK збирає сам, знизу endpoint 1
    p.append(fitbox(e1x - 168, 348, 336, 26,
                    "Descriptor 0x001D — SDK збирає СПИСКИ кластерів сам",
                    size=10.5, fill="#fff7e6", stroke="#b8860b"))

    # підсумок унизу
    p.append(fitbox(40, 404, W - 80, 40,
                    ["ти лише «клацаєш» дві цеглинки на endpoint 1 — а endpoint 0,",
                     "Descriptor і паспорт вузла SDK збирає сам; звідси й уся стислість коду"],
                    size=12, fill=FILL, stroke=MUTED))

    render(os.path.join(IMG, 'endpoint-build.svg'), W, H, *p, title=None)


def attr_callback_flow():
    # PROJ: дві протилежні дороги атрибута й де стоїть твій код.
    # Вгору (давач → атрибут): МИ штовхаємо attribute::update, множимо на 100.
    # Вниз (контролер → нам): callback PRE_UPDATE, ділимо на 100, крутимо реле.
    W, H = 820, 470
    p = []

    p.append(text(W / 2, 30, "Дві дороги атрибута: хто штовхає значення і де твій код",
                  size=16, color=INK, bold=True))

    hw_x = 120
    md_x = 410
    ctl_x = 700

    # МОДЕЛЬ посередині — стовпчик атрибутів
    p.append(rect(md_x - 104, 76, 208, 300, fill="#eafaf0", stroke=FIELD, sw=2, rx=10))
    p.append(text(md_x, 98, "endpoint 1  (модель даних)", size=11.5, color=FIELD, bold=True))
    attrs = [
        (128, "MeasuredValue", "Temp.Meas 0x0402", NEG),
        (196, "LocalTemperature", "Thermostat 0x0201", NEG),
        (292, "OccupiedHeatingSetpoint", "Thermostat 0x0201", POS),
    ]
    for ay, name, sub, col in attrs:
        p.append(rect(md_x - 92, ay, 184, 42, fill="#ffffff", stroke=col, sw=1.6, rx=6))
        p.append(fitbox(md_x - 88, ay + 4, 176, 18, name, size=10, fill="#ffffff",
                        stroke="none", color=INK, bold=True))
        p.append(text(md_x, ay + 34, sub, size=9, color=MUTED))

    # ЗАЛІЗО вузла ліворуч
    p.append(rect(hw_x - 78, 150, 156, 96, fill="#eaf0fd", stroke=NEG, sw=2, rx=8))
    p.append(mtext(hw_x, 180, ["давач", "температури"], size=12, color=NEG, bold=True))
    p.append(text(hw_x, 226, "21.00 °C", size=13, color=INK, bold=True))

    p.append(rect(hw_x - 78, 286, 156, 90, fill="#fdecea", stroke=POS, sw=2, rx=8))
    p.append(mtext(hw_x, 314, ["реле", "нагрівача"], size=12, color=POS, bold=True))
    p.append(text(hw_x, 358, "гріти / стоп", size=11, color=INK))

    # КОНТРОЛЕР праворуч
    p.append(rect(ctl_x - 78, 238, 156, 100, fill="#eaf0fd", stroke=NEG, sw=2, rx=8))
    p.append(mtext(ctl_x, 268, ["контролер", "телефон / HA"], size=12, color=NEG, bold=True))
    p.append(text(ctl_x, 308, "«став 22 °C»", size=11, color=INK, bold=True))

    # ── ДОРОГА ВГОРУ: давач → attribute::update (МИ штовхаємо) ──
    p.append(arrow(hw_x + 78, 178, md_x - 92, 150, color=NEG, sw=2))
    bb, bw, bh = textbox((hw_x + md_x) / 2 - 6, 118,
                         ["ТИ: attribute::update(...)", "×100 → 2100"],
                         size=10.5, bold=True, fill="#eaf0fd", stroke=NEG, min_w=180)
    p.append(bb)

    # ── ДОРОГА ВНИЗ: контролер → callback (SDK кличе ТЕБЕ) ──
    p.append(arrow(ctl_x - 78, 300, md_x + 92, 314, color=POS, sw=2))
    p.append(arrow(md_x - 92, 320, hw_x + 78, 332, color=POS, sw=2))
    cb, cw, ch = textbox(W / 2, 420,
                         ["SDK кличе ТВІЙ callback (тип PRE_UPDATE):",
                          "÷100 → 22.0 °C → крутиш реле, потім вертаєш ESP_OK"],
                         size=10.5, bold=True, fill="#fdecea", stroke=POS, min_w=360)
    p.append(cb)

    render(os.path.join(IMG, 'attr-callback-flow.svg'), W, H, *p, title=None)


if __name__ == '__main__':
    data_vs_meaning()
    two_roads()
    matter_timeline()
    ha_timeline()
    discovery_anatomy()
    matter_data_model()
    commissioning_crypto()
    shared_device()
    silent_typos()
    spake2_exchange()
    endpoint_build()
    attr_callback_flow()
    print("ok")

# -*- coding: utf-8 -*-
"""Фігури до теми «Захист від зникнення живлення: brown-out і рятування стану».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GREEN = FIELD        # норма / «добре»
RED   = POS          # небезпека / скидання
BLUE  = NEG          # попередження
AMBER = "#b9770e"    # сіра (жовта) зона


# ── 1. Три зони напруги живлення ─────────────────────────────────────────────
def fig_voltage_zones():
    W, H = 940, 460
    f = [text(W / 2, 32, "Три зони напруги живлення: де чіп служить, де шкодить, де мовчить",
              size=18, bold=True)]
    f.append(text(W / 2, 55, "Небезпечна не мертва зона, а сіра: чіп ще ввімкнений, "
                  "але рахує неправильно", size=12.5, color=MUTED, italic=True))

    # вертикальна вісь напруги: смуги зон
    bx, bw = 250, 360
    top = 80
    # зони (зверху вниз): зелена (норма), жовта (сіра), сіра (мертва)
    z_green = (top, 150)          # y, h
    z_amber = (top + 150, 95)
    z_dead  = (top + 245, 110)

    f.append(rect(bx, z_green[0], bw, z_green[1], fill="#eaf7ee", stroke=GREEN, sw=1.6, rx=0))
    f.append(rect(bx, z_amber[0], bw, z_amber[1], fill="#fff3d6", stroke=AMBER, sw=1.8, rx=0))
    f.append(rect(bx, z_dead[0],  bw, z_dead[1],  fill="#eceff2", stroke=MUTED, sw=1.6, rx=0))

    # підписи зон усередині
    f.append(text(bx + bw / 2, z_green[0] + 50, "ЗОНА НОРМИ", size=15, color=GREEN, bold=True))
    f.append(text(bx + bw / 2, z_green[0] + 78, "логіка коректна: пороги на місці,",
                  size=11.5, color=INK))
    f.append(text(bx + bw / 2, z_green[0] + 96, "такти стабільні, запис надійний",
                  size=11.5, color=INK))
    f.append(text(bx + bw / 2, z_green[0] + 120, "3.3 В  →  робочий діапазон", size=10.5, color=MUTED, italic=True))

    f.append(text(bx + bw / 2, z_amber[0] + 30, "СІРА ЗОНА — НЕБЕЗПЕЧНА", size=15, color=AMBER, bold=True))
    f.append(text(bx + bw / 2, z_amber[0] + 52, "пороги пливуть · такти затинаються",
                  size=11.5, color=INK))
    f.append(text(bx + bw / 2, z_amber[0] + 70, "запис у пам'ять може спотворитися",
                  size=11.5, color=INK))

    f.append(text(bx + bw / 2, z_dead[0] + 48, "МЕРТВА ЗОНА", size=15, color=MUTED, bold=True))
    f.append(text(bx + bw / 2, z_dead[0] + 72, "чіп просто не працює (безпечно)", size=11.5, color=INK))

    # вісь зі стрілкою вгору = напруга
    ax = bx - 40
    f.append(arrow(ax, z_dead[0] + z_dead[1], ax, top - 6, color=INK, sw=2))
    f.append(text(ax - 12, (top + z_dead[0] + z_dead[1]) / 2, "напруга живлення",
                  size=12, color=INK, anchor="middle"))
    # повернути підпис осі вертикально
    f[-1] = ('<text x="%.1f" y="%.1f" font-family="%s" font-size="12" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 %.1f %.1f)">напруга живлення</text>'
             % (ax - 14, (top + z_dead[0] + z_dead[1]) / 2, FONT, INK,
                ax - 14, (top + z_dead[0] + z_dead[1]) / 2))

    # межі праворуч
    f.append(line(bx + bw, z_green[1] + top, bx + bw + 70, z_green[1] + top, color=AMBER, sw=1.4, dash="4,3"))
    f.append(text(bx + bw + 74, z_green[1] + top - 6, "вхід у сіру зону", size=10.5,
                  color=AMBER, anchor="start", bold=True))
    f.append(line(bx + bw, z_amber[0] + z_amber[1], bx + bw + 70, z_amber[0] + z_amber[1],
                  color=MUTED, sw=1.4, dash="4,3"))
    f.append(text(bx + bw + 74, z_amber[0] + z_amber[1] - 6, "чіп гасне", size=10.5,
                  color=MUTED, anchor="start"))

    f.append(text(W / 2, 446, "Задача захисту — не дати пристрою лишатися в жовтій зоні «живим, але хворим».",
                  size=12, color=AMBER, bold=True))
    render(os.path.join(IMG, "voltage-zones.svg"), W, H, *f)


# ── 2. Два пороги: попередження + BOD, між ними вікно ─────────────────────────
def fig_two_thresholds():
    W, H = 960, 470
    f = [text(W / 2, 32, "Два рубежі: попередження вгорі, скидання внизу, вікно між ними",
              size=18, bold=True)]
    f.append(text(W / 2, 55, "Верхній поріг будить процесор рятуватися; нижній рубає чіп, "
                  "щоб дані не зіпсувалися", size=12.5, color=MUTED, italic=True))

    # осі
    ox, oy = 95, 90          # лівий верх області графіка
    gw, gh = 640, 290
    f.append(line(ox, oy, ox, oy + gh, color=INK, sw=1.6))            # вісь напруги
    f.append(line(ox, oy + gh, ox + gw, oy + gh, color=INK, sw=1.6))  # вісь часу
    f.append(text(ox + gw / 2, oy + gh + 34, "час →", size=12, color=INK))
    f.append(('<text x="%.1f" y="%.1f" font-family="%s" font-size="12" fill="%s" '
              'text-anchor="middle" transform="rotate(-90 %.1f %.1f)">напруга живлення</text>'
              % (ox - 34, oy + gh / 2, FONT, INK, ox - 34, oy + gh / 2)))

    # рівні
    y_nom  = oy + 35     # номінал
    y_warn = oy + 120    # верхній поріг (попередження)
    y_bod  = oy + 215    # нижній поріг (BOD)

    for y, lab, col in [(y_warn, "верхній поріг — ПОПЕРЕДЖЕННЯ", BLUE),
                        (y_bod,  "нижній поріг — BOD (скидання)", RED)]:
        f.append(line(ox, y, ox + gw, y, color=col, sw=1.4, dash="6,4"))
        f.append(text(ox + gw - 6, y - 7, lab, size=11.5, color=col, anchor="end", bold=True))

    # крива напруги: горизонталь на номіналі, потім спад
    x_fail = ox + 150        # мить «живлення зникло»
    x_warn = ox + 235        # перетин верхнього порога
    x_bod  = ox + 470        # перетин нижнього порога
    pts = [(ox, y_nom), (x_fail, y_nom), (x_warn, y_warn), (x_bod, y_bod), (ox + gw - 20, oy + gh - 8)]
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, INK))

    # позначки подій
    f.append(line(x_fail, y_nom, x_fail, oy + gh, color=MUTED, sw=1.1, dash="3,3"))
    f.append(text(x_fail, oy + gh + 18, "живлення зникло", size=10.5, color=MUTED))

    f.append(circle(x_warn, y_warn, 5, fill=BLUE, stroke=BLUE, sw=1))
    f.append(text(x_warn - 4, y_warn - 12, "переривання!", size=11, color=BLUE, anchor="middle", bold=True))

    f.append(circle(x_bod, y_bod, 5, fill=RED, stroke=RED, sw=1))
    f.append(text(x_bod + 4, y_bod - 12, "скидання чіпа", size=11, color=RED, anchor="middle", bold=True))

    # вікно реакції — заштрихована смуга між x_warn і x_bod
    f.append(rect(x_warn, y_warn, x_bod - x_warn, y_bod - y_warn, fill="#eef6ee", stroke=GREEN, sw=1.4, rx=0))
    f.append(text((x_warn + x_bod) / 2, (y_warn + y_bod) / 2 - 4, "ВІКНО РЕАКЦІЇ", size=12.5,
                  color=GREEN, bold=True))
    f.append(text((x_warn + x_bod) / 2, (y_warn + y_bod) / 2 + 14, "встигнути зберегти стан", size=10.5,
                  color=GREEN))

    # підпис «номінал»
    f.append(text(ox + 6, y_nom - 8, "номінал", size=10.5, color=MUTED, anchor="start"))

    f.append(text(W / 2, oy + gh + 70, "Ширину вікна задає розряд конденсаторів: "
                  "більша ємність і менший струм → ширше вікно.", size=12, color=INK))
    render(os.path.join(IMG, "two-thresholds.svg"), W, H, *f)


# ── 3. Часова шкала події зникнення живлення ─────────────────────────────────
def fig_power_fail_timeline():
    W, H = 980, 360
    f = [text(W / 2, 32, "Повний хід події: від попередження до відновлення при старті",
              size=18, bold=True)]
    f.append(text(W / 2, 55, "Кожен рубіж закриває свою дірку: попередження дає шанс, "
                  "FRAM встигає, BOD страхує, перевірка відсіює сміття",
                  size=12, color=MUTED, italic=True))

    # горизонтальна вісь часу
    ax0, ax1, ay = 70, 910, 130
    f.append(arrow(ax0, ay, ax1, ay, color=INK, sw=2))
    f.append(text(ax1, ay + 22, "час", size=12, color=INK, anchor="end"))

    # п'ять віх
    stages = [
        (150, "живлення\nзникло", MUTED, "напруга поповзла вниз"),
        (320, "ВЕРХНІЙ ПОРІГ\nпереривання", BLUE, "процесор прокинувся"),
        (500, "ВІКНО\nзапис у FRAM", GREEN, "глуши споживачів,\nзбережи стан + CRC"),
        (680, "НИЖНІЙ ПОРІГ\nскидання BOD", RED, "дані врятовано\nвід спотворення"),
        (855, "СТАРТ\nперевірка CRC", INK, "сума сходиться →\nвідновити; ні → скинути"),
    ]
    for x, top_lab, col, bot in stages:
        f.append(circle(x, ay, 8, fill=col, stroke=col, sw=1))
        # верхній підпис (над віссю)
        for i, ln in enumerate(top_lab.split("\n")):
            f.append(text(x, ay - 52 + i * 17, ln, size=12, color=col, bold=True))
        f.append(line(x, ay - 30, x, ay - 8, color=col, sw=1.1))
        # нижній підпис (під віссю)
        for i, ln in enumerate(bot.split("\n")):
            f.append(text(x, ay + 50 + i * 16, ln, size=10.5, color=INK))

    # дуга «вікно реакції» між порогами
    f.append(line(320, ay - 92, 680, ay - 92, color=GREEN, sw=1.6, dash="5,4"))
    f.append(text(500, ay - 98, "вікно реакції (мілісекунди)", size=11, color=GREEN, bold=True))
    f.append(line(320, ay - 88, 320, ay - 64, color=GREEN, sw=1.1))
    f.append(line(680, ay - 88, 680, ay - 64, color=GREEN, sw=1.1))

    # розрив часу перед стартом (живлення повернулося)
    f.append(text(767, ay - 14, "… живлення\nповернулося", size=10, color=MUTED))
    f[-1] = mtext(767, ay - 22, ["… живлення", "повернулося"], size=10, color=MUTED)

    f.append(text(W / 2, 340, "Цілісність гарантує BOD, шанс на стан дає попередження, "
                  "встигає FRAM, а перевірка суми не дає ожити з брехливими даними.",
                  size=12, color=INK))
    render(os.path.join(IMG, "power-fail-timeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_voltage_zones()
    fig_two_thresholds()
    fig_power_fail_timeline()
    print("OK: figs у", IMG)

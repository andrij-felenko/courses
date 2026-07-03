# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SRC = NEG          # синій — вихідний .c
OBJ = "#8a5cc7"    # фіолетовий — об'єктний .o
LNK = POS          # червоний — лінкувальник / прошивка
GEN = "#0f8a6d"    # зелений — генератор/збирач (Make, CMake)


# ── compile: роздільна компіляція — кожен .c → свій .o, потім лінкер зшиває ──
# Ідея: компілятор бачить один .c за раз; лінкер зводить усі .o в один образ.
def fig_compile():
    W, H = 800, 340
    p = []

    srcs = [("main.c", 60), ("led.c", 160), ("uart.c", 260)]
    for name, y in srcs:
        b, w, h = textbox(95, y, name, size=12, color=SRC, stroke=SRC,
                          fill="#eef2fb", min_w=110)
        p.append(b)

    # компілятор — окремий прогін на кожен файл
    for _, y in srcs:
        b, w, h = textbox(305, y, "компілятор", size=11, color=INK, stroke=INK,
                          fill=FILL, min_w=130)
        p.append(b)
        p.append(arrow(152, y, 238, y, color=SRC))

    # об'єктні файли
    objs = [("main.o", 60), ("led.o", 160), ("uart.o", 260)]
    for name, y in objs:
        b, w, h = textbox(490, y, name, size=12, color=OBJ, stroke=OBJ,
                          fill="#f3edfb", min_w=110)
        p.append(b)
        p.append(arrow(372, y, 434, y, color=INK))

    # лінкувальник зводить усе
    b, w, h = textbox(680, 160, "ЛІНКУВАЛЬНИК\nзшиває все", size=12, color=LNK,
                      stroke=LNK, fill="#fdecea", bold=True, min_w=150)
    p.append(b)
    for _, y in objs:
        p.append(arrow(548, y, 610, 160, color=OBJ))

    # образ
    b, w, h = textbox(680, 285, "firmware.elf\n(один образ)", size=11, color=INK,
                      stroke=INK, fill=FILL, min_w=150)
    p.append(b)
    p.append(arrow(680, 192, 680, 260, color=LNK))

    p.append(text(305, 305, "кожен .c компілюється ОКРЕМО", size=11,
                  color=MUTED, italic=True))

    render(os.path.join(OUT, "compile.svg"), W, H, *p,
           title="Роздільна компіляція: багато .c → багато .o → один образ")


# ── rebuild: інкрементна збірка — Make рахує час і перебудовує лише застаріле ──
# Ідея: змінили один .c — перекомпілюється лише він, решта .o беруться готові.
def fig_rebuild():
    W, H = 800, 300
    p = []

    p.append(text(400, 52, "змінили ТІЛЬКИ led.c", size=13, color=SRC, bold=True))

    rows = [
        ("main.c", "main.o", False),
        ("led.c",  "led.o",  True),
        ("uart.c", "uart.o", False),
    ]
    y0, dy = 95, 62
    for i, (src, obj, changed) in enumerate(rows):
        y = y0 + i * dy
        sfill = "#eef2fb" if not changed else "#fff4e6"
        sstroke = SRC if not changed else "#d97706"
        b, w, h = textbox(120, y, src, size=12, color=sstroke, stroke=sstroke,
                          fill=sfill, min_w=110)
        p.append(b)

        if changed:
            b, w, h = textbox(360, y, "перекомпілювати", size=11, color=LNK,
                              stroke=LNK, fill="#fdecea", bold=True, min_w=170)
            p.append(b)
            p.append(arrow(178, y, 272, y, color="#d97706"))
        else:
            b, w, h = textbox(360, y, ".o новіший — пропустити", size=11,
                              color=GEN, stroke=GEN, fill="#e9f7f2", min_w=170)
            p.append(b)
            p.append(line(178, y, 272, y, color=MUTED, dash="4,4"))

        b, w, h = textbox(600, y, obj, size=12, color=OBJ, stroke=OBJ,
                          fill="#f3edfb", min_w=100)
        p.append(b)
        p.append(arrow(448, y, 548, y, color=INK if changed else MUTED))

    # лінк
    b, w, h = textbox(730, y0 + dy, "лінк →\nобраз", size=11, color=LNK,
                      stroke=LNK, fill="#fdecea", bold=True, min_w=90)
    p.append(b)
    for i in range(3):
        p.append(arrow(651, y0 + i * dy, 690, y0 + dy, color=MUTED))

    render(os.path.join(OUT, "rebuild.svg"), W, H, *p,
           title="Make перебудовує лише те, що застаріло за часом")


# ── layers: CMake генерує складач, той жене компілятор/лінкер ────────────────
# Ідея: три шари — опис (CMake) → команди збірки (Make/Ninja) → інструменти.
def fig_layers():
    W, H = 720, 300
    p = []

    b, w, h = textbox(360, 60, "CMakeLists.txt  →  CMake\nописуємо проєкт, а не команди", size=12,
                      color=GEN, stroke=GEN, fill="#e9f7f2", bold=True, min_w=360)
    p.append(b)
    p.append(text(360, 100, "«збери програму app з main.c, led.c, uart.c»", size=11,
                  color=MUTED, italic=True))

    b, w, h = textbox(360, 155, "Make / Ninja\nконкретні команди збірки + залежності", size=12,
                      color=OBJ, stroke=OBJ, fill="#f3edfb", bold=True, min_w=360)
    p.append(b)
    p.append(arrow(360, 118, 360, 132, color=INK))

    b, w, h = textbox(360, 250, "компілятор  +  лінкувальник\ngcc … -c   ·   gcc … -o app", size=12,
                      color=LNK, stroke=LNK, fill="#fdecea", bold=True, min_w=360)
    p.append(b)
    p.append(arrow(360, 178, 360, 227, color=INK))

    p.append(text(628, 155, "переносимо", size=10, color=MUTED, italic=True))
    p.append(text(628, 250, "робить діло", size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "layers.svg"), W, H, *p,
           title="Три шари збірки: опис → команди → інструменти")


# ── history: дві появи складачів — Make (1976) і CMake (2000) на одній осі ────
# Ідея: спершу народився складач (Make: час файлів), через чверть віку — шар
# НАД ним (CMake: генератор під середовище). Кожен розв'язував свій головний біль.
def fig_history():
    W, H = 820, 340
    p = []

    ax_y = 150
    x0, x1 = 90, 730
    p.append(line(x0, ax_y, x1 + 10, ax_y, color=INK, sw=2))
    p.append(arrow(x1, ax_y, x1 + 12, ax_y, color=INK))

    # дві віхи на осі
    def milestone(x, year, who, up):
        p.append(circle(x, ax_y, 6, fill=INK, stroke=INK))
        p.append(text(x, ax_y + 26, year, size=13, color=INK, bold=True))
        dy = -1 if up else 1

    # Make — ліворуч, картка вгорі
    mx = 230
    p.append(circle(mx, ax_y, 7, fill=GEN, stroke=GEN))
    p.append(text(mx, ax_y + 28, "1976", size=13, color=INK, bold=True))
    b, w, h = textbox(mx, 80, "Make · Bell Labs\nСтюарт Фелдман\nбіль: не перебудовувати зайве",
                      size=11, color=GEN, stroke=GEN, fill="#e9f7f2", bold=True, min_w=250)
    p.append(b)
    p.append(line(mx, 108, mx, ax_y - 7, color=GEN, sw=1.5, dash="4,4"))

    # CMake — праворуч, картка вгорі
    cx = 590
    p.append(circle(cx, ax_y, 7, fill=OBJ, stroke=OBJ))
    p.append(text(cx, ax_y + 28, "2000", size=13, color=INK, bold=True))
    b, w, h = textbox(cx, 80, "CMake · Kitware\nГофман і Мартін\nбіль: одна збірка на всі платформи",
                      size=11, color=OBJ, stroke=OBJ, fill="#f3edfb", bold=True, min_w=260)
    p.append(b)
    p.append(line(cx, 108, cx, ax_y - 7, color=OBJ, sw=1.5, dash="4,4"))

    # підпис під віссю — чверть віку між ними
    p.append(line(mx, ax_y + 48, cx, ax_y + 48, color=MUTED, sw=1, dash="3,3"))
    p.append(text((mx + cx) / 2, ax_y + 66, "≈ чверть віку", size=11, color=MUTED, italic=True))

    # ярлик рівнів під кожним
    p.append(text(mx, 250, "складач: рахує час файлів", size=11, color=GEN))
    p.append(text(cx, 250, "генератор: НАД складачем", size=11, color=OBJ))
    p.append(arrow(mx + 130, 250, cx - 135, 250, color=MUTED, sw=1.4))
    p.append(text((mx + cx) / 2, 236, "ще один рівень абстракції", size=10,
                  color=MUTED, italic=True))

    render(os.path.join(OUT, "history.svg"), W, H, *p,
           title="Дві появи: спершу складач, згодом — шар над ним")


if __name__ == "__main__":
    fig_compile()
    fig_rebuild()
    fig_layers()
    fig_history()
    print("figs done")

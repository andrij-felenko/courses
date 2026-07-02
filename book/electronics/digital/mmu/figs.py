# -*- coding: utf-8 -*-
"""Фігури до теми «Блок керування пам'яттю (MMU)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

PURPLE = "#6a3fb5"   # MMU / переклад
AMBER  = "#b9770e"   # зсув / offset


# ── 1. Переклад адреси: віртуальна → сторінка+зсув → таблиця → фізична ────────
def fig_translate():
    W, H = 820, 380
    f = [text(W / 2, 26, "MMU перекладає віртуальну адресу у фізичну", size=14, bold=True)]

    # Віртуальна адреса: [ номер сторінки | зсув ]
    vx, vy = 40, 70
    f.append(rect(vx, vy, 210, 40, fill="#eef2fb", stroke=NEG, sw=2))
    f.append(line(vx + 130, vy, vx + 130, vy + 40, color=NEG, sw=1.6))
    f.append(text(vx + 65, vy + 25, "номер сторінки", size=11, color=NEG, bold=True))
    f.append(text(vx + 170, vy + 25, "зсув", size=11, color=AMBER, bold=True))
    f.append(text(vx + 105, vy - 10, "віртуальна адреса (те, що бачить програма)", size=10.5, color=MUTED))

    # Зсув іде прямо вниз, у фізичну адресу — не чіпається
    f.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="2" '
             'stroke-dasharray="5,4"/>' % (vx + 170, vy + 40, vx + 170 + 445, 300, AMBER))
    f.append(text(vx + 405, 200, "зсув не чіпається", size=10, color=AMBER, italic=True, anchor="start"))

    # Номер сторінки → в таблицю сторінок
    f.append(arrow(vx + 65, vy + 40, vx + 65, 150, color=NEG, sw=2))

    # Таблиця сторінок
    tx, ty = 40, 152
    rows = [("0", "—"), ("1", "кадр 12"), ("2", "кадр 05"), ("…", "…")]
    rh = 30
    f.append(text(tx + 105, ty - 8, "таблиця сторінок (у пам'яті)", size=10.5, color=PURPLE, bold=True))
    for i, (pg, fr) in enumerate(rows):
        yy = ty + i * rh
        hit = (i == 1)
        fill = "#f1ecfa" if hit else BG
        f.append(rect(tx, yy, 210, rh, fill=fill, stroke=PURPLE if hit else MUTED, sw=1.8 if hit else 1.2))
        f.append(line(tx + 70, yy, tx + 70, yy + rh, color=MUTED, sw=1))
        f.append(text(tx + 35, yy + 20, "стор. " + pg, size=10, color=INK))
        f.append(text(tx + 140, yy + 20, fr, size=10, color=PURPLE if hit else MUTED, bold=hit))

    # Стрілка «номер сторінки індексує рядок» уже показана; вихід рядка → номер кадру
    f.append(arrow(tx + 210, ty + rh + rh / 2, 470, ty + rh + rh / 2, color=PURPLE, sw=2))
    f.append(text(345, ty + rh + rh / 2 - 8, "MMU читає номер кадру", size=10, color=PURPLE, bold=True))

    # MMU-блок (акцент)
    mx, my = 300, 70
    f.append(rect(mx, my, 190, 62, fill="#f1ecfa", stroke=PURPLE, sw=2.4, rx=10))
    f.append(text(mx + 95, my + 25, "MMU", size=14, color=PURPLE, bold=True))
    f.append(text(mx + 95, my + 46, "робить це щодоступу", size=10, color=PURPLE))

    # Фізична адреса: [ номер кадру | зсув ]
    px, py = 470, 285
    f.append(rect(px, py, 210, 40, fill="#eef6ef", stroke=FIELD, sw=2))
    f.append(line(px + 130, py, px + 130, py + 40, color=FIELD, sw=1.6))
    f.append(text(px + 65, py + 25, "номер кадру", size=11, color=FIELD, bold=True))
    f.append(text(px + 170, py + 25, "зсув", size=11, color=AMBER, bold=True))
    f.append(text(px + 105, py + 55, "фізична адреса (реальна комірка в чипі)", size=10.5, color=MUTED))

    f.append(text(W / 2, 360,
                  "Старші біти адреси замінюються за таблицею; молодші (зсув усередині сторінки) проходять як є.",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "translate.svg"), W, H, *f)


# ── 2. Ізоляція: дві програми, ті самі віртуальні адреси, різна фізична ───────
def fig_isolation():
    W, H = 800, 340
    f = [text(W / 2, 26, "Кожна програма живе у власному просторі адрес", size=14, bold=True)]

    def vspace(x, y, name, col):
        f.append(rect(x, y, 160, 120, fill="#f7f8fb", stroke=col, sw=2, rx=8))
        f.append(text(x + 80, y - 8, name, size=11.5, color=col, bold=True))
        f.append(rect(x + 24, y + 30, 112, 34, fill=BG, stroke=col, sw=1.8))
        f.append(text(x + 80, y + 52, "адреса 0x2000", size=10.5, color=col, bold=True))
        f.append(text(x + 80, y + 92, "той самий номер", size=9.5, color=MUTED))
        return (x + 160, y + 47)  # точка виходу праворуч

    aout = vspace(40, 70, "програма A", NEG)
    bout = vspace(40, 210, "програма B", POS)

    # MMU у центрі
    mx, my, mw, mh = 320, 120, 150, 110
    f.append(rect(mx, my, mw, mh, fill="#f1ecfa", stroke=PURPLE, sw=2.4, rx=10))
    f.append(text(mx + mw / 2, my + 30, "MMU", size=14, color=PURPLE, bold=True))
    f.append(text(mx + mw / 2, my + 55, "своя таблиця", size=9.5, color=PURPLE))
    f.append(text(mx + mw / 2, my + 72, "для кожної", size=9.5, color=PURPLE))
    f.append(text(mx + mw / 2, my + 92, "програми", size=9.5, color=PURPLE))

    f.append(arrow(aout[0], aout[1], mx, my + 34, color=NEG, sw=2))
    f.append(arrow(bout[0], bout[1], mx, my + mh - 20, color=POS, sw=2))

    # Фізична пам'ять праворуч — різні кадри
    rx, ry, rw = 560, 60, 200
    f.append(rect(rx, ry, rw, 220, fill="#f4fbf5", stroke=FIELD, sw=2, rx=8))
    f.append(text(rx + rw / 2, ry - 8, "фізична пам'ять (одна на всіх)", size=10.5, color=FIELD, bold=True))
    f.append(rect(rx + 20, ry + 30, rw - 40, 34, fill=BG, stroke=NEG, sw=1.8))
    f.append(text(rx + rw / 2, ry + 52, "кадр A → 0x81000", size=10, color=NEG, bold=True))
    f.append(rect(rx + 20, ry + 150, rw - 40, 34, fill=BG, stroke=POS, sw=1.8))
    f.append(text(rx + rw / 2, ry + 172, "кадр B → 0x4A000", size=10, color=POS, bold=True))
    f.append(text(rx + rw / 2, ry + 108, "не перетинаються", size=10, color=FIELD, italic=True))

    f.append(arrow(mx + mw, my + 34, rx, ry + 47, color=NEG, sw=2))
    f.append(arrow(mx + mw, my + mh - 20, rx, ry + 167, color=POS, sw=2))

    f.append(text(W / 2, 322,
                  "Однакова віртуальна адреса 0x2000 у двох програм веде MMU у РІЗНІ фізичні кадри — тому вони не бачать даних одна одної.",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "isolation.svg"), W, H, *f)


# ── 3. TLB: швидкий шлях проти повільного обходу таблиці ──────────────────────
def fig_tlb():
    W, H = 800, 320
    f = [text(W / 2, 26, "TLB — маленький кеш недавніх перекладів", size=14, bold=True)]

    # Вхід
    f.append(rect(40, 120, 130, 44, fill="#eef2fb", stroke=NEG, sw=2))
    f.append(text(105, 140, "віртуальна", size=11, color=NEG, bold=True))
    f.append(text(105, 156, "адреса", size=11, color=NEG, bold=True))

    # TLB
    tx, ty, tw, th = 230, 108, 150, 68
    f.append(rect(tx, ty, tw, th, fill="#f1ecfa", stroke=PURPLE, sw=2.4, rx=10))
    f.append(text(tx + tw / 2, ty + 26, "TLB", size=13, color=PURPLE, bold=True))
    f.append(text(tx + tw / 2, ty + 48, "переклад тут?", size=10, color=PURPLE))
    f.append(arrow(170, 142, tx, 142, color=NEG, sw=2))

    # Влучення → фізична адреса (швидко)
    f.append(arrow(tx + tw, ty + 20, 620, ty + 20, color=FIELD, sw=2.4))
    f.append(text((tx + tw + 620) / 2, ty + 12, "влучення: 1 такт", size=10, color=FIELD, bold=True))
    f.append(rect(620, ty, 150, 40, fill="#eef6ef", stroke=FIELD, sw=2))
    f.append(text(695, ty + 25, "фізична адреса", size=10.5, color=FIELD, bold=True))

    # Промах → обхід таблиці (повільно), донизу
    f.append(arrow(tx + tw / 2, ty + th, tx + tw / 2, 232, color=POS, sw=2))
    f.append(text(tx + tw / 2 + 8, 210, "промах", size=10, color=POS, bold=True, anchor="start"))
    f.append(rect(tx - 40, 232, 230, 44, fill="#fdeef0", stroke=POS, sw=2, rx=8))
    f.append(text(tx + tw / 2 - 40 + 20, 252, "обхід таблиці сторінок", size=10.5, color=POS, bold=True))
    f.append(text(tx + tw / 2 - 40 + 20, 268, "у пам'яті — десятки тактів", size=9.5, color=POS))

    # Результат обходу повертається і в TLB, і на вихід
    f.append(arrow(tx + 190, 254, 620, ty + 28, color=MUTED, sw=1.6, ))
    f.append(text(500, 250, "знайдений переклад кладемо в TLB", size=9.5, color=MUTED, italic=True))

    f.append(text(W / 2, 300,
                  "Переклад через таблицю коштує зайвих звернень до пам'яті; TLB тримає недавні пари «сторінка → кадр», і майже всі доступи влучають у нього.",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "tlb.svg"), W, H, *f)


# ── 4. Atlas one-level store: барабан + осердя + 32 регістри-відповідники ─────
def fig_atlas():
    W, H = 820, 400
    DRUM = "#7a5a2e"  # барабан (магнітний, повільний)
    f = [text(W / 2, 26, "Atlas: барабан і осердя як одне «однорівневе сховище»", size=14, bold=True)]

    # Барабан (велике повільне сховище) — ліворуч
    dx, dy, dw, dh = 40, 70, 150, 250
    f.append(rect(dx, dy, dw, dh, fill="#f5efe6", stroke=DRUM, sw=2.2, rx=8))
    f.append(text(dx + dw / 2, dy - 10, "магнітний барабан", size=11, color=DRUM, bold=True))
    f.append(text(dx + dw / 2, dy + 22, "96 000 слів", size=11.5, color=DRUM, bold=True))
    f.append(text(dx + dw / 2, dy + 40, "повільний, великий", size=9.5, color=MUTED))
    # кілька «сторінок» на барабані
    for i in range(4):
        yy = dy + 62 + i * 42
        on = (i == 2)
        f.append(rect(dx + 22, yy, dw - 44, 30, fill=("#efe4d0" if on else BG),
                      stroke=(DRUM if on else MUTED), sw=(2 if on else 1.1)))
        f.append(text(dx + dw / 2, yy + 20, "стор. %d" % (100 + i), size=9.5,
                      color=(DRUM if on else MUTED), bold=on))

    # Осердя (мале швидке) — праворуч від центру
    cx, cy, cw, ch = 590, 70, 190, 250
    f.append(rect(cx, cy, cw, ch, fill="#eef6ef", stroke=FIELD, sw=2.2, rx=8))
    f.append(text(cx + cw / 2, cy - 10, "феритове осердя (core)", size=11, color=FIELD, bold=True))
    f.append(text(cx + cw / 2, cy + 22, "16 384 слова = 32 блоки", size=10.5, color=FIELD, bold=True))
    f.append(text(cx + cw / 2, cy + 40, "швидке, мале", size=9.5, color=MUTED))
    for i in range(4):
        yy = cy + 62 + i * 42
        empty = (i == 3)
        f.append(rect(cx + 22, yy, cw - 44, 30, fill=(BG if empty else "#e3f1e6"),
                      stroke=(MUTED if empty else FIELD), sw=(1.1 if empty else 1.8)))
        f.append(text(cx + cw / 2, yy + 20,
                      ("вільний блок" if empty else "блок %d" % i), size=9.5,
                      color=(MUTED if empty else FIELD), bold=not empty))

    # Асоціативний стос із 32 регістрів (прабатько TLB) — у центрі
    px, py, pw, ph = 300, 96, 210, 172
    f.append(rect(px, py, pw, ph, fill="#f1ecfa", stroke=PURPLE, sw=2.4, rx=10))
    f.append(text(px + pw / 2, py + 24, "32 регістри-", size=12, color=PURPLE, bold=True))
    f.append(text(px + pw / 2, py + 42, "відповідники (PAR)", size=12, color=PURPLE, bold=True))
    f.append(text(px + pw / 2, py + 62, "по одному на блок осердя", size=9, color=PURPLE))
    # символ паралельного порівняння
    for i in range(3):
        yy = py + 84 + i * 26
        f.append(rect(px + 20, yy, pw - 40, 20, fill=BG, stroke=PURPLE, sw=1.1))
        f.append(text(px + pw / 2, yy + 14, "стор. ? = блок ?", size=8.5, color=PURPLE))
    f.append(text(px + pw / 2, py + ph + 16, "звіряє адресу з усіма 32 нараз", size=9,
                  color=PURPLE, italic=True))

    # Процесор називає віртуальну адресу — заходить згори в регістри
    f.append(text(px + pw / 2, 62, "адреса від процесора", size=10, color=INK))
    f.append(arrow(px + pw / 2, 70, px + pw / 2, py, color=INK, sw=1.8))

    # Влучення: PAR → осердя (швидко)
    f.append(arrow(px + pw, py + 40, cx, cy + 40, color=FIELD, sw=2.2))
    f.append(text((px + pw + cx) / 2, py + 30, "є в осерді:", size=9, color=FIELD, bold=True))
    f.append(text((px + pw + cx) / 2, py + 44, "блок за такт", size=9, color=FIELD))

    # Промах (non-equivalence): барабан → осердя, підкачування сторінки
    f.append(arrow(dx + dw, dy + 180, px, py + 130, color=DRUM, sw=2))
    f.append(text((dx + dw + px) / 2 - 6, dy + 150, "нема в осерді →", size=9, color=DRUM, bold=True))
    f.append(text((dx + dw + px) / 2 - 6, dy + 164, "тягнемо з барабана", size=9, color=DRUM))
    f.append(arrow(px + pw / 2, py + ph, cx + cw / 2, cy + ch, color=DRUM, sw=1.8))
    f.append(text((px + cx) / 2 + 40, cy + ch - 6, "у вільний блок", size=9, color=DRUM, italic=True))

    f.append(text(W / 2, 388,
                  "Програма адресує всі 1 000 000 слів як одне ціле; апаратура сама тримає гарячі сторінки в осерді, решту — на барабані.",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "atlas-store.svg"), W, H, *f)


if __name__ == "__main__":
    fig_translate()
    fig_isolation()
    fig_tlb()
    fig_atlas()
    print("OK: 4 figures ->", IMG)

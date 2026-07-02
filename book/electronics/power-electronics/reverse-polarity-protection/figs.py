# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def diode_symbol(x, y, s=18, color=INK, flip=False):
    """Трикутник-діод із рискою-катодом. Струм тече в бік вершини трикутника.
    flip=False → провідний напрям зліва направо (вершина праворуч)."""
    out = []
    if not flip:
        out.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.5"/>'
                   % (x, y - s / 2, x, y + s / 2, x + s, y, "#dfe6ee", color))
        out.append(line(x + s, y - s / 2, x + s, y + s / 2, color=color, sw=2.4))  # катод
    else:
        out.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.5"/>'
                   % (x + s, y - s / 2, x + s, y + s / 2, x, y, "#dfe6ee", color))
        out.append(line(x, y - s / 2, x, y + s / 2, color=color, sw=2.4))
    return "".join(out)


# ── Фігура 1: чотири способи захисту, порівняння за одним поглядом ───────────
def fig_methods():
    W, H = 760, 430
    frags = [text(W / 2, 28, "Чотири способи захистити плату від переполюсування", size=17, bold=True)]

    col_w, col_h = 172, 320
    gap = 14
    x0 = (W - (4 * col_w + 3 * gap)) / 2
    top = 56

    cards = [
        ("Послідовний\nдіод", FIELD,
         "струм лише\nв один бік",
         "− завжди гріє\n   Vf·I\n− крадe 0.3–0.7 В",
         "просте\nй дешеве"),
        ("Шунтуючий діод\n+ запобіжник", NEG,
         "реверс → КЗ →\nплавкий згорає",
         "− одноразовий\n− міняти\n   запобіжник",
         "нуль втрат\nу нормі"),
        ("P-MOS\nу «плюсі»", POS,
         "Vgs = −Vin\nвідкриває канал",
         "− межа Vgs\n   на високому Vin",
         "втрати I²·Rds(on)\nземля ціла"),
        ("N-MOS\nу «землі»", INK,
         "найменший\nRds(on)",
         "− розриває\n   спільну землю",
         "найдешевший\nопір"),
    ]

    for i, (name, accent, how, cons, pro) in enumerate(cards):
        x = x0 + i * (col_w + gap)
        frags.append(rect(x, top, col_w, col_h, fill=FILL, stroke=accent, sw=2.2, rx=10))
        frags.append(rect(x, top, col_w, 44, fill=accent, stroke=accent, sw=1, rx=10))
        frags.append(rect(x, top + 22, col_w, 22, fill=accent, stroke=accent, sw=1, rx=0))
        frags.append(mtext(x + col_w / 2, top + 20, name.split("\n"), size=13.5, color="#ffffff", bold=True))
        # «як працює»
        frags.append(fitbox(x + 10, top + 54, col_w - 20, 50, how, size=12,
                            fill="#ffffff", stroke=MUTED, sw=1, rx=6, color=INK))
        # мінуси
        frags.append(fitbox(x + 10, top + 112, col_w - 20, 74, cons, size=11.5,
                            fill="#fdecea", stroke=POS, sw=1, rx=6, color="#7a271a"))
        # плюс
        frags.append(fitbox(x + 10, top + 194, col_w - 20, 50, pro, size=11.5,
                            fill="#eafaf1", stroke=FIELD, sw=1, rx=6, color="#145a32"))
        # мініатюра-символ
        cy = top + 288
        if i == 0:
            frags.append(line(x + 40, cy, x + 66, cy, color=INK, sw=2))
            frags.append(diode_symbol(x + 66, cy, s=18, color=FIELD))
            frags.append(line(x + 84, cy, x + col_w - 40, cy, color=INK, sw=2))
        elif i == 1:
            cyt = cy - 12
            frags.append(line(x + 26, cyt, x + 62, cyt, color=INK, sw=2))
            frags.append(rect(x + 62, cyt - 8, 24, 16, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=3))
            frags.append(line(x + 68, cyt, x + 80, cyt, color=NEG, sw=1.8))
            frags.append(line(x + 86, cyt, x + col_w - 26, cyt, color=INK, sw=2))
            frags.append(line(x + col_w - 42, cyt, x + col_w - 42, cyt + 20, color=INK, sw=2))
            frags.append(diode_symbol(x + col_w - 50, cyt + 20, s=15, color=NEG, flip=True))
            frags.append(line(x + col_w - 42, cyt + 35, x + 62, cyt + 35, color=MUTED, sw=1.5, dash="3,3"))
        else:
            # MOSFET як прямокутник-ключ
            frags.append(line(x + 40, cy, x + 62, cy, color=INK, sw=2))
            frags.append(rect(x + 62, cy - 12, 46, 24, fill="#fdecea" if i == 2 else "#eef1f5",
                             stroke=accent, sw=1.8, rx=4))
            frags.append(text(x + 85, cy + 4, "MOS", size=10, color=accent, bold=True))
            frags.append(line(x + 108, cy, x + col_w - 40, cy, color=INK, sw=2))

    render(os.path.join(IMG, 'methods-compare.svg'), W, H, *frags)


# ── Фігура 2: шунтуючий діод + запобіжник — механізм спрацювання ─────────────
def fig_shunt_fuse():
    W, H = 720, 340
    frags = [text(W / 2, 26, "Шунтуючий діод: реверс перетворює запобіжник на жертву", size=16, bold=True)]

    def panel(ox, title, reversed_):
        pw, ph = 320, 250
        oy = 56
        frags.append(rect(ox, oy, pw, ph, fill=BG, stroke=MUTED, sw=1.4, rx=10))
        frags.append(text(ox + pw / 2, oy + 24, title, size=13.5, bold=True,
                         color=(POS if reversed_ else FIELD)))

        # координати шини
        left = ox + 34
        right = ox + pw - 34
        ytop = oy + 78     # «плюсовий» провід
        ybot = oy + 190    # «мінусовий» провід / земля

        # джерело зліва (батарея)
        frags.append(rect(left - 22, ytop, 16, ybot - ytop, fill="#eef1f5", stroke=INK, sw=1.4, rx=3))
        if not reversed_:
            frags.append(plus(left - 14, ytop + 10, r=8))
            frags.append(minus(left - 14, ybot - 10, r=8))
        else:
            frags.append(minus(left - 14, ytop + 10, r=8))
            frags.append(plus(left - 14, ybot - 10, r=8))

        # верхній провід із запобіжником
        fx = ox + pw / 2 - 26
        frags.append(line(left, ytop, fx, ytop, color=INK, sw=2.4))
        # запобіжник
        blown = reversed_
        fuse_col = POS if blown else INK
        frags.append(rect(fx, ytop - 9, 34, 18, fill="#fdecea" if blown else "#eef1f5",
                         stroke=fuse_col, sw=1.8, rx=4))
        if blown:
            frags.append(line(fx + 4, ytop, fx + 14, ytop - 5, color=POS, sw=2))
            frags.append(line(fx + 14, ytop - 5, fx + 20, ytop + 5, color=POS, sw=2))
            frags.append(line(fx + 20, ytop + 5, fx + 30, ytop, color=POS, sw=2))
            frags.append(text(fx + 17, ytop - 16, "розрив", size=10, color=POS, bold=True))
        else:
            frags.append(line(fx + 4, ytop, fx + 30, ytop, color=INK, sw=2.2))
            frags.append(text(fx + 17, ytop - 15, "цілий", size=10, color=FIELD))
        frags.append(line(fx + 34, ytop, right, ytop, color=(MUTED if blown else INK), sw=2.4))

        # нижній провід
        frags.append(line(left, ybot, right, ybot, color=INK, sw=2.4))

        # шунтуючий діод між шинами, праворуч від запобіжника (катодом до «плюса»)
        dx = ox + pw / 2 + 58
        frags.append(line(dx, ytop, dx, ytop + 26, color=INK, sw=2))
        # діод: провідний з «мінуса» (низ) до «плюса» (верх) — тобто у нормі зворотно зміщений
        frags.append(diode_symbol(dx - 9, ytop + 44, s=18, color=(POS if reversed_ else MUTED), flip=True))
        frags.append(line(dx, ytop + 62, dx, ybot, color=INK, sw=2))

        # навантаження (плата) справа
        frags.append(rect(right - 4, ytop, 40, ybot - ytop, fill="#eafaf1" if not reversed_ else "#f4f6f8",
                         stroke=(FIELD if not reversed_ else MUTED), sw=1.6, rx=5))
        frags.append(mtext(right + 16, (ytop + ybot) / 2 - 6, ["плата"], size=11,
                          color=(FIELD if not reversed_ else MUTED), bold=True))

        # підпис-стан
        if not reversed_:
            frags.append(fitbox(ox + 20, oy + ph - 42, pw - 40, 34,
                                "діод зворотний → не проводить\nплата живиться, втрат Vf нема",
                                size=11, fill="#eafaf1", stroke=FIELD, sw=1, rx=5, color="#145a32"))
        else:
            frags.append(fitbox(ox + 20, oy + ph - 42, pw - 40, 34,
                                "діод відкрився → КЗ реверсу\nструм палить запобіжник, плата відрізана",
                                size=11, fill="#fdecea", stroke=POS, sw=1, rx=5, color="#7a271a"))

    panel(30, "Правильна полярність", False)
    panel(W - 30 - 320, "Полюси переплутано", True)

    render(os.path.join(IMG, 'shunt-fuse.svg'), W, H, *frags)


# ── Фігура 3 (hist): чому переполюсування стало аварією лише з генератором ────
def fig_timeline():
    W, H = 780, 360
    frags = [text(W / 2, 28, "Як переполюсування батареї стало типовою аварією", size=16, bold=True)]

    axis_y = 150
    x0, x1 = 60, W - 40
    frags.append(line(x0, axis_y, x1, axis_y, color=INK, sw=2.4))
    frags.append(arrow(x1 - 2, axis_y, x1 + 8, axis_y, color=INK, sw=2.4))
    frags.append(text(x1 + 4, axis_y + 22, "час", size=11, color=MUTED, anchor="end", italic=True))

    # три віхи
    stops = [
        (150, "до ~1960", "динамо (щіткова машина)",
         "реверс майже байдужий:\nобмотки й реле терплять\nзворотний струм",
         FIELD, "#145a32", "#eafaf1"),
        (400, "1960 →", "генератор із діодами",
         "кремнієві діоди випрямляча\nгинуть від реверсу за\nчастку секунди",
         POS, "#7a271a", "#fdecea"),
        (640, "1980-ті →", "стандарти випробувань",
         "reverse-battery кодифіковано:\n−14 В / 60 с у 12-В мережі,\nпослаблений −4 В із діодами",
         NEG, "#1e3a8a", "#eaf0fd"),
    ]
    for cx, era, title, body, accent, tcol, bg in stops:
        frags.append(circle(cx, axis_y, 9, fill=accent, stroke=accent, sw=2))
        frags.append(text(cx, axis_y - 20, era, size=12, color=accent, bold=True))
        # картка згори або знизу — чергуємо, щоб не тіснились
        cardw, cardh = 210, 96
        cy_top = axis_y - 24 - cardh
        # усі згори, крім середньої (знизу)
        below = (cx == 400)
        cy = axis_y + 26 if below else cy_top
        bx = cx - cardw / 2
        bx = max(x0 - 4, min(bx, x1 - cardw))
        frags.append(line(cx, axis_y, cx, cy if below else cy + cardh,
                          color=accent, sw=1.4, dash="3,3"))
        frags.append(rect(bx, cy, cardw, cardh, fill=bg, stroke=accent, sw=1.8, rx=8))
        frags.append(text(bx + cardw / 2, cy + 22, title, size=12.5, color=tcol, bold=True))
        frags.append(fitbox(bx + 8, cy + 32, cardw - 16, cardh - 40, body, size=10.5,
                            fill=bg, stroke=bg, sw=0, rx=4, color=tcol))

    render(os.path.join(IMG, 'reverse-battery-history.svg'), W, H, *frags)


# ── Фігура 4 (hist): чому стандарт дозволяє послаблені −4 В замість −14 В ─────
def fig_iso_case1():
    W, H = 760, 400
    frags = [text(W / 2, 26, "Чому стандарт має два рівні: −14 В без діодів, −4 В із діодами випрямляча",
                  size=15, bold=True)]

    def panel(ox, title, has_fuse):
        pw, ph = 330, 300
        oy = 52
        accent = POS if not has_fuse else NEG
        frags.append(rect(ox, oy, pw, ph, fill=BG, stroke=MUTED, sw=1.4, rx=10))
        frags.append(text(ox + pw / 2, oy + 24, title, size=13, bold=True, color=accent))

        left = ox + 40
        right = ox + pw - 40
        ytop = oy + 92
        ybot = oy + 210

        # перевернута батарея зліва: «мінус» на верхній шині
        frags.append(rect(left - 24, ytop, 16, ybot - ytop, fill="#eef1f5", stroke=INK, sw=1.4, rx=3))
        frags.append(minus(left - 16, ytop + 12, r=8))
        frags.append(plus(left - 16, ybot - 12, r=8))
        frags.append(text(left - 16, ybot + 22, "батарея\nнавпаки", size=9.5, color=MUTED))

        # верхня й нижня шини
        frags.append(line(left, ytop, right, ytop, color=INK, sw=2.4))
        frags.append(line(left, ybot, right, ybot, color=INK, sw=2.4))

        # генератор із діодом випрямляча — вертикальна вітка коло батареї
        gx = ox + pw / 2 - 40
        frags.append(line(gx, ytop, gx, ytop + 24, color=INK, sw=2))
        # при реверсі діод випрямляча зміщений ПРЯМО (проводить) → чергуємо колір
        frags.append(diode_symbol(gx - 9, ytop + 42, s=18, color=FIELD, flip=False))
        frags.append(line(gx, ytop + 60, gx, ybot, color=INK, sw=2))
        frags.append(text(gx, ytop + 4 - 10, "діод", size=9.5, color=FIELD, bold=True, anchor="end"))
        frags.append(text(gx - 12, (ytop + ybot) / 2 + 30, "випрямляч\nгенератора", size=9, color=FIELD, anchor="end"))

        if has_fuse:
            # запобіжник у верхньому проводі між генератором і платою — розриває вітку
            fx = ox + pw / 2 + 26
            frags.append(rect(fx, ytop - 9, 30, 18, fill="#f4f6f8", stroke=INK, sw=1.6, rx=4))
            frags.append(line(fx + 4, ytop, fx + 26, ytop, color=INK, sw=2))
            frags.append(text(fx + 15, ytop - 15, "запобіжник", size=9, color=MUTED))

        # плата справа
        frags.append(rect(right - 4, ytop, 42, ybot - ytop, fill="#f4f6f8", stroke=MUTED, sw=1.6, rx=5))
        frags.append(mtext(right + 17, (ytop + ybot) / 2 - 4, ["плата"], size=10.5, color=MUTED, bold=True))

        # позначка напруги, яку бачить плата
        if not has_fuse:
            frags.append(fitbox(ox + 18, oy + ph - 60, pw - 36, 48,
                                "діод відкритий → тече весь\nзворотний струм, спад на діоді\nтримає шину коло −4 В",
                                size=10.5, fill="#fdecea", stroke=POS, sw=1, rx=5, color="#7a271a"))
        else:
            frags.append(fitbox(ox + 18, oy + ph - 60, pw - 36, 48,
                                "запобіжник відрізав діод →\nнема що гасити реверс, плата\nбачить повні −14 В",
                                size=10.5, fill="#eaf0fd", stroke=NEG, sw=1, rx=5, color="#1e3a8a"))

    panel(24, "Запобіжника нема: діоди гасять реверс", False)
    panel(W - 24 - 330, "Запобіжник у колі: діоди відрізано", True)

    render(os.path.join(IMG, 'iso-case1-clamp.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_methods()
    fig_shunt_fuse()
    fig_timeline()
    fig_iso_case1()
    print("ok")

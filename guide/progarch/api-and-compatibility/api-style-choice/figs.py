# -*- coding: utf-8 -*-
"""Фігури до кроку «Стилі API як рішення, не релігія»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

PURPLE = "#7c3aed"


def fig_unit_of_conversation():
    """Що є ОДНІЄЮ одиницею взаємодії в кожному стилі."""
    W, H = 1020, 440
    frags = []

    for sx in (340, 680):
        frags.append(line(sx, 46, sx, 416, color=MUTED, sw=1, dash="4,5"))

    def panel(cx, header, top, target, cap2, color, fill):
        out = [text(cx, 58, header, size=15, bold=True)]
        b, _, _ = textbox(cx, 120, top, size=13)
        out.append(b)
        out.append(arrow(cx, 150, cx, 238, color=color, sw=2.4))
        b, _, _ = textbox(cx, 300, target, size=13, fill=fill)
        out.append(b)
        out.append(text(cx, 374, "одиниця розмови —", size=11, color=MUTED))
        out.append(text(cx, 396, cap2, size=11, color=MUTED))
        return out

    frags += panel(175, "REST", "клієнт", "GET /homes/42/\ndevices",
                   "РЕСУРС (іменник)", NEG, "#eef2fb")
    frags += panel(510, "gRPC", "клієнт (стаб)", "GetDevice(id)\n→ Device",
                   "ПРОЦЕДУРА (дієслово)", FIELD, "#eef7f0")
    frags += panel(845, "GraphQL", "клієнт малює запит", "{ device {\nname, state } }",
                   "ЗАПИТ ФОРМИ клієнта", PURPLE, "#f2ecfb")

    render(os.path.join(IMG, "unit-of-conversation.svg"), W, H, *frags,
           title="Одиниця розмови: іменник, дієслово, форма")


def fig_temporal_coupling():
    """Синхронний запит-відповідь проти асинхронного повідомлення в черзі."""
    W, H = 980, 400
    frags = []

    # ── Рядок 1: синхронно ──
    frags.append(text(490, 72, "Синхронно — REST / gRPC / GraphQL", size=15, bold=True))
    b, _, _ = textbox(200, 135, "клієнт", size=14)
    frags.append(b)
    b, _, _ = textbox(780, 135, "сервер", size=14)
    frags.append(b)
    frags.append(arrow(238, 124, 722, 124, color=NEG, sw=2.0))
    frags.append(text(490, 109, "запит →", size=12, color=MUTED))
    frags.append(arrow(722, 146, 238, 146, color=MUTED, sw=2.0))
    frags.append(text(490, 170, "← відповідь", size=12, color=MUTED))
    frags.append(text(490, 194, "обидва боки живі в один момент; клієнт блокований, поки чекає",
                      size=12, color=MUTED))

    # ── розділювач ──
    frags.append(line(70, 224, 910, 224, color=MUTED, sw=1, dash="5,6"))

    # ── Рядок 2: асинхронно ──
    frags.append(text(490, 258, "Асинхронно — черга / брокер (MQTT)", size=15, bold=True))
    b, _, _ = textbox(175, 320, "продюсер", size=13)
    frags.append(b)
    b, _, _ = textbox(490, 320, "брокер\n(черга)", size=13, fill="#eef7f0")
    frags.append(b)
    b, _, _ = textbox(810, 320, "споживач", size=13)
    frags.append(b)
    frags.append(arrow(219, 320, 449, 320, color=FIELD, sw=2.2))
    frags.append(text(334, 305, "поклав і пішов", size=12, color=MUTED))
    frags.append(arrow(531, 320, 765, 320, color=MUTED, sw=2.2))
    frags.append(text(648, 305, "забрав пізніше", size=12, color=MUTED))
    frags.append(text(490, 372, "у часі роз'єднані: брокер тримає, поки споживач готовий",
                      size=12, color=MUTED))

    render(os.path.join(IMG, "temporal-coupling.svg"), W, H, *frags,
           title="Зв'язок у часі")


def fig_choice_map():
    """Дві осі — хто на іншому кінці й яка форма читання — розводять стилі по кутах."""
    W, H = 820, 560
    ox, oy = 120, 470
    frags = []

    frags.append(arrow(ox, oy, 760, oy, color=LINE, sw=1.8))   # X →
    frags.append(arrow(ox, oy, ox, 90, color=LINE, sw=1.8))    # Y ↑

    # підписи осей
    frags.append(text(132, 100, "багатший граф ↑", size=12, color=MUTED, anchor="start"))
    frags.append(text(132, 452, "проста відповідь", size=12, color=MUTED, anchor="start"))
    frags.append(text(230, 494, "внутрішні сервіси", size=12, color=MUTED))
    frags.append(text(662, 494, "публічні клієнти", size=12, color=MUTED))
    frags.append(text(440, 517, "хто на іншому кінці  →", size=13, color=MUTED))

    # три стилі по кутах
    b, _, _ = textbox(255, 395, "gRPC\nсервіс↔сервіс,\nтипізовано", size=13, fill="#eef2fb")
    frags.append(b)
    b, _, _ = textbox(600, 405, "REST\nпублічно, ресурси,\nкешується", size=13)
    frags.append(b)
    b, _, _ = textbox(455, 185, "GraphQL\nодин граф, багато\nрізних екранів", size=13, fill="#f2ecfb")
    frags.append(b)

    # четверта вісь — час
    frags.append(text(440, 540,
                      "інша вісь — ЧАС: не треба відповіді зараз → черга, а не запит",
                      size=12, color=MUTED))

    render(os.path.join(IMG, "choice-map.svg"), W, H, *frags,
           title="Мапа вибору стилю")


def fig_roundtrip_cascade():
    """Обертів до сервера на ту саму панель: REST-водоспад (3 хвилі) проти 1 оберту."""
    W, H = 980, 396
    frags = []

    # ── Рядок 1: REST-водоспад ──
    frags.append(text(150, 106, "REST-водоспад", size=15, bold=True))
    frags.append(text(150, 128, "платить за глибину", size=12, color=MUTED))
    frags.append(fitbox(270, 84, 190, 54, "хвиля 1\nдім · 1 запит", size=13, fill="#eef2fb"))
    frags.append(fitbox(460, 84, 190, 54, "хвиля 2\n5 кімнат ∥", size=13, fill="#eef2fb"))
    frags.append(fitbox(650, 84, 190, 54, "хвиля 3\n15 пристроїв ∥", size=13, fill="#eef2fb"))
    frags.append(text(555, 170, "3 хвилі × 150 мс = 450 мс", size=13, color=MUTED))

    # ── Рядок 2: GraphQL / gRPC ──
    frags.append(text(150, 230, "GraphQL / gRPC", size=15, bold=True))
    frags.append(text(150, 252, "зібрана форма", size=12, color=MUTED))
    frags.append(fitbox(270, 208, 190, 54, "1 оберт\nформа за 1 захід", size=13, fill="#eef7f0"))
    frags.append(text(700, 228, "1 × 150 мс = 150 мс", size=13, color=MUTED))
    frags.append(text(700, 250, "утричі менша глибина", size=12, color=MUTED))

    # ── Вісь часу ──
    frags.append(arrow(270, 330, 885, 330, color=LINE, sw=1.6))
    for tx, lbl in ((270, "0"), (460, "150"), (650, "300"), (840, "450")):
        frags.append(line(tx, 326, tx, 334, color=LINE, sw=1.4))
        frags.append(text(tx, 352, lbl, size=12, color=MUTED))
    frags.append(text(555, 378, "час, мс  →", size=12, color=MUTED))

    render(os.path.join(IMG, "roundtrip-cascade.svg"), W, H, *frags,
           title="Обертів до сервера на ту саму панель")


AMBER = "#b45309"


def fig_lineage_timeline():
    """Три нитки походження, що сходяться до середини 2010-х: RPC→gRPC, Веб→REST, мобільний→GraphQL."""
    W, H = 1180, 600
    frags = []

    x0, x1 = 90.0, 1110.0
    Y0, Y1 = 1980.0, 2016.0
    def X(year):
        return x0 + (year - Y0) * (x1 - x0) / (Y1 - Y0)

    GREEN, BLUE, PURP = FIELD, NEG, PURPLE
    gb, bb, pb = 140, 320, 460          # базові лінії трьох ниток
    axis_y = 560

    # ── легенда кольорів (нитки) ──
    def legitem(cx, color, fill, label):
        return (circle(cx, 50, 7, fill=fill, stroke=color, sw=2) +
                text(cx + 13, 54, label, size=12, color=INK, anchor="start"))
    frags.append(legitem(118, GREEN, "#eef7f0", "Мрія RPC → gRPC"))
    frags.append(legitem(300, BLUE, "#eef2fb", "Веб описав себе → REST"))
    frags.append(legitem(575, PURP, "#f2ecfb", "Біль мобільної стрічки → GraphQL"))

    # ── смуга-виноска 2015 (позаду рамок; з розривами під вузлами 2015, щоб не різати текст) ──
    x2015 = X(2015)
    for gy0, gy1 in ((76, 158), (234, 366), (442, axis_y)):
        frags.append(line(x2015, gy0, x2015, gy1, color=MUTED, sw=1.2, dash="4,5"))
    frags.append(text(x2015, 70, "2015", size=12, color=MUTED))

    # ── три базові лінії ниток ──
    frags.append(line(x0, gb, X(2015), gb, color=GREEN, sw=2.4))
    frags.append(line(X(1991), bb, X(2000), bb, color=BLUE, sw=2.4))
    frags.append(line(X(2012), pb, X(2015), pb, color=PURP, sw=2.4))

    # ── SOAP/WS-* — тиск, що виніс REST у мейнстрим ──
    sx0, sx1, sy = X(1998), X(2003), 418
    frags.append(line(sx0, sy, sx1, sy, color=AMBER, sw=2.2))
    frags.append(line(sx0, sy - 6, sx0, sy + 6, color=AMBER, sw=2.2))
    frags.append(line(sx1, sy - 6, sx1, sy + 6, color=AMBER, sw=2.2))
    frags.append(text((sx0 + sx1) / 2, sy + 20,
                      "SOAP / WS-* тяжчають → тиск, що виніс REST у мейнстрим",
                      size=11, color=AMBER))

    # ── вузол: крапка на нитці + рамка-підпис над/під ──
    def node(year, side, label, color, fill):
        cx = X(year)
        base = {GREEN: gb, BLUE: bb, PURP: pb}[color]
        cy = base - 56 if side == "up" else base + 56
        out = [line(cx, base, cx, cy, color=color, sw=1.2)]
        b, _, _ = textbox(cx, cy, label, size=12, fill=fill, stroke=color, sw=1.4)
        out.append(b)
        out.append(circle(cx, base, 4.5, fill=color, stroke=color, sw=1))
        return out

    # RPC → gRPC (зелена)
    frags += node(1981, "up",   "1981\nтермін «RPC» (Нельсон)", GREEN, "#eef7f0")
    frags += node(1984, "down", "1984\nБірелл–Нельсон:\nреалізація", GREEN, "#eef7f0")
    frags += node(1991, "up",   "1991\nCORBA (OMG)", GREEN, "#eef7f0")
    frags += node(1994, "down", "1994\n«local ≠ remote»", GREEN, "#eef7f0")
    frags += node(2001, "up",   "≈2001\nGoogle Stubby", GREEN, "#eef7f0")
    frags += node(2015, "down", "2015\ngRPC → у світ\nHTTP/2 · protobuf", GREEN, "#eef7f0")

    # Веб → REST (синя)
    frags += node(1991, "down", "1991\nВеб масштабується", BLUE, "#eef2fb")
    frags += node(1997, "up",   "1997–99\nHTTP/1.1 (Філдінг)", BLUE, "#eef2fb")
    frags += node(2000, "down", "2000\nдисертація:\nREST", BLUE, "#eef2fb")

    # мобільний → GraphQL (фіолетова)
    frags += node(2012, "down", "2012\nбіль стрічки FB\nSuperGraph", PURP, "#f2ecfb")
    frags += node(2015, "up",   "2015\nпублічно\nReact.js Conf", PURP, "#f2ecfb")

    # ── вісь років ──
    frags.append(line(x0, axis_y, x1, axis_y, color=LINE, sw=1.6))
    for yr in (1980, 1985, 1990, 1995, 2000, 2005, 2010, 2015):
        frags.append(line(X(yr), axis_y, X(yr), axis_y + 6, color=LINE, sw=1.4))
        frags.append(text(X(yr), axis_y + 22, str(yr), size=11, color=MUTED))

    render(os.path.join(IMG, "lineage-timeline.svg"), W, H, *frags,
           title="Родовід трьох стилів: три походження, що сходяться")


def fig_origin_bias():
    """Пологовий біль → стиль → вроджене упередження (рідне середовище)."""
    W, H = 1160, 470
    frags = []

    # шапки колонок
    frags.append(text(230, 66, "ПОЛОГОВИЙ БІЛЬ", size=12, color=MUTED))
    frags.append(text(580, 66, "СТИЛЬ", size=12, color=MUTED))
    frags.append(text(915, 66, "ВРОДЖЕНЕ УПЕРЕДЖЕННЯ · РІДНЕ СЕРЕДОВИЩЕ", size=12, color=MUTED))

    lx, lw = 50, 360
    bx, bw = 500, 160
    rx, rw = 740, 380
    ch = 92

    def row(cy, pain, style, bias, color, fill):
        out = []
        out.append(fitbox(lx, cy - ch / 2, lw, ch, pain, size=13))
        out.append(arrow(lx + lw + 6, cy, bx - 6, cy, color=color, sw=2.2))
        b, _, _ = textbox(bx + bw / 2, cy, style, size=19, bold=True,
                          fill=fill, stroke=color, sw=2, min_w=bw)
        out.append(b)
        out.append(arrow(bx + bw + 6, cy, rx - 6, cy, color=color, sw=2.2))
        out.append(fitbox(rx, cy - ch / 2, rw, ch, bias, size=13, fill=fill, stroke=color))
        return out

    frags += row(130,
                 "Веб уже масштабувався\nсам; SOAP/WS-*\nдедалі тяжчали",
                 "REST",
                 "відкритість, без стану, єдині\nдієслова, їде на HTTP-інфрі —\nпід чужих некерованих клієнтів",
                 NEG, "#eef2fb")
    frags += row(258,
                 "30 років мрії RPC\n(Нельсон → CORBA) +\nвнутрішня шкала Google",
                 "gRPC",
                 "щільний типізований контракт,\nшвидкість, генерований клієнт —\nсвій сервіс до свого сервіса",
                 FIELD, "#eef7f0")
    frags += row(386,
                 "мобільна стрічка задихалась:\nбагато екранів, кепський\nканал, недобір і перебір",
                 "GraphQL",
                 "форму відповіді малює сам\nклієнт — один багатий граф\nпід багато різних облич",
                 PURPLE, "#f2ecfb")

    render(os.path.join(IMG, "origin-bias.svg"), W, H, *frags,
           title="Походження — це упередження")


if __name__ == "__main__":
    fig_unit_of_conversation()
    fig_temporal_coupling()
    fig_choice_map()
    fig_roundtrip_cascade()
    fig_lineage_timeline()
    fig_origin_bias()
    print("OK: unit-of-conversation.svg, temporal-coupling.svg, choice-map.svg, "
          "roundtrip-cascade.svg, lineage-timeline.svg, origin-bias.svg")

# -*- coding: utf-8 -*-
"""Фігури до кроку «Стійкий шлях команди DH»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

RED_FILL = "#fdecea"
GREEN_FILL = "#eafaf0"
BLUE_FILL = "#e6eefb"
AMBER_FILL = "#fff4e0"
AMBER = "#c77800"
GRAY_FILL = "#f0f0f2"


def fig_cascade():
    """Спільний пул топить усіх; перебірки тримають потоп в одному відсіку."""
    W, H = 1200, 680
    frags = []

    REQX, REQW = 210, 250
    POOLX = 620
    OUTX = 1050

    # ── ВЕРХНЯ СМУГА: спільний пул ──
    frags.append(text(W / 2, 74, "СПІЛЬНИЙ ПУЛ НА ВСІХ — повільна телеметрія забиває його весь",
                      size=16, bold=True, color=POS))

    reqs_top = [
        (150, "список пристроїв · швидко", INK, FILL),
        (208, "команда «зачинити» · швидко", INK, FILL),
        (266, "екран + телеметрія · 5 с", POS, RED_FILL),
    ]
    for y, lbl, col, fl in reqs_top:
        b, _, _ = textbox(REQX, y, lbl, size=12.5, bold=(fl == RED_FILL),
                          fill=fl, stroke=(POS if fl == RED_FILL else INK),
                          sw=1.5, color=col, min_w=REQW)
        frags.append(b)

    # спільний пул — червона забита коробка
    pw, ph, py = 250, 150, 133
    frags.append(rect(POOLX - pw / 2, py, pw, ph, fill=RED_FILL, stroke=POS, sw=2))
    frags.append(mtext(POOLX, py + 58, ["СПІЛЬНИЙ пул BFF (20)", "усі слоти зайняті",
                                        "повільною телеметрією"], size=13, bold=True, color=POS))
    # слоти-рисочки, всі червоні
    for i in range(10):
        sx = POOLX - pw / 2 + 18 + i * 22
        frags.append(rect(sx, py + ph - 26, 14, 14, fill=POS, stroke=POS, sw=1, rx=2))

    # повільний запит → пул
    frags.append(arrow(REQX + REQW / 2 + 6, 266, POOLX - pw / 2 - 6, 208, color=POS, sw=2))
    # швидкі запити впираються: ✗ нема слота
    frags.append(text(POOLX - pw / 2 - 92, 150, "✗", size=20, bold=True, color=POS))
    frags.append(text(POOLX - pw / 2 - 92, 170, "нема слота", size=11, color=MUTED))
    frags.append(text(POOLX - pw / 2 - 92, 208, "✗", size=20, bold=True, color=POS))

    # пул → вихід
    frags.append(arrow(POOLX + pw / 2 + 6, 208, OUTX - 96, 208, color=POS, sw=2))
    ob, _, _ = textbox(OUTX, 208, "увесь застосунок\nвисить", size=13.5, bold=True,
                       fill=RED_FILL, stroke=POS, sw=2, color=POS, min_w=196)
    frags.append(ob)

    # ── роздільник ──
    frags.append(line(60, 355, W - 60, 355, color=MUTED, sw=1.2, dash="7,7"))

    # ── НИЖНЯ СМУГА: перебірки ──
    frags.append(text(W / 2, 402, "ПЕРЕБІРКИ — кожній залежності свій відсік",
                      size=16, bold=True, color=FIELD))

    reqs_bot = [
        (470, "список пристроїв · швидко", INK, FILL),
        (528, "команда «зачинити» · швидко", INK, FILL),
        (586, "екран + телеметрія · 5 с", NEG, BLUE_FILL),
    ]
    for y, lbl, col, fl in reqs_bot:
        b, _, _ = textbox(REQX, y, lbl, size=12.5, bold=(fl != FILL),
                          fill=fl, stroke=(NEG if fl == BLUE_FILL else INK),
                          sw=1.5, color=col, min_w=REQW)
        frags.append(b)

    # два пули: телеметрії (забитий, але окремий) і решти (вільний)
    frags.append(rect(POOLX - 130, 445, 260, 62, fill=RED_FILL, stroke=POS, sw=1.8))
    frags.append(mtext(POOLX, 470, ["пул телеметрії (10)", "забитий — але лише він"],
                       size=12.5, bold=True, color=POS))
    frags.append(rect(POOLX - 130, 552, 260, 62, fill=GREEN_FILL, stroke=FIELD, sw=1.8))
    frags.append(mtext(POOLX, 577, ["пул ядра й команд", "вільний — течуть далі"],
                       size=12.5, bold=True, color=FIELD))

    frags.append(arrow(REQX + REQW / 2 + 6, 586, POOLX - 130 - 6, 476, color=POS, sw=1.8))
    frags.append(arrow(REQX + REQW / 2 + 6, 470, POOLX - 130 - 6, 570, color=FIELD, sw=1.8))
    frags.append(arrow(REQX + REQW / 2 + 6, 528, POOLX - 130 - 6, 583, color=FIELD, sw=1.8))

    frags.append(arrow(POOLX + 130 + 6, 583, OUTX - 96, 545, color=FIELD, sw=1.9))
    ob2, _, _ = textbox(OUTX, 545, "телеметрія → «—»,\nрешта працює", size=13.5, bold=True,
                        fill=GREEN_FILL, stroke=FIELD, sw=2, color=FIELD, min_w=196)
    frags.append(ob2)

    render(os.path.join(IMG, "cascade.svg"), W, H, *frags,
           title="Один повільний сервіс: спільний пул проти перебірок")


def _state(cx, cy, title_, sub, fill, stroke, color):
    b, w, h = textbox(cx, cy, title_ + "\n" + sub, size=13, bold=True,
                      fill=fill, stroke=stroke, sw=2.2, color=color, min_w=210)
    return b, w, h


def fig_breaker_states():
    """Три стани запобіжника й переходи між ними."""
    W, H = 1120, 470
    frags = []

    CY = 190
    XC, XO, XH = 190, 560, 930

    cb, cw, _ = _state(XC, CY, "ЗАКРИТИЙ", "викликає, лічить відмови",
                       GREEN_FILL, FIELD, FIELD)
    obx, ow, _ = _state(XO, CY, "ВІДКРИТИЙ", "не викликає — миттєвий фолбек",
                        RED_FILL, POS, POS)
    hb, hw, _ = _state(XH, CY, "НАПІВВІДКРИТИЙ", "пропускає ОДИН пробний",
                       AMBER_FILL, AMBER, AMBER)

    # closed → open
    frags.append(arrow(XC + cw / 2 + 6, CY - 12, XO - ow / 2 - 6, CY - 12, color=POS, sw=2))
    frags.append(text((XC + XO) / 2, CY - 30, "N відмов поспіль", size=12.5, bold=True, color=POS))

    # open → half-open
    frags.append(arrow(XO + ow / 2 + 6, CY - 12, XH - hw / 2 - 6, CY - 12, color=AMBER, sw=2))
    frags.append(text((XO + XH) / 2, CY - 30, "минув час охолодження", size=12.5, bold=True, color=AMBER))

    # half-open → closed (ok) — довга дуга зверху
    frags.append(text(W / 2, 92, "пробний ✓  →  назад у ЗАКРИТИЙ", size=13, bold=True, color=FIELD))
    frags.append(line(XH, CY - 44, XH, 108, color=FIELD, sw=1.8))
    frags.append(line(XH, 108, XC, 108, color=FIELD, sw=1.8))
    frags.append(arrow(XC, 108, XC, CY - 44, color=FIELD, sw=1.8))

    # half-open → open (fail) — дуга знизу
    frags.append(text((XO + XH) / 2, 330, "пробний ✗  →  знову ВІДКРИТИЙ", size=12.5, bold=True, color=POS))
    frags.append(line(XH, CY + 44, XH, 300, color=POS, sw=1.8))
    frags.append(line(XH, 300, XO, 300, color=POS, sw=1.8))
    frags.append(arrow(XO, 300, XO, CY + 44, color=POS, sw=1.8))

    frags += [cb, obx, hb]

    frags.append(text(W / 2, 432,
                      "Відкритий запобіжник дає вмирущому сервісу відхекатися, а викличнику — не марнувати таймаут на кожен виклик.",
                      size=13, color=MUTED))

    render(os.path.join(IMG, "breaker-states.svg"), W, H, *frags,
           title="Три стани запобіжника")


def fig_stack_order():
    """Порядок обгорток на одному виклику, ззовні всередину, і рейка фолбека."""
    W, H = 1100, 540
    frags = []

    bands = [
        (70, 90, 700, 400, FILL, INK, "Перебірка — узяти слот з пулу телеметрії (≤ 10)"),
        (120, 145, 600, 290, "#fbfcfe", NEG, "Запобіжник — відкритий? одразу фолбек, без виклику"),
        (170, 200, 500, 180, "#fbfcfe", INK, "Таймаут — стеля на цю спробу"),
    ]
    for x, y, w, h, fl, st, lbl in bands:
        frags.append(rect(x, y, w, h, fill=fl, stroke=st, sw=1.9))
        frags.append(text(x + 16, y + 24, lbl, size=13, bold=True, color=st, anchor="start"))

    # ядро — сам виклик
    frags.append(rect(220, 255, 400, 90, fill=BLUE_FILL, stroke=NEG, sw=2))
    frags.append(mtext(420, 292, ["Виклик  telemetry.lastReadings()",
                                  "повтор — усередині; його відмови лічить запобіжник"],
                       size=12.5, bold=True, color=INK))

    # рейка фолбека праворуч
    frags.append(rect(830, 145, 200, 245, fill=GREEN_FILL, stroke=FIELD, sw=2))
    frags.append(mtext(930, 250, ["ФОЛБЕК", "пристрій", "без останнього", "виміру"],
                       size=14, bold=True, color=FIELD))
    frags.append(arrow(720 + 4, 300, 830 - 6, 260, color=FIELD, sw=1.9))
    frags.append(text(785, 250, "відмова /", size=11, color=FIELD))
    frags.append(text(785, 266, "таймаут →", size=11, color=FIELD))
    frags.append(arrow(670, 200, 830 - 6, 190, color=FIELD, sw=1.8))
    frags.append(text(775, 176, "відкритий →", size=11, color=FIELD))

    frags.append(text(W / 2, 500,
                      "Обгортки стоять у певному порядку: слот → перевірка запобіжника → стеля часу → виклик; будь-який шар може зійти на фолбек.",
                      size=13, color=MUTED))

    render(os.path.join(IMG, "stack-order.svg"), W, H, *frags,
           title="Стійкий шлях одного виклику, ззовні всередину")


def fig_lineage():
    """Родовід «патернів стійкості»: метафори → іменування → промислові бібліотеки."""
    W, H = 1500, 560
    frags = []

    SPINE = 300
    LX, RX = 120, 1380

    frags.append(text(W / 2, 60, "(порядок подій, не в масштабі часу)", size=13, color=MUTED))

    # спина часу зі стрілкою вправо
    frags.append(arrow(LX, SPINE, RX, SPINE, color=INK, sw=2.5))

    # вузли: (x, рік, рядки, above?, колір, заливка)
    nodes = [
        (200, "Сун · 1924", ["Метафори з інженерії:", "переділка судна", "й автомат Штотца"],
         False, INK, GRAY_FILL),
        (420, "2007", ["«Release It!»", "Нюґард називає", "сімейство патернів"],
         True, NEG, BLUE_FILL),
        (640, "2012", ["Netflix Hystrix —", "патерн на", "промисловий масштаб"],
         False, FIELD, GREEN_FILL),
        (860, "2014", ["Fowler", "популяризує", "запобіжник"],
         True, INK, FILL),
        (1080, "2018", ["Hystrix →", "режим підтримки"],
         False, POS, RED_FILL),
        (1290, "після 2018", ["resilience4j,", "Sentinel —", "спадкоємці"],
         True, NEG, BLUE_FILL),
    ]

    for x, yr, lines, above, col, fl in nodes:
        # точка на спині
        frags.append(circle(x, SPINE, 8, fill=col, stroke=col, sw=2))
        if above:
            box, bw, bh = textbox(x, 150, "\n".join(lines), size=12.5, bold=True,
                                  fill=fl, stroke=col, sw=1.8, color=col, min_w=200)
            frags.append(line(x, SPINE - 12, x, 150 + bh / 2, color=col, sw=1.4, dash="3,4"))
            frags.append(text(x + 13, SPINE - 22, yr, size=14, bold=True, color=col, anchor="start"))
            frags.append(box)
        else:
            box, bw, bh = textbox(x, 430, "\n".join(lines), size=12.5, bold=True,
                                  fill=fl, stroke=col, sw=1.8, color=col, min_w=200)
            frags.append(line(x, SPINE + 12, x, 430 - bh / 2, color=col, sw=1.4, dash="3,4"))
            frags.append(text(x + 13, SPINE + 32, yr, size=14, bold=True, color=col, anchor="start"))
            frags.append(box)

    frags.append(text(W / 2, 530,
                      "Метафори дали образ, «Release It!» — спільні імена, Hystrix — промислову машинерію; "
                      "коли Hystrix пішов у підтримку, патерн лишився й переїхав до спадкоємців.",
                      size=13, color=MUTED))

    render(os.path.join(IMG, "lineage.svg"), W, H, *frags,
           title="Родовід «патернів стійкості»: від метафор до промислових бібліотек")


def fig_client_stack():
    """Один клієнт, стос політики на кожну залежність, фолбек — вибір КАЛЛЕРА."""
    W, H = 1220, 560
    frags = []

    CALLX, CALLW = 210, 320
    CLIX, CLIW = 620, 330
    OUTX, OUTW = 1055, 250

    # ── КАЛЛЕРИ (ліворуч) ──
    callers = [
        (130, "головний екран\nчитання останнього виміру", INK, FILL),
        (300, "головний екран\nсписок пристроїв", INK, FILL),
        (430, "команда «зачинити»\nкритичний шлях", POS, RED_FILL),
    ]
    for y, lbl, col, fl in callers:
        b, _, _ = textbox(CALLX, y, lbl, size=12.5, bold=True, fill=fl,
                          stroke=(POS if fl == RED_FILL else INK), sw=1.6,
                          color=col, min_w=CALLW)
        frags.append(b)

    # ── КЛІЄНТИ (центр): telemetry (свій пул) і core (свій пул) ──
    tb, tw, _ = textbox(CLIX, 130,
        "ServiceClient «telemetry»\nresolve → реєстр\nпул 10 · fail-fast\nзапобіжник 5 / 2с · таймаут 3с",
        size=12, fill=BLUE_FILL, stroke=NEG, sw=1.8, color=INK, min_w=CLIW)
    frags.append(tb)

    cb, cw, _ = textbox(CLIX, 365,
        "ServiceClient «core»\nresolve → реєстр\nпул 40 · черга 40\nзапобіжник 10 / 1с · таймаут 1с",
        size=12, fill=BLUE_FILL, stroke=NEG, sw=1.8, color=INK, min_w=CLIW)
    frags.append(cb)

    # ── ВИХОДИ (праворуч) ──
    ob1, _, _ = textbox(OUTX, 130, "фолбек каллера:\n«—» без виміру", size=12.5, bold=True,
                        fill=GREEN_FILL, stroke=FIELD, sw=1.9, color=FIELD, min_w=OUTW)
    ob2, _, _ = textbox(OUTX, 300, "список пристроїв", size=12.5, bold=True,
                        fill=FILL, stroke=INK, sw=1.6, color=INK, min_w=OUTW)
    ob3, _, _ = textbox(OUTX, 430, "БЕЗ фолбека:\nчесна відмова «спробуйте ще»", size=12, bold=True,
                        fill=AMBER_FILL, stroke=AMBER, sw=1.9, color=AMBER, min_w=OUTW)
    frags += [ob1, ob2, ob3]

    # ── СТРІЛКИ каллер → клієнт ──
    frags.append(arrow(CALLX + CALLW / 2 + 6, 130, CLIX - tw / 2 - 6, 130, color=NEG, sw=1.8))
    frags.append(arrow(CALLX + CALLW / 2 + 6, 300, CLIX - cw / 2 - 6, 350, color=NEG, sw=1.8))
    frags.append(arrow(CALLX + CALLW / 2 + 6, 430, CLIX - cw / 2 - 6, 385, color=POS, sw=1.9))

    # ── СТРІЛКИ клієнт → вихід ──
    frags.append(arrow(CLIX + tw / 2 + 6, 130, OUTX - OUTW / 2 - 6, 130, color=FIELD, sw=1.9))
    frags.append(arrow(CLIX + cw / 2 + 6, 350, OUTX - OUTW / 2 - 6, 300, color=INK, sw=1.6))
    frags.append(arrow(CLIX + cw / 2 + 6, 385, OUTX - OUTW / 2 - 6, 430, color=AMBER, sw=1.9))

    frags.append(text(W / 2, H - 20,
        "Той самий клієнт на кожен шов; окремий пул на залежність — окремий радіус ураження. "
        "Фолбек не в клієнті, а в каллера: читання деградує до «—», команда не бреше.",
        size=12.5, color=MUTED))

    render(os.path.join(IMG, "client-stack.svg"), W, H, *frags,
           title="Спільний клієнт: стос на кожну залежність, фолбек — у каллера")


def fig_burst_test():
    """Задушена телеметрія: пул тримає потоп, ядро тече, екран деградує до «—»."""
    W, H = 1200, 660
    frags = []

    frags.append(line(W / 2, 66, W / 2, 545, color=MUTED, sw=1.2, dash="7,7"))

    # ── ЛІВА панель: телеметрію задушено ──
    frags.append(text(300, 70, "ТЕЛЕМЕТРІЮ ЗАДУШЕНО — затримка 5 с", size=15, bold=True, color=POS))
    frags.append(rect(120, 92, 360, 96, fill=RED_FILL, stroke=POS, sw=2))
    frags.append(text(300, 116, "пул телеметрії — 10 слотів зайнято", size=12.5, bold=True, color=POS))
    for i in range(10):
        frags.append(rect(138 + i * 33, 142, 22, 30, fill=POS, stroke=POS, sw=1, rx=3))
    frags.append(text(300, 206, "висять до таймаута 3 с, тоді скасування", size=11.5, color=MUTED))

    b1, _, _ = textbox(300, 258, "40 викликів → «відсік повний»\nмиттєвий фолбек «—»", size=12.5,
                       bold=True, fill=AMBER_FILL, stroke=AMBER, sw=1.7, color=AMBER, min_w=360)
    b2, _, _ = textbox(300, 340, "після 5 відмов — запобіжник ВІДКРИТИЙ\nдалі виклики не йдуть у телеметрію",
                       size=12, bold=True, fill=RED_FILL, stroke=POS, sw=1.7, color=POS, min_w=360)
    b3, _, _ = textbox(300, 435, "усі 50 екранів: пристрій + «—»\nЖОДЕН не завис назавжди", size=13,
                       bold=True, fill=GREEN_FILL, stroke=FIELD, sw=2, color=FIELD, min_w=360)
    frags += [b1, b2, b3]

    # ── ПРАВА панель: ядро здорове ──
    frags.append(text(900, 70, "ЯДРО ЗДОРОВЕ — свій пул", size=15, bold=True, color=FIELD))
    frags.append(rect(720, 92, 360, 96, fill=GREEN_FILL, stroke=FIELD, sw=2))
    frags.append(text(900, 116, "пул ядра — 40 слотів, тече вільно", size=12.5, bold=True, color=FIELD))
    for i in range(10):
        frags.append(rect(738 + i * 33, 142, 22, 30, fill=FIELD, stroke=FIELD, sw=1, rx=3))
    frags.append(text(900, 206, "телеметрія його не торкнулась", size=11.5, color=MUTED))

    b4, _, _ = textbox(900, 268, "50 списків пристроїв — усі ✓\n10 команд «зачинити» — усі ✓", size=12.5,
                       bold=True, fill=BLUE_FILL, stroke=NEG, sw=1.7, color=INK, min_w=360)
    b5, _, _ = textbox(900, 435, "команди пройшли своїм пулом —\nжодної брехні «зачинено»", size=13,
                       bold=True, fill=GREEN_FILL, stroke=FIELD, sw=2, color=FIELD, min_w=360)
    frags += [b4, b5]

    # ── нижня стрічка тверджень ──
    frags.append(line(80, 560, W - 80, 560, color=MUTED, sw=1))
    frags.append(text(W / 2, 590, "що довів тест:", size=12.5, bold=True, color=INK))
    frags.append(text(W / 2, 616,
        "maxConcurrent(telemetry) ≤ 10   ·   ядро тече, не чекає телеметрію   ·   "
        "10 команд fulfilled   ·   екран деградував, не завис",
        size=12.5, color=FIELD))

    render(os.path.join(IMG, "burst-test.svg"), W, H, *frags,
           title="Тест: задушену телеметрію тримає пул, ядро й команди течуть")


if __name__ == "__main__":
    fig_cascade()
    fig_breaker_states()
    fig_stack_order()
    fig_lineage()
    fig_client_stack()
    fig_burst_test()
    print("OK: cascade, breaker-states, stack-order, lineage, client-stack, burst-test")

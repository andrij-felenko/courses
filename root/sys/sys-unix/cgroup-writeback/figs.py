# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SOFT   = "#fbfcff"
WARM   = "#fdecea"
COOL   = "#eaf0fd"
GREENF = "#eafaf0"
PALE   = "#f4f6f8"


# ── 1. Один потік зворотного запису на пристрій проти потоку на кожну групу ──
def fig_split_of_the_flusher():
    W, H = 1330, 760
    p = []

    # ── верхній ряд: як було ──
    p.append(text(60, 46, "один потік зворотного запису на пристрій — власник губиться на дорозі",
                  size=15, color=POS, anchor="start", bold=True))

    p.append(fitbox(60, 74, 190, 58, "група A\nwrite()", size=13,
                    fill=COOL, stroke=NEG, sw=1.6, color=INK, bold=True))
    p.append(fitbox(60, 152, 190, 58, "група B\nwrite()", size=13,
                    fill=GREENF, stroke=FIELD, sw=1.6, color=INK, bold=True))

    p.append(fitbox(320, 74, 215, 136, "кеш сторінок:\nбрудні сторінки\nобох груп разом",
                    size=13, fill=PALE, stroke=MUTED, sw=1.4, color=INK))
    p.append(fitbox(605, 74, 215, 136, "bdi пристрою:\nОДИН список\nбрудних inode-ів",
                    size=13, fill=PALE, stroke=LINE, sw=1.6, color=INK))
    p.append(fitbox(890, 74, 195, 136, "один потік\nзворотного запису\nна весь пристрій",
                    size=13, fill=PALE, stroke=LINE, sw=1.6, color=INK))
    p.append(fitbox(1155, 74, 155, 136, "bio\nбез власника:\nblkcg root",
                    size=13, fill=WARM, stroke=POS, sw=1.8, color=POS, bold=True))

    p.append(arrow(255, 103, 315, 128))
    p.append(arrow(255, 181, 315, 156))
    p.append(arrow(540, 142, 600, 142))
    p.append(arrow(825, 142, 885, 142))
    p.append(arrow(1090, 142, 1150, 142))

    p.append(text(60, 248, "io.max груп A і B не бачить жодного з цих запитів",
                  size=13, color=POS, anchor="start"))

    p.append(line(40, 278, W - 40, 278, color=MUTED, sw=1.2, dash="6 5"))

    # ── нижній ряд: як стало ──
    p.append(text(60, 322, "свій потік на кожну пару (пристрій, група) — власник їде разом зі сторінкою",
                  size=15, color=FIELD, anchor="start", bold=True))

    p.append(fitbox(60, 372, 190, 58, "група A\nwrite()", size=13,
                    fill=COOL, stroke=NEG, sw=1.6, color=INK, bold=True))
    p.append(fitbox(60, 560, 190, 58, "група B\nwrite()", size=13,
                    fill=GREENF, stroke=FIELD, sw=1.6, color=INK, bold=True))

    p.append(fitbox(320, 366, 215, 70, "сторінки A\nз міткою memcg A", size=12,
                    fill=SOFT, stroke=NEG, sw=1.3, color=INK))
    p.append(fitbox(320, 554, 215, 70, "сторінки B\nз міткою memcg B", size=12,
                    fill=SOFT, stroke=FIELD, sw=1.3, color=INK))

    # рамка bdi, що повністю накриває обидва wb
    p.append(rect(600, 348, 240, 294, fill="#fdfefe", stroke=LINE, sw=1.6, rx=10))
    p.append(text(720, 374, "bdi того самого пристрою", size=12, color=MUTED))
    p.append(fitbox(618, 392, 204, 96, "wb(A)\nсвій список inode-ів,\nсвоя оцінка смуги",
                    size=12, fill=COOL, stroke=NEG, sw=1.6, color=INK))
    p.append(fitbox(618, 526, 204, 96, "wb(B)\nсвій список inode-ів,\nсвоя оцінка смуги",
                    size=12, fill=GREENF, stroke=FIELD, sw=1.6, color=INK))

    p.append(fitbox(905, 392, 185, 96, "свій робочий\nелемент запису", size=12,
                    fill=SOFT, stroke=NEG, sw=1.4, color=INK))
    p.append(fitbox(905, 526, 185, 96, "свій робочий\nелемент запису", size=12,
                    fill=SOFT, stroke=FIELD, sw=1.4, color=INK))

    p.append(fitbox(1155, 392, 155, 96, "bio\nblkcg A", size=13,
                    fill=COOL, stroke=NEG, sw=1.8, color=NEG, bold=True))
    p.append(fitbox(1155, 526, 155, 96, "bio\nblkcg B", size=13,
                    fill=GREENF, stroke=FIELD, sw=1.8, color=FIELD, bold=True))

    p.append(arrow(255, 401, 315, 401, color=NEG))
    p.append(arrow(255, 589, 315, 589, color=FIELD))
    p.append(arrow(540, 401, 613, 425, color=NEG))
    p.append(arrow(540, 589, 613, 565, color=FIELD))
    p.append(arrow(827, 440, 900, 440, color=NEG))
    p.append(arrow(827, 574, 900, 574, color=FIELD))
    p.append(arrow(1095, 440, 1150, 440, color=NEG))
    p.append(arrow(1095, 574, 1150, 574, color=FIELD))

    p.append(text(60, 684, "гальмо на групі A зупиняє лише список A: сторінки B їдуть далі",
                  size=13, color=FIELD, anchor="start"))
    p.append(text(60, 718, "розділили не лише облік, а й саму одиницю виконання — інакше одна група тримала б чергу всіх",
                  size=12, color=MUTED, anchor="start", italic=True))

    render(os.path.join(OUT, "split-of-the-flusher.svg"), W, H, *p,
           title="Чому bdi довелося розділити на окремі потоки зворотного запису")


# ── 2. Замкнене коло тиску: від io.max назад у write() ───────────────────────
def fig_backpressure_loop():
    W, H = 1140, 560
    p = []

    p.append(text(W / 2, 44, "ціна повертається туди, звідки прийшла",
                  size=16, color=INK, bold=True))

    top_y, bot_y, bh = 100, 372, 84
    xs = [70, 400, 730]
    bw = 280

    p.append(fitbox(xs[0], top_y, bw, bh, "write() бруднить сторінку\nв групі A",
                    size=13, fill=COOL, stroke=NEG, sw=1.6, color=INK))
    p.append(fitbox(xs[1], top_y, bw, bh, "wb(A) подає bio,\nпомічений blkcg A",
                    size=13, fill=SOFT, stroke=LINE, sw=1.5, color=INK))
    p.append(fitbox(xs[2], top_y, bw, bh, "io.max групи A\nпригальмовує саме ці bio",
                    size=13, fill=WARM, stroke=POS, sw=1.8, color=INK))

    p.append(fitbox(xs[2], bot_y, bw, bh, "оцінка смуги запису\nwb(A) падає",
                    size=13, fill=SOFT, stroke=LINE, sw=1.5, color=INK))
    p.append(fitbox(xs[1], bot_y, bw, bh, "частка A у порозі\nбрудних сторінок падає",
                    size=13, fill=SOFT, stroke=LINE, sw=1.5, color=INK))
    p.append(fitbox(xs[0], bot_y, bw, bh, "balance_dirty_pages\nприсипляє того, хто пише",
                    size=13, fill=GREENF, stroke=FIELD, sw=1.8, color=INK))

    p.append(arrow(xs[0] + bw, top_y + bh / 2, xs[1] - 6, top_y + bh / 2))
    p.append(arrow(xs[1] + bw, top_y + bh / 2, xs[2] - 6, top_y + bh / 2))
    p.append(arrow(xs[2] + bw / 2, top_y + bh + 6, xs[2] + bw / 2, bot_y - 8, color=POS))
    p.append(arrow(xs[2] - 6, bot_y + bh / 2, xs[1] + bw + 6, bot_y + bh / 2))
    p.append(arrow(xs[1] - 6, bot_y + bh / 2, xs[0] + bw + 6, bot_y + bh / 2))
    p.append(arrow(xs[0] + bw / 2, bot_y - 8, xs[0] + bw / 2, top_y + bh + 6, color=FIELD))

    p.append(fitbox(410, 232, 320, 88,
                    "поріг брудних сторінок групи\nпропорційний її смузі запису —\nсаме тут коло замикається",
                    size=12, fill="#fffdf5", stroke="#b7791f", sw=1.5, color=INK))

    p.append(text(W / 2, 520,
                  "нікому не довелося вчити write() про io.max: ліміт диска сам знаходить дорогу до системного виклику",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "backpressure-loop.svg"), W, H, *p,
           title="Як обмеження диска доходить до самого write()")


# ── 3. Коли inode міняє власника ─────────────────────────────────────────────
def fig_owner_switch():
    W, H = 1250, 520
    p = []

    p.append(text(W / 2, 44, "вікно історії inode: 2 секунди, шістнадцять комірок по 125 мс",
                  size=15, color=INK, bold=True))

    x0, y0, sw_, sh = 90, 96, 66, 66
    own = 6          # комірки, які ще тримає давній власник
    round1 = 5       # перший обхід зворотного запису забирає щонайбільше 5
    for i in range(16):
        x = x0 + i * sw_
        if i < own:
            p.append(rect(x, y0, sw_ - 6, sh, fill=COOL, stroke=NEG, sw=1.4, rx=4))
        elif i < own + round1:
            p.append(rect(x, y0, sw_ - 6, sh, fill=WARM, stroke=POS, sw=1.6, rx=4))
        else:
            p.append(rect(x, y0, sw_ - 6, sh, fill="#fbd5cf", stroke=POS, sw=1.6, rx=4))

    p.append(text(x0 - 16, y0 + 40, "історія", size=12, color=MUTED, anchor="end"))

    p.append(fitbox(x0, y0 + 108, own * sw_ - 6, 62,
                    "давній власник\nутримує 6 комірок", size=12,
                    fill=SOFT, stroke=NEG, sw=1.4, color=INK))
    p.append(fitbox(x0 + own * sw_, y0 + 108, round1 * sw_ - 6, 62,
                    "перший обхід чужої групи:\nне більш ніж 5 комірок", size=12,
                    fill=SOFT, stroke=POS, sw=1.4, color=INK))
    p.append(fitbox(x0 + (own + round1) * sw_, y0 + 108, (16 - own - round1) * sw_ - 6, 62,
                    "другий обхід:\nще 5 — разом 10", size=12,
                    fill=SOFT, stroke=POS, sw=1.4, color=INK))

    p.append(fitbox(x0, y0 + 214, 16 * sw_ - 6, 76,
                    "межа — понад 8 комірок із 16: чужа група тримала inode більш ніж половину вікна,\n"
                    "і аж тоді ядро переписує власника на неї",
                    size=13, fill=GREENF, stroke=FIELD, sw=1.7, color=INK))

    p.append(text(W / 2, y0 + 330,
                  "один обхід не здатний відібрати inode: щоб набрати 9, потрібні щонайменше два —",
                  size=12, color=MUTED, italic=True))
    p.append(text(W / 2, y0 + 354,
                  "поодинокий сплеск чужого запису власника не міняє, стала течія міняє за секунду",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "owner-switch.svg"), W, H, *p,
           title="Коли inode переходить до групи, що бруднить його найбільше")


# ── 4. Чотири точки вимірювання: де шукати відповідь на кожне питання ──
def fig_measurement_points():
    W, H = 1300, 470
    p = []

    p.append(text(W / 2, 40,
                  "чотири лічильники на шляху одного мегабайта — і місце, де облік міняє одиницю",
                  size=15, color=INK, bold=True))

    xs = [50, 370, 690, 1010]
    BW, BH = 250, 90

    stages = [
        ("процес групи B\nвиконує write()", COOL, NEG),
        ("сторінка кешу\nстає брудною", PALE, MUTED),
        ("inode потрапляє\nу список одного wb", PALE, LINE),
        ("bio лягає\nв чергу пристрою", WARM, POS),
    ]
    for x, (s, f, st) in zip(xs, stages):
        p.append(fitbox(x, 80, BW, BH, s, size=13,
                        fill=f, stroke=st, sw=1.6, color=INK, bold=True))

    for a, b in ((0, 1), (1, 2), (2, 3)):
        p.append(arrow(xs[a] + BW + 6, 125, xs[b] - 6, 125))

    meters = [
        ("секундомір писаря\ntime ./dirtier\nсповільнюється, коли\nспрацював зворотний зв'язок",
         GREENF, FIELD),
        ("memory.stat групи B\nfile_dirty / file_writeback\nоблік ПОСТОРІНКОВИЙ:\nчия сторінка — тій і лічать",
         GREENF, FIELD),
        ("wb_stats пристрою\nWbCgIno та b_dirty\nоблік ПОІНОДНИЙ:\nвласник один на весь файл",
         SOFT, NEG),
        ("io.stat групи-власниці\nwbytes / wios\nсюди приходить\nувесь рахунок",
         WARM, POS),
    ]
    for x, (s, f, st) in zip(xs, meters):
        p.append(fitbox(x, 250, BW, 108, s, size=12,
                        fill=f, stroke=st, sw=1.5, color=INK))

    for x in xs:
        p.append(arrow(x + BW / 2, 176, x + BW / 2, 244))

    p.append(line(655, 66, 655, 378, color=POS, sw=2.0, dash="7,5"))
    p.append(text(655, 408,
                  "тут облік міняє одиницю: сторінка знає власника, а записують назад цілий inode",
                  size=13, color=POS, bold=True))
    p.append(text(655, 434,
                  "розбіжність лічильників ліворуч і праворуч від цієї межі — не хиба вимірювання, а сам механізм",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "measurement-points.svg"), W, H, *p,
           title="Де шукати відповідь на кожне питання про облік буферизованого запису")


fig_split_of_the_flusher()
fig_backpressure_loop()
fig_owner_switch()
fig_measurement_points()
print("ok")

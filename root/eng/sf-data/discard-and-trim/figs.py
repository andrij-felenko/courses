# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

LIVE_FILL = "#dfe8fc"      # дійсне / зайняте
DEAD_FILL = "#fbe6e3"      # мертве, але носій цього не знає
FREE_FILL = "#ffffff"      # вільне
WARM_FILL = "#fff4e0"
COOL_FILL = "#dff0e6"
WARM = "#b8860b"


# ── 1. Два погляди на ту саму ділянку ──────────────────────────────────────
def fig_two_views():
    W, H = 1180, 640
    p = []
    p.append(text(W / 2, 42, "одна ділянка логічних номерів — два погляди на неї",
                  size=18, bold=True, color=INK))

    BX, BW, NC = 320, 800, 20
    CW = BW / NC
    # 0 — вільно за файловою системою, 1 — зайнято живим файлом
    fs_map = [1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0]

    def band(y, h, kinds, fills, strokes):
        out = ""
        for i in range(NC):
            k = kinds[i]
            out += rect(BX + i * CW, y, CW, h, fill=fills[k], stroke=strokes[k],
                        sw=1.4, rx=2)
        return out

    # ── верхній ряд: погляд файлової системи
    p.append(text(60, 118, "файлова система", size=16, bold=True, color=INK, anchor="start"))
    p.append(text(60, 146, "знає, що з файлів живе,", size=13.5, color=MUTED, anchor="start"))
    p.append(text(60, 168, "а що видалили", size=13.5, color=MUTED, anchor="start"))
    p.append(band(112, 62, fs_map,
                  {0: FREE_FILL, 1: LIVE_FILL}, {0: MUTED, 1: NEG}))
    p.append(text(BX, 208, "зайнято: 6 блоків", size=14, bold=True, color=NEG, anchor="start"))
    p.append(text(BX + 260, 208, "вільно: 14 блоків", size=14, bold=True, color=MUTED,
                  anchor="start"))

    # ── стрілка «видалення сюди не доходить»
    p.append(line(60, 268, W - 60, 268, color=MUTED, sw=1, dash="6,6"))
    p.append(fitbox(BX + 130, 286, 540, 52,
                    ["видалення файлу переписує лише карту вгорі —",
                     "у самі блоки при цьому не пишуть нічого"],
                    size=13.5, fill=WARM_FILL, stroke=WARM, sw=1.8))

    # ── нижній ряд: погляд контролера
    ctrl = [1] * NC
    p.append(text(60, 400, "контролер носія", size=16, bold=True, color=INK, anchor="start"))
    p.append(text(60, 428, "знає лише те, у які номери", size=13.5, color=MUTED, anchor="start"))
    p.append(text(60, 450, "колись писали", size=13.5, color=MUTED, anchor="start"))
    p.append(band(394, 62, ctrl, {1: DEAD_FILL}, {1: POS}))
    p.append(text(BX, 490, "дійсних сторінок: 20 із 20", size=14, bold=True, color=POS,
                  anchor="start"))
    p.append(text(BX + 300, 490, "вільного місця для стирання: немає",
                  size=14, color=POS, anchor="start"))

    p.append(fitbox(BX, 530, BW, 62,
                    ["чотирнадцять блоків мертві — але про це знає тільки верхній ряд;",
                     "нижній ряд перекладатиме їх при кожному збиранні сміття"],
                    size=13.5, fill=COOL_FILL, stroke=FIELD, sw=1.8))

    render(os.path.join(IMG, 'two-views.svg'), W, H, *p)


# ── 2. Вирівнювання discard до одиниці обліку ──────────────────────────────
def fig_granularity():
    W, H = 1180, 560
    p = []
    p.append(text(W / 2, 42, "чому дрібний discard не робить нічого",
                  size=18, bold=True, color=INK))

    BX, BW = 150, 900
    UNITS = 6
    UW = BW / UNITS

    # смуга одиниць обліку пристрою
    y = 110
    for i in range(UNITS):
        p.append(rect(BX + i * UW, y, UW, 66, fill=FILL, stroke=LINE, sw=1.6, rx=4))
    p.append(text(BX + BW / 2, y - 24, "одиниці обліку контролера (discard_granularity)",
                  size=14.5, bold=True, color=INK))

    # великий запит: краї неповні
    y2 = 236
    rq_x, rq_w = BX + UW * 0.55, UW * 3.9
    p.append(rect(rq_x, y2, rq_w, 52, fill=LIVE_FILL, stroke=NEG, sw=2, rx=4))
    p.append(text(rq_x + rq_w / 2, y2 + 32, "запит на discard", size=14, bold=True, color=NEG))
    p.append(text(BX - 40, y2 + 32, "великий", size=15, bold=True, color=INK, anchor="end"))

    # що з нього лишиться
    y3 = 330
    keep_x, keep_w = BX + UW * 1, UW * 3
    p.append(rect(BX + UW * 0.55, y3, UW * 0.45, 46, fill=DEAD_FILL, stroke=POS, sw=1.6, rx=3))
    p.append(rect(keep_x, y3, keep_w, 46, fill=COOL_FILL, stroke=FIELD, sw=2, rx=3))
    p.append(rect(BX + UW * 4, y3, UW * 0.45, 46, fill=DEAD_FILL, stroke=POS, sw=1.6, rx=3))
    p.append(text(keep_x + keep_w / 2, y3 + 30, "виконано: 3 цілі одиниці",
                  size=14, bold=True, color=FIELD))
    p.append(text(BX - 40, y3 + 30, "дійшло", size=15, bold=True, color=INK, anchor="end"))
    p.append(text(BX + BW + 40, y3 + 30, "краї відкинуто", size=13.5, color=POS, anchor="start"))

    # дрібний запит
    y4 = 440
    sm_x, sm_w = BX + UW * 1.3, UW * 0.35
    p.append(rect(sm_x, y4, sm_w, 46, fill=LIVE_FILL, stroke=NEG, sw=2, rx=3))
    p.append(text(BX - 40, y4 + 30, "дрібний", size=15, bold=True, color=INK, anchor="end"))
    p.append(text(sm_x + sm_w + 40, y4 + 30,
                  "жодної цілої одиниці не містить — дійшов порожній запит, успішно й безшумно",
                  size=13.5, color=POS, anchor="start"))

    render(os.path.join(IMG, 'granularity.svg'), W, H, *p)


# ── 3. Три маршрути звільнення ─────────────────────────────────────────────
def fig_three_paths():
    W, H = 1240, 700
    p = []
    p.append(text(W / 2, 42, "три маршрути новини «блоки звільнилися»",
                  size=18, bold=True, color=INK))

    COLW, GAP = 350, 55
    X0 = 60

    cols = [
        ("негайно", NEG, LIVE_FILL,
         ["mount -o discard"],
         ["звільнення блоків"],
         ["коміт транзакції", "(раніше не можна:", "збій лишив би дірку)"],
         ["дрібні запити", "просто в шляху запису"]),
        ("відкладено", WARM, WARM_FILL,
         ["mount -o discard=async"],
         ["звільнення блоків"],
         ["список + злиття", "в суцільні діапазони"],
         ["фоновий потік,", "обмежена швидкість"]),
        ("пакетно", FIELD, COOL_FILL,
         ["fstrim / FITRIM"],
         ["таймер раз на тиждень"],
         ["обхід усієї карти", "вільного місця"],
         ["довгі суцільні смуги,", "сплеск раз на тиждень"]),
    ]

    for i, (name, col, fill, src, a, b, c) in enumerate(cols):
        x = X0 + i * (COLW + GAP)
        p.append(text(x + COLW / 2, 92, name, size=16.5, bold=True, color=col))
        p.append(fitbox(x, 110, COLW, 44, src, size=13.5, bold=True, fill=fill, stroke=col, sw=2))
        p.append(arrow(x + COLW / 2, 158, x + COLW / 2, 196, color=col, sw=1.8))
        p.append(fitbox(x, 200, COLW, 44, a, size=13.5, fill=FILL, stroke=MUTED, sw=1.5))
        p.append(arrow(x + COLW / 2, 248, x + COLW / 2, 286, color=col, sw=1.8))
        p.append(fitbox(x, 290, COLW, 74, b, size=13.5, fill=FILL, stroke=MUTED, sw=1.5))
        p.append(arrow(x + COLW / 2, 368, x + COLW / 2, 406, color=col, sw=1.8))
        p.append(fitbox(x, 410, COLW, 62, c, size=13.5, fill=fill, stroke=col, sw=1.8))
        p.append(arrow(x + COLW / 2, 476, x + COLW / 2, 526, color=col, sw=2))

    # спільний низ
    p.append(fitbox(X0, 530, COLW * 3 + GAP * 2, 52,
                    ["блоковий шар: REQ_OP_DISCARD"],
                    size=15, bold=True, fill=FILL, stroke=LINE, sw=2))
    p.append(arrow(W / 2 - 60, 586, W / 2 - 60, 622, color=LINE, sw=2))
    p.append(fitbox(X0 + 190, 626, COLW * 2, 50,
                    ["драйвер транспорту: TRIM · UNMAP · Deallocate"],
                    size=14.5, bold=True, fill=COOL_FILL, stroke=FIELD, sw=2))

    render(os.path.join(IMG, 'three-paths.svg'), W, H, *p)


fig_two_views()
fig_granularity()
fig_three_paths()
print("ok")

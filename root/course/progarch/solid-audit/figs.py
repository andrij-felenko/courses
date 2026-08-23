# -*- coding: utf-8 -*-
"""Фігури до кроку «SOLID разом» (solid-audit).
Три фігури:
  (1) five-lenses   — п'ять лінз S/O/L/I/D сходяться в один злам;
  (2) one-move      — один хід композиції перекидає п'ять оцінок у зелене;
  (3) structure-dial — замало / доречно / забагато структури."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

GREEN_FILL = "#e8f6ee"
RED_FILL   = "#fdecea"
BLUE_FILL  = "#eaf0fd"


# ── Фігура 1: п'ять лінз — один злам ────────────────────────────────────────
def fig_lenses():
    W, H = 1040, 440
    frags = []

    lenses = [
        "S · SRP\nде шов:\nодин актор",
        "O · OCP\nяк перетнути:\nдописуй, не прав",
        "L · LSP\nхто за контрактом:\nчесно тримає",
        "I · ISP\nяка ширина:\nпід клієнта",
        "D · DIP\nкуди дивиться:\nна абстракцію",
    ]
    bx0, bw, gap, by, bh = 21, 190, 12, 48, 94
    centers = []
    for i, s in enumerate(lenses):
        x = bx0 + i * (bw + gap)
        centers.append(x + bw / 2)
        frags.append(fitbox(x, by, bw, bh, s, size=13, bold=False))

    # центральний злам
    kx, kw, ky, kh = 310, 420, 312, 86
    frags.append(fitbox(kx, ky, kw, kh,
                        "ОДИН ЗЛАМ\nволатильне зрощене зі стабільним",
                        size=15, bold=True, fill=RED_FILL, stroke=POS))

    # стрілки: кожна лінза → своя точка на верхньому краю зламу
    targets = [370, 445, 520, 595, 670]
    for cx, tx in zip(centers, targets):
        frags.append(arrow(cx, by + bh, tx, ky, color=LINE, sw=1.8))

    render(os.path.join(IMG, 'five-lenses.svg'), W, H, *frags,
           title="П'ять лінз дивляться на одну ваду")


# ── Фігура 2: один хід — п'ять зелених ──────────────────────────────────────
def fig_one_move():
    W, H = 980, 470
    frags = []

    # БУЛО (ліворуч, червоне)
    frags.append(fitbox(40, 64, 250, 150,
                        "БУЛО\nAlarmDispatcher\nробить усе одразу:\nполітика + текст\n+ Twilio + файл",
                        size=13, bold=False, fill=RED_FILL, stroke=POS))
    # СТАЛО (праворуч, зелене)
    frags.append(fitbox(690, 64, 250, 150,
                        "СТАЛО\nAlarmPolicy — ядро\n+ Notifier / Clock\nподано ззовні;\nадаптери окремо",
                        size=13, bold=False, fill=GREEN_FILL, stroke=FIELD))

    # місток між ними
    frags.append(text(490, 108, "один хід: композиція", size=14, bold=True))
    frags.append(arrow(292, 139, 688, 139, color=INK, sw=2.0))
    frags.append(text(490, 172, "стабільне ядро окремо, деталі — впорснути",
                      size=12, color=MUTED))

    # смуга п'яти оцінок
    frags.append(text(W / 2, 250, "П'ять оцінок після одного ходу", size=15, bold=True))
    rows = [
        ("S", "кожен актор — у власному класі"),
        ("O", "новий канал = новий адаптер, ядро ціле"),
        ("L", "дублер записує, а не вдає — контракт чесний"),
        ("I", "Notifier — один метод, вузько"),
        ("D", "політика спирається на абстракцію, не на Twilio"),
    ]
    ys = [286, 322, 358, 394, 430]
    for (letter, reason), y in zip(rows, ys):
        frags.append(circle(150, y, 9, fill=RED_FILL, stroke=POS, sw=1.8))
        frags.append(arrow(166, y, 196, y, color=LINE, sw=1.6))
        frags.append(circle(212, y, 9, fill=GREEN_FILL, stroke=FIELD, sw=1.8))
        frags.append(text(238, y - 8, letter, size=15, color=INK, anchor="start", bold=True))
        frags.append(text(262, y + 5, reason, size=13, color=INK, anchor="start"))

    render(os.path.join(IMG, 'one-move.svg'), W, H, *frags,
           title="Один хід перекидає всі п'ять у зелене")


# ── Фігура 3: регулятор структури ───────────────────────────────────────────
def fig_dial():
    W, H = 920, 300
    frags = []

    bar_y, bar_h = 112, 60
    zones = [
        (60, 320, RED_FILL, POS, "ЗАМАЛО", 190,
         "грудка болота:\nзміна розповзається"),
        (320, 600, GREEN_FILL, FIELD, "ДОРЕЧНО", 460,
         "шов там, де\nзміна реальна"),
        (600, 860, BLUE_FILL, NEG, "ЗАБАГАТО", 730,
         "передчасна абстракція:\nподаток на непрямість"),
    ]
    for x0, x1, fill, stroke, tag, cx, desc in zones:
        frags.append(rect(x0, bar_y, x1 - x0, bar_h, fill=fill, stroke=stroke, sw=1.8, rx=0))
        frags.append(text(cx, bar_y + bar_h / 2 + 6, tag, size=16, color=INK, bold=True))
        frags.append(mtext(cx, 206, desc, size=12, color=MUTED))

    # вказівник у зелену середину
    frags.append(arrow(460, 72, 460, bar_y - 4, color=INK, sw=2.2))

    frags.append(text(W / 2, 268,
                      "вказівник веде реальний тиск зміни, не бажання «набрати SOLID»",
                      size=13, color=INK))

    render(os.path.join(IMG, 'structure-dial.svg'), W, H, *frags,
           title="Замало і забагато структури — обидва краї коштують")


# ── Фігура 4 (вставка hist): принципи старші за акронім ──────────────────────
def fig_timeline():
    W, H = 1120, 470
    frags = []

    axy = 235                       # вісь часу
    frags.append(line(110, axy, 1012, axy, color=INK, sw=2.2))
    frags.append(arrow(1010, axy, 1042, axy, color=INK, sw=2.2))
    frags.append(text(1054, axy + 5, "час", size=12, color=MUTED, anchor="start"))

    def X(year):
        return 140 + (year - 1987) * ((980 - 140) / (2004 - 1987))

    above = [
        (1988, "1988\nOCP — Бертран Меєр", FILL, LINE),
        (1996, "1996\nDIP · ISP · OCP-переосмислення\nРоберт Мартин, C++ Report", FILL, LINE),
        (2004, "2004\nАКРОНІМ «SOLID»\nМайкл Фезерс", BLUE_FILL, NEG),
    ]
    below = [
        (1987, "1987\nLSP — Барбара Лісков\n(ідея підстановки)", FILL, LINE),
        (1994, "1994\nLSP формалізовано\nЛісков і Вінг", FILL, LINE),
        (2000, "2000\n«Design Principles…»\nМартин збирає п'ять", FILL, LINE),
    ]

    top_y, box_h, box_w = 92, 84, 240
    for yr, s, fill, stroke in above:
        cx = X(yr)
        w = 210 if yr == 2004 else box_w
        frags.append(fitbox(cx - w / 2, top_y, w, box_h, s, size=13, fill=fill, stroke=stroke))
        frags.append(line(cx, top_y + box_h, cx, axy - 7, color=MUTED, sw=1.3))
        frags.append(circle(cx, axy, 6.5, fill=fill, stroke=stroke, sw=2))

    bot_y = 300
    for yr, s, fill, stroke in below:
        cx = X(yr)
        frags.append(fitbox(cx - box_w / 2, bot_y, box_w, box_h, s, size=13, fill=fill, stroke=stroke))
        frags.append(line(cx, axy + 7, cx, bot_y, color=MUTED, sw=1.3))
        frags.append(circle(cx, axy, 6.5, fill=fill, stroke=stroke, sw=2))

    # розрив 2000 → 2004: назва прийшла по тому
    x0, x4 = X(2000), X(2004)
    frags.append(text((x0 + x4) / 2, 191, "+4 роки: лише назва, не новий принцип",
                      size=12, color=NEG))
    frags.append(arrow(x0 + 12, 205, x4 - 12, 205, color=NEG, sw=1.6))

    render(os.path.join(IMG, 'timeline-principles.svg'), W, H, *frags,
           title="Принципи старші за акронім: 1987–2000 проти 2004")


# ── Фігура 5 (вставка proj): об'єктний граф — інверсія залежності ────────────
def fig_object_graph():
    W, H = 1000, 560
    frags = []

    # високий рівень — стабільне ядро
    frags.append(fitbox(380, 70, 240, 74,
                        "AlarmPolicy\n(стабільне ядро — сама політика)",
                        size=13, bold=True, fill=GREEN_FILL, stroke=FIELD))
    frags.append(text(636, 96, "високий рівень", size=12, color=MUTED, anchor="start"))

    # порти — вузькі абстракції (синій контур = абстракція)
    frags.append(fitbox(250, 250, 200, 66, "порт Notifier\nsend(msg)",
                        size=13, bold=True, fill=BLUE_FILL, stroke=NEG))
    frags.append(fitbox(600, 250, 180, 66, "порт Clock\nnow()",
                        size=13, bold=True, fill=BLUE_FILL, stroke=NEG))

    # ядро → порти (залежить від абстракції, стрілка вниз у порт)
    frags.append(arrow(468, 144, 362, 248, color=LINE, sw=1.9))
    frags.append(arrow(532, 144, 678, 248, color=LINE, sw=1.9))

    # низький рівень — адаптери під Notifier
    frags.append(fitbox(40, 432, 156, 60, "SmsNotifier\n(Twilio тут)", size=12))
    frags.append(fitbox(212, 432, 156, 60, "PushNotifier", size=12))
    frags.append(fitbox(384, 432, 156, 60, "EmailNotifier\n(додано пізніше)",
                        size=12, fill=GREEN_FILL, stroke=FIELD))
    frags.append(text(40, 520, "низький рівень — деталі", size=12, color=MUTED, anchor="start"))

    # адаптери → порт Notifier (реалізують, стрілка вгору в абстракцію)
    frags.append(arrow(118, 430, 322, 318, color=LINE, sw=1.6))
    frags.append(arrow(290, 430, 348, 318, color=LINE, sw=1.6))
    frags.append(arrow(462, 430, 374, 318, color=FIELD, sw=1.6))

    # адаптери під Clock
    frags.append(fitbox(576, 432, 160, 60, "SystemClock", size=12))
    frags.append(fitbox(752, 432, 160, 60, "FixedClock\n(тест)", size=12))
    frags.append(arrow(656, 430, 676, 318, color=LINE, sw=1.6))
    frags.append(arrow(832, 430, 712, 318, color=LINE, sw=1.6))

    frags.append(text(W / 2, 544,
                      "і ядро згори, і адаптери знизу залежать від порту — напрям стрілок інвертовано (DIP)",
                      size=13, color=INK))

    render(os.path.join(IMG, 'object-graph.svg'), W, H, *frags,
           title="Хто на кого спирається: і ядро, і адаптери дивляться в порт")


# ── Фігура 6 (вставка proj): контракт-тест як ворота (LSP) ───────────────────
def fig_contract_gate():
    W, H = 1000, 470
    frags = []

    # ворота — контракт
    frags.append(fitbox(400, 116, 200, 244,
                        "КОНТРАКТ\nNotifier\n———\nпісля send(m):\nm є у стоці\nдоставки",
                        size=14, bold=True, fill=FILL, stroke=INK, sw=2.4))

    # кандидати ліворуч
    frags.append(fitbox(48, 112, 250, 60, "RecordingNotifier\nсток = масив прийнятих",
                        size=12, fill=GREEN_FILL, stroke=FIELD))
    frags.append(fitbox(48, 212, 250, 60, "SmsNotifier\nсток = вихідні Twilio",
                        size=12, fill=BLUE_FILL, stroke=NEG))
    frags.append(fitbox(48, 312, 250, 60, "SilentNotifier\nвдає, нічого не шле",
                        size=12, fill=RED_FILL, stroke=POS))

    frags.append(arrow(300, 142, 398, 176, color=FIELD, sw=1.8))
    frags.append(arrow(300, 242, 398, 236, color=NEG, sw=1.8))
    frags.append(arrow(300, 342, 398, 300, color=POS, sw=1.8))

    # праворуч — хто пройшов, той підставний
    frags.append(fitbox(700, 150, 252, 92,
                        "проходить →\nпідставляється всюди,\nде стоїть Notifier",
                        size=12, fill=GREEN_FILL, stroke=FIELD))
    frags.append(arrow(602, 200, 698, 196, color=FIELD, sw=1.8))

    # силента ловлять
    frags.append(fitbox(700, 300, 252, 74,
                        "сток порожній —\nконтракт не виконано,\nдо Notifier не пускають",
                        size=12, fill=RED_FILL, stroke=POS))
    frags.append(arrow(602, 300, 698, 330, color=POS, sw=1.8))

    frags.append(text(W / 2, 448,
                      "той самий контракт-тест женуть на КОЖНУ реалізацію Notifier",
                      size=13, color=INK))

    render(os.path.join(IMG, 'contract-gate.svg'), W, H, *frags,
           title="Контракт-тест — ворота: чесний дублер проходить, «мовчазний» ловиться")


if __name__ == "__main__":
    fig_lenses()
    fig_one_move()
    fig_dial()
    fig_timeline()
    fig_object_graph()
    fig_contract_gate()
    print("ok:", os.listdir(IMG))

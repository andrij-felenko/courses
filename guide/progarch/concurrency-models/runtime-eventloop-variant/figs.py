# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

SLEEP = "#eaf0fd"   # заливка «спить» — холодне
SLEEPST = NEG
LOOPFILL = "#eefaf1"
HOT = "#fdecea"     # заливка гарячого / болю


# ── Фігура 1: чому виграє — арифметика мовчазних з'єднань ─────────────────────
def fig_mem_contrast():
    W, H = 960, 430
    frags = []
    frags.append(text(W / 2, 40, "Мільйон з'єднань, майже завжди мовчать", size=17, bold=True))
    frags.append(line(480, 66, 480, 410, color="#d7dbe0", sw=1.4, dash="7 7"))

    # ── лівий бік: потік на кожну розмову ──
    frags.append(text(240, 64, "Потік на кожну розмову", size=15, bold=True, color=INK))
    for i in range(4):
        y = 80 + i * 38
        frags.append(fitbox(150, y, 180, 32, "потік · стек ≈ 1 МБ", size=12,
                            fill=SLEEP, stroke=SLEEPST, color=INK))
    frags.append(text(240, 250, "⋮   × 10⁶ з'єднань", size=13, color=MUTED))
    frags.append(text(240, 270, "майже всі просто сплять", size=12, color=MUTED, italic=True))
    frags.append(fitbox(52, 292, 376, 104,
                        "10⁶ × 1 МБ ≈ 1 ТБ RAM\n— на розмови, що мовчать\n+ ОС тасує 10⁶ потоків",
                        size=14, fill=HOT, stroke=POS, color=INK))

    # ── правий бік: один цикл подій ──
    frags.append(text(720, 64, "Один цикл подій", size=15, bold=True, color=INK))
    frags.append(fitbox(645, 80, 150, 44, "1 потік\n(цикл подій)", size=13,
                        fill=LOOPFILL, stroke=FIELD, color=INK, bold=True))
    frags.append(fitbox(628, 138, 184, 38, "epoll: хто готовий?", size=13,
                        fill=SLEEP, stroke=SLEEPST, color=INK))
    frags.append(line(720, 176, 720, 190, color=MUTED, sw=1.3))
    for r in range(3):
        for c in range(5):
            frags.append(circle(662 + c * 29, 202 + r * 22, 6, fill=FILL, stroke=MUTED, sw=1.2))
    frags.append(text(720, 274, "стан з'єднання ≈ кілька КБ  ·  × 10⁶",
                      size=12, color=MUTED))
    frags.append(fitbox(532, 292, 376, 104,
                        "10⁶ × ~4 КБ ≈ 4 ГБ RAM\n— влазить в одну коробку\nодин потік, без тасування",
                        size=14, fill=LOOPFILL, stroke=FIELD, color=INK))

    render(os.path.join(OUT, "mem-contrast.svg"), W, H, *frags)


# ── Фігура 2: одна смуга — один блокуючий виклик морозить усіх ────────────────
def fig_single_lane():
    W, H = 960, 360
    frags = []
    frags.append(text(W / 2, 40, "Один потік — одна смуга", size=17, bold=True))

    # смуга
    frags.append(rect(60, 150, 840, 92, fill=FILL, stroke=LINE, sw=1.6, rx=10))
    frags.append(text(72, 142, "смуга = єдиний потік циклу подій", size=12,
                      italic=True, color=MUTED, anchor="start"))

    # черга готових задач, що чекають
    for i in range(3):
        frags.append(fitbox(78 + i * 82, 168, 74, 56, "готова\nзадача", size=11,
                            fill=LOOPFILL, stroke=FIELD, color=INK))
    frags.append(text(160, 262, "готові (epoll сказав), але чекають", size=11,
                      italic=True, color=FIELD))

    # блокуючий виклик у смузі
    frags.append(fitbox(430, 163, 232, 66, "блокуючий / CPU виклик\n· 200 мс ·", size=14,
                        fill=HOT, stroke=POS, color=INK, bold=True))
    frags.append(text(546, 132, "тримає смугу 200 мс", size=12, color=POS))
    frags.append(text(781, 200, "жоден інший обробник не біжить", size=12,
                      italic=True, color=MUTED))

    # контраст унизу
    frags.append(fitbox(60, 286, 410, 60,
                        "Норма: попрацював коротко → await → звільнив смугу.",
                        size=12, fill=LOOPFILL, stroke=FIELD, color=INK))
    frags.append(fitbox(500, 286, 400, 60,
                        "Ціна: один виклик не віддає смугу — і всі сусіди мерзнуть.",
                        size=12, fill=HOT, stroke=POS, color=INK))

    render(os.path.join(OUT, "single-lane.svg"), W, H, *frags)


# ── Фігура 3: колір функції — async піднімається стеком угору ─────────────────
def fig_coloring():
    W, H = 820, 470
    frags = []
    frags.append(text(W / 2, 40, "Асинхронність фарбує стек угору", size=17, bold=True))

    stack = [
        (96,  "вхідна точка сервера"),
        (170, "маршрут /reading"),
        (244, "обробник пристрою"),
        (318, "await читання з сокета"),
    ]
    for (y, label) in stack:
        frags.append(fitbox(170, y, 300, 52, label, size=14,
                            fill=HOT, stroke=POS, color=INK))
    # стрілки «async піднімається» (знизу вгору)
    for i in range(len(stack) - 1, 0, -1):
        y_low = stack[i][0]
        y_up = stack[i - 1][0]
        frags.append(arrow(320, y_low, 320, y_up + 52 + 2, color=POS, sw=2))
    frags.append(text(112, 240, "async", size=12, italic=True, color=POS))
    frags.append(text(112, 258, "піднімається", size=12, italic=True, color=POS))

    # синій, що застряг
    frags.append(fitbox(560, 218, 220, 58, "синхронна функція\n(лишитись blue)", size=13,
                        fill=SLEEP, stroke=SLEEPST, color=INK))
    frags.append(line(558, 250, 476, 258, color=MUTED, sw=1.8, dash="5 5"))
    frags.append(text(516, 242, "✕", size=17, color=POS, bold=True))
    frags.append(text(670, 300, "red із blue напряму не викликати", size=11,
                      italic=True, color=MUTED))

    frags.append(text(W / 2, 436,
                      "Один await знизу — і кожен, хто гукає вгору, теж async.",
                      size=13, color=INK))
    frags.append(text(W / 2, 456,
                      "Синьому лишається стати red — або блокувати потік.",
                      size=12, color=MUTED))

    render(os.path.join(OUT, "coloring.svg"), W, H, *frags)


# ── Фігура 4 (proj): межа offload — що лишається в циклі, що йде в пул ─────────
def fig_offload_boundary():
    W, H = 980, 470
    frags = []
    frags.append(text(W / 2, 40, "Межа offload: цикл тримає ввід-вивід, пул тримає CPU",
                      size=17, bold=True))

    # напис межі — над усім, у проміжку між колонками
    frags.append(text(485, 80, "межа процесу / потоку", size=11, color=MUTED, italic=True))

    # ── лівий бік: цикл подій ──
    frags.append(rect(50, 92, 360, 320, fill=LOOPFILL, stroke=FIELD, sw=1.6, rx=10))
    frags.append(text(230, 122, "Цикл подій · один потік", size=15, bold=True, color=INK))
    for r in range(3):
        for c in range(6):
            frags.append(circle(100 + c * 44, 160 + r * 30, 7, fill=FILL, stroke=MUTED, sw=1.2))
    frags.append(text(230, 268, "сокети: epoll стежить за всіма", size=12, color=MUTED))
    frags.append(fitbox(85, 282, 290, 40, "await I/O — потік нікого не тримає", size=13,
                        fill=SLEEP, stroke=SLEEPST, color=INK))
    frags.append(fitbox(75, 336, 310, 58,
                        "дрібна робота (парсинг JSON,\nпересилання) лишається тут", size=12,
                        fill=FILL, stroke=LINE, color=INK))

    # ── правий бік: пул робітників ──
    frags.append(text(770, 118, "Пул робітників", size=15, bold=True, color=INK))
    frags.append(text(770, 140, "(окремі процеси / потоки)", size=12, color=MUTED, italic=True))
    for i in range(4):
        frags.append(fitbox(600, 158 + i * 58, 330, 46, "робітник · окреме ядро — CPU",
                            size=12, fill=HOT, stroke=POS, color=INK))
    frags.append(text(770, 404, "місячна агрегація рахується тут", size=12, color=MUTED))

    # ── межа й стрілки в проміжку (410..560), розірвана пунктирна вертикаль ──
    frags.append(line(485, 92, 485, 150, color="#d7dbe0", sw=1.4, dash="6 6"))
    frags.append(line(485, 332, 485, 412, color="#d7dbe0", sw=1.4, dash="6 6"))
    frags.append(arrow(410, 214, 560, 214, color=POS, sw=2))
    frags.append(text(485, 202, "важке →", size=12, color=POS, bold=True))
    frags.append(arrow(560, 292, 410, 292, color=FIELD, sw=2))
    frags.append(text(485, 314, "← зведення", size=12, color=FIELD, bold=True))

    frags.append(text(W / 2, 450,
                      "Через межу — лише робота, велика настільки, щоб покрити вартість переходу.",
                      size=12, color=INK))
    render(os.path.join(OUT, "offload-boundary.svg"), W, H, *frags)


# ── Фігура 5 (proj): отруєння смуги та лік через offload (до / після) ──────────
def fig_offload_before_after():
    W, H = 980, 480
    frags = []
    frags.append(text(W / 2, 38, "Отруєння смуги і його лік: винести CPU з циклу",
                      size=17, bold=True))

    # ── ДО ──
    frags.append(text(52, 84, "ДО — важкий рахунок просто в циклі", size=14, bold=True,
                      color=INK, anchor="start"))
    frags.append(rect(50, 96, 880, 68, fill=FILL, stroke=LINE, sw=1.6, rx=8))
    frags.append(fitbox(62, 110, 112, 44, "/reading", size=12, fill=LOOPFILL, stroke=FIELD, color=INK))
    frags.append(fitbox(182, 110, 112, 44, "/health", size=12, fill=LOOPFILL, stroke=FIELD, color=INK))
    frags.append(fitbox(320, 104, 412, 52, "агрегація · 900 мс — тримає смугу", size=14,
                        fill=HOT, stroke=POS, color=INK, bold=True))
    frags.append(text(838, 126, "усі", size=12, color=POS, bold=True))
    frags.append(text(838, 144, "мерзнуть", size=12, color=POS, bold=True))
    frags.append(text(178, 186, "готові, але стоять", size=12, color=FIELD, italic=True))

    # ── ПІСЛЯ ──
    frags.append(text(52, 236, "ПІСЛЯ — агрегацію винесено з циклу", size=14, bold=True,
                      color=INK, anchor="start"))
    frags.append(rect(50, 250, 880, 66, fill=FILL, stroke=LINE, sw=1.6, rx=8))
    for i in range(4):
        frags.append(fitbox(62 + i * 92, 262, 82, 42, "обробник", size=11,
                            fill=LOOPFILL, stroke=FIELD, color=INK))
    frags.append(text(700, 285, "цикл вільний — приймає далі", size=12, color=FIELD, italic=True))
    frags.append(text(250, 338, "короткий обробник → await → звільнив смугу", size=11,
                      color=MUTED, italic=True))

    # робітник унизу
    frags.append(rect(300, 392, 470, 60, fill=FILL, stroke=POS, sw=1.6, rx=8))
    frags.append(fitbox(310, 400, 450, 44, "робітник (окреме ядро): агрегація · 900 мс",
                        size=12, fill=HOT, stroke=POS, color=INK))
    # стрілки між смугою циклу і робітником
    frags.append(arrow(500, 316, 500, 392, color=POS, sw=2))
    frags.append(text(492, 360, "віддав", size=11, color=POS, anchor="end"))
    frags.append(arrow(570, 392, 570, 316, color=FIELD, sw=2))
    frags.append(text(578, 360, "зведення (await)", size=11, color=FIELD, anchor="start"))

    render(os.path.join(OUT, "offload-before-after.svg"), W, H, *frags)


# ── Фігура 6 (вставка hist-c10k): родовід — два фронти однієї проблеми ────────
def fig_c10k_lineage():
    W, H = 1040, 432
    frags = []
    frags.append(text(W / 2, 30, "Родовід C10k: два фронти однієї проблеми", size=17, bold=True))

    # ── іскра-причина (1999) ──
    frags.append(fitbox(360, 46, 320, 48,
                        "1999 · виклик «C10k» (Ден Кегель)\ncdrom.com: ~10 000 клієнтів на однім боксі",
                        size=12, fill=HOT, stroke=POS, color=INK, bold=True))
    frags.append(text(W / 2, 116, "одна провокація — два фронти відповіді:",
                      size=12, italic=True, color=MUTED))

    # ── фронт 1: примітиви ядра ──
    frags.append(text(60, 150, "① Примітиви ядра: «хто готовий?» → «зроблено»",
                      size=13, bold=True, color=NEG, anchor="start"))
    prim = [
        (60,  "select\n4.2BSD · 1983\nсканує всі fd",       FILL,     MUTED, False),
        (250, "poll\nSystem V · ~1986\nсканує всі fd",       FILL,     MUTED, False),
        (440, "kqueue\nFreeBSD · 2000\nЛемон",               LOOPFILL, FIELD, False),
        (630, "epoll\nLinux · 2002\nЛібенці",                LOOPFILL, FIELD, False),
        (820, "io_uring\nLinux · 2019\nАксбо · завершення",  SLEEP,    NEG,   True),
    ]
    for (x, s, fill, st, bold) in prim:
        frags.append(fitbox(x, 164, 170, 60, s, size=12, fill=fill, stroke=st, color=INK, bold=bold))
    for x0 in (230, 420, 610, 800):
        frags.append(arrow(x0, 194, x0 + 20, 194, color=MUTED, sw=2))
    frags.append(line(60, 230, 420, 230, color=POS, sw=1.2))
    frags.append(text(240, 246, "O(N): дорого на 10 000 сплячих", size=11.5, color=POS))
    frags.append(line(440, 230, 800, 230, color=FIELD, sw=1.2))
    frags.append(text(620, 246, "O(готових): інтерес живе в ядрі", size=11.5, color=FIELD))

    # ── фронт 2: крій сервера ──
    frags.append(text(60, 296, "② Крій сервера: процес-на-з'єднання → цикл подій",
                      size=13, bold=True, color=NEG, anchor="start"))
    frags.append(fitbox(60, 312, 220, 64, "Apache\nпроцес / потік\nна з'єднання",
                        size=12, fill=FILL, stroke=MUTED, color=INK))
    frags.append(fitbox(400, 312, 250, 64, "nginx · 2004\nІгор Сисоєв\nцикл подій на epoll / kqueue",
                        size=12, fill=LOOPFILL, stroke=FIELD, color=INK))
    frags.append(fitbox(700, 312, 270, 64, "Node.js · 2009\nРаян Дал\nцикл подій · V8 + пул потоків",
                        size=12, fill=LOOPFILL, stroke=FIELD, color=INK))
    # стіна C10k між Apache і nginx + стрілки крізь неї
    frags.append(arrow(282, 344, 398, 344, color=MUTED, sw=2))
    frags.append(arrow(652, 344, 700, 344, color=MUTED, sw=2))
    frags.append(line(330, 306, 330, 384, color=POS, sw=2.4, dash="6 5"))
    frags.append(text(330, 400, "стіна C10k", size=11, color=POS, bold=True))
    frags.append(line(60, 390, 280, 390, color=POS, sw=1.2))
    frags.append(text(170, 406, "тут уперлося", size=11.5, color=POS))
    frags.append(line(400, 390, 970, 390, color=FIELD, sw=1.2))
    frags.append(text(685, 406, "тут прорвало", size=11.5, color=FIELD))

    render(os.path.join(OUT, "c10k-lineage.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_mem_contrast()
    fig_single_lane()
    fig_coloring()
    fig_offload_boundary()
    fig_offload_before_after()
    fig_c10k_lineage()
    print("figures written")

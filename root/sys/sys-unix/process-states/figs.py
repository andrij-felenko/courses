# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SOFT = "#fbfcff"
WARM = "#fdf3e7"
COLD = "#eef3fd"
PURPLE = "#7a4fb0"


def biarrow(x1, y1, x2, y2, color=LINE, sw=1.8):
    """Лінія зі стрілками з обох кінців (маркер із render() орієнтується сам)."""
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
            'stroke-width="%.1f" marker-start="url(#arrow)" marker-end="url(#arrow)"/>'
            % (x1, y1, x2, y2, color, sw))


# ── 1. Кільце сну: як задача сходить з процесора й як повертається ────────────
def fig_sleep_cycle():
    W, H = 1000, 500
    p = []

    def station(x, y, w, h, head, body, accent, fill):
        out = [rect(x, y, w, h, fill=fill, stroke=accent, sw=2, rx=10)]
        out.append(text(x + w / 2, y + 26, head, size=13, color=accent, bold=True))
        out.append(mtext(x + w / 2, y + 52, body, size=11, color=INK, lh=1.35))
        return "".join(out)

    p.append(station(60, 90, 240, 110, "Черга готових",
                     "задачі зі станом R:\nнічого не бракує,\nбракує лише ядра", NEG, COLD))
    p.append(station(700, 90, 240, 110, "Процесор",
                     "одна задача виконується;\nїй належить\nувесь регістровий стан", FIELD, SOFT))
    p.append(station(700, 340, 240, 110, "Черга очікування",
                     "задача стоїть при об'єкті,\nякого чекає:\nсокет, сторінка, м'ютекс", PURPLE, SOFT))
    p.append(station(60, 340, 240, 110, "Хто розбудить",
                     "перервання від пристрою\nабо інша задача,\nяка дала дані", POS, WARM))

    # верхня стрілка: черга готових → процесор
    p.append(arrow(300, 145, 700, 145))
    p.append(text(500, 130, "планувальник обирає й ставить на процесор", size=11, color=MUTED))

    # права стрілка: процесор → черга очікування
    p.append(arrow(820, 200, 820, 340))
    p.append(mtext(800, 246, ["блокувальний виклик не має даних:",
                              "стан = S або D, далі schedule()"],
                   size=11, color=MUTED, anchor="end"))

    # нижня стрілка: черга очікування → хто розбудить
    p.append(arrow(700, 395, 300, 395))
    p.append(text(500, 424, "поки подія не сталася, задача не є кандидатом на процесор",
                  size=11, color=MUTED))

    # ліва стрілка: хто розбудить → черга готових
    p.append(arrow(180, 340, 180, 200))
    p.append(mtext(200, 246, ["wake_up(): стан = R,",
                              "задача знову в черзі готових"],
                   size=11, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "sleep-cycle.svg"), W, H, *p,
           title="Коло, яким ходить задача: готова → на процесорі → у сні → знову готова")


# ── 2. Граф станів: що переводить задачу з одного стану в інший ───────────────
def fig_state_graph():
    W, H = 1080, 640
    p = []

    def node(cx, cy, label, accent, fill, size=13):
        body, w, h = textbox(cx, cy, label, size=size, pad=14, fill=fill,
                             stroke=accent, sw=2.2, color=INK, bold=True, rx=10)
        return body

    p.append(node(540, 120, "R — готова: на процесорі або в черзі", FIELD, SOFT))
    p.append(node(200, 320, "S — переривний сон", NEG, COLD))
    p.append(node(880, 320, "D — непереривний сон", POS, WARM))
    p.append(node(200, 540, "T — зупинена ззовні", MUTED, FILL))
    p.append(node(880, 540, "Z — зомбі", PURPLE, SOFT))

    # R ↔ S
    p.append(biarrow(415, 148, 258, 292))
    p.append(mtext(275, 249, ["туди: чекання, яке можна перервати",
                              "назад: дані прийшли або сигнал"],
                   size=11, color=MUTED, anchor="end"))

    # R ↔ D
    p.append(biarrow(665, 148, 822, 292))
    p.append(mtext(1040, 249, ["туди: сон усередині вже початої операції",
                               "назад: тільки її завершення"],
                   size=11, color=MUTED, anchor="end"))

    # R ↔ T
    p.append(biarrow(500, 145, 224, 516))
    p.append(mtext(378, 400, ["SIGSTOP, SIGTSTP — зупинити",
                              "SIGCONT — пустити далі"],
                   size=11, color=MUTED, anchor="start"))

    # R → Z
    p.append(arrow(580, 145, 856, 516))
    p.append(mtext(702, 400, ["exit(): ресурси віддано,",
                              "лишився тільки код виходу"],
                   size=11, color=MUTED, anchor="end"))

    # Z зникає
    p.append(arrow(880, 566, 880, 590))
    p.append(text(880, 616, "батько викликав wait() — запис зникає", size=11, color=MUTED))

    p.append(text(60, 616, "стрілки — події, що переводять задачу між станами",
                  size=11, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "state-graph.svg"), W, H, *p,
           title="Стани задачі й події, що ними рухають")


# ── 3. Що сигнал робить зі сплячою задачею — залежно від виду сну ─────────────
def fig_signal_vs_state():
    W, H = 1000, 470
    p = []

    LX, LW = 40, 250
    C1X, C1W = 310, 320
    C2X, C2W = 650, 310

    p.append(fitbox(C1X, 72, C1W, 56, "сигнал, який процес перехопить\n(є обробник)",
                    size=13, fill=COLD, stroke=NEG, sw=2, color=NEG, bold=True))
    p.append(fitbox(C2X, 72, C2W, 56, "сигнал, який процес уб'є\n(SIGKILL, неперехоплений SIGTERM)",
                    size=13, fill=WARM, stroke=POS, sw=2, color=POS, bold=True))

    rows = [
        (140, "S — переривний сон",
         "прокидається;\nвиклик повертає EINTR",
         "прокидається;\nпроцес гине одразу"),
        (250, "D — непереривний сон",
         "не прокидається;\nсигнал чекає в черзі",
         "не прокидається;\nчекає кінця операції"),
        (360, "D — сон із дозволом на смерть",
         "не прокидається;\nсигнал чекає в черзі",
         "прокидається;\nпроцес гине"),
    ]
    for y, lab, c1, c2 in rows:
        p.append(fitbox(LX, y, LW, 90, lab, size=12, fill=FILL, stroke=LINE,
                        sw=1.6, color=INK, bold=True))
        p.append(fitbox(C1X, y, C1W, 90, c1, size=12, fill=SOFT, stroke=NEG, sw=1.6))
        p.append(fitbox(C2X, y, C2W, 90, c2, size=12, fill=SOFT, stroke=POS, sw=1.6))

    render(os.path.join(OUT, "signal-vs-state.svg"), W, H, *p,
           title="Прокинути сплячу задачу може не всякий сигнал")


# ── 4. Смуга лабораторного прогону: п'ять фаз піддослідного ──────────────────
def fig_lab_run():
    W, H = 1220, 500
    p = []

    COLX, COLW, GAP = 210, 180, 16
    cols = [
        ("R", FIELD, SOFT,
         "порожній цикл\nрівно 3 секунди",
         "нічого чекати не треба:\nзадача вже готова",
         "SIGTERM без обробника\n— гине одразу"),
        ("S", NEG, COLD,
         "nanosleep(3 c)",
         "таймер — або\nбудь-який сигнал",
         "SIGTERM без обробника\n— гине одразу"),
        ("T", MUTED, FILL,
         "raise(SIGSTOP)",
         "тільки SIGCONT;\nйого шле спостерігач",
         "SIGTERM без обробника\n— гине без SIGCONT"),
        ("Z", PURPLE, SOFT,
         "дитина вийшла,\nwait() ще не було",
         "wait() від батька",
         "сигнали не діють:\nвиконувати вже нікому"),
        ("D", POS, WARM,
         "clone(CLONE_VFORK):\nбатько чекає дитину",
         "тільки вихід дитини",
         "SIGTERM без обробника\nі SIGKILL — гине від обох"),
    ]

    p.append(text(1180, 70, "усі п'ять — на одному PID, окрім Z: зомбі — це дитина",
                  size=11, color=MUTED, anchor="end"))

    for y, h, lab in ((88, 54, "фаза"), (158, 92, "що робить\nпіддослідний"),
                      (266, 92, "що поверне\nйого в R"), (374, 92, "як діє\nсигнал")):
        p.append(fitbox(40, y, 150, h, lab, size=12, fill=BG, stroke=BG,
                        sw=0, color=MUTED, bold=True))

    for i, (letter, accent, fill, doing, waking, killing) in enumerate(cols):
        x = COLX + i * (COLW + GAP)
        p.append(fitbox(x, 88, COLW, 54, letter, size=26, fill=fill,
                        stroke=accent, sw=2.4, color=accent, bold=True))
        p.append(fitbox(x, 158, COLW, 92, doing, size=12, fill=SOFT,
                        stroke=LINE, sw=1.4, color=INK))
        p.append(fitbox(x, 266, COLW, 92, waking, size=12, fill=FILL,
                        stroke=LINE, sw=1.4, color=INK))
        p.append(fitbox(x, 374, COLW, 92, killing, size=12, fill=SOFT,
                        stroke=accent, sw=1.6, color=INK))

    render(os.path.join(OUT, "lab-run.svg"), W, H, *p,
           title="П'ять фаз піддослідного і що виводить його з кожної")


# ── 5. Звідки беруться три секунди непереривного сну ─────────────────────────
def fig_slow_disk_stack():
    W, H = 1060, 580
    p = []

    BX, BW = 80, 540
    stack = [
        (64, "dd if=/dev/mapper/slowdisk iflag=direct", FIELD, SOFT,
         "процес просить 4 КіБ повз кеш сторінок"),
        (164, "блоковий шар ядра", NEG, COLD,
         "подав bio й ліг спати: TASK_UNINTERRUPTIBLE"),
        (264, "dm-delay: /dev/mapper/slowdisk", POS, WARM,
         "тримає кожен bio рівно 3000 мс"),
        (364, "loop-пристрій /dev/loop0", MUTED, FILL,
         "робить із файлу блоковий пристрій"),
        (464, "файл /var/tmp/slow.img", MUTED, FILL,
         "звичайні 64 МіБ на звичайній файловій системі"),
    ]

    for y, head, accent, fill, note in stack:
        p.append(rect(BX, y, BW, 76, fill=fill, stroke=accent, sw=2, rx=10))
        p.append(text(BX + BW / 2, y + 28, head, size=13, color=accent, bold=True))
        p.append(text(BX + BW / 2, y + 54, note, size=11, color=INK))

    for y in (140, 240, 340, 440):
        p.append(arrow(BX + BW / 2, y, BX + BW / 2, y + 24))

    p.append(fitbox(680, 168, 330, 68,
                    "поки триває ця пауза, задача\nстоїть у D: SIGKILL лягає\nв набір недоправлених",
                    size=12, fill=SOFT, stroke=NEG, sw=1.6, color=INK))
    p.append(arrow(680, 202, 620, 202))

    p.append(fitbox(680, 268, 330, 68,
                    "уся затримка живе тільки тут;\nвище й нижче — звичайні,\nздорові пристрої",
                    size=12, fill=SOFT, stroke=POS, sw=1.6, color=INK))
    p.append(arrow(680, 302, 620, 302))

    p.append(text(80, 556, "розібрати в зворотному порядку: dmsetup remove → losetup -d → rm",
                  size=11, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "slow-disk-stack.svg"), W, H, *p,
           title="Повільний диск, зібраний із файлу: де саме беруться три секунди")


# ── 6. Шлях від бітів __state до однієї літери ───────────────────────────────
def fig_state_letter_path():
    W, H = 1180, 500
    p = []

    # колонка 1: біти поля __state
    p.append(rect(40, 78, 340, 176, fill=COLD, stroke=NEG, sw=2, rx=10))
    p.append(text(210, 100, "у масці TASK_REPORT — видно назовні",
                  size=12, color=NEG, bold=True))
    p.append(mtext(58, 126, [
        "0x0001  TASK_INTERRUPTIBLE",
        "0x0002  TASK_UNINTERRUPTIBLE",
        "0x0004  __TASK_STOPPED",
        "0x0008  __TASK_TRACED",
        "0x0010  EXIT_DEAD  (exit_state)",
        "0x0020  EXIT_ZOMBIE  (exit_state)",
        "0x0040  TASK_PARKED",
    ], size=11, color=INK, anchor="start", lh=1.45))

    p.append(rect(40, 288, 340, 176, fill=FILL, stroke=MUTED, sw=1.8, rx=10))
    p.append(text(210, 310, "поза маскою — назовні не потрапляє",
                  size=12, color=MUTED, bold=True))
    p.append(mtext(58, 336, [
        "0x0080  TASK_DEAD — це не EXIT_DEAD",
        "0x0100  TASK_WAKEKILL — «можна вбити»",
        "0x0200  TASK_WAKING",
        "0x0400  TASK_NOLOAD — не в навантаженні",
        "0x0800  TASK_NEW",
        "0x1000  TASK_RTLOCK_WAIT",
        "0x2000  TASK_FREEZABLE",
        "0x8000  TASK_FROZEN",
    ], size=11, color=INK, anchor="start", lh=1.45))

    # колонка 2: три кроки перетворення
    p.append(rect(430, 78, 310, 110, fill=SOFT, stroke=LINE, sw=1.8, rx=10))
    p.append(text(585, 102, "1. звести до маски", size=12, color=INK, bold=True))
    p.append(mtext(448, 130, [
        "state = (__state | exit_state)",
        "              & TASK_REPORT",
    ], size=11, color=INK, anchor="start", lh=1.5))

    p.append(rect(430, 212, 310, 120, fill=WARM, stroke=POS, sw=1.8, rx=10))
    p.append(text(585, 236, "2. підмінити спецвипадки", size=12, color=POS, bold=True))
    p.append(mtext(448, 264, [
        "TASK_IDLE (0x0402) → 0x80",
        "RTLOCK_WAIT або FROZEN → 0x02",
    ], size=11, color=INK, anchor="start", lh=1.5))

    p.append(rect(430, 368, 310, 96, fill=SOFT, stroke=FIELD, sw=1.8, rx=10))
    p.append(text(585, 392, "3. узяти номер біта", size=12, color=FIELD, bold=True))
    p.append(mtext(585, 418, [
        "index = fls(state)",
        "старший одиничний біт",
    ], size=11, color=INK, lh=1.5))

    # колонка 3: масив рядків стану
    p.append(rect(790, 78, 350, 250, fill=SOFT, stroke=PURPLE, sw=2, rx=10))
    p.append(text(965, 100, "task_state_array[index]", size=12, color=PURPLE, bold=True))
    p.append(mtext(818, 128, [
        "0 → R (running)",
        "1 → S (sleeping)",
        "2 → D (disk sleep)",
        "3 → T (stopped)",
        "4 → t (tracing stop)",
        "5 → X (dead)",
        "6 → Z (zombie)",
        "7 → P (parked)",
        "8 → I (idle)",
    ], size=11, color=INK, anchor="start", lh=1.55))

    p.append(rect(790, 372, 350, 92, fill=FILL, stroke=LINE, sw=1.6, rx=10))
    p.append(mtext(965, 398, [
        "ту саму літеру віддають:",
        "поле 3 у /proc/PID/stat · «State:» у status",
        "перший символ STAT у ps",
    ], size=11, color=INK, lh=1.5))

    # зв'язки
    p.append(arrow(382, 160, 426, 133))
    p.append(line(382, 350, 426, 205, color=MUTED, sw=1.6, dash="6 5"))
    p.append(arrow(585, 188, 585, 212))
    p.append(arrow(585, 332, 585, 368))
    p.append(arrow(744, 404, 788, 318))
    p.append(arrow(965, 330, 965, 370))

    render(os.path.join(OUT, "state-letter-path.svg"), W, H, *p,
           title="Як біти поля __state перетворюються на одну літеру")


fig_sleep_cycle()
fig_state_graph()
fig_signal_vs_state()
fig_lab_run()
fig_slow_disk_stack()
fig_state_letter_path()
print("ok")

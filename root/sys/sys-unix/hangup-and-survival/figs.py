# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE = "#eaf0fd"
GREEN = "#eaf6ef"
RED = "#fdecea"
WARM = "#fff6e5"
GREY = "#eceff1"


def tb(cx, cy, lines, **kw):
    """textbox + межі рамки (x0, x1, y0, y1)."""
    frag, w, h = textbox(cx, cy, lines, **kw)
    return frag, cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2


# ── 1. Каскад розриву сесії в ядрі Linux ─────────────────────────────────────
def fig_terminal_hangup_chain():
    W, H = 1440, 840
    p = []

    p.append(text(W / 2, 45, "Каскад подій при закритті термінала або розриві SSH", size=18, bold=True))

    # Ліва колонка — подія на рівні користувача / емулятора
    LX = 260
    f, _, _, _, y1_close = tb(LX, 130, "Закриття PTY Master\nclose(ptm_fd) в sshd або терміналі", size=14, fill=RED, pad=12)
    p.append(f)

    f, _, _, y0_kern, y1_kern = tb(LX, 255, "Драйвер PTY у ядрі\npty_close() → tty_vhangup()", size=14, fill=GREY, pad=12)
    p.append(f)
    p.append(arrow(LX, y1_close, LX, y0_kern))

    f, _, _, y0_hup, y1_hup = tb(LX, 385, "Маркування PTY Slave\nПрапорець TTY_HUPPED\nread() → 0 (EOF), write() → EIO", size=14, fill=WARM, pad=12)
    p.append(f)
    p.append(arrow(LX, y1_kern, LX, y0_hup))

    # Центральна колонка — Сигнали лідеру сесії
    CX = 720
    f, cx0_lead, cx1_lead, cy0_lead, cy1_lead = tb(CX, 255, "Лідер сесії (Session Leader)\nЯдро надсилає SIGHUP процесу SID\nkill_pgrp(tty->session, SIGHUP)", size=14, bold=True, fill=RED, pad=14)
    p.append(f)
    p.append(arrow(LX + 140, 255, cx0_lead - 8, 255))
    p.append(text((LX + 140 + cx0_lead) / 2, 235, "kill_pgrp()", size=13, color=MUTED))

    f, _, _, y0_bash, y1_bash = tb(CX, 415, "Оболонка (Bash / Zsh)\nОтримує SIGHUP або EOF\nОбходить Jobs Table", size=14, fill=BLUE, pad=12)
    p.append(f)
    p.append(arrow(CX, cy1_lead, CX, y0_bash))

    f, cx0_bcast, cx1_bcast, y0_bcast, y1_bcast = tb(CX, 575, "Розсилка SIGHUP по завданнях\nkillpg(job->pgrp, SIGHUP)\nдля кожної активної групи процесу", size=14, fill=WARM, pad=14)
    p.append(f)
    p.append(arrow(CX, y1_bash, CX, y0_bcast))

    # Права колонка — Доля процесів і осиротілі групи
    RX = 1180
    f, rx0_fg, _, _, _ = tb(RX, 490, "Група переднього плану (FG)\nОтримує SIGHUP від оболонки\nЗа замовчуванням — завершення", size=14, fill=RED, pad=12)
    p.append(f)
    p.append(arrow(cx1_bcast + 8, 560, rx0_fg - 8, 500))

    f, rx0_bg, _, _, _ = tb(RX, 650, "Фонові групи процесів (BG)\nОтримують SIGHUP від оболонки\nЗавершуються без захисту", size=14, fill=RED, pad=12)
    p.append(f)
    p.append(arrow(cx1_bcast + 8, 585, rx0_bg - 8, 640))

    # Нижня частина — Осиротілі зупинені групи (Orphaned Stopped Process Groups)
    p.append(line(90, 715, W - 90, 715, color=MUTED, sw=1.2, dash="6,6"))
    f, _, _, _, _ = tb(W / 2, 775, "Захист ядра від вічного зависання зупинених процесів:\nякщо група стає осиротілою (orphaned) і має процеси в TASK_STOPPED → ядро надсилає SIGHUP + SIGCONT", size=14, fill=GREEN, pad=12)
    p.append(f)

    render(os.path.join(IMG, "terminal-hangup-chain.svg"), W, H, *p,
           title="Каскад розриву сесії в ядрі Linux")


# ── 2. Порівняння трьох механізмів живучості ────────────────────────────────
def fig_survival_mechanisms_comparison():
    W, H = 1480, 760
    p = []

    p.append(text(W / 2, 45, "Порівняння рівнів ізоляції: звичайний процес, nohup, disown та setsid", size=18, bold=True))

    COLS = [
        (220, "1. Без захисту\n(за замовчуванням)", RED,
         ["Сесія: стара (SID = Shell)",
          "TTY: прив'язаний slave PTY",
          "Диспозиція SIGHUP: SIG_DFL",
          "Таблиця Jobs: присутній",
          "Результат: гине при SIGHUP"]),
        (580, "2. nohup\n(утиліта обгортки)", BLUE,
         ["Сесія: стара (SID = Shell)",
          "TTY: від'єднано дескриптори",
          "Диспозиція SIGHUP: SIG_IGN",
          "Таблиця Jobs: присутній",
          "Результат: ігнорує SIGHUP"]),
        (940, "3. disown -h\n(вбудована дія shell)", WARM,
         ["Сесія: стара (SID = Shell)",
          "TTY: залишається старим",
          "Диспозиція SIGHUP: не змінюється",
          "Таблиця Jobs: прапорець NOSIGHUP",
          "Результат: Shell не шле SIGHUP"]),
        (1300, "4. setsid / демон\n(повна ізоляція)", GREEN,
         ["Сесія: нова (SID = PID)",
          "TTY: немає (controlling TTY = NULL)",
          "Диспозиція SIGHUP: ізольований",
          "Таблиця Jobs: відсутній у Shell",
          "Результат: повна автономність"]),
    ]

    ROWS = [
        (170, "Належність сесії"),
        (270, "Керівний термінал (TTY)"),
        (370, "Обробка сигналу"),
        (470, "Стан у Shell"),
        (570, "Живучість при виході")
    ]

    for y, label in ROWS:
        p.append(text(60, y + 6, label, size=13, bold=True, color=MUTED, anchor="start"))

    for cx, head, col, cells in COLS:
        p.append(textbox(cx, 105, head, size=15, bold=True, fill=col, pad=12)[0])
        for (y, _), body in zip(ROWS, cells):
            p.append(textbox(cx, y, body, size=13, fill=FILL, pad=10, min_w=240)[0])

    p.append(text(W / 2, 690, "Кожен наступний рівень переносить відповідальність глибше: від обробника сигналів до структури сесії ядра",
                  size=14, color=MUTED, italic=True))

    render(os.path.join(IMG, "survival-mechanisms-comparison.svg"), W, H, *p,
           title="Порівняння рівнів ізоляції процесів")


# ── 3. Пастка дескрипторів мертвого TTY ──────────────────────────────────────
def fig_dead_tty_io_trap():
    W, H = 1440, 720
    p = []

    p.append(text(W / 2, 45, "Пастка дескрипторів: чому живий процес гине на мертвому TTY", size=18, bold=True))

    # Ліва панель — Що відбувається без перенаправлення
    p.append(rect(80, 80, 610, 560, fill="#fffaf9", stroke=POS, sw=1.5, rx=10))
    p.append(text(385, 120, "Без перенаправлення дескрипторів (ПОМИЛКА)", size=16, bold=True, color=POS))

    f, _, _, _, y1_a = tb(385, 195, "Процес ігнорує SIGHUP (живий)\nАле fd 0, 1, 2 ведуть у /dev/pts/X", size=14, fill=BLUE, pad=12)
    p.append(f)

    f, _, _, y0_b, y1_b = tb(385, 320, "Термінал закрито: PTY Slave у стані HUPPED\nКанал передачі зруйновано", size=14, fill=GREY, pad=12)
    p.append(f)
    p.append(arrow(385, y1_a, 385, y0_b))

    f, _, _, y0_c, _ = tb(385, 460, "Операції введення-виведення:\n• write(1, ...) → помилка EIO або падіння\n• read(0, ...) → 0 (EOF) або помилка EIO\nПроцес аварійно завершується", size=14, fill=RED, pad=14)
    p.append(f)
    p.append(arrow(385, y1_b, 385, y0_c))

    # Права панель — Що робить nohup / правильна демонізація
    p.append(rect(750, 80, 610, 560, fill="#f9fcf9", stroke=FIELD, sw=1.5, rx=10))
    p.append(text(1055, 120, "З ізоляцією дескрипторів (nohup / setsid)", size=16, bold=True, color=FIELD))

    f, _, _, _, y1_r1 = tb(1055, 195, "Перенаправлення дескрипторів:\nstdin: /dev/null · stdout: nohup.out / log", size=14, fill=BLUE, pad=12)
    p.append(f)

    f, _, _, y0_r2, y1_r2 = tb(1055, 320, "Відсутність зв'язку з slave PTY\nДескриптори не залежать від емулятора", size=14, fill=GREY, pad=12)
    p.append(f)
    p.append(arrow(1055, y1_r1, 1055, y0_r2))

    f, _, _, y0_r3, _ = tb(1055, 460, "Стабільне виконання:\n• read(0, ...) повертає EOF штатно\n• write(1, ...) пише у дисковий файл логу\nПроцес продовжує роботу без термінала", size=14, fill=GREEN, pad=14)
    p.append(f)
    p.append(arrow(1055, y1_r2, 1055, y0_r3))

    p.append(text(W / 2, 675, "Живучість вимагає захисту в двох точках: сигнальної диспозиції (SIGHUP) та ізоляції каналів вводу-виводу (stdio)",
                  size=14, color=MUTED, italic=True))

    render(os.path.join(IMG, "dead-tty-io-trap.svg"), W, H, *p,
           title="Пастка дескрипторів мертвого термінала")


fig_terminal_hangup_chain()
fig_survival_mechanisms_comparison()
fig_dead_tty_io_trap()
print("Figures generated successfully.")

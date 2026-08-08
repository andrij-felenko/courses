# -*- coding: utf-8 -*-
"""Фігури до теми «sysctl: параметри ядра, які крутять на ходу»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)

GREEN_FILL = "#eaf7ef"
RED_FILL = "#fdecea"
BLUE_FILL = "#eaf0fd"
GREY_FILL = "#f4f6f8"


# ── 1. Що лежить за «файлом» у /proc/sys ───────────────────────────────────
def fig_entry_anatomy():
    W, H = 1200, 640
    f = []

    # шлях
    f.append(fitbox(50, 150, 260, 80, "/proc/sys/net/ipv4/\nip_forward",
                    size=14, fill=BG, stroke=INK))
    f.append(text(180, 250, "шлях — це і є ім'я параметра", size=12, color=MUTED))

    # опис параметра
    f.append(rect(360, 60, 380, 300, fill=GREY_FILL, stroke=MUTED))
    f.append(text(550, 44, "опис, який зареєструвала підсистема", size=12, color=MUTED))
    rows = [
        (90, "procname = \"ip_forward\""),
        (142, "data → адреса справжньої змінної"),
        (194, "maxlen = 4 · mode = 0644"),
        (246, "proc_handler = proc_dointvec_minmax"),
        (298, "extra1 = 0 · extra2 = 1"),
    ]
    for y, s in rows:
        f.append(fitbox(380, y, 340, 42, s, size=13, fill=BG, stroke=MUTED))

    # справжня змінна
    f.append(fitbox(800, 150, 300, 80, "справжня змінна ядра\nint sysctl_ip_forward",
                    size=14, fill=GREEN_FILL, stroke=FIELD))
    f.append(text(950, 250, "жодного байта на диску не існує", size=12, color=MUTED))

    f.append(arrow(314, 190, 356, 190))
    f.append(arrow(744, 190, 796, 190))

    # смуги: що робить обробник
    f.append(text(600, 400, "усю роботу робить обробник", size=13, color=MUTED, bold=True))

    f.append(fitbox(40, 425, 95, 58, "читання", size=13, fill=BLUE_FILL, stroke=NEG))
    lane1 = [(175, "read() на відкритому файлі"),
             (455, "обробник бере поточне\nзначення змінної"),
             (735, "форматує його текстом\nу ваш буфер")]
    for x, s in lane1:
        f.append(fitbox(x, 425, 250, 58, s, size=12, fill=BG, stroke=NEG))
    f.append(arrow(429, 454, 451, 454))
    f.append(arrow(709, 454, 731, 454))

    f.append(fitbox(40, 525, 95, 58, "запис", size=13, fill=RED_FILL, stroke=POS))
    lane2 = [(175, "write(\"1\\n\")"),
             (370, "розбір тексту\nв число"),
             (565, "звірка з межами\nextra1…extra2"),
             (760, "присвоєння\nзмінній"),
             (955, "побічна дія\nв обробнику")]
    for x, s in lane2:
        f.append(fitbox(x, 525, 175, 58, s, size=12, fill=BG, stroke=POS))
    for x in (350, 545, 740, 935):
        f.append(arrow(x, 554, x + 20, 554))

    render(os.path.join(IMG, 'entry-anatomy.svg'), W, H, *f,
           title="Запис у /proc/sys — не файл, а опис змінної разом із обробником")


# ── 2. Три моменти, коли рішення ще можна змінити ──────────────────────────
def fig_three_moments():
    W, H = 1180, 520
    f = []

    f.append(arrow(60, 118, 1130, 118))
    f.append(text(220, 100, "збірка ядра", size=14, color=INK, bold=True))
    f.append(text(570, 100, "завантаження", size=14, color=INK, bold=True))
    f.append(text(950, 100, "робота машини", size=14, color=INK, bold=True))

    f.append(fitbox(60, 150, 320, 110,
                    ".config: y / n / m —\nчи цей код узагалі\nпотрапить в образ",
                    size=13, fill=BG, stroke=MUTED))
    f.append(fitbox(420, 150, 300, 110,
                    "командний рядок ядра,\nпараметри модулів",
                    size=13, fill=BG, stroke=MUTED))
    f.append(fitbox(760, 150, 380, 110,
                    "/proc/sys — записом\nу звичайний файл",
                    size=13, fill=GREEN_FILL, stroke=FIELD))

    f.append(fitbox(60, 285, 320, 56, "змінити = перезібрати ядро",
                    size=13, fill=RED_FILL, stroke=POS))
    f.append(fitbox(420, 285, 300, 56, "змінити = перезавантажити",
                    size=13, fill=RED_FILL, stroke=POS))
    f.append(fitbox(760, 285, 380, 56, "змінити = один write(), негайно",
                    size=13, fill=GREEN_FILL, stroke=FIELD))

    f.append(arrow(950, 345, 950, 388))
    f.append(fitbox(200, 390, 800, 90,
                    "перезавантаження стирає все, що записали в /proc/sys:\n"
                    "при старті systemd-sysctl просто програє ті самі записи заново\n"
                    "з /etc/sysctl.d/*.conf — це не збережене значення, а повтор дії",
                    size=13, fill=GREY_FILL, stroke=MUTED))

    render(os.path.join(IMG, 'three-moments.svg'), W, H, *f,
           title="Що ще можна змінити на кожному з трьох моментів життя ядра")


# ── 3. /proc/sys — не одне дерево, а погляд ────────────────────────────────
def fig_namespaced_view():
    W, H = 1160, 590
    f = []

    f.append(rect(50, 70, 460, 190, fill=GREY_FILL, stroke=MUTED))
    f.append(text(280, 58, "контейнер A", size=13, color=INK, bold=True))
    f.append(fitbox(70, 105, 200, 120, "net/ipv4/\nip_forward",
                    size=13, fill=BG, stroke=FIELD))
    f.append(fitbox(290, 105, 200, 120, "kernel/\npid_max",
                    size=13, fill=BG, stroke=POS))

    f.append(rect(650, 70, 460, 190, fill=GREY_FILL, stroke=MUTED))
    f.append(text(880, 58, "контейнер B", size=13, color=INK, bold=True))
    f.append(fitbox(670, 105, 200, 120, "net/ipv4/\nip_forward",
                    size=13, fill=BG, stroke=FIELD))
    f.append(fitbox(890, 105, 200, 120, "kernel/\npid_max",
                    size=13, fill=BG, stroke=POS))

    f.append(text(120, 392, "пам'ять ядра", size=12, color=MUTED, anchor="start"))

    f.append(fitbox(80, 420, 300, 80, "змінні мережевого\nпростору імен A",
                    size=13, fill=GREEN_FILL, stroke=FIELD))
    f.append(fitbox(430, 420, 300, 80, "одна змінна на всю\nмашину: pid_max",
                    size=13, fill=RED_FILL, stroke=POS))
    f.append(fitbox(780, 420, 300, 80, "змінні мережевого\nпростору імен B",
                    size=13, fill=GREEN_FILL, stroke=FIELD))

    f.append(arrow(170, 228, 200, 414))
    f.append(arrow(770, 228, 930, 414))
    f.append(arrow(390, 228, 540, 414))
    f.append(arrow(990, 228, 620, 414))

    f.append(mtext(300, 300, "той самий шлях —\nрізні змінні", size=12, color=MUTED))
    f.append(text(580, 540,
                  "спільну змінну запис із контейнера змінив би всій машині — тому такі шляхи монтують лише для читання",
                  size=12, color=MUTED))

    render(os.path.join(IMG, 'namespaced-view.svg'), W, H, *f,
           title="Однаковий шлях у /proc/sys веде до різних змінних — залежно від простору імен")


# ── 4. Де народжується кожна помилка запису ────────────────────────────────
def fig_write_path_errors():
    W, H = 1320, 560
    f = []

    cols = [40, 300, 560, 820, 1080]
    CW = 200

    stages = [
        ("open()\nпошук імені", "перевірка бітів прав\nна знайденому записі"),
        ("write()\nвхід у ядро", "запис ще існує?\nправа ще ті самі?"),
        ("гачок eBPF\ncgroup/sysctl", "програма бачить ім'я\nй нове значення"),
        ("обробник\nproc_do*", "розбір тексту\nй звірка з межами"),
        ("змінна ядра", "нове значення\nна місці"),
    ]
    errs = [
        "ENOENT — шляху немає\nEACCES — біти не дають",
        "ENOENT — запис зняли\nEPERM — права змінились\nENOMEM — завеликий буфер",
        "EPERM — програма\nповернула 0",
        "EINVAL — не число\nEINVAL — поза межами\nERANGE — у *uint*_minmax",
        "помилок уже немає",
    ]

    for i, (head, sub) in enumerate(stages):
        x = cols[i]
        fill = GREEN_FILL if i == 4 else BLUE_FILL
        f.append(fitbox(x, 70, CW, 76, head, size=14, bold=True,
                        fill=fill, stroke=INK))
        f.append(fitbox(x, 160, CW, 68, sub, size=12,
                        fill=GREY_FILL, stroke=MUTED))
        f.append(fitbox(x, 300, CW, 96, errs[i], size=12,
                        fill=RED_FILL if i < 4 else BG,
                        stroke=POS if i < 4 else MUTED,
                        color=INK if i < 4 else MUTED))
        if i < 4:
            f.append(arrow(x + CW + 8, 108, cols[i + 1] - 8, 108))
        f.append(line(x + CW / 2, 228, x + CW / 2, 296, color=MUTED, sw=1.2,
                      dash="5 4"))

    f.append(text(660, 44, "шлях одного write() і помилки, які він може повернути",
                 size=13, color=MUTED))
    f.append(text(660, 430,
                  "нуль повернутих байтів або лічильник менший за поданий — теж відповідь: значення взяли не все",
                  size=12, color=MUTED))
    f.append(text(660, 460,
                  "запис не з нульової позиції у числовий параметр помилки не дає — його просто відкидають",
                  size=12, color=MUTED))

    render(os.path.join(IMG, 'write-path-errors.svg'), W, H, *f,
           title="Де на шляху запису в /proc/sys народжується кожна помилка")


# ── 5. Крутилка, що міняє двоє зв'язаних чисел ─────────────────────────────
def fig_snapshot_swap():
    W, H = 1200, 600
    f = []

    f.append(rect(50, 80, 500, 420, fill=GREY_FILL, stroke=MUTED))
    f.append(text(300, 66, "два незалежні глобали", size=14, color=INK, bold=True))
    f.append(fitbox(80, 110, 200, 62, "slots = 64", size=14, fill=BG, stroke=POS))
    f.append(fitbox(320, 110, 200, 62, "hit → масив на 16", size=13, fill=BG, stroke=MUTED))
    f.append(text(180, 192, "обробник уже записав", size=11, color=MUTED))
    f.append(text(420, 192, "масив ще старий", size=11, color=MUTED))
    f.append(arrow(160, 205, 230, 226))
    f.append(arrow(430, 205, 370, 226))
    f.append(fitbox(140, 230, 320, 62, "читач бере нову довжину\nі старий масив",
                    size=12, fill=BG, stroke=INK))
    f.append(arrow(300, 296, 300, 340))
    f.append(fitbox(120, 344, 360, 76, "звертання за межі масиву —\nпсування чужої пам'яті",
                    size=13, fill=RED_FILL, stroke=POS))
    f.append(text(300, 456, "жодна крутилка не робить двох записів разом",
                  size=11, color=MUTED))

    f.append(rect(650, 80, 500, 420, fill=GREY_FILL, stroke=MUTED))
    f.append(text(900, 66, "один незмінний знімок", size=14, color=INK, bold=True))
    f.append(fitbox(690, 110, 420, 62, "cur_bins → { n = 64, hit[64] }",
                    size=14, fill=BG, stroke=FIELD))
    f.append(text(900, 192, "довжина й масив — в одній структурі", size=11, color=MUTED))
    f.append(arrow(900, 205, 900, 226))
    f.append(fitbox(740, 230, 320, 62, "читач бере один вказівник\nпід rcu_read_lock()",
                    size=12, fill=BG, stroke=NEG))
    f.append(arrow(900, 296, 900, 340))
    f.append(fitbox(720, 344, 360, 76, "n і масив не можуть\nрозійтися ніколи",
                    size=13, fill=GREEN_FILL, stroke=FIELD))
    f.append(text(900, 456, "старий знімок звільнить RCU, коли вийде останній читач",
                  size=11, color=MUTED))

    f.append(text(600, 545,
                  "запис одного числа неподільний — біда в тому, що узгодженими мають бути двоє",
                  size=12, color=MUTED))

    render(os.path.join(IMG, 'snapshot-swap.svg'), W, H, *f,
           title="Чому число, яке описує розмір, доводиться міняти разом із тим, що воно описує")


if __name__ == '__main__':
    fig_entry_anatomy()
    fig_three_moments()
    fig_namespaced_view()
    fig_write_path_errors()
    fig_snapshot_swap()
    print("ok")

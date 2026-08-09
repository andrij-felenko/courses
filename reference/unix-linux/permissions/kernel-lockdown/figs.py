# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL = "#fdecea"
WARM_FILL = "#fff6e5"
WARM = "#b8860b"
GREY_FILL = "#eeeeee"


# ── 1. Розрив у ланцюгу довіри ─────────────────────────────────────────────
def fig_trust_gap():
    W, H = 1300, 650
    p = []

    p.append(text(650, 34, "що накриває перевірка підпису", size=16, bold=True))

    p.append(fitbox(70, 56, 230, 70, "прошивка UEFI", size=15,
                    fill=GREEN_FILL, stroke=FIELD))
    p.append(arrow(302, 91, 366, 91, color=FIELD, sw=2))
    p.append(fitbox(370, 56, 230, 70, "завантажувач\nshim і GRUB", size=15,
                    fill=GREEN_FILL, stroke=FIELD))
    p.append(arrow(602, 91, 666, 91, color=FIELD, sw=2))
    p.append(fitbox(670, 56, 230, 70, "образ ядра\nvmlinuz", size=15,
                    fill=GREEN_FILL, stroke=FIELD))
    p.append(arrow(902, 91, 966, 91, color=FIELD, sw=2))
    p.append(fitbox(970, 56, 260, 70, "ядро запустилося", size=15,
                    fill=GREEN_FILL, stroke=FIELD))

    p.append(text(650, 158, "кожна ланка перевіряє підпис наступної", size=14, color=MUTED))

    p.append(text(650, 212, "чого ця перевірка вже не бачить", size=16, bold=True))

    p.append(fitbox(70, 240, 250, 300, "root\nу системі,\nщо вже працює",
                    size=16, bold=True, fill=RED_FILL, stroke=POS))

    doors = [
        (240, "запис у /dev/mem за фізичною адресою"),
        (300, "kexec непідписаного ядра"),
        (360, "запис у MSR і порти вводу-виводу"),
        (420, "підміна таблиць ACPI з initramfs"),
        (480, "kprobes у код працюючого ядра"),
    ]
    for y, s in doors:
        p.append(fitbox(420, y, 330, 52, s, size=13, fill=WARM_FILL, stroke=WARM))
        p.append(arrow(322, y + 26, 416, y + 26, color=POS, sw=2))
        p.append(arrow(752, y + 26, 846, y + 26, color=POS, sw=2))

    p.append(fitbox(850, 240, 380, 300,
                    "адресний простір\nядра, що вже працює",
                    size=16, bold=True, fill=BLUE_FILL, stroke=NEG))

    render(os.path.join(IMG, 'trust-gap.svg'), W, H, *p,
           title="Підпис накриває шлях до старту, але не те, що роблять з ядром після старту")


# ── 2. Порядок причин як політика ──────────────────────────────────────────
def fig_reason_ruler():
    W, H = 1240, 600
    p = []

    p.append(text(620, 36, "перелік причин: порядок значень і є політикою", size=16, bold=True))

    rows = [
        (62, "LOCKDOWN_NONE = 0", GREY_FILL, LINE, False),
        (110, "LOCKDOWN_MODULE_SIGNATURE", BLUE_FILL, NEG, False),
        (154, "LOCKDOWN_DEV_MEM", BLUE_FILL, NEG, False),
        (198, "LOCKDOWN_KEXEC", BLUE_FILL, NEG, False),
        (242, "… ще півтора десятка причин запису", BLUE_FILL, NEG, False),
        (290, "LOCKDOWN_INTEGRITY_MAX", WARM_FILL, WARM, True),
        (338, "LOCKDOWN_KCORE", RED_FILL, POS, False),
        (382, "LOCKDOWN_KPROBES", RED_FILL, POS, False),
        (426, "… решта причин читання", RED_FILL, POS, False),
        (474, "LOCKDOWN_CONFIDENTIALITY_MAX", WARM_FILL, WARM, True),
    ]
    for y, s, fill, stroke, bold in rows:
        p.append(fitbox(330, y, 500, 40, s, size=14, bold=bold, fill=fill, stroke=stroke))

    p.append(fitbox(60, 150, 240, 130,
                    "усе, що веде\nдо запису\nв пам'ять ядра",
                    size=14, fill=BLUE_FILL, stroke=NEG))
    p.append(fitbox(60, 340, 240, 130,
                    "усе, що веде\nдо читання\nпам'яті ядра",
                    size=14, fill=RED_FILL, stroke=POS))

    p.append(arrow(886, 310, 838, 310, color=WARM, sw=2))
    p.append(fitbox(890, 274, 300, 72,
                    "тут зупиняється\nрівень integrity", size=14,
                    fill=WARM_FILL, stroke=WARM))
    p.append(arrow(886, 494, 838, 494, color=WARM, sw=2))
    p.append(fitbox(890, 458, 300, 72,
                    "тут зупиняється\nрівень confidentiality", size=14,
                    fill=WARM_FILL, stroke=WARM))

    p.append(fitbox(330, 526, 500, 50,
                    "рівень ≥ причина  →  відмова −EPERM",
                    size=15, bold=True, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, 'reason-ruler.svg'), W, H, *p,
           title="Причини впорядковані так, що рішення політики зводиться до порівняння двох чисел")


# ── 3. Куди насправді ведуть відкриті двері ────────────────────────────────
def fig_doors():
    W, H = 1300, 700
    p = []

    p.append(text(650, 36, "різні інтерфейси — два спільні наслідки", size=16, bold=True))

    write_doors = [
        (70, "прямий запис у пам'ять\n/dev/mem, /dev/port"),
        (166, "власний код у ядрі\nнепідписаний модуль, kexec"),
        (262, "залізо як посередник\nPCI BAR, порти, MSR, параметри модуля"),
        (358, "таблиці прошивки\nACPI custom_method, підміна таблиць"),
        (454, "налагодження з правом запису\nkgdb, kprobes, bpf у пам'ять процесу"),
    ]
    for y, s in write_doors:
        p.append(fitbox(60, y, 400, 76, s, size=13, fill=WARM_FILL, stroke=WARM))
        p.append(arrow(464, y + 38, 776, 274, color=NEG, sw=1.6))

    p.append(fitbox(780, 214, 460, 120,
                    "довільний запис\nу пам'ять ядра", size=17, bold=True,
                    fill=BLUE_FILL, stroke=NEG))
    p.append(fitbox(780, 348, 460, 44, "рівень integrity закриває це", size=14,
                    fill=FILL, stroke=NEG))

    p.append(fitbox(60, 570, 400, 76,
                    "читання пам'яті ядра\n/proc/kcore, perf, tracefs, bpf",
                    size=13, fill=WARM_FILL, stroke=WARM))
    p.append(arrow(464, 608, 776, 530, color=POS, sw=1.6))

    p.append(fitbox(780, 470, 460, 120,
                    "видача вмісту\nпам'яті ядра назовні", size=17, bold=True,
                    fill=RED_FILL, stroke=POS))
    p.append(fitbox(780, 604, 460, 44, "додає рівень confidentiality", size=14,
                    fill=FILL, stroke=POS))

    render(os.path.join(IMG, 'doors.svg'), W, H, *p,
           title="Критерій відбору — не назва інтерфейсу, а те, чим він закінчується")


# ── 4. Як прочитати відповідь на стук (для вставки-проби) ─────────────────
def fig_verdict_tree():
    W, H = 1340, 620
    p = []

    p.append(text(670, 34, "стук у двері повернув — і що з цього випливає", size=16, bold=True))

    p.append(fitbox(50, 250, 250, 110,
                    "виклик, у якому\nстоїть перевірка", size=15, bold=True,
                    fill=GREY_FILL, stroke=LINE))

    rows = [
        (70,  "0 — дескриптор відкрився,\nвиклик пройшов",
              "двері відчинені: на цьому рівні\nця причина не закрита",
              GREEN_FILL, FIELD),
        (192, "−EPERM, і в журналі ядра\nз'явився рядок «Lockdown: …»",
              "зачинило блокування;\nу рядку — назва причини",
              RED_FILL, POS),
        (314, "−EPERM, журнал мовчить",
              "інша перевірка: немає CAP_SYS_RAWIO,\nSELinux, STRICT_DEVMEM, allow_writes=off",
              WARM_FILL, WARM),
        (436, "−ENOENT, −ENXIO, −ENODEV",
              "дверей немає: ядро зібрано\nбез цього інтерфейсу",
              BLUE_FILL, NEG),
    ]
    for y, cond, verdict, fill, stroke in rows:
        p.append(fitbox(360, y, 420, 100, cond, size=13, fill=FILL, stroke=stroke))
        p.append(arrow(304, 305, 356, y + 50, color=stroke, sw=1.6))
        p.append(arrow(784, y + 50, 836, y + 50, color=stroke, sw=1.6))
        p.append(fitbox(840, y, 450, 100, verdict, size=13, fill=fill, stroke=stroke))

    p.append(fitbox(360, 552, 930, 46,
                    "рядок у журналі рвано-обмежений — стукати треба поволі й по одних дверях за раз",
                    size=14, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, 'verdict-tree.svg'), W, H, *p,
           title="Сам код повернення нічого не доводить: вирок складають із трьох свідчень")


fig_trust_gap()
fig_reason_ruler()
fig_doors()
fig_verdict_tree()
print("ok")

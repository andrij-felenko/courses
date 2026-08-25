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
GREY_FILL = "#eceff1"


# ── 1. Прилипле число ───────────────────────────────────────────────────────
def fig_sticky_uid():
    W, H = 1340, 560
    p = []

    cols = [(40, "1 · служба працює"),
            (490, "2 · пакунок прибрано"),
            (940, "3 · число видано знову")]
    for x, cap in cols:
        p.append(rect(x, 54, 360, 460, fill=BG, stroke=MUTED, sw=1.2, rx=10))
        p.append(text(x + 180, 88, cap, size=16, bold=True))

    # 1
    p.append(fitbox(70, 112, 300, 74,
                    "база облікових записів\nmetrics → 999",
                    size=14, fill=GREEN_FILL, stroke=FIELD))
    p.append(arrow(220, 186, 220, 236))
    p.append(fitbox(70, 238, 300, 74,
                    "inode файлу\nuid = 999",
                    size=14, fill=BLUE_FILL, stroke=NEG))
    p.append(fitbox(70, 356, 300, 74,
                    "ls -l друкує «metrics»",
                    size=14, fill=FILL, stroke=LINE))

    # 2
    p.append(fitbox(520, 112, 300, 74,
                    "рядок видалено\n— порожньо —",
                    size=14, fill=RED_FILL, stroke=POS))
    p.append(fitbox(520, 238, 300, 74,
                    "inode файлу\nuid = 999 (не змінився)",
                    size=14, fill=BLUE_FILL, stroke=NEG))
    p.append(fitbox(520, 356, 300, 74,
                    "ls -l друкує «999»",
                    size=14, fill=FILL, stroke=LINE))

    # 3
    p.append(fitbox(970, 112, 300, 74,
                    "база облікових записів\nbackup → 999",
                    size=14, fill=WARM_FILL, stroke=MUTED))
    p.append(arrow(1120, 186, 1120, 236))
    p.append(fitbox(970, 238, 300, 74,
                    "inode файлу\nuid = 999 (той самий)",
                    size=14, fill=BLUE_FILL, stroke=NEG))
    p.append(fitbox(970, 356, 300, 74,
                    "нова служба читає й пише\nстарі файли на повних правах",
                    size=14, fill=RED_FILL, stroke=POS))

    p.append(text(670, 534,
                  "ядро звіряє числа, а не імена — тому крок 2 нічого не змінює у файлах",
                  size=15, color=MUTED))

    render(os.path.join(IMG, 'sticky-uid.svg'), W, H, *p,
           title="Прилипле число: чому обліковий запис бояться видаляти")


# ── 2. Вибір числа й замок ──────────────────────────────────────────────────
def fig_uid_allocation():
    W, H = 1300, 660
    p = []

    p.append(text(650, 46, "вибір кандидата — три заходи по черзі", size=16, bold=True))

    ph = [(60, "1 · підказка з диску",
           "власник каталогу стану\n/var/lib/private/metrics"),
          (490, "2 · хеш імені",
           "siphash24(\"metrics\")\nстиснутий у 61184…65519"),
          (920, "3 · навмання",
           "випадкове число з проміжку\nдо ста спроб")]
    for x, cap, body in ph:
        p.append(text(x + 160, 92, cap, size=15, bold=True))
        p.append(fitbox(x, 108, 320, 84, body, size=14, fill=WARM_FILL, stroke=MUTED))

    p.append(arrow(380, 150, 490, 150))
    p.append(arrow(810, 150, 920, 150))
    p.append(text(435, 138, "зайнято", size=12, color=MUTED))
    p.append(text(865, 138, "зайнято", size=12, color=MUTED))

    p.append(arrow(650, 200, 650, 246))

    p.append(fitbox(330, 250, 640, 92,
                    "open(\"/run/systemd/dynamic-uid/61234\", O_CREAT|O_RDWR, 0600)\n"
                    "flock(fd, LOCK_EX|LOCK_NB)",
                    size=14, fill=BLUE_FILL, stroke=NEG))

    p.append(arrow(650, 342, 650, 392))

    p.append(fitbox(140, 396, 480, 100,
                    "у файлі — один рядок: metrics\n"
                    "число → ім'я читається просто з файлу",
                    size=14, fill=GREEN_FILL, stroke=FIELD))
    p.append(fitbox(680, 396, 480, 100,
                    "замок тримається за дескриптором\n"
                    "останній дескриптор закрито — число вільне",
                    size=14, fill=GREEN_FILL, stroke=FIELD))

    p.append(fitbox(140, 528, 1020, 78,
                    "/run — це tmpfs: після перезавантаження жодного замка не лишається, "
                    "тож зайнятість числа не переживає вимкнення живлення",
                    size=14, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, 'uid-allocation.svg'), W, H, *p,
           title="Вибір тимчасового числа й замок, що знімається сам")


# ── 3. Стіна /var/lib/private ───────────────────────────────────────────────
def fig_var_lib_private():
    W, H = 1320, 600
    p = []

    # ліворуч — хост
    p.append(rect(40, 56, 600, 500, fill=BG, stroke=MUTED, sw=1.2, rx=10))
    p.append(text(340, 92, "погляд хоста", size=16, bold=True))

    p.append(fitbox(80, 118, 520, 66,
                    "/var/lib/metrics  →  private/metrics",
                    size=14, fill=FILL, stroke=LINE))
    p.append(arrow(340, 184, 340, 226))

    p.append(fitbox(80, 230, 520, 78,
                    "/var/lib/private\nroot:root, режим 0700 — стіна",
                    size=14, fill=RED_FILL, stroke=POS))
    p.append(arrow(340, 308, 340, 350))

    p.append(fitbox(120, 354, 440, 78,
                    "/var/lib/private/metrics\nвласник — тимчасове число 61234",
                    size=14, fill=BLUE_FILL, stroke=NEG))

    p.append(text(340, 480, "стороння служба з тим самим числом", size=13, color=MUTED))
    p.append(text(340, 508, "спиняється на стіні, а не на каталозі", size=13, color=MUTED))

    # праворуч — служба
    p.append(rect(700, 56, 580, 500, fill=BG, stroke=MUTED, sw=1.2, rx=10))
    p.append(text(990, 92, "погляд самої служби", size=16, bold=True))

    p.append(fitbox(740, 118, 500, 66,
                    "власний простір монтувань",
                    size=14, fill=GREY_FILL, stroke=MUTED))
    p.append(arrow(990, 184, 990, 226))

    p.append(fitbox(740, 230, 500, 78,
                    "bind-монтування справжнього каталогу\nна /var/lib/metrics",
                    size=14, fill=GREEN_FILL, stroke=FIELD))
    p.append(arrow(990, 308, 990, 350))

    p.append(fitbox(760, 354, 460, 78,
                    "/var/lib/metrics\nзвичайний власний каталог",
                    size=14, fill=GREEN_FILL, stroke=FIELD))

    p.append(text(990, 480, "про існування private служба", size=13, color=MUTED))
    p.append(text(990, 508, "не знає нічого", size=13, color=MUTED))

    render(os.path.join(IMG, 'var-lib-private.svg'), W, H, *p,
           title="Каталог стану під стіною /var/lib/private")


# ── 4. Що саме тримає замок ─────────────────────────────────────────────────
def fig_lock_holder():
    W, H = 1100, 470
    p = []

    # ── ліворуч: окремий open() — окремий опис ──────────────────────────────
    p.append(rect(30, 54, 500, 380, fill=BG, stroke=MUTED, sw=1.2, rx=10))
    p.append(text(280, 88, "Окремий open() — окремий опис", size=15, bold=True))

    p.append(fitbox(60, 112, 190, 54, "процес\nfd 3", size=14,
                    fill=BLUE_FILL, stroke=NEG))
    p.append(fitbox(310, 112, 190, 54, "той самий процес\nfd 4", size=14,
                    fill=RED_FILL, stroke=POS))
    p.append(arrow(155, 166, 155, 208))
    p.append(arrow(405, 166, 405, 208))

    p.append(fitbox(60, 212, 190, 50, "опис №1", size=14,
                    fill=BLUE_FILL, stroke=NEG))
    p.append(fitbox(310, 212, 190, 50, "опис №2", size=14,
                    fill=RED_FILL, stroke=POS))
    p.append(arrow(155, 262, 235, 312))
    p.append(arrow(405, 262, 325, 312))

    p.append(fitbox(130, 316, 300, 50, "файл-замок 64667", size=14,
                    fill=GREY_FILL, stroke=MUTED))

    p.append(text(280, 396, "flock на описі №2 → EWOULDBLOCK:", size=13, color=POS))
    p.append(text(280, 418, "число вже зайняте", size=13, color=POS))

    # ── праворуч: той самий опис ────────────────────────────────────────────
    p.append(rect(570, 54, 500, 380, fill=BG, stroke=MUTED, sw=1.2, rx=10))
    p.append(text(820, 88, "fork, dup, передача сокетом — опис один", size=15, bold=True))

    p.append(fitbox(600, 112, 190, 54, "процес A\nfd 3", size=14,
                    fill=BLUE_FILL, stroke=NEG))
    p.append(fitbox(850, 112, 190, 54, "процес B\nfd 3", size=14,
                    fill=BLUE_FILL, stroke=NEG))
    p.append(arrow(695, 166, 785, 212))
    p.append(arrow(945, 166, 855, 212))

    p.append(fitbox(730, 216, 180, 50, "опис №1", size=14,
                    fill=BLUE_FILL, stroke=NEG))
    p.append(arrow(820, 266, 820, 312))

    p.append(fitbox(670, 316, 300, 50, "файл-замок 64667", size=14,
                    fill=GREEN_FILL, stroke=FIELD))

    p.append(text(820, 396, "замок цілий, поки живий хоч один fd;", size=13, color=FIELD))
    p.append(text(820, 418, "зникає на закритті ОСТАННЬОГО", size=13, color=FIELD))

    render(os.path.join(IMG, 'lock-holder.svg'), W, H, *p,
           title="Замок належить опису відкритого файлу, а не процесові")


# ── 5. Як роздавали ідентичності службам (історія) ──────────────────────────
def fig_identity_timeline():
    W, H = 1300, 470
    p = []

    y_line = 235
    p.append(line(40, y_line, 1260, y_line, color=MUTED, sw=2))

    cols = [
        (40, "above", GREY_FILL, MUTED,
         "звичай\nнизькі номери — системі;\nмежа 1…999 закріплена\nтиповим UID_MIN = 1000"),
        (360, "below", BLUE_FILL, NEG,
         "2014 · systemd 215\nsysusers.d: потрібний запис\nописано декларативно,\nа не скриптом у пакунку"),
        (680, "above", GREEN_FILL, FIELD,
         "2016 · systemd 232\nDynamicUser=: номер\nз проміжку 61184…65519\nна час роботи служби"),
        (1000, "below", WARM_FILL, MUTED,
         "2017 · systemd 235\nStateDirectory= та решта:\nкерований стан для служб,\nяким є що зберігати"),
    ]

    for x, side, fill, stroke, body in cols:
        cx = x + 130
        p.append(circle(cx, y_line, 8, fill=BG, stroke=MUTED, sw=2))
        if side == "above":
            p.append(fitbox(x, 40, 260, 150, body, size=14, fill=fill, stroke=stroke))
            p.append(line(cx, 190, cx, y_line - 8, color=MUTED, sw=1.2))
        else:
            p.append(fitbox(x, 280, 260, 150, body, size=14, fill=fill, stroke=stroke))
            p.append(line(cx, y_line + 8, cx, 280, color=MUTED, sw=1.2))

    render(os.path.join(IMG, 'identity-timeline.svg'), W, H, *p,
           title="Чотири способи дати службі ідентичність")


if __name__ == '__main__':
    fig_identity_timeline()
    fig_sticky_uid()
    fig_uid_allocation()
    fig_var_lib_private()
    fig_lock_holder()
    print("ok")

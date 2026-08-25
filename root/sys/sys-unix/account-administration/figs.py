# -*- coding: utf-8 -*-
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL = "#fdecea"
WARM_FILL = "#fff6e5"
GREY_FILL = "#f4f6f8"


# ── 1. Конвеєр створення облікового запису useradd ──────────────────────────
def fig_account_provisioning():
    W, H = 1000, 480
    frags = []

    # 5 послідовних кроків у колонках або картках
    steps = [
        (30, 70, 165, "1. Конфігурація",
         "/etc/login.defs\n/etc/default/useradd\nUID_MIN / UMASK\nSHELL / SKEL",
         WARM_FILL, MUTED),
        (225, 70, 165, "2. Блокування",
         "Створення замків\n/etc/ptmp\n/etc/sptmp\nO_CREAT | O_EXCL",
         RED_FILL, POS),
        (420, 70, 165, "3. Бази даних",
         "Вибір вільного UID\nЗапис у .ptmp / .sptmp\nДодавання до груп\n/etc/group",
         BLUE_FILL, NEG),
        (615, 70, 165, "4. Домівка і skel",
         "mkdir /home/user\nКопіювання /etc/skel\nchown -R uid:gid\nchmod 0700 / 0750",
         GREEN_FILL, FIELD),
        (810, 70, 165, "5. Атомарний комміт",
         "fsync(ptmp)\nrename(ptmp, passwd)\nrename(sptmp, shadow)\nЗняття блокувань",
         WARM_FILL, MUTED),
    ]

    for x, y, w, title, desc, fcolor, scolor in steps:
        frags.append(rect(x, y, w, 220, fill=fcolor, stroke=scolor, sw=1.5, rx=8))
        frags.append(text(x + w / 2, y + 28, title, size=14, bold=True, color=INK))
        frags.append(line(x + 10, y + 42, x + w - 10, y + 42, color=scolor, sw=1.0))
        frags.append(mtext(x + w / 2, y + 70, desc, size=12, color=INK, lh=1.4))

    # Стрілки між кроками
    frags.append(arrow(195, 180, 225, 180, color=LINE, sw=1.8))
    frags.append(arrow(390, 180, 420, 180, color=LINE, sw=1.8))
    frags.append(arrow(585, 180, 615, 180, color=LINE, sw=1.8))
    frags.append(arrow(780, 180, 810, 180, color=LINE, sw=1.8))

    # Нижній пояснювальний блок
    frags.append(rect(30, 320, 945, 120, fill=BG, stroke=MUTED, sw=1.2, rx=8))
    frags.append(text(500, 348, "Гарантії надійності: ізоляція гонок та консистентність файлової системи", size=14, bold=True, color=INK))
    info_text = (
        "• Конкурентні виклики useradd зупиняються на кроці 2 (блокувальний файл ptmp гарантує ексклюзивність).\n"
        "• Якщо збій стається на кроці 3 або 4 — основні файли /etc/passwd та /etc/shadow лишаються неушкодженими.\n"
        "• Крок 5 виконується системним викликом rename(), що забезпечує миттєву й атомарну підміну файлів бази."
    )
    frags.append(mtext(500, 375, info_text, size=12, color=INK, lh=1.35))

    render(os.path.join(IMG, "account-provisioning-flow.svg"), W, H, *frags,
           title="Послідовність створення облікового запису утилітою useradd")


# ── 2. Часова шкала та поля /etc/shadow ──────────────────────────────────────
def fig_shadow_lifecycle():
    W, H = 1000, 490
    frags = []

    # Верхній блок: структура рядка shadow
    frags.append(rect(30, 55, 940, 75, fill=GREY_FILL, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(500, 78, "Структура рядка /etc/shadow (9 полів, розділених двокрапкою)", size=14, bold=True))
    fmt_str = "user : $6$... : 19800 : 7 : 90 : 14 : 30 : 20200 : [res]"
    frags.append(text(500, 108, fmt_str, size=13, bold=True, color=NEG))

    # Вісь часу
    axis_y = 240
    frags.append(line(50, axis_y, 950, axis_y, color=LINE, sw=2.5))
    frags.append(arrow(930, axis_y, 960, axis_y, color=LINE, sw=2.5))
    frags.append(text(960, axis_y + 24, "Час (дні)", size=12, bold=True, anchor="end"))

    # Позначки на осі часу
    # Точка 1: Останній пароль (lstchg)
    frags.append(circle(100, axis_y, 6, fill=FIELD, stroke=INK, sw=1.5))
    frags.append(text(100, axis_y - 18, "Зміна пароля", size=12, bold=True, color=FIELD))
    frags.append(text(100, axis_y + 20, "sp_lstchg", size=11, color=MUTED))

    # Зона 1: Мін. вік (sp_min)
    frags.append(rect(100, axis_y - 8, 120, 16, fill=RED_FILL, stroke=POS, sw=1, rx=2))
    frags.append(circle(220, axis_y, 6, fill=POS, stroke=INK, sw=1.5))
    frags.append(text(160, axis_y - 22, "Заборона зміни", size=11, color=POS, bold=True))
    frags.append(text(220, axis_y + 20, "+ sp_min", size=11, color=MUTED))

    # Зона 2: Активний пароль (до max - warn)
    frags.append(rect(220, axis_y - 8, 300, 16, fill=GREEN_FILL, stroke=FIELD, sw=1, rx=2))
    frags.append(text(370, axis_y - 22, "Нормальна дія пароля", size=11, color=FIELD, bold=True))

    # Зона 3: Попередження (sp_warn)
    frags.append(rect(520, axis_y - 8, 140, 16, fill=WARM_FILL, stroke=MUTED, sw=1, rx=2))
    frags.append(circle(520, axis_y, 6, fill=MUTED, stroke=INK, sw=1.5))
    frags.append(circle(660, axis_y, 6, fill=POS, stroke=INK, sw=1.5))
    frags.append(text(590, axis_y - 22, "Попередження", size=11, color=INK, bold=True))
    frags.append(text(520, axis_y + 20, "max - warn", size=11, color=MUTED))
    frags.append(text(660, axis_y + 20, "+ sp_max", size=11, color=POS, bold=True))

    # Зона 4: Пільговий період неактивності (sp_inact)
    frags.append(rect(660, axis_y - 8, 120, 16, fill=RED_FILL, stroke=POS, sw=1, rx=2))
    frags.append(circle(780, axis_y, 6, fill=POS, stroke=INK, sw=1.5))
    frags.append(text(720, axis_y - 22, "Пароль прострочено", size=11, color=POS, bold=True))
    frags.append(text(780, axis_y + 20, "+ sp_inact", size=11, color=MUTED))

    # Точка 5: Абсолютне блокування / кінець дії
    frags.append(circle(890, axis_y, 7, fill=POS, stroke=INK, sw=2))
    frags.append(text(890, axis_y - 22, "Блокування запису", size=12, bold=True, color=POS))
    frags.append(text(890, axis_y + 20, "sp_expire", size=11, color=POS))

    # Блок пояснень знизу
    frags.append(rect(30, 310, 940, 150, fill=BG, stroke=MUTED, sw=1.2, rx=8))
    frags.append(text(500, 335, "Керування політикою старіння утилітою chage", size=13, bold=True))
    expl = (
        "• chage -m <дні> (sp_min): мінімальний інтервал між змінами — захищає від швидкої ротації заради повернення старого пароля.\n"
        "• chage -M <дні> (sp_max): максимальний термін чинності пароля; після цього вхід вимагає негайної заміни пароля.\n"
        "• chage -W <дні> (sp_warn): кількість днів перед закінченням sp_max, коли login/PAM попереджає користувача.\n"
        "• chage -I <дні> (sp_inact): пільговий період; після нього обліковий запис вимикається, навіть якщо користувач знає старий пароль.\n"
        "• chage -E <YYYY-MM-DD> (sp_expire): абсолютна дата закінчення дії облікового запису (наприклад, термін контракту)."
    )
    frags.append(mtext(500, 360, expl, size=11, color=INK, lh=1.35))

    render(os.path.join(IMG, "shadow-lifecycle-and-chage.svg"), W, H, *frags,
           title="Життєвий цикл пароля та параметри терміну дії в /etc/shadow")


# ── 3. Видалення облікового запису та осиротілі файли ───────────────────────
def fig_orphan_files():
    W, H = 1000, 480
    frags = []

    cols = [
        (30, "1 · Користувач активний",
         "Обліковий запис: andrij (UID 1005)\n\n"
         "• /home/andrij (inode: uid=1005)\n"
         "• /var/mail/andrij (inode: uid=1005)\n"
         "• /srv/shared/data.csv (inode: uid=1005)\n\n"
         "ls -l показує власником «andrij»",
         GREEN_FILL, FIELD),
        (360, "2 · Видалення userdel -r",
         "Записи в /etc/passwd і shadow стерто\n\n"
         "✓ /home/andrij — видалено\n"
         "✓ /var/mail/andrij — видалено\n"
         "✗ /srv/shared/data.csv — ЗАЛИШИВСЯ\n\n"
         "ls -l показує «1005» (без імені)",
         WARM_FILL, MUTED),
        (690, "3 · Повторне використання UID",
         "Створено новачка: bohdan (UID 1005)\n\n"
         "Ядро перевіряє тільки число 1005!\n"
         "bohdan отримує повний доступ до\n"
         "/srv/shared/data.csv попередника.\n\n"
         "Ризик витоку конфіденційних даних!",
         RED_FILL, POS)
    ]

    for x, title, desc, fcolor, scolor in cols:
        frags.append(rect(x, 60, 280, 260, fill=fcolor, stroke=scolor, sw=1.5, rx=8))
        frags.append(text(x + 140, 90, title, size=13, bold=True, color=INK))
        frags.append(line(x + 10, 105, x + 270, 105, color=scolor, sw=1.0))
        frags.append(mtext(x + 140, 130, desc, size=11, color=INK, lh=1.4))

    # Стрілки
    frags.append(arrow(310, 190, 360, 190, color=LINE, sw=1.8))
    frags.append(arrow(640, 190, 690, 190, color=LINE, sw=1.8))

    # Нижній блок: процедура аудиту
    frags.append(rect(30, 340, 940, 110, fill=BG, stroke=MUTED, sw=1.2, rx=8))
    frags.append(text(500, 365, "Аудит та знешкодження осиротілих ресурсів перед видаленням UID", size=13, bold=True))
    audit_text = (
        "1. Пошук файлів за числовим UID: find / -uid 1005 2>/dev/null  (або загальний пошук безпритульних: find / -nouser)\n"
        "2. Зміна власника або архівація: find / -uid 1005 -exec chown root:root {} +  або переміщення в архів безпеки.\n"
        "3. Перевірка фонових завдань: crontab -u andrij -r, перевірка at-черги, завершення процесів: pkill -u 1005."
    )
    frags.append(mtext(500, 392, audit_text, size=11, color=INK, lh=1.35))

    render(os.path.join(IMG, "orphan-files-and-userdel.svg"), W, H, *frags,
           title="Проблема повторного використання UID та осиротілих файлів")


if __name__ == "__main__":
    fig_account_provisioning()
    fig_shadow_lifecycle()
    fig_orphan_files()
    print("Усі 3 фігури згенеровано успішно.")

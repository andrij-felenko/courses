# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE   = "#eaf0fd"
GREEN  = "#eaf6ef"
RED    = "#fdecea"
WARM   = "#fff6e5"
GREY   = "#eceff1"
PURPLE = "#f3e5f5"

# ── 1. Ієрархія та граф залежностей завантажувальних таргетів systemd ──────────
def fig_target_dag_hierarchy():
    W, H = 1400, 720
    p = []

    p.append(text(700, 45, "Спрямований ациклічний граф (DAG) завантажувальних таргетів systemd", size=18, bold=True))

    # Стовпчик 1: Early Boot
    p.append(fitbox(50, 100, 260, 110, "1. Раннє завантаження:\nsysinit.target\n\n(ФС /, swap, sysctl,\nudev, LVM, crypto)", size=13, bold=True, fill=RED))

    # Стовпчик 2: Auxiliary Milestones
    p.append(fitbox(370, 100, 260, 80, "Допоміжні майлстоуни:\nsockets.target", size=13, fill=PURPLE))
    p.append(fitbox(370, 200, 260, 80, "Допоміжні майлстоуни:\ntimers.target", size=13, fill=PURPLE))
    p.append(fitbox(370, 300, 260, 80, "Допоміжні майлстоуни:\npaths.target", size=13, fill=PURPLE))
    p.append(fitbox(370, 400, 260, 80, "Точка синхронізації:\nnetwork.target", size=13, fill=WARM))

    # Стовпчик 3: Basic Target
    p.append(fitbox(690, 200, 280, 110, "2. Базовий стан системи:\nbasic.target\n\n(Усі таймери, сокети та\nлокальні ФС активні)", size=14, bold=True, fill=BLUE))

    # Стовпчик 4: Final Operational Targets
    p.append(fitbox(1040, 140, 310, 110, "3. Консольний режим (CLI):\nmulti-user.target\n\n(Мережеві демони, SSH,\nTTY, cron, користувачі)", size=14, bold=True, fill=GREEN))

    p.append(fitbox(1040, 340, 310, 110, "4. Графічний режим (GUI):\ngraphical.target\n\n(Дисплейний менеджер,\nWayland/X11 сесія)", size=14, bold=True, fill=GREEN))

    # Мережевий майлстоун для мережевих служб
    p.append(fitbox(1040, 520, 310, 90, "Активна мережева точка:\nnetwork-online.target\n\n(IP піднято, маршрут є)", size=13, fill=WARM))

    # Зв'язки між ранніми блоками
    p.append(arrow(310, 155, 370, 140, color=LINE, sw=1.8))
    p.append(arrow(310, 155, 370, 240, color=LINE, sw=1.8))
    p.append(arrow(310, 155, 370, 340, color=LINE, sw=1.8))
    p.append(arrow(310, 155, 370, 440, color=LINE, sw=1.8))

    # Зв'язки допоміжних блоків з basic.target
    p.append(arrow(630, 140, 690, 235, color=LINE, sw=1.8))
    p.append(arrow(630, 240, 690, 255, color=LINE, sw=1.8))
    p.append(arrow(630, 340, 690, 275, color=LINE, sw=1.8))

    # Зв'язок basic.target -> multi-user.target
    p.append(arrow(970, 240, 1040, 195, color=POS, sw=2))
    p.append(text(1005, 205, "After/Wants", size=11, color=POS, italic=True))

    # Зв'язок multi-user.target -> graphical.target
    p.append(arrow(1195, 250, 1195, 340, color=POS, sw=2))
    p.append(text(1210, 295, "After/Wants", size=11, color=POS, italic=True))

    # Зв'язок network.target -> network-online.target
    p.append(arrow(630, 440, 1040, 565, color=LINE, sw=1.5))

    # Нижня примітка
    p.append(rect(50, 630, 1300, 65, fill=GREY, stroke="#cfd8dc", sw=1))
    p.append(text(700, 665, "Порядок запуску визначається директивою After=, а склад залежностей — Wants= / Requires=.\nВузли .target не містять ExecStart= та виконують роль чистих груп синхронізації.", size=13))

    render(os.path.join(IMG, 'target-dag-hierarchy.svg'), W, H, *p)


# ── 2. порівняння SysVinit Runlevels та systemd Targets ──────────────────────
def fig_sysv_vs_systemd_targets():
    W, H = 1400, 640
    p = []

    p.append(text(700, 40, "Еволюція: Монолітні числові runlevels vs Графові цільові юніти", size=18, bold=True))

    # Ліва колонка — SysVinit
    p.append(rect(40, 80, 620, 520, fill="#ffffff", stroke="#cfd8dc", sw=1.5))
    p.append(text(350, 115, "Парадигма SysVinit (Лінійна шкала 0-6)", size=16, bold=True))

    p.append(fitbox(70, 150, 560, 70, "Числові стани у /etc/inittab:\nid:3:initdefault:", size=14, fill=WARM))
    p.append(arrow(350, 220, 350, 250, color=LINE, sw=1.5))

    p.append(fitbox(70, 250, 560, 100, "Послідовні каталоги скриптів:\n/etc/rc.d/rc3.d/\nK15httpd -> S10network -> S20syslog -> S55sshd", size=13, fill=RED))
    p.append(arrow(350, 350, 350, 380, color=LINE, sw=1.5))

    p.append(fitbox(70, 380, 560, 190, "Недоліки системи:\n- Синхронне однопотокове виконання скриптів Shell\n- Фіксовані номери S10/S55 замість графа залежностей\n- Неможливість описати проміжні стани\n- Ризик залишення невизначеного стану при помилках", size=13, fill=GREY))

    # Права колонка — systemd Targets
    p.append(rect(720, 80, 640, 520, fill="#ffffff", stroke="#cfd8dc", sw=1.5))
    p.append(text(1040, 115, "Парадигма systemd (Декларативний DAG)", size=16, bold=True))

    p.append(fitbox(750, 150, 580, 70, "Символьне посилання таргета за замовчуванням:\n/etc/systemd/system/default.target -> multi-user.target", size=13, fill=BLUE))
    p.append(arrow(1040, 220, 1040, 250, color=LINE, sw=1.5))

    p.append(fitbox(750, 250, 580, 100, "Сумісність через символьні посилання:\nrunlevel0.target -> poweroff.target\nrunlevel3.target -> multi-user.target\nrunlevel5.target -> graphical.target", size=13, fill=PURPLE))
    p.append(arrow(1040, 350, 1040, 380, color=LINE, sw=1.5))

    p.append(fitbox(750, 380, 580, 190, "Переваги systemd:\n- Паралельний запуск залежностей у багатопотоковому режимі\n- Декларативний граф (Wants=, Requires=, After=, Before=)\n- Динамічна та надійна ізоляція станів (systemctl isolate)\n- Масштабованість через дроп-ін каталоги .wants/ та .requires/", size=13, fill=GREEN))

    render(os.path.join(IMG, 'sysv-vs-systemd-targets.svg'), W, H, *p)


# ── 3. Механізм ізоляції станів (Transaction Engine) ─────────────────────────
def fig_isolation_transaction_engine():
    W, H = 1400, 660
    p = []

    p.append(text(700, 40, "Життєвий цикл транзакційного рушія PID 1 під час ізоляції (systemctl isolate)", size=18, bold=True))

    # Крок 1: Вхідна команда
    p.append(fitbox(50, 100, 280, 160, "1. Вхідна команда:\nsystemctl isolate kiosk.target\n\n(або D-Bus метод\nStartUnit(\"kiosk.target\",\n\"isolate\"))", size=13, bold=True, fill=BLUE))

    # Крок 2: Перевірка прапорця
    p.append(fitbox(380, 100, 280, 160, "2. Перевірка прапорця:\nAllowIsolate=yes\n\nЯкщо AllowIsolate=no ->\nТранзакцію скасовується\nз помилкою!", size=13, fill=WARM))

    # Крок 3: Обчислення транзакції
    p.append(fitbox(710, 100, 320, 160, "3. Побудова транзакції в PID 1:\n\n- Обчислення графа kiosk.target\n- Формування JOB_START для потрібних\n- Формування JOB_STOP для зайвих", size=13, bold=True, fill=PURPLE))

    # Крок 4: Фільтрація захищених юнітів
    p.append(fitbox(1080, 100, 270, 160, "4. Перевірка захисту:\nIgnoreOnIsolate=yes\n\n(journald, dbus, sysinit\nНЕ зупиняються!)", size=13, fill=GREEN))

    # Стрілки верхнього ряду
    p.append(arrow(330, 180, 380, 180, color=LINE, sw=2))
    p.append(arrow(660, 180, 710, 180, color=LINE, sw=2))
    p.append(arrow(1030, 180, 1080, 180, color=LINE, sw=2))

    # Нижній блок: Результат транзакції
    p.append(rect(50, 320, 1300, 300, fill="#ffffff", stroke="#cfd8dc", sw=1.5))
    p.append(text(700, 355, "Виконання робіт у транзакційній черзі (Job Queue)", size=16, bold=True))

    p.append(fitbox(80, 390, 370, 200, "Роботи активації (JOB_START):\n\n- kiosk.target\n- kiosk-browser.service\n- kiosk-watchdog.service\n- multi-user.target (залежність)", size=13, fill=GREEN))

    p.append(fitbox(510, 390, 380, 200, "Роботи зупинки (JOB_STOP):\n\n- graphical.target\n- gdm.service / display-manager\n- user-session.slice\n- службові фонові юніти вне графа", size=13, fill=RED))

    p.append(fitbox(930, 390, 390, 200, "Захищені збережені юніти:\n\n- systemd-journald.service\n- dbus.service\n- sysinit.target / basic.target\n- Точки монтування дискових масивів", size=13, fill=GREY))

    render(os.path.join(IMG, 'isolation-transaction-engine.svg'), W, H, *p)


if __name__ == '__main__':
    fig_target_dag_hierarchy()
    fig_sysv_vs_systemd_targets()
    fig_isolation_transaction_engine()
    print("Figures generated successfully.")

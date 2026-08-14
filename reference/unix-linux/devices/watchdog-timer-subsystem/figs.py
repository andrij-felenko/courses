# -*- coding: utf-8 -*-
"""
Генератор фігур SVG для теми "Підсистема та драйвери таймерів Watchdog (/dev/watchdog)"
"""
import os
import sys

# Додаємо шлях до scripts/ у корені репозиторію (4 рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def make_architecture_fig():
    path = os.path.join(IMG_DIR, "watchdog-architecture.svg")
    w, h = 820, 430

    t_title = text(w / 2, 28, "Архітектура підсистеми Watchdog у Linux", size=16, bold=True)

    b_user_bg = rect(30, 50, 760, 65, fill="#f9fafb", stroke="#d1d5db", rx=8)
    lbl_user = text(50, 72, "User Space", size=11, color=MUTED, bold=True, anchor="start")
    b_daemon, _, _ = textbox(250, 85, "systemd / watchdogd\n(Демон супервізії)", size=12, fill="#eef2ff", stroke="#4f46e5", min_w=200)
    b_uapi, _, _ = textbox(570, 85, "ioctl(WDIOC_KEEPALIVE)\nwrite('V')", size=12, fill="#eef2ff", stroke="#4f46e5", min_w=220)

    l_vfs = line(30, 130, 790, 130, color="#9ca3af", sw=1.2, dash="4,4")
    lbl_vfs = text(410, 126, "VFS / Character Device Boundary (/dev/watchdog, /dev/watchdog0)", size=11, color=MUTED, bold=True)

    b_kernel_bg = rect(30, 145, 760, 140, fill="#f0fdf4", stroke="#86efac", rx=8)
    lbl_kernel = text(50, 165, "Kernel Space (Watchdog Framework)", size=11, color=FIELD, bold=True, anchor="start")

    b_cdev, _, _ = textbox(190, 205, "cdev / watchdog_dev.c\n(/dev/watchdog Mux)", size=12, fill="#ffffff", stroke="#16a34a", min_w=180)
    b_core, _, _ = textbox(410, 205, "watchdog_core.c\nstruct watchdog_device", size=12, fill="#dcfce7", stroke="#16a34a", min_w=190)
    b_pre_gov, _, _ = textbox(630, 205, "Pretimeout Framework\n(panic, dumper, noop)", size=12, fill="#ffffff", stroke="#16a34a", min_w=180)

    b_kthread, _, _ = textbox(410, 260, "Kernel Ping Worker (watchdog_kworker / hrtimer)", size=11, fill="#ffffff", stroke="#16a34a", min_w=340)

    b_hw_bg = rect(30, 300, 760, 105, fill="#fff7ed", stroke="#fdba74", rx=8)
    lbl_hw = text(50, 320, "Drivers & Hardware", size=11, color=POS, bold=True, anchor="start")

    b_drv1, _, _ = textbox(160, 355, "iTCO_wdt / sp805_wdt\n(Апаратний драйвер)", size=11, fill="#ffffff", stroke="#ea580c", min_w=170)
    b_drv2, _, _ = textbox(410, 355, "softdog\n(Програмний таймер)", size=11, fill="#ffffff", stroke="#ea580c", min_w=170)
    b_chip, _, _ = textbox(650, 355, "SoC Timer / PMIC\nHardware RESET Pin", size=11, fill="#ffedd5", stroke="#c0392b", min_w=170)

    a1 = arrow(250, 108, 190, 185, color=LINE, sw=1.5)
    a2 = arrow(570, 108, 410, 185, color=LINE, sw=1.5)
    a3 = arrow(190, 225, 410, 225, color=LINE, sw=1.5)
    a4 = arrow(410, 225, 630, 225, color=LINE, sw=1.5)
    a5 = arrow(410, 243, 410, 277, color=LINE, sw=1.5)
    a6 = arrow(320, 277, 160, 335, color=LINE, sw=1.5)
    a7 = arrow(410, 277, 410, 335, color=LINE, sw=1.5)
    a8 = arrow(245, 355, 565, 355, color=LINE, sw=1.5)

    render(
        path,
        w,
        h,
        t_title,
        b_user_bg,
        lbl_user,
        b_daemon,
        b_uapi,
        l_vfs,
        lbl_vfs,
        b_kernel_bg,
        lbl_kernel,
        b_cdev,
        b_core,
        b_pre_gov,
        b_kthread,
        b_hw_bg,
        lbl_hw,
        b_drv1,
        b_drv2,
        b_chip,
        a1,
        a2,
        a3,
        a4,
        a5,
        a6,
        a7,
        a8,
    )


def make_timeline_fig():
    path = os.path.join(IMG_DIR, "watchdog-timeline.svg")
    w, h = 800, 360

    t_title = text(w / 2, 28, "Часова діаграма скидання лічильника та спрацювання таймауту", size=16, bold=True)

    l_axis = arrow(60, 280, 750, 280, color=INK, sw=2.0)
    lbl_axis = text(740, 305, "Час t (секунди)", size=12, bold=True)

    l_vaxis = arrow(80, 290, 80, 60, color=INK, sw=2.0)
    lbl_vaxis = text(40, 70, "Counter", size=11, bold=True)

    l_tout = line(80, 100, 720, 100, color=MUTED, sw=1.0, dash="3,3")
    lbl_tout = text(75, 104, "T_out (30s)", size=11, color=MUTED, anchor="end")

    l_tpre = line(80, 170, 720, 170, color=POS, sw=1.0, dash="3,3")
    lbl_tpre = text(75, 174, "T_pre (5s)", size=11, color=POS, anchor="end")

    p_cnt1 = line(80, 100, 240, 220, color=NEG, sw=2.0)
    p_reset1 = line(240, 220, 240, 100, color=FIELD, sw=1.5, dash="2,2")
    lbl_ping1 = text(240, 300, "Ping #1\n(WDIOC_KEEPALIVE)", size=10, color=FIELD, bold=True)
    c_ping1 = circle(240, 280, 5, fill=FIELD, stroke=INK)

    p_cnt2 = line(240, 100, 400, 220, color=NEG, sw=2.0)
    p_reset2 = line(400, 220, 400, 100, color=FIELD, sw=1.5, dash="2,2")
    lbl_ping2 = text(400, 300, "Ping #2\n(WDIOC_KEEPALIVE)", size=10, color=FIELD, bold=True)
    c_ping2 = circle(400, 280, 5, fill=FIELD, stroke=INK)

    lbl_crash = text(470, 240, "Зависання демона\nабо CPU Deadlock", size=11, color=POS, bold=True)

    p_cnt3 = line(400, 100, 610, 170, color=NEG, sw=2.0)
    p_cnt4 = line(610, 170, 670, 280, color=POS, sw=2.5)

    c_pre = circle(610, 170, 5, fill=POS, stroke=INK)
    lbl_pre_event = text(610, 150, "NMI Interrupt\n(Pretimeout Governor)", size=10, color=POS, bold=True)

    c_zero = circle(670, 280, 6, fill=POS, stroke=INK)
    lbl_reset_event = text(670, 320, "HARDWARE RESET!\n(System Reboot)", size=11, color=POS, bold=True)

    render(
        path,
        w,
        h,
        t_title,
        l_axis,
        lbl_axis,
        l_vaxis,
        lbl_vaxis,
        l_tout,
        lbl_tout,
        l_tpre,
        lbl_tpre,
        p_cnt1,
        p_reset1,
        lbl_ping1,
        c_ping1,
        p_cnt2,
        p_reset2,
        lbl_ping2,
        c_ping2,
        lbl_crash,
        p_cnt3,
        p_cnt4,
        c_pre,
        lbl_pre_event,
        c_zero,
        lbl_reset_event,
    )


def make_pretimeout_fig():
    path = os.path.join(IMG_DIR, "watchdog-pretimeout.svg")
    w, h = 820, 320

    t_title = text(w / 2, 28, "Механізм Pretimeout та перехоплення аварійних подій", size=16, bold=True)

    b_hw, _, _ = textbox(130, 120, "Апаратний лічильник\n(Досягнуто Pretimeout)", size=12, fill="#fee2e2", stroke="#dc2626", min_w=170)
    b_irq, _, _ = textbox(360, 120, "NMI / High-Priority IRQ\n(Переривання ядра)", size=12, fill="#fef3c7", stroke="#d97706", min_w=180)
    b_gov, _, _ = textbox(620, 120, "Watchdog Pretimeout Governor\n(watchdog_pretimeout.c)", size=12, fill="#e0e7ff", stroke="#4338ca", min_w=220)

    # 3 Варіанти Governors рознесені по X без накладання
    b_gov_panic, _, _ = textbox(160, 230, "Governor 'panic'\n(Виклик panic -> Kdump)", size=11, fill="#f3f4f6", stroke="#374151", min_w=210)
    b_gov_dump, _, _ = textbox(410, 230, "Governor 'dumper'\n(printk + register dump)", size=11, fill="#f3f4f6", stroke="#374151", min_w=210)
    b_gov_noop, _, _ = textbox(660, 230, "Governor 'noop'\n(Тільки sysfs uevent)", size=11, fill="#f3f4f6", stroke="#374151", min_w=200)

    a1 = arrow(215, 120, 270, 120, color=LINE, sw=1.8)
    a2 = arrow(450, 120, 510, 120, color=LINE, sw=1.8)

    a3 = arrow(620, 155, 160, 205, color=LINE, sw=1.5)
    a4 = arrow(620, 155, 410, 205, color=LINE, sw=1.5)
    a5 = arrow(620, 155, 660, 205, color=LINE, sw=1.5)

    render(
        path,
        w,
        h,
        t_title,
        b_hw,
        b_irq,
        b_gov,
        b_gov_panic,
        b_gov_dump,
        b_gov_noop,
        a1,
        a2,
        a3,
        a4,
        a5,
    )


if __name__ == "__main__":
    make_architecture_fig()
    make_timeline_fig()
    make_pretimeout_fig()
    print("SVG figures generated successfully.")

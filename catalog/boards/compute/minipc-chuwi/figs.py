# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

ACCENT = "#2457d6"
SOC = "#eaf0fd"
WARM = "#fdecea"


# ── Фігура 1: що всередині — SoC і плата навколо нього ───────────────────────
def fig_inside():
    W, H = 820, 560
    parts = []

    # Велика рамка SoC (система-на-кристалі)
    sx, sy, sw_, sh = 60, 70, 420, 400
    parts.append(rect(sx, sy, sw_, sh, fill=SOC, stroke=ACCENT, sw=2.2, rx=12))
    parts.append(text(sx + sw_ / 2, sy + 30, "SoC Intel N100 / N150 (один кристал)",
                      size=16, color=ACCENT, bold=True))

    # 4 ядра-Gracemont у ряд
    core_w, core_h, gap = 88, 62, 12
    cx0 = sx + 24
    cy = sy + 60
    for i in range(4):
        x = cx0 + i * (core_w + gap)
        parts.append(fitbox(x, cy, core_w, core_h,
                            "ядро %d\nGracemont\nE-core" % (i + 1),
                            size=12, fill=BG, stroke=INK, sw=1.5))
    parts.append(text(sx + sw_ / 2, cy + core_h + 24,
                      "4 ядра · 4 потоки · без Hyper-Threading",
                      size=12, color=MUTED))

    # Спільний кеш
    cache_y = cy + core_h + 40
    parts.append(fitbox(cx0, cache_y, 4 * core_w + 3 * gap, 40,
                        "спільний кеш 6 МБ", size=13, fill=FILL, stroke=INK))

    # iGPU + медіа-рушій
    gpu_y = cache_y + 58
    gpu_w = 4 * core_w + 3 * gap
    parts.append(fitbox(cx0, gpu_y, gpu_w, 60,
                        "графіка Intel Xe (24 EU)\nмедіа-декод H.265 / AV1 · Quick Sync",
                        size=13, fill="#eafaf1", stroke=FIELD, sw=1.6))

    # Контролери пам'яті / PCIe / USB — низ SoC
    ctrl_y = gpu_y + 78
    parts.append(fitbox(cx0, ctrl_y, 195, 54,
                        "контролер пам'яті\n1 канал DDR5/DDR4", size=11.5,
                        fill=BG, stroke=INK))
    parts.append(fitbox(cx0 + 205, ctrl_y, 172, 54,
                        "9 ліній PCIe 3.0\n+ USB, SATA, дисплеї", size=11.5,
                        fill=BG, stroke=INK))

    # ── Зовнішні до SoC блоки на платі ──
    rx = 560
    # RAM
    ram_y = 120
    parts.append(fitbox(rx, ram_y, 200, 66,
                        "ОЗП  (RAM)\nрозпаяне LPDDR5\nабо SO-DIMM DDR4/5",
                        size=12, fill=WARM, stroke=POS, sw=1.6))
    parts.append(arrow(sx + sw_, ctrl_y + 18, rx, ram_y + 33, color=POS, sw=2))
    parts.append(text((sx + sw_ + rx) / 2, ram_y + 8, "1 канал",
                      size=10.5, color=MUTED))

    # NVMe / SATA
    ssd_y = 240
    parts.append(fitbox(rx, ssd_y, 200, 66,
                        "диск  M.2 NVMe\n(PCIe) + гніздо\nSATA 2.5\" HDD/SSD",
                        size=12, fill=FILL, stroke=INK))
    parts.append(arrow(sx + sw_, ctrl_y + 30, rx, ssd_y + 33, color=ACCENT, sw=2))

    # I/O
    io_y = 360
    parts.append(fitbox(rx, io_y, 200, 82,
                        "порти назовні:\nUSB 3.0 / USB-C\nHDMI · DisplayPort\nEthernet · Wi-Fi",
                        size=12, fill=FILL, stroke=INK))
    parts.append(arrow(sx + sw_, ctrl_y + 42, rx, io_y + 41, color=ACCENT, sw=2))

    # Живлення знизу
    pwr_y = 490
    parts.append(fitbox(sx + 40, pwr_y, 360, 44,
                        "живлення 12 В від адаптера → внутрішні перетворювачі",
                        size=13, fill="#eafaf1", stroke=FIELD, sw=1.6))
    parts.append(arrow((sx + 40) + 180, pwr_y, sx + sw_ / 2, sy + sh, color=FIELD, sw=2))

    render(os.path.join(IMG, 'inside.svg'), W, H, *parts)


# ── Фігура 2: карта портів на корпусі ───────────────────────────────────────
def fig_ports():
    W, H = 860, 430
    parts = []
    parts.append(text(W / 2, 30, "Типова задня панель міні-ПК Chuwi", size=16, bold=True))

    # Корпус
    bx, by, bw, bh = 50, 70, 760, 150
    parts.append(rect(bx, by, bw, bh, fill="#eef1f4", stroke=INK, sw=2, rx=10))

    # Порти зліва направо. Кожен — гніздо + підпис нижче з великим запасом.
    ports = [
        ("живлення\n12 В", FIELD, "#eafaf1"),
        ("USB-C\n(дані+відео)", ACCENT, SOC),
        ("HDMI\n4K@60", INK, BG),
        ("Display-\nPort 4K", INK, BG),
        ("USB 3.0", ACCENT, SOC),
        ("USB 3.0", ACCENT, SOC),
        ("Gigabit\nEthernet", POS, WARM),
        ("аудіо\n3.5 мм", MUTED, FILL),
    ]
    n = len(ports)
    slot_w = 74
    slot_h = 46
    total = n * slot_w + (n - 1) * 14
    x0 = bx + (bw - total) / 2
    y_slot = by + 34
    for i, (label, col, fill) in enumerate(ports):
        x = x0 + i * (slot_w + 14)
        parts.append(rect(x, y_slot, slot_w, slot_h, fill=fill, stroke=col, sw=2, rx=5))
        # Підпис ПІД корпусом, вертикально розведений, щоб не накладався
        ly = by + bh + 40 + (i % 2) * 46
        parts.append(line(x + slot_w / 2, y_slot + slot_h, x + slot_w / 2, ly - 16,
                          color=MUTED, sw=1))
        cf = fit_font(max(label.split("\n"), key=len), slot_w + 30, 12)
        parts.append(mtext(x + slot_w / 2, ly, label, size=cf, color=INK))

    render(os.path.join(IMG, 'ports.svg'), W, H, *parts)


# ── Фігура 3: шари безголового сервера — від заліза до твого демона ──────────
def fig_stack():
    W, H = 860, 560
    parts = []
    parts.append(text(W / 2, 30, "Шари безголового сервера: хто кого несе", size=16, bold=True))

    # Спільна колонка шарів (стек знизу вгору малюємо зверху вниз)
    lx, lw = 70, 470
    layers = [
        ("залізо: x86-міні-ПК (N100), диск, Ethernet", "#eef1f4", INK, 44),
        ("ядро Linux + служби: systemd керує всім, що працює", SOC, ACCENT, 44),
    ]
    y = 54
    for label, fill, col, hh in layers:
        parts.append(fitbox(lx, y, lw, hh, label, size=13, fill=fill, stroke=col, sw=2))
        y += hh + 12

    # Рівень служб: два стовпці — Docker-контейнери і власний unit
    row_y = y
    row_h = 150
    # Docker зліва
    dx, dw = lx, 224
    parts.append(rect(dx, row_y, dw, row_h, fill="#eafaf1", stroke=FIELD, sw=2, rx=8))
    parts.append(text(dx + dw / 2, row_y + 22, "Docker (демон dockerd)", size=12.5,
                      color=FIELD, bold=True))
    svc = ["контейнер: Jellyfin", "контейнер: база даних", "контейнер: веб-сервіс"]
    for i, s in enumerate(svc):
        parts.append(fitbox(dx + 16, row_y + 40 + i * 34, dw - 32, 28, s,
                            size=11.5, fill=BG, stroke=INK))

    # Власний unit справа
    ux = lx + 246
    uw = lw - 246
    parts.append(rect(ux, row_y, uw, row_h, fill=WARM, stroke=POS, sw=2, rx=8))
    parts.append(text(ux + uw / 2, row_y + 22, "твоя служба (systemd unit)", size=12.5,
                      color=POS, bold=True))
    parts.append(fitbox(ux + 16, row_y + 40, uw - 32, 92,
                        "мій демон на C++\n\n• SIGTERM → чистий вихід\n• лог у journald\n• рестарт при падінні",
                        size=11.5, fill=BG, stroke=INK))

    # systemd тримає обидва стовпці — стрілки вниз від шару systemd
    sy = 54 + 44 + 12  # верх другого шару
    parts.append(text(lx + lw + 6, sy + 22, "керує", size=10.5, color=ACCENT, anchor="start"))
    parts.append(arrow(dx + dw / 2, sy + 44, dx + dw / 2, row_y, color=ACCENT, sw=1.8))
    parts.append(arrow(ux + uw / 2, sy + 44, ux + uw / 2, row_y, color=ACCENT, sw=1.8))

    # Праворуч — вхід по SSH до всього стека
    ssh_x = lx + lw + 60
    parts.append(fitbox(ssh_x, 150, 190, 150,
                        "ти — з ноутбука\n\nssh user@міні-ПК\n\nодин зашифрований\nканал у консоль\nвсього вузла",
                        size=12, fill=SOC, stroke=ACCENT, sw=2))
    parts.append(arrow(ssh_x, 225, lx + lw, 225, color=ACCENT, sw=2.2))
    parts.append(text((lx + lw + ssh_x) / 2, 214, "SSH", size=12, color=ACCENT, bold=True))

    render(os.path.join(IMG, 'stack.svg'), W, H, *parts)


# ── Фігура 4: життєвий цикл демона під systemd (сигнали й рестарт) ───────────
def fig_lifecycle():
    W, H = 880, 470
    parts = []
    parts.append(text(W / 2, 30, "Життя демона під systemd: сигнали, вихід, рестарт", size=16, bold=True))

    # Три головні стани в ряд
    bw, bh, gap = 200, 74, 90
    y0 = 90
    x_run = 60
    x_stop = x_run + bw + gap
    x_dead = x_stop + bw + gap

    parts.append(fitbox(x_run, y0, bw, bh,
                        "ПРАЦЮЄ\nголовний цикл, WATCHDOG=1\nраз на пів-періоду",
                        size=12, fill="#eafaf1", stroke=FIELD, sw=2))
    parts.append(fitbox(x_stop, y0, bw, bh,
                        "ЗУПИНЯЄТЬСЯ\nловить SIGTERM,\nдописує, закриває, виходить 0",
                        size=12, fill=SOC, stroke=ACCENT, sw=2))
    parts.append(fitbox(x_dead, y0, bw, bh,
                        "ЗУПИНЕНО\nsystemctl бачить\nчистий вихід",
                        size=12, fill=FILL, stroke=INK, sw=1.8))

    # PRACHUE -> ZUPYNYA: SIGTERM
    parts.append(arrow(x_run + bw, y0 + bh / 2, x_stop, y0 + bh / 2, color=ACCENT, sw=2))
    parts.append(text((x_run + bw + x_stop) / 2, y0 + bh / 2 - 12,
                      "SIGTERM", size=12, color=ACCENT, bold=True))
    parts.append(text((x_run + bw + x_stop) / 2, y0 + bh / 2 + 18,
                      "(systemctl stop)", size=10, color=MUTED))

    parts.append(arrow(x_stop + bw, y0 + bh / 2, x_dead, y0 + bh / 2, color=INK, sw=1.8))

    # Гілка «впав» від ПРАЦЮЄ вниз
    crash_y = 250
    parts.append(fitbox(x_run, crash_y, bw, 60,
                        "ВПАВ\nбаг, SIGKILL, вихід ≠ 0\nбез попередження",
                        size=12, fill=WARM, stroke=POS, sw=2))
    parts.append(arrow(x_run + bw / 2, y0 + bh, x_run + bw / 2, crash_y, color=POS, sw=2))
    parts.append(text(x_run + bw / 2 + 8, (y0 + bh + crash_y) / 2, "аварія",
                      size=11, color=POS, anchor="start"))

    # systemd рестарт: від ВПАВ назад у ПРАЦЮЄ через таймер
    restart_y = crash_y + 30
    mid_x = x_run + bw + gap / 2 + 40
    parts.append(fitbox(x_stop, crash_y, bw + gap + 40, 60,
                        "systemd: Restart=on-failure\nчекає RestartSec, піднімає знову",
                        size=12, fill="#fff7e6", stroke="#b8860b", sw=2))
    parts.append(arrow(x_run + bw, crash_y + 30, x_stop, crash_y + 30, color="#b8860b", sw=2))
    # стрілка рестарту вгору назад у ПРАЦЮЄ
    up_x = x_stop + bw + gap + 40 - 30
    parts.append(line(x_stop + bw + gap + 40, crash_y + 30, up_x + 120, crash_y + 30,
                      color="#b8860b", sw=2))
    parts.append(line(up_x + 120, crash_y + 30, up_x + 120, y0 + bh + 24,
                      color="#b8860b", sw=2))
    parts.append(arrow(up_x + 120, y0 + bh + 24, x_run + bw / 2 + 60, y0 + bh + 24,
                      color="#b8860b", sw=2))
    parts.append(line(x_run + bw / 2 + 60, y0 + bh + 24, x_run + bw / 2 + 60, y0 + bh,
                      color="#b8860b", sw=2))
    parts.append(text(up_x + 40, crash_y - 6, "автопідйом", size=11, color="#b8860b",
                      anchor="middle"))

    # Виноска про SIGKILL
    parts.append(fitbox(x_dead - 20, crash_y + 90, bw + 60, 50,
                        "не вийшов за TimeoutStopSec (90 с) →\nsystemd б'є SIGKILL — обірве брудно",
                        size=11, fill=BG, stroke=MUTED, sw=1.4))

    render(os.path.join(IMG, 'lifecycle.svg'), W, H, *parts)


if __name__ == '__main__':
    fig_inside()
    fig_ports()
    fig_stack()
    fig_lifecycle()
    print("ok")

# -*- coding: utf-8 -*-
"""Фігури до теми «Налагодження у VS Code» (базова версія).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).

Фігури теми (імена-слаги, без номерів):
  stack · launch-map · panels · servers
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── stack: розширення лише оркеструє той самий ланцюг ─────────────────────────
# Ідея: показати, що cortex-debug не замінює OpenOCD+GDB, а САМ їх запускає й
# керує ними; вікно редактора — це обгортка над тим самим RSP-ланцюгом.

def fig_stack():
    W, H = 820, 360
    p = []

    # верхня смуга — вікно VS Code (оркестратор)
    ide_x, ide_y, ide_w, ide_h = 40, 56, 740, 64
    p.append(rect(ide_x, ide_y, ide_w, ide_h, fill="#eaf0fd", stroke=NEG, sw=2.0, rx=8))
    p.append(text(ide_x + ide_w / 2, ide_y + 26, "VS Code + cortex-debug", size=15, color=NEG, bold=True))
    p.append(text(ide_x + ide_w / 2, ide_y + 46,
                  "читає launch.json · запускає сервер · веде GDB · малює панелі",
                  size=11, color=MUTED))

    # нижній ланцюг — той самий, що й без редактора
    y = 196
    bw, bh, gap = 150, 78, 56
    x0 = 56
    nodes = [
        ("OpenOCD", ["сервер RSP", ":3333"], "#fff8e1", "#e67e22"),
        ("arm-…-gdb", ["читає .elf", "команди RSP"], "#d5e8d4", "#27ae60"),
        ("Зонд + чип", ["SWD/JTAG", "залізо"], "#f4f6f8", INK),
    ]
    cx = []
    x = x0
    for title, sub, fill, col in nodes:
        p.append(rect(x, y, bw, bh, fill=fill, stroke=col, sw=2.0, rx=8))
        p.append(text(x + bw / 2, y + 28, title, size=14, color=col, bold=True))
        p.append(mtext(x + bw / 2, y + 48, sub, size=11, color=MUTED, lh=1.25))
        cx.append((x, x + bw))
        x += bw + gap

    # зв'язки всередині ланцюга
    p.append(arrow(cx[0][1] + 3, y + bh / 2, cx[1][0] - 3, y + bh / 2, color=LINE, sw=2.0))
    p.append(text((cx[0][1] + cx[1][0]) / 2, y + bh / 2 - 8, "RSP", size=10, color=MUTED))
    p.append(arrow(cx[1][1] + 3, y + bh / 2, cx[2][0] - 3, y + bh / 2, color=LINE, sw=2.0))
    p.append(text((cx[1][1] + cx[2][0]) / 2, y + bh / 2 - 8, "USB", size=10, color=MUTED))

    # редактор тримає обидва процеси (стрілки-«запускає» вниз)
    for (lo, hi) in (cx[0], cx[1]):
        mx = (lo + hi) / 2
        p.append(arrow(mx, ide_y + ide_h + 2, mx, y - 2, color=NEG, sw=1.6))
    p.append(text((cx[0][0] + cx[1][1]) / 2, ide_y + ide_h + 36, "запускає й веде",
                  size=10, color=NEG))

    msg = "Той самий ланцюг, що й у голому терміналі, — лише схований за вікном редактора"
    box, _, _ = textbox(W / 2, 326, msg, size=11, fill="#f4f6f8", stroke=LINE, sw=1.3, color=INK, pad=11)
    p.append(box)

    render(os.path.join(IMG, "stack.svg"), W, H, *p,
           title="Розширення не замінює OpenOCD і GDB — воно їх оркеструє")


# ── launch-map: анатомія launch.json і що кожне поле вмикає ───────────────────
# Ідея: ключові поля launch.json — це не магія, а підпис під кожною ланкою:
# одне обирає сервер, друге — конфіг чипа, третє — символи, четверте — де стати.

def fig_launch_map():
    W, H = 800, 430
    p = []

    # ліворуч — поля файлу
    fx, fw = 40, 320
    top = 60
    rh, rgap = 52, 12
    rows = [
        ('"servertype": "openocd"', "який GDB-сервер підняти", "#fff8e1", "#e67e22"),
        ('"configFiles": ["…cfg"]', "конфіг зонда й чипа (-f)", "#fff8e1", "#e67e22"),
        ('"executable": "app.elf"', "звідки брати символи", "#d5e8d4", "#27ae60"),
        ('"runToEntryPoint": "main"', "стати на вході в main", "#d5e8d4", "#27ae60"),
        ('"svdFile": "chip.svd"', "вікно периферії (регістри)", "#eaf0fd", NEG),
    ]
    targets = ["OpenOCD", "OpenOCD", "GDB (.elf)", "GDB", "панель периферії"]

    ty = top
    ry_centers = []
    for (key, desc, fill, col) in rows:
        p.append(rect(fx, ty, fw, rh, fill=fill, stroke=col, sw=1.5, rx=6))
        p.append(text(fx + 12, ty + 21, key, size=12, color=col, bold=True, anchor="start"))
        p.append(text(fx + 12, ty + 39, desc, size=10, color=INK, anchor="start"))
        ry_centers.append(ty + rh / 2)
        ty += rh + rgap

    # праворуч — куди це йде
    gx, gw = fx + fw + 96, 280
    for i, lab in enumerate(targets):
        cyc = ry_centers[i]
        p.append(arrow(fx + fw + 2, cyc, gx - 2, cyc, color=MUTED, sw=1.5))
        p.append(fitbox(gx, cyc - 16, gw, 32, lab, size=11,
                        fill="#f4f6f8", stroke=LINE, sw=1.2, color=INK))

    p.append(text(fx + fw / 2, top - 16, "launch.json (.vscode/)", size=12, color=MUTED, bold=True))
    p.append(text(gx + gw / 2, top - 16, "що це налаштовує", size=12, color=MUTED, bold=True))

    render(os.path.join(IMG, "launch-map.svg"), W, H, *p,
           title="launch.json: кожне поле — підпис під ланкою ланцюга")


# ── panels: чотири вікна налагодження і звідки кожне бере дані ────────────────
# Ідея: GUI не додає нових можливостей до GDB — він робить ВИДИМИМ те, що в
# голому gdb доводиться питати командами (print, x, info reg, disassemble).

def fig_panels():
    W, H = 820, 400
    p = []
    cw, ch, gx, gy = 360, 132, 24, 60
    x0 = 30
    cards = [
        ("Змінні та Watch", "p g_cfg.rate · info locals",
         "значення з .elf у контексті потоку", "#d5e8d4", "#27ae60"),
        ("Периферія (SVD)", "x/1xw 0x40021000",
         "регістри чипа з імен у .svd", "#eaf0fd", NEG),
        ("Памʼять", "x/16xw 0x3FFB0000",
         "сирий дамп будь-якої адреси", "#fff8e1", "#e67e22"),
        ("Дизасемблер", "disassemble · stepi",
         "інструкції + крок по асемблеру", "#fdecea", POS),
    ]
    for i, (title, cmd, sub, fill, col) in enumerate(cards):
        cx = x0 + (i % 2) * (cw + gx)
        cy = gy + (i // 2) * (ch + gy - 18)
        p.append(rect(cx, cy, cw, ch, fill=fill, stroke=col, sw=1.8, rx=8))
        p.append(text(cx + 16, cy + 28, title, size=14, color=col, bold=True, anchor="start"))
        # еквівалент у голому gdb — моноширинний рядок
        p.append(rect(cx + 16, cy + 42, cw - 32, 30, fill="#ffffff", stroke=LINE, sw=1.0, rx=4))
        p.append(text(cx + 26, cy + 62, "gdb: " + cmd, size=11, color=INK, anchor="start"))
        p.append(text(cx + 16, cy + 96, sub, size=11, color=MUTED, anchor="start"))
        p.append(text(cx + 16, cy + 116, "клік — замість набору команди", size=10, color=col, anchor="start"))

    render(os.path.join(IMG, "panels.svg"), W, H, *p,
           title="Панелі редактора = ті самі запити GDB, але видимі й клікабельні")


# ── servers: один launch.json, інший зонд — те саме вікно ────────────────────
# Ідея (паралель до rsp-frame з openocd-gdb): протокол між GDB і сервером
# однаковий, тож зміна одного поля servertype міняє весь нижній стек, а
# панелі й брейкпоінти лишаються ті самі.

def fig_servers():
    W, H = 800, 360
    p = []

    # спільний верх — те саме вікно й ті самі брейкпоінти
    tx, tw = 250, 300
    p.append(rect(tx, 52, tw, 56, fill="#eaf0fd", stroke=NEG, sw=2.0, rx=8))
    p.append(text(tx + tw / 2, 76, "те саме вікно VS Code", size=13, color=NEG, bold=True))
    p.append(text(tx + tw / 2, 96, "панелі · брейкпоінти · Watch — без змін", size=10, color=MUTED))

    # три варіанти servertype нижче
    y = 196
    bw, bh = 220, 92
    xs = [30, 290, 550]
    variants = [
        ('"openocd"', ["OpenOCD", "ST-Link / FT2232", "будь-який чип"], "#fff8e1", "#e67e22"),
        ('"jlink"', ["J-Link GDB Server", "зонд SEGGER", "RTOS-аналіз"], "#d5e8d4", "#27ae60"),
        ('"qemu"', ["емулятор QEMU", "без заліза", "тест на ПК"], "#f4f6f8", INK),
    ]
    for x, (key, sub, fill, col) in zip(xs, variants):
        p.append(rect(x, y, bw, bh, fill=fill, stroke=col, sw=1.8, rx=8))
        p.append(text(x + bw / 2, y + 24, 'servertype: ' + key, size=12, color=col, bold=True))
        p.append(mtext(x + bw / 2, y + 46, sub, size=10.5, color=MUTED, lh=1.3))
        # стрілка від спільного вікна вниз до кожного варіанта
        p.append(arrow(tx + tw / 2, 110, x + bw / 2, y - 2, color=MUTED, sw=1.3))

    msg = "Міняєш одне поле servertype — увесь нижній стек інший, а UI той самий (спільний RSP)"
    box, _, _ = textbox(W / 2, 330, msg, size=11, fill="#f4f6f8", stroke=LINE, sw=1.3, color=INK, pad=11)
    p.append(box)

    render(os.path.join(IMG, "servers.svg"), W, H, *p,
           title="Один launch.json, різні сервери — вікно не змінюється")


if __name__ == "__main__":
    fig_stack()
    fig_launch_map()
    fig_panels()
    fig_servers()
    print("OK: figures written to", IMG)

# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── chain: зонд → OpenOCD → GDB → інженер; .elf як словник збоку ──────────────
# Ідея: показати, на якому рівні абстракції працює кожна ланка і де вона бере знання.
# Зонд знає тільки біти; OpenOCD — чип; GDB — символи з .elf; інженер — логіку.

def fig_chain():
    W, H = 860, 300
    p = []
    y = 110
    bw, bh, gap = 168, 86, 42
    x0 = 18
    nodes = [
        ("Зонд", ["біти SWD/JTAG", "(апаратний рівень)"], "#fff8e1", "#e67e22"),
        ("OpenOCD", ["знає чип і конфіг;", "сервер RSP :3333"], "#eaf0fd", "#2457d6"),
        ("GDB", ["читає .elf:", "адреса → ім'я, рядок"], "#d5e8d4", "#27ae60"),
        ("Інженер", ["мислить логікою", "програми"], "#f4f6f8", "#1a1a1a"),
    ]
    cx = []
    x = x0
    for title, sub, fill, col in nodes:
        p.append(rect(x, y, bw, bh, fill=fill, stroke=col, sw=2.0, rx=8))
        p.append(text(x + bw / 2, y + 30, title, size=15, color=col, bold=True))
        p.append(mtext(x + bw / 2, y + 50, sub, size=11, color=MUTED, lh=1.25))
        cx.append((x, x + bw))
        x += bw + gap

    # стрілки між ланками, двобічні підписи рівнів перекладу
    labels = ["USB-команди", "запити регістрів", "Remote Serial\nProtocol (TCP)"]
    for i in range(3):
        ax, bx2 = cx[i][1], cx[i + 1][0]
        p.append(arrow(ax + 3, y + bh / 2, bx2 - 3, y + bh / 2, color=LINE, sw=2.0))
        midx = (ax + bx2) / 2
        p.append(mtext(midx, y - 10, labels[i], size=9, color=MUTED, lh=1.1))

    # .elf як зовнішнє джерело символів для GDB
    elf_cx = cx[2][0] + bw / 2
    ex, ey, ew, eh = elf_cx - 90, y + bh + 44, 180, 56
    p.append(rect(ex, ey, ew, eh, fill="#fff8e1", stroke="#e67e22", sw=1.6, rx=6))
    p.append(text(elf_cx, ey + 23, "app.elf", size=14, color="#e67e22", bold=True))
    p.append(text(elf_cx, ey + 42, "символи: адреса → ім'я", size=10, color=MUTED))
    p.append(arrow(elf_cx, ey - 2, elf_cx, y + bh + 2, color="#e67e22", sw=1.8))
    p.append(text(elf_cx + 14, (ey + y + bh) / 2 + 4, "«словник»", size=10, color="#e67e22", anchor="start"))

    render(os.path.join(OUT, "chain.svg"), W, H, *p,
           title="Чотири ланки: кожна перекладає на наступний рівень абстракції")


# ── command-map: словник команд GDB за призначенням (4 групи) ─────────────────
# Ідея: згрупувати щоденні команди за наміром (рух / огляд / пастки / monitor),
# щоб читач тримав у голові не список, а карту.

def fig_command_map():
    W, H = 840, 380
    p = []
    col_w, gap = 192, 16
    x0 = 20
    top = 56
    head_h = 30
    row_h = 40
    cols = [
        ("РУХ", "#2457d6", "#eaf0fd", [
            ("continue / c", "далі до пастки"),
            ("next / n", "крок, не входити"),
            ("step / s", "крок, входити"),
            ("finish", "вийти з функції"),
        ]),
        ("ОГЛЯД", "#27ae60", "#d5e8d4", [
            ("print / p VAR", "значення змінної"),
            ("backtrace / bt", "стек викликів"),
            ("info registers", "регістри CPU"),
            ("x/16xw ADDR", "дамп пам'яті"),
        ]),
        ("ПАСТКИ", "#c0392b", "#fdecea", [
            ("break / b LOC", "програмний"),
            ("hbreak LOC", "апаратний (Flash)"),
            ("watch VAR", "вотчпоінт запису"),
            ("tbreak LOC", "одноразовий"),
        ]),
        ("MONITOR (→ OpenOCD)", "#e67e22", "#fff8e1", [
            ("mon reset halt", "скинути й стати"),
            ("mon reg", "регістри ядра"),
            ("mon mdw ADDR", "читати слово"),
            ("mon flash erase", "стерти Flash"),
        ]),
    ]
    x = x0
    for head, col, fill, rows in cols:
        p.append(rect(x, top, col_w, head_h, fill=col, stroke=col, sw=1.5, rx=6))
        p.append(text(x + col_w / 2, top + 20, head, size=fit_font(head, col_w - 12, 13, True), color="#ffffff", bold=True))
        ry = top + head_h + 6
        for cmd, desc in rows:
            p.append(rect(x, ry, col_w, row_h, fill=fill, stroke=col, sw=1.0, rx=4))
            p.append(text(x + col_w / 2, ry + 17, cmd, size=11, color=col, bold=True))
            p.append(text(x + col_w / 2, ry + 32, desc, size=9, color=INK))
            ry += row_h + 6
        x += col_w + gap

    render(os.path.join(OUT, "command-map.svg"), W, H, *p,
           title="Карта команд GDB: рух, огляд, пастки, monitor")


# ── connect-fail: дерево «не підключається» — яка з ланок винна ───────────────
# Ідея: типова діагностика йде знизу вгору ланцюгом; кожна перевірка відсікає
# одну ланку. Це детальна фігура (для -d): від USB до .elf.

def fig_connect_fail():
    W, H = 840, 470
    p = []
    qx = 40                      # ліва колонка — питання
    qw, bh = 360, 50
    vgap = 66
    cx = qx + qw / 2
    fx = qx + qw + 70            # права колонка — вердикт «ні»
    fw = 280
    y = 40

    def node(yy, q, fill="#eef4ff", stroke=NEG):
        p.append(fitbox(qx, yy, qw, bh, q, size=12, fill=fill, stroke=stroke, sw=1.6, bold=True, color=INK))
        return yy + bh

    def verdict(yy, lab):
        p.append(fitbox(fx, yy, fw, 40, lab, size=11, fill="#fdecea", stroke=POS, sw=1.5, bold=True, color=POS))
        p.append(arrow(qx + qw + 2, yy + 20, fx - 2, yy + 20, color=POS, sw=1.6))
        p.append(text((qx + qw + fx) / 2, yy + 12, "ні", size=9, color=POS))

    checks = [
        ("Зонд видно в USB? (lsusb / Диспетчер)", "перевір кабель, драйвер, права"),
        ("OpenOCD стартував без помилок?", "не той .cfg: інтерфейс / чип"),
        ("Target halted, PC показано?", "живлення, RESET, режим завантаження"),
        ("target remote :3333 з'єднався?", "порт зайнятий / фаєрвол :3333"),
        ("Символи збігаються з Flash?", "перезапиши: load"),
    ]
    yy = y
    for i, (q, fail) in enumerate(checks):
        bot = node(yy, q)
        verdict(yy + 5, fail)
        if i < len(checks) - 1:
            p.append(arrow(cx, bot, cx, yy + vgap, color=FIELD, sw=1.8))
            p.append(text(cx + 14, bot + (vgap - bh) / 2 + 4, "так", size=9, color=FIELD, anchor="start"))
        yy += vgap

    # фінал — усе гаразд
    fy = yy
    p.append(rect(cx - 130, fy, 260, 40, fill="#d5e8d4", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(cx, fy + 25, "сеанс відлагодження працює", size=12, color=FIELD, bold=True))

    render(os.path.join(OUT, "connect-fail.svg"), W, H, *p,
           title="«Не підключається»: яка з ланок винна (зверху вниз)")


# ── rsp-frame: кадр Remote Serial Protocol ───────────────────────────────────
# Ідея: показати, що GDB↔сервер говорять простими текстовими пакетами
# $дані#кс — і саме тому будь-який сервер (OpenOCD, J-Link, qemu) взаємозамінний.

def fig_rsp_frame():
    W, H = 760, 300
    p = []
    y = 90
    # сам кадр
    parts = [
        ("$", "#6b7280", 34),
        ("m400d2010,4", INK, 200),   # приклад: читати 4 байти з адреси
        ("#", "#6b7280", 34),
        ("a7", POS, 56),
    ]
    x = 60
    bh = 52
    coords = []
    for s, col, w in parts:
        p.append(rect(x, y, w, bh, fill="#f4f6f8", stroke=LINE, sw=1.4, rx=4))
        p.append(text(x + w / 2, y + bh / 2 + 6, s, size=16, color=col, bold=True))
        coords.append((x, w))
        x += w
    total_r = x
    # підписи частин
    p.append(text(coords[0][0] + coords[0][1] / 2, y - 12, "старт", size=10, color=MUTED))
    p.append(text(coords[1][0] + coords[1][1] / 2, y - 12, "команда + аргументи", size=10, color=MUTED))
    p.append(text(coords[2][0] + coords[2][1] / 2, y - 12, "кінець", size=10, color=MUTED))
    p.append(text(coords[3][0] + coords[3][1] / 2, y - 12, "контр. сума", size=10, color=POS))

    # розшифровка прикладу
    p.append(text(60, y + bh + 36, "приклад: m400d2010,4 — «прочитай 4 байти з адреси 0x400d2010»",
                  size=12, color=INK, anchor="start"))
    p.append(text(60, y + bh + 58, "сервер відповідає '+' (кадр прийнято), тоді $<байти>#<кс>",
                  size=11, color=MUTED, anchor="start"))
    p.append(text(60, y + bh + 84, "кс = сума байтів даних mod 256 — простий текст по TCP",
                  size=11, color=MUTED, anchor="start"))

    # висновок: будь-який сервер RSP взаємозамінний
    msg = "Той самий протокол слухають OpenOCD, J-Link GDB Server, QEMU — GDB однаковий"
    box, bw2, bh2 = textbox(W / 2, y + bh + 130, msg, size=11, fill="#eaf0fd", stroke=NEG, sw=1.4, color=NEG, pad=12)
    p.append(box)

    render(os.path.join(OUT, "rsp-frame.svg"), W, H, *p,
           title="Кадр Remote Serial Protocol: $дані#контрольна-сума")


if __name__ == "__main__":
    fig_chain()
    fig_command_map()
    fig_connect_fail()
    fig_rsp_frame()
    print("OK: figures written to", OUT)

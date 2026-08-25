# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── stack-place: де в системі живе TinyUSB ───────────────────────────────────
# Ідея: TinyUSB — прошарок між «голим» апаратним USB-блоком МК і твоїм кодом
# класів. Знизу — залізо (різне на кожному чипі), посередині — портований стек
# (однаковий скрізь), зверху — твої tud-колбеки. Те, що шар стека той самий на
# різних МК, і є причина не писати регістровий код руками.
def fig_stack_place():
    W, H = 720, 360
    p = []
    layers = [
        ("Твій код: дескриптори + tud_*-колбеки", "#eafaf1", FIELD,
         "пишеш ти — однаково для будь-якого підтриманого МК"),
        ("TinyUSB: енумерація, класи CDC / HID / MSC, черги", "#eaf0fd", NEG,
         "портований стек — той самий код на ESP32, RP2040, STM32, nRF"),
        ("Портовий шар (dcd): драйвер USB-блоку чипа", "#f4f6f8", MUTED,
         "тонка прокладка під конкретне залізо — пишуть автори порту"),
        ("Апаратний USB-блок МК + D+ / D−", "#fdecea", POS,
         "регістри, FIFO, переривання — у кожного чипа свої"),
    ]
    top, lh = 56, 70
    for i, (name, fill, col, note) in enumerate(layers):
        y = top + i * lh
        p.append(rect(40, y, W - 80, lh - 14, fill=fill, stroke=col, sw=2.0, rx=9))
        p.append(text(W / 2, y + 24, name, size=14, color=col, bold=True))
        p.append(text(W / 2, y + 44, note, size=11, color=MUTED, italic=True))
        if i < len(layers) - 1:
            p.append(line(W / 2, y + lh - 14, W / 2, y + lh - 2, color=MUTED, sw=1.2, dash="3 3"))
    return render(os.path.join(OUT, "stack-place.svg"), W, H, *p,
                  title="Де в системі живе TinyUSB")


# ── descriptor-tree: ланцюг дескрипторів ─────────────────────────────────────
# Ідея: серце теми. Хост при під'єднанні читає не один опис, а вкладене дерево:
# Device → Configuration → Interface → Endpoint. Кожен рівень відповідає на своє
# питання. Композит — це просто кілька Interface під одним Device.
def fig_descriptor_tree():
    W, H = 760, 470
    p = []
    nodes = [
        (0, "Device", "хто загалом: VID, PID, клас, версія USB", FIELD, "#eafaf1"),
        (1, "Configuration", "скільки струму (bMaxPower), скільки інтерфейсів", NEG, "#eaf0fd"),
        (2, "Interface (CDC)", "одна функція-клас пристрою", POS, "#fdecea"),
        (3, "Endpoint IN / OUT", "канали даних: до хоста й від хоста", MUTED, "#f4f6f8"),
        (2, "Interface (HID)", "друга функція в тому ж пристрої → композит", POS, "#fdecea"),
        (3, "Endpoint IN", "канал звітів до хоста", MUTED, "#f4f6f8"),
    ]
    top, rh = 56, 60
    bx0, bw = 60, 230
    cx_q = 470
    for i, (depth, name, q, col, fill) in enumerate(nodes):
        y = top + i * rh
        x = bx0 + depth * 28
        w = bw - depth * 28
        p.append(rect(x, y, w, rh - 16, fill=fill, stroke=col, sw=1.8, rx=7))
        p.append(text(x + 12, y + 27, name, size=13, color=col, anchor="start", bold=True))
        # дужка-роз'яснення праворуч
        p.append(text(cx_q, y + 27, q, size=11, color=MUTED, anchor="start", italic=True))
        # вертикальні зв'язки вкладеності
        if depth > 0:
            px = bx0 + (depth - 1) * 28 + 14
            p.append(line(px, y - rh + (rh - 16), px, y + (rh - 16) / 2, color=col, sw=1.4))
            p.append(line(px, y + (rh - 16) / 2, x, y + (rh - 16) / 2, color=col, sw=1.4))
    p.append(fitbox(60, top + len(nodes) * rh + 16, W - 120, 36,
                    "Той самий ланцюг для всіх МК: ти заповнюєш байти — TinyUSB віддає їх хосту",
                    size=12, fill="#eafaf1", stroke=FIELD, sw=1.4, bold=True))
    return render(os.path.join(OUT, "descriptor-tree.svg"), W, H, *p,
                  title="Ланцюг дескрипторів: вкладене дерево")


# ── callback-model: хост питає → TinyUSB → твій tud-колбек ────────────────────
# Ідея: ти не опитуєш USB у циклі — ти даєш TinyUSB набір колбеків, а він кличе
# потрібний, коли по шині щось сталося. tud_task() прокручує цей механізм; події
# приходять у твій код tud_cdc_rx_cb / tud_hid_get_report_cb тощо.
def fig_callback_model():
    W, H = 760, 340
    p = []
    # три стовпці: хост → стек → твій код
    cols = [
        ("Хост (ПК)", "#f4f6f8", MUTED, ["надсилає байти", "просить звіт", "читає диск"]),
        ("TinyUSB\n(tud_task)", "#eaf0fd", NEG, ["розбирає пакет", "знаходить колбек", "веде черги"]),
        ("Твій код\n(tud_*-колбеки)", "#eafaf1", FIELD,
         ["tud_cdc_rx_cb", "tud_hid_get_report_cb", "tud_msc_read10_cb"]),
    ]
    cw = 200
    gap = (W - 3 * cw - 80) / 2
    top = 64
    centers = []
    for i, (name, fill, col, items) in enumerate(cols):
        x = 40 + i * (cw + gap)
        centers.append(x + cw / 2)
        p.append(rect(x, top, cw, 200, fill=fill, stroke=col, sw=2.0, rx=10))
        p.append(mtext(x + cw / 2, top + 26, name.split("\n"), size=14, color=col, bold=True, lh=1.15))
        for j, it in enumerate(items):
            iy = top + 78 + j * 38
            p.append(fitbox(x + 14, iy, cw - 28, 30, it, size=11, fill=BG, stroke=col, sw=1.2, bold=True))
    # стрілки між стовпцями
    midy = top + 100
    p.append(arrow(centers[0] + cw / 2, midy - 18, centers[1] - cw / 2, midy - 18, color=NEG, sw=1.8))
    p.append(text((centers[0] + centers[1]) / 2, midy - 26, "подія по шині", size=10, color=MUTED))
    p.append(arrow(centers[1] + cw / 2, midy + 18, centers[2] - cw / 2, midy + 18, color=FIELD, sw=1.8))
    p.append(text((centers[1] + centers[2]) / 2, midy + 10, "виклик колбека", size=10, color=MUTED))
    p.append(text(W / 2, top + 230, "Ти не опитуєш USB — стек сам кличе твій колбек, коли є що обробити",
                  size=12, color=INK, italic=True))
    return render(os.path.join(OUT, "callback-model.svg"), W, H, *p,
                  title="Колбек-модель: подія приходить до тебе")


# ── enumeration-steps: що коїться при під'єднанні (детальна) ──────────────────
# Ідея: енумерація — стрічка кроків, і кожен «не визначається» падає на КОНКРЕТНИЙ
# крок. Знаючи порядок, читаєш dmesg як історію хвороби.
def fig_enumeration_steps():
    W, H = 780, 360
    steps = [
        ("Підтяжка D+", "1.5 кОм до 3.3 В → хост бачить Full-Speed", NEG),
        ("Reset лінії", "хост скидає шину коротким стартовим станом", NEG),
        ("Адр. 0: 8 байт", "читає розмір EP0 зі спільної нульової адреси", POS),
        ("Set Address", "пристрій дістає унікальну адресу", FIELD),
        ("Дескриптори", "Device → Config → Interface → Endpoint", FIELD),
        ("Set Config", "конфігурацію обрано → пристрій готовий", FIELD),
    ]
    p = []
    n = len(steps)
    bw = (W - 60 - (n - 1) * 16) / n
    top = 80
    bh = 150
    for i, (name, desc, col) in enumerate(steps):
        x = 30 + i * (bw + 16)
        p.append(rect(x, top, bw, bh, fill="#f4f6f8", stroke=col, sw=1.8, rx=8))
        p.append(circle(x + bw / 2, top + 24, 13, fill=BG, stroke=col, sw=2.0))
        p.append(text(x + bw / 2, top + 29, str(i + 1), size=13, color=col, bold=True))
        p.append(mtext(x + bw / 2, top + 56, _wrap(name, 12), size=12, color=INK, bold=True, lh=1.15))
        p.append(mtext(x + bw / 2, top + 96, _wrap(desc, 16), size=10, color=MUTED, lh=1.2))
        if i < n - 1:
            p.append(arrow(x + bw + 1, top + bh / 2, x + bw + 15, top + bh / 2, color=MUTED, sw=1.6))
    p.append(fitbox(30, top + bh + 18, W - 60, 34,
                    "Збій «не визначається» завжди падає на конкретний крок — діагноз ставиш за тим, де урвалось",
                    size=12, fill="#fdecea", stroke=POS, sw=1.4, bold=True))
    return render(os.path.join(OUT, "enumeration-steps.svg"), W, H, *p,
                  title="Енумерація крок за кроком")


# ── composite-iad: композит і навіщо IAD (детальна) ──────────────────────────
# Ідея: один пристрій = кілька функцій. Класи з двох інтерфейсів (CDC) хост сам
# не згрупує — потрібен дескриптор IAD, що каже «ці два інтерфейси — одна функція».
def fig_composite_iad():
    W, H = 740, 380
    p = []
    # ліворуч: без IAD — хост бачить розсипані інтерфейси
    p.append(rect(28, 56, 320, 290, fill="#fdecea", stroke=POS, sw=1.6, rx=10))
    p.append(text(188, 82, "Без IAD: хост губиться", size=13, color=POS, bold=True))
    bad = ["Interface 0: CDC-керування", "Interface 1: CDC-дані",
           "Interface 2: HID"]
    for i, b in enumerate(bad):
        y = 104 + i * 46
        p.append(fitbox(46, y, 284, 34, b, size=11, fill=BG, stroke=MUTED, sw=1.2, bold=True))
    p.append(mtext(188, 264,
                   ["Хост не знає, що Interface 0 і 1 —",
                    "один CDC. Бере їх за різні пристрої",
                    "або вантажить не той драйвер."],
                   size=11, color=INK, lh=1.35))
    # праворуч: з IAD — два інтерфейси злиті в одну функцію
    p.append(rect(392, 56, 320, 290, fill="#eafaf1", stroke=FIELD, sw=1.6, rx=10))
    p.append(text(552, 82, "З IAD: функції злиті", size=13, color=FIELD, bold=True))
    p.append(fitbox(410, 104, 284, 26, "IAD: «Interface 0–1 = один CDC»", size=11,
                    fill=BG, stroke=FIELD, sw=1.4, bold=True))
    p.append(rect(424, 134, 256, 54, fill="#ffffff", stroke=NEG, sw=1.4, rx=6))
    p.append(text(552, 154, "Interface 0: CDC-керування", size=10, color=INK, bold=True))
    p.append(text(552, 174, "Interface 1: CDC-дані", size=10, color=INK, bold=True))
    p.append(fitbox(410, 200, 284, 26, "Interface 2: HID (окрема функція)", size=11,
                    fill=BG, stroke=POS, sw=1.2, bold=True))
    p.append(mtext(552, 264,
                   ["IAD каже хосту, які інтерфейси —",
                    "одна функція. Композитний CDC",
                    "без нього на Windows часто не встає."],
                   size=11, color=INK, lh=1.35))
    return render(os.path.join(OUT, "composite-iad.svg"), W, H, *p,
                  title="Композит: навіщо IAD")


# ── endpoint-types: типи кінцевих точок і їхні буфери (детальна) ──────────────
# Ідея: не всі канали однакові. Контрольний — діалог/енумерація; bulk — об'єм без
# гарантій часу (MSC); interrupt — дрібно й вчасно (HID); ізохронний — потік без
# повторів (звук). Кожен має свій буфер у пам'яті чипа, і вони не безкоштовні.
def fig_endpoint_types():
    W, H = 760, 360
    rows = [
        ("Control (EP0)", "діалог і енумерація; є на кожному пристрої", NEG, "запити Setup"),
        ("Bulk", "великий обсяг, без гарантії часу — MSC, CDC-дані", POS, "файли, диск"),
        ("Interrupt", "мало даних, але вчасно й регулярно — HID", FIELD, "звіти клавіш"),
        ("Isochronous", "сталий потік без повторів — звук, відео", MUTED, "аудіо-кадри"),
    ]
    p = []
    top, rh = 64, 58
    for i, (name, desc, col, use) in enumerate(rows):
        y = top + i * rh
        p.append(rect(40, y, 200, rh - 14, fill="#f4f6f8", stroke=col, sw=1.8, rx=7))
        p.append(text(140, y + 28, name, size=13, color=col, bold=True))
        p.append(text(260, y + 20, desc, size=11, color=INK, anchor="start"))
        p.append(text(260, y + 38, "приклад: " + use, size=10, color=MUTED, anchor="start", italic=True))
    p.append(fitbox(40, top + len(rows) * rh + 8, W - 80, 36,
                    "Кожна точка тримає буфер у пам'яті чипа — більше класів і точок означає більше витраченої RAM",
                    size=12, fill="#eaf0fd", stroke=NEG, sw=1.4, bold=True))
    return render(os.path.join(OUT, "endpoint-types.svg"), W, H, *p,
                  title="Типи кінцевих точок і навіщо кожен")


def _wrap(s, n):
    """Простий перенос рядка по словах до ~n символів — для багаторядкових підписів."""
    words, lines, cur = s.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > n:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    return lines


if __name__ == "__main__":
    fig_stack_place()
    fig_descriptor_tree()
    fig_callback_model()
    fig_enumeration_steps()
    fig_composite_iad()
    fig_endpoint_types()
    print("ok: stack-place, descriptor-tree, callback-model, enumeration-steps, composite-iad, endpoint-types")

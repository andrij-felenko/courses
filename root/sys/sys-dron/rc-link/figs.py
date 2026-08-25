# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «RC-лінк».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/.
Запуск:  python figs.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Рух стіка стає каналом ────────────────────────────────────────────────
# Ідея словами важка: положення осі стіка — це одне ЧИСЛО (1000..2000 мкс,
# центр 1500), і кожна вісь дає окремий канал; усі канали пакуються в один кадр.
def fig_channels():
    W, H = 900, 360
    P = [text(W / 2, 30, "Вісь стіка → число → канал", size=17, bold=True)]

    # стік ліворуч: квадрат із точкою-положенням
    sx, sy, ss = 90, 150, 90
    P.append(rect(sx, sy, ss, ss, fill="#fbfcfd", stroke=INK, sw=1.6, rx=8))
    P.append(line(sx, sy + ss / 2, sx + ss, sy + ss / 2, color="#e3e7ec", sw=1))
    P.append(line(sx + ss / 2, sy, sx + ss / 2, sy + ss, color="#e3e7ec", sw=1))
    P.append(circle(sx + ss * 0.66, sy + ss * 0.40, 7, fill=FIELD, stroke=FIELD))
    P.append(text(sx + ss / 2, sy + ss + 22, "правий стік", size=12, bold=True))
    P.append(text(sx + ss / 2, sy + ss + 38, "крен · тангаж", size=11, color=MUTED))

    # горизонтальна вісь однієї осі стіка: 1000..2000
    ax0, ax1, ay = 280, 760, 150
    P.append(line(ax0, ay, ax1, ay, color=MUTED, sw=1.4))
    for v, lab in [(0.0, "1000"), (0.5, "1500"), (1.0, "2000")]:
        x = ax0 + v * (ax1 - ax0)
        P.append(line(x, ay - 6, x, ay + 6, color=MUTED, sw=1.4))
        P.append(text(x, ay + 24, lab, size=11, color=MUTED))
    P.append(text((ax0 + ax1) / 2, ay - 40, "крен (CH1)", size=12, bold=True))
    P.append(text(ax0, ay - 14, "ліво", size=10, color=MUTED, anchor="start"))
    P.append(text(ax1, ay - 14, "право", size=10, color=MUTED, anchor="end"))
    P.append(text((ax0 + ax1) / 2, ay + 24, "нейтраль", size=10, color=FIELD, bold=True))
    # поточне положення стіка → крапка на осі (відповідає 0.66 праворуч)
    cx = ax0 + 0.66 * (ax1 - ax0)
    P.append(circle(cx, ay, 6, fill=FIELD, stroke=FIELD))
    P.append(line(cx, ay, cx, ay - 26, color=FIELD, sw=1.3, dash="3,3"))
    P.append(text(cx, ay - 30, "1660 мкс", size=11, color=FIELD, bold=True))
    P.append(arrow(sx + ss + 10, sy + ss / 2, ax0 - 12, ay, color=INK))

    # внизу: кадр із багатьох каналів
    fy = 270
    P.append(text(W / 2, fy - 14, "усі канали пакуються в ОДИН кадр і йдуть в ефір:",
                  size=12, color=INK))
    labels = ["газ", "крен", "тангаж", "нишп.", "aux1", "aux2", "…"]
    fw = 92
    fx = (W - fw * len(labels)) / 2
    for i, lab in enumerate(labels):
        x = fx + i * fw
        col = FIELD if i == 1 else INK
        fill = "#eef6ef" if i == 1 else "#f4f6f8"
        P.append(rect(x, fy, fw - 6, 30, fill=fill, stroke=col, sw=1.4, rx=4))
        P.append(text(x + (fw - 6) / 2, fy + 20, lab, size=11, color=col,
                      bold=(i == 1)))
    render(os.path.join(IMG, "channels.svg"), W, H, *P)


# ── 2. Повний ланцюг: стік → канали → радіолінк → RX → FC → мотори ───────────
# Ідея: дві РІЗНІ за природою точки стику — радіо (ефір, прив'язка) і дріт
# (протокол приймача). Їх корисно бачити окремо: різні проблеми, різні фікси.
def fig_chain():
    W, H = 960, 320
    P = [text(W / 2, 30, "Повний ланцюг керування: від стіка до мотора",
              size=17, bold=True)]

    y = 150
    boxes = [
        ("ПУЛЬТ\n(TX)", "стіки → канали → кадр", "#eef2f7"),
        ("ПРИЙМАЧ\n(RX)", "ловить ефір,\nрозпаковує канали", "#eef2f7"),
        ("КОНТРОЛЕР\n(FC)", "змішує канали,\nкерує моторами", "#eef2f7"),
        ("МОТОРИ", "тяга", "#eef6ef"),
    ]
    xs = [110, 380, 650, 880]
    bw = 150
    for (title, sub, fill), x in zip(boxes, xs):
        fr, w, h = textbox(x, y, title, size=13, bold=True, fill=fill,
                           stroke=INK, min_w=bw)
        P.append(fr)
        P.append(text(x, y + 44, sub.split("\n")[0], size=10, color=MUTED))
        if "\n" in sub:
            P.append(text(x, y + 58, sub.split("\n")[1], size=10, color=MUTED))

    # стик 1: радіолінк (по ефіру, червоний — потребує прив'язки)
    P.append(arrow(xs[0] + bw / 2 - 5, y, xs[1] - bw / 2 + 5, y, color=POS, sw=2.4))
    P.append(text((xs[0] + xs[1]) / 2, y - 30, "радіолінк", size=12, color=POS, bold=True))
    P.append(text((xs[0] + xs[1]) / 2, y - 14, "ефір · стрибки частоти", size=10, color=POS))
    P.append(text((xs[0] + xs[1]) / 2, y + 34, "▲ прив'язка", size=10.5, color=POS, bold=True))

    # стик 2: протокол приймача (дріт, синій)
    P.append(arrow(xs[1] + bw / 2 - 5, y, xs[2] - bw / 2 + 5, y, color=NEG, sw=2.4))
    P.append(text((xs[1] + xs[2]) / 2, y - 30, "протокол приймача", size=12, color=NEG, bold=True))
    P.append(text((xs[1] + xs[2]) / 2, y - 14, "дріт · SBUS / CRSF", size=10, color=NEG))

    # стик 3: контролер → мотори
    P.append(arrow(xs[2] + bw / 2 - 5, y, xs[3] - bw / 2 + 5, y, color=INK, sw=2.2))

    P.append(text(W / 2, H - 26,
                  "дві точки стику різні за природою: одна по ефіру, друга по дроту — і ламаються по-різному",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "chain.svg"), W, H, *P)


# ── 3. Прив'язка: спільний секрет робить пару «глухою» до чужих ───────────────
# Ідея: дві пари поряд на тому самому діапазоні не заважають, бо кожна стрибає
# за СВОЇМ псевдовипадковим розкладом, узгодженим раз під час прив'язки.
def fig_binding():
    W, H = 900, 400
    P = [text(W / 2, 30, "Прив'язка: кожна пара стрибає за своїм розкладом",
              size=17, bold=True)]

    # дві пари TX–RX
    def pair(cy, name, col, seq):
        P.append(textbox(110, cy, "пульт\n" + name, size=12, bold=True,
                         fill="#eef2f7", stroke=col, min_w=110)[0])
        P.append(textbox(W - 110, cy, "приймач\n" + name, size=12, bold=True,
                         fill="#eef2f7", stroke=col, min_w=110)[0])
        # маленька «гребінка» стрибків по частоті між ними
        gx0, gx1 = 210, W - 210
        lanes = 5
        lh = 16
        top = cy - lanes * lh / 2
        for k in range(lanes):
            ly = top + k * lh
            P.append(line(gx0, ly, gx1, ly, color="#eef0f3", sw=1))
        step = (gx1 - gx0) / len(seq)
        prev = None
        for i, s in enumerate(seq):
            x = gx0 + i * step + step / 2
            yv = top + s * lh
            P.append(circle(x, yv, 5, fill=col, stroke=col))
            if prev is not None:
                P.append(line(prev[0], prev[1], x, yv, color=col, sw=1.4))
            prev = (x, yv)
        P.append(text((gx0 + gx1) / 2, cy + lanes * lh / 2 + 16,
                      "ключ #%s · свій розклад стрибків" % name, size=10.5, color=col))

    pair(140, "A", NEG, [0, 3, 1, 4, 2, 0, 3])
    pair(290, "B", FIELD, [4, 1, 3, 0, 2, 4, 1])

    # висновок
    P.append(rect(60, H - 54, W - 120, 38, fill="#f4f6f8", stroke=INK, sw=1.3, rx=6))
    P.append(text(W / 2, H - 30,
                  "пара A не чує пари B: різні ключі й розклади → десятки пілотів літають поруч, не перехоплюючи керування",
                  size=11.5, color=INK))
    render(os.path.join(IMG, "binding.svg"), W, H, *P)


# ── 4. PWM проти PPM: пучок дротів проти одного ───────────────────────────────
# Ідея: PWM — окремий дріт на канал (як серво), дротів = каналів; PPM кладе ті
# самі імпульси ОДИН ЗА ОДНИМ по одному дроту. Видно економію проводки.
def fig_pwm_ppm():
    W, H = 900, 420
    P = [text(W / 2, 30, "Старі протоколи: PWM (пучок дротів) і PPM (один дріт)",
              size=17, bold=True)]

    # ── ліворуч: PWM — окремий дріт на канал ──
    lx = 70
    P.append(text(lx + 140, 70, "PWM: окремий дріт на КОЖЕН канал",
                  size=13, bold=True, color=POS, anchor="middle"))
    rxx = lx
    P.append(rect(rxx, 90, 70, 230, fill="#eef2f7", stroke=INK, sw=1.5, rx=6))
    P.append(text(rxx + 35, 210, "RX", size=12, bold=True))
    # 5 окремих імпульсів-доріжок
    labs = ["CH1", "CH2", "CH3", "CH4", "CH5"]
    for i, lab in enumerate(labs):
        y = 110 + i * 44
        x0 = rxx + 80
        x1 = x0 + 230
        P.append(text(x0 - 6, y + 4, lab, size=10, color=MUTED, anchor="end"))
        # один прямокутний імпульс 1000..2000 на доріжці
        base = y + 12
        wpulse = 40 + i * 14
        P.append(line(x0, base, x0 + 30, base, color=POS, sw=2))
        P.append(line(x0 + 30, base, x0 + 30, base - 18, color=POS, sw=2))
        P.append(line(x0 + 30, base - 18, x0 + 30 + wpulse, base - 18, color=POS, sw=2))
        P.append(line(x0 + 30 + wpulse, base - 18, x0 + 30 + wpulse, base, color=POS, sw=2))
        P.append(line(x0 + 30 + wpulse, base, x1, base, color=POS, sw=2))
    P.append(text(rxx + 175, 340, "8 каналів = 8 проводів", size=11, color=POS, bold=True))

    # ── праворуч: PPM — усі канали по одному дроту ──
    rx0 = 540
    P.append(text(rx0 + 150, 70, "PPM: усі канали по ОДНОМУ дроту",
                  size=13, bold=True, color=FIELD, anchor="middle"))
    P.append(rect(rx0, 90, 70, 100, fill="#eef2f7", stroke=INK, sw=1.5, rx=6))
    P.append(text(rx0 + 35, 145, "RX", size=12, bold=True))
    # один дріт, серія імпульсів-роздільників
    y = 220
    x0 = rx0 + 80
    x1 = W - 40
    P.append(line(x0, y, x1, y, color=FIELD, sw=2))
    P.append(arrow(rx0 + 70, 140, x0, y - 6, color=INK))
    # роздільники з різними проміжками = різні канали
    gaps = [34, 50, 28, 46, 38, 30]
    x = x0 + 10
    ch = 1
    for g in gaps:
        P.append(line(x, y, x, y - 26, color=FIELD, sw=2))
        P.append(line(x, y - 26, x + 6, y - 26, color=FIELD, sw=2))
        P.append(line(x + 6, y - 26, x + 6, y, color=FIELD, sw=2))
        if ch <= 5:
            P.append(text(x + g / 2 + 3, y + 16, "CH%d" % ch, size=9, color=MUTED))
        x += g
        ch += 1
    P.append(text(rx0 + 175, 340, "до ~8 каналів = 1 провід", size=11, color=FIELD, bold=True))

    P.append(text(W / 2, H - 24,
                  "обидва — аналогові за духом, повільні й вразливі до завад; нині їх витіснили цифрові",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "pwm-ppm.svg"), W, H, *P)


# ── 5. SBUS і CRSF: той самий UART, різні «характери» ────────────────────────
# Ідея: обидва — серійний UART, але SBUS односторонній (лише канали вниз),
# а CRSF двосторонній (канали вниз + телеметрія вгору) і набагато швидший.
def fig_sbus_crsf():
    W, H = 920, 380
    P = [text(W / 2, 30, "Цифрові протоколи приймача: SBUS і CRSF — це UART",
              size=17, bold=True)]

    def block(cy, name, sub, color, bidir):
        rxx, fcx = 150, W - 150
        P.append(textbox(rxx, cy, "RX", size=13, bold=True, fill="#eef2f7",
                         stroke=INK, min_w=90)[0])
        P.append(textbox(fcx, cy, "FC", size=13, bold=True, fill="#eef2f7",
                         stroke=INK, min_w=90)[0])
        # канали вниз (RX → FC)
        P.append(arrow(rxx + 50, cy - 8, fcx - 50, cy - 8, color=color, sw=2.4))
        P.append(text((rxx + fcx) / 2, cy - 18, "канали керування →", size=11,
                      color=color, bold=True))
        if bidir:
            P.append(arrow(fcx - 50, cy + 12, rxx + 50, cy + 12, color=NEG, sw=2.2))
            P.append(text((rxx + fcx) / 2, cy + 28, "← телеметрія", size=11,
                          color=NEG, bold=True))
        else:
            P.append(text((rxx + fcx) / 2, cy + 24, "(односторонній)", size=10,
                          color=MUTED))
        # підпис зліва
        P.append(text(rxx, cy + 52, name, size=13, bold=True, color=color))
        P.append(text(rxx, cy + 68, sub, size=10, color=MUTED))

    block(140, "SBUS (Futaba)", "інвертований UART · 100 000 бод · до 16 каналів", FIELD, False)
    block(280, "CRSF (Crossfire / ELRS)", "UART · 420 000 бод · наднизька затримка", POS, True)

    P.append(text(W / 2, H - 22,
                  "ті самі цеглинки UART — кадри, біти, швидкість — на службі керування дроном",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "sbus-crsf.svg"), W, H, *P)


# ── 6. Вибір RC-системи: компроміс діапазону ─────────────────────────────────
# Ідея: головна вісь вибору — 900 МГц (далі, крізь перешкоди) проти 2.4 ГГц
# (більше даних, менша дальність); конкретні системи лягають на цю вісь.
def fig_systems():
    W, H = 900, 360
    P = [text(W / 2, 30, "Вибір RC-системи: усе впирається в діапазон", size=17, bold=True)]

    # горизонтальна вісь компромісу
    ax0, ax1, ay = 120, W - 120, 150
    P.append(line(ax0, ay, ax1, ay, color=MUTED, sw=1.6))
    P.append(arrow(ax0 + 40, ay, ax0, ay, color=NEG, sw=1.6))
    P.append(arrow(ax1 - 40, ay, ax1, ay, color=POS, sw=1.6))
    P.append(text(ax0, ay - 18, "900 МГц (868/915)", size=12, color=NEG, bold=True, anchor="start"))
    P.append(text(ax0, ay + 22, "далі · крізь перешкоди", size=10, color=NEG, anchor="start"))
    P.append(text(ax1, ay - 18, "2.4 ГГц", size=12, color=POS, bold=True, anchor="end"))
    P.append(text(ax1, ay + 22, "більше даних · ближче", size=10, color=POS, anchor="end"))

    # системи як мітки на осі (приблизне положення за типовим діапазоном)
    sys = [
        (0.18, "ELRS", "відкрита, на LoRa\nнаднизька затримка"),
        (0.30, "TBS Crossfire", "фірмова, CRSF\nдалекобійна"),
        (0.78, "FrSky / Spektrum\nFutaba", "класичні масові\nвласні протоколи"),
    ]
    for t, name, desc in sys:
        x = ax0 + t * (ax1 - ax0)
        P.append(circle(x, ay, 6, fill=INK, stroke=INK))
        P.append(line(x, ay, x, ay + 60, color="#d0d5dd", sw=1, dash="3,3"))
        fr, w, h = textbox(x, ay + 95, name + "\n" + desc, size=10.5,
                           fill="#f4f6f8", stroke=INK)
        P.append(fr)

    P.append(text(W / 2, H - 22,
                  "дальнобійний політ — 900 МГц / ELRS; ближній спритний — 2.4 ГГц",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "systems.svg"), W, H, *P)


# ── 7. Failsafe: що приймач робить, коли сигнал зник ─────────────────────────
# Ідея: на втрату сигналу є заздалегідь заданий план. Три відповіді — від
# найгіршої (зависнути на останній команді) до найкращої (preset → RTL/посадка).
def fig_failsafe():
    W, H = 900, 420
    P = [text(W / 2, 30, "Failsafe: заздалегідь заданий план на втрату сигналу",
              size=17, bold=True)]

    # подія обриву
    P.append(textbox(W / 2, 80, "сигнал зник\n(вийшов за межу · заглушили · сіла батарея пульта)",
                     size=12, bold=True, fill="#fdecea", stroke=POS, color=POS)[0])

    # три гілки-відповіді
    branches = [
        (0.18, "ЗАВИСНУТИ\nна останній команді", POS,
         "найгірше:\nдрон летить геть,\nпоки не впаде", "#fdecea"),
        (0.50, "ПРИБРАТИ ГАЗ\n(або стоп моторів)", "#b08900",
         "не помчить удалечінь,\nале сяде де є", "#fff6e0"),
        (0.82, "ВІДДАТИ FAILSAFE-\nЗНАЧЕННЯ", FIELD,
         "найкраще:\nFC робить RTL\nчи м'яку посадку", "#eef6ef"),
    ]
    y_branch = 200
    for t, title, col, desc, fill in branches:
        x = 90 + t * (W - 180)
        P.append(arrow(W / 2, 112, x, y_branch - 22, color=MUTED, sw=1.4))
        P.append(textbox(x, y_branch, title, size=12, bold=True, fill=fill,
                         stroke=col, color=(INK if isinstance(col, str) and col.startswith("#") else col))[0])
        P.append(rect(x - 110, y_branch + 36, 220, 70, fill="#fbfcfd",
                      stroke="#dde3ea", sw=1.2, rx=6))
        for i, ln in enumerate(desc.split("\n")):
            P.append(text(x, y_branch + 58 + i * 16, ln, size=10.5, color=MUTED))

    P.append(rect(60, H - 56, W - 120, 40, fill="#eef6ef", stroke=FIELD, sw=1.4, rx=6))
    P.append(text(W / 2, H - 31,
                  "правило незмінне: ЗАВЖДИ налаштуй failsafe перед польотом — це різниця між «сам повернувся» і «загубився»",
                  size=11.5, color=INK, bold=True))
    render(os.path.join(IMG, "failsafe.svg"), W, H, *P)


if __name__ == "__main__":
    fig_channels()
    fig_chain()
    fig_binding()
    fig_pwm_ppm()
    fig_sbus_crsf()
    fig_systems()
    fig_failsafe()
    print("OK: 7 figures ->", IMG)

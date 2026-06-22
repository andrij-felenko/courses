# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── recover-not-patch: чистий відомий старт проти латання невідомого стану ─────
# Ідея: з однієї точки збою два шляхи. Латання тягне за собою невідомий стан
# (приховані «міни»), reset обриває його й веде у повністю визначений старт.

def fig_recover_not_patch():
    W, H = 720, 320
    p = []

    # точка збою
    fault, fw, fh = textbox(W / 2, 56, "збій під час роботи\n(стан пошкоджено)",
                            size=12, bold=True, color=POS, fill="#fdecea", stroke=POS, sw=1.8)
    p.append(fault)

    # лівий шлях — латати
    lx = 175
    p.append(line(W / 2 - fw / 4, 56 + fh / 2, lx, 132, color=POS, sw=1.7))
    patch, pw, ph = textbox(lx, 150, "латати на льоту",
                            size=12, bold=True, color=POS, fill=BG, stroke=POS, sw=1.6)
    p.append(patch)
    bad, bw, bh = textbox(lx, 246, "невідомий стан:\nприховані «міни»\nрезультат непевний",
                          size=11, color=INK, fill="#fdecea", stroke="#e8b4ad", sw=1.4)
    p.append(line(lx, 150 + ph / 2, lx, 246 - bh / 2, color=POS, sw=1.7, dash="5 4"))

    # правий шлях — reset
    rx = W - 175
    p.append(line(W / 2 + fw / 4, 56 + fh / 2, rx, 132, color=FIELD, sw=1.7))
    res, rw, rh = textbox(rx, 150, "перезавантажитися чисто",
                          size=12, bold=True, color=FIELD, fill=BG, stroke=FIELD, sw=1.6)
    p.append(res)
    good, gw, gh = textbox(rx, 250, "повністю визначений старт:\nRAM очищено, периферія\nв reset, змінні з нуля",
                           size=11, color=INK, fill="#eafaf0", stroke="#a9dcc0", sw=1.4)
    p.append(arrow(rx, 150 + rh / 2, rx, 250 - gh / 2, color=FIELD, sw=1.8))

    render(os.path.join(OUT, "recover-not-patch.svg"), W, H, *p,
           title="Сумніваєшся в стані — чистий старт надійніший за латання")


# ── when-reset: відновна ситуація vs невідновна ───────────────────────────────
# Ідея: розвилка на кожен збій. Відновне (давач не відповів, мережа впала) —
# повтор через паузу. Невідновне (псування структури, deadlock, вичерпання) — reset.

def fig_when_reset():
    W, H = 720, 360
    p = []

    q, qw, qh = textbox(W / 2, 50, "збій — він відновний?",
                        size=13, bold=True, fill="#f6f4ec", stroke=INK, sw=2, pad=12)
    p.append(q)

    # ліва гілка — так, відновне → повтор
    lx = 180
    p.append(text((W / 2 + lx) / 2 - 30, 95, "так", size=12, color=FIELD, bold=True))
    p.append(line(W / 2 - qw / 4, 50 + qh / 2, lx, 110, color=FIELD, sw=1.7))
    retry, rw, rh = textbox(lx, 128, "повтори, не перезавантажуй",
                            size=12, bold=True, color=FIELD, fill="#eafaf0", stroke=FIELD, sw=1.7)
    p.append(retry)
    ex_l = [
        "давач не відповів → ще раз через 100 мс",
        "мережа впала → зачекай і спробуй знову",
        "одне читання збійне → не чіпай весь пристрій",
    ]
    yy = 196
    for s in ex_l:
        b = fitbox(lx - 150, yy, 300, 34, s, size=10.5, fill=BG, stroke="#a9dcc0", sw=1.2)
        p.append(b)
        yy += 44

    # права гілка — ні, невідновне → reset
    rx = W - 180
    p.append(text((W / 2 + rx) / 2 + 30, 95, "ні", size=12, color=POS, bold=True))
    p.append(line(W / 2 + qw / 4, 50 + qh / 2, rx, 110, color=POS, sw=1.7))
    reset, rsw, rsh = textbox(rx, 128, "перезавантаж чисто",
                              size=12, bold=True, color=POS, fill="#fdecea", stroke=POS, sw=1.7)
    p.append(reset)
    ex_r = [
        "критичну структуру пошкоджено",
        "deadlock / зависання (ловить watchdog)",
        "вичерпано ресурс: фрагментація купи,",
        "витік дескрипторів, мертва периферія",
    ]
    yy = 196
    for s in ex_r:
        b = fitbox(rx - 150, yy, 300, 30, s, size=10.5, fill=BG, stroke="#e8b4ad", sw=1.2)
        p.append(b)
        yy += 38

    render(os.path.join(OUT, "when-reset.svg"), W, H, *p,
           title="Спершу спитай: збій відновний — повтор; невідновний — reset")


# ── state-through-reset: зберегти доказ ДО reset, бо reset стирає SRAM ─────────
# Ідея: часова смуга. Збій → записати причину/лічильник у пам'ять, що переживе
# reset (RTC / NVS) → reset чистить SRAM → після старту доказ на місці.

def fig_state_through_reset():
    W, H = 740, 300
    p = []
    y = 96
    bw, bh = 150, 60
    step = 188
    x = 24

    stages = [
        ("збій", "#fdecea", POS, "виявлено\nневідновну помилку"),
        ("зберегти ДО reset", "#eafaf0", FIELD, "причину, лічильник,\nprapor safe mode →\nRTC або NVS"),
        ("reset", "#eef4ff", NEG, "SRAM очищено\nповністю"),
        ("після старту", "#f6f4ec", INK, "доказ на місці:\nЧОМУ стався reset"),
    ]
    centers = []
    for i, (lab, fill, col, sub) in enumerate(stages):
        b = fitbox(x, y - bh / 2, bw, bh, lab, size=12, fill=fill, stroke=col, sw=1.8, bold=True, color=col)
        p.append(b)
        p.append(mtext(x + bw / 2, y + bh / 2 + 16, sub, size=9.5, color=MUTED))
        centers.append((x, x + bw))
        if i > 0:
            px = centers[i - 1][1]
            p.append(arrow(px, y, x - 2, y, color=INK, sw=1.8))
        x += step

    # застереження під «зберегти»
    warn = centers[1][0] + bw / 2
    p.append(text(warn, y - bh / 2 - 14, "тільки тут можна!", size=10, color=POS, bold=True))

    p.append(text(W / 2, H - 22,
                  "не записав до reset — reset зітре сам доказ того, чому він стався",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "state-through-reset.svg"), W, H, *p,
           title="Стан крізь reset: записати доказ ДО перезавантаження")


# ── boot-loop: лічильник + поріг → safe mode обриває нескінченний цикл ─────────
# Ідея: цикл reset→boot→reset, що сам себе годує при сталій причині; лічильник
# рахує невдалі старти, поріг розриває коло й уводить у безпечний режим.

def fig_boot_loop():
    W, H = 720, 330
    p = []
    cx, cy, r = 245, 165, 96

    # коло boot loop (дуга зі стрілкою)
    import math
    def pt(a):
        return cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))
    # майже повне коло
    a0, a1 = -60, 250
    x0, y0 = pt(a0); x1, y1 = pt(a1)
    large = 1 if (a1 - a0) % 360 > 180 else 0
    p.append('<path d="M %.1f %.1f A %.1f %.1f 0 %d 1 %.1f %.1f" fill="none" '
             'stroke="%s" stroke-width="2.6" marker-end="url(#arrow)"/>'
             % (x0, y0, r, r, large, x1, y1, POS))

    # вузли на колі
    b1 = textbox(cx, cy - r, "reset", size=11, bold=True, color=POS, fill="#fdecea", stroke=POS, sw=1.6)[0]
    b2 = textbox(cx + r, cy, "boot", size=11, bold=True, color=INK, fill=BG, stroke=INK, sw=1.5)[0]
    b3 = textbox(cx, cy + r, "падіння", size=11, bold=True, color=POS, fill="#fdecea", stroke=POS, sw=1.6)[0]
    p += [b1, b2, b3]
    p.append(mtext(cx - r - 8, cy - 6, "стала\nпричина", size=10, color=MUTED, anchor="end"))
    p.append(mtext(cx, cy, "boot loop", size=13, color=POS, bold=True))

    # вихід: лічильник + поріг → safe mode
    gx = 540
    cnt, cw, ch = textbox(gx, 96, "лічильник невдалих\nстартів (у NVS)",
                          size=11, bold=True, color=INK, fill="#eef4ff", stroke=NEG, sw=1.6)
    p.append(cnt)
    p.append(arrow(cx + r + 18, cy - 30, gx - cw / 2, 110, color=NEG, sw=1.6))

    thr, tw, th = textbox(gx, 188, "поріг (напр. 3)\nперевищено?",
                          size=11, bold=True, color=INK, fill=BG, stroke=INK, sw=1.5)
    p.append(thr)
    p.append(arrow(gx, 96 + ch / 2, gx, 188 - th / 2, color=INK, sw=1.6))

    safe, sw_, sh = textbox(gx, 280, "увійти в safe mode:\nкільце розірвано",
                            size=11, bold=True, color=FIELD, fill="#eafaf0", stroke=FIELD, sw=1.8)
    p.append(safe)
    p.append(arrow(gx, 188 + th / 2, gx, 280 - sh / 2, color=FIELD, sw=1.8))
    p.append(text(gx + tw / 2 + 6, 188, "так", size=10, color=FIELD, bold=True, anchor="start"))

    render(os.path.join(OUT, "boot-loop.svg"), W, H, *p,
           title="Boot loop: лічильник і поріг розривають нескінченний цикл")


if __name__ == "__main__":
    fig_recover_not_patch()
    fig_when_reset()
    fig_state_through_reset()
    fig_boot_loop()
    print("OK: figures written to", OUT)

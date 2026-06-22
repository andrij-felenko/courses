# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── escalation: драбина «що пробувати далі, коли просте не допомогло» ──────────
# Ідея: лічильник збоїв — не лік, а підказка наступного кроку. Кожен щабель
# чіпляється лише тоді, коли попередній не вилікував; кольори ведуть від
# спокійного (чорний RESTART) до тривожного (червоний відкат прошивки).
def fig_escalation():
    W, H = 760, 430
    bx, bw, bh = 200, 360, 52          # головна колонка дій
    cx = bx + bw / 2
    gap = 70                            # крок по вертикалі між щаблями
    y0 = 64
    steps = [
        ("RESTART\n(просто перезавантажся)",      FILL,      INK,  "разовий збій"),
        ("SAFE MODE\n(урізана функціональність)",  "#fff3cd", "#c07000", "поріг: 5 за хвилину"),
        ("ВІДКОТИТИ КОНФІГ\nдо дефолту або попереднього", "#eaf0fd", NEG, "safe mode не зарадив"),
        ("ВІДКОТИТИ ПРОШИВКУ\nна попередній OTA-слот", "#fdecea", POS, "конфіг не допоміг"),
        ("ЗАСТРЯГТИ в SAFE MODE\n+ покликати на допомогу", "#fdecea", POS, "крайній рубіж"),
    ]
    p = []
    centers = []
    for i, (label, fill, col, _cond) in enumerate(steps):
        y = y0 + i * gap
        cy = y + bh / 2
        centers.append(cy)
        sw = 2.4 if i in (3, 4) else 1.8
        p.append(rect(bx, y, bw, bh, fill=fill, stroke=col, sw=sw))
        p.append(mtext(cx, cy - 6, label, size=12, color=col, bold=True))
    # умова-ярлик ліворуч від кожного щабля + стрілка вниз між щаблями
    for i in range(len(steps)):
        cond = steps[i][3]
        cy = centers[i]
        box, w, h = textbox(110, cy, cond, size=10, pad=7, fill=FILL,
                            stroke=MUTED, sw=1.0, color=MUTED)
        p.append(box)
        p.append(arrow(110 + w / 2, cy, bx - 2, cy, color=MUTED, sw=1.2))
        if i < len(steps) - 1:
            p.append(arrow(cx, centers[i] + bh / 2, cx, centers[i + 1] - bh / 2,
                           color=MUTED, sw=1.5))
    # вертикаль «лічильник зростає» праворуч
    p.append(line(bx + bw + 18, y0, bx + bw + 18, centers[-1] + bh / 2, color=POS, sw=2.5))
    p.append(arrow(bx + bw + 18, centers[-1] + bh / 2 - 12, bx + bw + 18,
                   centers[-1] + bh / 2 + 4, color=POS, sw=2.5))
    p.append(mtext(bx + bw + 26, (y0 + centers[-1]) / 2, "boot_fail_cnt\nзростає",
                   size=11, color=POS, anchor="start"))
    render(os.path.join(OUT, "escalation-ladder.svg"), W, H, *p,
           title="Драбина ескалації: кожен щабель — коли попереднє не допомогло")


# ── lifecycle: серія швидких рестартів → поріг → safe mode → скидання ──────────
# Ідея: показати лічильник у часі. Сходинки вгору на кожен патологічний reset,
# пунктир порога, момент safe mode, і зелений обрив у 0 після T секунд спокою.
def fig_lifecycle():
    W, H = 760, 360
    ox, oy = 64, 232            # початок осей
    aw = 632                    # довжина осі часу
    top = 64
    rows = 6                    # 0..5
    rh = (oy - top) / (rows - 1)
    thr = 5                     # поріг
    p = []
    # осі
    p.append(line(ox, top, ox, oy, color=MUTED, sw=1.0))
    p.append(line(ox, oy, ox + aw, oy, color=MUTED, sw=1.0))
    p.append(text(ox + aw, oy + 18, "час", size=11, color=MUTED, italic=True, anchor="end"))
    p.append(text(ox - 12, top - 6, "лічильник", size=11, color=MUTED, anchor="start"))
    for v in range(rows):
        yy = oy - v * rh
        p.append(line(ox - 4, yy, ox, yy, color=MUTED, sw=1.0))
        p.append(text(ox - 8, yy + 4, str(v), size=10, color=MUTED, anchor="end"))
    # лінія порога
    ythr = oy - thr * rh
    p.append(line(ox, ythr, ox + aw, ythr, color=POS, sw=1.5, dash="6 4"))
    p.append(text(ox + aw - 2, ythr - 6, "поріг", size=10, color=POS, bold=True, anchor="end"))

    # сходинки лічильника: x-позиції рестартів
    xs = [ox + 70 + i * 58 for i in range(6)]       # 6 рестартів до порога
    vals = [1, 2, 3, 4, 5, 5]                        # після power-on +1 на кожен збій
    # старт у 0
    p.append(line(ox, oy, xs[0], oy, color=INK, sw=2.2))
    prev_x, prev_v = xs[0], 0
    for x, v in zip(xs, vals):
        y_prev = oy - prev_v * rh
        y_new = oy - v * rh
        p.append(line(prev_x, y_prev, x, y_prev, color=INK, sw=2.2))   # плато до рестарту
        p.append(line(x, y_prev, x, y_new, color=INK, sw=2.2))         # стрибок угору
        p.append(text(x, oy + 16, "reset", size=9, color=MUTED, anchor="middle"))
        prev_x, prev_v = x, v
    # порогу досягнуто → safe mode
    x_thr = xs[4]
    p.append(text(x_thr, top + 4, "поріг досягнуто", size=10, color=POS, bold=True, anchor="middle"))
    p.append(rect(x_thr + 6, top + 14, 150, oy - top - 14, fill="#fdecea", stroke=POS, sw=1.0, rx=3))
    p.append(mtext((x_thr + 6 + x_thr + 156) / 2, (top + oy) / 2, "SAFE MODE",
                   size=12, color=POS, bold=True))
    # після стабільної роботи — обрив у 0
    x_ok = xs[5] + 96
    p.append(line(prev_x, oy - prev_v * rh, x_ok, oy - prev_v * rh, color=FIELD, sw=2.2))
    p.append(line(x_ok, oy - prev_v * rh, x_ok, oy, color=FIELD, sw=2.2))
    p.append(line(x_ok, oy, ox + aw - 4, oy, color=FIELD, sw=2.2))
    p.append(mtext((x_ok + ox + aw) / 2, oy + 18, "60 с стабільно → 0",
                   size=10, color=FIELD, bold=True))
    render(os.path.join(OUT, "counter-lifecycle.svg"), W, H, *p,
           title="Життя лічильника: швидкі рестарти ростуть до порога, потім обнуляються")


# ── reset domains: який reset зберігає RTC-пам'ять, а який стирає ──────────────
# Ідея (ключова й неочевидна): watchdog/panic — Core Reset, RTC живе → лічильник
# доїде. Brownout/power-on — System Reset, RTC-домен теж скидається → у NOINIT
# лишається сміття, тому потрібен магічний-числовий вартовий.
def fig_reset_domains():
    W, H = 760, 320
    p = []
    # дві колонки: Core Reset (RTC живе) | System Reset (RTC скинуто)
    colw, colh = 320, 200
    lx, rx = 50, 390
    ty = 70
    # ліва: Core Reset
    p.append(rect(lx, ty, colw, colh, fill="#eef7f0", stroke=FIELD, sw=2.0))
    p.append(mtext(lx + colw / 2, ty + 26, "Core Reset", size=15, color=FIELD, bold=True))
    p.append(mtext(lx + colw / 2, ty + 50, "ядро скинуто, RTC-домен живий",
                   size=11, color=INK))
    for i, s in enumerate(["watchdog (TASK_WDT / INT_WDT)", "panic (PANIC)", "програмний esp_restart()"]):
        p.append(fitbox(lx + 24, ty + 74 + i * 34, colw - 48, 28, s, size=11,
                        fill=FILL, stroke=MUTED, sw=1.0, color=INK))
    p.append(mtext(lx + colw / 2, ty + colh - 14, "RTC-пам'ять зберігається → лічильник доїде",
                   size=11, color=FIELD, bold=True))
    # права: System Reset
    p.append(rect(rx, ty, colw, colh, fill="#fdeeec", stroke=POS, sw=2.0))
    p.append(mtext(rx + colw / 2, ty + 26, "System Reset", size=15, color=POS, bold=True))
    p.append(mtext(rx + colw / 2, ty + 50, "скидається весь чип разом з RTC",
                   size=11, color=INK))
    for i, s in enumerate(["power-on (POWERON)", "brown-out (BROWNOUT)"]):
        p.append(fitbox(rx + 24, ty + 74 + i * 34, colw - 48, 28, s, size=11,
                        fill=FILL, stroke=MUTED, sw=1.0, color=INK))
    p.append(mtext(rx + colw / 2, ty + colh - 26, "у RTC_NOINIT — сміття, не нуль",
                   size=11, color=POS, bold=True))
    p.append(mtext(rx + colw / 2, ty + colh - 10, "тому магічне число вартує лічильник",
                   size=11, color=POS, bold=True))
    render(os.path.join(OUT, "reset-domains.svg"), W, H, *p,
           title="Чому RTC переживає watchdog, але не brown-out")


if __name__ == "__main__":
    fig_escalation()
    fig_lifecycle()
    fig_reset_domains()
    print("figs done")

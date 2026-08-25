# -*- coding: utf-8 -*-
"""Фігури до теми «Вирівнювання зносу Flash».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

HOT  = "#c0392b"   # зношене / гаряче
COLD = "#2457d6"   # свіже / холодне
OK   = "#27ae60"   # рівно / здорове


def _brick(x, y, w, h, wear, label=None, sub=None):
    """Блок флеші, залитий кольором за часткою зносу wear∈[0..1]:
    від синього (свіжий) до червоного (зношений)."""
    # проста інтерполяція синій→червоний через сірий
    r = int(0x24 + (0xc0 - 0x24) * wear)
    g = int(0x57 + (0x39 - 0x57) * wear)
    b = int(0xd6 + (0x2c - 0xd6) * wear)
    fill = "#%02x%02x%02x" % (r, g, b)
    out = ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="4" '
           'fill="%s" opacity="0.85" stroke="#1a1a1a" stroke-width="1.2"/>'
           % (x, y, w, h, fill))
    if label:
        out += text(x + w / 2, y + h / 2 + 4, label, size=11, color="#ffffff", bold=True)
    if sub:
        out += text(x + w / 2, y + h + 13, sub, size=9.5, color=MUTED)
    return out


# ── 1. Чому в комірки є межа: стирання прострілює ізолятор і псує його ─────────
def fig_why_wear():
    W, H = 760, 360
    f = [text(W / 2, 26, "Кожне стирання жене заряд крізь тонкий ізолятор — і поволі псує його",
              size=15, bold=True)]

    # три стадії однієї комірки: свіжа → потерта → пробита
    stages = [
        (150, "Свіжа комірка", ["ізолятор цілий,", "заряд тримається", "роками"], COLD, 0),
        (380, "Після десятків тисяч", ["у стінках застрягли", "заряди, ізолятор", "потоншав"], "#e67e22", 6),
        (610, "Кінець ресурсу", ["заряд витікає за", "години — біт більше", "не тримається"], HOT, 12),
    ]
    for cx, ttl, lines, col, ntrap in stages:
        # плавучий заряд (пастка) — прямокутник, довкола ізолятор
        gx, gy, gw, gh = cx - 46, 90, 92, 34
        # ізолятор (тунельний оксид) — рамка знизу
        f.append(rect(gx - 6, gy - 6, gw + 12, gh + 40, fill="#f4f6f8", stroke=col, sw=2))
        f.append(rect(gx, gy, gw, gh, fill="#eaf0fd" if col == COLD else "#fdecea",
                      stroke=col, sw=1.8))
        f.append(text(cx, gy + 21, "заряд", size=10.5, color=col, bold=True))
        # тунельний оксид — тонка смуга під пасткою; застряглі заряди — крапки в ній
        oy = gy + gh + 6
        f.append(rect(gx, oy, gw, 16, fill="#ffffff", stroke=col, sw=1.4))
        f.append(text(cx, oy + 12, "ізолятор", size=9, color=MUTED))
        import random
        random.seed(ntrap)
        for _ in range(ntrap):
            tx = gx + 6 + random.random() * (gw - 12)
            ty = oy + 4 + random.random() * 8
            f.append(circle(tx, ty, 1.7, fill=HOT, stroke=HOT))
        f.append(text(cx, 78, ttl, size=12, color=col, bold=True))
        f.append(mtext(cx, oy + 40, lines, size=10, color=MUTED, lh=1.25))

    # стрілки старіння між стадіями
    f.append(arrow(150 + 70, 200, 380 - 70, 200, color="#e67e22", sw=2))
    f.append(arrow(380 + 70, 200, 610 - 70, 200, color=HOT, sw=2))
    f.append(text((150 + 380) / 2, 194, "цикли стирання →", size=10, color="#e67e22", italic=True))
    f.append(text((380 + 610) / 2, 194, "цикли стирання →", size=10, color=HOT, italic=True))

    f.append(line(50, H - 46, W - 50, H - 46, color=MUTED, sw=1, dash="4,4"))
    f.append(text(W / 2, H - 26,
                  "знос лічать не роками, а числом «стерти-записати» (P/E-циклами): ресурс скінченний",
                  size=11.5, color=INK, bold=True))
    render(os.path.join(IMG, "why-wear.svg"), W, H, *f)


# ── 2. Наївно (гарячий LBA вбиває один блок) vs вирівняно (знос розмазано) ────
def fig_naive_vs_leveled():
    W, H = 780, 380
    f = [text(W / 2, 26, "Одна й та сама флеш під тим самим навантаженням: без вирівнювання й з ним",
              size=15, bold=True)]

    def panel(x0, title, wears, col_title, dead=False):
        f.append(text(x0 + 150, 62, title, size=13, color=col_title, bold=True))
        bw, bh, gap = 60, 46, 14
        for i, wv in enumerate(wears):
            bx = x0 + i % 4 * (bw + gap)
            by = 86 + (i // 4) * (bh + 26)
            lab = "%d%%" % int(wv * 100)
            f.append(_brick(bx, by, bw, bh, wv, label=lab))
            if dead and wv >= 0.99:
                # хрест «мертвий блок»
                f.append(line(bx + 6, by + 6, bx + bw - 6, by + bh - 6, color="#000", sw=2))
                f.append(line(bx + bw - 6, by + 6, bx + 6, by + bh - 6, color="#000", sw=2))
        return

    # ліва панель: наївно — один блок 100% (мертвий), решта майже свіжі
    naive = [1.0, 0.05, 0.04, 0.05, 0.06, 0.05, 0.04, 0.05]
    panel(70, "Наївно: гарячі дані б'ють в один блок", naive, HOT, dead=True)
    f.append(mtext(70 + 150, 250, ["той самий блок стирали знову й знову →", "він помер, хоч сусіди майже не працювали"],
                   size=10.5, color=HOT, lh=1.3))

    # вертикальний роздільник
    f.append(line(W / 2, 74, W / 2, 300, color=MUTED, sw=1, dash="5,5"))

    # права панель: вирівняно — усі ~35%
    lev = [0.34, 0.36, 0.35, 0.33, 0.36, 0.34, 0.35, 0.35]
    panel(430, "Вирівняно: знос розмазано по всіх", lev, OK)
    f.append(mtext(430 + 150, 250, ["жоден блок не вибивається наперед →", "ресурс усієї флеші служить цілком"],
                   size=10.5, color=OK, lh=1.3))

    f.append(line(50, H - 40, W - 50, H - 40, color=MUTED, sw=1, dash="4,4"))
    f.append(text(W / 2, H - 20,
                  "мета вирівнювання зносу: тримати число стирань усіх блоків якомога ближче одне до одного",
                  size=11.5, color=INK, bold=True))
    render(os.path.join(IMG, "naive-vs-leveled.svg"), W, H, *f)


# ── 3. Динамічне лишає холодні блоки недоторканими; статичне їх зрушує ─────────
def fig_dynamic_vs_static():
    W, H = 780, 380
    f = [text(W / 2, 26, "Динамічне вирівнювання не чіпає «холодні» дані — і саме там ховається пастка",
              size=15, bold=True)]

    bw, bh, gap = 66, 44, 14
    # верхній ряд: динамічне — блоки з активними даними зношуються, «холодний» стоїть свіжим
    ytop = 78
    f.append(text(60, ytop - 16, "Динамічне: крутить лише блоки, які й так переписують",
                  size=12, color="#e67e22", bold=True, anchor="start"))
    dyn = [(0.55, "часті"), (0.58, "часті"), (0.54, "часті"), (0.05, "ХОЛОДНІ"), (0.57, "часті"), (0.56, "часті")]
    for i, (wv, tag) in enumerate(dyn):
        bx = 60 + i * (bw + gap)
        f.append(_brick(bx, ytop, bw, bh, wv, label="%d%%" % int(wv * 100), sub=tag))
        if tag == "ХОЛОДНІ":
            f.append(rect(bx - 3, ytop - 3, bw + 6, bh + 6, fill="none", stroke=COLD, sw=2.2, rx=6))
    f.append(mtext(60, ytop + bh + 44,
                   ["блок із рідко змінюваними даними («холодний») жодного разу не зрушив —",
                    "решта зносилися до 55–58 %, а він застряг на 5 %: половина ресурсу флеші лежить мертвим капіталом"],
                   size=10, color="#e67e22", lh=1.35, anchor="start"))

    # роздільна лінія
    f.append(line(50, 208, W - 50, 208, color=MUTED, sw=1, dash="5,5"))

    # нижній ряд: статичне — холодний блок примусово переселено, знос вирівнявся
    ybot = 242
    f.append(text(60, ybot - 16, "Статичне: примусово переселяє й холодні дані, аби й той блок працював",
                  size=12, color=OK, bold=True, anchor="start"))
    stat = [(0.33, ""), (0.35, ""), (0.34, ""), (0.32, "тепер теж"), (0.34, ""), (0.35, "")]
    for i, (wv, tag) in enumerate(stat):
        bx = 60 + i * (bw + gap)
        f.append(_brick(bx, ybot, bw, bh, wv, label="%d%%" % int(wv * 100), sub=tag))
        if tag:
            f.append(rect(bx - 3, ybot - 3, bw + 6, bh + 6, fill="none", stroke=OK, sw=2.2, rx=6))
    f.append(text(60, ybot + bh + 30,
                  "холодні дані відселили у зношеніший блок, а свіжий пустили під активний запис — знос зійшовся до ~34 %",
                  size=10, color=OK, anchor="start"))
    render(os.path.join(IMG, "dynamic-vs-static.svg"), W, H, *f)


# ── 4. Механізм: лічильники стирань керують вибором блока під запис ────────────
def fig_counters():
    W, H = 760, 380
    f = [text(W / 2, 26, "Як контролер це робить: у кожного блока — лічильник стирань, і вибір іде за ним",
              size=15, bold=True)]

    # таблиця блоків з лічильниками
    rows = [("блок 0", 812, 0.81), ("блок 1", 47, 0.05), ("блок 2", 790, 0.79),
            ("блок 3", 805, 0.80), ("блок 4", 51, 0.05)]
    x0, y0 = 90, 84
    rw, rh, gap = 150, 40, 12
    f.append(text(x0, y0 - 14, "лічильник стирань кожного блока (у RAM/службовій ділянці)",
                  size=11, color=MUTED, anchor="start", italic=True))
    for i, (name, cnt, wear) in enumerate(rows):
        by = y0 + i * (rh + gap)
        f.append(_brick(x0, by, rw, rh, wear))
        f.append(text(x0 + 12, by + rh / 2 + 4, name, size=11.5, color="#fff", bold=True, anchor="start"))
        f.append(text(x0 + rw - 12, by + rh / 2 + 4, "%d" % cnt, size=13, color="#fff",
                      bold=True, anchor="end"))

    # праворуч — правила вибору
    rx = x0 + rw + 60
    tb1 = textbox(rx + 150, y0 + 30, "Новий запис →\nбрати блок із НАЙМЕНШИМ\nлічильником (тут блок 1: 47)",
                  size=11, color=COLD, stroke=COLD, fill="#eaf0fd", bold=False)
    f.append(tb1[0])
    tb2 = textbox(rx + 150, y0 + 130,
                  "Розрив завеликий?\n(812 − 47 = 765 ≫ порога)\n→ переселити холодні дані\nз блока-ветерана у свіжий",
                  size=11, color=HOT, stroke=HOT, fill="#fdecea", bold=False)
    f.append(tb2[0])
    tb3 = textbox(rx + 150, y0 + 250,
                  "Мета: тримати max − min\nлічильників у вузькій смузі",
                  size=11, color=OK, stroke=OK, fill="#eafaf0", bold=False)
    f.append(tb3[0])

    f.append(line(50, H - 34, W - 50, H - 34, color=MUTED, sw=1, dash="4,4"))
    f.append(text(W / 2, H - 15,
                  "лічильник — це «пробіг» блока; вирівнювання = не давати одним блокам обганяти інші",
                  size=11.5, color=INK, bold=True))
    render(os.path.join(IMG, "counters.svg"), W, H, *f)


if __name__ == "__main__":
    fig_why_wear()
    fig_naive_vs_leveled()
    fig_dynamic_vs_static()
    fig_counters()
    print("OK: 4 figures ->", IMG)

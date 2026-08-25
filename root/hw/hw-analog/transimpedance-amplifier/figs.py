# -*- coding: utf-8 -*-
"""Фігури до статті «Трансімпедансний підсилювач (TIA)»
(book/electronics/analog/transimpedance-amplifier).
Фігури статті transimpedance-amplifier.md:
  idea.svg       — суть: джерело струму → віртуальна земля → весь струм у Rf → U = -I·Rf
  resistor-vs.svg— чому не просто резистор: на R напруга гойдає вузол; TIA тримає вузол при 0
  cf-cure.svg    — вхідна ємність задирає шумовий коефіцієнт; Cf ставить нуль і згладжує пік
  bandwidth.svg  — компроміс: більший Cf тихіший і стабільніший, але вужча смуга 1/(2π·Rf·Cf)
Фігури вставки math-tia-stability.md (виведення стійкості через петльове підсилення):
  beta-zero.svg      — β падає з fz=1/(2π·Rf·Cin); обернена 1/β (шумовий коеф.) з тієї ж fz лізе вгору
  closure.svg        — |A| і 1/β на одному полі: без Cf сходяться під 40 дБ/дек → −180°, запас фази 0
  cf-compensation.svg— Cf додає в 1/β полюс fp: підйом зрізано в полицю, перетин під 20 дБ/дек, запас повернуто
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Локальні символи ─────────────────────────────────────────────────────────
def opamp(cx, cy, w=70, h=64, plus_top=True):
    """Трикутник ОП вістрям праворуч. Повертає (svg, in_top, in_bot, out_pt)."""
    x0 = cx - w / 2
    pts = "%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (
        x0, cy - h / 2, x0, cy + h / 2, cx + w / 2, cy)
    body = ('<polygon points="%s" fill="#fbfbfd" stroke="%s" stroke-width="1.8"/>'
            % (pts, INK))
    in_top = (x0, cy - h / 4)
    in_bot = (x0, cy + h / 4)
    out_pt = (cx + w / 2, cy)
    s_top = "−" if plus_top is False else "+"
    s_bot = "+" if plus_top is False else "−"
    c_top = NEG if s_top == "−" else POS
    c_bot = NEG if s_bot == "−" else POS
    body += text(x0 + 13, in_top[1] + 5, s_top, size=18, color=c_top, bold=True)
    body += text(x0 + 13, in_bot[1] + 5, s_bot, size=18, color=c_bot, bold=True)
    return body, in_top, in_bot, out_pt


def photodiode(cx, cy, r=13):
    """Символ фотодіода: діод-трикутник + дві стрілочки світла."""
    out = circle(cx, cy, r, fill="#fffdf3", stroke=INK, sw=1.6)
    # трикутник анод→катод (струм донизу)
    out += ('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
            % (cx - 6, cy - 5, cx + 6, cy - 5, cx, cy + 4, INK))
    out += line(cx - 6, cy + 4, cx + 6, cy + 4, color=INK, sw=2)
    # два промені світла, що падають
    for dx in (-1, 1):
        bx, by = cx + dx * 4 - 16, cy - 18
        out += arrow(bx, by, bx + 9, by + 10, color=FIELD, sw=1.6)
    return out


def node(cx, cy):
    return circle(cx, cy, 3.2, fill=INK, stroke=INK, sw=1)


def gnd(cx, y):
    out = line(cx, y, cx, y + 8, color=INK, sw=1.8)
    yy = y + 8
    for i, w in enumerate((14, 9, 4)):
        out += line(cx - w / 2, yy + i * 4, cx + w / 2, yy + i * 4, color=INK, sw=1.8)
    return out


def res_h(x1, x2, y, label=None, color=INK):
    """Горизонтальний резистор-зигзаг між x1..x2 на висоті y."""
    out = line(x1, y, x1 + 8, y, color=color, sw=1.6)
    out += line(x2 - 8, y, x2, y, color=color, sw=1.6)
    seg = (x2 - 8) - (x1 + 8)
    n = 6
    step = seg / n
    pts = []
    for i in range(n + 1):
        xx = x1 + 8 + i * step
        yy = y + (5 if i % 2 else -5) if 0 < i < n else y
        pts.append("%.1f,%.1f" % (xx, yy))
    out += ('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6"/>'
            % (" ".join(pts), color))
    if label:
        out += text((x1 + x2) / 2, y - 11, label, size=13, color=color, bold=True)
    return out


def cap_h(x1, x2, y, label=None, color=NEG):
    """Горизонтальний конденсатор (дві пластини) між x1..x2."""
    mid = (x1 + x2) / 2
    out = line(x1, y, mid - 5, y, color=color, sw=1.6)
    out += line(mid + 5, y, x2, y, color=color, sw=1.6)
    out += line(mid - 5, y - 9, mid - 5, y + 9, color=color, sw=2)
    out += line(mid + 5, y - 9, mid + 5, y + 9, color=color, sw=2)
    if label:
        out += text(mid, y - 14, label, size=12, color=color, bold=True)
    return out


# ── 1) Суть: струм у віртуальну землю, весь у Rf ─────────────────────────────
def fig_idea():
    W, H = 720, 360
    cx, cy = 430, 175
    body, in_top, in_bot, out_pt = opamp(cx, cy, plus_top=False)  # − зверху
    nodes = [body]

    # неінвертувальний вхід (+, нижній) → земля
    nodes.append(line(in_bot[0], in_bot[1], in_bot[0] - 40, in_bot[1], color=INK))
    nodes.append(gnd(in_bot[0] - 40, in_bot[1]))

    # сумувальний вузол (− вхід)
    nx, ny = in_top[0] - 70, in_top[1]
    nodes.append(line(in_top[0], in_top[1], nx, ny, color=INK))
    nodes.append(node(nx, ny))
    nodes.append(text(nx - 6, ny - 14, "U ≈ 0", size=13, color=FIELD, bold=True))
    nodes.append(mtext(nx - 6, ny + 22, ["віртуальна", "земля"],
                       size=11, color=MUTED))

    # фотодіод як джерело струму: зверху вниз у вузол
    pdx, pdy = nx, ny - 95
    nodes.append(photodiode(pdx, pdy))
    nodes.append(line(pdx, pdy + 13, pdx, ny, color=INK))
    # стрілка струму I у вузол
    nodes.append(arrow(pdx, ny - 60, pdx, ny - 30, color=POS, sw=2.2))
    nodes.append(text(pdx + 16, ny - 44, "I", size=15, color=POS, bold=True))
    nodes.append(text(pdx - 40, pdy - 22, "світло → струм", size=12, color=FIELD))

    # зворотний зв'язок: Rf від виходу до вузла (зверху)
    fb_y = cy - 80
    nodes.append(line(out_pt[0], out_pt[1], out_pt[0] + 22, out_pt[1], color=INK))
    ox = out_pt[0] + 22
    nodes.append(line(ox, out_pt[1], ox, fb_y, color=INK))
    nodes.append(res_h(nx, ox, fb_y, label="Rf"))
    nodes.append(line(nx, fb_y, nx, ny, color=INK))
    # стрілка: той самий струм тече крізь Rf
    nodes.append(arrow(nx + 70, fb_y, nx + 130, fb_y, color=POS, sw=2.0))
    nodes.append(text(nx + 100, fb_y - 12, "той самий I", size=12, color=POS, bold=True))

    # вихід
    nodes.append(line(ox, out_pt[1], ox + 80, out_pt[1], color=INK))
    nodes.append(node(ox + 80, out_pt[1]))
    b, bw, bh = textbox(ox + 130, out_pt[1], "U = − I · Rf",
                        size=16, bold=True, fill="#eafaf0", stroke=FIELD, color="#0f5d33")
    nodes.append(b)

    nodes.append(text(W / 2, H - 18,
                      "Підсилювач тримає вузол при нулі → увесь струм джерела йде в Rf → на виході рівно −I·Rf",
                      size=12, color=MUTED))
    render(os.path.join(IMG, "idea.svg"), W, H, *nodes,
           title="Струм у віртуальну землю стає напругою на Rf")


# ── 2) Чому не просто резистор ───────────────────────────────────────────────
def fig_resistor_vs():
    W, H = 720, 320
    # ліворуч: голий резистор навантаження
    lx = 175
    top = 70
    out = [text(lx, 48, "Просто резистор", size=14, bold=True, color=INK)]
    out.append(photodiode(lx, top, r=12))
    out.append(line(lx, top + 12, lx, top + 50, color=INK))
    out.append(node(lx, top + 50))
    out.append(mtext(lx + 70, top + 44, ["U джерела", "гойдається"], size=12, color=POS))
    # резистор донизу до землі
    out.append(line(lx, top + 50, lx, top + 70, color=INK))
    # вертикальний R (через зигзаг повернутий — намалюю простими сегментами)
    ry0 = top + 70
    n = 6
    seg = 60 / n
    pts = []
    for i in range(n + 1):
        yy = ry0 + i * seg
        xx = lx + (6 if i % 2 else -6) if 0 < i < n else lx
        pts.append("%.1f,%.1f" % (xx, yy))
    out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6"/>'
               % (" ".join(pts), INK))
    out.append(text(lx + 22, ry0 + 30, "R", size=13, color=INK, bold=True))
    out.append(line(lx, ry0 + 60, lx, ry0 + 72, color=INK))
    out.append(gnd(lx, ry0 + 72))
    out.append(mtext(lx, H - 56, ["U = I·R, але напруга вузла",
                                  "змінює зворотну напругу діода:",
                                  "ємність гуляє, лінійність гірша"],
                     size=11, color=MUTED))

    # праворуч: TIA
    rx = 500
    cy = 150
    out.append(text(rx, 48, "Трансімпедансний підсилювач", size=14, bold=True, color=INK))
    body, in_top, in_bot, out_pt = opamp(rx, cy, plus_top=False)
    out.append(body)
    out.append(line(in_bot[0], in_bot[1], in_bot[0] - 34, in_bot[1], color=INK))
    out.append(gnd(in_bot[0] - 34, in_bot[1]))
    nx, ny = in_top[0] - 58, in_top[1]
    out.append(line(in_top[0], in_top[1], nx, ny, color=INK))
    out.append(node(nx, ny))
    out.append(text(nx - 4, ny - 12, "U ≈ 0", size=12, color=FIELD, bold=True))
    # фотодіод зверху
    out.append(photodiode(nx, ny - 70, r=12))
    out.append(line(nx, ny - 58, nx, ny, color=INK))
    out.append(arrow(nx, ny - 44, nx, ny - 22, color=POS, sw=2))
    out.append(text(nx + 14, ny - 34, "I", size=14, color=POS, bold=True))
    # Rf
    fb_y = cy - 66
    out.append(line(out_pt[0], out_pt[1], out_pt[0] + 18, out_pt[1], color=INK))
    ox = out_pt[0] + 18
    out.append(line(ox, out_pt[1], ox, fb_y, color=INK))
    out.append(res_h(nx, ox, fb_y, label="Rf"))
    out.append(line(nx, fb_y, nx, ny, color=INK))
    out.append(line(ox, out_pt[1], ox + 60, out_pt[1], color=INK))
    out.append(node(ox + 60, out_pt[1]))
    out.append(text(ox + 60, out_pt[1] + 22, "U = −I·Rf", size=13, color="#0f5d33", bold=True))
    out.append(mtext(rx - 30, H - 56, ["Вузол прибитий до нуля петлею:",
                                       "діод бачить сталу напругу,",
                                       "уся ємність невидима, лінійно"],
                     size=11, color=MUTED))

    # роздільна риса
    out.append(line(335, 60, 335, H - 60, color="#d0d4da", sw=1.2, dash="5,5"))
    render(os.path.join(IMG, "resistor-vs.svg"), W, H, *out,
           title="Резистор гойдає вузол; TIA тримає вузол нерухомо")


# ── 3) Вхідна ємність задирає шум; Cf лікує ─────────────────────────────────
def fig_cf_cure():
    W, H = 750, 360
    # осі: частота (лог) →, коефіцієнт підсилення шуму ↑
    ax_l, ax_r = 90, 660
    ax_b, ax_t = 300, 70
    out = [line(ax_l, ax_b, ax_r, ax_b, color=INK, sw=1.6),
           line(ax_l, ax_b, ax_l, ax_t, color=INK, sw=1.6),
           text(ax_r, ax_b + 24, "частота (лог)", size=12, color=MUTED, anchor="end"),
           text(ax_l - 8, ax_t - 6, "шумовий коефіцієнт", size=12, color=MUTED, anchor="start")]

    base = ax_b - 30   # рівень +1 (постійна складова)
    out.append(line(ax_l, base, ax_r, base, color="#c8ccd2", sw=1, dash="4,4"))
    out.append(text(ax_l + 4, base - 6, "×1", size=11, color=MUTED, anchor="start"))

    # крива БЕЗ Cf: рівна, тоді росте (нуль від Cin·Rf), гострий пік, обрив
    fz = ax_l + 250   # частота зламу Cin
    peak_x = ax_l + 430
    peak_y = ax_t + 18
    out.append(('<path d="M %d %d L %d %d Q %d %d %d %d L %d %d" '
                'fill="none" stroke="%s" stroke-width="2.4"/>'
                % (ax_l, base, fz, base, peak_x - 70, base, peak_x, peak_y,
                   ax_r - 20, base + 40, POS)))
    out.append(mtext(peak_x + 6, peak_y - 4, ["пік шуму +", "дзвін / генерація"], size=12,
                     color=POS, bold=True, anchor="start"))
    out.append(text(fz, base + 18, "тут вмикається Cin·Rf", size=11, color=POS, anchor="middle"))
    out.append(line(fz, base, fz, ax_t + 30, color=POS, sw=1, dash="3,3"))

    # крива З Cf: росте так само, тоді нуль Cf зрізає й тримає полицю
    flat_y = base - 70
    out.append(('<path d="M %d %d L %d %d Q %d %d %d %d L %d %d" '
                'fill="none" stroke="%s" stroke-width="2.4"/>'
                % (ax_l, base, fz, base, fz + 60, base, fz + 110, flat_y,
                   ax_r, flat_y, FIELD)))
    out.append(text(ax_r, flat_y - 8, "з Cf: рівна полиця", size=12,
                    color="#0f5d33", bold=True, anchor="end"))

    # підпис унизу
    out.append(text(W / 2, H - 24,
                    "Ємність на вході (Cin) задирає коефіцієнт, на який множиться власний шум ОП. "
                    "Конденсатор Cf додає нуль, що зрізає підйом і прибирає пік.",
                    size=11, color=MUTED))
    render(os.path.join(IMG, "cf-cure.svg"), W, H, *out,
           title="Вхідна ємність задирає шум; Cf зрізає пік")


# ── 4) Компроміс Cf ↔ смуга ─────────────────────────────────────────────────
def fig_bandwidth():
    W, H = 720, 320
    ax_l, ax_r = 90, 640
    ax_b, ax_t = 250, 70
    out = [line(ax_l, ax_b, ax_r, ax_b, color=INK, sw=1.6),
           line(ax_l, ax_b, ax_l, ax_t, color=INK, sw=1.6),
           text(ax_r, ax_b + 24, "частота (лог)", size=12, color=MUTED, anchor="end"),
           text(ax_l - 8, ax_t - 6, "підсилення тракту", size=12, color=MUTED, anchor="start")]

    flat = ax_t + 40   # полиця підсилення Rf
    out.append(line(ax_l, flat, ax_r - 10, flat, color="#c8ccd2", sw=1, dash="4,4"))
    out.append(text(ax_l + 4, flat - 6, "Rf", size=11, color=MUTED, anchor="start"))

    # три криві з різними Cf: різні точки злому 1/(2π·Rf·Cf)
    cols = [("малий Cf", POS, ax_l + 360),
            ("середній Cf", INK, ax_l + 250),
            ("великий Cf", FIELD, ax_l + 150)]
    for label, col, fc in cols:
        # полиця до fc, тоді спад -20 дБ/дек
        drop_y = ax_b - 10
        out.append(('<path d="M %d %d L %d %d L %d %d" fill="none" '
                    'stroke="%s" stroke-width="2.2"/>'
                    % (ax_l, flat, fc, flat, fc + 130, drop_y, col)))
        out.append(line(fc, flat, fc, ax_b, color=col, sw=1, dash="3,3"))
        out.append(text(fc, ax_b + 16, label, size=11, color=col, anchor="middle"))

    out.append(text(ax_r, flat + 26, "смуга = 1 / (2π·Rf·Cf)", size=13,
                    color="#0f5d33", bold=True, anchor="end"))
    out.append(text(W / 2, H - 18,
                    "Більший Cf → стабільніше й тихіше, але точка зламу нижча: смуга вужча. "
                    "Cf обирають найменшим, що ще гасить дзвін.",
                    size=11, color=MUTED))
    render(os.path.join(IMG, "bandwidth.svg"), W, H, *out,
           title="Cf проти смуги: чим більший Cf, тим вужча смуга")


# ── Помічник для Bode-полів вставки про стійкість ────────────────────────────
def _axes(f, ox, oy, axw, axh, ylab):
    """Осі Bode: X — частота (лог), Y — підсилення в дБ. Додає підписи осей."""
    f.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.8))       # вісь частоти
    f.append(arrow(ox, oy, ox, oy - axh, color=INK, sw=1.8))       # вісь дБ
    f.append(text(ox + axw - 4, oy + 24, "частота (лог)", size=12, color=MUTED, anchor="end"))
    f.append(text(ox - 6, oy - axh + 10, ylab, size=12, color=INK, bold=True, anchor="start"))


def _vmark(f, x, oy, ytop, label, color, dy=18):
    """Вертикальна пунктирна позначка частоти зламу з підписом під віссю."""
    f.append(line(x, oy, x, ytop, color=color, sw=1.2, dash="4 4"))
    f.append(text(x, oy + dy, label, size=12, color=color, anchor="middle", bold=True))


# ════════════════════════════════════════════════════════════════════════════
# 5. beta-zero.svg — β падає з fz; обернена 1/β (шумовий коефіцієнт) лізе вгору.
#    Дзеркало відносно рівня ×1 (0 дБ): полюс β = нуль 1/β на одній частоті fz.
# ════════════════════════════════════════════════════════════════════════════
def fig_beta_zero():
    W, H = 720, 410
    f = []
    ox, oy = 96, 296
    axw, axh = 556, 246
    _axes(f, ox, oy, axw, axh, "дБ")

    y1 = oy - 118                 # рівень ×1 (0 дБ) — вісь дзеркала
    f.append(line(ox, y1, ox + axw, y1, color="#c8ccd2", sw=1.2, dash="5 5"))
    f.append(text(ox + axw - 4, y1 - 8, "×1  (0 дБ)", size=12, color=MUTED, anchor="end"))

    fz = ox + 232                 # частота зламу 1/(2π·Rf·Cin)
    end = ox + axw - 40           # кінець кривих (лишаємо місце під підпис праворуч)
    slope = 108                   # підйом/спад на праву частину поля

    # 1/β — шумовий коефіцієнт: рівна полиця, тоді вгору +20 дБ/дек від fz
    f.append(line(ox + 4, y1, fz, y1, color=POS, sw=2.8))
    f.append(line(fz, y1, end, y1 - slope, color=POS, sw=2.8))
    f.append(text(end + 8, y1 - slope + 4, "1/β", size=15, color=POS, bold=True, anchor="start"))
    f.append(text(fz + 104, y1 - 54, "+20 дБ/дек", size=12, color=POS, anchor="middle", italic=True))

    # β — коефіцієнт зв'язку: рівна полиця, тоді вниз −20 дБ/дек від fz (дзеркало)
    f.append(line(ox + 4, y1, fz, y1, color=NEG, sw=2.8))
    f.append(line(fz, y1, end, y1 + slope, color=NEG, sw=2.8))
    f.append(text(end + 8, y1 + slope + 4, "β", size=15, color=NEG, bold=True, anchor="start"))
    f.append(text(fz + 104, y1 + 54, "−20 дБ/дек", size=12, color=NEG, anchor="middle", italic=True))

    # позначка частоти зламу
    _vmark(f, fz, oy, y1 + slope, "fz = 1/(2π·Rf·Cin)", INK)
    f.append(circle(fz, y1, 4.5, fill="#ffffff", stroke=INK, sw=2.2))

    b, w0, h0 = textbox(W / 2, H - 30,
                        "Подільник Rf–Cin: з частоти fz коефіцієнт β котиться вниз,\n"
                        "а обернена 1/β — вгору. Підйом 1/β — корінь нестійкості TIA.",
                        size=11, color=INK, fill="#f4f6f8", stroke=INK)
    f.append(b)

    render(os.path.join(IMG, "beta-zero.svg"), W, H, *f,
           title="Нуль шумового коефіцієнта від вхідної ємності")


# ════════════════════════════════════════════════════════════════════════════
# 6. closure.svg — |A| і 1/β на одному полі. |A| спадає −20 дБ/дек від ≈120 дБ;
#    1/β рівна на 0 дБ, з fz росте +20 дБ/дек. Без Cf вони сходяться під
#    40 дБ/дек → −90° (спад ОП) + −90° (нуль Cin) = −180°, запас фази 0.
# ════════════════════════════════════════════════════════════════════════════
def fig_closure():
    W, H = 780, 440
    f = []
    ox, oy = 100, 316
    axw, axh = 620, 262
    _axes(f, ox, oy, axw, axh, "підсилення, дБ")

    y0db = oy - 44                # рівень 0 дБ = полиця 1/β резистивного TIA
    ytop = oy - axh + 24          # рівень ≈120 дБ (старт |A|)
    f.append(line(ox, y0db, ox + axw, y0db, color="#c8ccd2", sw=1.2, dash="5 5"))
    f.append(text(ox + 6, y0db - 7, "0 дБ  (×1)", size=11, color=MUTED, anchor="start"))

    fz = ox + 240                 # нуль 1/β від Cin
    fc = ox + 396                 # частота перетину f_c
    end = ox + axw - 22

    # 1/β — рівна полиця на 0 дБ, з fz росте +20 дБ/дек, крізь перетин
    slope = 22.0 / 60.0           # px вгору на px управо (нахил лінії 1/β)
    yc = y0db - slope * (fc - fz)                       # рівень 1/β у точці перетину
    y_ib_end = y0db - slope * (end - fz)
    f.append(line(ox + 4, y0db, fz, y0db, color=POS, sw=2.8))
    f.append(line(fz, y0db, end, y_ib_end, color=POS, sw=2.8))
    b, w0, h0 = textbox(end - 4, y_ib_end - 20, "1/β", size=15, color=POS,
                        bold=True, fill="#fdecea", stroke=POS)
    f.append(b)
    f.append(text(fz + 96, y0db - slope * 96 - 12, "+20 дБ/дек", size=11,
                  color=POS, anchor="middle", italic=True))

    # |A| — підсилення ОП: від ≈120 дБ спад −20 дБ/дек крізь ту саму точку перетину
    drop = 40.0 / 60.0            # крутіший видимий нахил |A| (щоб не злитися з 1/β)
    y_a_start = yc - drop * (fc - ox - 4)               # старт зліва, щоб пройти через (fc, yc)
    if y_a_start < ytop:                               # не вилазити за верх поля
        y_a_start = ytop
    x_a_start = fc - (yc - y_a_start) / drop
    y_a_end = yc + drop * (end - fc)
    if y_a_end > oy - 6:                               # не вилазити під вісь
        x_a_end = fc + (oy - 6 - yc) / drop
        y_a_end = oy - 6
    else:
        x_a_end = end
    f.append(line(x_a_start, y_a_start, x_a_end, y_a_end, color=NEG, sw=2.8))
    f.append(text(x_a_start + 6, y_a_start - 8, "|A|  (підсилення ОП)", size=12,
                  color=NEG, anchor="start", bold=True))
    f.append(text(x_a_start + 70, y_a_start + 46, "−20 дБ/дек", size=11,
                  color=NEG, anchor="middle", italic=True))

    # позначки частот зламу
    _vmark(f, fz, oy, y0db, "fz = 1/(2π·Rf·Cin)", MUTED)

    # точка перетину — критична
    f.append(circle(fc, yc, 5.5, fill="#ffffff", stroke=INK, sw=2.6))
    f.append(line(fc, yc, fc, oy, color=INK, sw=1.2, dash="4 4"))
    f.append(text(fc, oy + 18, "перетин f_c: |A| = 1/β  (|T| = 1)", size=12,
                  color=INK, anchor="middle", bold=True))

    # рамка-висновок про складання фаз
    b, w0, h0 = textbox(fc + 168, ytop + 74,
                        "сходяться під 40 дБ/дек:\n−90° спад ОП\n−90° нуль 1/β (Cin)\n= −180°\nзапас фази = 0",
                        size=12, color=POS, fill="#fdecea", stroke=POS, sw=2, min_w=196)
    f.append(b)

    render(os.path.join(IMG, "closure.svg"), W, H, *f,
           title="Перетин |A| і 1/β без Cf: два −90° дають −180°")


# ════════════════════════════════════════════════════════════════════════════
# 7. cf-compensation.svg — Cf додає в 1/β полюс fp=1/(2π·Rf·Cf): підйом від fz
#    зрізано в полицю на рівні (Cin+Cf)/Cf; |A| перетинає полицю під 20 дБ/дек.
#    Випередження +90° полюса гасить −90° нуля → у перетині лишається −90° ОП.
# ════════════════════════════════════════════════════════════════════════════
def fig_cf_compensation():
    W, H = 780, 440
    f = []
    ox, oy = 100, 316
    axw, axh = 620, 262
    _axes(f, ox, oy, axw, axh, "підсилення, дБ")

    y0db = oy - 44
    ytop = oy - axh + 24
    f.append(line(ox, y0db, ox + axw, y0db, color="#c8ccd2", sw=1.2, dash="5 5"))
    f.append(text(ox + 6, y0db - 7, "0 дБ  (×1)", size=11, color=MUTED, anchor="start"))

    fz = ox + 210                 # нуль 1/β від Cin
    fp = ox + 330                 # полюс 1/β від Cf (злам у полицю)
    end = ox + axw - 22

    slope = 22.0 / 60.0
    y_shelf = y0db - slope * (fp - fz)                  # рівень полиці (Cin+Cf)/Cf

    # 1/β з Cf: полиця 0 дБ → підйом від fz → полиця від fp
    f.append(line(ox + 4, y0db, fz, y0db, color=POS, sw=2.8))
    f.append(line(fz, y0db, fp, y_shelf, color=POS, sw=2.8))
    f.append(line(fp, y_shelf, end, y_shelf, color=POS, sw=2.8))
    b, w0, h0 = textbox(end - 4, y_shelf - 20, "1/β", size=15, color=POS,
                        bold=True, fill="#fdecea", stroke=POS)
    f.append(b)
    f.append(text((fz + fp) / 2 + 10, (y0db + y_shelf) / 2 - 26, "нуль fz",
                  size=11, color=POS, anchor="middle", italic=True))
    f.append(text(end - 96, y_shelf + 18, "полиця (Cin+Cf)/Cf", size=11,
                  color="#0f5d33", anchor="middle", italic=True))

    # |A| — спад −20 дБ/дек, перетинає ПОЛИЦЮ 1/β під 20 дБ/дек (похило)
    fc = fp + 150                 # перетин лежить на полиці, правіше fp
    drop = 40.0 / 60.0
    y_a_start = y_shelf - drop * (fc - ox - 4)
    if y_a_start < ytop:
        y_a_start = ytop
    x_a_start = fc - (y_shelf - y_a_start) / drop
    if fc > end:                                       # тримати перетин у полі
        fc = end - 6
    y_a_end = y_shelf + drop * (end - fc)
    if y_a_end > oy - 6:
        x_a_end = fc + (oy - 6 - y_shelf) / drop
        y_a_end = oy - 6
    else:
        x_a_end = end
    f.append(line(x_a_start, y_a_start, x_a_end, y_a_end, color=NEG, sw=2.8))
    f.append(text(x_a_start + 6, y_a_start - 8, "|A|  (підсилення ОП)", size=12,
                  color=NEG, anchor="start", bold=True))

    # позначки fz та fp
    _vmark(f, fz, oy, y0db, "fz", MUTED)
    _vmark(f, fp, oy, y_shelf, "fp = 1/(2π·Rf·Cf)", INK)
    f.append(circle(fp, y_shelf, 4.5, fill="#ffffff", stroke=INK, sw=2.2))

    # точка перетину на полиці
    f.append(circle(fc, y_shelf, 5.5, fill="#ffffff", stroke=FIELD, sw=2.6))
    f.append(mtext(fc + 8, y_shelf + 20, ["перетин під", "20 дБ/дек"],
                   size=11, color="#0f5d33", anchor="start", bold=True))

    # рамка-висновок: полюс гасить нуль, запас повернуто
    b, w0, h0 = textbox(fp + 20, ytop + 66,
                        "полюс fp зрізає підйом:\n+90° полюса гасить\n−90° нуля →\nу перетині лишається\n−90° ОП, запас 45–64°",
                        size=12, color="#0f5d33", fill="#eafaf0", stroke=FIELD, sw=2, min_w=206)
    f.append(b)

    render(os.path.join(IMG, "cf-compensation.svg"), W, H, *f,
           title="Cf ставить полюс у 1/β: перетин під 20 дБ/дек, запас повернуто")


if __name__ == "__main__":
    fig_idea()
    fig_resistor_vs()
    fig_cf_cure()
    fig_bandwidth()
    fig_beta_zero()
    fig_closure()
    fig_cf_compensation()
    print("ok:", os.listdir(IMG))

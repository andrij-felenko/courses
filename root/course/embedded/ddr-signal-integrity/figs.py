# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── whats-hard: чому саме DDR — найважчий випадок цілісності сигналу ───────────
# Ідея: не один провідник, а широка ПАРАЛЕЛЬНА шина, що перемикається разом,
# двонапрямлена, з крутими фронтами й власним стробом замість спільного такту.
# Кожен пункт додає свою біду — звідси й арсенал прийомів.

def fig_whats_hard():
    W, H = 820, 360
    p = []
    cx = W / 2

    # центральний «вузол біди» — DDR-шина
    core, cw, ch = textbox(cx, 190, "DDR-шина", size=15, bold=True,
                           color=POS, fill="#fdecea", stroke=POS, sw=2.4, pad=16)

    # чотири біди довкола — кожна тягне свій прийом-протиотруту
    troubles = [
        (170,  95, "багато ліній разом\n(8·n біт DQ)", "стрибок землі,\nперехресна наводка", NEG, "#eef4ff"),
        (650,  95, "двонапрямлена\n(читання й запис)", "термінацію треба\nвмикати/вимикати", FIELD, "#eafaf0"),
        (170, 290, "крутий фронт\n(сотні пс)", "відбиття від кожного\nрозгалуження", POS, "#fdecea"),
        (650, 290, "строб іде з даними\n(DQS, без спільного такту)", "перекоси ліній\nз'їдають вікно", MUTED, "#efefef"),
    ]
    centers = []
    for tx, ty, head, body, col, fill in troubles:
        b, bw, bh = textbox(tx, ty, head, size=11, bold=True, color=col,
                            fill=fill, stroke=col, sw=1.8)
        p.append(b)
        p.append(mtext(tx, ty + bh / 2 + 16, body, size=9, color=MUTED))
        centers.append((tx, ty, bw, bh))

    # лінії від кожної біди до центру
    for tx, ty, bw, bh in centers:
        dx = cx - tx
        dy = 190 - ty
        d = math.hypot(dx, dy)
        x1 = tx + dx / d * (bw / 2 + 6)
        y1 = ty + dy / d * (bh / 2 + 6)
        x2 = cx - dx / d * (cw / 2 + 6)
        y2 = 190 - dy / d * (ch / 2 + 6)
        p.append(line(x1, y1, x2, y2, color="#c9ced6", sw=1.6))

    p.append(core)

    p.append(text(cx, H - 16, "одна шина — чотири біди разом; тому DDR несе цілий арсенал вбудованих прийомів",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "whats-hard.svg"), W, H, *p,
           title="Чому DDR — найважчий випадок цілісності сигналу")


# ── fly-by: подвійне-Т проти fly-by ───────────────────────────────────────────
# Ідея: у DDR2 адресу/команду вели Т-розгалуженнями — кожен відгалужок це куксa,
# що відбиває. DDR3 вишикував чипи в один ряд (fly-by) з короткими куксами й
# термінацією в кінці; ціна — сигнал доходить до чипів у різний час (перекіс).

def fig_flyby():
    W, H = 840, 380
    p = []

    def chip(cx, cy, lab):
        out = fitbox(cx - 26, cy - 16, 52, 32, lab, size=10, fill="#eef4ff",
                     stroke=NEG, sw=1.6, bold=True)
        return out

    # ── ліворуч: подвійне-Т (DDR2) ──
    lx = 70
    p.append(text(lx + 150, 64, "подвійне-Т (DDR2)", size=13, color=INK, bold=True))
    drv_y = 120
    p.append(fitbox(lx, drv_y - 18, 70, 36, "конт-\nролер", size=10, fill="#f6f4ec",
                    stroke=INK, sw=1.6, bold=True))
    # головна жила розгалужується надвоє, потім ще надвоє
    midx = lx + 130
    p.append(line(lx + 70, drv_y, midx, drv_y, color=INK, sw=2.0))
    # вузол гілкування 1
    p.append(circle(midx, drv_y, 4, fill=POS, stroke=POS, sw=1.5))
    for sy in (drv_y - 60, drv_y + 60):
        p.append(line(midx, drv_y, midx, sy, color=INK, sw=2.0))
        p.append(line(midx, sy, midx + 40, sy, color=INK, sw=2.0))
        p.append(circle(midx + 40, sy, 4, fill=POS, stroke=POS, sw=1.5))
        for ssy in (sy - 26, sy + 26):
            p.append(line(midx + 40, sy, midx + 40, ssy, color=INK, sw=1.8))
            p.append(line(midx + 40, ssy, midx + 70, ssy, color=INK, sw=1.8))
            p.append(chip(midx + 96, ssy, "DRAM"))
    # позначка кукс
    p.append(text(midx + 4, drv_y + 96, "кожен відгалужок — кукса:", size=9, color=POS, anchor="start"))
    p.append(text(midx + 4, drv_y + 110, "відбиває й глушить фронт", size=9, color=POS, anchor="start"))

    # роздільник
    p.append(line(W / 2, 80, W / 2, 320, color="#e4e8ee", sw=1.4))

    # ── праворуч: fly-by (DDR3+) ──
    rx = W / 2 + 40
    p.append(text(rx + 150, 64, "fly-by (DDR3 і далі)", size=13, color=INK, bold=True))
    fy = 150
    p.append(fitbox(rx, fy - 18, 70, 36, "конт-\nролер", size=10, fill="#f6f4ec",
                    stroke=INK, sw=1.6, bold=True))
    # одна жила проходить повз усі чипи в ряд і закінчується термінатором
    bus_x0 = rx + 70
    bus_x1 = rx + 290
    p.append(line(bus_x0, fy, bus_x1, fy, color=INK, sw=2.2))
    chip_xs = [bus_x0 + 50, bus_x0 + 110, bus_x0 + 170]
    for i, cxp in enumerate(chip_xs):
        p.append(line(cxp, fy, cxp, fy + 34, color=INK, sw=1.6))   # коротка кукса
        p.append(chip(cxp, fy + 58, "DRAM"))
        p.append(circle(cxp, fy, 3.5, fill=FIELD, stroke=FIELD, sw=1.2))
    # термінатор у кінці (до Vtt) — вниз від жили
    p.append(line(bus_x1, fy, bus_x1, fy - 18, color=INK, sw=2.0))
    p.append(fitbox(bus_x1 - 20, fy - 50, 40, 28, "Rt", size=11, fill="#eafaf0",
                    stroke=FIELD, sw=1.8, bold=True, color=FIELD))
    p.append(line(bus_x1, fy - 50, bus_x1, fy - 66, color=FIELD, sw=1.6))
    p.append(text(bus_x1, fy - 72, "Vtt", size=10, color=FIELD, anchor="middle", bold=True))
    # перекіс
    p.append(text(bus_x0 + 4, fy + 96, "короткі кукси, термінація в кінці —", size=9, color=FIELD, anchor="start"))
    p.append(text(bus_x0 + 4, fy + 110, "ціна: сигнал доходить до чипів", size=9, color=POS, anchor="start"))
    p.append(text(bus_x0 + 4, fy + 124, "у РІЗНИЙ час (перекіс → вирівнювання)", size=9, color=POS, anchor="start"))

    p.append(text(W / 2, H - 14, "Т-розгалуження міняють на один ряд: менше відбиттів ціною керованого перекосу",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "flyby.svg"), W, H, *p,
           title="Топологія адреси й команди: подвійне-Т проти fly-by")


# ── odt: термінація переїхала в чип і стала вмикною ────────────────────────────
# Ідея: замість резистора на платі біля кожного входу — резистор УСЕРЕДИНІ чипа,
# який контролер вмикає лише там, де треба зараз. Праворуч — як це відчиняє око.

def fig_odt():
    W, H = 820, 360
    p = []

    # ── ліва панель: де живе термінатор ──
    p.append(text(200, 64, "де живе термінатор", size=13, color=INK, bold=True))
    # було: резистор на платі
    p.append(fitbox(60, 100, 150, 38, "БУЛО: резистор\nна платі (Vtt-острів)", size=10,
                    fill="#fdecea", stroke=POS, sw=1.6, bold=True, color=POS))
    p.append(text(135, 156, "зайва площа, шлейф,", size=9, color=MUTED))
    p.append(text(135, 170, "фіксований опір", size=9, color=MUTED))
    p.append(arrow(135, 178, 135, 206, color=INK, sw=1.8))
    # стало: ODT усередині чипа
    p.append(fitbox(60, 206, 150, 38, "СТАЛО: ODT\nусередині кристала", size=10,
                    fill="#eafaf0", stroke=FIELD, sw=1.8, bold=True, color=FIELD))
    p.append(text(135, 262, "контролер вмикає лише", size=9, color=MUTED))
    p.append(text(135, 276, "там, де приймає зараз", size=9, color=MUTED))

    # роздільник
    p.append(line(W / 2, 80, W / 2, 300, color="#e4e8ee", sw=1.4))

    # ── права панель: око до й після термінації ──
    ox = W / 2 + 60
    p.append(text(ox + 110, 64, "як це відчиняє око", size=13, color=INK, bold=True))

    def eye(cx, cy, w, h, openness, col, lab):
        out = []
        # рамка-область
        out.append(rect(cx - w/2, cy - h/2, w, h, fill=BG, stroke="#e4e8ee", sw=1.0))
        # верхня й нижня «повіки» ока: ромб, тим вужчий що менша openness
        midx_l = cx - w/2
        midx_r = cx + w/2
        oy = h/2 * openness
        ox_ = w/2 * openness
        # верхня крива
        out.append('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="none" stroke="%s" stroke-width="2.2"/>'
                   % (midx_l, cy - h/2 + 4, cx, cy - oy, midx_r, cy - h/2 + 4, col))
        out.append('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="none" stroke="%s" stroke-width="2.2"/>'
                   % (midx_l, cy + h/2 - 4, cx, cy + oy, midx_r, cy + h/2 - 4, col))
        # позначка висоти ока (запас по напрузі)
        out.append(line(cx, cy - oy, cx, cy + oy, color=MUTED, sw=1.0, dash="3 3"))
        out.append(mtext(cx, cy + h/2 + 22, lab, size=10, color=col, bold=True))
        return out

    p += eye(ox + 70, 180, 130, 130, 0.16, POS, "без термінації:\nдзвін, око майже\nзачинене")
    p.append(arrow(ox + 150, 180, ox + 190, 180, color=INK, sw=1.8))
    p += eye(ox + 270, 180, 130, 130, 0.62, FIELD, "з ODT:\nдзвін гасне,\nоко відчинене")

    p.append(text(W / 2, H - 14, "термінатор переїхав у чип і вмикається на льоту; відкрите око — це запас на похибки",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "odt.svg"), W, H, *p,
           title="On-die termination: термінація всередині чипа, вмикна на льоту")


# ── eye-training: вікно даних і центрування строба ────────────────────────────
# Ідея: дані дійсні лише вузьке вікно; строб DQS треба поставити в його СЕРЕДИНУ.
# Тренування зсуває DQS (і підбирає поріг Vref), шукаючи найширше розплющення.

def fig_eye_training():
    W, H = 820, 380
    p = []

    # ── ліва панель: вікно даних і куди ставити строб ──
    lx, ly = 70, 230
    lw = 300
    p.append(text(lx + lw/2, 64, "вікно даних і строб", size=13, color=INK, bold=True))
    # часова вісь
    p.append(line(lx, ly, lx + lw, ly, color=INK, sw=1.6))
    p.append(text(lx + lw, ly + 16, "час", size=10, color=INK, italic=True))
    # перехідні зони (невизначеність) і дійсне вікно посередині
    valid_x0 = lx + 110
    valid_x1 = lx + 200
    p.append(rect(lx + 20, ly - 90, 90, 90, fill="#fdecea", stroke=POS, sw=1.0, rx=2))
    p.append(rect(valid_x1, ly - 90, 90, 90, fill="#fdecea", stroke=POS, sw=1.0, rx=2))
    p.append(rect(valid_x0, ly - 90, valid_x1 - valid_x0, 90, fill="#eafaf0", stroke=FIELD, sw=1.6, rx=2))
    p.append(text((valid_x0+valid_x1)/2, ly - 44, "дійсне", size=10, color=FIELD, bold=True))
    p.append(text((valid_x0+valid_x1)/2, ly - 30, "вікно", size=10, color=FIELD, bold=True))
    p.append(text(lx + 65, ly - 100, "перехід", size=9, color=POS))
    p.append(text(valid_x1 + 45, ly - 100, "перехід", size=9, color=POS))
    # строб у центрі вікна
    sx = (valid_x0 + valid_x1) / 2
    p.append(line(sx, ly - 105, sx, ly + 18, color=NEG, sw=2.2, dash="6 4"))
    p.append(text(sx, ly + 34, "DQS — у центр", size=10, color=NEG, bold=True))
    # запаси праворуч/ліворуч
    p.append(arrow(valid_x0 + 4, ly + 8, sx - 4, ly + 8, color=MUTED, sw=1.2))
    p.append(arrow(sx + 4, ly + 8, valid_x1 - 4, ly + 8, color=MUTED, sw=1.2))

    # роздільник
    p.append(line(W / 2, 80, W / 2, 320, color="#e4e8ee", sw=1.4))

    # ── права панель: 2D-око тренування (зсув DQS × поріг Vref) ──
    ox, oy = W/2 + 60, 220
    ax, ay = ox, oy + 90
    aw, ah = 250, 190
    p.append(text(ox + aw/2, 64, "що шукає тренування", size=13, color=INK, bold=True))
    p.append(line(ax, ay, ax + aw, ay, color=INK, sw=1.6))      # вісь X: зсув DQS
    p.append(line(ax, ay, ax, ay - ah, color=INK, sw=1.6))      # вісь Y: поріг Vref
    p.append(text(ax + aw, ay + 16, "зсув DQS →", size=10, color=INK, italic=True))
    p.append(text(ax - 6, ay - ah + 4, "поріг Vref", size=9, color=MUTED, anchor="end"))
    # «око» як еліпс надійних точок
    ecx, ecy = ax + aw*0.5, ay - ah*0.5
    p.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="#eafaf0" stroke="%s" stroke-width="2.0"/>'
             % (ecx, ecy, aw*0.30, ah*0.32, FIELD))
    p.append(text(ecx, ecy - 4, "надійно", size=10, color=FIELD, bold=True))
    p.append(text(ecx, ecy + 12, "читається", size=10, color=FIELD, bold=True))
    # ціль — центр ока
    p.append(line(ecx - 9, ecy, ecx + 9, ecy, color=NEG, sw=1.8))
    p.append(line(ecx, ecy - 9, ecx, ecy + 9, color=NEG, sw=1.8))
    p.append(circle(ecx, ecy, 12, fill="none", stroke=NEG, sw=1.6))
    # межі — за оком помилки
    p.append(text(ax + aw*0.12, ay - ah*0.88, "тут — помилки", size=9, color=POS))

    p.append(text(W / 2, H - 14, "контролер сам зсуває строб і підбирає поріг, шукаючи центр найширшого ока",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "eye-training.svg"), W, H, *p,
           title="Тренування: поставити строб у центр вікна даних")


if __name__ == "__main__":
    fig_whats_hard()
    fig_flyby()
    fig_odt()
    fig_eye_training()
    print("OK: figures written to", OUT)

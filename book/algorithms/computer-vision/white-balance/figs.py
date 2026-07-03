# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── white-balance-idea: перекошені канали під теплим світлом → пер-канальний
#    коефіцієнт множить R/G/B нарізно → нейтраль повертається ─────────────────
# Ідея: біла стіна під лампою дає не рівні R=G=B, а R>G>B (синього мало).
# Множимо кожен канал на свій gain так, щоб знову R=G=B — колір «випрямляється».

def _bars(x, base, vals, bw, gap, labels, cols):
    """три стовпчики висотою vals[i], підписані labels[i]."""
    out = []
    for i, v in enumerate(vals):
        bx = x + i * (bw + gap)
        out.append(rect(bx, base - v, bw, v, fill=cols[i], stroke=INK, sw=1.0, rx=2))
        out.append(text(bx + bw / 2, base + 16, labels[i], size=12, color=INK, bold=True))
        out.append(text(bx + bw / 2, base - v - 6, str(int(v / 1.4)), size=11, color=MUTED))
    return out


def fig_white_balance_idea():
    W, H = 860, 430
    p = []
    p.append(text(W / 2, 26, "Баланс білого = помножити кожен канал на свій коефіцієнт",
                  size=15, bold=True))

    RC, GC, BC = "#d64545", "#3aa856", "#3b6fd6"
    scale = 1.4                       # px на одиницю значення
    base = 330
    bw, gap = 30, 14

    # ── ліва панель: сира біла стіна під теплим світлом (перекіс) ──
    lx = 55
    lvals = [210 * scale, 150 * scale, 78 * scale]  # R=210, G=150, B=78 (синього мало)
    p.append(rect(lx - 12, 60, 210, 20, fill="#fff4e0", stroke="#e0a94f", sw=1.2, rx=6))
    p.append(text(lx + 93, 74, "тепла лампа (жовтувата)", size=11, color="#a9761f", bold=True))
    p.append(text(lx + 93, 98, "сира біла стіна", size=12, bold=True))
    p.append(text(lx + 93, 114, "R > G > B  →  жовтий відлив", size=10, color=MUTED))
    p.extend(_bars(lx, base, lvals, bw, gap, ["R", "G", "B"], [RC, GC, BC]))
    # зразок кольору (жовтуватий)
    p.append(rect(lx + 150, base - 70, 44, 44, fill="#f0d27a", stroke=INK, sw=1.2, rx=6))
    p.append(text(lx + 172, base + 16, "видно", size=10, color=MUTED))

    # ── коефіцієнти між панелями ──
    mx = 355
    p.append(text(mx + 40, 150, "×gain", size=13, bold=True, color=POS))
    p.append(text(mx + 40, 172, "g_R=1.00", size=11, color=RC))
    p.append(text(mx + 40, 188, "g_G=1.40", size=11, color=GC))
    p.append(text(mx + 40, 204, "g_B=2.69", size=11, color=BC))
    p.append(arrow(mx, 250, mx + 82, 250, color=POS, sw=2.2))
    p.append(text(mx + 40, 240, "рівняємо до G", size=10, color=MUTED))

    # ── права панель: після балансу (рівні канали) ──
    rx = 500
    g = 210 * scale                    # усі до рівня R (найбільшого) — нейтраль
    rvals = [g, g, g]
    p.append(rect(rx - 12, 60, 210, 20, fill="#eef6ff", stroke="#8ab4e8", sw=1.2, rx=6))
    p.append(text(rx + 93, 74, "уявне нейтральне світло", size=11, color=NEG, bold=True))
    p.append(text(rx + 93, 98, "після балансу білого", size=12, bold=True))
    p.append(text(rx + 93, 114, "R = G = B  →  чисто біле", size=10, color=MUTED))
    p.extend(_bars(rx, base, rvals, bw, gap, ["R", "G", "B"], [RC, GC, BC]))
    p.append(rect(rx + 150, base - 70, 44, 44, fill="#f2f2f2", stroke=INK, sw=1.2, rx=6))
    p.append(text(rx + 172, base + 16, "стало", size=10, color=MUTED))

    # підсумок
    box = fitbox(55, 358, 750, 52,
                 "Ключ: сіре/біле має давати рівні R=G=B. Світло перекошує канали — множимо кожен на свій "
                 "коефіцієнт, щоб нейтраль знову стала нейтральною. Це і є весь баланс білого.",
                 size=11, pad=12, fill="#f0f9f4", stroke=FIELD, sw=1.5)
    p.append(box)

    render(os.path.join(OUT, "white-balance-idea.svg"), W, H, *p)


# ── two-estimators: gray-world (середнє→сіре) vs white-patch (найяскравіше→біле)
#    — що кожен припускає і де ламається ───────────────────────────────────────

def fig_two_estimators():
    W, H = 860, 470
    p = []
    p.append(text(W / 2, 26, "Звідки взяти коефіцієнти: дві прості здогадки", size=15, bold=True))

    RC, GC, BC = "#d64545", "#3aa856", "#3b6fd6"

    # ── ліва половина: gray-world ──
    lx, lw = 40, 380
    p.append(rect(lx, 50, lw, 380, fill="#fbfbfd", stroke=MUTED, sw=1.2, rx=10))
    p.append(text(lx + lw / 2, 74, "Сірий світ (gray-world)", size=13, bold=True))
    p.append(text(lx + lw / 2, 92, "припущення: середній колір сцени — сірий", size=10, color=MUTED))

    # маленька «сцена» з різнокольорових плям
    sx, sy, sw2, sh = lx + 30, 108, 150, 110
    p.append(rect(sx, sy, sw2, sh, fill="#eef2f7", stroke=INK, sw=1.2, rx=6))
    blobs = [("#c98", 25, 22), ("#7a9", 70, 30), ("#89b", 110, 24),
             ("#caa46a", 45, 70), ("#6b8fb0", 100, 74)]
    for col, dx, dy in blobs:
        p.append(circle(sx + dx, sy + dy, 15, fill=col, stroke="none", sw=0))
    p.append(text(sx + sw2 / 2, sy + sh + 15, "усе множимо, ділимо на N", size=9, color=MUTED))

    # стрілка → середнє
    p.append(arrow(sx + sw2 + 8, sy + sh / 2, sx + sw2 + 46, sy + sh / 2, color=INK, sw=1.8))
    ax = sx + sw2 + 60
    p.append(text(ax + 30, sy + 8, "середнє каналів", size=10, bold=True))
    avals = [64, 92, 118]
    ab = sy + 96
    for i, v in enumerate([64, 92, 118]):
        bx = ax + 6 + i * 30
        p.append(rect(bx, ab - v * 0.7, 22, v * 0.7, fill=[RC, GC, BC][i], stroke=INK, sw=0.8, rx=2))
        p.append(text(bx + 11, ab + 13, "RGB"[i], size=10, bold=True))
    p.append(text(ax + 45, ab + 30, "g = avgG / avg_канал", size=10, color=POS, bold=True))

    # де ламається
    box1 = fitbox(lx + 20, 300, lw - 40, 116,
                  "Дешево, один прохід. Але хибиться, коли сцена НЕ сіра в середньому: "
                  "велике червоне тло, зелене поле, синє небо на весь кадр — воно вважає "
                  "той колір «перекосом світла» й вибілює його в сіре. Мало кольорів — теж хиба.",
                  size=10, pad=12, fill="#fdf3f0", stroke=POS, sw=1.3)
    p.append(box1)

    # ── права половина: white-patch ──
    rx0, rw = 440, 380
    p.append(rect(rx0, 50, rw, 380, fill="#fbfbfd", stroke=MUTED, sw=1.2, rx=10))
    p.append(text(rx0 + rw / 2, 74, "Біла пляма (white-patch)", size=13, bold=True))
    p.append(text(rx0 + rw / 2, 92, "припущення: найяскравіше в кадрі — біле", size=10, color=MUTED))

    sx2, sy2 = rx0 + 30, 108
    p.append(rect(sx2, sy2, sw2, sh, fill="#eef2f7", stroke=INK, sw=1.2, rx=6))
    for col, dx, dy in blobs:
        p.append(circle(sx2 + dx, sy2 + dy, 15, fill=col, stroke="none", sw=0))
    # яскрава пляма-відблиск
    p.append(circle(sx2 + 128, sy2 + 20, 12, fill="#fbfbf5", stroke=POS, sw=2))
    p.append(text(sx2 + sw2 / 2, sy2 + sh + 15, "беремо верхній 1% яскравих", size=9, color=MUTED))

    p.append(arrow(sx2 + sw2 + 8, sy2 + sh / 2, sx2 + sw2 + 46, sy2 + sh / 2, color=INK, sw=1.8))
    ax2 = sx2 + sw2 + 60
    p.append(text(ax2 + 30, sy2 + 8, "макс кожного каналу", size=10, bold=True))
    ab2 = sy2 + 96
    for i, v in enumerate([248, 232, 150]):
        bx = ax2 + 6 + i * 30
        p.append(rect(bx, ab2 - v * 0.33, 22, v * 0.33, fill=[RC, GC, BC][i], stroke=INK, sw=0.8, rx=2))
        p.append(text(bx + 11, ab2 + 13, "RGB"[i], size=10, bold=True))
    p.append(text(ax2 + 45, ab2 + 30, "g = 255 / max_канал", size=10, color=POS, bold=True))

    box2 = fitbox(rx0 + 20, 300, rw - 40, 116,
                  "Теж дешево. Але тримається на ОДНОМУ найяскравішому пікселі: "
                  "пересвіт, відблиск від металу, кольоровий ліхтар у кадрі — і оцінку зносить. "
                  "Тому беруть не пік, а перцентиль (верхній ~1%), щоб не ловити випадковий блиск.",
                  size=10, pad=12, fill="#fdf3f0", stroke=POS, sw=1.3)
    p.append(box2)

    render(os.path.join(OUT, "two-estimators.svg"), W, H, *p)


# ── color-temperature: перевернута шкала — низькі K теплі (жовті), високі холодні
#    (сині); і куди балансує корекція ──────────────────────────────────────────

def fig_color_temperature():
    W, H = 820, 300
    p = []
    p.append(text(W / 2, 26, "Колірна температура: шкала перевернута", size=15, bold=True))
    p.append(text(W / 2, 46, "нижчі кельвіни — тепле світло, вищі — холодне (усупереч чуттю)",
                  size=11, color=MUTED))

    bx, by, bw, bh = 60, 90, 700, 40
    # градієнт-стрічка жовтий→білий→синій, намальована смугами
    stops = [(0.00, "#f0a020"), (0.18, "#f4c060"), (0.38, "#f6e0a8"),
             (0.52, "#fbfbf2"), (0.66, "#dfe9f6"), (0.82, "#b8cdec"), (1.00, "#8fb0e0")]
    nseg = 60
    def lerp(a, b, t):
        return int(a + (b - a) * t)
    def hexcol(t):
        for k in range(len(stops) - 1):
            t0, c0 = stops[k]; t1, c1 = stops[k + 1]
            if t0 <= t <= t1:
                f = (t - t0) / (t1 - t0)
                r0, g0, b0 = int(c0[1:3], 16), int(c0[3:5], 16), int(c0[5:7], 16)
                r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
                return "#%02x%02x%02x" % (lerp(r0, r1, f), lerp(g0, g1, f), lerp(b0, b1, f))
        return "#ffffff"
    for i in range(nseg):
        t = i / float(nseg - 1)
        p.append(rect(bx + t * (bw - bw / nseg), by, bw / nseg + 0.6, bh,
                      fill=hexcol(t), stroke="none", sw=0, rx=0))
    p.append(rect(bx, by, bw, bh, fill="none", stroke=INK, sw=1.4, rx=4))

    # мітки шкали
    ticks = [(0.06, "2000 K", "свічка"), (0.20, "3000 K", "лампа розжарення"),
             (0.44, "4000 K", "нейтраль"), (0.60, "5500 K", "денне"),
             (0.80, "6500 K", "хмарне небо"), (0.96, "9000 K", "тінь / блакить")]
    for t, k, name in ticks:
        x = bx + t * bw
        p.append(line(x, by + bh, x, by + bh + 8, color=INK, sw=1.2))
        p.append(text(x, by + bh + 24, k, size=11, bold=True))
        p.append(text(x, by + bh + 40, name, size=9, color=MUTED))

    # підписи «тепле»/«холодне»
    p.append(text(bx + 30, by - 10, "тепле", size=12, bold=True, color="#c07818", anchor="start"))
    p.append(text(bx + bw - 30, by - 10, "холодне", size=12, bold=True, color=NEG, anchor="end"))

    # думка знизу
    box = fitbox(60, 215, 700, 62,
                 "Камера під теплим світлом бачить жовтий кадр — щоб «охолодити» його до нейтралі, вона "
                 "ПІДСИЛЮЄ синій і гасить червоний (рух ліворуч по шкалі корекції). Під синім світлом — навпаки. "
                 "Одне число (температура) плюс зсув тінт задають обидва коефіцієнти.",
                 size=11, pad=12, fill="#eef6ff", stroke=NEG, sw=1.4)
    p.append(box)

    render(os.path.join(OUT, "color-temperature.svg"), W, H, *p)


# ── awb-percentile: чому верхній 1% гістограми, а не голий максимум ──────────
#    Гістограма каналу: один сміттєвий піксель задає max далеко праворуч;
#    поріг 99-го перцентиля стоїть на масі реальних яскравих пікселів.

def fig_awb_percentile():
    W, H = 860, 400
    p = []
    p.append(text(W / 2, 26, "Перцентиль замість максимуму: один блиск не має вирішувати",
                  size=15, bold=True))

    # осі гістограми
    gx, gy, gw, gh = 70, 300, 640, 210
    p.append(line(gx, gy, gx + gw, gy, color=INK, sw=1.5))          # вісь X
    p.append(line(gx, gy, gx, gy - gh, color=INK, sw=1.5))          # вісь Y
    p.append(text(gx + gw / 2, gy + 34, "яскравість каналу  0 … 255", size=11, color=MUTED))
    p.append(text(gx - 46, gy - gh / 2, "к-сть", size=11, color=MUTED))

    # «горб» реального розподілу (маса пікселів) — стовпчики
    import math
    def bell(x, mu, s, amp):
        return amp * math.exp(-((x - mu) ** 2) / (2.0 * s * s))
    nb = 48
    bw = gw / float(nb)
    peak99 = None
    for i in range(nb):
        v255 = (i + 0.5) / nb * 255.0
        h = bell(v255, 150, 42, gh * 0.88) + bell(v255, 60, 30, gh * 0.28)
        if h < 1.5:
            h = 1.5
        bx = gx + i * bw
        col = "#cbd5e1"
        if 226 <= v255 <= 244:      # зона верхнього ~1%
            col = "#f3c9a0"
        p.append(rect(bx, gy - h, bw - 1.2, h, fill=col, stroke="none", sw=0, rx=0))

    # поріг 99-го перцентиля
    px99 = gx + (233 / 255.0) * gw
    p.append(line(px99, gy, px99, gy - gh - 6, color=POS, sw=2.0, dash="5 4"))
    p.append(text(px99, gy - gh - 14, "поріг 99%  ≈ 233", size=11, bold=True, color=POS))
    p.append(text(px99 + 4, gy - 40, "верхній 1%", size=10, color="#a9761f", anchor="start"))

    # сміттєвий піксель — гарячий максимум далеко праворуч
    pxmax = gx + (254 / 255.0) * gw
    p.append(line(pxmax, gy, pxmax, gy - 40, color=NEG, sw=2.0))
    p.append(circle(pxmax, gy - 44, 4, fill=NEG, stroke="none", sw=0))
    p.append(text(pxmax, gy - 56, "max = 254", size=11, bold=True, color=NEG, anchor="middle"))
    p.append(text(pxmax, gy - 72, "1 гарячий піксель", size=9, color=NEG, anchor="middle"))

    box = fitbox(70, 334, 640, 56,
                 "Голий максимум ловить випадковий блиск (гарячий піксель, відблиск металу) і роздуває коефіцієнт.\n"
                 "Поріг «вище за 99% пікселів» стоїть на масі справді яскравих точок — стійка оцінка «майже-білого»,\n"
                 "яку не зсуне поодинокий викид.",
                 size=11, pad=10, fill="#fdf3f0", stroke=POS, sw=1.4)
    p.append(box)

    render(os.path.join(OUT, "awb-percentile.svg"), W, H, *p)


# ── awb-pipeline: місце автобалансу в конвеєрі — після демозаїки, ДО тонової
#    кривої (працюємо в лінійному світлі, поки піксель ще пропорційний L·ρ) ────

def fig_awb_pipeline():
    W, H = 860, 330
    p = []
    p.append(text(W / 2, 26, "Де стоїть автобаланс: у лінійному світлі, до тонової кривої",
                  size=15, bold=True))

    stages = [
        ("сирий\nBayer", "#e5e7eb", "L·ρ,\nодин канал"),
        ("демозаїка", "#dbe4f0", "повний RGB,\nще лінійний"),
        ("БАЛАНС\nБІЛОГО", "#f6d9a8", "×g на канал,\nтут і тільки тут"),
        ("тонова\nкрива / γ", "#dcefdc", "стиск у 8 біт,\nнелінійно"),
        ("JPEG", "#e5e7eb", "колір\nвже вбудований"),
    ]
    n = len(stages)
    bw, bh = 132, 74
    gap = (W - 2 * 40 - n * bw) / (n - 1)
    y = 96
    cx_list = []
    for i, (name, col, sub) in enumerate(stages):
        x = 40 + i * (bw + gap)
        cx = x + bw / 2
        cx_list.append(cx)
        hot = name.startswith("БАЛАНС")
        p.append(rect(x, y, bw, bh, fill=col, stroke=(POS if hot else INK),
                      sw=(2.4 if hot else 1.3), rx=8))
        p.append(mtext(cx, y + 26, name, size=12, bold=True))
        p.append(mtext(cx, y + bh + 16, sub, size=9, color=MUTED))
        if i < n - 1:
            xa = x + bw
            p.append(arrow(xa + 4, y + bh / 2, xa + gap - 4, y + bh / 2, color=INK, sw=2.0))

    # підкреслення «лінійної зони»
    lz_x0 = cx_list[0] - bw / 2
    lz_x1 = cx_list[3] - bw / 2
    ly = y - 20
    p.append(line(lz_x0, ly, lz_x1, ly, color=NEG, sw=1.6, dash="6 4"))
    p.append(text((lz_x0 + lz_x1) / 2, ly - 6, "лінійне світло: піксель ∝ L·ρ", size=10,
                  color=NEG, bold=True))

    box = fitbox(40, 246, W - 80, 66,
                 "Коефіцієнти множать сам сигнал світла, тож ставити їх треба ДО тонової кривої (гами), поки\n"
                 "піксель ще пропорційний L·ρ. Після кривої шкала вже стиснена нелінійно — те саме множення дасть\n"
                 "інший, спотворений відтінок. І лише на повному RGB: до демозаїки окремих каналів ще нема.",
                 size=11, pad=10, fill="#eef6ff", stroke=NEG, sw=1.4)
    p.append(box)

    render(os.path.join(OUT, "awb-pipeline.svg"), W, H, *p)


# ── constancy-lineage: історична лінія «ідея → застосування → модель → алгоритм»
#    фон Кріс(1902) → Айвз(1912) → Ленд–МакКанн(1971) → Бухсбаум(1980) → камера ─
# Ідея фігури: показати, що баланс білого — не один винахід, а ланцюг ланок;
# кожна додала один шар. Ліворуч рік+ім'я, праворуч — що саме внесено.

def fig_constancy_lineage():
    W, H = 900, 566
    p = []
    p.append(text(W / 2, 28, "Від загадки ока до трьох коефіцієнтів: ланцюг, не винахід",
                  size=15, bold=True))
    p.append(text(W / 2, 48,
                  "кожна ланка додала рівно один шар — нікого одного не можна назвати «автором балансу білого»",
                  size=10, color=MUTED))

    rows = [
        ("1902", "Йоганн фон Кріс", "ідея (словами)",
         "Колбочки ока адаптуються НАРІЗНО: кожен тип множить свою чутливість на свій "
         "коефіцієнт. Це діагональне перетворення — жоден канал не підмішується в чужий.",
         NEG),
        ("1912", "Герберт Айвз", "застосування",
         "Уперше застосував коефіцієнти фон Кріса до задачі: як їх обрати, щоб ВІДОМИЙ "
         "білий еталон лишався білим під різним світлом. Це — баланс по сірій картці.",
         FIELD),
        ("1971", "Ленд і МакКанн", "модель зору (ретинекс)",
         "Світлість = відношення до НАЙЯСКРАВІШОГО вздовж дороги по зображенню. З цього "
         "нормування «до максимуму» й випала пізніша «біла пляма»: найяскравіше = біле.",
         POS),
        ("1980", "Ґершон Бухсбаум", "формальна модель",
         "Око оцінює світло з УСЬОГО поля зору; середня відбивність сцени сіра. Звідси "
         "прямо: середній колір кадру = колір світла. Це формальний «сірий світ».",
         "#8a5a00"),
    ]

    x_year = 40
    x_card = 250
    cardw = 610
    y0 = 78
    rowh = 92
    for i, (yr, who, tag, body, col) in enumerate(rows):
        cy = y0 + i * rowh
        p.append(text(x_year, cy + 22, yr, size=20, bold=True, color=col, anchor="start"))
        p.append(text(x_year, cy + 42, who, size=11, bold=True, anchor="start"))
        p.append(text(x_year, cy + 58, tag, size=9, color=MUTED, anchor="start"))
        # кольорова риска-ланка ліворуч від картки
        p.append(rect(x_card - 22, cy + 4, 6, rowh - 22, fill=col, stroke=col, sw=0, rx=3))
        # картка внеску
        p.append(fitbox(x_card, cy + 4, cardw, rowh - 22, body,
                        size=11, pad=12, fill="#fbfbfd", stroke=MUTED, sw=1.2))
        # з'єднувальна риска вниз до наступної ланки
        p.append(line(x_card - 19, cy + rowh - 18, x_card - 19, cy + rowh + 2, color=INK, sw=1.6))

    # фінальна ланка: камера
    fy = y0 + len(rows) * rowh + 2
    p.append(rect(x_card - 22, fy, cardw + 22, 46, fill="#eef6ff", stroke=NEG, sw=1.6, rx=8))
    p.append(text(x_card + cardw / 2, fy + 20, "інженерія камери", size=12, bold=True, color=NEG))
    p.append(text(x_card + cardw / 2, fy + 37,
                  "три коефіцієнти g_R, g_G, g_B на канал — біла пляма й сірий світ сходяться сюди з різних кінців ланцюга",
                  size=10, color=INK))

    render(os.path.join(OUT, "constancy-lineage.svg"), W, H, *p)


if __name__ == "__main__":
    fig_white_balance_idea()
    fig_two_estimators()
    fig_color_temperature()
    fig_awb_percentile()
    fig_awb_pipeline()
    fig_constancy_lineage()
    print("figs: white-balance-idea.svg, two-estimators.svg, color-temperature.svg, "
          "awb-percentile.svg, awb-pipeline.svg, constancy-lineage.svg")

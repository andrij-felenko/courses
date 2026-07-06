# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. Тонка нитка крізь усі вузли VS повні вузли без нитки ─────────────────────
# Головна ідея: кістяк проходить ВСІ архітектурні вузли наскрізь, але в кожному
# бере лише один найтонший шлях. Ліворуч — кістяк (тонка суцільна нитка від краю
# до краю). Праворуч — звична помилка: два вузли зроблені «повністю», але не
# з'єднані — стик іще не перевірено, ризик цілий.
def fig_thread():
    W, H = 860, 420
    p = []
    p.append(text(W / 2, 28, "Кістяк бере один тонкий шлях, але веде його крізь УСІ вузли до кінця",
                  size=14, bold=True))

    nodes = ["давач", "прошивка\nМК", "радіо-\nканал", "сервер", "екран\nоператора"]

    # ── ЛІВОРУЧ: ходячий кістяк — тонка суцільна нитка наскрізь ──
    lx0 = 55
    p.append(text(lx0 + 150, 62, "ходячий кістяк", size=13, bold=True, color=FIELD))
    p.append(text(lx0 + 150, 78, "один шлях, але від краю до краю", size=9.5, color=MUTED))
    ny = 150
    bx, bw, gap = lx0, 58, 20
    centers = []
    for i, lbl in enumerate(nodes):
        x = bx + i * (bw + gap)
        p.append(rect(x, ny, bw, 46, fill="#e7f7ee", stroke=FIELD, sw=1.6))
        for j, ln in enumerate(lbl.split("\n")):
            p.append(text(x + bw / 2, ny + 22 + j * 13 - (6 if "\n" in lbl else 0), ln, size=9.5, color=INK))
        centers.append(x + bw / 2)
    # суцільна нитка крізь усі
    for i in range(len(centers) - 1):
        p.append(arrow(centers[i] + bw / 2 - 2, ny + 23, centers[i + 1] - bw / 2 + 2, ny + 23,
                       color=FIELD, sw=2.2))
    p.append(text(lx0 + 150, ny + 90, "одне значення доходить до екрана —", size=10.5, color=INK))
    p.append(text(lx0 + 150, ny + 106, "усі стики вже працюють", size=10.5, bold=True, color=FIELD))

    # роздільник
    p.append(line(W / 2, 55, W / 2, 375, color=MUTED, sw=1, dash="4,4"))

    # ── ПРАВОРУЧ: два «повні» вузли без нитки ──
    rx0 = W / 2 + 40
    p.append(text(rx0 + 150, 62, "вузли поодинці", size=13, bold=True, color=POS))
    p.append(text(rx0 + 150, 78, "готові, але не з'єднані", size=9.5, color=MUTED))
    filled = [0, 3]  # давач і сервер зроблені «повністю»
    rcenters = []
    for i, lbl in enumerate(nodes):
        x = rx0 + i * (bw + gap)
        if i in filled:
            p.append(rect(x, ny, bw, 46, fill="#fadbd6", stroke=POS, sw=2))
        else:
            p.append(rect(x, ny, bw, 46, fill=BG, stroke=MUTED, sw=1.3, rx=6))
        for j, ln in enumerate(lbl.split("\n")):
            col = POS if i in filled else MUTED
            p.append(text(x + bw / 2, ny + 22 + j * 13 - (6 if "\n" in lbl else 0), ln, size=9.5, color=col))
        rcenters.append(x + bw / 2)
    # розірвані стики
    for i in range(len(rcenters) - 1):
        p.append(line(rcenters[i] + bw / 2 - 2, ny + 23, rcenters[i + 1] - bw / 2 + 2, ny + 23,
                      color=POS, sw=1.6, dash="4,4"))
    # хрестик на першому стику
    sx = (rcenters[0] + bw / 2 + rcenters[1] - bw / 2) / 2
    p.append(line(sx - 6, ny + 17, sx + 6, ny + 29, color=POS, sw=2.4))
    p.append(line(sx - 6, ny + 29, sx + 6, ny + 17, color=POS, sw=2.4))
    p.append(text(rx0 + 150, ny + 90, "два вузли «готові», а разом", size=10.5, color=INK))
    p.append(text(rx0 + 150, ny + 106, "не працювали жодного разу", size=10.5, bold=True, color=POS))

    p.append(text(W / 2, H - 18,
                  "Ризик архітектури живе не всередині вузлів, а на стиках між ними — кістяк перевіряє саме стики першими",
                  size=10.5, color=INK, italic=True))
    render(os.path.join(OUT, "thread.svg"), W, H, *p)


# ── 2. Коли виявляється хиба інтеграції: вузли-спершу VS кістяк-спершу ──────────
# Дві часові смуги. Зверху — будуємо вузол за вузлом, стик перевіряємо в кінці:
# помилка інтеграції зринає пізно, коли все дороге до переробки. Знизу — кістяк
# у перший тиждень: та сама помилка зринає одразу, поки дешево.
def fig_risk_timing():
    W, H = 880, 400
    p = []
    p.append(text(W / 2, 28, "Кістяк не прибирає ризик інтеграції — він переносить зустріч із ним на початок",
                  size=14, bold=True))

    x0, x1 = 250, 800
    # шкала часу
    def X(f):
        return x0 + f * (x1 - x0)

    # ── смуга А: спершу вузли ──
    yA = 120
    p.append(text(x0 - 20, yA - 4, "спершу вузли", size=12, bold=True, color=POS, anchor="end"))
    p.append(text(x0 - 20, yA + 12, "поодинці", size=12, bold=True, color=POS, anchor="end"))
    p.append(line(x0, yA, x1, yA, color=INK, sw=2))
    p.append(arrow(x1 - 2, yA, x1 + 8, yA, color=INK, sw=2))
    # відрізки роботи над окремими вузлами
    segs = [(0.02, 0.20, "давач"), (0.22, 0.42, "прошивка"), (0.44, 0.64, "сервер"), (0.66, 0.82, "екран")]
    for a, b, lbl in segs:
        p.append(rect(X(a), yA - 12, X(b) - X(a), 24, fill="#fdece9", stroke=POS, sw=1.3, rx=4))
        p.append(text((X(a) + X(b)) / 2, yA + 5, lbl, size=9.5, color=INK))
    # вибух інтеграції наприкінці
    ix = X(0.92)
    p.append(circle(ix, yA, 12, fill=POS, stroke=POS, sw=2))
    p.append(text(ix, yA + 5, "!", size=15, bold=True, color=BG))
    p.append(text(ix, yA - 22, "стик зібрано", size=10, color=POS, bold=True, anchor="middle"))
    p.append(text(x1, yA + 34, "хиба інтеграції спливає пізно — переробляти дорого", size=10.5,
                  color=POS, bold=True, anchor="end"))

    # ── смуга Б: спершу кістяк ──
    yB = 260
    p.append(text(x0 - 20, yB - 4, "спершу ходячий", size=12, bold=True, color=FIELD, anchor="end"))
    p.append(text(x0 - 20, yB + 12, "кістяк", size=12, bold=True, color=FIELD, anchor="end"))
    p.append(line(x0, yB, x1, yB, color=INK, sw=2))
    p.append(arrow(x1 - 2, yB, x1 + 8, yB, color=INK, sw=2))
    # тонкий наскрізний зріз одразу
    p.append(rect(X(0.02), yB - 12, X(0.13) - X(0.02), 24, fill="#e7f7ee", stroke=FIELD, sw=1.4, rx=4))
    p.append(text((X(0.02) + X(0.13)) / 2, yB + 5, "кістяк", size=9.5, color=INK))
    # вибух одразу
    ix2 = X(0.15)
    p.append(circle(ix2, yB, 12, fill=FIELD, stroke=FIELD, sw=2))
    p.append(text(ix2, yB + 5, "!", size=15, bold=True, color=BG))
    p.append(text(ix2 + 20, yB - 22, "стик зібрано в перший тиждень", size=10, color=FIELD, bold=True, anchor="start"))
    # далі — нарощування м'язів на живому кістяку
    for a, b, lbl in [(0.22, 0.42, "давач"), (0.44, 0.64, "прошивка"), (0.66, 0.98, "решта")]:
        p.append(rect(X(a), yB - 12, X(b) - X(a), 24, fill="#eef6ff", stroke=NEG, sw=1.2, rx=4))
        p.append(text((X(a) + X(b)) / 2, yB + 5, lbl, size=9.5, color=INK))
    p.append(text(x1, yB + 34, "хибу знайдено дешево — м'ясо наростає на робочому кістяку", size=10.5,
                  color=INK, anchor="end"))

    p.append(text(W / 2, H - 18,
                  "Та сама помилка коштує тим менше, чим раніше її зустріти; кістяк призначає зустріч на перший тиждень",
                  size=10.5, color=INK, italic=True))
    render(os.path.join(OUT, "risk-timing.svg"), W, H, *p)


# ── 3. Родовід ідеї в часі: куля, кістяк, загострення, милиці ──────────────────
# Історична фігура для вставки hist-. Одна вісь часу з подіями-віхами. Дві
# споріднені лінії: «трасувальна куля» (Hunt/Thomas) і «ходячий кістяк»
# (Cockburn), що сходяться в спільну ідею; далі загострення (Freeman/Pryce,
# 97 Things) і уточнення (Adzic). Підписи розставлені з ЗАПАСОМ — над віссю й
# під нею по черзі, щоб жоден напис не ліг на інший.
def fig_lineage():
    W, H = 900, 470
    p = []
    p.append(text(W / 2, 30, "Родовід ідеї: дві споріднені лінії сходяться в один прийом",
                  size=15, bold=True))

    x0, x1 = 70, 830
    axy = 240                      # вісь часу
    # роки, які реально розставляємо (нерівномірно — за подіями, не за масштабом)
    years = [1996, 1999, 2000, 2004, 2009, 2014]
    fx = {1996: 0.02, 1999: 0.20, 2000: 0.30, 2004: 0.50, 2009: 0.74, 2014: 0.97}

    def X(f):
        return x0 + f * (x1 - x0)

    # головна вісь часу
    p.append(line(x0 - 10, axy, x1 + 18, axy, color=INK, sw=2.4))
    p.append(arrow(x1 + 6, axy, x1 + 22, axy, color=INK, sw=2.4))
    for y in years:
        xx = X(fx[y])
        p.append(line(xx, axy - 6, xx, axy + 6, color=INK, sw=2))
        p.append(text(xx, axy + 22, str(y), size=11, bold=True, color=MUTED))

    # ── подія-картка над/під віссю; side=+1 знизу, −1 зверху ──
    # Без поводків-ліній до карток: вузол-кружок на осі + близька картка вже
    # читаються як пара, а зайва лінія ризикує перетнути напис (svgcheck).
    def event(year, side, title_lines, who, color, fill):
        xx = X(fx[year])
        # вузол на осі
        p.append(circle(xx, axy, 6.5, fill=color, stroke=color, sw=2))
        bw, bh = 168, 52
        gap = 46
        by = axy - gap - bh if side < 0 else axy + gap
        bx = xx - bw / 2
        bx = max(x0 - 8, min(bx, x1 + 18 - bw))     # не за край
        p.append(rect(bx, by, bw, bh, fill=fill, stroke=color, sw=1.6, rx=7))
        for j, ln in enumerate(title_lines):
            p.append(text(bx + bw / 2, by + 18 + j * 15, ln, size=10.5, bold=(j == 0), color=INK))
        p.append(text(bx + bw / 2, by + bh - 7, who, size=9, italic=True, color=MUTED))
        return xx, by, bh

    # трасувальна куля (споріднена лінія) — зверху
    tx, tby, tbh = event(1999, -1, ["трасувальна куля", "лишається в системі"],
                         "Hunt · Thomas, 1999", NEG, "#eef3fe")
    # коинаж кістяка — знизу
    cx96, _, _ = event(1996, +1, ["термін «ходячий кістяк»", "тонко зв'язана архітектура"],
                       "Cockburn, 1996", FIELD, "#e7f7ee")
    # канонічне визначення — зверху
    cx04, cby, cbh = event(2004, -1, ["канонічне визначення", "зв'язати головні складники"],
                          "Crystal Clear, 2004", FIELD, "#e7f7ee")
    # загострення — знизу
    fx09, fby, fbh = event(2009, +1, ["загострення: авто", "збірка·розгортання·тест"],
                          "Freeman · Pryce, 2009", INK, FILL)
    # уточнення милицями — зверху
    ax14, _, _ = event(2014, -1, ["«на милиці»: спершу", "лице, бекенд — потім"],
                      "Adzic, 2014", POS, "#fdecea")

    # тонкий місток спорідненості: куля (1999) ⇢ канонічне визначення (2004)
    p.append(text(W / 2, H - 20,
                  "Куля Ганта й Томаса та кістяк Кокберна — одна ідея наскрізної нитки, що лишається; далі її загострили й уточнили",
                  size=10.5, color=INK, italic=True))
    render(os.path.join(OUT, "lineage.svg"), W, H, *p)


if __name__ == "__main__":
    fig_thread()
    fig_risk_timing()
    fig_lineage()
    print("figs done")

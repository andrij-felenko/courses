# -*- coding: utf-8 -*-
# Фігури до статті «Супутникові системи доповнення (SBAS)»
# (book/communications/synchronization/sbas-corrections).
# svgkit імпортуємо зі scripts/ (НЕ копіюємо). Вивід — у ./img/.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: ланцюг доповнення — від наземних станцій до приймача ────────────
# Ключова ідея, яку важко переказати словами: SBAS вимірює похибки НА ЗЕМЛІ
# (мережа точних станцій), рахує їх у центрі й розсилає ВГОРУ через GEO-супутник,
# щоб приймач узяв готову поправку з неба. Тому «супутникова» система доповнення.
def fig_augmentation_chain():
    W, H = 680, 470
    parts = []

    gnss = (150, 70)     # GPS-супутник (джерело сигналу з похибками)
    geo = (540, 70)      # геостаціонарний супутник SBAS (роздає поправки)
    user = (540, 380)    # приймач користувача
    ref = [(70, 360), (150, 385), (235, 362)]   # наземні опорні станції
    master = (355, 300)  # головна станція (центр обробки)
    uplink = (455, 200)  # станція закачування

    # той самий сигнал GPS іде і до наземних станцій, і до користувача
    for sx, sy in ref:
        parts.append(line(gnss[0], gnss[1], sx, sy - 8, color=MUTED, sw=1, dash="3 4"))
    parts.append(line(gnss[0], gnss[1], user[0], user[1], color=MUTED, sw=1, dash="3 4"))

    # похибка «в дорозі» — підпис на промені GPS→користувач
    parts.append(text(300, 150, 'сигнал GPS + похибки', size=12, color=MUTED,
                      anchor='start', italic=True))

    # ланцюг обробки: станції → головна → закачування → GEO → користувач
    for sx, sy in ref:
        parts.append(arrow(sx, sy - 4, master[0] - 8, master[1] - 6, color=NEG, sw=1.4))
    parts.append(arrow(master[0] + 20, master[1] - 20, uplink[0] - 6, uplink[1] + 10,
                       color=FIELD, sw=2))
    parts.append(arrow(uplink[0] + 4, uplink[1] - 6, geo[0] - 10, geo[1] + 14,
                       color=FIELD, sw=2))
    parts.append(arrow(geo[0], geo[1] + 12, user[0], user[1] - 12, color=POS, sw=2.2))

    # підписи ролей ланцюга
    parts.append(text(300, 250, 'виміряні похибки', size=11, color=NEG, anchor='start'))
    parts.append(text(392, 250, '→ поправки', size=11, color=FIELD, anchor='start'))
    parts.append(text(560, 235, 'поправки з неба', size=11, color=POS, anchor='start'))

    # вузли
    parts.append(circle(gnss[0], gnss[1], 12, fill="#eef2ff", stroke=NEG, sw=2))
    parts.append(text(gnss[0], gnss[1] - 20, 'супутник GNSS', size=12, bold=True))
    parts.append(circle(geo[0], geo[1], 12, fill="#fdecea", stroke=POS, sw=2))
    parts.append(text(geo[0], geo[1] - 20, 'GEO-супутник SBAS', size=12, bold=True))

    for i, (sx, sy) in enumerate(ref):
        parts.append(rect(sx - 11, sy - 4, 22, 16, fill="#eaf0fd", stroke=NEG, sw=1.4, rx=3))
    parts.append(text(150, 415, 'опорні станції (точно відомі місця)',
                      size=12, color=NEG))

    b, bw, bh = textbox(master[0], master[1], "головна\nстанція", size=12, bold=True,
                        fill="#eaf7ef", stroke=FIELD)
    parts.append(b)
    parts.append(rect(uplink[0] - 13, uplink[1] - 8, 26, 16, fill="#eaf7ef",
                      stroke=FIELD, sw=1.4, rx=3))
    parts.append(text(uplink[0] + 20, uplink[1] + 4, 'закачування', size=11,
                      color=FIELD, anchor='start'))

    b2, bw2, bh2 = textbox(user[0], user[1] + 4, "приймач:\n−похибки", size=12, bold=True,
                           fill="#fff7e6", stroke="#d98c00")
    parts.append(b2)

    cap = ("Похибки міряють на землі точні станції, головна станція зводить їх у поправки,\n"
           "а GEO-супутник роздає готову поправку з неба — тому доповнення «супутникове».")
    parts.append(fitbox(20, H - 50, W - 40, 40, cap, size=12, fill="#f4f6f8", stroke=MUTED))

    return render(os.path.join(OUT, 'augmentation-chain.svg'), W, H,
                  *parts, title='Як SBAS доносить поправку: земля → центр → GEO → приймач')


# ── Фігура 2: іоносферна сітка — чому поправка не одне число, а карта ─────────
# Іоносфера гальмує сигнал по-різному над різними точками. SBAS міряє затримку
# у вузлах СІТКИ (IGP) на висоті ~350 км; приймач бере точку, де його промінь
# протикає шар (pierce point), та інтерполює затримку із сусідніх вузлів.
def fig_iono_grid():
    W, H = 660, 430
    parts = []

    # шар іоносфери — смуга вгорі
    parts.append(rect(60, 70, W - 120, 40, fill="#eef2ff", stroke=NEG, sw=1.2, rx=8))
    parts.append(text(W / 2, 60, 'шар іоносфери ≈ 350 км над Землею', size=13, bold=True))

    # вузли сітки IGP на шарі
    gx = [120, 210, 300, 390, 480, 570]
    gy = 90
    for x in gx:
        parts.append(circle(x, gy, 5, fill="#fff", stroke=NEG, sw=1.8))
    parts.append(text(120, gy - 14, 'IGP: виміряна затримка у вузлі', size=11,
                      color=NEG, anchor='start'))

    # приймач і супутник — промінь протикає шар у pierce point між вузлами
    rec = (300, 360)
    sat = (470, 130)
    pierce = (393, 100)   # приблизно на шарі, між вузлами x=390 і x=480
    parts.append(line(rec[0], rec[1], sat[0], sat[1], color=MUTED, sw=1.4, dash="4 4"))
    parts.append(circle(pierce[0], pierce[1], 6, fill="#fdecea", stroke=POS, sw=2))
    parts.append(text(pierce[0] + 10, pierce[1] + 22, 'точка протику (pierce point)',
                      size=11, color=POS, anchor='start'))

    # інтерполяція: тягнемо від pierce до двох сусідніх вузлів
    parts.append(line(pierce[0], pierce[1], 390, gy, color=POS, sw=1, dash="2 3"))
    parts.append(line(pierce[0], pierce[1], 480, gy, color=POS, sw=1, dash="2 3"))
    parts.append(text(435, 128, 'інтерполяція', size=10, color=POS))

    # вузли й приймач
    parts.append(circle(sat[0], sat[1], 11, fill="#eef2ff", stroke=NEG, sw=2))
    parts.append(text(sat[0] + 16, sat[1], 'супутник', size=12, anchor='start'))
    b, bw, bh = textbox(rec[0], rec[1], "приймач", size=12, bold=True,
                        fill="#fff7e6", stroke="#d98c00")
    parts.append(b)

    cap = ("Затримка в іоносфері різна над різними місцями, тож поправка — не одне число, а карта:\n"
           "SBAS дає затримку у вузлах сітки, приймач інтерполює її в точці протику променем.")
    parts.append(fitbox(20, H - 50, W - 40, 40, cap, size=12, fill="#f4f6f8", stroke=MUTED))

    return render(os.path.join(OUT, 'iono-grid.svg'), W, H,
                  *parts, title='Іоносферна сітка: поправка як карта затримок')


# ── Фігура 3: дві осі SBAS — точність І цілісність (захисний рівень) ──────────
# Головне непорозуміння: SBAS не лише зменшує похибку (точність), а й ГАРАНТУЄ
# межу — захисний рівень. Поки межа під допуском (alert limit) — можна довіряти;
# перевищила — «не використовувати». Саме цілісність робить SBAS придатним для авіації.
def fig_accuracy_integrity():
    W, H = 660, 420
    parts = []

    axis_x = 150
    top = 90
    bot = 340
    parts.append(line(axis_x, top, axis_x, bot, color=INK, sw=2))
    parts.append(arrow(axis_x, top + 4, axis_x, top - 8, color=INK, sw=2))
    parts.append(text(axis_x - 10, top - 14, 'похибка ↑', size=12, anchor='end'))

    # межа допуску (alert limit) — горизонталь
    al_y = 150
    parts.append(line(axis_x, al_y, W - 60, al_y, color=POS, sw=2, dash="6 4"))
    parts.append(text(W - 56, al_y - 6, 'допуск (alert limit)', size=12, color=POS,
                      anchor='start'))

    # СЛУЖБА ДОСТУПНА: справжня похибка мала, захисний рівень під допуском
    x1 = 300
    parts.append(circle(x1, 300, 6, fill="#fff", stroke=INK, sw=2))
    parts.append(text(x1, 320, 'справжня', size=10))
    parts.append(text(x1, 333, 'похибка', size=10))
    pl_y1 = 210
    parts.append(line(x1, 300, x1, pl_y1, color=FIELD, sw=8))
    parts.append(circle(x1, pl_y1, 5, fill="#eaf7ef", stroke=FIELD, sw=2))
    parts.append(text(x1, pl_y1 - 12, 'захисний рівень', size=11, color=FIELD))
    parts.append(text(x1, 360, 'МОЖНА ДОВІРЯТИ', size=12, bold=True, color=FIELD))

    # СЛУЖБА НЕДОСТУПНА: захисний рівень виліз за допуск → «не використовувати»
    x2 = 500
    parts.append(circle(x2, 300, 6, fill="#fff", stroke=INK, sw=2))
    pl_y2 = 118
    parts.append(line(x2, 300, x2, pl_y2, color=POS, sw=8))
    parts.append(circle(x2, pl_y2, 5, fill="#fdecea", stroke=POS, sw=2))
    parts.append(text(x2, pl_y2 - 12, 'захисний рівень', size=11, color=POS))
    parts.append(text(x2, 360, 'НЕ ВИКОРИСТОВУВАТИ', size=12, bold=True, color=POS))

    cap = ("SBAS не лише зменшує похибку — він рахує гарантовану межу зверху (захисний рівень).\n"
           "Межа під допуском — фіксу можна довіряти; виповзла — приймач сам каже «не використовувати».")
    parts.append(fitbox(20, H - 50, W - 40, 40, cap, size=12, fill="#f4f6f8", stroke=MUTED))

    return render(os.path.join(OUT, 'accuracy-integrity.svg'), W, H,
                  *parts, title='Дві осі SBAS: точність і цілісність (захисний рівень)')


if __name__ == '__main__':
    fig_augmentation_chain()
    fig_iono_grid()
    fig_accuracy_integrity()
    print('OK figs:', os.listdir(OUT))

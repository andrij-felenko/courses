# -*- coding: utf-8 -*-
"""Фігури до вставки «proj-base-drive-firmware» (керування базою BJT у прошивці).
Запуск:  python figs-proj.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def fig_deadtime():
    """Команда ШІМ на базу vs реальний струм колектора: сховок зсуває спад,
    компенсація вкорочує команду наперед, щоб реальний ON збігся з бажаним."""
    W, H = 780, 470
    f = [text(W / 2, 26, "Мертвий час = сховок t_s: чому команду вимкнення дають РАНІШЕ",
              size=15, bold=True)]

    x0, x1 = 90, 700          # межі часової осі
    def X(frac):              # frac 0..1 → піксель
        return x0 + (x1 - x0) * frac

    # три доріжки
    y_cmd = 92               # команда бази (регістр ШІМ)
    y_col = 232              # реальний струм колектора
    y_fix = 372              # команда з компенсацією
    hi, lo = 46, 0           # висота рівня

    def track(y, label, sub):
        f.append(text(x0 - 12, y - lo - 22, label, size=12, bold=True, anchor="end"))
        f.append(text(x0 - 12, y - lo - 6, sub, size=9, color=MUTED, anchor="end"))
        f.append(line(x0, y, x1, y, color=MUTED, sw=1.0))  # базова лінія (низ)

    def pulse(y, a, b, color=INK, dash=None):
        """Прямокутний імпульс від frac a до frac b (високий рівень = провідність)."""
        xa, xb = X(a), X(b)
        yt = y - hi
        f.append(line(xa, y, xa, yt, color=color, sw=2.4, dash=dash))
        f.append(line(xa, yt, xb, yt, color=color, sw=2.4, dash=dash))
        f.append(line(xb, yt, xb, y, color=color, sw=2.4, dash=dash))

    # спільні мітки моментів
    on_cmd = 0.16            # команда «ввімкнути»
    off_cmd = 0.62           # команда «вимкнути» (наївна)
    ts = 0.16                # тривалість сховку (частка осі)
    tr = 0.05               # наростання
    tf = 0.05               # спад

    # ── доріжка 1: наївна команда бази ──
    track(y_cmd, "Команда бази", "регістр CCR ШІМ")
    pulse(y_cmd, on_cmd, off_cmd, color=NEG)
    f.append(text(X((on_cmd + off_cmd) / 2), y_cmd - hi - 8,
                  "бажаний ON", size=10, color=NEG))

    # ── доріжка 2: реальний колектор (відстає на t_s після зняття бази) ──
    track(y_col, "Струм колектора", "реальний Ic")
    col_on = on_cmd + tr                    # ввімкнувся трохи згодом (наростання)
    col_off = off_cmd + ts                  # ВИМКНУВСЯ пізніше на сховок!
    pulse(y_col, col_on, col_off, color=POS)
    f.append(text(X((col_on + col_off) / 2), y_col - hi - 8,
                  "реальний ON — ДОВШИЙ", size=10, color=POS))
    # заштрихувати «зайвий» шматок від off_cmd до col_off
    xa, xb = X(off_cmd), X(col_off)
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" opacity="0.18"/>'
             % (xa, y_col - hi, xb - xa, hi, POS))
    # стрілка сховку
    f.append(line(X(off_cmd), y_col + 16, X(col_off), y_col + 16, color=POS, sw=1.6))
    f.append(line(X(off_cmd), y_col + 12, X(off_cmd), y_col + 20, color=POS, sw=1.6))
    f.append(line(X(col_off), y_col + 12, X(col_off), y_col + 20, color=POS, sw=1.6))
    f.append(text(X((off_cmd + col_off) / 2), y_col + 30, "t_s (сховок)",
                  size=10, color=POS, bold=True))

    # вертикаль команди off (спільна) через усі доріжки
    f.append(line(X(off_cmd), y_cmd - hi - 4, X(off_cmd), y_fix + 8,
                  color=MUTED, sw=1.0, dash="4 3"))
    f.append(text(X(off_cmd), y_cmd - hi - 12, "команда OFF (наївна)",
                  size=9, color=MUTED))

    # ── доріжка 3: компенсована команда (OFF раніше на t_s) ──
    track(y_fix, "Команда з компенс.", "OFF раніше на t_s")
    off_fix = off_cmd - ts                  # даємо OFF наперед
    pulse(y_fix, on_cmd, off_fix, color=FIELD)
    f.append(line(X(off_fix), y_fix - hi - 4, X(off_fix), y_fix + 8,
                  color=FIELD, sw=1.2, dash="4 3"))
    f.append(text(X(off_fix), y_fix - hi - 12, "OFF раніше", size=9, color=FIELD, bold=True))
    # тепер реальний колектор вимкнеться на off_fix + ts = off_cmd → збіг!
    f.append(text(X((on_cmd + off_fix) / 2), y_fix - hi - 8,
                  "коротша команда", size=10, color=FIELD))

    note = ("Сховок t_s зсуває реальний спад Ic на ~t_s ПІСЛЯ команди — ефективна\n"
            "шпаруватість більша за задану. Лік: віднімати виміряний t_s від часу ON у CCR.")
    f.append(fitbox(x0, 412, x1 - x0, 44, note, size=11, fill="#f0f7f1", stroke=FIELD, color=INK))

    render(os.path.join(IMG, "deadtime-comp.svg"), W, H, *f)


def fig_capture():
    """Як МК сам міряє t_s: GPIO знімає базу в момент t0 (регістр), дільник на
    колекторі + компаратор дають фронт на вхід захоплення; t_s = t_cap − t0."""
    W, H = 780, 430
    f = [text(W / 2, 26, "МК міряє власний сховок: захоплення фронту на колекторі",
              size=15, bold=True)]

    # ── блок МК ──
    mcu_x, mcu_y, mcu_w, mcu_h = 60, 70, 250, 300
    f.append(rect(mcu_x, mcu_y, mcu_w, mcu_h, fill="#fbfcfd", stroke=MUTED, sw=1.4, rx=10))
    f.append(text(mcu_x + 14, mcu_y + 22, "Мікроконтролер", size=12, bold=True, anchor="start"))

    # таймер усередині
    f.append(rect(mcu_x + 24, mcu_y + 44, mcu_w - 48, 70, fill="#eef1f5", stroke=INK, sw=1.4, rx=6))
    f.append(text(mcu_x + mcu_w / 2, mcu_y + 70, "Таймер (лічильник)", size=11, bold=True))
    f.append(text(mcu_x + mcu_w / 2, mcu_y + 90, "t0: запис у момент OFF", size=10, color=NEG))
    f.append(text(mcu_x + mcu_w / 2, mcu_y + 106, "t_cap: input capture", size=10, color=POS))

    # GPIO OFF-вивід
    gpio_y = mcu_y + 150
    f.append(text(mcu_x + 24, gpio_y - 6, "GPIO → база", size=11, bold=True, anchor="start"))
    f.append(text(mcu_x + 24, gpio_y + 10, "знімаємо базу (OFF)", size=9, color=MUTED, anchor="start"))
    f.append(line(mcu_x + mcu_w, gpio_y, 360, gpio_y, color=NEG, sw=2.0))

    # ICx вхід захоплення
    ic_y = mcu_y + 240
    f.append(text(mcu_x + 24, ic_y - 6, "ICx ← захоплення", size=11, bold=True, anchor="start"))
    f.append(text(mcu_x + 24, ic_y + 10, "фронт напруги колектора", size=9, color=MUTED, anchor="start"))
    f.append(line(mcu_x + mcu_w, ic_y, 360, ic_y, color=POS, sw=2.0))

    # ── ключ BJT праворуч ──
    tx = 470                       # вісь транзистора
    # база від GPIO через Rb
    f.append(rect(370, gpio_y - 11, 54, 22, fill="#eef1f5", stroke=INK, sw=1.4, rx=3))
    f.append(text(397, gpio_y + 4, "Rb", size=11))
    f.append(line(424, gpio_y, tx - 4, gpio_y, color=INK, sw=1.8))

    # символ NPN спрощено
    bt, bb = gpio_y - 26, gpio_y + 40
    f.append(line(tx, bt, tx, bb, color=INK, sw=2.4))           # планка бази
    f.append(line(tx, bt + 8, tx + 26, bt - 10, color=INK, sw=1.8))   # колектор угору
    col_top = bt - 40
    f.append(line(tx + 26, bt - 10, tx + 26, col_top, color=INK, sw=1.8))
    f.append(line(tx, bb - 8, tx + 26, bb + 10, color=INK, sw=1.8))   # емітер униз
    f.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>' % (
        tx + 17, bb + 1, tx + 26, bb + 10, tx + 15, bb + 9, INK))
    # емітер → земля
    ey = bb + 34
    f.append(line(tx + 26, bb + 10, tx + 26, ey, color=INK, sw=1.8))
    gx = tx + 26
    f.append(line(gx - 13, ey, gx + 13, ey, color=INK, sw=2.2))
    f.append(line(gx - 8, ey + 5, gx + 8, ey + 5, color=INK, sw=2.0))
    f.append(line(gx - 3, ey + 10, gx + 3, ey + 10, color=INK, sw=1.8))

    # навантаження від +V до колектора
    f.append(rect(tx + 13, col_top - 74, 26, 54, fill=FILL, stroke=INK, sw=1.4, rx=4))
    f.append(text(tx + 70, col_top - 47, "навантаження", size=10, color=MUTED, anchor="start"))
    f.append(line(tx + 26, col_top, tx + 26, col_top - 20, color=INK, sw=1.8))
    f.append(line(tx + 26, col_top - 74, tx + 26, col_top - 92, color=INK, sw=1.8))
    f.append(plus(tx + 26, col_top - 100))
    f.append(text(tx + 46, col_top - 96, "+V", size=11, bold=True, anchor="start"))

    # відгалуження колектора на дільник → назад у ICx
    node_y = (col_top + bt - 10) / 2
    f.append('<circle cx="%.1f" cy="%.1f" r="3" fill="%s"/>' % (tx + 26, node_y, INK))
    f.append(line(tx + 26, node_y, 640, node_y, color=POS, sw=1.6))
    # дільник (два резистори схематично) вниз до землі, середина → ICx
    dvx = 640
    f.append(rect(dvx - 13, node_y + 10, 26, 40, fill="#eef1f5", stroke=INK, sw=1.2, rx=3))
    f.append(rect(dvx - 13, node_y + 62, 26, 40, fill="#eef1f5", stroke=INK, sw=1.2, rx=3))
    f.append(line(dvx, node_y, dvx, node_y + 10, color=POS, sw=1.6))
    f.append(line(dvx, node_y + 50, dvx, node_y + 62, color=INK, sw=1.4))
    f.append(text(dvx + 18, node_y + 34, "дільник", size=9, color=MUTED, anchor="start"))
    f.append(text(dvx + 18, node_y + 50, "(+ компаратор)", size=9, color=MUTED, anchor="start"))
    # земля дільника
    f.append(line(dvx, node_y + 102, dvx, node_y + 112, color=INK, sw=1.4))
    f.append(line(dvx - 10, node_y + 112, dvx + 10, node_y + 112, color=INK, sw=2.0))
    f.append(line(dvx - 6, node_y + 117, dvx + 6, node_y + 117, color=INK, sw=1.6))
    # середина дільника → ICx (ліворуч, у вивід захоплення)
    midy = node_y + 56
    f.append('<circle cx="%.1f" cy="%.1f" r="3" fill="%s"/>' % (dvx, midy, POS))
    f.append(line(dvx, midy, dvx + 30, midy, color=POS, sw=1.6))
    f.append(line(dvx + 30, midy, dvx + 30, ic_y, color=POS, sw=1.6))
    f.append(line(dvx + 30, ic_y, 360, ic_y, color=POS, sw=1.6))
    # напрям (стрілка на вхід ICx)
    f.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>' % (
        368, ic_y - 5, 360, ic_y, 368, ic_y + 5, POS))

    note = ("Знімаємо базу й ОДРАЗУ фіксуємо t0. Колектор ще проводить (сховок), потім\n"
            "різко злітає — цей фронт ловить захоплення в t_cap. Сховок t_s = t_cap − t0.")
    f.append(fitbox(60, 384, 660, 40, note, size=11, fill="#f0f7f1", stroke=FIELD, color=INK))

    render(os.path.join(IMG, "measure-ts.svg"), W, H, *f)


if __name__ == "__main__":
    fig_deadtime()
    fig_capture()
    print("OK: img/deadtime-comp.svg, img/measure-ts.svg")

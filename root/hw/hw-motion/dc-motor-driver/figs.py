# -*- coding: utf-8 -*-
"""Фігури до теми «Драйвер DC-моторів».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def motor(cx, cy, r=26, label="M"):
    """Кружок-мотор з підписом."""
    return (circle(cx, cy, r, fill="#eef2f7", stroke=LINE, sw=2) +
            text(cx, cy + 6, label, size=18, bold=True, color=INK))


def nmos(cx, cy, on=False):
    """Спрощений значок NMOS-ключа: квадрат із підписом, зелений якщо відкритий."""
    w = 34
    fill = "#e8f7ee" if on else FILL
    stroke = FIELD if on else LINE
    out = rect(cx - w / 2, cy - w / 2, w, w, fill=fill, stroke=stroke, sw=2.2)
    out += text(cx, cy + 5, "вкл" if on else "вим", size=11,
                color=FIELD if on else MUTED, bold=on)
    return out


# ── 1. Чому ніжка МК не крутить мотор: різниця струмів ──────────────────────
def fig_why_driver():
    W, H = 720, 330
    f = [text(W / 2, 30, "Ніжка мікроконтролера не тягне мотор: різниця в струмі", size=16, bold=True)]

    # ліва колонка: ніжка МК
    f.append(rect(70, 70, 230, 200, fill="#eef2f7", stroke=LINE, sw=1.6))
    f.append(text(185, 96, "ніжка МК", size=15, bold=True))
    f.append(text(185, 128, "віддає ≈ 20 мА", size=14, color=NEG))
    # маленький стовпчик струму
    f.append(rect(160, 170, 50, 16, fill=NEG, stroke=NEG, sw=1))
    f.append(text(185, 210, "20 мА", size=12, color=NEG, bold=True))
    f.append(text(185, 250, "досить на світлодіод", size=12, color=MUTED))

    # права колонка: мотор
    f.append(rect(420, 70, 230, 200, fill="#fdecea", stroke=POS, sw=1.6))
    f.append(text(535, 96, "малий мотор", size=15, bold=True))
    f.append(text(535, 128, "бере 0.5…2 А пуску", size=14, color=POS))
    # великий стовпчик струму
    f.append(rect(445, 150, 180, 36, fill=POS, stroke=POS, sw=1))
    f.append(text(535, 210, "≈ 1000 мА і більше", size=12, color=POS, bold=True))
    f.append(text(535, 250, "у 50+ разів більше", size=12, color=MUTED))

    # стрілка-висновок
    f.append(text(360, 300, "→ між МК і мотором потрібен ключ-підсилювач струму (драйвер)",
                  size=13, bold=True, color=INK))
    render(os.path.join(IMG, "why-driver.svg"), W, H, *f)


# ── 2. Найпростіший драйвер: один ключ + гасний діод ────────────────────────
def fig_one_switch():
    W, H = 720, 360
    f = [text(W / 2, 30, "Найпростіший драйвер: один ключ вмикає мотор в один бік", size=16, bold=True)]

    # шина +V зверху
    f.append(line(120, 80, 600, 80, color=POS, sw=2.5))
    f.append(plus(120, 80, 11))
    f.append(text(150, 72, "+V живлення", size=13, color=POS, bold=True))
    # земля знизу
    f.append(line(120, 320, 600, 320, color=NEG, sw=2.5))
    f.append(minus(120, 320, 11))
    f.append(text(150, 312, "земля (GND)", size=13, color=NEG, bold=True))

    # мотор зверху (між +V і стоком)
    f.append(line(360, 80, 360, 120, color=LINE, sw=2))
    f.append(motor(360, 150))
    f.append(line(360, 176, 360, 210, color=LINE, sw=2))

    # ключ NMOS
    f.append(nmos(360, 240, on=True))
    f.append(line(360, 257, 360, 320, color=LINE, sw=2))

    # затвор від МК
    f.append(line(343, 240, 250, 240, color=LINE, sw=1.6))
    f.append(rect(150, 224, 100, 32, fill="#eef2f7", stroke=LINE, sw=1.4))
    f.append(text(200, 245, "ШІМ з МК", size=12, bold=True))

    # гасний діод паралельно мотору (катод до +V)
    f.append(line(470, 120, 470, 80, color=FIELD, sw=2))   # верх до +V
    f.append(line(470, 210, 470, 176, color=FIELD, sw=2))  # низ до стоку рівня мотора
    f.append(line(470, 120, 470, 210, color=FIELD, sw=2))
    # трикутник діода (вістрям донизу = провідність знизу вгору)
    f.append('<path d="M456 195 L484 195 L470 170 z" fill="#e8f7ee" stroke="%s" stroke-width="2"/>' % FIELD)
    f.append(line(456, 170, 484, 170, color=FIELD, sw=2.5))  # смужка катода
    f.append(line(360, 120, 470, 120, color=FIELD, sw=2))    # верхній вузол до мотора
    f.append(line(360, 210, 470, 210, color=FIELD, sw=2))    # нижній вузол (стік)
    f.append(text(548, 150, "гасний", size=12, color=FIELD, bold=True))
    f.append(text(548, 168, "діод", size=12, color=FIELD, bold=True))

    f.append(text(W / 2, 346, "Ключ садить низ мотора до землі; діод дає струмові котушки кільце в паузі",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "one-switch.svg"), W, H, *f)


# ── 3. Напрямок задає діагональ (суть драйвера реверсу) ─────────────────────
def fig_direction():
    W, H = 720, 360

    def bridge(x0, title, q1, q2, q3, q4, cur_dir):
        out = [text(x0 + 150, 60, title, size=15, bold=True)]
        # рамка
        topY, botY = 90, 270
        lX, rX = x0 + 70, x0 + 230
        # шина +V і земля
        out.append(line(lX - 20, topY, rX + 20, topY, color=POS, sw=2.2))
        out.append(line(lX - 20, botY, rX + 20, botY, color=NEG, sw=2.2))
        out.append(plus(lX - 20, topY, 9))
        out.append(minus(lX - 20, botY, 9))
        # верхні ключі
        out.append(nmos(lX, topY + 40, on=q1))
        out.append(nmos(rX, topY + 40, on=q2))
        out.append(text(lX - 30, topY + 44, "Q1", size=11, color=MUTED, anchor="end"))
        out.append(text(rX + 30, topY + 44, "Q2", size=11, color=MUTED, anchor="start"))
        # нижні ключі
        out.append(nmos(lX, botY - 40, on=q3))
        out.append(nmos(rX, botY - 40, on=q4))
        out.append(text(lX - 30, botY - 36, "Q3", size=11, color=MUTED, anchor="end"))
        out.append(text(rX + 30, botY - 36, "Q4", size=11, color=MUTED, anchor="start"))
        # з'єднання ключів із шинами
        out.append(line(lX, topY, lX, topY + 23, color=LINE, sw=1.8))
        out.append(line(rX, topY, rX, topY + 23, color=LINE, sw=1.8))
        out.append(line(lX, botY, lX, botY - 23, color=LINE, sw=1.8))
        out.append(line(rX, botY, rX, botY - 23, color=LINE, sw=1.8))
        # середні вузли до мотора
        midY = (topY + botY) / 2
        out.append(line(lX, topY + 57, lX, midY, color=LINE, sw=1.8))
        out.append(line(lX, botY - 57, lX, midY, color=LINE, sw=1.8))
        out.append(line(rX, topY + 57, rX, midY, color=LINE, sw=1.8))
        out.append(line(rX, botY - 57, rX, midY, color=LINE, sw=1.8))
        out.append(line(lX, midY, x0 + 124, midY, color=LINE, sw=1.8))
        out.append(line(rX, midY, x0 + 176, midY, color=LINE, sw=1.8))
        out.append(motor(x0 + 150, midY))
        # стрілка напрямку струму крізь мотор
        if cur_dir == "right":
            out.append(arrow(x0 + 120, midY - 34, x0 + 180, midY - 34, color=POS, sw=2.2))
        else:
            out.append(arrow(x0 + 180, midY - 34, x0 + 120, midY - 34, color=POS, sw=2.2))
        return out

    f = [text(W / 2, 28, "Напрямок обертання задає, яку діагональ ключів відкрити", size=16, bold=True)]
    f += bridge(20, "Вперед: Q1 + Q4", True, False, False, True, "right")
    f += bridge(380, "Назад: Q2 + Q3", False, True, True, False, "left")
    f.append(text(W / 2, 320, "Одна діагональ жене струм →, протилежна — ←; решта ключів закриті",
                  size=12, color=MUTED))
    f.append(text(W / 2, 344, "Глибше про сам H-міст — окрема стаття; тут він — серце драйвера",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "direction.svg"), W, H, *f)


# ── 4. Гальмо проти вибігу ──────────────────────────────────────────────────
def fig_brake_coast():
    W, H = 720, 330

    def case(x0, title, shorted, desc):
        out = [text(x0 + 150, 60, title, size=15, bold=True)]
        cx, cy = x0 + 150, 165
        out.append(motor(cx, cy, r=30))
        if shorted:
            # дуга, що замикає кінці мотора (закорочено)
            out.append('<path d="M%d %d Q %d %d %d %d" fill="none" stroke="%s" '
                       'stroke-width="2.6"/>' % (cx - 30, cy, cx, cy + 70, cx + 30, cy, FIELD))
            out.append(arrow(cx - 6, cy + 52, cx + 12, cy + 50, color=FIELD, sw=2))
            out.append(text(cx, cy + 92, "струм біжить по колу — гальмує", size=12, color=FIELD, bold=True))
        else:
            # розірвані кінці
            out.append(line(cx - 30, cy, cx - 60, cy, color=MUTED, sw=2))
            out.append(line(cx + 30, cy, cx + 60, cy, color=MUTED, sw=2))
            out.append(text(cx - 70, cy + 4, "×", size=20, color=MUTED, anchor="end", bold=True))
            out.append(text(cx + 70, cy + 4, "×", size=20, color=MUTED, anchor="start", bold=True))
            out.append(text(cx, cy + 92, "від'єднано — крутиться вільно", size=12, color=MUTED, bold=True))
        out.append(text(x0 + 150, 290, desc, size=12, color=MUTED))
        return out

    f = [text(W / 2, 28, "Той самий міст уміє і зупиняти: гальмо проти вибігу", size=16, bold=True)]
    f += case(20, "Гальмо: обидва нижні ключі", True,
              "мотор закорочено сам на себе → різко стає")
    f += case(380, "Вибіг: усі ключі закрито", False,
              "мотор відпущено → котиться за інерцією")
    render(os.path.join(IMG, "brake-coast.svg"), W, H, *f)


# ── 5. ШІМ: шпаруватість задає середню швидкість ────────────────────────────
def fig_pwm_speed():
    W, H = 720, 360
    f = [text(W / 2, 30, "Швидкість — шпаруватістю ШІМ: мотор усереднює імпульси", size=16, bold=True)]

    def waveform(y0, duty, label, avg_label):
        baseY = y0 + 60
        topY = y0 + 12
        x0, x1 = 150, 600
        period = (x1 - x0) / 4.0
        out = [text(70, y0 + 38, label, size=13, bold=True, anchor="start")]
        # вісь
        out.append(line(x0, baseY, x1, baseY, color=MUTED, sw=1))
        # імпульси
        path = []
        x = x0
        for _ in range(4):
            on_w = period * duty
            # фронт угору
            path.append((x, baseY)); path.append((x, topY))
            path.append((x + on_w, topY)); path.append((x + on_w, baseY))
            path.append((x + period, baseY))
            x += period
        d = "M%.1f %.1f" % path[0] + "".join(" L%.1f %.1f" % p for p in path[1:])
        out.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d, INK))
        # рівень середнього (пунктир)
        avgY = baseY - (baseY - topY) * duty
        out.append(line(x0, avgY, x1, avgY, color=POS, sw=2, dash="6 5"))
        out.append(text(x1 + 8, avgY + 4, avg_label, size=12, color=POS, bold=True, anchor="start"))
        return out

    f += waveform(70, 0.8, "80 %\nувімкнено", "майже повна")
    f += waveform(210, 0.3, "30 %\nувімкнено", "повільно")
    f.append(text(W / 2, 348, "Та сама діагональ, лише «миготить»: довший імпульс → вища середня напруга → швидше",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "pwm-speed.svg"), W, H, *f)


if __name__ == "__main__":
    fig_why_driver()
    fig_one_switch()
    fig_direction()
    fig_brake_coast()
    fig_pwm_speed()
    print("Готово: 5 фігур у", IMG)

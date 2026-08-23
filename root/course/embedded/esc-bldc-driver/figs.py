# -*- coding: utf-8 -*-
"""Фігури до теми «Регулятор обертів (ESC)» (курс embedded/drony).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. ESC як коробка: одне число газу → три фази мотора ──────────────────────
def fig_blackbox():
    """Контролер дає ОДНЕ число (газ) тонким сигнальним проводом; ESC бере
    товсте живлення з батареї й перетворює його на ТРИ силові фази, перемикаючи
    їх у правильному порядку. Це і є робота ESC — між абстрактним числом і
    залізом мотора."""
    W, H = 820, 360
    f = [text(W / 2, 28, "ESC: одне число газу → три силові фази мотора", size=17, bold=True)]

    # — батарея (ліворуч, товсте живлення) —
    bx, by = 60, 150
    f.append(rect(bx, by, 90, 70, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(bx + 45, by + 30, "батарея", size=13, bold=True))
    f.append(text(bx + 45, by + 50, "+ / −", size=12, color=MUTED))
    # товсті силові дроти в ESC
    f.append(line(bx + 90, by + 22, 330, by + 22, color=POS, sw=6))
    f.append(line(bx + 90, by + 50, 330, by + 50, color=NEG, sw=6))
    f.append(text((bx + 90 + 330) / 2, by - 4, "товсте живлення (десятки А)", size=11, color=MUTED))

    # — контролер (зверху, тонкий сигнал) —
    fx, fy = 200, 40
    f.append(rect(fx, fy, 140, 46, fill="#eaf0fd", stroke=NEG, sw=2))
    f.append(text(fx + 70, fy + 20, "політний контролер", size=12, bold=True))
    f.append(text(fx + 70, fy + 37, "«газ = N»", size=12, color=NEG))
    # тонкий сигнальний провід вниз у ESC
    f.append(arrow(fx + 70, fy + 46, fx + 70, 150, color=NEG, sw=2))
    f.append(text(fx + 78, 120, "тонкий сигнал", size=11, color=MUTED, anchor="start"))

    # — ESC (центр) —
    ex, ey, ew, eh = 330, 110, 180, 150
    f.append(rect(ex, ey, ew, eh, fill="#eafaf1", stroke=FIELD, sw=2.5))
    f.append(text(ex + ew / 2, ey + 26, "ESC", size=16, bold=True, color=FIELD))
    f.append(fitbox(ex + 14, ey + 40, ew - 28, 92,
                    "транзистори-ключі\n+\nкомутація:\nяку фазу й коли\nживити",
                    size=12))

    # — три фази до мотора —
    mx, my = 660, 185
    phase_y = [150, 185, 220]
    cols = [POS, FIELD, NEG]
    names = ["A", "B", "C"]
    for yy, col, nm in zip(phase_y, cols, names):
        f.append(line(ex + ew, yy, mx - 30, yy, color=col, sw=5))
        f.append(text(ex + ew + 14, yy - 8, nm, size=12, bold=True, color=col, anchor="start"))
    f.append(text((ex + ew + mx) / 2, 135, "три фази", size=11, color=MUTED))

    # — мотор —
    f.append(circle(mx, my, 42, fill="#f4f6f8", stroke=LINE, sw=2.5))
    f.append(text(mx, my - 4, "BLDC", size=13, bold=True))
    f.append(text(mx, my + 14, "мотор", size=12, color=MUTED))
    # стрілка обертання
    f.append('<path d="M %.1f %.1f A 56 56 0 0 1 %.1f %.1f" fill="none" stroke="%s" stroke-width="2" marker-end="url(#arrow)"/>'
             % (mx + 56, my - 8, mx + 38, my - 44, MUTED))

    f.append(text(W / 2, 338,
                  "ESC бере просте число й товсту напругу — і сам вирішує, як перемикати фази, щоб мотор крутився.",
                  size=12, color=MUTED))
    render(os.path.join(IMG, 'blackbox.svg'), W, H, *f)


# ── 2. Дві мови газу: аналоговий PWM проти цифрового DShot ────────────────────
def fig_languages():
    """Угорі — старий аналоговий сигнал: ширина імпульсу 1000..2000 мкс несе газ,
    але дрижить від шуму й повільний. Унизу — цифровий кадр DShot: послідовність
    бітів із контрольною сумою, число доходить точно, ще й телеметрія назад."""
    W, H = 820, 430
    f = [text(W / 2, 28, "Дві мови газу: аналоговий PWM проти цифрового DShot", size=17, bold=True)]

    # === ВЕРХ: аналоговий PWM ===
    f.append(text(70, 66, "Аналоговий PWM (ширина імпульсу)", size=14, bold=True, color=NEG, anchor="start"))
    bx0, bx1, base = 70, 750, 150
    f.append(line(bx0, base, bx1, base, color=MUTED, sw=1))     # рівень 0
    # три імпульси різної ширини
    def pulse(x, w, label):
        out = [line(x, base, x, base - 50, color=NEG, sw=2.5),
               line(x, base - 50, x + w, base - 50, color=NEG, sw=2.5),
               line(x + w, base - 50, x + w, base, color=NEG, sw=2.5),
               text(x + w / 2, base + 16, label, size=11, color=MUTED)]
        return out
    f += pulse(110, 30, "1000 мкс (0%)")
    f += pulse(330, 55, "1500 мкс (50%)")
    f += pulse(560, 80, "2000 мкс (100%)")
    # «дрижання» — хвиляста підказка
    f.append(text(750, base - 58, "± шум, ~50 Гц", size=11, color=POS, anchor="end"))
    f.append(text(70, base + 40, "ширина = газ; аналогова, дрижить, повільне оновлення", size=11, color=MUTED, anchor="start"))

    # === НИЗ: цифровий DShot ===
    f.append(text(70, 250, "Цифровий DShot (кадр з бітів + контрольна сума)", size=14, bold=True, color=FIELD, anchor="start"))
    fy = 300
    # сегменти кадру: 11 біт газу | 1 біт телеметрії | 4 біти CRC
    segs = [(70, 360, "#eafaf1", FIELD, "11 біт: газ (0…2047)"),
            (430, 70, "#eaf0fd", NEG, "1 біт: телеметрія"),
            (500, 200, "#fdecea", POS, "4 біти: CRC (контроль)")]
    for x0, w, fill, stroke, cap in segs:
        f.append(rect(x0, fy, w, 44, fill=fill, stroke=stroke, sw=2))
        f.append(text(x0 + w / 2, fy + 27, cap, size=11, bold=True, color=stroke))
    f.append(text(70, fy - 8, "16 бітів = один кадр", size=11, color=MUTED, anchor="start"))
    # телеметрія назад тим самим проводом
    f.append(arrow(700, fy + 70, 70, fy + 70, color=FIELD, sw=2))
    f.append(text((70 + 700) / 2, fy + 88, "двосторонній DShot: оберти (eRPM) назад тим самим проводом",
                  size=11, color=FIELD))
    f.append(text(70, fy + 112, "число доходить точно; CRC ловить спотворення; жодного калібрування країв",
                  size=11, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'languages.svg'), W, H, *f)


# ── 3. Простір команди DShot: 0 / 1–47 / 48–2047 ─────────────────────────────
def fig_throttle_map():
    """Усі 2048 значень 11-бітного газу поділені на три зони: 0 — роззброєно
    (мотор стоїть), 1..47 — службові команди (біп, напрям, режими; лише на
    зупиненому моторі), 48..2047 — справжній газ (рівно 2000 кроків)."""
    W, H = 820, 300
    f = [text(W / 2, 28, "Простір команди DShot: одне число — три зони", size=17, bold=True)]

    bar_x, bar_y, bar_w, bar_h = 60, 110, 700, 64
    total = 2048.0
    # межі зон у частках
    zones = [
        (0, 1, "#fdecea", POS, "0", "роззброєно", "мотор стоїть"),
        (1, 48, "#eaf0fd", NEG, "1…47", "службові", "біп · напрям · режим"),
        (48, 2048, "#eafaf1", FIELD, "48…2047", "справжній газ", "рівно 2000 кроків"),
    ]
    for lo, hi, fill, stroke, rng, name, note in zones:
        x0 = bar_x + bar_w * lo / total
        x1 = bar_x + bar_w * hi / total
        w = max(x1 - x0, 3)
        f.append(rect(x0, bar_y, w, bar_h, fill=fill, stroke=stroke, sw=2, rx=4))
        cx = x0 + w / 2
        # зони 0 і 1..47 дуже вузькі — підписуємо знесено вгору з лінією-вказівкою
        if hi <= 48:
            ty = bar_y - 18 if lo == 0 else bar_y - 44
            f.append(line(cx, bar_y, cx, ty + 6, color=stroke, sw=1, dash="3 3"))
            f.append(text(cx, ty, rng, size=12, bold=True, color=stroke))
            side = "start" if lo == 0 else "middle"
            f.append(text(cx, ty - 16, name, size=11, color=stroke))
        else:
            f.append(text(cx, bar_y + 28, name, size=14, bold=True, color=stroke))
            f.append(text(cx, bar_y + 48, rng, size=12, color=stroke))
            f.append(text(cx, bar_y + bar_h + 22, note, size=11, color=MUTED))

    # підписи країв шкали
    f.append(text(bar_x, bar_y + bar_h + 22, "0", size=11, color=MUTED))
    f.append(text(bar_x + bar_w, bar_y + bar_h + 22, "2047", size=11, color=MUTED, anchor="end"))

    f.append(text(W / 2, 250,
                  "Службові команди (1…47) ESC слухає лише на зупиненому моторі — у польоті це завжди газ.",
                  size=12, color=MUTED))
    f.append(text(W / 2, 272,
                  "Зсув на 48 лишає окрему зону під команди, не крадучи в газу дозволу біля нуля.",
                  size=11, color=MUTED))
    render(os.path.join(IMG, 'throttle-map.svg'), W, H, *f)


# ── 4. Сходи протоколів: як тиснули аналоговий імпульс, доки не зламали стелю ──
def fig_protocol_ladder():
    """Хронологія мови газу очима того, ЩО несе число. PWM, OneShot125, OneShot42,
    Multishot — це той самий аналоговий імпульс, який лише дедалі коротшає (стеля
    точності лишається). DShot — стрибок убік: не коротший імпульс, а кадр із бітів
    із контрольною сумою. Показуємо, що перші чотири кроки — одна ідея на межі, а
    п'ятий — інша ідея без межі."""
    W, H = 860, 430
    f = [text(W / 2, 28, "Сходи протоколів ESC: чотири кроки тиснули імпульс — п'ятий змінив саму ідею",
              size=16, bold=True)]

    base = 250
    f.append(line(50, base, 810, base, color=MUTED, sw=1))

    # — аналогова родина: той самий імпульс, лише коротший —
    f.append(text(50, 70, "Аналоговий імпульс: газ = тривалість", size=13, bold=True, color=NEG, anchor="start"))
    f.append(text(50, 88, "коротшає рік за роком, але «де точно край» лишається на око — стеля точності",
                  size=11, color=MUTED, anchor="start"))

    # чотири стовпчики-імпульси, що звужуються
    analog = [
        (110, 150, "PWM",        "~2009", "1000…2000 мкс"),
        (260, 70,  "OneShot125", "2015",  "125…250 мкс"),
        (400, 32,  "OneShot42",  "2015",  "42…84 мкс"),
        (520, 18,  "Multishot",  "2016",  "5…25 мкс"),
    ]
    for x, w, name, year, span in analog:
        f.append(rect(x, base - 60, max(w, 4), 60, fill="#eaf0fd", stroke=NEG, sw=2, rx=2))
        f.append(text(x + max(w, 4) / 2 if w > 40 else x + 2, base - 70, name,
                      size=12, bold=True, color=NEG,
                      anchor="middle" if w > 40 else "start"))
        f.append(text(x + max(w, 4) / 2 if w > 40 else x + 2, base + 16, year,
                      size=11, color=MUTED,
                      anchor="middle" if w > 40 else "start"))
        f.append(text(x + max(w, 4) / 2 if w > 40 else x + 2, base + 30, span,
                      size=10, color=MUTED,
                      anchor="middle" if w > 40 else "start"))

    # стрілка «коротшає» над аналоговими
    f.append(arrow(120, 120, 540, 120, color=MUTED, sw=1.5))
    f.append(text(330, 112, "той самий імпульс, лише дедалі коротший", size=11, color=MUTED))

    # — стрибок убік: DShot —
    jx = 640
    f.append('<path d="M 560 %.1f Q 600 %.1f 630 %.1f" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#arrow)"/>'
             % (base - 30, base - 90, base - 40, FIELD))
    f.append(text(600, base - 96, "стрибок убік", size=11, bold=True, color=FIELD))

    # кадр із бітів (а не імпульс)
    bitx, bitw, bn = jx, 150, 8
    for i in range(bn):
        on = i in (0, 2, 3, 6)
        f.append(rect(bitx + i * (bitw / bn), base - 48, bitw / bn - 2, 30,
                      fill="#eafaf1" if on else BG, stroke=FIELD, sw=1.5, rx=1))
    f.append(text(bitx + bitw / 2, base - 60, "DShot", size=13, bold=True, color=FIELD))
    f.append(text(bitx + bitw / 2, base + 16, "2016", size=11, color=MUTED))
    f.append(text(bitx + bitw / 2, base + 30, "кадр із бітів + CRC", size=10, color=FIELD))

    f.append(text(jx + bitw / 2, base - 86, "не коротший імпульс —", size=11, color=FIELD))

    # нижній висновок
    f.append(textbox(W / 2, 360,
                     "Перші чотири — одна ідея (коротший аналоговий імпульс) на межі точності.\n"
                     "DShot — інша ідея: число їде бітами з контрольною сумою, тож стелі точності більше нема.",
                     size=12, pad=12, fill="#f7faf8", stroke=FIELD, sw=1.5)[0])
    render(os.path.join(IMG, 'protocol-ladder.svg'), W, H, *f)


if __name__ == "__main__":
    fig_blackbox()
    fig_languages()
    fig_throttle_map()
    fig_protocol_ladder()
    print("OK: blackbox, languages, throttle-map, protocol-ladder ->", IMG)

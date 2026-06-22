# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── no-overwrite: чому не можна писати прошивку поверх себе ────────────────────
# Ідея: робочий слот виконується ЗАРАЗ; писати в нього нове = впасти посеред
# власного кроку. Звідси потреба у другому місці.
def fig_no_overwrite():
    W, H = 720, 300
    p = []
    cx, cy = W / 2, 130
    core, cw, ch = textbox(cx, cy, "поточна прошивка\n▶ виконується зараз",
                           size=13, bold=True, color=FIELD, fill="#eafaf0", stroke=FIELD, sw=2, pad=16)
    p.append(core)

    # стрілка «пишемо нове» врізається в робочий слот
    p.append(arrow(110, cy, cx - cw / 2 - 4, cy, color=POS, sw=2.4))
    p.append(text(110, cy - 16, "пишемо нове", size=11, color=POS, bold=True, anchor="middle"))

    # результат — «цеглина»
    p.append(text(cx + cw / 2 + 60, cy + 9, "✗", size=30, color=POS, bold=True))
    p.append(text(cx + cw / 2 + 60, cy + 40, "«цеглина»", size=11, color=POS, bold=True))

    p.append(fitbox(70, 214, W - 140, 60,
                    "Потрібне ДРУГЕ місце: писати новий образ туди,\nне чіпаючи того, що зараз працює.",
                    size=12, fill="#fdf6e3", stroke=MUTED, sw=1.4, bold=True))

    render(os.path.join(OUT, "no-overwrite.svg"), W, H, *p,
           title="Чому прошивку не можна писати поверх себе")


# ── two-slots: ota_0 працює, ota_1 вільний — пишемо в нього ───────────────────
def fig_two_slots():
    W, H = 720, 290
    p = []
    y, bw, bh = 100, 250, 104

    work, _, _ = textbox(70 + bw / 2, y + bh / 2, "ota_0\nПРАЦЮЄ зараз\nнедоторканий",
                         size=12, bold=True, color=FIELD, fill="#eafaf0", stroke=FIELD, sw=2.2, min_w=bw)
    p.append(work)

    fx = W - 70 - bw
    free = rect(fx, y, bw, bh, fill="#eaf0fd", stroke=NEG, sw=2.2, rx=10)
    free = free.replace('stroke-width="2.2"', 'stroke-width="2.2" stroke-dasharray="7 5"')
    p.append(free)
    p.append(mtext(fx + bw / 2, y + bh / 2 - 10, ["ota_1", "вільний слот", "сюди новий образ"],
                   size=12, color=NEG, bold=True))

    p.append(arrow(70 + bw + 6, y + bh / 2, fx - 6, y + bh / 2, color=NEG, sw=2.4))
    p.append(text((70 + bw + fx) / 2, y + bh / 2 - 12, "новий", size=10, color=NEG))

    p.append(text(W / 2, y + bh + 44,
                  "Поки пишемо в ota_1, ota_0 спокійно виконується далі —",
                  size=12, color=INK, bold=True))
    p.append(text(W / 2, y + bh + 64,
                  "збій під час запису не чіпає робочої прошивки.",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "two-slots.svg"), W, H, *p,
           title="Два слоти для прошивки: ota_0 і ota_1")


# ── otadata: крихітний перемикач завантаження ─────────────────────────────────
def fig_otadata():
    W, H = 740, 320
    p = []
    y = 120
    b1, w1, h1 = textbox(130, y, "завантажувач", size=12, bold=True, color=NEG,
                         fill="#eaf0fd", stroke=NEG, sw=1.8)
    p.append(b1)
    p.append(arrow(130 + w1 / 2, y, 300, y, color=MUTED, sw=2))

    b2, w2, h2 = textbox(370, y, "otadata\n«старт зі слота 1»", size=11, bold=True,
                         color="#8a6d1a", fill="#fdf6e3", stroke="#caa24a", sw=1.8)
    p.append(b2)
    p.append(arrow(370 + w2 / 2, y, 560, y, color=MUTED, sw=2))

    b3, w3, h3 = textbox(620, y, "ota_1\nновий образ", size=12, bold=True, color=FIELD,
                         fill="#eafaf0", stroke=FIELD, sw=1.8)
    p.append(b3)

    p.append(fitbox(80, 200, W - 160, 96,
                    "Порядок незмінний:\n"
                    "1) записати новий образ у вільний слот ПОВНІСТЮ;  2) перевірити його;\n"
                    "3) аж тоді перемкнути otadata на цей слот — одним коротким кроком.",
                    size=11, fill="#fbfbfb", stroke=MUTED, sw=1.4))
    p.append(text(W / 2, 286, "Збій до кроку 3 → стартує старий слот; після → новий. Без «напівоновлення».",
                  size=10.5, color=FIELD, bold=True))

    render(os.path.join(OUT, "otadata.svg"), W, H, *p,
           title="Перемикач завантаження: крихітна otadata")


# ── trial-rollback: пробний запуск і відкат ───────────────────────────────────
def fig_trial_rollback():
    W, H = 740, 330
    p = []
    top, tw, th = textbox(W / 2, 100, "новий образ\nстартує (пробний)", size=12, bold=True,
                          color=NEG, fill="#eaf0fd", stroke=NEG, sw=1.8)
    p.append(top)

    # ліва гілка — успіх
    p.append(line(W / 2 - 30, 100 + th / 2, 230, 214, color=FIELD, sw=2.2))
    p.append(fitbox(60, 214, 320, 92,
                    "працює й каже «я в нормі»\notadata закріплює новий слот\n✓ оновлення вдалося",
                    size=11, fill="#eafaf0", stroke=FIELD, sw=1.8, color=FIELD, bold=True))

    # права гілка — відкат
    p.append(line(W / 2 + 30, 100 + th / 2, W - 230, 214, color="#caa24a", sw=2.2))
    p.append(fitbox(W - 380, 214, 320, 92,
                    "падає / зациклюється / мовчить\nзавантажувач вертає старий слот\n✓ відкат — пристрій живий",
                    size=11, fill="#fdf6e3", stroke="#caa24a", sw=1.8, color="#8a6d1a", bold=True))

    render(os.path.join(OUT, "trial-rollback.svg"), W, H, *p,
           title="Перше вмикання: випробування й відкат")


# ── cost: ціна — половина місця під код ───────────────────────────────────────
def fig_cost():
    W, H = 740, 280
    p = []
    bx, by, bw, bh = 90, 120, W - 180, 56
    p.append(text(bx, by - 14, "область під код:", size=11, color=INK, anchor="start", bold=True))
    half = bw / 2
    p.append(rect(bx, by, half, bh, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(bx + half / 2, by + bh / 2 + 4, "ota_0  (половина)", size=11.5, color=FIELD, bold=True))
    p.append(rect(bx + half, by, half, bh, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=6))
    p.append(text(bx + half + half / 2, by + bh / 2 + 4, "ota_1  (половина)", size=11.5, color=NEG, bold=True))

    p.append(fitbox(bx, 206, bw, 58,
                    "За надійне оновлення платять половиною місця під код.\n"
                    "Тому, плануючи Flash, одразу закладайте місце під ДВА образи.",
                    size=11, fill="#fbfbfb", stroke=MUTED, sw=1.4))

    render(os.path.join(OUT, "cost.svg"), W, H, *p,
           title="Ціна безпечних оновлень: місце")


# ── same-idea: той самий прийом у двох масштабах ──────────────────────────────
def fig_same_idea():
    W, H = 740, 300
    p = []
    p.append(rect(60, 76, W - 120, 70, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=10))
    p.append(text(84, 106, "Конфіг:", size=12, color=FIELD, anchor="start", bold=True))
    p.append(text(84, 128, "два маленькі слоти + перемикач (номер версії)",
                  size=10.5, color=INK, anchor="start"))

    p.append(rect(60, 158, W - 120, 70, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=10))
    p.append(text(84, 188, "Прошивка:", size=12, color=NEG, anchor="start", bold=True))
    p.append(text(84, 210, "два великі слоти + перемикач (otadata)",
                  size=10.5, color=INK, anchor="start"))

    p.append(text(W / 2, 264,
                  "Один прийом: пиши нове поряд → перемкни одним кроком → май запас на відкат.",
                  size=11, color=INK, bold=True))

    render(os.path.join(OUT, "same-idea.svg"), W, H, *p,
           title="Та сама ідея, інший масштаб")


if __name__ == "__main__":
    fig_no_overwrite()
    fig_two_slots()
    fig_otadata()
    fig_trial_rollback()
    fig_cost()
    fig_same_idea()
    print("OK: figures written to", OUT)

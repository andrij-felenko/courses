# -*- coding: utf-8 -*-
"""Фігури до теми «Оновлення прошивки через ефір (OTA)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Один слот: збій посеред заливки лишає «цеглину» ───────────────────────
def fig_brick_risk():
    W, H = 780, 430
    f = [text(W / 2, 28, "Один слот: новий образ пишуть поверх робочого — і ризикують усім",
              size=16, bold=True)]

    # три фази зліва направо
    cx = [150, 390, 630]
    fy = 150
    fw, fh = 130, 120

    # --- Фаза 1: робоча прошивка ---
    f.append(text(cx[0], 78, "До оновлення", size=13, bold=True, color=MUTED))
    f.append(fitbox(cx[0] - fw / 2, fy, fw, fh, "РОБОЧА\nпрошивка\n(ціла)",
                    size=13, fill="#eef7f0", stroke=FIELD, bold=True))
    f.append(text(cx[0], fy + fh + 26, "пристрій працює", size=11.5, color=FIELD))

    # стрілка
    f.append(arrow(cx[0] + fw / 2 + 6, fy + fh / 2, cx[1] - fw / 2 - 6, fy + fh / 2))
    f.append(text((cx[0] + cx[1]) / 2, fy + fh / 2 - 12, "пишемо", size=11, color=MUTED))
    f.append(text((cx[0] + cx[1]) / 2, fy + fh / 2 + 22, "поверх", size=11, color=MUTED))

    # --- Фаза 2: запис поверх (небезпечне вікно) ---
    f.append(text(cx[1], 78, "Під час заливки", size=13, bold=True, color=POS))
    # половина нового зверху, половина старого знизу
    half = fh / 2
    f.append(rect(cx[1] - fw / 2, fy, fw, half, fill="#fdecea", stroke=POS, sw=1.8, rx=0))
    f.append(text(cx[1], fy + half / 2 + 4, "нове", size=12, color=POS, bold=True))
    f.append(rect(cx[1] - fw / 2, fy + half, fw, half, fill="#eef2f7", stroke=MUTED, sw=1.5, rx=0))
    f.append(text(cx[1], fy + half + half / 2 + 4, "старе", size=12, color=MUTED))
    f.append(text(cx[1], fy - 6, "⚡ збій тут!", size=12, color=POS, bold=True))
    for dx in (-30, -10, 10, 30):
        f.append(line(cx[1] + dx, fy + half - 9, cx[1] + dx, fy + half + 9, color=POS, sw=1.4, dash="2,2"))

    # стрілка
    f.append(arrow(cx[1] + fw / 2 + 6, fy + fh / 2, cx[2] - fw / 2 - 6, fy + fh / 2))
    f.append(text((cx[1] + cx[2]) / 2, fy + fh / 2 - 12, "обрив", size=11, color=POS))

    # --- Фаза 3: цеглина ---
    f.append(text(cx[2], 78, "Після збою", size=13, bold=True, color=POS))
    f.append(fitbox(cx[2] - fw / 2, fy, fw, fh, "напівстара-\nнапівнова\nЦЕГЛИНА",
                    size=13, fill="#fdecea", stroke=POS, bold=True))
    f.append(text(cx[2], fy + fh + 26, "не завантажиться", size=11.5, color=POS, bold=True))

    box = fitbox(90, 320, 600, 78, [
                 "З єдиним слотом новий образ пишуть прямо поверх робочого. Доїде цілим —",
                 "пощастило. Та якщо мережа чи живлення обірвуться на півдорозі, у єдиному",
                 "слоті лишиться напівстара-напівнова прошивка — і пристрій уже не оживе.",
                 "Це і є «цеглина»: ось чому одного слота для безпечного OTA замало."],
                 size=12.5, fill="#fdecea", stroke=POS)
    f.append(box)
    render(os.path.join(IMG, "brick-risk.svg"), W, H, *f)


# ── 2. Дві банки A/B: працюємо з однієї, пишемо в другу, перемикаємось ───────
def fig_ab_banks():
    W, H = 780, 450
    f = [text(W / 2, 28, "Дві банки: робочу не чіпаємо, новий образ ллємо в запасну",
              size=16, bold=True)]

    bw, bh = 150, 150
    ax, bx = 180, 600           # центри банок A і B
    by = 130

    # --- Банка A: робоча ---
    f.append(fitbox(ax - bw / 2, by, bw, bh, "Слот A\n(РОБОЧИЙ)\n\nстара,\nробоча\nпрошивка",
                    size=13, fill="#eef7f0", stroke=FIELD, bold=False))
    f.append(text(ax, by - 12, "звідси виконуємось", size=12, color=FIELD, bold=True))

    # --- Банка B: запасна → новий образ ---
    f.append(fitbox(bx - bw / 2, by, bw, bh, "Слот B\n(ЗАПАСНИЙ)\n\nсюди пишемо\nновий\nобраз",
                    size=13, fill="#fdecea", stroke=POS, bold=False))
    f.append(text(bx, by - 12, "сюди ллємо нове", size=12, color=POS, bold=True))

    # стрілка заливки в B (зверху)
    f.append(arrow(bx, 70, bx, by - 24, color=POS))
    f.append(text(bx + 80, 92, "образ із мережі", size=11, color=POS, anchor="middle"))

    # перемикач otadata між банками (унизу)
    sw_y = by + bh + 48
    sb = textbox((ax + bx) / 2, sw_y, "перемикач  (otadata)", size=12.5,
                 fill="#fff7e6", stroke="#e67e22", bold=True)
    f.append(sb[0])
    # лінії від банок до перемикача
    f.append(line(ax, by + bh, ax, sw_y, color=MUTED, sw=1.2, dash="3,3"))
    f.append(line(bx, by + bh, bx, sw_y, color=MUTED, sw=1.2, dash="3,3"))
    # стрілка перемикання A→B після перевірки
    f.append(arrow(ax + 20, sw_y, bx - sb[1] / 2 - 6, sw_y, color="#e67e22"))
    f.append(text((ax + bx) / 2, sw_y + 40, "1 короткий крок: «завантажуйся з B»",
                  size=11.5, color="#e67e22", bold=True))
    f.append(text((ax + bx) / 2, sw_y + 58, "тільки ПІСЛЯ повного запису й перевірки",
                  size=11, color=MUTED))

    box = fitbox(90, 388, 600, 50, [
                 "Той, що пишемо, і той, що виконуємо, — завжди різні. Ризикуємо лише запасним",
                 "слотом; робочий цілий до останньої миті. Наступного разу ролі поміняються."],
                 size=12.5, fill="#f4f6f8")
    f.append(box)
    render(os.path.join(IMG, "ab-banks.svg"), W, H, *f)


# ── 3. Потік OTA: сервер → крихітний буфер RAM → запасний слот Flash ─────────
def fig_ota_flow():
    W, H = 800, 470
    f = [text(W / 2, 28, "Образ тече з сервера шматками крізь крихітний буфер у Flash",
              size=16, bold=True)]

    midy = 150

    # --- Сервер ---
    srv = fitbox(40, midy - 55, 150, 110, "СЕРВЕР\n\nобраз\n+ сума\n+ підпис",
                 size=12.5, fill="#eef2f7", stroke=NEG, bold=False)
    f.append(srv)
    f.append(text(115, midy - 70, "хмара", size=11, color=MUTED))

    # стрілка «питаємо / приймаємо шматками»
    f.append(arrow(192, midy, 300, midy, color=NEG))
    f.append(text(246, midy - 24, "«чи є новіше?»", size=11, color=NEG))
    f.append(text(246, midy + 22, "шматок за шматком", size=11, color=NEG))

    # --- Буфер RAM (крихітний) ---
    rb_w, rb_h = 110, 60
    f.append(rect(302, midy - rb_h / 2, rb_w, rb_h, fill="#fff7e6", stroke="#e67e22", sw=1.8))
    f.append(text(302 + rb_w / 2, midy + 4, "буфер RAM", size=12, color="#e67e22", bold=True))
    f.append(text(302 + rb_w / 2, midy - rb_h / 2 - 10, "крихітний (1 КБ)", size=10.5, color=MUTED))
    f.append(text(302 + rb_w / 2, midy + rb_h / 2 + 18, "весь образ НЕ влазить", size=10.5, color=POS))

    # стрілка буфер → Flash
    f.append(arrow(302 + rb_w + 4, midy, 470, midy, color="#e67e22"))
    f.append(text((302 + rb_w + 470) / 2 + 4, midy - 14, "пишемо", size=11, color="#e67e22"))

    # --- Flash: два слоти ---
    fx = 474
    sl_w, sl_h = 150, 56
    f.append(text(fx + sl_w / 2, midy - 78, "Flash", size=12, bold=True, color=MUTED))
    # робочий слот
    f.append(rect(fx, midy - 62, sl_w, sl_h, fill="#eef7f0", stroke=FIELD, sw=1.6))
    f.append(text(fx + sl_w / 2, midy - 30, "слот A — робочий", size=11.5, color=FIELD, bold=True))
    # запасний слот (туди тече образ)
    f.append(rect(fx, midy + 8, sl_w, sl_h, fill="#fdecea", stroke=POS, sw=1.8))
    f.append(text(fx + sl_w / 2, midy + 34, "слот B ← новий образ", size=11.5, color=POS, bold=True))
    # підвести стрілку саме до B
    f.append(line(470, midy, 470, midy + 34, color="#e67e22", sw=1.6))
    f.append(line(470, midy + 34, fx - 2, midy + 34, color="#e67e22", sw=1.6))

    # --- Наприкінці: перевірка → перемикач ---
    chk = fitbox(fx - 6, midy + 96, sl_w + 12, 64,
                 "наприкінці:\nсума + підпис →\nперемкнути слот",
                 size=11.5, fill="#fff7e6", stroke="#e67e22", bold=False)
    f.append(chk)
    f.append(arrow(fx + sl_w / 2, midy + 64, fx + sl_w / 2, midy + 94, color="#e67e22"))

    box = fitbox(70, 360, 660, 90, [
                 "Образ прошивки — сотні кілобайтів чи мегабайти, а RAM мікроконтролера — лічені",
                 "десятки кілобайтів: увесь образ у пам'ять не влазить. Тому OTA йде потоком —",
                 "кожен кусень проходить крізь крихітний буфер RAM прямо в запасний слот Flash,",
                 "буфер звільняється, і так увесь образ. Перевірка цілості й підпису — ПЕРЕД",
                 "перемиканням, тож робочий слот лишається цілим до самого кінця."],
                 size=12.5, fill="#f4f6f8")
    f.append(box)
    render(os.path.join(IMG, "ota-flow.svg"), W, H, *f)


# ── 4. Пробний запуск і відкат ──────────────────────────────────────────────
def fig_trial_rollback():
    W, H = 780, 440
    f = [text(W / 2, 28, "Новий образ — на випробуванні: підтвердив себе чи відкіт",
              size=16, bold=True)]

    # старт: перемкнулись на новий образ
    start = textbox(W / 2, 80, "перемкнулись на новий образ → пробний запуск",
                    size=13, fill="#fff7e6", stroke="#e67e22", bold=True)
    f.append(start[0])

    # розгалуження
    f.append(arrow(W / 2 - 120, 100, 240, 150, color=FIELD))
    f.append(arrow(W / 2 + 120, 100, 540, 150, color=POS))

    # --- Гілка успіху ---
    f.append(fitbox(150, 158, 180, 70, "образ піднявся,\nголовне працює →\n«я СПРАВНИЙ»",
                    size=12, fill="#eef7f0", stroke=FIELD, bold=False))
    f.append(arrow(240, 230, 240, 268, color=FIELD))
    f.append(fitbox(150, 272, 180, 64, "перемикач\nЗАКРІПЛЕНО →\nоновлення вдалося",
                    size=12, fill="#eef7f0", stroke=FIELD, bold=True))

    # --- Гілка невдачі ---
    f.append(fitbox(450, 158, 180, 70, "образ упав / завис /\nмовчить кілька\nспроб поспіль",
                    size=12, fill="#fdecea", stroke=POS, bold=False))
    f.append(arrow(540, 230, 540, 268, color=POS))
    f.append(fitbox(450, 272, 180, 64, "ВІДКАТ на старий,\nробочий слот →\nпристрій живий",
                    size=12, fill="#fdecea", stroke=POS, bold=True))

    box = fitbox(90, 360, 600, 72, [
                 "Образ може доїхати ЦІЛИМ як файл, але бути ПОГАНИМ як програма — з помилкою",
                 "в коді. Перевірка цілості тут безсила. Тому новий код стартує «на випробуванні»",
                 "й мусить САМ себе підтвердити; не підтвердив — завантажувач відкочується на",
                 "старий, перевірений слот. Забути виклик «я справний» — пастка: відкотить і добру."],
                 size=12.5, fill="#f4f6f8")
    f.append(box)
    render(os.path.join(IMG, "trial-rollback.svg"), W, H, *f)


# ── 5. Цифровий підпис: пристрій бере лише свою прошивку ─────────────────────
def fig_signature():
    W, H = 790, 450
    f = [text(W / 2, 28, "Підпис: пристрій запускає лише прошивку, підписану своїм ключем",
              size=16, bold=True)]

    # --- Виробник підписує ---
    f.append(text(160, 70, "Виробник", size=13, bold=True, color=NEG))
    f.append(fitbox(80, 92, 160, 56, "образ\n+ ТАЄМНИЙ ключ", size=12,
                    fill="#eef2f7", stroke=NEG, bold=False))
    f.append(arrow(160, 150, 160, 184, color=NEG))
    f.append(fitbox(80, 188, 160, 50, "образ + ПІДПИС", size=12,
                    fill="#eef2f7", stroke=NEG, bold=True))

    # стрілка доставки (захищеним каналом)
    f.append(arrow(244, 213, 360, 213, color=MUTED))
    f.append(text(302, 198, "захищений", size=10.5, color=MUTED))
    f.append(text(302, 230, "канал (TLS)", size=10.5, color=MUTED))

    # --- Пристрій перевіряє ---
    f.append(text(560, 70, "Пристрій", size=13, bold=True, color=INK))
    f.append(fitbox(480, 92, 200, 56, "ВІДКРИТИЙ ключ\n(зашитий у пристрій)", size=12,
                    fill="#f4f6f8", stroke=INK, bold=False))
    # вузол перевірки
    chk = textbox(560, 213, "перевірити підпис", size=12.5,
                  fill="#fff7e6", stroke="#e67e22", bold=True)
    f.append(chk[0])
    f.append(arrow(560, 150, 560, 196, color=INK))   # ключ → перевірка
    f.append(line(360, 213, 560 - chk[1] / 2 - 4, 213, color=MUTED, sw=1.5))  # образ → перевірка

    # два виходи перевірки
    f.append(arrow(540, 232, 470, 292, color=FIELD))
    f.append(arrow(580, 232, 660, 292, color=POS))
    f.append(fitbox(380, 296, 180, 56, "підпис сходиться →\nЗАПУСТИТИ", size=12,
                    fill="#eef7f0", stroke=FIELD, bold=True))
    f.append(fitbox(600, 296, 170, 56, "чужий / підмінений →\nВІДКИНУТИ", size=12,
                    fill="#fdecea", stroke=POS, bold=True))

    box = fitbox(90, 372, 610, 64, [
                 "Контрольна сума ловить ВИПАДКОВЕ псування, та безсила проти зловмисника: він",
                 "перерахував би й суму. Підпис — інший рубіж: виробник підписує образ таємним",
                 "ключем, пристрій перевіряє відкритим. Чужа чи підмінена прошивка підпис не",
                 "пройде, хоч би якою цілою доїхала. OTA без перевірки підпису — двері без замка."],
                 size=12.5, fill="#f4f6f8")
    f.append(box)
    render(os.path.join(IMG, "signature.svg"), W, H, *f)


if __name__ == "__main__":
    fig_brick_risk()
    fig_ab_banks()
    fig_ota_flow()
    fig_trial_rollback()
    fig_signature()
    print("OK: figures written to", IMG)

# -*- coding: utf-8 -*-
# Фігури ДЕТАЛЬНОЇ статті «Заводське прошивання й провізіонування».
# Окремий файл, щоб не чіпати базовий figs.py; вивід у той самий ./img/.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

BROWN = "#b07a35"
PURPLE = "#8e44ad"


# ── Фігура D1: бюджет такту станції — де осідає час на одну плату ─────────────
def fig_cycle_budget():
    W, H = 860, 430
    f = [text(W / 2, 30, "Такт станції: із чого складається час на ОДНУ плату",
              size=15, bold=True)]

    # горизонтальна смуга часу, поділена на фази (px пропорційні секундам)
    x0, y0 = 60, 92
    bar_h = 54
    # (назва, секунди, колір, підпис-примітка)
    phases = [
        ("завести\nплату", 3, MUTED, "оператор кладе,\nголки притискаються"),
        ("прошити\nобраз", 12, POS, "вузьке місце —\nросте з розміру .bin"),
        ("записати\nособистість", 2, NEG, "серійник, MAC,\nкалібр. у розділ"),
        ("звірити +\nсамотест", 6, FIELD, "прочитати назад,\nдати платі стартувати"),
        ("пропалити\neFuse", 2, BROWN, "необоротно,\nв останню чергу"),
    ]
    total_s = sum(p[1] for p in phases)
    scale = (W - 2 * x0) / total_s
    x = x0
    for name, sec, col, note in phases:
        w = sec * scale
        f.append(rect(x, y0, w, bar_h, fill="#fbfbfb", stroke=col, sw=1.8))
        f.append(mtext(x + w / 2, y0 + bar_h / 2 - 5, name, size=10.5, color=col, bold=True))
        f.append(text(x + w / 2, y0 + bar_h / 2 + 18, "%d с" % sec, size=10, color=MUTED))
        # підпис-примітка під смугою, з запасом по висоті
        f.append(mtext(x + w / 2, y0 + bar_h + 22, note, size=9, color=MUTED, lh=1.25))
        x += w
    # підсумкова дужка «такт»
    by = y0 - 16
    f.append(line(x0, by, x0 + total_s * scale, by, color=INK, sw=1.4))
    f.append(line(x0, by, x0, by + 6, color=INK, sw=1.4))
    f.append(line(x0 + total_s * scale, by, x0 + total_s * scale, by + 6, color=INK, sw=1.4))
    f.append(text((x0 + x0 + total_s * scale) / 2, by - 6,
                  "такт ≈ %d с на плату" % total_s, size=12, color=INK, bold=True))

    # три висновки-рамки внизу
    ry = 300
    rw = (W - 2 * x0 - 2 * 20) / 3
    f.append(fitbox(x0, ry, rw, 96,
                    "ПРОПУСКНА ЗДАТНІСТЬ\n3600 с/год ÷ такт\n= 3600 ÷ 25 ≈ 144\nплати за годину\nз ОДНІЄЇ голови",
                    size=10.5, color=INK, fill="#eef2f7", stroke=INK, sw=1.5))
    f.append(fitbox(x0 + rw + 20, ry, rw, 96,
                    "ВУЗЬКЕ МІСЦЕ — прошивка.\nПодвоївся розмір образу —\nподвоївся найдовший\nстовпчик, а з ним і такт.\nОсь чому образ тиснуть.",
                    size=10.5, color=POS, fill="#fdecea", stroke=POS, sw=1.5))
    f.append(fitbox(x0 + 2 * (rw + 20), ry, rw, 96,
                    "ПАРАЛЕЛЬ рятує: N голів\nшиють N плат заразом,\nтакт той самий, а плат/год\n× N. Тому станції\nроблять багатоголовими.",
                    size=10.5, color=FIELD, fill="#eafaf1", stroke=FIELD, sw=1.5))
    render(os.path.join(OUT, 'cycle-budget.svg'), W, H, *f)


# ── Фігура D2: розподіл серійників — резервуй ПЕРЕД записом, підтверджуй ПІСЛЯ ─
def fig_serial_allocation():
    W, H = 840, 440
    f = [text(W / 2, 30, "Серійник — спільний лічильник: як його не роздвоїти й не втратити",
              size=15, bold=True)]

    # дві колонки: НАЇВНО (ліворуч, ламається) і ПРАВИЛЬНО (праворуч)
    colw = 360
    xL, xR = 40, 440
    ytop = 72

    def stepbox(x, y, s, col, fill):
        f.append(fitbox(x, y, colw, 40, s, size=11, color=col, fill=fill, stroke=col, sw=1.5, bold=True))

    # ── ліва колонка: наївно «взяв → записав → інкремент» ──
    f.append(text(xL + colw / 2, ytop - 8, "НАЇВНО: інкремент ПІСЛЯ запису", size=12, bold=True, color=POS))
    y = ytop + 8
    stepbox(xL, y, "1. взяти лічильник N = 42", INK, "#eef2f7"); a1 = y + 40
    y = a1 + 24; stepbox(xL, y, "2. зашити 42 в плату…", INK, "#eef2f7"); a2 = y + 40
    y = a2 + 24
    f.append(fitbox(xL, y, colw, 46, "✗ ЖИВЛЕННЯ СТАНЦІЇ МОРГНУЛО\nдо кроку «інкремент»",
                    size=11, color=POS, fill="#fdecea", stroke=POS, sw=1.7, bold=True)); a3 = y + 46
    y = a3 + 24; stepbox(xL, y, "3. інкремент N так і не стався", MUTED, "#f4f6f8"); a4 = y + 40
    y = a4 + 22
    f.append(fitbox(xL, y, colw, 52, "НАСЛІДОК: наступна плата теж дістане 42 →\nДВА вироби з одним серійником у полі",
                    size=10.5, color=POS, fill="#fdecea", stroke=POS, sw=1.6, bold=True))
    for (yy1, yy2) in ((a1, a1 + 24), (a2, a2 + 24), (a3, a3 + 24)):
        f.append(arrow(xL + colw / 2, yy1, xL + colw / 2, yy2, color=POS, sw=1.5))

    # ── права колонка: резервуй ДО, підтверджуй ПІСЛЯ ──
    f.append(text(xR + colw / 2, ytop - 8, "ПРАВИЛЬНО: резервуй ДО, підтверджуй ПІСЛЯ", size=12, bold=True, color=FIELD))
    y = ytop + 8
    stepbox(xR, y, "1. атомарно ЗАРЕЗЕРВУВАТИ N=42\n   (запис у БД: 42 = «видано, в роботі»)", NEG, "#eaf0fd"); b1 = y + 44
    y = b1 + 20; stepbox(xR, y, "2. зашити 42, прочитати назад, самотест", INK, "#eef2f7"); b2 = y + 44
    y = b2 + 20
    f.append(fitbox(xR, y, colw, 46, "✓ усе зійшлося → ПІДТВЕРДИТИ 42\n(у БД: 42 = «народжено», дата, партія)",
                    size=11, color=FIELD, fill="#eafaf1", stroke=FIELD, sw=1.7, bold=True)); b3 = y + 46
    y = b3 + 20
    f.append(fitbox(xR, y, colw, 66,
                    "збій до підтвердження? 42 лишиться «в роботі» —\nйого НЕ віддадуть іншій платі (пропуск краще,\nніж дублікат). Лічильник монотонний, дублів нема.",
                    size=10, color=NEG, fill="#eaf0fd", stroke=NEG, sw=1.6))
    for (yy1, yy2) in ((b1, b1 + 20), (b2, b2 + 20)):
        f.append(arrow(xR + colw / 2, yy1, xR + colw / 2, yy2, color=FIELD, sw=1.5))

    render(os.path.join(OUT, 'serial-allocation.svg'), W, H, *f)


# ── Фігура D3: ланцюг довіри — де народжується ключ і чому не в руках CM ───────
def fig_key_ceremony():
    W, H = 860, 470
    f = [text(W / 2, 30, "Де народжується секрет: ланцюг довіри й недовірений завод",
              size=15, bold=True)]

    # ── верх: приватний ключ НІКОЛИ не покидає чип (генерація на борту) ──
    f.append(text(W / 2, 58, "Задум: приватний ключ народжується В ЧИПІ й НІКОЛИ його не покидає",
                  size=12, bold=True, color=FIELD))

    # чип (ліворуч) і ЦС/HSM (праворуч) на одному рівні, з широким проміжком під підписи стрілок
    bw, bh = 176, 100
    cy = 150
    cx_box = 56          # лівий край чипа
    hx_box = W - 56 - bw # лівий край ЦС
    ccx = cx_box + bw / 2
    hcx = hx_box + bw / 2

    f.append(rect(cx_box, cy, bw, bh, fill="#eafaf1", stroke=FIELD, sw=2))
    f.append(text(ccx, cy + 22, "ЧИП на платі", size=12, bold=True, color=FIELD))
    f.append(mtext(ccx, cy + 44, "1. згенерувати пару\nключів усередині", size=10, color=INK))
    f.append(text(ccx, cy + 84, "приват. ключ тут і помре", size=9.5, color=POS))

    f.append(rect(hx_box, cy, bw, bh, fill="#eef2f7", stroke=INK, sw=2))
    f.append(text(hcx, cy + 22, "ЦС виробника (HSM)", size=12, bold=True))
    f.append(mtext(hcx, cy + 44, "3. підписати відкритий\nключ кореневим", size=10, color=INK))
    f.append(text(hcx, cy + 84, "корінь довіри — у HSM", size=9.5, color=POS))

    # верхня стрілка: CSR (лише відкритий ключ) чип → ЦС, підпис НАД стрілкою
    ay_top = cy + 26
    f.append(arrow(cx_box + bw + 4, ay_top, hx_box - 4, ay_top, color=NEG, sw=1.8))
    f.append(mtext((cx_box + bw + hx_box) / 2, ay_top - 12,
                   "2. лише ВІДКРИТИЙ ключ (CSR) — назовні", size=10, color=NEG))
    # нижня стрілка: сертифікат ЦС → чип, підпис ПІД стрілкою
    ay_bot = cy + 78
    f.append(arrow(hx_box - 4, ay_bot, cx_box + bw + 4, ay_bot, color=NEG, sw=1.8))
    f.append(mtext((cx_box + bw + hx_box) / 2, ay_bot + 20,
                   "4. СЕРТИФІКАТ (підписаний відкр. ключ) — назад у розділ даних", size=10, color=NEG))

    # ── низ: чому саме так — недовірений CM ──
    yb = 300
    f.append(text(W / 2, yb, "ЧОМУ приватний ключ не дають самому заводу-складачу (contract manufacturer)",
                  size=12, bold=True, color=POS))
    f.append(fitbox(56, yb + 14, 372, 100,
                    "ЯКБИ ключ генерували НА ХОСТІ станції й заливали:\nу мить заливання приватний ключ ІСНУЄ поза чипом —\nу пам'яті станції, у файлі, у логах. Скомпрометований\nзавод → скомпрометовано КОЖЕН ключ, що там пройшов.\nЦе «вікно вразливості» транспортування секрету.",
                    size=10, color=POS, fill="#fdecea", stroke=POS, sw=1.6))
    f.append(fitbox(56 + 372 + 16, yb + 14, W - 56 - (56 + 372 + 16), 100,
                    "ГЕНЕРАЦІЯ НА БОРТУ це вікно закриває:\nприватний ключ ніколи не покидає кремній,\nзаводу нема чого вкрасти — він бачить лише\nвідкритий ключ. Там, де чип так не вміє,\nключ вливають із HSM/захищеного елемента,\nа не з відкритого файлу на станції.",
                    size=10, color=FIELD, fill="#eafaf1", stroke=FIELD, sw=1.6))
    render(os.path.join(OUT, 'key-ceremony.svg'), W, H, *f)


# ── Фігура D4: часова вісь незворотності — усе оборотне, тоді один необоротний ─
def fig_burn_order():
    W, H = 860, 400
    f = [text(W / 2, 30, "Точка неповернення: усе оборотне спершу, необоротне — останнім",
              size=15, bold=True)]

    # вісь часу зліва направо
    ax0, ax1 = 60, W - 60
    ay = 150
    f.append(line(ax0, ay, ax1, ay, color=INK, sw=2))
    f.append(arrow(ax1 - 2, ay, ax1 + 20, ay, color=INK, sw=2))
    f.append(text(ax1 + 8, ay + 20, "час", size=11, color=MUTED, anchor="start"))

    # оборотні кроки (можна перезробити) — зелена зона
    green_end = ax0 + (ax1 - ax0) * 0.66
    f.append(rect(ax0, ay - 40, green_end - ax0, 34, fill="#eafaf1", stroke=FIELD, sw=1.4))
    f.append(text((ax0 + green_end) / 2, ay - 19, "ОБОРОТНА ЗОНА — Flash перезаписуваний, усе можна перешити",
                  size=11, color=FIELD, bold=True))
    # необоротна зона — коричнева
    f.append(rect(green_end, ay - 40, ax1 - green_end, 34, fill="#fff3d6", stroke=BROWN, sw=1.4))
    f.append(text((green_end + ax1) / 2, ay - 19, "НЕОБОРОТНО", size=11, color=BROWN, bold=True))

    # позначки-кроки на осі
    steps = [
        (0.08, "прошити\nобраз", FIELD, False),
        (0.24, "записати\nособистість", FIELD, False),
        (0.40, "звірити:\nчитання назад", FIELD, False),
        (0.55, "самотест\nзелений?", FIELD, False),
        (0.78, "ПРОПАЛИТИ\neFuse", BROWN, True),
        (0.92, "запис\nу БД", INK, False),
    ]
    for frac, name, col, irrev in steps:
        x = ax0 + (ax1 - ax0) * frac
        f.append(circle(x, ay, 7, fill=("#fff3d6" if irrev else "#eafaf1"), stroke=col, sw=2))
        f.append(mtext(x, ay + 34, name, size=10, color=col, bold=irrev, lh=1.2))

    # рамка-пояснення внизу
    f.append(fitbox(60, 250, W - 120, 106,
                    "ЧОМУ такий порядок — це виведення, не смак. Пропалений eFuse НЕ ВІДКОТИШ: зіпсуєш біт, заллєш не той ключ,\n"
                    "увімкнеш захист зарано — плата або мертва, або назавжди зачинена. Тому необоротний крок ставлять ОСТАННІМ\n"
                    "і роблять ЛИШЕ після того, як усе оборотне вже підтверджено зчитуванням і самотестом. Помилку в оборотній зоні\n"
                    "виправляє перешивання; помилку в необоротній — уже НІЩО. Порядок кроків станції — страховка від необоротної\n"
                    "помилки, помноженої на тисячу плат.",
                    size=10.5, color=INK, fill="#f4f6f8", stroke=BROWN, sw=1.6))
    render(os.path.join(OUT, 'burn-order.svg'), W, H, *f)


if __name__ == '__main__':
    fig_cycle_budget()
    fig_serial_allocation()
    fig_key_ceremony()
    fig_burn_order()
    print("ok")

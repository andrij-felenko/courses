# -*- coding: utf-8 -*-
"""Фігури до теми «Смуга і межа Шеннона» (bandwidth-capacity).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Сама формула, розібрана на множники ───────────────────────────────────
# Ідея, яку важко передати прозою: показати очима, що C — це добуток, де B стоїть
# зовні (множник), а S/N — усередині логарифма; кожен символ підписаний.
def fig_formula():
    W, H = 720, 330
    f = []
    # центральна рамка з формулою
    bx, by, bw, bh = 170, 70, 380, 78
    f.append(rect(bx, by, bw, bh, fill="#eaf0fd", stroke=NEG, sw=2, rx=12))
    f.append(text(W / 2, by + bh / 2 + 10, "C = B · log₂(1 + S/N)", 29, INK, "middle", bold=True))

    # три підписи-колонки під множниками
    cols = [
        (250, FIELD, "C", "макс. біт/с", "пропускна здатність"),
        (400, NEG,   "B", "смуга, Гц",   "ширина каналу"),
        (560, POS,   "S/N", "сигнал/шум", "у разах, не в дБ"),
    ]
    for cx, col, sym, l1, l2 in cols:
        f.append(text(cx, 208, sym, 18, col, "middle", bold=True))
        f.append(text(cx, 230, l1, 11.5, col, "middle", bold=True))
        f.append(text(cx, 247, l2, 10, MUTED, "middle"))
        f.append(line(cx, 190, cx, by + bh + 4, color=col, sw=1.4, dash="3 3"))

    # підсумкова смуга
    f.append(fitbox(50, 280, 620, 32,
                    "нижче за C — зв'язок без помилок можливий; вище за C — неможливий у принципі",
                    size=12.5, fill="#eef6ef", stroke=FIELD, color=INK))
    render(os.path.join(IMG, "formula.svg"), W, H, *f,
           title="Межа Шеннона: стеля швидкості будь-якої лінії")


# ── 2. Два важелі — лінійний (смуга) проти логарифмічного (потужність) ────────
# Ідея: подвоїти смугу = подвоїти швидкість (щедро); щоб додати +1 біт/с/Гц,
# потужність треба ПОМНОЖИТИ (скупо). Дві колонки-сходинки поруч.
def fig_two_levers():
    W, H = 720, 400
    f = [text(W / 2, 28, "Два важелі ємності — і вони геть різні", 16, INK, "middle", bold=True)]

    # ліва колонка: смуга — лінійно
    lx = 180
    f.append(text(lx, 64, "Смуга B — щедрий важіль", 13, NEG, "middle", bold=True))
    f.append(text(lx, 82, "×2 смуги  →  ×2 швидкості", 11, MUTED, "middle"))
    base = 340
    for i, mul in enumerate([1, 2, 3, 4]):
        h = 34 * mul
        x = lx - 110 + i * 60
        f.append(rect(x, base - h, 44, h, fill="#eaf0fd", stroke=NEG, sw=1.8))
        f.append(text(x + 22, base - h - 8, "×%d" % mul, 11, NEG, "middle", bold=True))
        f.append(text(x + 22, base + 16, "%dB" % mul, 10, MUTED, "middle"))
    f.append(text(lx, base + 40, "лінійно: швидкість росте\nрівно зі смугою", 10.5, MUTED, "middle"))
    # перетворимо дворядковий підпис
    f.pop()
    f.append(mtext(lx, base + 38, ["лінійно: швидкість росте", "рівно зі смугою"], 10.5, MUTED))

    # розділювач
    f.append(line(W / 2, 56, W / 2, 360, color="#dde3ea", sw=1.4, dash="4 5"))

    # права колонка: потужність — логарифмічно
    rx = 540
    f.append(text(rx, 64, "Потужність (S/N) — скупий важіль", 12.5, POS, "middle", bold=True))
    f.append(text(rx, 82, "+1 біт/с/Гц коштує ×2 потужності", 11, MUTED, "middle"))
    # сходинки однакової висоти (по +1 біт), а підпис — множник потужності
    for i, lab in enumerate(["×1", "×2", "×4", "×8"]):
        x = rx - 110 + i * 60
        h = 100
        f.append(rect(x, base - h, 44, h, fill="#fdecea", stroke=POS, sw=1.8))
        f.append(text(x + 22, base - h - 8, "+1 біт", 9.5, POS, "middle", bold=True))
        f.append(text(x + 22, base + 16, lab, 10.5, MUTED, "middle"))
    f.append(mtext(rx, base + 38, ["щоб додавати рівні кроки бітів,", "потужність доводиться подвоювати"], 10.5, MUTED))

    render(os.path.join(IMG, "two-levers.svg"), W, H, *f)


# ── 3. Крива спектральної ефективності C/B = log2(1+S/N) ──────────────────────
# Ідея: росте, але дедалі повільніше; кожні +10 дБ дають лише ~3.3 біт/с/Гц.
def fig_efficiency_curve():
    W, H = 720, 400
    ox, oy = 90, 330
    aw, ah = 560, 250
    f = []

    # осі
    f.append(line(ox, oy, ox + aw + 12, oy, color=INK, sw=1.6))
    f.append(arrow(ox + aw, oy, ox + aw + 18, oy, color=INK, sw=1.6))
    f.append(text(ox + aw + 6, oy + 22, "S/N, дБ", 11, INK, "end", bold=True))
    f.append(line(ox, oy + 4, ox, oy - ah - 4, color=INK, sw=1.6))
    f.append(arrow(ox, oy - ah, ox, oy - ah - 18, color=INK, sw=1.6))
    f.append(text(ox - 12, oy - ah - 6, "біт/с/Гц", 11, INK, "end", bold=True))

    db_max, y_max = 40.0, 14.0
    def px(db):  return ox + (db / db_max) * aw
    def py(v):   return oy - (v / y_max) * ah

    # сітка по dB
    for db in [0, 10, 20, 30, 40]:
        f.append(line(px(db), oy, px(db), oy + 5, color=INK, sw=1.2))
        f.append(text(px(db), oy + 20, "%d" % db, 10, MUTED, "middle"))
    for v in [0, 2, 4, 6, 8, 10, 12, 14]:
        f.append(line(ox - 5, py(v), ox, py(v), color=INK, sw=1.2))
        f.append(text(ox - 9, py(v) + 4, "%d" % v, 10, MUTED, "end"))
        if v:
            f.append(line(ox, py(v), ox + aw, py(v), color="#eef0f2", sw=1))

    # крива log2(1 + 10^(dB/10))
    pts = []
    db = 0.0
    while db <= db_max:
        snr = 10 ** (db / 10.0)
        pts.append("%.1f,%.1f" % (px(db), py(math.log2(1 + snr))))
        db += 0.8
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join(pts), FIELD))

    # маркери на круглих dB
    for db in [0, 10, 20, 30]:
        snr = 10 ** (db / 10.0)
        v = math.log2(1 + snr)
        f.append(circle(px(db), py(v), 4.2, fill=POS, stroke=POS, sw=0))
        f.append(text(px(db) + 8, py(v) - 8, "%d дБ → %.1f" % (db, v), 9.5, POS, "start", bold=True))

    # підпис-висновок
    f.append(mtext(ox + aw - 6, py(13.0), ["перші децибели цінні,", "дальші — майже марні"],
                   10.5, MUTED, anchor="end"))
    render(os.path.join(IMG, "efficiency-curve.svg"), W, H, *f,
           title="Спектральна ефективність C/B = log₂(1 + S/N): логарифм-скнара")


# ── 4. Стіна Шеннона: зона можливого і неможливого ────────────────────────────
# Ідея: C — це межа; ліворуч можна підійти як завгодно близько, праворуч — глухо.
def fig_wall():
    W, H = 720, 350
    f = [text(W / 2, 30, "Межа C — стіна можливого", 16, INK, "middle", bold=True)]
    wallx = W / 2
    top, bot = 70, 300
    # ліва зона — можливе
    f.append(rect(70, top, wallx - 70 - 6, bot - top, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=8))
    f.append(text((70 + wallx) / 2 - 3, 120, "ЗОНА МОЖЛИВОГО", 13.5, FIELD, "middle", bold=True))
    f.append(mtext((70 + wallx) / 2 - 3, 156,
                   ["швидкість нижча за C:", "є кодування, що дає зв'язок", "майже без помилок навіть у шумі"],
                   11, INK))
    # права зона — неможливе
    f.append(rect(wallx + 6, top, 650 - wallx - 6, bot - top, fill="#fdecea", stroke=POS, sw=1.6, rx=8))
    f.append(text((wallx + 650) / 2 + 3, 120, "ЗОНА НЕМОЖЛИВОГО", 13.5, POS, "middle", bold=True))
    f.append(mtext((wallx + 650) / 2 + 3, 156,
                   ["швидкість вища за C:", "жодна модуляція й жодне", "кодування не врятують"],
                   11, INK))
    # сама стіна
    f.append(line(wallx, top - 6, wallx, bot + 6, color=INK, sw=4))
    f.append(text(wallx, bot + 26, "C = B · log₂(1 + S/N)", 13, INK, "middle", bold=True))
    # стрілка «підійти можна як завгодно близько»
    f.append(arrow(wallx - 130, 250, wallx - 8, 250, color=FIELD, sw=2))
    f.append(text(wallx - 130, 240, "підійти — як завгодно близько", 10, MUTED, "middle"))
    render(os.path.join(IMG, "wall.svg"), W, H, *f)


# ── 5. Дозвонний модем: чому стеля ~33.6k ─────────────────────────────────────
# Ідея: підставляємо реальні B≈3100 Гц і S/N≈30 дБ — і виходить ~31 кбіт/с.
def fig_dialup_modem():
    W, H = 720, 360
    f = [text(W / 2, 30, "Чому дозвонний модем уперся в ~33.6 кбіт/с", 15.5, INK, "middle", bold=True)]

    # ліворуч — телефонна лінія з її параметрами
    f.append(rect(60, 80, 250, 150, fill="#f4f6f8", stroke=LINE, sw=1.6, rx=10))
    f.append(text(185, 108, "Телефонна лінія", 13, INK, "middle", bold=True))
    f.append(text(185, 140, "смуга B ≈ 3100 Гц", 12, NEG, "middle", bold=True))
    f.append(text(185, 168, "сигнал/шум ≈ 30 дБ", 12, POS, "middle", bold=True))
    f.append(text(185, 188, "(× 1000 у разах)", 10.5, MUTED, "middle"))
    f.append(text(185, 214, "вузька смуга для голосу", 10, MUTED, "middle"))

    # стрілка «у формулу»
    f.append(arrow(316, 155, 372, 155, color=INK, sw=2.2))
    f.append(text(344, 144, "Шеннон", 10.5, INK, "middle", bold=True))

    # праворуч — обчислення й результат
    f.append(rect(380, 80, 280, 150, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=10))
    f.append(mtext(520, 116,
                   ["C = 3100 · log₂(1 + 1000)", "C = 3100 · 9.97", "C ≈ 31 000 біт/с"],
                   12.5, INK))
    f.append(line(400, 178, 640, 178, color="#cfd6dd", sw=1.2))
    f.append(text(520, 202, "≈ 31 кбіт/с", 17, FIELD, "middle", bold=True))
    f.append(text(520, 220, "це фізична стеля лінії", 10.5, MUTED, "middle"))

    # нижній висновок про 56k
    f.append(fitbox(60, 270, 600, 56,
                    "«56k» не побили закон: один бік лінії зробили цифровим — прибрали етап\nперетворення й підняли ефективний S/N. Не перестрибнули стіну, а відсунули її.",
                    size=11.5, fill="#fdf6ec", stroke="#b08900", color=INK))
    render(os.path.join(IMG, "dialup-modem.svg"), W, H, *f)


# ── 6. Один закон під усіма модуляціями ───────────────────────────────────────
# Ідея: усі схеми — різні угоди в межах того самого «обмінного курсу» Шеннона.
def fig_under_all_modulation():
    W, H = 720, 340
    f = [text(W / 2, 30, "Один закон під усіма модуляціями", 16, INK, "middle", bold=True)]
    # центральний вузол — межа Шеннона
    cx, cy = W / 2, 90
    bx, bw = cx - 150, 300
    f.append(rect(bx, 58, bw, 46, fill="#eaf0fd", stroke=NEG, sw=2, rx=10))
    f.append(text(cx, 86, "межа Шеннона C = B · log₂(1 + S/N)", 12.5, INK, "middle", bold=True))

    items = [
        (140, "FM (Армстронг)", "міняє СМУГУ", "на запас від шуму"),
        (360, "QAM-сузір'я", "міняє S/N", "на біти за символ"),
        (580, "Розширений спектр", "міняє СМУГУ", "на стійкість і скритність"),
    ]
    for ix, name, t1, t2 in items:
        f.append(arrow(cx, 106, ix, 168, color=MUTED, sw=1.6))
        f.append(rect(ix - 95, 172, 190, 90, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=8))
        f.append(text(ix, 196, name, 12.5, INK, "middle", bold=True))
        f.append(text(ix, 222, t1, 12, FIELD, "middle", bold=True))
        f.append(text(ix, 244, t2, 10.5, MUTED, "middle"))
    f.append(text(W / 2, 296, "різні угоди — той самий обмінний курс, що його задає Шеннон",
                  11.5, MUTED, "middle"))
    render(os.path.join(IMG, "under-all-modulation.svg"), W, H, *f)


# ── 7. Клод Шеннон і народження теорії інформації ─────────────────────────────
# Ідея: хронологія попередників → синтез 1948 → що з нього виросло.
def fig_shannon():
    W, H = 720, 340
    f = [text(W / 2, 30, "Клод Шеннон і народження теорії інформації", 15.5, INK, "middle", bold=True)]

    # таймлайн
    ty = 110
    f.append(line(70, ty, 650, ty, color=MUTED, sw=1.6))
    marks = [
        (140, "1924–28", "Найквіст", "смуга ↔ 2B імпульсів/с"),
        (320, "1928", "Гартлі", "кількісна міра швидкості"),
        (520, "1948", "Шеннон", "точна межа C + доказ\nдосяжності"),
    ]
    for x, yr, who, what in marks:
        f.append(circle(x, ty, 6, fill=NEG, stroke=NEG, sw=0))
        f.append(text(x, ty - 16, yr, 12, NEG, "middle", bold=True))
        f.append(text(x, ty + 26, who, 12.5, INK, "middle", bold=True))
        lines = what.split("\n")
        f.append(mtext(x, ty + 44, lines, 10, MUTED))

    # підсумкова рамка — внесок Шеннона
    f.append(rect(70, 200, 580, 56, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=8))
    f.append(mtext(360, 224,
                   ["стаття «A Mathematical Theory of Communication» (Bell Labs):",
                    "заснувала теорію інформації й увела «біт» як одиницю"],
                   11, INK))
    # що виросло
    f.append(text(W / 2, 290, "звідси — уся завадостійка передача: від QR-кодів до 5G і зв'язку з марсоходами",
                  11, MUTED, "middle"))
    render(os.path.join(IMG, "shannon.svg"), W, H, *f)


if __name__ == "__main__":
    fig_formula()
    fig_two_levers()
    fig_efficiency_curve()
    fig_wall()
    fig_dialup_modem()
    fig_under_all_modulation()
    fig_shannon()
    print("OK: figures written to", IMG)

# -*- coding: utf-8 -*-
"""Фігури до теми «Пакування й транспортування ESD» та її вставок.
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).
Без номерів розділів у підписах (AUTHORING §2/§5)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

PINK = "#f6d4de"   # рожевий «антистатик»
GREY = "#d7d7d7"   # розсіювальний пластик
SILV = "#cfe0ea"   # екранувальний (метал)
CHIP = "#2b4a40"   # корпус ІМС


# ── 1. Три класи пакувань (тема) ─────────────────────────────────────────────
def fig_bags():
    W, H = 940, 470
    f = [text(W / 2, 30, "Три класи пакувань: антистатичне, розсіювальне, екранувальне",
              size=17, bold=True)]
    f.append(text(W / 2, 52, "що від чого захищає — залежить від того, чи проводить плівка й чи має вона суцільний екран",
                  size=12, color=MUTED, italic=True))

    def panel(cx, accent, title, bagfill, shield, verdict, vcol, bullets):
        x = cx - 125
        f.append(rect(x, 84, 250, 250, fill="#fcfcfc", stroke=accent, sw=1.8, rx=12))
        f.append(text(cx, 110, title, size=13, color=accent, bold=True))
        # пакет
        f.append(rect(cx - 70, 132, 140, 90, fill=bagfill, stroke=accent, sw=2, rx=6))
        # деталь усередині
        f.append(rect(cx - 35, 160, 70, 34, fill=CHIP, stroke=FIELD, sw=1.6, rx=3))
        f.append(text(cx, 182, "ІМС", size=10, color="#dff0e6", bold=True))
        if shield:
            f.append(rect(cx - 72, 134, 4, 86, fill=accent, stroke=accent, sw=0, rx=0))
        # хвиля зовнішнього поля, що йде до пакета
        f.append(line(x + 18, 177, cx - 70, 177, color=POS if not shield else FIELD, sw=2))
        f.append(text(cx, 244, verdict, size=11, color=vcol, bold=True))
        f.append(mtext(cx, 266, bullets, size=10.5, color=INK, lh=1.5))

    panel(175, POS, "Рожевий «антистатик»", PINK, False,
          "поле проходить ✗", POS,
          "сам не іскрить\nале НЕ екранує\nдля нечутливого / вторинне")
    panel(465, INK, "Чорний розсіювальний", GREY, False,
          "поле проходить ✗", POS,
          "проводить помалу\nвирівнює заряд на собі\nлотки, піна, мати")
    panel(765, NEG, "Сріблястий екранувальний", SILV, True,
          "поле НЕ проходить ✓", FIELD,
          "метал. шар = клітка Фарадея\n+ розсіювальний шар усередині\nОСНОВНИЙ для чутливих ІМС")

    b, _, _ = textbox(W / 2, 372,
                      "Пастка: рожевий «антистатик» лише не іскрить сам — він НЕ екран. Чутливу ІМС возять у сріблястому екранувальному пакеті.",
                      size=12, fill="#fbeee6", stroke=POS, bold=True)
    f.append(b)
    f.append(text(W / 2, 414, "Екранувальний пакет — клітка Фарадея, лише поки закритий: відкрив — захисту вже немає.",
                  size=11, color=MUTED))
    f.append(text(W / 2, 436, "Транспортна тара (тубуси, котушки, лотки) — з розсіювального пластику, щоб тряска не родила заряд.",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "bags.svg"), W, H, *f)


# ── 2. Транспортна тара (тема) ───────────────────────────────────────────────
def fig_carriers():
    W, H = 920, 360
    f = [text(W / 2, 30, "Транспортна тара: щоб виводи не терлися й не електризувались",
              size=17, bold=True)]
    f.append(text(W / 2, 52, "форма тримає компоненти нерухомо; матеріал розсіювальний, щоб тертя не родило заряд",
                  size=12, color=MUTED, italic=True))

    # Тубус
    f.append(text(170, 92, "Тубус (туба) для DIP", size=12, bold=True))
    f.append(rect(60, 110, 220, 36, fill=GREY, stroke=INK, sw=2, rx=6))
    for x in (74, 114, 154, 194, 234):
        f.append(rect(x, 116, 26, 24, fill="#333", stroke=INK, sw=1.4, rx=2))
    f.append(text(170, 168, "мікросхеми лежать у ряд, не торкаючись", size=10, color=MUTED))

    # Стрічка на котушці
    f.append(text(490, 92, "Стрічка на котушці (tape & reel)", size=12, bold=True))
    f.append(circle(420, 150, 44, fill="#fafafa", stroke=INK, sw=2))
    f.append(circle(420, 150, 12, fill=BG, stroke=INK, sw=1.6))
    f.append(rect(470, 138, 200, 24, fill=GREY, stroke=INK, sw=2, rx=0))
    for x in range(478, 640, 26):
        f.append(rect(x, 142, 14, 16, fill="#333", stroke=INK, sw=1, rx=2))
    f.append(text(560, 188, "SMD у кишеньках, накрито плівкою", size=10, color=MUTED))

    # Лоток
    f.append(text(780, 92, "Лоток (tray)", size=12, bold=True))
    f.append(rect(700, 110, 160, 90, fill="#3f6f5f", stroke=INK, sw=2, rx=6))
    for ry in (124, 164):
        for rx in (716, 764, 812):
            f.append(rect(rx, ry, 36, 28, fill=CHIP, stroke=FIELD, sw=1.4, rx=3))
    f.append(text(780, 220, "для QFP/BGA — кожен у комірці", size=10, color=MUTED))

    # спільна ідея
    f.append(rect(120, 250, 680, 86, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=10))
    f.append(text(460, 276, "Спільна ідея всієї тари", size=12.5, color=FIELD, bold=True))
    f.append(text(460, 300, "механічно: компонент не совається, виводи не труться один об одного й об стінки;",
                  size=10.5, color=INK))
    f.append(text(460, 322, "електрично: матеріал розсіювальний (не діелектрик), тож перевезення не накопичує заряд.",
                  size=10.5, color=INK))
    render(os.path.join(IMG, "carriers.svg"), W, H, *f)


# ── 3. Чому дріт не рятує ізолятор, а іони — рятують (вставка) ────────────────
def fig_ion_why():
    W, H = 920, 470
    f = [text(W / 2, 30, "Дріт осушує лише провідник. Ізолятор нейтралізує лише повітря",
              size=17, bold=True)]
    f.append(text(W / 2, 52, "заряд на пластику сидить там, де осів, і по дроту нікуди не стікає — потрібні іони з повітря",
                  size=12, color=MUTED, italic=True))

    # ── ліва панель: дріт не працює ──
    f.append(rect(40, 80, 411, 350, fill="#eef1f4", stroke=POS, sw=1.8, rx=10))
    f.append(mtext(245, 108, "Спроба: заземлити ізолятор дротом — НЕ працює",
                   size=13, color=POS, bold=True, lh=1.4))
    f.append(rect(80, 160, 331, 70, fill="#f1ece0", stroke="#b9ad8a", sw=2, rx=6))
    f.append(text(245, 152, "заряджений ізолятор (пластик, плівка)", size=11, color=MUTED, italic=True))
    for cx in (104, 161, 217, 274, 330, 387):
        f.append(minus(cx, 178, r=7))
    f.append(text(245, 208, "заряд осів локально й нерухомий", size=11, color=NEG))
    # дріт із землею
    f.append(line(411, 230, 433, 230, color=INK, sw=2))
    f.append(line(433, 230, 433, 296, color=INK, sw=2))
    f.append(line(417, 300, 449, 300, color=INK, sw=2.4))
    f.append(line(423, 306, 443, 306, color=INK, sw=2.2))
    f.append(line(428, 312, 438, 312, color=INK, sw=2))
    f.append(text(406, 262, "✕", size=22, color=POS, bold=True))
    f.append(mtext(245, 372,
                   "по ізолятору заряд не доходить до дроту:\nнемає вільних носіїв — немає провідності",
                   size=11, color=INK, lh=1.4))
    f.append(text(245, 414, "поверхня лишається зарядженою", size=12, color=POS, bold=True))

    # ── права панель: іони працюють ──
    f.append(rect(479, 80, 411, 350, fill="#eef3ee", stroke=FIELD, sw=1.8, rx=10))
    f.append(mtext(684, 108, "Рішення: облити поверхню\nбіполярними іонами повітря",
                   size=13, color=FIELD, bold=True, lh=1.4))
    f.append(rect(638, 142, 92, 22, fill="#dfe5ea", stroke=MUTED, sw=1.6, rx=5))
    f.append(text(684, 157, "іонізатор", size=11, color=INK, bold=True))
    f.append(line(684, 164, 684, 176, color=MUTED, sw=2))
    # хмара іонів обох знаків
    for cx, cy, pos in [(626, 188, 1), (654, 200, 0), (678, 184, 1),
                        (704, 198, 0), (730, 190, 1), (746, 202, 0)]:
        f.append(plus(cx, cy, r=6) if pos else minus(cx, cy, r=6))
    f.append(rect(519, 232, 331, 70, fill="#eef6ef", stroke=FIELD, sw=2, rx=6))
    f.append(text(684, 226, "той самий ізолятор", size=11, color=FIELD, italic=True))
    # від'ємні ділянки притягують + іони
    for cx in (549, 605, 662, 718, 775, 832):
        f.append(minus(cx, 252, r=6))
        f.append(line(cx, 210, cx, 242, color=POS, sw=1.6, dash="2,3"))
        f.append(plus(cx, 214, r=5))
    f.append(text(684, 280, "+ з повітря сідають на − поверхні → 0", size=11, color=FIELD, bold=True))
    f.append(mtext(684, 372,
                   "поверхня сама притягує іон протилежного\nзнаку — і нейтралізується за секунди",
                   size=11, color=INK, lh=1.4))
    f.append(text(684, 414, "заземлення не потрібне", size=12, color=FIELD, bold=True))
    render(os.path.join(IMG, "ion-why.svg"), W, H, *f)


# ── 4. Тракт іонізатора і дві цифри (вставка) ────────────────────────────────
def fig_ion_specs():
    W, H = 920, 500
    f = [text(W / 2, 30, "Будова іонізатора і дві цифри, за якими його судять",
              size=17, bold=True)]
    f.append(text(W / 2, 52, "корона на вістрі народжує іони; вентилятор несе їх до деталі",
                  size=12, color=MUTED, italic=True))

    # ── верхній ряд: тракт ──
    stages = [(125, NEG, "Високовольтне\nживлення\n(кВ, AC або DC)"),
              (335, POS, "Емітер-вістря\nкорона\nіони + і −"),
              (555, FIELD, "Вентилятор\nнесе іони\nдо зони"),
              (775, INK, "Заряджена\nдеталь / поверхня\nнейтралізується")]
    for cx, accent, label in stages:
        f.append(fitbox(cx - 85, 90, 170, 78, label, size=11.5, fill=BG, stroke=accent,
                        color=accent, bold=True))
    for x in (210, 420, 640):
        f.append(arrow(x, 129, x + 38, 129, color=INK, sw=2.2))

    # вістря з короною під емітером
    f.append(line(335, 194, 335, 210, color=MUTED, sw=3))
    f.append(line(335, 210, 327, 224, color=POS, sw=2.4))
    f.append(line(335, 210, 343, 224, color=POS, sw=2.4))
    for dx in (-13, -7, 0, 7, 13):
        f.append(line(335, 224, 335 + dx, 204, color=POS, sw=1.4, dash="2,3"))
    f.append(plus(316, 238, r=5))
    f.append(minus(354, 238, r=5))
    f.append(text(335, 262, "поле біля вістря ≫ середнього", size=11, color=MUTED, italic=True))

    # ── нижній блок: графік спаду ──
    f.append(rect(70, 300, 780, 170, fill=BG, stroke=MUTED, sw=1.4, rx=6))
    # осі
    ox, oy, ow, oh = 120, 318, 700, 106
    f.append(line(ox, oy, ox, oy + oh, color=INK, sw=2))
    f.append(line(ox, oy + oh, ox + ow, oy + oh, color=INK, sw=2))
    f.append(text(112, 314, "U пластини", size=11, color=INK, bold=True, anchor="end"))
    f.append(text(ox + ow, oy + oh + 18, "час, с", size=11, color=INK, bold=True, anchor="end"))
    f.append(text(114, 328, "+1000", size=10, color=MUTED, anchor="end"))
    f.append(text(114, oy + oh + 4, "0", size=10, color=MUTED, anchor="end"))
    # крива експоненційного спаду
    import math
    top, bot = 333.0, oy + oh        # 1000 В .. 0 В
    pts = []
    for i in range(121):
        xx = ox + ow * i / 120.0
        yy = bot - (bot - top) * math.exp(-i / 28.0)
        pts.append("%.1f,%.1f" % (xx, yy))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3" '
             'stroke-linejoin="round"/>' % (" ".join(pts), FIELD))
    # лінія залишкового офсету (баланс)
    f.append(line(ox, bot - 4, ox + ow, bot - 4, color="#caa24a", sw=1.8, dash="5,4"))
    f.append(text(ox + 130, 376, "час спаду ~ кілька секунд", size=11, color=FIELD, bold=True))
    # рамка з двома цифрами
    f.append(fitbox(588, 320, 250, 50,
                    "баланс (offset): чим ближче до 0 В\nчас спаду: 1000→100 В за одиниці с",
                    size=10.5, fill="#fbf7ec", stroke="#caa24a", color="#8a6a14", bold=True))
    render(os.path.join(IMG, "ion-specs.svg"), W, H, *f)


if __name__ == "__main__":
    fig_bags()
    fig_carriers()
    fig_ion_why()
    fig_ion_specs()
    print("OK: 4 figures ->", IMG)

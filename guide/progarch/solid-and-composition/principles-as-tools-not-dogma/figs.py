# -*- coding: utf-8 -*-
"""Фігури до кроку «Принципи як інструменти, не догми».
Три фігури:
  (1) rule-and-force   — правило = стиснута сила; догма = правило без сили;
  (2) principles-collide — два принципи тягнуть у різні боки, суддя вирішує;
  (3) three-questions  — три питання, якими наводять будь-який принцип."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

GREEN_FILL = "#e8f6ee"
RED_FILL   = "#fdecea"
BLUE_FILL  = "#eaf0fd"


def drect(x, y, w, h, stroke, sw=1.6):
    """Пунктирна рамка без заливки (для «порожнього місця сили»)."""
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="6" fill="none" '
            'stroke="%s" stroke-width="%.1f" stroke-dasharray="7 5"/>' % (x, y, w, h, stroke, sw))


# ── Фігура 1: правило = стиснута сила; догма = правило без сили ───────────────
def fig_rule_and_force():
    W, H = 960, 470
    frags = []

    # Панель А — ІНСТРУМЕНТ
    frags.append(text(W / 2, 60, "ІНСТРУМЕНТ — правило тримається за силу", size=15, bold=True))
    frags.append(fitbox(70, 86, 320, 94,
                        "СИЛА (джерело)\nпродубльоване знання\nз часом розходиться",
                        size=13, fill=GREEN_FILL, stroke=FIELD))
    frags.append(fitbox(570, 86, 320, 94,
                        "ПРАВИЛО (кеш)\n«Не повторюйся» (DRY)",
                        size=13, fill=BLUE_FILL, stroke=NEG))
    frags.append(text(479, 100, "стискається в", size=12, color=MUTED))
    frags.append(arrow(392, 112, 566, 112, color=INK, sw=1.9))
    frags.append(arrow(566, 150, 392, 150, color=MUTED, sw=1.6))
    frags.append(text(479, 172, "вказує назад на силу", size=12, color=MUTED))

    # роздільник
    frags.append(line(60, 214, 900, 214, color=MUTED, sw=1.2, dash="4 4"))

    # Панель Б — ДОГМА
    frags.append(text(W / 2, 250, "ДОГМА — те саме правило, а сили під ним нема", size=15, bold=True))
    # порожнє місце сили
    frags.append(drect(90, 286, 300, 84, POS))
    frags.append(line(96, 292, 384, 364, color=POS, sw=1.8))
    frags.append(line(384, 292, 96, 364, color=POS, sw=1.8))
    frags.append(text(240, 392, "місце сили порожнє", size=12, color=MUTED))
    # правило все одно застосоване
    frags.append(fitbox(570, 286, 300, 84, "ПРАВИЛО\nвсе одно застосоване",
                        size=13, fill=BLUE_FILL, stroke=NEG))
    frags.append(text(480, 314, "«усунь дублювання!»", size=12, color=POS))
    frags.append(arrow(566, 328, 392, 328, color=POS, sw=1.9))

    frags.append(text(W / 2, 438,
                      "Верх: правило й сила тримаються разом — це інструмент. Низ: правило без сили — карго.",
                      size=13, color=INK))

    render(os.path.join(IMG, 'rule-and-force.svg'), W, H, *frags,
           title="Правило — стиснута сила; догма — правило без сили")


# ── Фігура 2: принципи стикаються — суддя вирішує ────────────────────────────
def fig_collide():
    W, H = 1000, 480
    frags = []

    # вузол рішення
    frags.append(fitbox(360, 74, 280, 78,
                        "РІШЕННЯ\nвиносити двійника\nу спільну абстракцію?",
                        size=13, bold=True, fill=FILL, stroke=INK, sw=2.2))

    # ліворуч — DRY тягне до ТАК
    frags.append(fitbox(48, 250, 258, 88,
                        "DRY\n«не дублюй»\nтягне до ТАК",
                        size=13, fill=GREEN_FILL, stroke=FIELD))
    # праворуч — розчеплення + YAGNI тягне до НІ
    frags.append(fitbox(694, 250, 268, 88,
                        "Розчеплення + YAGNI\n«не зшивай дві осі»\nтягне до НІ",
                        size=13, fill=BLUE_FILL, stroke=NEG))

    # стрілки-тяга до вузла рішення
    frags.append(arrow(214, 250, 402, 154, color=FIELD, sw=2.0))
    frags.append(arrow(792, 250, 600, 154, color=NEG, sw=2.0))

    # суддя внизу
    frags.append(fitbox(292, 366, 416, 70,
                        "СУДДЯ — ти\nпитання: це те саме знання\nчи випадковий збіг?",
                        size=13, bold=True, fill=FILL, stroke=INK))
    frags.append(arrow(500, 364, 500, 156, color=INK, sw=2.0))
    frags.append(text(516, 250, "зважує сили", size=12, color=MUTED, anchor="start"))

    frags.append(text(W / 2, 462,
                      "Закон не буває скасований рівним законом. Принципи — важелі; нічию розв'язує суддя.",
                      size=13, color=INK))

    render(os.path.join(IMG, 'principles-collide.svg'), W, H, *frags,
           title="Принципи стикаються — суддя вирішує")


# ── Фігура 3: три питання, якими наводять принцип ────────────────────────────
def fig_three_questions():
    W, H = 1080, 372
    frags = []

    qy, qh = 78, 98
    frags.append(fitbox(40, qy, 300, qh,
                        "1. Яку СИЛУ\nце правило стереже?\n(назви біль)",
                        size=13, bold=False, fill=FILL, stroke=INK))
    frags.append(fitbox(390, qy, 300, qh,
                        "2. Сила тут РЕАЛЬНА\nі присутня — чи\nгіпотетична «раптом»?",
                        size=13, bold=False, fill=FILL, stroke=INK))
    frags.append(fitbox(740, qy, 300, qh,
                        "3. Ціна дотримання\nменша за біль,\nякий він відводить?",
                        size=13, bold=False, fill=FILL, stroke=INK))
    frags.append(arrow(340, qy + qh / 2, 388, qy + qh / 2, color=INK, sw=1.8))
    frags.append(arrow(690, qy + qh / 2, 738, qy + qh / 2, color=INK, sw=1.8))

    # розвилка з Q3 у два наслідки
    jx, jy = 890, 210
    frags.append(line(890, qy + qh, jx, jy, color=INK, sw=1.8))
    frags.append(fitbox(250, 250, 320, 80,
                        "усі ТАК →\nзастосуй: проведи шов,\nвинеси абстракцію",
                        size=13, fill=GREEN_FILL, stroke=FIELD))
    frags.append(fitbox(636, 250, 344, 80,
                        "сили нема →\nтримай простим,\nлінза чекає в шухляді",
                        size=13, fill=BLUE_FILL, stroke=NEG))
    frags.append(arrow(jx, jy, 470, 248, color=FIELD, sw=1.8))
    frags.append(arrow(jx, jy, 808, 248, color=NEG, sw=1.8))

    frags.append(text(W / 2, 356,
                      "Присутня сила — застосовуй; нема — найкраще рішення часто «нічого не роби».",
                      size=13, color=INK))

    render(os.path.join(IMG, 'three-questions.svg'), W, H, *frags,
           title="Три питання, якими наводять будь-який принцип")


# ── Фігура 4 (до вставки proj): зливати за силою, а не за формою ─────────────
def fig_true_vs_false_axis():
    W, H = 1080, 560
    frags = []

    # роздільник панелей
    frags.append(line(540, 52, 540, 460, color=MUTED, sw=1.2, dash="5 6"))

    # ── ЛІВА панель: хибна вісь — спільна форма рядка ────────────────────────
    frags.append(text(275, 62, "ХИБНА ВІСЬ · форма рядка", size=15, bold=True))
    frags.append(fitbox(130, 96, 290, 66, "notify(kind, …)\n«спільне» лише на око",
                        size=13, fill=RED_FILL, stroke=POS, sw=2.0))
    frags.append(fitbox(70, 300, 180, 60, "notifyMotion", size=13, fill=FILL, stroke=INK))
    frags.append(fitbox(300, 300, 180, 60, "notifyOffline", size=13, fill=FILL, stroke=INK))
    frags.append(arrow(160, 300, 232, 163, color=POS, sw=1.9))
    frags.append(arrow(390, 300, 318, 163, color=POS, sw=1.9))
    frags.append(text(275, 392, "гілки motion і offline не діляться — if(kind) каша",
                      size=12, color=POS))

    # ── ПРАВА панель: справжня вісь — формула небезпеки ──────────────────────
    frags.append(text(810, 62, "СПРАВЖНЯ ВІСЬ · формула небезпеки", size=15, bold=True))
    frags.append(fitbox(575, 96, 145, 58, "тривога\nруху", size=13, fill=FILL, stroke=INK))
    frags.append(fitbox(738, 96, 145, 58, "офлайн-\nпристрій", size=13, fill=FILL, stroke=INK))
    frags.append(fitbox(901, 96, 145, 58, "озброєння\nзони", size=13, fill=FILL, stroke=INK))
    frags.append(fitbox(690, 300, 240, 74,
                        "dangerLevel(zone)\nодна формула —\nбізнес міняє як одне",
                        size=13, fill=GREEN_FILL, stroke=FIELD, sw=2.0))
    frags.append(arrow(647, 154, 744, 300, color=FIELD, sw=1.9))
    frags.append(arrow(810, 154, 810, 300, color=FIELD, sw=1.9))
    frags.append(arrow(973, 154, 876, 300, color=FIELD, sw=1.9))
    frags.append(text(810, 402, "тричі → правило трьох спрацювало по суті",
                      size=12, color=FIELD))

    frags.append(text(W / 2, 500,
                      "Зливай не те, що на око схоже (рядок), а те, за чим одна сила (формула небезпеки).",
                      size=13, color=INK))

    render(os.path.join(IMG, 'true-vs-false-axis.svg'), W, H, *frags,
           title="Зливати за силою, а не за формою")


# ── Фігура 5 (до вставки hist): карго-культ старший за війну ──────────────────
def fig_cargo_timeline():
    W, H = 1180, 500
    frags = []
    axis_y = 244
    xs = [110, 300, 490, 680, 870, 1060]
    above = [True, False, True, False, True, False]
    fills = [GREEN_FILL, GREEN_FILL, GREEN_FILL, RED_FILL, BLUE_FILL, BLUE_FILL]
    strokes = [FIELD, FIELD, FIELD, POS, NEG, NEG]
    data = [
        ["1885", "рух Тука · Фіджі", "ще без літаків"],
        ["1919–1922", "Вайлала · Папуа", "«пароплав предків»"],
        ["кінець 1930-х", "Джон Фрум · Танна", "пророцтво про поміч"],
        ["1942", "бази США на островах", "вантаж мов «підтвердив»"],
        ["1945", "Норріс Бірд, PIM", "друкує «карго-культ»"],
        ["1974", "Річард Фейнман", "«наука-карго»"],
    ]
    frags.append(line(80, axis_y, 1104, axis_y, color=MUTED, sw=2))
    bw, bh = 186, 74
    for i, cx in enumerate(xs):
        if above[i]:
            by = 78
            frags.append(line(cx, axis_y, cx, by + bh + 2, color=strokes[i], sw=1.6))
        else:
            by = 330
            frags.append(line(cx, axis_y, cx, by - 2, color=strokes[i], sw=1.6))
        frags.append(fitbox(cx - bw / 2, by, bw, bh, "\n".join(data[i]), size=13,
                            fill=fills[i], stroke=strokes[i], sw=1.8))
        frags.append(circle(cx, axis_y, 6, fill=strokes[i], stroke=INK, sw=1.5))
    frags.append(text(W / 2, 484,
                      "Рухи 1885–1930-х старші за війну; вантаж 1942-го лише «підтвердив» їх — "
                      "термін (1945) і метафора (1974) прийшли пізніше.",
                      size=13, color=INK))
    render(os.path.join(IMG, 'cargo-timeline.svg'), W, H, *frags,
           title="Карго-культ старший за війну — коротка хронологія")


if __name__ == "__main__":
    fig_rule_and_force()
    fig_collide()
    fig_three_questions()
    fig_true_vs_false_axis()
    fig_cargo_timeline()
    print("ok:", os.listdir(IMG))

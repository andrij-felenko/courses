# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. З учителем vs без учителя ─────────────────────────────────────────────
def fig_labeled_vs_not():
    W, H = 720, 360
    els = []
    els.append(text(W / 2, 26, "З учителем: є підписи · Без учителя: підписів нема", size=17, bold=True))

    # ліва панель — з учителем (кожна точка вже підписана)
    els.append(fitbox(30, 50, 310, 34, "З УЧИТЕЛЕМ — точки з відповідями",
                      size=14, bold=True, fill="#eef7f0", stroke=FIELD))
    # дві групи точок з готовими мітками (колір = відомий клас)
    catsL = [(110, 150, POS), (140, 175, POS), (95, 200, POS), (130, 215, POS), (165, 165, POS)]
    dogsL = [(250, 260, NEG), (280, 240, NEG), (235, 290, NEG), (300, 285, NEG), (265, 310, NEG)]
    for (x, y, c) in catsL:
        els.append(circle(x, y, 8, fill="#fdecea", stroke=c, sw=2))
    for (x, y, c) in dogsL:
        els.append(circle(x, y, 8, fill="#eaf0fd", stroke=c, sw=2))
    els.append(text(130, 128, "«кіт»", size=12, color=POS, bold=True))
    els.append(text(268, 330, "«пес»", size=12, color=NEG, bold=True))
    els.append(text(185, 100, "мета: провести межу кіт|пес", size=11, color=MUTED))

    # права панель — без учителя (усі точки однакові, сірі)
    els.append(fitbox(390, 50, 300, 34, "БЕЗ УЧИТЕЛЯ — точки без відповідей",
                      size=14, bold=True, fill="#f4f6f8", stroke=LINE))
    grey = "#9aa0a6"
    blobA = [(470, 150), (500, 170), (455, 190), (490, 205), (525, 165)]
    blobB = [(610, 255), (640, 235), (595, 285), (660, 280), (625, 305)]
    for (x, y) in blobA + blobB:
        els.append(circle(x, y, 8, fill="#eceff1", stroke=grey, sw=2))
    # пунктирні оболонки — те, що модель має ЗНАЙТИ сама
    els.append('<ellipse cx="490" cy="178" rx="52" ry="42" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="5 4"/>' % FIELD)
    els.append('<ellipse cx="626" cy="272" rx="48" ry="40" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="5 4"/>' % FIELD)
    els.append(text(540, 110, "мета: знайти групи самому", size=11, color=MUTED))

    render(os.path.join(IMG, "labeled-vs-not.svg"), W, H, *els)


# ── 2. Три родини роботи без учителя ─────────────────────────────────────────
def fig_three_families():
    W, H = 720, 300
    els = []
    els.append(text(W / 2, 26, "Що робить навчання без учителя", size=17, bold=True))

    grey = "#9aa0a6"

    # (A) кластеризація — з хмари точок стають групи
    els.append(fitbox(20, 46, 210, 30, "Кластеризація", size=14, bold=True, fill="#eef7f0", stroke=FIELD))
    ca = [(70, 120), (95, 140), (60, 155)]
    cb = [(170, 200), (195, 180), (150, 215)]
    for (x, y) in ca:
        els.append(circle(x, y, 7, fill="#eef7f0", stroke=FIELD, sw=2))
    for (x, y) in cb:
        els.append(circle(x, y, 7, fill="#eaf0fd", stroke=NEG, sw=2))
    els.append('<ellipse cx="75" cy="138" rx="34" ry="30" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="4 3"/>' % FIELD)
    els.append('<ellipse cx="172" cy="198" rx="34" ry="30" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="4 3"/>' % NEG)
    els.append(text(125, 268, "згрупувати схоже", size=11, color=MUTED))

    # (B) зниження вимірності — 2D → 1D вісь
    els.append(fitbox(255, 46, 210, 30, "Зниження вимірності", size=14, bold=True, fill="#eef7f0", stroke=FIELD))
    # хмара, витягнута по діагоналі
    pts = [(300, 200), (320, 185), (345, 165), (370, 150), (395, 135), (335, 178), (360, 158)]
    for (x, y) in pts:
        els.append(circle(x, y, 6, fill="#eceff1", stroke=grey, sw=1.8))
    els.append(arrow(292, 208, 405, 128, color=POS, sw=2.2))  # головна вісь
    els.append(text(360, 250, "стиснути осі,", size=11, color=MUTED))
    els.append(text(360, 266, "лишити головне", size=11, color=MUTED))

    # (C) виявлення аномалій — щільна хмара + один вигнанець
    els.append(fitbox(490, 46, 210, 30, "Виявлення аномалій", size=14, bold=True, fill="#fdecea", stroke=POS))
    dense = [(560, 170), (580, 185), (555, 195), (575, 205), (590, 175), (565, 210)]
    for (x, y) in dense:
        els.append(circle(x, y, 6, fill="#eceff1", stroke=grey, sw=1.8))
    els.append(circle(660, 130, 8, fill="#fdecea", stroke=POS, sw=2.4))
    els.append(text(660, 158, "?", size=15, color=POS, bold=True))
    els.append(text(595, 260, "знайти вигнанця", size=11, color=MUTED))

    render(os.path.join(IMG, "three-families.svg"), W, H, *els)


# ── 3. Цикл k-середніх (присвоїти → пересунути) ──────────────────────────────
def fig_kmeans_loop():
    W, H = 700, 300
    els = []
    els.append(text(W / 2, 26, "Цикл k-середніх: присвоїти → пересунути → повторити", size=16, bold=True))

    # три кроки в ряд
    b1, w1, _ = textbox(130, 150, ["1. Кинути k центрів", "навмання"], size=13,
                        fill="#eef7f0", stroke=FIELD, min_w=180)
    b2, w2, _ = textbox(350, 150, ["2. Присвоїти кожну", "точку найближчому", "центру"], size=13,
                        fill=FILL, stroke=LINE, min_w=180)
    b3, w3, _ = textbox(570, 150, ["3. Пересунути центр", "у середину своїх", "точок"], size=13,
                        fill=FILL, stroke=LINE, min_w=180)
    els += [b1, b2, b3]

    els.append(arrow(130 + w1 / 2, 150, 350 - w2 / 2, 150, color=INK, sw=2))
    els.append(arrow(350 + w2 / 2, 150, 570 - w3 / 2, 150, color=INK, sw=2))

    # петля назад від 3 до 2
    els.append('<path d="M 570 %.0f Q 460 250 350 %.0f" fill="none" stroke="%s" stroke-width="2" marker-end="url(#arrow)"/>'
               % (150 + 40, 150 + 40, INK))
    els.append(text(460, 262, "поки центри рухаються", size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "kmeans-loop.svg"), W, H, *els)


# ── 4. Родовід k-середніх: чотири незалежні винаходи ─────────────────────────
def fig_kmeans_lineage():
    W, H = 720, 430
    els = []
    els.append(text(W / 2, 26, "Одна ідея — чотири незалежні винаходи", size=17, bold=True))

    # горизонтальна вісь часу
    y0 = 90
    els.append(line(60, y0, 660, y0, color=MUTED, sw=2))
    for (xx, yr) in [(90, "1956"), (250, "1957"), (450, "1965"), (610, "1967")]:
        els.append(line(xx, y0 - 6, xx, y0 + 6, color=MUTED, sw=2))
        els.append(text(xx, y0 - 14, yr, size=13, color=MUTED, bold=True))

    # чотири картки-винахідники під своїми роками
    b1, w1, h1 = textbox(120, 165, ["Гуго Штайнгаус", "матем., Польща",
                                    "поділ тіл на частини"], size=12,
                          fill="#eef7f0", stroke=FIELD, min_w=175)
    b2, w2, h2 = textbox(300, 165, ["Стюарт Ллойд", "Bell Labs, зв'язок",
                                    "квантування сигналу"], size=12,
                          fill="#eaf0fd", stroke=NEG, min_w=175)
    b3, w3, h3 = textbox(490, 275, ["Едвард Форджі", "статистика",
                                    "кластер-аналіз"], size=12,
                          fill=FILL, stroke=LINE, min_w=175)
    b4, w4, h4 = textbox(600, 165, ["Джеймс Маккуїн", "статистика",
                                    "дав НАЗВУ «k-means»"], size=12,
                          fill="#fdf3e0", stroke=POS, min_w=175)
    els += [b1, b2, b3, b4]

    # тонкі поводки від осі до карток
    els.append(line(90, y0, 120, 165 - h1 / 2, color=MUTED, sw=1, dash="3 3"))
    els.append(line(250, y0, 300, 165 - h2 / 2, color=MUTED, sw=1, dash="3 3"))
    els.append(line(450, y0, 490, 275 - h3 / 2, color=MUTED, sw=1, dash="3 3"))
    els.append(line(610, y0, 600, 165 - h4 / 2, color=MUTED, sw=1, dash="3 3"))

    # спільна ідея внизу — усі стрілки збігаються в одне
    hub_y = 375
    hb, hbw, _ = textbox(360, hub_y, ["ТА САМА ІДЕЯ:", "центри = середні, повторюй"],
                         size=13, bold=True, fill="#f4f6f8", stroke=FIELD, min_w=300)
    els.append(hb)
    for (cx, cyb) in [(120, 165 + h1 / 2), (300, 165 + h2 / 2),
                      (490, 275 + h3 / 2), (600, 165 + h4 / 2)]:
        els.append(line(cx, cyb, 360, hub_y - 22, color=MUTED, sw=1.2, dash="4 3"))

    els.append(text(360, 415, "ніхто не «винайшов» — усі перевідкрили",
                    size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "kmeans-lineage.svg"), W, H, *els)


if __name__ == "__main__":
    fig_labeled_vs_not()
    fig_three_families()
    fig_kmeans_loop()
    fig_kmeans_lineage()
    print("figs done")

# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_pipeline():
    """Конвеєр як складальна лінія: сире Байєр → три домени → чистий кадр."""
    W, H = 940, 430
    parts = []
    parts.append(text(W / 2, 28, "ISP-конвеєр: сире з матриці → чистий кадр", size=17, bold=True))

    # три домени-смуги
    bands = [
        (40, 295, "Байєр-домен (одноколірна мозаїка)", "#eef4ff"),
        (350, 235, "RGB-домен (повний колір)", "#eafaf0"),
        (600, 300, "YUV-домен (яскравість+колір)", "#fff4e8"),
    ]
    by = 60
    bh = 300
    for x, w, label, fill in bands:
        parts.append(rect(x, by, w, bh, fill=fill, stroke=MUTED, sw=1.2, rx=10))
        parts.append(text(x + w / 2, by + bh - 12, label, size=11, color=MUTED, bold=True))

    # вузли-стадії
    def stage(cx, cy, label, color=LINE):
        f, w, h = textbox(cx, cy, label, size=11, pad=7, min_w=120, stroke=color)
        parts.append(f)
        return w

    col1 = 168
    ys = [95, 138, 181, 224]
    labels1 = ["Чорний рівень\n(відняти темновий)",
               "Биті пікселі\n(залатати)",
               "Віньєтка лінзи\n(підняти краї)",
               "Баланс білого\n(зрівняти R,G,B)"]
    for y, lab in zip(ys, labels1):
        stage(col1, y, lab, color=NEG)
    # стрілка вниз через перший домен
    parts.append(arrow(col1, 250, col1, 268, color=MUTED))
    stage(col1, 285 - 6, "Демозаїка →", color=POS)

    col2 = 467
    stage(col2, 110, "Колірна матриця\n(вірний відтінок)", color=POS)
    stage(col2, 165, "Гама / тонова\nкрива", color=POS)
    parts.append(arrow(col2, 200, col2, 222, color=MUTED))
    stage(col2, 240, "RGB → YUV →", color=POS)

    col3 = 745
    labels3 = ["Прибрати шум\n(зберегти краї)",
               "Підвищити\nрізкість",
               "Контраст,\nнасиченість"]
    for y, lab in zip([110, 168, 226], labels3):
        stage(col3, y, lab, color=FIELD)

    # вхід / вихід
    parts.append(textbox(168, 360, "сирий Байєр\n(RAW з матриці)", size=11, pad=7, fill="#f0f0f0", stroke=MUTED)[0])
    parts.append(arrow(168, 305, 168, 345, color=LINE))
    parts.append(textbox(745, 360, "чистий кадр\n(до кодека / зору)", size=11, pad=7, fill="#eafaf0", stroke=FIELD)[0])
    parts.append(arrow(745, 250, 745, 345, color=LINE))

    # горизонтальні переходи між доменами
    parts.append(arrow(232, 285, 405, 250, color=LINE))
    parts.append(arrow(530, 240, 685, 226, color=LINE))

    render(os.path.join(OUT, 'pipeline.svg'), W, H, *parts)


def fig_raw_is_ugly():
    """Чому сирий кадр негодящий: чотири дефекти, що їх лагодять перші стадії."""
    W, H = 900, 320
    parts = []
    parts.append(text(W / 2, 28, "Сирий кадр негодящий — що лагодять перші стадії", size=17, bold=True))

    cards = [
        (40, "Темний п'єдестал", "Навіть у пітьмі лічильник\nдає не 0, а ~64. Усе фото\nпідняте — сіра поволока.",
         "Чорний рівень: відняти", NEG),
        (260, "Биті пікселі", "Кілька комірок «залипли»\nяскраві чи мертві —\nкольорові цятки на кадрі.",
         "Латка: взяти середнє сусідів", NEG),
        (480, "Темні кути", "Лінза пропускає в центр\nбільше світла, ніж у кути —\nкадр темніє до країв.",
         "Віньєтка: підняти краї", NEG),
        (700, "Зелений відтінок", "Матриця ловить більше\nзеленого. Білий аркуш\nвиходить зеленавим.",
         "Баланс білого: зрівняти", NEG),
    ]
    cw = 180
    for x, title_, body, fix, col in cards:
        parts.append(rect(x, 52, cw, 200, fill="#fff6f6", stroke=col, sw=1.4, rx=10))
        parts.append(text(x + cw / 2, 78, title_, size=13, bold=True, color=col))
        parts.append(mtext(x + cw / 2, 108, body, size=11, color=INK, lh=1.35))
        parts.append(line(x + 14, 196, x + cw - 14, 196, color=MUTED, sw=1, dash="3,3"))
        parts.append(fitbox(x + 12, 208, cw - 24, 36, fix, size=11, fill="#eafaf0", stroke=FIELD, bold=True))

    render(os.path.join(OUT, 'raw-is-ugly.svg'), W, H, *parts)


def fig_on_drone():
    """Де ISP сидить на апараті: між матрицею і двома споживачами кадру."""
    W, H = 820, 360
    parts = []
    parts.append(text(W / 2, 28, "Де ISP сидить на апараті", size=17, bold=True))

    # матриця
    parts.append(textbox(120, 170, "Матриця\n(сирий Байєр)", size=12, pad=10, fill="#f0f0f0", stroke=MUTED, bold=True)[0])
    # ISP
    f, w, h = textbox(370, 170, "ISP\n(конвеєр стадій)", size=13, pad=14, fill="#eef4ff", stroke=NEG, bold=True, min_w=150)
    parts.append(f)
    parts.append(arrow(190, 170, 290, 170, color=LINE))
    parts.append(text(240, 158, "RAW", size=10, color=MUTED))

    # два споживачі
    parts.append(textbox(655, 105, "Кодек → лінк\n(H.264 у радіо)", size=12, pad=10, fill="#fff4e8", stroke=POS, bold=True)[0])
    parts.append(textbox(655, 250, "Детектор / зір\n(на борту)", size=12, pad=10, fill="#eafaf0", stroke=FIELD, bold=True)[0])
    parts.append(arrow(455, 150, 558, 110, color=LINE))
    parts.append(arrow(455, 195, 558, 245, color=LINE))
    parts.append(text(515, 118, "чистий\nкадр", size=10, color=MUTED, anchor="middle"))

    # підпис-висновок
    parts.append(fitbox(120, 300, 580, 40,
                        "Сире з матриці нікуди не годиться напряму — ISP робить його придатним і кодекові, і детекторові.",
                        size=12, fill="#f4f6f8", stroke=MUTED))

    render(os.path.join(OUT, 'on-drone.svg'), W, H, *parts)


def fig_isp_history():
    """Як кадр перейшов із коду в залізо: три ери + вісь зростання роботи."""
    W, H = 960, 430
    parts = []
    parts.append(text(W / 2, 28, "Як обробка кадру перейшла з коду в залізо", size=17, bold=True))

    # три ери-колонки
    cols = [
        (40, 285, "1990-ті", "Код на процесорі / DSP", NEG, "#eef2fb",
         ["Конвеєр = програма", "≈1 секунда на кадр", "Відео неможливе",
          "Гнучко, але повільно", "й ненажерливо"]),
        (345, 280, "поч. 2000-х", "Окрема мікросхема / IP-ядро", FIELD, "#eafaf0",
         ["Canon DIGIC (2002):", "усе в один чип", "Nikon Expeed, Sony Bionz…",
          "ISP-ядра ліцензують", "(Apical, iridix)"]),
        (645, 275, "2011 → 2015", "ISP вбудований у SoC", POS, "#fff4e8",
         ["Apple A5 — перший", "власний ISP у чипі", "A7/iPhone 5S (2013):",
          "локальне тонове відобр.", "Qualcomm Spectra/SD 820"]),
    ]
    cy0 = 58
    ch = 232
    for x, w, era, head, col, fill, rows in cols:
        parts.append(rect(x, cy0, w, ch, fill=fill, stroke=col, sw=1.6, rx=12))
        parts.append(text(x + w / 2, cy0 + 26, era, size=13, bold=True, color=col))
        parts.append(fitbox(x + 14, cy0 + 38, w - 28, 34, head,
                            size=12, fill="#ffffff", stroke=col, bold=True))
        ry = cy0 + 92
        for r in rows:
            parts.append(text(x + w / 2, ry, r, size=11, color=INK))
            ry += 21

    # стрілки переходу між ерами
    parts.append(arrow(325, cy0 + ch / 2, 345, cy0 + ch / 2, color=LINE, sw=2.2))
    parts.append(arrow(625, cy0 + ch / 2, 645, cy0 + ch / 2, color=LINE, sw=2.2))

    # вісь зростання роботи під колонками
    ay = 322
    parts.append(arrow(40, ay, 920, ay, color=MUTED, sw=2))
    parts.append(text(40, ay + 20, "мегапікселі / кадр", size=10, color=MUTED, anchor="start"))
    parts.append(text(920, ay + 20, "0.6 млрд оп/с (відео)", size=10, color=MUTED, anchor="end"))
    parts.append(text(W / 2, ay - 8, "роботи дедалі більше →", size=11, color=MUTED, bold=True))

    # підсумок-висновок
    parts.append(fitbox(40, 355, 880, 56,
                        "Наскрізне правило: щойно роботи стає забагато для універсального процесора, "
                        "її віддають спеціалізованому залізу — спершу окремому, потім вбудованому ближче до даних.",
                        size=12, fill="#f4f6f8", stroke=MUTED))

    render(os.path.join(OUT, 'isp-history.svg'), W, H, *parts)


if __name__ == '__main__':
    fig_pipeline()
    fig_raw_is_ugly()
    fig_on_drone()
    fig_isp_history()
    print("OK")

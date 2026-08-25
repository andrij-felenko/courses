# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_chicken_egg():
    """Порочне коло: щоб зкомпілювати компілятор мовою X, треба компілятор мови X."""
    W, H = 640, 300
    parts = []
    cx, cy, r = 320, 165, 92

    # Дві коробки на колі
    b1, w1, h1 = textbox(320, 73, ["Компілятор мови X", "написаний мовою X"],
                         size=14, bold=False, fill="#eaf0fd", stroke=NEG)
    b2, w2, h2 = textbox(320, 258, ["Щоб його зібрати,", "потрібен компілятор X"],
                         size=14, fill="#fdecea", stroke=POS)
    # Дугові стрілки між ними (по колу)
    def curve(x1, y1, x2, y2, bend, color):
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2 + bend
        return ('<path d="M%.1f %.1f Q%.1f %.1f %.1f %.1f" fill="none" stroke="%s" '
                'stroke-width="2.2" marker-end="url(#arrow)"/>' % (x1, y1, mx, my, x2, y2, color))

    parts.append(curve(430, 88, 430, 243, 0, NEG))
    parts.append(curve(210, 243, 210, 88, 0, POS))
    parts.append(text(505, 168, "потрібен", size=12, color=NEG, italic=True))
    parts.append(text(120, 168, "щоб зібрати", size=12, color=POS, italic=True))
    parts.append(b1)
    parts.append(b2)
    parts.append(text(320, 165, "?", size=48, color=MUTED, bold=True))

    render(os.path.join(OUT, 'chicken-egg.svg'), W, H, *parts,
           title="Курка чи яйце: замкнене коло самопідняття")


def fig_bootstrap_chain():
    """Ланцюг: ручний стартовий → перша збірка → фінальний компілятор."""
    W, H = 720, 340
    parts = []
    colw, colh, top = 190, 128, 70
    xs = [40, 265, 490]

    titles = ["Стартовий (stage 0)", "Перший (stage 1)", "Фінальний (stage 2)"]
    bodies = [
        ["урізана мова X", "написаний РУКАМИ", "іншою мовою / асемблером", "повільний, кривий"],
        ["повна мова X", "джерело мовою X", "зібраний стартовим", "уже вміє все"],
        ["повна мова X", "те саме джерело", "зібраний першим", "оптимізований"],
    ]
    fills = ["#fdecea", "#f4f6f8", "#eafaf0"]
    strokes = [POS, LINE, FIELD]

    for i in range(3):
        x = xs[i]
        parts.append(rect(x, top, colw, colh, fill=fills[i], stroke=strokes[i], sw=1.8))
        parts.append(text(x + colw / 2, top - 12, titles[i], size=13, bold=True))
        # рядки всередині
        for j, ln in enumerate(bodies[i]):
            parts.append(text(x + colw / 2, top + 30 + j * 24, ln, size=12.5,
                              color=INK if j == 0 else MUTED, bold=(j == 0)))

    # Стрілки «компілює джерело у»
    ay = top + colh / 2
    parts.append(arrow(xs[0] + colw + 6, ay, xs[1] - 6, ay, color=INK, sw=2.2))
    parts.append(arrow(xs[1] + colw + 6, ay, xs[2] - 6, ay, color=INK, sw=2.2))
    parts.append(text((xs[0] + colw + xs[1]) / 2, ay - 12, "компілює", size=11.5, color=MUTED, italic=True))
    parts.append(text((xs[1] + colw + xs[2]) / 2, ay - 12, "перекомпілює", size=11.5, color=MUTED, italic=True))

    # Нижній підпис: stage1 і stage2 з ОДНОГО джерела → байти мають збігтися
    yb = top + colh + 42
    b, bw, bh = textbox(360, yb + 18, ["Stage 1 і Stage 2 — з ТОГО САМОГО джерела.",
                                       "Якщо байти збіглися — самопідняття зійшлося."],
                        size=13, fill="#eafaf0", stroke=FIELD)
    parts.append(b)

    render(os.path.join(OUT, 'bootstrap-chain.svg'), W, H, *parts,
           title="Ланцюг самопідняття: руками → перший → фінальний")


def fig_trusting_trust():
    """Отрута живе у бінарнику й переносить себе, хоч у джерелі її нема."""
    W, H = 700, 330
    parts = []

    # Джерело (чисте) — ліворуч
    src, sw_, sh = textbox(120, 90, ["Джерело компілятора", "ЧИСТЕ — жодного", "рядка про закладку"],
                           size=13, fill="#eafaf0", stroke=FIELD)
    parts.append(src)

    # Заражений бінарник — центр
    bx = rect(300, 55, 200, 96, fill="#fdecea", stroke=POS, sw=2)
    parts.append(bx)
    parts.append(text(400, 78, "Заражений компілятор", size=13, bold=True, color=POS))
    parts.append(text(400, 100, "(бінарник)", size=12, color=MUTED))
    parts.append(text(400, 124, "таємно вставляє закладку", size=11.5, color=POS, italic=True))

    # Новий бінарник — праворуч (теж заражений)
    nb = rect(300, 200, 200, 96, fill="#fdecea", stroke=POS, sw=2)
    parts.append(nb)
    parts.append(text(400, 223, "Новий компілятор", size=13, bold=True, color=POS))
    parts.append(text(400, 245, "теж ЗАРАЖЕНИЙ", size=12, color=POS, bold=True))
    parts.append(text(400, 269, "хоч джерело чисте", size=11.5, color=MUTED, italic=True))

    # Стрілки: джерело + заражений → новий заражений
    parts.append(arrow(210, 100, 296, 100, color=INK, sw=2))
    parts.append(arrow(400, 155, 400, 196, color=POS, sw=2.4))
    parts.append(text(430, 178, "копіює отруту в себе", size=11.5, color=POS, italic=True, anchor="start"))

    # Петля назад: новий стає інструментом для наступної збірки
    parts.append('<path d="M500 248 Q640 248 640 150 Q640 55 502 90" fill="none" '
                 'stroke="%s" stroke-width="2.2" stroke-dasharray="6 4" '
                 'marker-end="url(#arrow)"/>' % POS)
    parts.append(text(632, 170, "наступна", size=11, color=POS, anchor="end", italic=True))
    parts.append(text(632, 186, "збірка", size=11, color=POS, anchor="end", italic=True))

    render(os.path.join(OUT, 'trusting-trust.svg'), W, H, *parts,
           title="Довіряти довірі: отрута живе в бінарнику, не в джерелі")


def fig_tdiagram_anatomy():
    """Анатомія Т-діаграми Братмана: одна Т із трьома підписами + стик двох Т."""
    W, H = 720, 360
    parts = []

    def tshape(cx, top, ww, arm_h, stem_h, src, tgt, impl,
               fill="#eaf0fd", stroke=NEG, tcolor=INK):
        """Т-фігура: горизонтальна перекладина (вхід|вихід) + ніжка (написана чим)."""
        stem_w = ww * 0.40
        # перекладина
        bar = rect(cx - ww / 2, top, ww, arm_h, fill=fill, stroke=stroke, sw=1.8, rx=4)
        # ніжка
        stem = rect(cx - stem_w / 2, top + arm_h, stem_w, stem_h,
                    fill=fill, stroke=stroke, sw=1.8, rx=4)
        p = [bar, stem]
        # підписи: вхід ліворуч, вихід праворуч у перекладині
        p.append(text(cx - ww / 4, top + arm_h / 2 + 5, src, size=13, color=tcolor, bold=True))
        p.append(text(cx + ww / 4, top + arm_h / 2 + 5, tgt, size=13, color=tcolor, bold=True))
        # роздільна лінійка в перекладині
        p.append(line(cx, top + 4, cx, top + arm_h - 4, color=stroke, sw=1.2))
        # підпис ніжки — мова реалізації
        p.append(text(cx, top + arm_h + stem_h / 2 + 5, impl, size=13, color=tcolor, bold=True))
        return p

    # Ліворуч — одна Т з поясненнями кутів
    x1 = 190
    parts += tshape(x1, 90, 210, 54, 84, "X", "маш. код", "C")
    parts.append(text(x1, 62, "Один компілятор", size=13, bold=True, color=MUTED))
    # виноски-підписи
    parts.append(text(x1 - 148, 120, "що читає", size=11.5, color=NEG, anchor="middle", italic=True))
    parts.append(text(x1 + 150, 120, "у що перекладає", size=11.5, color=NEG, anchor="middle", italic=True))
    parts.append(text(x1, 250, "чим сам написаний", size=11.5, color=NEG, italic=True))
    parts.append(line(x1 - 148, 128, x1 - 92, 116, color=MUTED, sw=1))
    parts.append(line(x1 + 150, 128, x1 + 92, 116, color=MUTED, sw=1))
    parts.append(line(x1, 242, x1, 176, color=MUTED, sw=1, dash="3 3"))

    # Праворуч — дві Т стикуються (ніжка = вихід сусідньої)
    x2 = 540
    # верхня Т: компілятор мовою X, написаний C
    parts += tshape(x2, 74, 180, 48, 60, "X", "маш.", "C",
                    fill="#eafaf0", stroke=FIELD)
    # нижня Т: наявний C-компілятор (C → маш., написаний маш.)
    parts += tshape(x2, 182, 180, 48, 60, "C", "маш.", "маш.",
                    fill="#f4f6f8", stroke=LINE)
    parts.append(text(x2, 300, "«C» ніжки верхньої = «C» входу нижньої", size=11.5,
                      color=MUTED, italic=True))
    parts.append(text(x2, 320, "стикуються — і збірка читається", size=11.5,
                      color=MUTED, italic=True))
    parts.append(text(x2, 50, "Дві Т в стик", size=13, bold=True, color=MUTED))

    render(os.path.join(OUT, 'tdiagram-anatomy.svg'), W, H, *parts,
           title="Діаграма-надгробок Братмана: три підписи однієї Т")


# ── Фігури для вставки hist-trusting-trust.md ────────────────────────────────
def fig_three_bugs():
    """Три закладки атаки Томпсона: очевидна → самовідтворна → та, що ховає перші дві."""
    W, H = 720, 360
    parts = []
    xs = [40, 260, 480]
    top, colw, colh = 80, 200, 150

    titles = ["Закладка 1", "Закладка 2", "Закладка 3"]
    subs = ["у програмі входу", "у компіляторі", "у компіляторі"]
    bodies = [
        ["впізнає таємний", "пароль → пускає", "чужого як root", "", "у ДЖЕРЕЛІ видно"],
        ["впізнає джерело", "входу й вставляє", "туди закладку 1", "", "у ДЖЕРЕЛІ видно"],
        ["впізнає джерело", "компілятора й", "вписує 1 і 2", "в новий бінарник", "джерело ЧИСТЕ"],
    ]
    fills = ["#fdecea", "#fdecea", "#f4eafb"]
    strokes = [POS, POS, "#8e44ad"]
    seen = [MUTED, MUTED, "#8e44ad"]

    for i in range(3):
        x = xs[i]
        parts.append(rect(x, top, colw, colh, fill=fills[i], stroke=strokes[i], sw=2))
        parts.append(text(x + colw / 2, top - 32, titles[i], size=14, bold=True, color=strokes[i]))
        parts.append(text(x + colw / 2, top - 12, subs[i], size=12, color=MUTED, italic=True))
        for j, ln in enumerate(bodies[i]):
            if not ln:
                continue
            last = (j == len(bodies[i]) - 1)
            parts.append(text(x + colw / 2, top + 30 + j * 23, ln, size=12.5,
                              color=seen[i] if last else INK,
                              bold=last, italic=last))

    ay = top + colh / 2
    parts.append(arrow(xs[1] - 6, ay, xs[0] + colw + 6, ay, color="#8e44ad", sw=2))
    parts.append(text((xs[0] + colw + xs[1]) / 2, ay - 10, "відтворює", size=11, color="#8e44ad", italic=True))
    parts.append(arrow(xs[2] - 6, ay + 30, xs[1] + colw + 6, ay + 30, color="#8e44ad", sw=2))
    parts.append(text((xs[1] + colw + xs[2]) / 2, ay + 20, "ховає обидві", size=11, color="#8e44ad", italic=True))

    b, bw, bh = textbox(360, top + colh + 40,
                        ["Джерело компілятора можна вичистити до останнього рядка —",
                         "закладка 3 живе в бінарнику й щоразу переписує 1, 2 і саму себе."],
                        size=12.5, fill="#f4eafb", stroke="#8e44ad")
    parts.append(b)

    render(os.path.join(OUT, 'three-bugs.svg'), W, H, *parts,
           title="Триетапна атака: три закладки, що прикривають одна одну")


def fig_ddc():
    """Подвійна компіляція різними компіляторами: розбіжність байтів викриває отруту."""
    W, H = 720, 340
    parts = []

    src, sw_, sh = textbox(360, 62, ["Джерело компілятора A", "(те саме, читане обома)"],
                           size=13, fill="#eaf0fd", stroke=NEG)
    parts.append(src)

    la = rect(60, 140, 240, 60, fill="#fdecea", stroke=POS, sw=2)
    parts.append(la)
    parts.append(text(180, 165, "Підозрюваний A збирає", size=12.5, bold=True))
    parts.append(text(180, 185, "джерело A → бінарник X", size=12, color=MUTED))

    ra = rect(420, 140, 240, 60, fill="#eafaf0", stroke=FIELD, sw=2)
    parts.append(ra)
    parts.append(text(540, 162, "Незалежний T збирає джерело A,", size=11.5, bold=True))
    parts.append(text(540, 182, "тим результатом — знову → Y", size=11.5, color=MUTED))

    parts.append(arrow(300, 92, 180, 136, color=POS, sw=2))
    parts.append(arrow(420, 92, 540, 136, color=FIELD, sw=2))

    cmp_, cw, ch = textbox(360, 255, ["X  vs  Y   —   біт-у-біт?"],
                           size=15, bold=True, fill="#fff", stroke=INK)
    parts.append(cmp_)
    parts.append(arrow(180, 200, 320, 236, color=POS, sw=2))
    parts.append(arrow(540, 200, 400, 236, color=FIELD, sw=2))

    parts.append(text(150, 305, "збіглися → джерело чесне", size=12, color=FIELD, bold=True))
    parts.append(text(560, 305, "різні → у X отрута", size=12, color=POS, bold=True))

    render(os.path.join(OUT, 'ddc.svg'), W, H, *parts,
           title="Подвійна компіляція різними: незалежний свідок проти отрути")


# ── Фігура для вставки comp-reproducible-builds.md ───────────────────────────
def fig_repro_leaks():
    """Три щілини, крізь які оточення тече у збірку; нижня гілка — їх заткнуто."""
    W, H = 760, 448
    parts = []

    # Верхня гілка: звичайна збірка з протіканнями
    top = 108
    # джерело + інструкції (зелене — те, що бачать усі)
    src, sw_, sh = textbox(115, top + 26, ["Джерело", "+ інструкції"],
                           size=13, bold=True, fill="#eafaf0", stroke=FIELD)
    parts.append(src)
    # блок збірки
    bx, bw, bh = 250, 150, 66
    parts.append(rect(bx, top, bw, bh, fill="#f4f6f8", stroke=LINE, sw=1.8))
    parts.append(text(bx + bw / 2, top + 27, "Збірка", size=14, bold=True))
    parts.append(text(bx + bw / 2, top + 48, "компілятор + лінкер", size=11, color=MUTED))
    # бінарник (у кожного свій)
    ob, ow, oh = textbox(600, top + 26, ["Бінарник", "у КОЖНОГО свій"],
                         size=13, bold=True, fill="#fdecea", stroke=POS)
    parts.append(ob)
    parts.append(arrow(180, top + 33, bx - 6, top + 33, color=INK, sw=2))
    parts.append(arrow(bx + bw + 6, top + 33, 540, top + 33, color=POS, sw=2))

    # три джерела протікання — над блоком збірки
    leaks = [("Годинник", "дата → в образ"),
             ("Файлова система", "порядок · тека"),
             ("Середовище", "машина · локаль")]
    lx = [bx - 60, bx + bw / 2, bx + bw + 60]
    ly = top - 42
    for i, (a, b) in enumerate(leaks):
        lb, lw, lh = textbox(lx[i], ly, [a, b], size=10.5, bold=False,
                             fill="#fdecea", stroke=POS, pad=6)
        parts.append(lb)
        parts.append(arrow(lx[i], ly + 16, lx[i] if i != 0 else bx + 20,
                           top - 2 if i == 1 else top + 4, color=POS, sw=1.6))
    parts.append(text(bx + bw / 2, ly - 26, "оточення тече у вихід", size=12,
                      color=POS, italic=True, bold=True))

    # роздільник
    parts.append(line(40, 232, W - 40, 232, color=MUTED, sw=1, dash="4 4"))
    parts.append(text(W / 2, 250, "— те саме, але кожне джерело недетермінізму зафіксовано —",
                      size=12, color=MUTED, italic=True))

    # Нижня гілка: полагоджена збірка
    bot = 328
    src2, s2w, s2h = textbox(115, bot + 26, ["Джерело", "+ інструкції"],
                             size=13, bold=True, fill="#eafaf0", stroke=FIELD)
    parts.append(src2)
    parts.append(rect(bx, bot, bw, bh, fill="#f4f6f8", stroke=LINE, sw=1.8))
    parts.append(text(bx + bw / 2, bot + 27, "Збірка", size=14, bold=True))
    parts.append(text(bx + bw / 2, bot + 48, "чиста функція", size=11, color=MUTED))
    ob2, o2w, o2h = textbox(600, bot + 26, ["Бінарник", "в УСІХ однаковий"],
                            size=13, bold=True, fill="#eafaf0", stroke=FIELD)
    parts.append(ob2)
    parts.append(arrow(180, bot + 33, bx - 6, bot + 33, color=INK, sw=2))
    parts.append(arrow(bx + bw + 6, bot + 33, 540, bot + 33, color=FIELD, sw=2))

    fixes = [("час", "= з джерела"),
             ("порядок", "= відсортовано"),
             ("шляхи", "= знеособлено")]
    fy = bot - 40
    for i, (a, b) in enumerate(fixes):
        fb, fw, fh = textbox(lx[i], fy, [a + " " + b], size=10.5, bold=False,
                             fill="#eafaf0", stroke=FIELD, pad=6)
        parts.append(fb)
    parts.append(text(bx + bw / 2, fy - 22, "у вихід тече лише зелене",
                      size=12, color=FIELD, italic=True, bold=True))

    render(os.path.join(OUT, 'repro-leaks.svg'), W, H, *parts,
           title="Три щілини недетермінізму — і як їх заткнути")


if __name__ == '__main__':
    fig_chicken_egg()
    fig_bootstrap_chain()
    fig_trusting_trust()
    fig_tdiagram_anatomy()
    fig_three_bugs()
    fig_ddc()
    fig_repro_leaks()
    print("figures written to", OUT)

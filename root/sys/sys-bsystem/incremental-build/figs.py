# -*- coding: utf-8 -*-
"""Фігури до теми «Інкрементальна збірка: як вирішують, що застаріло»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

DIRTY = "#fdecea"     # перезбирається
CLEAN = "#eaf7ef"     # лишається чинним
PANEL = "#f8fafc"


def node(cx, cy, label, fill=FILL, stroke=LINE, bold=False, size=15, sw=1.5):
    frag, w, h = textbox(cx, cy, label, size=size, fill=fill, stroke=stroke,
                         bold=bold, sw=sw)
    return frag, (cx, cy, w, h)


def down(a, b, color=LINE, sw=1.8):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return arrow(ax, ay + ah / 2 + 3, bx, by - bh / 2 - 5, color=color, sw=sw)


def down_dashed(a, b, color=MUTED, sw=1.6):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return line(ax, ay + ah / 2 + 3, bx, by - bh / 2 - 5,
                color=color, sw=sw, dash="6,6")


# ── 1. Дві сім'ї доказів і те, що кожна здатна побачити ─────────────────────
def fig_two_families():
    W, H = 1040, 570
    p = []

    # ліва панель — порівняння з теперішнім станом
    p.append(rect(50, 62, 430, 336, fill=PANEL, stroke=MUTED, sw=1.5))
    p.append(text(265, 92, "Сім'я A · звірити теперішнє з теперішнім",
                  size=14.5, bold=True))
    p.append(fitbox(78, 116, 158, 62, "входи\nзараз", size=14, fill=BG))
    p.append(text(265, 154, "≟", size=26, bold=True, color=NEG))
    p.append(fitbox(294, 116, 158, 62, "вихід\nзараз", size=14, fill=BG))
    p.append(fitbox(78, 204, 374, 52, "порівнюємо мітки часу файлів", size=13.5))
    p.append(fitbox(78, 282, 374, 96,
                    "зберігати нічого не треба —\nале видно лише те,\nщо лишає слід у файлах",
                    size=13.5, fill=BG, stroke=MUTED))

    # права панель — порівняння із записом
    p.append(rect(560, 62, 430, 336, fill=PANEL, stroke=MUTED, sw=1.5))
    p.append(text(775, 92, "Сім'я Б · звірити теперішнє із записом",
                  size=14.5, bold=True))
    p.append(fitbox(588, 116, 158, 62, "запис минулого\nпрогону", size=13.5, fill=BG))
    p.append(text(775, 154, "≟", size=26, bold=True, color=NEG))
    p.append(fitbox(804, 116, 158, 62, "стан\nзараз", size=14, fill=BG))
    p.append(fitbox(588, 204, 374, 52, "порівнюємо ключ, геші входів і команду",
                    size=13.5))
    p.append(fitbox(588, 282, 374, 96,
                    "потрібне сховище —\nзате видно все,\nщо записали",
                    size=13.5, fill=BG, stroke=MUTED))

    # зміна, що не лишає сліду у файлах
    ch, cw, chh = textbox(520, 492, "змінили  -O2 → -O0\nжоден файл не змінився",
                          size=14.5, bold=True, fill=BG, stroke=NEG, sw=2)
    p.append(ch)

    p.append(line(430, 464, 282, 402, color=POS, sw=2, dash="7,6"))
    p.append(arrow(610, 464, 768, 402, color=FIELD, sw=2))

    lf, _, _ = textbox(196, 434, "не видно", size=13, fill=DIRTY, stroke=POS, pad=8)
    rf, _, _ = textbox(858, 434, "видно", size=13, fill=CLEAN, stroke=FIELD, pad=8)
    p += [lf, rf]

    render(os.path.join(IMG, "two-families.svg"), W, H, *p,
           title="Що кожна сім'я доказів здатна побачити")


# ── 2. Та сама правка з ранньою відсічкою і без неї ─────────────────────────
def fig_early_cutoff():
    W, H = 1060, 640
    p = []
    p.append(line(530, 58, 530, 600, color=MUTED, sw=1.2, dash="5,7"))

    for cx, cut in ((268, False), (792, True)):
        head = "без ранньої відсічки" if not cut else "з ранньою відсічкою"
        p.append(text(cx, 74, head, size=15.5, bold=True,
                      color=POS if not cut else FIELD))

        src, g_src = node(cx, 126, "config.h.in", fill=BG, stroke=POS,
                          bold=True, sw=2.2)
        gen, g_gen = node(cx, 208, "генератор", fill=DIRTY, stroke=POS, sw=2)
        hdr, g_hdr = node(cx, 290, "config.h", fill=DIRTY, stroke=POS, sw=2)

        objfill = DIRTY if not cut else CLEAN
        objstroke = POS if not cut else FIELD
        objs = []
        for dx, name in ((-124, "a.o"), (0, "b.o"), (124, "c.o")):
            f, g = node(cx + dx, 392, name, fill=objfill, stroke=objstroke, sw=2)
            objs.append((f, g))
        app, g_app = node(cx, 480, "app", fill=objfill, stroke=objstroke,
                          bold=True, sw=2)

        p += [src, gen, hdr] + [f for f, _ in objs] + [app]
        p.append(down(g_src, g_gen, color=POS))
        p.append(down(g_gen, g_hdr, color=POS))

        edge = down if not cut else down_dashed
        col = POS if not cut else MUTED
        for _, g in objs:
            p.append(edge(g_hdr, g, color=col))
            p.append(edge(g, g_app, color=col))

        note = ("команда переписала файл —\nmtime зрушив, хоч байти ті самі"
                if not cut else
                "вміст той самий —\nmtime не зрушив, хвиля спинилася")
        nf, _, _ = textbox(cx + 196, 290, note, size=12.5,
                           fill=DIRTY if not cut else CLEAN,
                           stroke=POS if not cut else FIELD, pad=9)
        p.append(nf)

        total = "перезібрано 5 задач" if not cut else "перезібрано 1 задачу"
        tf, _, _ = textbox(cx, 566, total, size=14.5, bold=True,
                           fill=DIRTY if not cut else CLEAN,
                           stroke=POS if not cut else FIELD)
        p.append(tf)

    render(os.path.join(IMG, "early-cutoff.svg"), W, H, *p,
           title="Генератор виконується в обох випадках — різниця в тому, чи спитали, що він записав")


# ── 3. Правка, що потрапила у вікно між стартом команди й записом виходу ────
def fig_build_race():
    W, H = 1010, 440
    p = []

    y = 250
    p.append(arrow(70, y, 940, y, sw=1.8))
    p.append(text(918, 278, "час", size=13, color=MUTED))

    p.append(fitbox(182, 196, 578, 38, "команда компілює util.c",
                    size=14, fill=FILL))

    marks = ((182, "старт команди"),
             (432, "ви зберегли util.c"),
             (760, "util.o дописано"))
    for x, label in marks:
        p.append(line(x, 172, x, y + 14, color=MUTED, sw=1.2, dash="5,5"))
        f, _, _ = textbox(x, 150, label, size=13, fill=BG, stroke=MUTED, pad=8)
        p.append(f)

    p.append(text(330, 300, "що бачить порівняння виходу з входом", size=13,
                  color=MUTED))
    f1, _, _ = textbox(330, 350, "mtime(util.o) > mtime(util.c)\n→ «актуальний» назавжди",
                       size=13.5, fill=DIRTY, stroke=POS, sw=2)
    p.append(f1)

    p.append(text(742, 300, "що бачить записаний момент старту", size=13,
                  color=MUTED))
    f2, _, _ = textbox(742, 350, "util.c новіший за старт команди\n→ задача брудна",
                       size=13.5, fill=CLEAN, stroke=FIELD, sw=2)
    p.append(f2)

    render(os.path.join(IMG, "build-race.svg"), W, H, *p,
           title="Правка у вікні між стартом команди й записом виходу")


# ── 4. Та сама перевірка вмісту нагорі конуса й під ним (вставка math) ──────
def fig_cutoff_placement():
    W, H = 1080, 610
    p = []

    p.append(rect(40, 62, 480, 500, fill=PANEL, stroke=MUTED, sw=1.5))
    p.append(rect(560, 62, 480, 500, fill=PANEL, stroke=MUTED, sw=1.5))
    p.append(text(280, 92, "Тест нагорі конуса", size=15, bold=True))
    p.append(text(800, 92, "Тест під широким шаром", size=15, bold=True))

    # ліва панель: відсічка на згенерованому заголовку
    fa, a1 = node(280, 148, "згенерований заголовок\n20 КБ", fill=CLEAN, size=14)
    fb, a2 = node(280, 258, "1200 × компіляція\n480 с", size=14)
    fc, a3 = node(280, 350, "лінк · 12 с", size=14)
    p += [fa, fb, fc, down(a1, a2), down(a2, a3)]

    p.append(line(296, 203, 336, 203, color=FIELD, sw=1.6, dash="5,5"))
    ft, _, _ = textbox(412, 203, "геш виходу · 8 мкс", size=12.5,
                       fill=BG, stroke=FIELD, sw=1.8, pad=8)
    p.append(ft)

    p.append(fitbox(70, 402, 420, 138,
                    "ціна тесту: 8 мкс\n"
                    "спрацює з імовірністю 1 − q\n"
                    "знімає роботи на 492 с\n"
                    "у плюсі, поки q < 1 − 1.6·10⁻⁸",
                    size=14, fill=BG, stroke=MUTED))

    # права панель: відсічка на 1200 обʼєктних файлах
    fd, b1 = node(800, 148, "заголовок правлено рукою", fill=DIRTY, size=14)
    fe, b2 = node(800, 258, "1200 × компіляція\n480 с", size=14)
    ff, b3 = node(800, 350, "лінк · 12 с", size=14)
    p += [fd, fe, ff, down(b1, b2), down(b2, b3)]

    p.append(line(816, 308, 856, 308, color=POS, sw=1.6, dash="5,5"))
    ft2, _, _ = textbox(930, 308, "1200 гешів · 0.19 с", size=12.5,
                        fill=BG, stroke=POS, sw=1.8, pad=8)
    p.append(ft2)

    p.append(fitbox(590, 402, 420, 138,
                    "ціна тесту: 0.19 с\n"
                    "спрацює з імовірністю (1 − q)¹²⁰⁰\n"
                    "знімає роботи на 12 с\n"
                    "у плюсі, поки q < 3.4·10⁻³",
                    size=14, fill=BG, stroke=MUTED))

    render(os.path.join(IMG, "cutoff-placement.svg"), W, H, *p,
           title="Однакова перевірка вмісту, різна ціна й різні шанси")


# ── 5. Поріг q як функція кількості входів споживача ────────────────────────
def fig_breakeven():
    import math
    W, H = 1010, 545
    p = []

    X0, X1 = 155, 930
    Y0, Y1 = 105, 430
    LGX = 3.3          # вісь n: 10⁰ … 10³·³
    LGY = 3.0          # вісь q: 10⁰ … 10⁻³

    def px(n):
        return X0 + math.log10(n) / LGX * (X1 - X0)

    def py(q):
        return Y0 + (-math.log10(q)) / LGY * (Y1 - Y0)

    # сітка
    for k in (1, 2, 3):
        x = X0 + k / LGX * (X1 - X0)
        p.append(line(x, Y0, x, Y1, color="#dfe3e8", sw=1.2, dash="4,6"))
        p.append(text(x, Y1 + 26, "1" + "0" * k, size=13, color=MUTED))
    for k in (1, 2, 3):
        y = Y0 + k / LGY * (Y1 - Y0)
        p.append(line(X0, y, X1, y, color="#dfe3e8", sw=1.2, dash="4,6"))
        p.append(text(X0 - 14, y + 5, ("0.1", "0.01", "0.001")[k - 1],
                      size=13, color=MUTED, anchor="end"))
    p.append(text(X0 - 14, Y0 + 5, "1", size=13, color=MUTED, anchor="end"))
    p.append(text(X0, Y1 + 26, "1", size=13, color=MUTED))

    p.append(line(X0, Y0, X0, Y1, sw=1.6))
    p.append(line(X0, Y1, X1, Y1, sw=1.6))
    p.append(text(X1 - 30, Y1 + 52, "n — скільки входів у споживача",
                  size=13.5, color=MUTED, anchor="end"))
    p.append(text(X0 - 6, Y0 - 24, "поріг q*", size=13.5, color=MUTED,
                  anchor="start"))

    # крива q*(n) = 1 − (n·h/C)^(1/n),  h = 0.16 мс, C = 12 с
    h, C = 1.6e-4, 12.0
    ns = [1, 1.3, 1.7, 2.2, 2.8, 3.6, 4.6, 6, 8, 10, 13, 17, 22, 28, 36, 46,
          60, 80, 100, 130, 170, 220, 280, 360, 460, 600, 800, 1000, 1300,
          1700, 2000]
    pts = [(px(n), py(1 - (n * h / C) ** (1.0 / n))) for n in ns]
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        p.append(line(x1, y1, x2, y2, color=NEG, sw=2.4))

    p.append(text(730, 168, "тут відсічка коштує більше, ніж дає",
                  size=14, color=POS, bold=True))
    p.append(text(285, 398, "тут відсічка окуповується",
                  size=14, color=FIELD, bold=True))

    xd, yd = px(1200), py(1 - (1200 * h / C) ** (1.0 / 1200))
    p.append(circle(xd, yd, 6, fill=NEG, stroke=NEG))
    p.append(line(xd - 8, yd + 12, 812, 458, color=MUTED, sw=1.2))
    fl, _, _ = textbox(742, 476, "лінк: n = 1200 → q* = 3.4·10⁻³",
                       size=13, fill=BG, stroke=MUTED, pad=8)
    p.append(fl)

    render(os.path.join(IMG, "cutoff-breakeven.svg"), W, H, *p,
           title="Поріг окупності відсічки: ціна росте як n, шанс падає як (1−q)ⁿ")


# ── Життя файлу залежностей: ninja проти make ───────────────────────────────
def fig_depfile_flow():
    W, H = 1040, 596
    p = []

    cols = (
        (265, "ninja · deps = gcc", CLEAN, FIELD,
         ("правило в build.ninja:\ndepfile = $out.d · deps = gcc",
          "компілятор пише build/util.o.d\nтекстовий, живе кілька секунд",
          "ninja розбирає його одразу\nпісля команди — і видаляє",
          ".ninja_deps · двійковий журнал\nнаступний прогін читає лише його"),
         "на старті збірки — один файл,\nодин послідовний прохід"),
        (775, "make · -include", FILL, MUTED,
         ("рецепт у Makefile:\ngcc -MMD -MP -MF $(@:.o=.d)",
          "компілятор пише build/util.d\nтекстовий, лишається на диску",
          "-include $(OBJ:.o=.d)\nmake читає всі .d як makefile",
          "прочитавши, make ще й пробує\nоновити кожен із них"),
         "на старті збірки — тисячі\nдрібних файлів щоразу"),
    )

    for cx, head, fill, stroke, steps, foot in cols:
        p.append(rect(cx - 215, 62, 430, 478, fill=PANEL, stroke=MUTED, sw=1.5))
        p.append(text(cx, 92, head, size=15, bold=True, color=stroke))

        tops = (112, 200, 288, 376)
        for top, s in zip(tops, steps):
            p.append(fitbox(cx - 194, top, 388, 62, s, size=13,
                            fill=fill, stroke=stroke))
        for top in tops[:-1]:
            p.append(arrow(cx, top + 64, cx, top + 84, color=stroke, sw=1.8))

        ff, _, _ = textbox(cx, 500, foot, size=13, fill=BG, stroke=MUTED, pad=9)
        p.append(ff)

    render(os.path.join(IMG, "depfile-flow.svg"), W, H, *p,
           title="Куди потрапляє перелік залежностей після компіляції")


if __name__ == "__main__":
    fig_two_families()
    fig_early_cutoff()
    fig_build_race()
    fig_cutoff_placement()
    fig_breakeven()
    fig_depfile_flow()
    print("готово:", IMG)

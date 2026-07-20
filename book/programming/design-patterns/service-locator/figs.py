# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Fig 1: два обличчя локатора — статичний глобал проти впровадженого реєстру ─
def fig_two_faces():
    W, H = 1200, 600
    frags = []
    frags.append(text(W / 2, 34, "Дві версії локатора під однією назвою", size=18, bold=True))
    frags.append(text(W / 2, 58, "той самий реєстр «ключ → служба» — а вигоди й шкода зовсім різні",
                      size=12.5, color=MUTED))
    frags.append(line(W / 2, 76, W / 2, 500, color="#d0d5db", sw=1.1, dash="4,6"))

    lx, rx = W * 0.265, W * 0.735   # 318, 882

    # ── Ліворуч: статичний глобальний локатор (червоне) ──────────────────────
    frags.append(text(lx, 100, "СТАТИЧНИЙ ГЛОБАЛЬНИЙ ЛОКАТОР", size=13.5, bold=True, color=POS))
    loc, lw, lh = textbox(lx, 156, "глобальний  Locator", size=12.5, bold=True,
                          fill="#fdecea", stroke=POS, sw=1.7, min_w=250)
    frags.append(loc)
    sv, svw, svh = textbox(lx, 300, ["OrderService", "ctor() — порожній"], size=12.5, bold=True,
                           fill=FILL, stroke=LINE, sw=1.6, min_w=250)
    frags.append(sv)
    # смик угору (get) і повернення служби вниз — чорний хід до глобала
    frags.append(arrow(lx - 26, 300 - svh / 2 - 4, lx - 26, 156 + lh / 2 + 4, color=POS, sw=1.8))
    frags.append(arrow(lx + 26, 156 + lh / 2 + 4, lx + 26, 300 - svh / 2 - 4, color=MUTED, sw=1.4))
    frags.append(text(lx - 36, 232, "смикає get()", size=11, color=POS, anchor="end"))
    frags.append(text(lx + 36, 232, "служба", size=11, color=MUTED, anchor="start"))
    cy = 300 + svh / 2 + 34
    frags.append(text(lx, cy, "✗ невидима в сигнатурі", size=12.5, bold=True, color=POS))
    frags.append(text(lx, cy + 24, "✗ тест готує спільний глобал", size=12, color=MUTED))
    frags.append(text(lx, cy + 48, "✗ збій виринає в рантаймі", size=12, color=MUTED))

    # ── Праворуч: упроваджений реєстр (зелене) ───────────────────────────────
    frags.append(text(rx, 100, "УПРОВАДЖЕНИЙ РЕЄСТР", size=13.5, bold=True, color=FIELD))
    comp, cw, ch = textbox(rx, 156, "хто складає (корінь)", size=12.5, bold=True,
                           fill="#eaf0fd", stroke=NEG, sw=1.6, min_w=250)
    frags.append(comp)
    sv2, sv2w, sv2h = textbox(rx, 300, ["OrderService", "ctor(ServiceRegistry)"], size=12.5, bold=True,
                              fill="#eaf7ef", stroke=FIELD, sw=1.9, min_w=250)
    frags.append(sv2)
    frags.append(arrow(rx, 156 + ch / 2 + 4, rx, 300 - sv2h / 2 - 4, color=FIELD, sw=1.9))
    frags.append(text(rx + 96, 232, "подає ззовні", size=11.5, color=FIELD, anchor="start"))
    cy2 = 300 + sv2h / 2 + 34
    frags.append(text(rx, cy2, "✓ реєстр видно в сигнатурі", size=12.5, bold=True, color=FIELD))
    frags.append(text(rx, cy2 + 24, "✓ тест подає власний екземпляр", size=12, color=MUTED))
    frags.append(text(rx, cy2 + 48, "✓ спільного сховища нема", size=12, color=MUTED))

    frags.append(line(40, 520, W - 40, 520, color="#d0d5db", sw=1.1))
    frags.append(text(W / 2, 550, "Антипатерном локатор роблять не «ключ → служба», а глобальна статична досяжність",
                      size=13, bold=True))
    frags.append(text(W / 2, 574, "прибери глобальність — і найгостріші жала витягнуто",
                      size=11.5, color=MUTED))

    render(os.path.join(IMG, 'two-faces.svg'), W, H, *frags)


# ── Fig 2: контейнер у двох ролях — чесний у корені, локатор у нутрі ──────────
def fig_container_as_locator():
    W, H = 1200, 620
    frags = []
    frags.append(text(W / 2, 34, "Контейнер у двох ролях", size=18, bold=True))
    frags.append(text(W / 2, 58, "той самий інструмент чесний на порозі й шкідливий у нутрі",
                      size=12.5, color=MUTED))

    # ── Верхня зона: корінь (зелене) ─────────────────────────────────────────
    frags.append(rect(50, 78, 1100, 200, fill="#f2faf5", stroke=FIELD, sw=1.8))
    frags.append(text(72, 104, "КОРІНЬ — поріг програми", size=14, bold=True, color=FIELD, anchor="start"))
    cont, cw, chh = textbox(250, 192, ["контейнер", "(DI-контейнер)"], size=12.5, bold=True,
                            fill="#eaf0fd", stroke=NEG, sw=1.7, min_w=210)
    frags.append(cont)
    osb, ow, oh = textbox(885, 192, ["OrderService(gateway)", "дістав саме шлюз"], size=12.5, bold=True,
                          fill="#eaf7ef", stroke=FIELD, sw=1.9, min_w=250)
    frags.append(osb)
    mid_top = (250 + cw / 2 + 885 - ow / 2) / 2
    frags.append(arrow(250 + cw / 2 + 8, 192, 885 - ow / 2 - 8, 192, color=FIELD, sw=2.0))
    frags.append(text(mid_top, 172, "збирає граф і подає готове", size=12, color=FIELD))
    frags.append(text(mid_top, 216, "стрілка-впровадження", size=11, color=MUTED))
    frags.append(text(885, 192 + oh / 2 + 22, "✓ правильно", size=12.5, bold=True, color=FIELD))

    # ── Підписана межа між зонами ────────────────────────────────────────────
    frags.append(line(50, 306, 358, 306, color=MUTED, sw=1.3, dash="5,5"))
    frags.append(line(842, 306, 1150, 306, color=MUTED, sw=1.3, dash="5,5"))
    blab, blw, blh = textbox(600, 306, "контейнер торкається коду рівно в одній точці — у корені",
                             size=12, bold=True, fill=BG, stroke=MUTED, sw=1.3)
    frags.append(blab)

    # ── Нижня зона: нутро (червоне) ──────────────────────────────────────────
    frags.append(rect(50, 336, 1100, 214, fill="#fdf3f2", stroke=POS, sw=1.8))
    frags.append(text(72, 362, "НУТРО — робочий код", size=14, bold=True, color=POS, anchor="start"))
    osg, ogw, ogh = textbox(355, 452, ["OrderService", "ctor(container: Container)", "resolve<PaymentGateway>()"],
                            size=12, bold=True, fill=BG, stroke=POS, sw=1.7, min_w=300)
    frags.append(osg)
    chip, ccw, cch = textbox(830, 452, "container", size=12.5, bold=True,
                             fill="#f3f4f6", stroke=POS, sw=1.6, min_w=170)
    frags.append(chip)
    mid_bot = (355 + ogw / 2 + 830 - ccw / 2) / 2
    frags.append(arrow(355 + ogw / 2 + 8, 445, 830 - ccw / 2 - 8, 445, color=POS, sw=1.8))
    frags.append(text(mid_bot, 425, "смик resolve() посеред методу", size=11.5, color=POS))
    frags.append(text(mid_bot, 476, "прийнято ВЕСЬ контейнер", size=11, color=MUTED))
    frags.append(text(600, 528, "сигнатура каже «потрібен контейнер» = «потрібно все» → став локатором",
                      size=12, bold=True, color=POS))

    frags.append(text(W / 2, 590, "контейнер видно ЛИШЕ в корені; resolve() усередині коду — майже завжди помилка на рев'ю",
                      size=12.5, bold=True, color=INK))

    render(os.path.join(IMG, 'container-as-locator.svg'), W, H, *frags)


# ── Fig 3: тришаровий кордон — смикай на краю, впроваджуй усередину ───────────
def fig_keep_at_edge():
    W, H = 1300, 580
    frags = []
    frags.append(text(W / 2, 34, "Смикай на краю — впроваджуй усередину", size=18, bold=True))
    frags.append(text(W / 2, 58, "коли створенням об'єкта порядкує чужий код, локатор лишають тонкою смугою на межі",
                      size=12, color=MUTED))

    # три смуги
    frags.append(rect(40, 80, 350, 420, fill="#f7f8fa", stroke=MUTED, sw=1.6))
    frags.append(rect(410, 80, 200, 420, fill="#fff8e1", stroke="#b8860b", sw=1.8))
    frags.append(rect(630, 80, 630, 420, fill="#f2faf5", stroke=FIELD, sw=1.8))
    frags.append(text(215, 108, "ЗОВНІШНІЙ КАРКАС", size=13.5, bold=True, color=INK))
    frags.append(text(510, 108, "КРАЙ", size=13.5, bold=True, color="#b8860b"))
    frags.append(text(945, 108, "ЯДРО — чисте", size=13.5, bold=True, color=FIELD))

    # ── Смуга А: каркас створює обробник і дає йому контекст-локатор ──────────
    fw, fww, fwh = textbox(215, 178, ["каркас", "(веб · платформа · JSON)"], size=12, bold=True,
                           fill="#eaf0fd", stroke=NEG, sw=1.6, min_w=250)
    frags.append(fw)
    ctx, cxw, cxh = textbox(215, 332, ["контекст-локатор", "постачальник служб"], size=12, bold=True,
                            fill="#fdecea", stroke=POS, sw=1.7, min_w=250)
    frags.append(ctx)
    frags.append(text(215, 424, "конструктор недоступний —", size=11.5, color=MUTED))
    frags.append(text(215, 444, "каркас кличе порожній", size=11.5, color=MUTED))

    # ── Смуга Б: обробник дістає з контексту раз ─────────────────────────────
    hd, hdw, hdh = textbox(510, 178, ["обробник", "(на межі)"], size=12, bold=True,
                           fill=BG, stroke="#b8860b", sw=1.8, min_w=160)
    frags.append(hd)
    frags.append(text(510, 262, "дістає з контексту раз:", size=11, color=MUTED))
    pull, pw, ph = textbox(510, 332, ["gateway", "clock", "repo"], size=12, bold=True,
                           fill="#fff3cd", stroke="#b8860b", sw=1.5, min_w=130)
    frags.append(pull)

    # ── Смуга В: ядро приймає залежності конструктором ───────────────────────
    c1, c1w, c1h = textbox(945, 178, "OrderService(gateway, clock)", size=12, bold=True,
                           fill="#eaf7ef", stroke=FIELD, sw=1.7, min_w=280)
    frags.append(c1)
    c2, c2w, c2h = textbox(790, 306, "PriceCalc(rates)", size=12, bold=True,
                           fill="#eaf7ef", stroke=FIELD, sw=1.7, min_w=190)
    frags.append(c2)
    c3, c3w, c3h = textbox(1105, 306, "OrderRepo(db)", size=12, bold=True,
                           fill="#eaf7ef", stroke=FIELD, sw=1.7, min_w=190)
    frags.append(c3)
    frags.append(text(945, 420, "жоден клас ядра локатора не бачить", size=12.5, bold=True, color=FIELD))

    # ── Стрілки, що перетинають межі смуг ────────────────────────────────────
    frags.append(arrow(215 + fww / 2 + 6, 178, 510 - hdw / 2 - 6, 178, color=MUTED, sw=1.6))
    frags.append(text((215 + fww / 2 + 510 - hdw / 2) / 2, 162, "створює", size=11, color=MUTED))
    frags.append(arrow(215 + cxw / 2 + 6, 332, 510 - pw / 2 - 6, 332, color=POS, sw=1.6))
    frags.append(text((215 + cxw / 2 + 510 - pw / 2) / 2, 316, "дає локатор", size=11, color=POS))
    frags.append(arrow(510 + hdw / 2 + 6, 178, 945 - c1w / 2 - 6, 178, color=FIELD, sw=1.9))
    frags.append(text((510 + hdw / 2 + 945 - c1w / 2) / 2, 162, "подає конструктором", size=11, color=FIELD))

    frags.append(line(40, 524, W - 40, 524, color="#d0d5db", sw=1.1))
    frags.append(text(W / 2, 552, "локатор — вузька смужка на кордоні; у ядро залежності приходять уже впровадженням",
                      size=12.5, bold=True, color=INK))

    render(os.path.join(IMG, 'keep-at-edge.svg'), W, H, *frags)


# ── Fig 4 (hist): як народжувалась назва — прийом → назва → вирок ─────────────
def fig_naming_timeline():
    W, H = 1440, 600
    frags = []
    frags.append(text(W / 2, 36, "Як народжувалась назва «локатор служб»", size=18, bold=True))
    frags.append(text(W / 2, 60, "прийом старший за назву на роки; назва старша за вирок «антипатерн» на дев'ять років",
                      size=12.5, color=MUTED))

    spine_y = 312
    frags.append(line(105, spine_y, 1335, spine_y, color="#c3c8d0", sw=2.2))

    xs = [190, 460, 730, 1000, 1255]
    # (x, вгору?, колір-обвід, заливка, роки, [рядки], підпис-колір)
    nodes = [
        (xs[0], False, MUTED, FILL,      "кінець 1990-х",
         ["JNDI-пошук", "ctx.lookup(\"…\")", "прийом БЕЗ назви"], INK),
        (xs[1], True,  NEG,   "#eaf0fd",  "червень 2001",
         ["«Core J2EE Patterns»", "Alur · Crupi · Malks", "→ назва Service Locator"], NEG),
        (xs[2], False, NEG,   "#eaf0fd",  "2004",
         ["Мартін Фаулер", "стаття про IoC / DI", "→ рівноправна пара до DI"], NEG),
        (xs[3], True,  POS,   "#fdecea",  "3 лютого 2010",
         ["Марк Симан · ploeh.dk", "«…is an Anti-Pattern»", "→ назва = вирок"], POS),
        (xs[4], False, "#b8860b", "#fff8e1", "2010 → досі",
         ["суперечка триває", "Богард (2022): «як коли»", "→ уся річ у контексті"], "#b8860b"),
    ]

    for x, up, stroke, fill, yr, lines, ycol in nodes:
        cy = 176 if up else 452
        box, bw, bh = textbox(x, cy, lines, size=12.5, bold=True,
                              fill=fill, stroke=stroke, sw=1.8, min_w=272)
        if up:
            frags.append(line(x, spine_y - 6, x, cy + bh / 2 + 4, color=stroke, sw=1.6))
            frags.append(text(x, spine_y + 34, yr, size=12.5, bold=True, color=ycol))
        else:
            frags.append(line(x, spine_y + 6, x, cy - bh / 2 - 4, color=stroke, sw=1.6))
            frags.append(text(x, spine_y - 22, yr, size=12.5, bold=True, color=ycol))
        frags.append(box)
        frags.append(circle(x, spine_y, 8, fill=fill, stroke=stroke, sw=2.4))

    # дві доби назви — нейтральна vs спірна — тонкими дужками під спайном
    frags.append(text((xs[1] + xs[2]) / 2, spine_y + 66,
                      "дев'ять років назва була нейтральною — одним із двох законних виборів",
                      size=11.5, italic=True, color=MUTED))

    frags.append(line(40, 560, W - 40, 560, color="#d0d5db", sw=1.1))
    frags.append(text(W / 2, 586,
                      "той самий реєстр-пошук: спершу безіменний прийом, потім названий патерн, потім тавро антипатерну — а річ не змінилась",
                      size=12.5, bold=True, color=INK))

    render(os.path.join(IMG, 'naming-timeline.svg'), W, H, *frags)


# ── Fig 5 (proj): де вмирає одрук — рядковий ключ проти токена, що несе тип ───
def fig_typed_token():
    W, H = 1220, 580
    frags = []
    frags.append(text(W / 2, 36, "Де вмирає одрук: рядковий ключ проти токена", size=18, bold=True))
    frags.append(text(W / 2, 60, "той самий пошук служби — а помилку ловлять у різні моменти",
                      size=12.5, color=MUTED))
    frags.append(line(W / 2, 82, W / 2, 486, color="#d0d5db", sw=1.1, dash="4,6"))

    lx, rx = 330, 890

    # ── Ліворуч: ключ-рядок (червоне) ────────────────────────────────────────
    frags.append(text(lx, 108, "КЛЮЧ — РЯДОК", size=14, bold=True, color=POS))
    b1, _, _ = textbox(lx, 156, 'registry.get("getway")', size=12.5,
                       fill="#fdecea", stroke=POS, sw=1.7, min_w=320)
    frags.append(b1)
    frags.append(arrow(lx, 176, lx, 216, color=POS, sw=1.7))
    frags.append(text(lx, 240, "компілятор пропускає — рядок є рядок", size=11.5, color=MUTED))
    b2, _, _ = textbox(lx, 284, "рантайм: undefined → виняток", size=12,
                       fill=BG, stroke=POS, sw=1.6, min_w=320)
    frags.append(b2)
    frags.append(arrow(lx, 304, lx, 340, color=POS, sw=1.5))
    frags.append(text(lx, 362, "тип повернення: unknown", size=12, color=INK))
    frags.append(text(lx, 384, "→ приведення as PaymentGateway щоразу", size=11, color=MUTED))
    frags.append(text(lx, 428, "✗ одрук доживає до рантайму", size=12.5, bold=True, color=POS))
    frags.append(text(lx, 454, "✗ приведення в кожній точці", size=12, color=MUTED))

    # ── Праворуч: типізований токен (зелене) ─────────────────────────────────
    frags.append(text(rx, 108, "КЛЮЧ — ТОКЕН, ЩО НЕСЕ ТИП", size=14, bold=True, color=FIELD))
    r1, _, _ = textbox(rx, 156, "registry.resolve(GATEWY)", size=12.5,
                       fill=BG, stroke=FIELD, sw=1.7, min_w=320)
    frags.append(r1)
    frags.append(arrow(rx, 176, rx, 216, color=FIELD, sw=1.7))
    frags.append(text(rx, 240, "компілятор: Cannot find name 'GATEWY'", size=11.5, bold=True, color=FIELD))
    r2, _, _ = textbox(rx, 284, "виправив → resolve(GATEWAY)", size=12,
                       fill="#eaf7ef", stroke=FIELD, sw=1.6, min_w=320)
    frags.append(r2)
    frags.append(arrow(rx, 304, rx, 340, color=FIELD, sw=1.5))
    frags.append(text(rx, 362, "тип повернення: PaymentGateway", size=12, color=INK))
    frags.append(text(rx, 384, "→ без приведення, одразу типизовано", size=11, color=MUTED))
    frags.append(text(rx, 428, "✓ одрук не компілюється", size=12.5, bold=True, color=FIELD))
    frags.append(text(rx, 454, "✓ жодного приведення", size=12, color=MUTED))

    frags.append(line(40, 496, W - 40, 496, color="#d0d5db", sw=1.1))
    frags.append(text(W / 2, 524, "Секрет один: вкласти тип служби в сам ключ", size=13, bold=True))
    frags.append(text(W / 2, 548, "тоді одрук ловить компілятор, а не користувач у проді",
                      size=11.5, color=MUTED))

    render(os.path.join(IMG, 'typed-token.svg'), W, H, *frags)


# ── Fig 6 (proj): два рівні кешу — корінь (спільне) і області запитів ─────────
def fig_scope_tree():
    W, H = 1260, 650
    frags = []
    frags.append(text(W / 2, 36, "Два рівні кешу: корінь і області", size=18, bold=True))
    frags.append(text(W / 2, 60, "спільне — на корені, особисте — на області запиту",
                      size=12.5, color=MUTED))

    # ── Корінь ───────────────────────────────────────────────────────────────
    root, _, rh = textbox(630, 150, ["КОРІНЬ · заморожений на старті",
                                     "сінглтони: Clock, Config (спільні для всіх)",
                                     "рецепти: як зробити кожну службу"],
                          size=12.5, pad=12, fill="#eef2f7", stroke=LINE, sw=1.8, min_w=470)
    frags.append(root)
    frags.append(text(630, 214, "на кожен запит — своя область (createScope)", size=11.5, color=MUTED))

    # ── Дві області ──────────────────────────────────────────────────────────
    ax, bx, cy = 340, 920, 384
    ca, _, ch = textbox(ax, cy, ["ОБЛАСТЬ · запит A", "свій кеш scoped:",
                                 "UnitOfWork·A · CurrentUser·A"],
                        size=12.5, pad=12, fill="#eaf7ef", stroke=FIELD, sw=1.8, min_w=350)
    frags.append(ca)
    cb, _, _ = textbox(bx, cy, ["ОБЛАСТЬ · запит B", "свій кеш scoped:",
                                "UnitOfWork·B · CurrentUser·B"],
                       size=12.5, pad=12, fill="#eaf7ef", stroke=FIELD, sw=1.8, min_w=350)
    frags.append(cb)

    frags.append(arrow(540, 150 + rh / 2 + 4, 400, cy - ch / 2 - 6, color=MUTED, sw=1.7))
    frags.append(arrow(720, 150 + rh / 2 + 4, 860, cy - ch / 2 - 6, color=MUTED, sw=1.7))

    # ── Між областями: не ділять scoped ──────────────────────────────────────
    frags.append(text(630, 366, "A і B", size=11.5, bold=True, color=POS))
    frags.append(text(630, 386, "не ділять", size=11.5, bold=True, color=POS))
    frags.append(text(630, 406, "scoped-стан", size=11.5, bold=True, color=POS))

    # ── Делегація сінглтонів + dispose ───────────────────────────────────────
    frags.append(text(ax, cy + ch / 2 + 24, "Clock, Config — з кореня (ті самі)", size=11, color=MUTED))
    frags.append(text(bx, cy + ch / 2 + 24, "Clock, Config — з кореня (ті самі)", size=11, color=MUTED))
    frags.append(text(ax, cy + ch / 2 + 58, "край запиту A → dispose:", size=11.5, color=INK))
    frags.append(text(ax, cy + ch / 2 + 78, "UnitOfWork·A звільнено, з'єднання закрито", size=10.5, color=MUTED))
    frags.append(text(bx, cy + ch / 2 + 58, "край запиту B → dispose:", size=11.5, color=INK))
    frags.append(text(bx, cy + ch / 2 + 78, "UnitOfWork·B звільнено, з'єднання закрито", size=10.5, color=MUTED))

    frags.append(line(40, 566, W - 40, 566, color="#d0d5db", sw=1.1))
    frags.append(text(630, 594, "Ізоляція виникає не з дисципліни, а з того, ДЕ стоїть кеш готового екземпляра",
                      size=13, bold=True))
    frags.append(text(630, 618, "сінглтон — на корені (один на всіх); scoped — на області (свій на запит, гине з нею)",
                      size=11.5, color=MUTED))

    render(os.path.join(IMG, 'scope-tree.svg'), W, H, *frags)


# ── Fig 7 (proj): правило життя й полонена залежність (captive dependency) ────
def fig_lifetime_rule():
    W, H = 1200, 600
    frags = []
    frags.append(text(W / 2, 36, "Правило життя й полонена залежність", size=18, bold=True))
    frags.append(text(W / 2, 60, "служба залежить лише від рівного або довшого життя",
                      size=12.5, color=MUTED))

    # ── Три строки життя різної довжини ──────────────────────────────────────
    x0 = 250
    frags.append(rect(x0, 106, 830, 32, fill="#eaf7ef", stroke=FIELD, sw=1.6))
    frags.append(text(60, 127, "сінглтон", size=12.5, bold=True, anchor="start"))
    frags.append(text(665, 127, "весь застосунок", size=11.5, color=FIELD))
    frags.append(rect(x0, 150, 420, 32, fill="#fff3cd", stroke="#b8860b", sw=1.6))
    frags.append(text(60, 171, "scoped", size=12.5, bold=True, anchor="start"))
    frags.append(text(460, 171, "один запит", size=11.5, color="#b8860b"))
    frags.append(rect(x0, 194, 150, 32, fill="#fdecea", stroke=POS, sw=1.6))
    frags.append(text(60, 215, "transient", size=12.5, bold=True, anchor="start"))
    frags.append(text(325, 215, "один виклик", size=11, color=POS))

    frags.append(text(W / 2, 258, "залежати можна лише праворуч — на рівне або довше життя",
                      size=12.5, bold=True, color=FIELD))
    frags.append(text(W / 2, 282, "scoped → scoped/сінглтон ✓    ·    transient → будь-що ✓    ·    сінглтон → лише сінглтон ✓",
                      size=11.5, color=MUTED))

    frags.append(line(40, 306, W - 40, 306, color="#d0d5db", sw=1.1))

    # ── Заборонений випадок: сінглтон полонить scoped ─────────────────────────
    frags.append(text(W / 2, 336, "ЗАБОРОНЕНО: сінглтон тримає scoped (коротше життя)",
                      size=13, bold=True, color=POS))
    frags.append(text(343, 366, "полонений — тримається аж до кінця віку сінглтона", size=11, color=POS))
    frags.append(arrow(343, 384, 1070, 384, color=POS, sw=1.6))
    frags.append(rect(250, 396, 830, 44, fill="#eef2f7", stroke=LINE, sw=1.6))
    frags.append(text(60, 422, "сінглтон", size=12.5, bold=True, anchor="start"))
    frags.append(rect(268, 404, 150, 28, fill="#fdecea", stroke=POS, sw=1.7))
    frags.append(text(343, 422, "UnitOfWork", size=10.5, bold=True, color=POS))
    frags.append(line(470, 392, 470, 448, color=POS, sw=1.3, dash="5,5"))
    frags.append(text(470, 466, "кінець запиту", size=11, bold=True, color=POS))
    frags.append(text(470, 484, "тут scoped мав померти", size=10, color=POS))
    frags.append(text(1072, 466, "транзакція протухла → витік", size=10.5, color=POS, anchor="end"))

    frags.append(line(40, 512, W - 40, 512, color="#d0d5db", sw=1.1))
    frags.append(text(W / 2, 540, "«Полонена залежність» (Mark Seemann): коротше життя не сміє переживати свою область",
                      size=12.5, bold=True))
    frags.append(text(W / 2, 564, "довше життя тримає коротше прив'язаним — і воно застаряє разом з утриманим станом",
                      size=11.5, color=MUTED))

    render(os.path.join(IMG, 'lifetime-rule.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_two_faces()
    fig_container_as_locator()
    fig_keep_at_edge()
    fig_naming_timeline()
    fig_typed_token()
    fig_scope_tree()
    fig_lifetime_rule()
    print("figs done")

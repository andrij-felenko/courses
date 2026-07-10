# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Ролі адаптера: два боки й перекладки між ними ────────────────────────────
def fig_adapter_roles():
    W, H = 1160, 560
    frags = []

    frags.append(text(W / 2, 40, "Адаптер має два боки — і перекладає між ними",
                      size=17, bold=True, color=INK))

    # ── ЛІВОРУЧ: клієнтський код (Ціль) ──────────────────────────────────────
    cl_x, cl_y = 150, 250
    cl, clw, clh = textbox(cl_x, cl_y,
                           ["Клієнтський код", "вміє лише:",
                            "charge(гривні, валюта)"],
                           size=13, bold=True, fill="#e8f6ee", stroke=FIELD,
                           sw=1.8, min_w=250)
    frags.append(cl)
    frags.append(text(cl_x, cl_y - clh / 2 - 14, "ЦІЛЬ (що очікує наш код)",
                      size=11.5, color=FIELD, bold=True))

    # ── ПРАВОРУЧ: чужий SDK (Адаптований) ────────────────────────────────────
    st_x, st_y = W - 150, 250
    st, stw, sth = textbox(st_x, st_y,
                           ["StripeClient (чужий)", "вміє лише:",
                            "createCharge(центи)"],
                           size=13, bold=True, fill="#eaf0fd", stroke=NEG,
                           sw=1.8, min_w=250)
    frags.append(st)
    frags.append(text(st_x, st_y - sth / 2 - 14, "АДАПТОВАНИЙ (чужий об'єкт)",
                      size=11.5, color=NEG, bold=True))

    # ── ПОСЕРЕДИНІ: адаптер із двома роз'ємами ───────────────────────────────
    ad_x = W / 2
    ad_w, ad_h = 320, 250
    ad_y0 = 150
    frags.append(rect(ad_x - ad_w / 2, ad_y0, ad_w, ad_h,
                      fill="#fff8f0", stroke=POS, sw=2, rx=10))
    frags.append(text(ad_x, ad_y0 + 26, "StripeAdapter", size=15, bold=True, color=POS))

    # верхній роз'єм — форми Цілі (ліворуч догори до клієнта)
    frags.append(text(ad_x, ad_y0 + 52, "роз'єм зверху = форма charge",
                      size=11, color=FIELD))
    # нижній роз'єм — форми Адаптованого
    frags.append(text(ad_x, ad_y0 + ad_h - 14, "роз'єм знизу = форма createCharge",
                      size=11, color=NEG))

    # три перекладки всередині
    tr = ["гривні × 100 → центи",
          "валюта → малі літери",
          "з відповіді взяти лише id"]
    for i, t in enumerate(tr):
        ty = ad_y0 + 92 + i * 34
        frags.append(fitbox(ad_x - ad_w / 2 + 22, ty - 15, ad_w - 44, 28,
                            t, size=12, pad=6, fill=FILL, stroke=LINE, sw=1.2))

    # стрілки: клієнт → адаптер (верхній бік), адаптер → SDK (нижній бік)
    frags.append(arrow(cl_x + clw / 2, cl_y - 30, ad_x - ad_w / 2 - 4, ad_y0 + 56,
                       color=FIELD, sw=1.8))
    frags.append(arrow(ad_x + ad_w / 2 + 4, ad_y0 + ad_h - 40,
                       st_x - stw / 2, st_y + 30, color=NEG, sw=1.8))

    # підпис під стрілками
    frags.append(text(W / 2, H - 26,
                      "сам адаптер нічого не обчислює по суті — лише пристосовує форму виклику",
                      size=12.5, color=MUTED))

    render(os.path.join(IMG, 'adapter-roles.svg'), W, H, *frags)


# ── Об'єктний адаптер (композиція) проти класового (спадкування) ─────────────
def fig_object_vs_class():
    W, H = 1120, 560
    frags = []

    # роздільник посередині
    frags.append(line(W / 2, 88, W / 2, H - 60, color="#d0d5db", sw=1.2, dash="6,6"))

    # ═══════════ ЛІВОРУЧ: ОБ'ЄКТНИЙ (композиція) ═══════════
    lcx = W / 4
    frags.append(text(lcx, 52, "Об'єктний адаптер", size=16, bold=True, color=FIELD))
    frags.append(text(lcx, 74, "тримає адаптованого ПОЛЕМ", size=12, color=MUTED))

    # адаптер
    ad, adw, adh = textbox(lcx, 176,
                           ["StripeAdapter", "implements PaymentGateway"],
                           size=12.5, bold=True, fill="#e8f6ee", stroke=FIELD,
                           sw=1.8, min_w=270)
    frags.append(ad)

    # окремий об'єкт адаптованого нижче, зв'язок = стрілка-поле
    aee, aeew, aeeh = textbox(lcx, 336, ["StripeClient", "(окремий об'єкт)"],
                              size=12.5, bold=True, fill=FILL, stroke=LINE,
                              sw=1.5, min_w=230)
    frags.append(aee)
    frags.append(arrow(lcx, 176 + adh / 2, lcx, 336 - aeeh / 2 - 2,
                       color=FIELD, sw=1.8))
    # підпис збоку від стрілки, щоб лінія не перетинала напис
    frags.append(text(lcx + 96, 176 + adh / 2 + 46, "поле-посилання", size=11.5,
                      color=FIELD, bold=True, anchor="start"))

    frags.append(text(lcx, 430, "підмінний · тестований фейком", size=12, color=INK))
    frags.append(text(lcx, 452, "працює з підкласами · можна кілька",
                      size=12, color=INK))
    frags.append(text(lcx, 480, "СТАНДАРТНИЙ вибір", size=13, bold=True, color=FIELD))

    # ═══════════ ПРАВОРУЧ: КЛАСОВИЙ (спадкування) ═══════════
    rcx = 3 * W / 4
    frags.append(text(rcx, 52, "Класовий адаптер", size=16, bold=True, color=NEG))
    frags.append(text(rcx, 74, "УСПАДКОВУЄ адаптованого", size=12, color=MUTED))

    # два предки зверху
    tgt, tgtw, tgth = textbox(rcx - 120, 168, ["PaymentGateway", "(ціль)"],
                              size=12, bold=True, fill=FILL, stroke=LINE,
                              sw=1.4, min_w=190)
    frags.append(tgt)
    aee2, aee2w, aee2h = textbox(rcx + 120, 168, ["StripeClient", "(адаптований)"],
                                 size=12, bold=True, fill="#eaf0fd", stroke=NEG,
                                 sw=1.4, min_w=190)
    frags.append(aee2)

    # адаптер знизу, дві лінії спадкування догори
    ad2, ad2w, ad2h = textbox(rcx, 320, ["StripeAdapter", "(успадкував обидва)"],
                              size=12.5, bold=True, fill="#eaf0fd", stroke=NEG,
                              sw=1.8, min_w=250)
    frags.append(ad2)
    frags.append(line(rcx - 120, 168 + tgth / 2, rcx - 40, 320 - ad2h / 2,
                      color=LINE, sw=1.6))
    frags.append(line(rcx + 120, 168 + aee2h / 2, rcx + 40, 320 - ad2h / 2,
                      color=NEG, sw=1.6))
    # напис ставимо високо, де лінії ще широко розведені й не перетинають його
    frags.append(text(rcx, 214, "спадкування", size=11.5, color=NEG, bold=True))

    frags.append(text(rcx, 430, "прибитий до одного класу", size=12, color=INK))
    frags.append(text(rcx, 452, "не підмінити · нерухомий у рантаймі",
                      size=12, color=INK))
    frags.append(text(rcx, 480, "лише де мова дає множинне спадкування",
                      size=12, color=NEG))

    render(os.path.join(IMG, 'object-vs-class.svg'), W, H, *frags)


# ── Чотири учасники й коло одного виклику (детальна) ─────────────────────────
def fig_four_participants():
    W, H = 1180, 560
    frags = []
    frags.append(text(W / 2, 34,
                      "Один виклик замикається в коло: униз із перекладом входу, угору — виходу",
                      size=16, bold=True, color=INK))

    # Клієнт (ліворуч)
    clx, cly = 210, 195
    cl, clw, clh = textbox(clx, cly, ["Клієнт", "бачить лише Target"],
                           size=13, bold=True, fill="#e8f6ee", stroke=FIELD, sw=1.8, min_w=230)
    frags.append(cl)

    # «interface» Target (верх-центр)
    tgx, tgy = 660, 150
    tg, tgw, tgh = textbox(tgx, tgy, ["«interface» Target", "charge(amount, currency)"],
                           size=13, bold=True, fill=FILL, stroke=LINE, sw=1.6, min_w=300)
    frags.append(tg)

    # Adapter (під Target)
    adx, ady = 660, 365
    ad, adw, adh = textbox(adx, ady, ["StripeAdapter", "реалізує Target"],
                           size=13, bold=True, fill="#fff8f0", stroke=POS, sw=2, min_w=300)
    frags.append(ad)

    # Adaptee (праворуч від Adapter)
    aex, aey = 1020, 365
    ae, aew, aeh = textbox(aex, aey, ["StripeClient", "(чужий)"],
                           size=13, bold=True, fill="#eaf0fd", stroke=NEG, sw=1.8, min_w=200)
    frags.append(ae)

    # (1) Клієнт → Target
    frags.append(arrow(clx + clw / 2 + 4, cly - 12, tgx - tgw / 2 - 4, tgy + 8,
                       color=FIELD, sw=1.8))
    frags.append(text((clx + clw / 2 + tgx - tgw / 2) / 2, cly - 66,
                      "(1) charge(499, «UAH»)", size=12, color=FIELD, bold=True))

    # (2) реалізує: пунктир Adapter → Target
    frags.append(line(adx, ady - adh / 2, tgx, tgy + tgh / 2, color=MUTED, sw=1.6, dash="6,5"))
    frags.append(text(adx + 22, (ady - adh / 2 + tgy + tgh / 2) / 2,
                      "(2) виклик виконує Adapter", size=11.5, color=MUTED, anchor="start"))

    # (3) Adapter → Adaptee (верхня лінія, праворуч)
    y3 = aey - 24
    frags.append(arrow(adx + adw / 2 + 4, y3, aex - aew / 2 - 4, y3, color=POS, sw=1.8))
    frags.append(text((adx + adw / 2 + aex - aew / 2) / 2, y3 - 12,
                      "(3) createCharge( f_in )", size=11.5, color=POS, bold=True))

    # (4) Adaptee → Adapter (нижня лінія, ліворуч, повернення)
    y4 = aey + 28
    frags.append(arrow(aex - aew / 2 - 4, y4, adx + adw / 2 + 4, y4, color=NEG, sw=1.6))
    frags.append(text((adx + adw / 2 + aex - aew / 2) / 2, y4 + 20,
                      "(4) сирий результат", size=11.5, color=NEG))

    # (5) Adapter → Клієнт (повернення, по діагоналі вниз-ліворуч)
    frags.append(arrow(adx - adw / 2 - 4, ady + 8, clx + clw / 2 - 6, cly + clh / 2 + 8,
                       color=POS, sw=1.6))
    frags.append(text(340, 330, "(5) f_out(result)", size=11.5, color=POS,
                      bold=True, anchor="start"))

    render(os.path.join(IMG, 'four-participants.svg'), W, H, *frags)


# ── Квадрат перекладу: коли адаптер вірний (детальна) ────────────────────────
def fig_translation_square():
    W, H = 1000, 590
    frags = []
    frags.append(text(W / 2, 34, "Квадрат перекладу: вірний адаптер його замикає",
                      size=16, bold=True, color=INK))

    tlx, tly = 280, 165
    trx, try_ = 720, 165
    blx, bly = 280, 385
    brx, bry = 720, 385

    tl, tlw, tlh = textbox(tlx, tly, ["charge(499, «UAH»)", "вхід у термінах Target"],
                           size=12, bold=True, fill="#e8f6ee", stroke=FIELD, sw=1.7, min_w=260)
    tr, trw, trh = textbox(trx, try_, ["id платежу", "вихід у термінах Target"],
                           size=12, bold=True, fill="#e8f6ee", stroke=FIELD, sw=1.7, min_w=260)
    bl, blw, blh = textbox(blx, bly, ["createCharge(minor, «uah»)", "вхід у термінах Adaptee"],
                           size=12, bold=True, fill="#eaf0fd", stroke=NEG, sw=1.7, min_w=260)
    br, brw, brh = textbox(brx, bry, ["{ id }", "вихід у термінах Adaptee"],
                           size=12, bold=True, fill="#eaf0fd", stroke=NEG, sw=1.7, min_w=260)
    frags += [tl, tr, bl, br]

    # верхнє ребро (пунктир) — семантика Target
    frags.append(line(tlx + tlw / 2, tly, trx - trw / 2, try_, color=MUTED, sw=1.6, dash="7,5"))
    frags.append(text(W / 2, tly - tlh / 2 - 14, "семантика, яку обіцяє Target",
                      size=11.5, color=MUTED))

    # ліве ребро — f_in
    frags.append(arrow(tlx, tly + tlh / 2 + 2, blx, bly - blh / 2 - 2, color=INK, sw=1.7))
    frags.append(text(tlx - tlw / 2 - 12, (tly + bly) / 2, "f_in", size=13, color=INK,
                      bold=True, anchor="end"))
    frags.append(text(tlx - tlw / 2 - 12, (tly + bly) / 2 + 18, "перекласти вхід",
                      size=10.5, color=MUTED, anchor="end"))

    # праве ребро — f_out (знизу вгору)
    frags.append(arrow(brx, bry - brh / 2 - 2, trx, try_ + trh / 2 + 2, color=INK, sw=1.7))
    frags.append(text(trx + trw / 2 + 12, (tly + bly) / 2, "f_out", size=13, color=INK,
                      bold=True, anchor="start"))
    frags.append(text(trx + trw / 2 + 12, (tly + bly) / 2 + 18, "перекласти вихід",
                      size=10.5, color=MUTED, anchor="start"))

    # нижнє ребро — робота Adaptee
    frags.append(arrow(blx + blw / 2 + 2, bly, brx - brw / 2 - 2, bry, color=NEG, sw=1.7))
    frags.append(text(W / 2, bly + blh / 2 + 22, "робота Adaptee (specificRequest)",
                      size=11.5, color=NEG))

    # підпис-висновок
    frags.append(fitbox(150, 495, 700, 66,
                        ["Адаптер вірний ⟺ обидва шляхи від лівого-верху до правого-верху дають те саме.",
                         "f_in губить потрібну Adaptee інформацію → квадрат не замкнути → адаптер тече."],
                        size=12, pad=10, fill=FILL, stroke=LINE, sw=1.4))

    render(os.path.join(IMG, 'translation-square.svg'), W, H, *frags)


# ── Контейнерний адаптер: звуження інтерфейсу (детальна) ─────────────────────
def fig_container_adapter():
    W, H = 1120, 560
    frags = []
    frags.append(text(W / 2, 34,
                      "std::stack адаптує контейнер: звужує багатий інтерфейс до трьох операцій",
                      size=15.5, bold=True, color=INK))

    frags.append(text(255, 92, "std::stack — адаптер", size=14, bold=True, color=FIELD))
    frags.append(text(690, 92, "std::deque — підлеглий контейнер", size=14, bold=True, color=NEG))

    rows = [("push(v)", "push_back(v)"),
            ("pop()", "pop_back()"),
            ("top()", "back()")]
    ys = [165, 275, 385]
    for (lop, rop), y in zip(rows, ys):
        lb, lbw, lbh = textbox(255, y, lop, size=13, bold=True,
                               fill="#e8f6ee", stroke=FIELD, sw=1.8, min_w=180)
        rb, rbw, rbh = textbox(690, y, rop, size=13, bold=True,
                               fill=FILL, stroke=LINE, sw=1.6, min_w=220)
        frags += [lb, rb]
        frags.append(arrow(255 + lbw / 2 + 4, y, 690 - rbw / 2 - 4, y, color=INK, sw=1.7))

    frags.append(text((255 + 690) / 2, 148, "переклад імені", size=11, color=MUTED))

    # приховані методи контейнера
    frags.append(fitbox(190, 452, 740, 74,
                        ["Приховані стеком (недосяжні): push_front · pop_front · front",
                         "operator[] · at · insert · erase        (empty, size — проходять як є)"],
                        size=12, pad=10, fill="#f7f2ea", stroke=MUTED, sw=1.4))

    render(os.path.join(IMG, 'container-adapter.svg'), W, H, *frags)


# ── Функція абстракції Гоара: α, f_in та інваріант представлення ──────────────
def fig_abstraction_map():
    W, H = 1040, 560
    frags = []
    frags.append(text(W / 2, 34,
                      "Функція абстракції Гоара: α піднімає справні представлення в семантику Target",
                      size=15, bold=True, color=INK))

    # Простір Target (угорі)
    tgx, tgy = 330, 150
    tg, tgw, tgh = textbox(tgx, tgy, ["Простір Target — T", "значення, які обіцяє контракт"],
                           size=13, bold=True, fill="#e8f6ee", stroke=FIELD, sw=1.8, min_w=380)
    frags.append(tg)

    # Інваріант I ⊆ A (унизу, справні стани)
    ivx, ivy = 330, 400
    iv, ivw, ivh = textbox(ivx, ivy, ["Інваріант I ⊆ A", "справні стани Adaptee"],
                           size=13, bold=True, fill="#eef7f1", stroke=FIELD, sw=1.6, min_w=380)
    frags.append(iv)

    midy = (tgy + ivy) / 2
    # α (угору, ліворуч): від I до T
    ax = 250
    frags.append(arrow(ax, ivy - ivh / 2 - 2, ax, tgy + tgh / 2 + 2, color=INK, sw=1.8))
    frags.append(text(ax - 16, midy - 6, "α = f_out", size=13, color=INK, bold=True, anchor="end"))
    frags.append(text(ax - 16, midy + 15, "(абстракція)", size=10.5, color=MUTED, anchor="end"))

    # f_in (униз, праворуч): від T до I
    fx = 410
    frags.append(arrow(fx, tgy + tgh / 2 + 2, fx, ivy - ivh / 2 - 2, color=INK, sw=1.8))
    frags.append(text(fx + 16, midy - 6, "f_in", size=13, color=INK, bold=True, anchor="start"))
    frags.append(text(fx + 16, midy + 15, "(вибір представлення)", size=10.5, color=MUTED, anchor="start"))

    # A ∖ I — стани поза інваріантом
    frags.append(fitbox(640, 348, 350, 112,
                        ["A ∖ I — стани поза інваріантом",
                         "α не визначена — саме тут адаптер тече"],
                        size=12.5, pad=12, fill=FILL, stroke=MUTED, sw=1.4))

    frags.append(fitbox(140, 492, 760, 46,
                        ["Пара (f_in, α): f_in обирає представлення в I, α читає з нього значення Target.",
                         "За межами I пари немає — і жодне f_out не відновить того, чого f_in не дав."],
                        size=12, pad=10, fill="#f7f2ea", stroke=MUTED, sw=1.3))

    render(os.path.join(IMG, 'abstraction-map.svg'), W, H, *frags)


# ── Втрата інформації у f_in: квадрат не замкнути ────────────────────────────
def fig_square_collapse():
    W, H = 920, 720
    frags = []
    frags.append(text(W / 2, 34, "Втрата інформації у f_in робить квадрат незамкненим",
                      size=15.5, bold=True, color=INK))
    frags.append(text(460, 76, "два входи, які Target тримає нарізно",
                      size=12.5, bold=True, color=MUTED))

    # два входи
    x1, x1w, x1h = textbox(350, 122, ["x₁"], size=14, bold=True,
                           fill="#e8f6ee", stroke=FIELD, sw=1.8, min_w=110)
    x2, x2w, x2h = textbox(570, 122, ["x₂"], size=14, bold=True,
                           fill="#e8f6ee", stroke=FIELD, sw=1.8, min_w=110)
    frags += [x1, x2]

    # склеювання f_in → a
    a, aw, ah = textbox(460, 242, ["a = f_in(x₁) = f_in(x₂)"], size=13, bold=True,
                        fill="#eaf0fd", stroke=NEG, sw=1.8, min_w=300)
    frags.append(a)
    frags.append(arrow(350, 122 + x1h / 2 + 2, 430, 242 - ah / 2 - 2, color=INK, sw=1.7))
    frags.append(arrow(570, 122 + x2h / 2 + 2, 490, 242 - ah / 2 - 2, color=INK, sw=1.7))
    frags.append(text(250, 182, "f_in склеює два входи", size=12, color=INK,
                      bold=True, anchor="end"))

    # Adaptee: a → b
    b, bw, bh = textbox(460, 362, ["b = Adaptee(a)", "один вихід"], size=13, bold=True,
                        fill="#eaf0fd", stroke=NEG, sw=1.7, min_w=300)
    frags.append(b)
    frags.append(arrow(460, 242 + ah / 2 + 2, 460, 362 - bh / 2 - 2, color=NEG, sw=1.7))
    frags.append(text(662, 302, "робота Adaptee", size=12, color=NEG, anchor="start"))

    # f_out: b → v
    v, vw, vh = textbox(460, 500, ["v = f_out(b)", "єдине значення"], size=13, bold=True,
                        fill="#fff8f0", stroke=POS, sw=1.9, min_w=300)
    frags.append(v)
    frags.append(arrow(460, 362 + bh / 2 + 2, 460, 500 - vh / 2 - 2, color=POS, sw=1.7))
    frags.append(text(662, 446, "f_out", size=13, color=POS, bold=True, anchor="start"))

    # два несумісні цільові виходи
    y1, y1w, y1h = textbox(350, 612, ["y₁"], size=14, bold=True,
                           fill="#e8f6ee", stroke=FIELD, sw=1.8, min_w=110)
    y2, y2w, y2h = textbox(570, 612, ["y₂"], size=14, bold=True,
                           fill="#e8f6ee", stroke=FIELD, sw=1.8, min_w=110)
    frags += [y1, y2]
    frags.append(text(460, 620, "≠", size=24, color=POS, bold=True))
    frags.append(arrow(460, 500 + vh / 2 + 2, 360, 612 - y1h / 2 - 2, color=POS, sw=1.5))
    frags.append(arrow(460, 500 + vh / 2 + 2, 560, 612 - y2h / 2 - 2, color=POS, sw=1.5))
    frags.append(text(356, 566, "=?", size=13, color=POS, bold=True, anchor="end"))
    frags.append(text(564, 566, "=?", size=13, color=POS, bold=True, anchor="start"))

    frags.append(fitbox(110, 662, 700, 48,
                        ["v — одне значення, а мусило б дорівнювати водночас y₁ і y₂ (y₁ ≠ y₂).",
                         "Суперечність: квадрат не замкнути — втрату у f_in не відновить жодне f_out."],
                        size=12, pad=10, fill="#f7f2ea", stroke=MUTED, sw=1.3))

    render(os.path.join(IMG, 'square-collapse.svg'), W, H, *frags)


# ── Композиція двох вірних адаптерів: A→B→C дає A→C ──────────────────────────
def fig_adapter_compose():
    W, H = 1000, 600
    frags = []
    frags.append(text(W / 2, 34, "Композиція двох вірних адаптерів: A→B→C дає вірний A→C",
                      size=15.5, bold=True, color=INK))

    frags.append(text(190, 72, "F_in: вниз", size=12.5, bold=True, color=INK))
    frags.append(text(810, 72, "F_out: вгору", size=12.5, bold=True, color=INK))

    A, Aw, Ah = textbox(500, 120, ["A — Target (що бачить клієнт)"], size=13, bold=True,
                        fill="#e8f6ee", stroke=FIELD, sw=1.8, min_w=480)
    B, Bw, Bh = textbox(500, 300, ["B — проміжний інтерфейс"], size=13, bold=True,
                        fill=FILL, stroke=LINE, sw=1.6, min_w=480)
    C, Cw, Ch = textbox(500, 480, ["C — Adaptee (справжній виконавець)"], size=13, bold=True,
                        fill="#eaf0fd", stroke=NEG, sw=1.8, min_w=480)
    frags += [A, B, C]

    # ліворуч — вхід іде вниз
    frags.append(arrow(300, 120 + Ah / 2 + 2, 300, 300 - Bh / 2 - 2, color=INK, sw=1.7))
    frags.append(arrow(300, 300 + Bh / 2 + 2, 300, 480 - Ch / 2 - 2, color=INK, sw=1.7))
    frags.append(text(245, 210, "f_in¹", size=13, color=INK, bold=True, anchor="end"))
    frags.append(text(245, 390, "f_in²", size=13, color=INK, bold=True, anchor="end"))

    # праворуч — вихід іде вгору (зворотний порядок)
    frags.append(arrow(700, 480 - Ch / 2 - 2, 700, 300 + Bh / 2 + 2, color=POS, sw=1.7))
    frags.append(arrow(700, 300 - Bh / 2 - 2, 700, 120 + Ah / 2 + 2, color=POS, sw=1.7))
    frags.append(text(755, 390, "f_out²", size=13, color=POS, bold=True, anchor="start"))
    frags.append(text(755, 210, "f_out¹", size=13, color=POS, bold=True, anchor="start"))

    frags.append(fitbox(140, 545, 720, 44,
                        ["Підставляємо ⟦B⟧ = f_out² ∘ ⟦C⟧ ∘ f_in² у ⟦A⟧ = f_out¹ ∘ ⟦B⟧ ∘ f_in¹:",
                         "⟦A⟧ = (f_out¹ ∘ f_out²) ∘ ⟦C⟧ ∘ (f_in² ∘ f_in¹).   Вихідний бік — зворотним порядком."],
                        size=12, pad=10, fill="#f7f2ea", stroke=MUTED, sw=1.3))

    render(os.path.join(IMG, 'adapter-compose.svg'), W, H, *frags)


# ── Перехідник парадигми: переклад керування в часі (proj callback→async) ────
def fig_time_translation():
    W, H = 1180, 620
    frags = []
    frags.append(text(W / 2, 40,
                      "Перехідник парадигми перекладає не підпис, а керування в часі",
                      size=17, bold=True, color=INK))

    lx = 400   # центр лівої колонки (світ колбеків)
    rx = 880   # центр правої колонки (світ async)
    frags.append(text(lx, 96, "світ колбеків", size=14, bold=True, color=NEG))
    frags.append(text(rx, 96, "світ async / await", size=14, bold=True, color=FIELD))

    rows = [
        ("результат",     "cb(null, value)",             "resolve(value)"),
        ("помилка",       "cb(err) — перший аргумент",    "reject(err) / throw"),
        ("скільки разів", "0 … ∞ викликів",               "рівно 1 — проміс застигає"),
        ("скасування",    "власний прапорець",            "AbortSignal"),
        ("прибирання",    "removeListener вручну",         "finally / автозняття"),
    ]
    y0, dy = 158, 88
    for i, (axis, lft, rgt) in enumerate(rows):
        y = y0 + i * dy
        frags.append(text(56, y + 4, axis, size=12.5, bold=True,
                          color=MUTED, anchor="start"))
        lb, lbw, lbh = textbox(lx, y, lft, size=12.5, bold=True,
                               fill="#eaf0fd", stroke=NEG, sw=1.6, min_w=300)
        rb, rbw, rbh = textbox(rx, y, rgt, size=12.5, bold=True,
                               fill="#e8f6ee", stroke=FIELD, sw=1.6, min_w=300)
        frags += [lb, rb]
        frags.append(arrow(lx + lbw / 2 + 8, y, rx - rbw / 2 - 8, y,
                           color=INK, sw=1.7))

    frags.append(text(W / 2, H - 34,
                      "кожен рядок треба замкнути — інакше час «протікає» крізь межу: "
                      "загублена помилка, витік слухачів, подвійний виклик",
                      size=12.5, color=MUTED))
    render(os.path.join(IMG, 'time-translation.svg'), W, H, *frags)


# ── Одноразовий проміс проти потоку подій: чому два різні перехідники ─────────
def fig_oneshot_vs_stream():
    W, H = 1160, 560
    frags = []
    frags.append(text(W / 2, 38,
                      "Одноразовий проміс проти потоку подій: чому потрібні ДВА перехідники",
                      size=16, bold=True, color=INK))

    # ── ВЕРХ: одноразова операція → Promise ──────────────────────────────────
    frags.append(text(70, 108, "одноразова операція", size=13.5, bold=True,
                      color=FIELD, anchor="start"))
    ty = 172
    frags.append(line(120, ty, 700, ty, color=LINE, sw=1.6))
    frags.append(arrow(700, ty, 748, ty, color=LINE, sw=1.6))
    frags.append(circle(180, ty, 7, fill="#e8f6ee", stroke=FIELD, sw=2))
    frags.append(text(180, ty - 18, "виклик", size=11.5, color=INK))
    frags.append(circle(470, ty, 7, fill="#e8f6ee", stroke=FIELD, sw=2))
    frags.append(text(470, ty - 18, "результат — 1 раз", size=11.5, color=FIELD, bold=True))
    frags.append(text(628, ty + 26, "далі застигло: 2-й resolve — no-op",
                      size=11, color=MUTED))
    mb, mbw, mbh = textbox(952, ty, ["Promise<T>", "await p"], size=13, bold=True,
                           fill="#e8f6ee", stroke=FIELD, sw=1.8, min_w=210)
    frags.append(mb)

    # ── НИЗ: потік подій → async-ітератор ────────────────────────────────────
    frags.append(text(70, 324, "потік подій", size=13.5, bold=True,
                      color=NEG, anchor="start"))
    by = 388
    frags.append(line(120, by, 700, by, color=LINE, sw=1.6))
    frags.append(arrow(700, by, 748, by, color=LINE, sw=1.6))
    for x in (180, 300, 420, 540):
        frags.append(circle(x, by, 7, fill="#eaf0fd", stroke=NEG, sw=2))
        frags.append(text(x, by - 18, "подія", size=11, color=NEG))
    frags.append(circle(650, by, 7, fill=FILL, stroke=LINE, sw=2))
    frags.append(text(650, by - 18, "end", size=11, color=INK))
    mb2, mb2w, mb2h = textbox(952, by, ["AsyncIterable<T>", "for await … of"],
                              size=13, bold=True, fill="#eaf0fd", stroke=NEG,
                              sw=1.8, min_w=210)
    frags.append(mb2)

    frags.append(text(W / 2, H - 32,
                      "проміс розв'язується РАЗ і застигає, потік триває до кінця — "
                      "тому одноразову обгортаємо в проміс, а багаторазову в async-ітератор",
                      size=12, color=MUTED))
    render(os.path.join(IMG, 'oneshot-vs-stream.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_adapter_roles()
    fig_object_vs_class()
    fig_four_participants()
    fig_translation_square()
    fig_container_adapter()
    fig_abstraction_map()
    fig_square_collapse()
    fig_adapter_compose()
    fig_time_translation()
    fig_oneshot_vs_stream()
    print("figs done")


# ── (hist-вставка hist-wrapper-impedance) фігури історії назв адаптера ────────
def fig_wrapper_fork():
    W, H = 1100, 520
    frags = []
    frags.append(text(W / 2, 40, "«Wrapper» називає ФОРМУ, а не намір — тому імен два",
                      size=17, bold=True, color=INK))
    wr, wrw, wrh = textbox(W / 2, 135,
                           ["Wrapper — «обгортка»",
                            "об'єкт усередині об'єкта; виклик проходить крізь"],
                           size=13.5, bold=True, fill=FILL, stroke=LINE, sw=1.8, min_w=520)
    frags.append(wr)
    adx, chy = 300, 360
    ad, adw, adh = textbox(adx, chy,
                           ["Adapter (Адаптер)", "МІНЯЄ інтерфейс",
                            "поведінку не додає", "«інший роз'єм»"],
                           size=13, bold=True, fill="#e8f6ee", stroke=FIELD, sw=1.9, min_w=310)
    frags.append(ad)
    dcx = 800
    dc, dcw, dch = textbox(dcx, chy,
                           ["Decorator (Декоратор)", "ЗБЕРІГАЄ інтерфейс",
                            "ДОДАЄ поведінку", "«той самий роз'єм»"],
                           size=13, bold=True, fill="#eaf0fd", stroke=NEG, sw=1.9, min_w=310)
    frags.append(dc)
    frags.append(arrow(W / 2 - 70, 135 + wrh / 2, adx + 40, chy - adh / 2 - 2, color=LINE, sw=1.8))
    frags.append(arrow(W / 2 + 70, 135 + wrh / 2, dcx - 40, chy - dch / 2 - 2, color=LINE, sw=1.8))
    frags.append(fitbox(170, 448, 760, 54,
                        ["Обидва фізично загортають чужий об'єкт — тому GoF позначив кожен і словом «Wrapper».",
                         "Але намір різний, тож у кожного лишилось і власне, точніше ім'я."],
                        size=12.5, pad=10, fill="#f7f2ea", stroke=MUTED, sw=1.4))
    render(os.path.join(IMG, 'wrapper-fork.svg'), W, H, *frags)


def fig_impedance():
    W, H = 1200, 560
    frags = []
    frags.append(text(W / 2, 40, "Неузгодження імпедансів: чому взагалі потрібен перехідник",
                      size=17, bold=True, color=INK))
    frags.append(line(600, 92, 600, 430, color="#d0d5db", sw=1.2, dash="6,6"))
    frags.append(text(310, 118, "Неузгоджено", size=15, bold=True, color=POS))
    zs, zsw, zsh = textbox(190, 250, ["Джерело", "Z = 8 Ω"], size=13, bold=True,
                           fill=FILL, stroke=LINE, sw=1.7, min_w=150)
    zl, zlw, zlh = textbox(470, 250, ["Навантаження", "Z = 75 Ω"], size=13, bold=True,
                           fill=FILL, stroke=LINE, sw=1.7, min_w=175)
    frags += [zs, zl]
    frags.append(line(330, 216, 330, 284, color=POS, sw=1.6, dash="4,4"))
    frags.append(arrow(190 + zsw / 2 + 4, 236, 470 - zlw / 2 - 4, 236, color=FIELD, sw=1.8))
    frags.append(arrow(470 - zlw / 2 - 10, 268, 190 + zsw / 2 + 4, 268, color=POS, sw=1.8))
    frags.append(fitbox(70, 330, 470, 62,
                        ["Опір стрибає 8 → 75 Ω. Частина хвилі відбивається назад (червона стрілка)",
                         "— ця потужність не доходить до навантаження, губиться на межі."],
                        size=12, pad=10, fill=FILL, stroke=MUTED, sw=1.3))
    frags.append(text(890, 118, "Узгоджено", size=15, bold=True, color=FIELD))
    zs2, zs2w, zs2h = textbox(700, 250, ["Джерело", "8 Ω"], size=13, bold=True,
                              fill=FILL, stroke=LINE, sw=1.7, min_w=130)
    mt, mtw, mth = textbox(890, 250, ["Узгоджувач", "(перехідник)"], size=13, bold=True,
                           fill="#e8f6ee", stroke=FIELD, sw=1.9, min_w=150)
    zl2, zl2w, zl2h = textbox(1080, 250, ["Навантаження", "75 Ω"], size=13, bold=True,
                              fill=FILL, stroke=LINE, sw=1.7, min_w=150)
    frags += [zs2, mt, zl2]
    frags.append(arrow(700 + zs2w / 2 + 4, 250, 890 - mtw / 2 - 4, 250, color=FIELD, sw=1.8))
    frags.append(arrow(890 + mtw / 2 + 4, 250, 1080 - zl2w / 2 - 4, 250, color=FIELD, sw=1.8))
    frags.append(fitbox(640, 330, 470, 62,
                        ["Проміжна ланка згладжує стрибок опору. Хвиля проходить уся,",
                         "без відбивання — уся потужність доходить до навантаження."],
                        size=12, pad=10, fill=FILL, stroke=MUTED, sw=1.3))
    frags.append(fitbox(120, 462, 960, 66,
                        ["У коді — те саме: світ об'єктів і світ реляційних таблиць мають різний «опір».",
                         "Адаптер (чи ORM) — це узгоджувач між ними, щоб дані пройшли без втрат на «відбивання»."],
                        size=12.5, pad=11, fill="#f7f2ea", stroke=MUTED, sw=1.4))
    render(os.path.join(IMG, 'impedance.svg'), W, H, *frags)


def fig_name_timeline():
    W, H = 1220, 470
    frags = []
    frags.append(text(W / 2, 40, "Мандри однієї метафори: 108 років слова «impedance»",
                      size=17, bold=True, color=INK))
    spine_y = 210
    frags.append(line(120, spine_y, 1100, spine_y, color=INK, sw=2))
    stops = [
        (180, "1886", ["Олівер Гевісайд", "вводить «impedance»", "в електротехніці"]),
        (480, "1984", ["Copeland & Maier:", "«impedance mismatch»", "Smalltalk ↔ база даних"]),
        (780, "1990", ["ObjectWorks" + chr(92) + "Smalltalk:", "«pluggable adapter»", "адаптація вбудована в клас"]),
        (1080, "1994", ["GoF: «Adapter (Wrapper)»", "патерн дістає", "подвійне канонічне ім'я"]),
    ]
    for sx, yr, desc in stops:
        frags.append(text(sx, 182, yr, size=16, bold=True, color=POS))
        frags.append(circle(sx, spine_y, 6, fill=POS, stroke=POS, sw=1))
        frags.append(line(sx, spine_y + 6, sx, 270, color=MUTED, sw=1.3))
        b, bw, bh = textbox(sx, 305, desc, size=12, bold=False,
                            fill=FILL, stroke=LINE, sw=1.5, min_w=250)
        frags.append(b)
    frags.append(fitbox(210, 400, 800, 50,
                        ["Образ старший за патерн: від телеграфних ліній Гевісайда до назви",
                         "обгортки над чужим об'єктом слово мандрувало понад століття."],
                        size=12.5, pad=10, fill="#f7f2ea", stroke=MUTED, sw=1.4))
    render(os.path.join(IMG, 'name-timeline.svg'), W, H, *frags)


# окремий guard (подвійні лапки — щоб не збігтися з головним анкером інших агентів)
if __name__ == "__main__":
    fig_wrapper_fork()
    fig_impedance()
    fig_name_timeline()

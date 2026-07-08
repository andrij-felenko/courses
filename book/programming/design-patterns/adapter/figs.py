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


if __name__ == '__main__':
    fig_adapter_roles()
    fig_object_vs_class()
    print("figs done")

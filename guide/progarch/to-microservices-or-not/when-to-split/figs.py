# -*- coding: utf-8 -*-
"""Фігури до кроку «Коли й як різати» (guide/progarch/to-microservices-or-not)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

GREEN_TINT = "#eafaf0"
RED_TINT = "#fdecea"
NEUT = "#f7f8fa"


def fig_quadrant():
    """Зчеплення × розподіленість: чотири квадранти, розподілений моноліт — найгірший."""
    W, H = 900, 600
    L, R, T, B = 170, 830, 96, 506         # межі поля
    mx, my = (L + R) / 2, (T + B) / 2      # серединні лінії
    frags = []

    # напис про напрям осей (між заголовком render і полем)
    frags.append(text(W / 2, 74, "по вертикалі — розподіленість,   по горизонталі — зчеплення",
                      size=12, color=MUTED))

    # чотири клітини (спершу заливки)
    frags.append(rect(L, my, mx - L, B - my, fill=GREEN_TINT, stroke="none", sw=0, rx=0))   # BL
    frags.append(rect(mx, my, R - mx, B - my, fill=NEUT, stroke="none", sw=0, rx=0))         # BR
    frags.append(rect(L, T, mx - L, my - T, fill=GREEN_TINT, stroke="none", sw=0, rx=0))     # TL
    frags.append(rect(mx, T, R - mx, my - T, fill=RED_TINT, stroke="none", sw=0, rx=0))      # TR

    # рамка поля + серединні лінії
    frags.append(rect(L, T, R - L, B - T, fill="none", stroke=LINE, sw=1.8))
    frags.append(line(mx, T, mx, B, color=LINE, sw=1.4))
    frags.append(line(L, my, R, my, color=LINE, sw=1.4))

    # центри квадрантів
    blc, brc = (335, 402), (665, 402)
    tlc, trc = (335, 197), (665, 197)

    # напрямні стрілки (у порожньому проміжку між рамками): угору = додати мережу
    frags.append(arrow(335, 360, 335, 242, color=FIELD, sw=3))    # ліворуч (низьке зчеплення) — варто
    frags.append(arrow(665, 360, 665, 242, color=POS, sw=3))      # праворуч (високе зчеплення) — у червоне

    # підписи квадрантів (рамка сама вміщує напис)
    b, _, _ = textbox(*blc, "модульний моноліт\nчисті межі, один процес",
                      size=13, fill=GREEN_TINT, stroke=FIELD, bold=True)
    frags.append(b)
    b, _, _ = textbox(*brc, "моноліт-клубок\nбез меж, один процес",
                      size=13, fill="#ffffff", stroke=MUTED)
    frags.append(b)
    b, _, _ = textbox(*tlc, "мікросервіси\nчисті межі, по мережі",
                      size=13, fill=GREEN_TINT, stroke=FIELD, bold=True)
    frags.append(b)
    b, _, _ = textbox(*trc, "РОЗПОДІЛЕНИЙ МОНОЛІТ\nмережа + усе зчеплення",
                      size=13, fill=RED_TINT, stroke=POS, color=POS, bold=True)
    frags.append(b)

    # підписи осей — по краях поля
    frags.append(text(335, 534, "← низьке зчеплення", size=12, color=MUTED))
    frags.append(text(665, 534, "високе зчеплення →", size=12, color=MUTED))
    frags.append(text(L - 12, my - 66, "по", size=11, color=MUTED, anchor="end"))
    frags.append(text(L - 12, my - 52, "мережі", size=11, color=MUTED, anchor="end"))
    frags.append(text(L - 12, my + 52, "один", size=11, color=MUTED, anchor="end"))
    frags.append(text(L - 12, my + 66, "процес", size=11, color=MUTED, anchor="end"))
    frags.append(text(L - 40, my, "↕", size=18, color=MUTED, anchor="end"))

    render(os.path.join(IMG, "coupling-distribution.svg"), W, H, *frags,
           title="Додавати мережу варто лише з лівого, низькозчепленого боку")


def module_box(cx, cy, label, kind="plain"):
    """Маленький модуль усередині моноліта. kind: plain|target|faint."""
    if kind == "target":
        fill, stroke, col, bold, dash = GREEN_TINT, FIELD, INK, True, None
    elif kind == "faint":
        fill, stroke, col, bold, dash = "#ffffff", MUTED, MUTED, False, "5,4"
    else:
        fill, stroke, col, bold, dash = FILL, LINE, INK, False, None
    w, h = 150, 54
    out = ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="7" fill="%s" '
           'stroke="%s" stroke-width="1.6"%s/>' %
           (cx - w / 2, cy - h / 2, w, h, fill, stroke,
            (' stroke-dasharray="%s"' % dash) if dash else ''))
    out += text(cx, cy + 5, label, size=13, color=col, bold=bold)
    return out


def db_box(cx, cy, label="БД"):
    out = rect(cx - 24, cy - 27, 48, 54, fill="#eef2fb", stroke=NEG, sw=1.6, rx=8)
    out += text(cx, cy + 5, label, size=12, color=NEG, bold=True)
    return out


def fig_safe_cut():
    """Три стадії strangler: чистий шов → сервіс поряд (крапля) → старе прибрано."""
    W, H = 1200, 470
    cA, cB, cC = 200, 600, 995
    frags = []

    # ── заголовки стадій ──
    for cx, t in [(cA, "1 · чистий шов"), (cB, "2 · сервіс поряд"), (cC, "3 · старе прибрано")]:
        b, _, _ = textbox(cx, 62, t, size=14, fill="#eef2fb", stroke=NEG, bold=True)
        frags.append(b)

    # стрілки-переходи між стадіями
    frags.append(arrow(372, 205, 404, 205, color=INK, sw=2.2))
    frags.append(arrow(792, 205, 824, 205, color=INK, sw=2.2))

    # ══ Стадія A ══
    frags.append(text(70, 130, "моноліт", size=11, color=MUTED, anchor="start"))
    frags.append(rect(60, 116, 300, 168, fill="none", stroke=LINE, sw=1.8))
    frags.append(module_box(210, 205, "Твін", "target"))
    frags.append(line(120, 246, 300, 246, color=MUTED, sw=1))            # роздільник
    frags.append(text(210, 266, "… інші модулі", size=11, color=MUTED))
    # шов
    frags.append('<rect x="126" y="172" width="168" height="66" rx="8" fill="none" '
                 'stroke="%s" stroke-width="1.6" stroke-dasharray="6,5"/>' % FIELD)
    b, _, _ = textbox(210, 100, "запити твіна", size=11, fill=FILL, stroke=MUTED)
    frags.append(b)
    frags.append(arrow(210, 112, 210, 176, color=INK, sw=2))

    # ══ Стадія B ══
    frags.append(text(440, 130, "моноліт", size=11, color=MUTED, anchor="start"))
    frags.append(rect(432, 116, 170, 168, fill="none", stroke=LINE, sw=1.8))
    frags.append(module_box(517, 205, "Твін", "faint"))
    frags.append(line(447, 246, 597, 246, color=MUTED, sw=1))
    frags.append(text(517, 266, "… інші модулі", size=11, color=MUTED))
    # сервіс поряд + БД
    frags.append(module_box(700, 205, "Твін-сервіс", "target"))
    frags.append(db_box(700, 268))
    b, _, _ = textbox(600, 100, "запити твіна", size=11, fill=FILL, stroke=MUTED)
    frags.append(b)
    frags.append(arrow(576, 112, 540, 176, color=MUTED, sw=2.6))         # старий шлях (товстий)
    frags.append(arrow(624, 112, 690, 176, color=FIELD, sw=1.6))         # крапля (тонка)
    frags.append(text(690, 140, "крапля", size=10, color=FIELD, bold=True, anchor="start"))

    # ══ Стадія C ══
    frags.append(text(838, 130, "моноліт", size=11, color=MUTED, anchor="start"))
    frags.append(rect(830, 116, 180, 168, fill="none", stroke=LINE, sw=1.8))
    frags.append(text(920, 200, "твін винесено", size=10, color=MUTED, italic=True))
    frags.append(line(848, 226, 992, 226, color=MUTED, sw=1))
    frags.append(text(920, 250, "… інші модулі", size=11, color=MUTED))
    frags.append(module_box(1095, 205, "Твін-сервіс", "target"))
    frags.append(db_box(1095, 268))
    b, _, _ = textbox(995, 100, "запити твіна", size=11, fill=FILL, stroke=MUTED)
    frags.append(b)
    frags.append(arrow(970, 112, 916, 176, color=MUTED, sw=1.6))         # інші → моноліт
    frags.append(arrow(1018, 112, 1082, 176, color=FIELD, sw=3))         # увесь трафік → сервіс

    # ══ смуга зворотності ══
    frags.append(line(70, 358, 250, 358, color=FIELD, sw=3))
    frags.append(line(550, 358, 748, 358, color=FIELD, sw=3))
    b, _, _ = textbox(400, 358, "зворотно — трафік можна повернути назад",
                      size=12, fill=GREEN_TINT, stroke=FIELD, color=INK)
    frags.append(b)
    frags.append(line(812, 340, 812, 376, color=POS, sw=2.6))
    b, _, _ = textbox(980, 358, "незворотно — старе прибрано",
                      size=12, fill=RED_TINT, stroke=POS, color=POS, bold=True)
    frags.append(b)

    render(os.path.join(IMG, "safe-cut.svg"), W, H, *frags,
           title="Розріз — це перехід, а не подія")


def _node(cx, cy, r, kind="plain"):
    if kind == "mono":
        return circle(cx, cy, r, fill=GREEN_TINT, stroke=FIELD, sw=2)
    if kind == "many":
        return circle(cx, cy, r, fill="#ffffff", stroke=MUTED, sw=1.6)
    return circle(cx, cy, r, fill=FILL, stroke=LINE, sw=1.6)


def fig_pendulum():
    """Спектр відповідей на перекрут: Segment (повний відкат), Prime Video
    (один компонент), Uber (не відкат, а лад). Ліворуч моноліт, праворуч мікросервіси."""
    W, H = 1060, 620
    xM, xS = 226, 828                  # вісь: моноліт ←→ мікросервіси
    topG, botG = 108, 566
    frags = []

    # ── дві напрямні осі ──
    frags.append(line(xM, topG, xM, botG, color=MUTED, sw=1.2, dash="5,6"))
    frags.append(line(xS, topG, xS, botG, color=MUTED, sw=1.2, dash="5,6"))
    frags.append(mtext(xM, 66, ["МОНОЛІТ", "один процес"], size=13, bold=True, color=NEG))
    frags.append(mtext(xS, 66, ["МІКРОСЕРВІСИ", "багато процесів"], size=13, bold=True, color=MUTED))
    frags.append(text(W / 2, 96, "← менше меж-процесів        більше меж-процесів →",
                      size=11, color=MUTED))

    r1, r2, r3 = 190, 330, 476

    # ── Segment: повний відкат праворуч → ліворуч ──
    b, _, _ = textbox(96, r1, "Segment\n2017", size=13, fill=FILL, stroke=NEG, bold=True)
    frags.append(b)
    frags.append(_node(xS, r1, 8, "many"))
    frags.append(text(xS, r1 - 24, "100+ сервісів", size=12, color=MUTED))
    frags.append(_node(xM, r1, 11, "mono"))
    frags.append(text(xM, r1 - 26, "1 моноліт", size=12, color=INK, bold=True))
    frags.append(text(xM, r1 - 12, "(Centrifuge)", size=10, color=MUTED))
    frags.append(arrow(xS - 16, r1, xM + 18, r1, color=FIELD, sw=3.2))
    frags.append(text((xM + xS) / 2, r1 + 26,
                      "повний відкат — складність росла лінійно з кожною інтеграцією",
                      size=12, color=INK))

    # ── Prime Video: один компонент, коротший рух ──
    b, _, _ = textbox(96, r2, "Prime Video\n2023", size=13, fill=FILL, stroke=NEG, bold=True)
    frags.append(b)
    xPV = 690
    frags.append(_node(xPV, r2, 8, "many"))
    frags.append(mtext(xPV, r2 - 24, ["Step Functions", "+ S3 між кроками"], size=11, color=MUTED))
    frags.append(_node(xM + 46, r2, 10, "mono"))
    frags.append(text(xM + 46, r2 - 22, "один процес", size=12, color=INK, bold=True))
    frags.append(arrow(xPV - 16, r2, xM + 62, r2, color=FIELD, sw=2.6))
    frags.append(text((xM + 46 + xPV) / 2, r2 + 26,
                      "−90 % витрат на ОДИН компонент — консолідований сервіс, не вся платформа",
                      size=12, color=INK))

    # ── Uber: не відкат, а лад — лишились праворуч, згруповані ──
    b, _, _ = textbox(96, r3, "Uber\n2020", size=13, fill=FILL, stroke=NEG, bold=True)
    frags.append(b)
    # хмарка з багатьох сервісів праворуч
    import math
    cxU, cyU = 748, r3
    pts = [(-52, -14), (-26, 10), (0, -16), (24, 8), (50, -10),
           (-40, 14), (12, 16), (-12, -2), (38, -18), (60, 12)]
    for dx, dy in pts:
        frags.append(_node(cxU + dx, cyU + dy, 5, "many"))
    # рамка-домен навколо хмарки
    frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="14" fill="none" '
                 'stroke="%s" stroke-width="1.8" stroke-dasharray="7,5"/>'
                 % (cxU - 78, cyU - 34, 168, 68, FIELD))
    frags.append(text(cxU, r3 - 46, "2200 сервісів", size=12, color=MUTED))
    frags.append(text(cxU, r3 + 52, "70 доменів · жорсткі контракти · шари", size=11, color=FIELD, bold=True))
    # позначка «без відкату» на боці моноліта
    frags.append(text(xM, r3, "×", size=22, color=POS, bold=True))
    frags.append(mtext(xM, r3 + 22, ["ліворуч", "не рухались"], size=10, color=POS))
    frags.append(text((xM + cxU) / 2 + 10, r3 + 84,
                      "не відкат, а лад: приборкати мікросервіси на місці",
                      size=12, color=INK))

    render(os.path.join(IMG, "pendulum-spectrum.svg"), W, H, *frags,
           title="Три відповіді на перекрут: відкотити, консолідувати шматок — чи впорядкувати")


if __name__ == "__main__":
    fig_quadrant()
    fig_safe_cut()
    fig_pendulum()
    print("OK: coupling-distribution.svg, safe-cut.svg, pendulum-spectrum.svg")

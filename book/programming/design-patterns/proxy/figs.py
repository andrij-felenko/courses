# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Будова проксі: клієнт → заступник → (ліниво) справжній об'єкт ─────────────
def fig_proxy_structure():
    W, H = 1120, 440
    frags = []

    frags.append(text(W / 2, 40, "Заступник стоїть на місці справжнього об'єкта",
                      size=17, bold=True, color=INK))
    frags.append(text(W / 2, 62, "клієнт працює через інтерфейс і не бачить, хто за ним",
                      size=12.5, color=MUTED))

    cy = 240

    # ── Клієнт ліворуч ──
    cli_cx = 150
    cli, cw, ch = textbox(cli_cx, cy,
                          ["Клієнт", "тримає тип «Image»", "викликає draw()"],
                          size=12.5, bold=True, fill="#eaf0fd", stroke=NEG,
                          sw=1.7, min_w=210)
    frags.append(cli)

    # ── Проксі посередині ──
    px_cx = 500
    px, pw, ph = textbox(px_cx, cy,
                         ["ImageProxy", "той самий інтерфейс", "тримає лише шлях"],
                         size=12.5, bold=True, fill="#e8f6ee", stroke=FIELD,
                         sw=1.9, min_w=240)
    frags.append(px)

    # стрілка клієнт → проксі (суцільна: завжди йде сюди)
    frags.append(arrow(cli_cx + cw / 2, cy, px_cx - pw / 2 - 2, cy,
                       color=NEG, sw=2.0))
    frags.append(text((cli_cx + cw / 2 + px_cx - pw / 2) / 2, cy - 16,
                      "draw()", size=12, color=NEG))

    # ── Справжній об'єкт праворуч ──
    real_cx = 900
    real, rw, rh = textbox(real_cx, cy,
                           ["RealImage", "читає ВЕСЬ файл", "важкий у пам'яті"],
                           size=12.5, bold=True, fill=FILL, stroke=LINE,
                           sw=1.7, min_w=230)
    frags.append(real)

    # пунктирна стрілка проксі → справжній (створюється аж на перший виклик)
    frags.append(arrow(px_cx + pw / 2 + 2, cy, real_cx - rw / 2 - 2, cy,
                       color=FIELD, sw=1.9))
    midx = (px_cx + pw / 2 + real_cx - rw / 2) / 2
    frags.append(text(midx, cy - 26, "створюється", size=12, color=FIELD))
    frags.append(text(midx, cy - 10, "аж на перший виклик", size=12, bold=True, color=FIELD))

    # підпис під справжнім об'єктом: до першого дотику тут порожньо
    frags.append(text(real_cx, cy + rh / 2 + 30,
                      "до першого дотику — порожньо", size=12, color=MUTED))

    # роздільна дужка «те, що клієнт бачить»
    frags.append(line(cli_cx - cw / 2, H - 46, px_cx + pw / 2, H - 46,
                      color=NEG, sw=1.4))
    frags.append(text((cli_cx - cw / 2 + px_cx + pw / 2) / 2, H - 26,
                      "це все, що бачить клієнт", size=12, bold=True, color=NEG))

    render(os.path.join(IMG, 'proxy-structure.svg'), W, H, *frags)


# ── Чотири різновиди проксі: одна форма, різна робота довкола виклику ─────────
def fig_proxy_kinds():
    W, H = 1240, 560
    frags = []

    frags.append(text(W / 2, 38, "Одна форма — чотири мети",
                      size=17, bold=True, color=INK))
    frags.append(text(W / 2, 60,
                      "заступник із тим самим інтерфейсом; різнить лише робота довкола делегування",
                      size=12, color=MUTED))

    col_cx = [W * 0.135, W * 0.375, W * 0.625, W * 0.865]
    titles = [
        ("Віртуальний", FIELD),
        ("Захисний", POS),
        ("Віддалений", NEG),
        ("Розумне посилання", INK),
    ]
    jobs = [
        "створюю аж на\nперший виклик",
        "спершу перевіряю\nправа доступу",
        "пакую й шлю\nмережею, чекаю",
        "рахую виклики,\nкешую, пишу лог",
    ]
    gains = [
        "не платимо за\nневикористане",
        "об'єкт лишається\nбез охорони в собі",
        "виклик виглядає\nяк місцевий",
        "облік винесено\nз об'єкта",
    ]

    # роздільники між колонками
    for x in (W / 4, W / 2, 3 * W / 4):
        frags.append(line(x, 82, x, H - 60, color="#d0d5db", sw=1.0, dash="6,6"))

    for cx, (t, c), job, gain in zip(col_cx, titles, jobs, gains):
        # заголовок
        frags.append(text(cx, 108, t, size=14.5, bold=True, color=c))

        # клієнт
        cli, cw, chh = textbox(cx, 158, "клієнт", size=11.5, fill="#eef2f7",
                               stroke=MUTED, sw=1.3, min_w=150)
        frags.append(cli)

        # стрілка вниз до проксі з підписом-роботою збоку
        frags.append(arrow(cx, 158 + chh / 2, cx, 232, color=c, sw=1.6))

        # проксі з роботою всередині
        px, pw, phh = textbox(cx, 268, ["проксі"] + job.split("\n"),
                              size=11.5, bold=True, fill=FILL, stroke=c,
                              sw=1.7, min_w=176)
        frags.append(px)

        # стрілка вниз до справжнього об'єкта
        frags.append(arrow(cx, 268 + phh / 2, cx, 372, color=c, sw=1.5))

        # справжній об'єкт (для віддаленого — за пунктирною межею машини)
        if t == "Віддалений":
            # рамка «інша машина» навколо справжнього об'єкта
            frags.append(rect(cx - 92, 388, 184, 66, fill="#eef2fb",
                              stroke=NEG, sw=1.2, rx=8))
            frags.append(text(cx, 404, "інша машина", size=10.5, italic=True, color=NEG))
            obj, _, _ = textbox(cx, 432, "об'єкт", size=11.5, bold=True,
                                fill=BG, stroke=NEG, sw=1.3, min_w=150)
            frags.append(obj)
        else:
            obj, _, _ = textbox(cx, 408, "об'єкт", size=11.5, bold=True,
                                fill="#eef2f7", stroke=MUTED, sw=1.3, min_w=150)
            frags.append(obj)

        # виграш унизу
        frags.append(mtext(cx, 490, gain.split("\n"), size=11, color=c, lh=1.35))

    render(os.path.join(IMG, 'proxy-kinds.svg'), W, H, *frags)


# ── Ланцюжок заступників: охорона → облік → база, з ранніми обривами ──────────
def fig_access_proxy_chain():
    W, H = 1180, 560
    frags = []

    frags.append(text(W / 2, 40, "Заступники складаються в конвеєр",
                      size=17, bold=True, color=INK))
    frags.append(text(W / 2, 62,
                      "виклик іде ззовні всередину й може обірватися на будь-якому шарі",
                      size=12, color=MUTED))

    cy = 250   # спільна вісь коробок

    # ── Клієнт ліворуч ──
    cli_cx = 130
    cli, cw, ch = textbox(cli_cx, cy,
                          ["Клієнт", "тип «OrderService»"],
                          size=12.5, bold=True, fill="#eef2f7", stroke=MUTED,
                          sw=1.5, min_w=200)
    frags.append(cli)

    # ── Три заступники в ряд ──
    guard_cx = 430
    guard, gw, gh = textbox(guard_cx, cy,
                            ["Захисний", "право?"],
                            size=12.5, bold=True, fill="#fdecea", stroke=POS,
                            sw=1.9, min_w=210)

    smart_cx = 720
    smart, sw_, sh = textbox(smart_cx, cy,
                             ["Розумне посилання", "кеш + лог"],
                             size=12.5, bold=True, fill="#e8f6ee", stroke=FIELD,
                             sw=1.9, min_w=240)

    real_cx = 1010
    real, rw, rh = textbox(real_cx, cy,
                           ["RealOrderService", "база"],
                           size=12.5, bold=True, fill=FILL, stroke=LINE,
                           sw=1.7, min_w=220)

    # наскрізна стрілка клієнт → захисний
    frags.append(arrow(cli_cx + cw / 2, cy, guard_cx - gw / 2 - 2, cy, color=INK, sw=2.0))
    frags.append(text((cli_cx + cw / 2 + guard_cx - gw / 2) / 2, cy - 14,
                      "getOrder", size=12, color=INK))
    # захисний → розумне посилання
    frags.append(arrow(guard_cx + gw / 2, cy, smart_cx - sw_ / 2 - 2, cy, color=INK, sw=2.0))
    frags.append(text((guard_cx + gw / 2 + smart_cx - sw_ / 2) / 2, cy - 14,
                      "право є", size=11.5, color=POS))
    # розумне посилання → база
    frags.append(arrow(smart_cx + sw_ / 2, cy, real_cx - rw / 2 - 2, cy, color=INK, sw=2.0))
    frags.append(text((smart_cx + sw_ / 2 + real_cx - rw / 2) / 2, cy - 14,
                      "промах", size=11.5, color=FIELD))

    # коробки поверх стрілок
    frags += [guard, smart, real]

    # ── Ранній обрив 1: немає права → відмова (червона дуга вгору, назад до клієнта) ──
    top_y = 150
    frags.append(line(guard_cx, cy - gh / 2, guard_cx, top_y, color=POS, sw=1.8))
    frags.append(arrow(guard_cx, top_y, cli_cx, top_y, color=POS, sw=1.8))
    frags.append(line(cli_cx, top_y, cli_cx, cy - ch / 2, color=POS, sw=1.8))
    frags.append(text((cli_cx + guard_cx) / 2, top_y - 12,
                      "немає права → відмова", size=12, bold=True, color=POS))

    # ── Ранній обрив 2: влучення в кеш → відповідь (зелена дуга вниз, назад до клієнта) ──
    bot_y = 402
    frags.append(line(smart_cx, cy + sh / 2, smart_cx, bot_y, color=FIELD, sw=1.8))
    frags.append(arrow(smart_cx, bot_y, cli_cx, bot_y, color=FIELD, sw=1.8))
    frags.append(line(cli_cx, bot_y, cli_cx, cy + ch / 2, color=FIELD, sw=1.8))
    frags.append(text((cli_cx + smart_cx) / 2, bot_y + 22,
                      "влучення в кеш → відповідь, база не чіпається", size=12, bold=True, color=FIELD))

    # підпис-висновок унизу
    frags.append(text(W / 2, H - 30,
                      "кожен шар вирішує сам: пустити виклик глибше чи обірвати тут",
                      size=12.5, bold=True, color=INK))

    render(os.path.join(IMG, 'access-proxy-chain.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_proxy_structure()
    fig_proxy_kinds()
    fig_access_proxy_chain()
    print("figs done")

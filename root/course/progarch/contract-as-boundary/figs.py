# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_membrane():
    """Обидві сторони торкаються лише контракту; де концентрується ціна зміни."""
    W, H = 980, 420
    f = []

    # ── контракт — вертикальна лінія-мембрана по центру ──────────────
    cx = 490
    f.append(text(cx, 92, "КОНТРАКТ", size=16, bold=True, color=FIELD))
    f.append(text(cx, 112, "межі", size=12.5, color=MUTED))
    f.append(line(cx, 128, cx, 300, color=FIELD, sw=3.4))

    # ── споживач (ліворуч) ───────────────────────────────────────────
    f.append(rect(95, 158, 230, 104, fill="#fbfcfd", stroke=INK, sw=2))
    f.append(text(210, 200, "споживач", size=15, bold=True))
    f.append(text(210, 224, "(хаб)", size=12.5, color=MUTED))

    # ── постачальник (праворуч) ──────────────────────────────────────
    f.append(rect(655, 158, 230, 104, fill="#fbfcfd", stroke=INK, sw=2))
    f.append(text(770, 200, "постачальник", size=15, bold=True))
    f.append(text(770, 224, "(драйвер)", size=12.5, color=MUTED))

    # ── виклик крізь межу: дві стрілки, що не торкаються лінії ────────
    f.append(text(407, 150, "виклик →", size=12.5, color=MUTED, anchor="middle"))
    f.append(arrow(328, 172, 474, 172))
    f.append(arrow(506, 172, 653, 172))

    # ── підпис: зміна за контрактом (дешево) — під постачальником ─────
    f.append(mtext(770, 300, ["міняєш нутро — контракт цілий",
                              "→ дешево, сусід не помітив"],
                   size=13, color=FIELD, lh=1.35))

    # ── підпис: зміна самого контракту (дорого) — унизу по центру ─────
    f.append(mtext(cx, 340, ["міняєш САМ контракт →",
                             "б'є по всіх, хто на межу спирався"],
                   size=13, color=POS, lh=1.35))

    render(os.path.join(OUT, 'contract-membrane.svg'), W, H, *f,
           title="Контракт як межа: ціна зміни концентрується на самій лінії")


def fig_two_contracts():
    """Оголошений контракт усередині спостережної поведінки; кільце — Гайрам."""
    W, H = 980, 430
    f = []

    # ── зовнішня рамка: усе спостережне ──────────────────────────────
    ox, oy, ow, oh = 150, 100, 560, 250
    f.append(rect(ox, oy, ow, oh, fill="#f4f6f8", stroke=MUTED, sw=1.8))
    f.append(text(ox + ow / 2, oy + 30, "спостережна поведінка — усе, що видно ззовні",
                  size=13, color=MUTED))

    # ── внутрішня рамка: оголошений контракт ─────────────────────────
    ix, iy, iw, ih = ox + 160, oy + 72, 240, 104
    f.append(fitbox(ix, iy, iw, ih, "оголошений\nконтракт", size=15, bold=True,
                    fill="#eafaf1", stroke=FIELD, sw=2.4, color=FIELD))

    # ── кільце між ними: випадковий контракт ─────────────────────────
    f.append(text(ox + ow / 2, oy + oh - 26,
                  "різниця = випадковий контракт, на який уже спираються (Гайрам)",
                  size=13, color=POS))

    # ── підказка-мета праворуч унизу ─────────────────────────────────
    f.append(text(W / 2, oy + oh + 40,
                  "мета дисципліни — стиснути кільце: обіцяти явно, ховати решту",
                  size=12.5, color=MUTED, italic=True))

    render(os.path.join(OUT, 'two-contracts.svg'), W, H, *f,
           title="Два контракти межі: оголошений і справжній")


def fig_robustness_loop():
    """Порочне коло ласкавого приймача: той самий механізм, що й Гайрам, лише з боку приймача."""
    W, H = 1000, 445
    f = []

    tl_c = (258, 158)
    tr_c = (742, 158)
    br_c = (742, 352)
    bl_c = (258, 352)

    tl, wtl, htl = textbox(tl_c[0], tl_c[1], "Приймач ласкаво\nковтає криве", size=14)
    tr, wtr, htr = textbox(tr_c[0], tr_c[1], "Відправник бачить:\nкриве проходить", size=14)
    br, wbr, hbr = textbox(br_c[0], br_c[1], "Недбалих відправників\nстає більше", size=14)
    bl, wbl, hbl = textbox(bl_c[0], bl_c[1], "Криве = справжній контракт,\nзвузити вже не можна",
                           size=14, stroke=POS, color=POS, fill="#fdecea")

    gap = 9
    # стрілки по периметру за годинниковою — до КРАЇВ рамок, не в текст
    f.append(arrow(tl_c[0] + wtl / 2 + gap, tl_c[1], tr_c[0] - wtr / 2 - gap, tr_c[1]))   # TL→TR
    f.append(arrow(tr_c[0], tr_c[1] + htr / 2 + gap, br_c[0], br_c[1] - hbr / 2 - gap))   # TR→BR
    f.append(arrow(br_c[0] - wbr / 2 - gap, br_c[1], bl_c[0] + wbl / 2 + gap, bl_c[1]))   # BR→BL
    f.append(arrow(bl_c[0], bl_c[1] - hbl / 2 - gap, tl_c[0], tl_c[1] + htl / 2 + gap))   # BL→TL

    f += [tl, tr, br, bl]

    f.append(mtext(500, 238, ["кожен оберт —", "ширший справжній контракт;",
                              "RFC 9413: «патологічний цикл»"],
                   size=13, color=MUTED, lh=1.4))

    render(os.path.join(OUT, 'robustness-loop.svg'), W, H, *f,
           title="Порочне коло ласкавого приймача")


def fig_contract_sheet():
    """Артефакт-контракт як спільна сторінка: синтаксис угорі, виписані інваріанти
    нижче; постачальник грає чесно, споживач спирається лише на це."""
    W, H = 1000, 470
    f = []

    # ── центральний «аркуш» — сам артефакт контракту ─────────────────
    sx, sy, sw, sh = 340, 60, 320, 350
    f.append(rect(sx, sy, sw, sh, fill="#fbfcfd", stroke=FIELD, sw=2.6))
    f.append(text(500, 86, "КОНТРАКТ межі", size=15, bold=True, color=FIELD))
    f.append(text(500, 104, "(робочий артефакт — один файл)", size=10.5, color=MUTED))

    # ── смуга СИНТАКСИСУ: типи й підписи ─────────────────────────────
    f.append(rect(360, 118, 280, 70, fill=BG, stroke=MUTED, sw=1.4))
    f.append(text(500, 136, "СИНТАКСИС — типи й підписи", size=10.5, color=MUTED))
    f.append(text(376, 159, "read() → Reading", size=12.5, color=INK, anchor="start"))
    f.append(text(376, 179, "setTarget(t) → Ack", size=12.5, color=INK, anchor="start"))

    # ── СЕМАНТИКА: виписані інваріанти ───────────────────────────────
    f.append(text(500, 210, "СЕМАНТИКА — виписані інваріанти", size=10.5, color=MUTED))
    inv = [
        "одиниці — °C",
        "діапазон — [−40, 85]",
        "крізь межу — без винятку",
        "команда — ідемпотентна",
        "read — не частіше 1/с",
        "at — свій вимір (мс / с)",
    ]
    y = 234
    for s in inv:
        f.append(text(368, y, "•", size=13, color=FIELD, anchor="start"))
        f.append(text(384, y, s, size=12.5, color=INK, anchor="start"))
        y += 29

    # ── постачальник (ліворуч) ───────────────────────────────────────
    f.append(rect(48, 176, 250, 128, fill=FILL, stroke=INK, sw=2))
    f.append(text(173, 212, "Постачальник", size=15, bold=True))
    f.append(text(173, 234, "(фальшивий драйвер)", size=11.5, color=MUTED))
    f.append(mtext(173, 264, ["грає ЧЕСНО —", "тримається в межах обіцяного"],
                   size=11.5, color=FIELD, lh=1.3))

    # ── споживач (праворуч) ──────────────────────────────────────────
    f.append(rect(702, 176, 250, 128, fill=FILL, stroke=INK, sw=2))
    f.append(text(827, 212, "Споживач", size=15, bold=True))
    f.append(text(827, 234, "(хаб)", size=11.5, color=MUTED))
    f.append(mtext(827, 264, ["спирається ЛИШЕ", "на ці обіцянки"],
                   size=11.5, color=FIELD, lh=1.3))

    # ── обидва тягнуться до аркуша, не одне до одного ─────────────────
    f.append(arrow(300, 240, 337, 240))
    f.append(arrow(700, 240, 663, 240))

    # ── теза внизу ───────────────────────────────────────────────────
    f.append(text(500, 448, "обидві сторони спираються на контракт, а не одна на одну",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, 'contract-sheet.svg'), W, H, *f,
           title="Контракт-артефакт: один аркуш, дві сторони")


if __name__ == '__main__':
    fig_membrane()
    fig_two_contracts()
    fig_robustness_loop()
    fig_contract_sheet()
    print("figures written to", OUT)

# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_blank_to_fabric():
    """Порожній кристал при старті → бітстрім заливає комірки конфігурації → схема."""
    W, H = 720, 380
    frags = []
    frags.append(text(W / 2, 28, "Що робить конфігурація: з порожнього кристала — схема", size=17, bold=True))

    # ЛІВОРУЧ: порожня SRAM-сітка при вмиканні
    lx, ly = 40, 80
    frags.append(fitbox(lx, ly - 26, 190, 22, "Одразу після ввімкнення", size=12, bold=True,
                        fill="#fdecea", stroke=POS))
    for r in range(5):
        for c in range(5):
            x = lx + 6 + c * 36
            y = ly + 6 + r * 36
            frags.append(rect(x, y, 26, 26, fill="#ffffff", stroke=MUTED, sw=1))
            frags.append(text(x + 13, y + 18, "?", size=13, color=MUTED))
    frags.append(text(lx + 95, ly + 208, "комірки порожні — 0/1 невизначені", size=11, color=POS))
    frags.append(text(lx + 95, ly + 226, "чип не робить нічого осмисленого", size=11, color=MUTED))

    # СТРІЛКА з бітстрімом
    ax = 250
    frags.append(text(W / 2, 120, "бітстрім", size=13, bold=True, color=NEG))
    frags.append(text(W / 2, 138, "1011 0100 …", size=12, color=NEG))
    frags.append(arrow(ax, 150, ax + 175, 150, color=NEG, sw=2.4))
    frags.append(text(W / 2, 170, "один біт → одна комірка", size=11, color=MUTED))

    # ПРАВОРУЧ: заповнена сітка = конкретна схема
    rx, ry = 470, 80
    frags.append(fitbox(rx, ry - 26, 210, 22, "Після заливки бітстріму", size=12, bold=True,
                        fill="#e9f7ef", stroke=FIELD))
    import random
    random.seed(7)
    for r in range(5):
        for c in range(5):
            x = rx + 6 + c * 36
            y = ry + 6 + r * 36
            on = random.random() < 0.5
            frags.append(rect(x, y, 26, 26, fill=("#dff3e6" if on else "#eef2ff"),
                              stroke=FIELD, sw=1))
            frags.append(text(x + 13, y + 18, ("1" if on else "0"), size=12,
                              color=(FIELD if on else NEG)))
    frags.append(text(rx + 100, ry + 208, "кожен LUT і перемикач заданий", size=11, color=FIELD))
    frags.append(text(rx + 100, ry + 226, "сітка стала потрібною схемою", size=11, color=MUTED))
    render(os.path.join(IMG, 'blank-to-fabric.svg'), W, H, *frags)


def fig_where_lives():
    """Три способи, звідки береться конфігурація при старті."""
    W, H = 740, 400
    frags = []
    frags.append(text(W / 2, 28, "Де живе конфігурація між вимкненнями — три підходи", size=17, bold=True))

    cols = [
        (30, "#e9f7ef", FIELD, "Зовнішня SPI-флеш",
         ["SRAM у чипі — летка,",
          "втрачається без живлення.",
          "Поряд стоїть флеш;",
          "чип САМ читає з неї",
          "бітстрім при кожному старті.",
          "",
          "Найпоширеніше:",
          "гнучко, перешив флеш —",
          "змінив дизайн."]),
        (270, "#eef2ff", NEG, "Внутрішня NV-пам'ять",
         ["Той самий кристал несе",
          "власну незалежну пам'ять",
          "(NVCM / флеш-комірки).",
          "Конфіг лежить УСЕРЕДИНІ,",
          "стартує миттєво,",
          "зайвої мікросхеми нема.",
          "",
          "Компактно й захищено;",
          "перешивів — обмежено."]),
        (510, "#fdecea", POS, "Антизапобіжник (OTP)",
         ["Конфіг «пропалюють» у зв'язки",
          "раз і назавжди — фізично.",
          "Нелетка, жива при старті,",
          "стійка до радіації,",
          "але переписати НЕ можна.",
          "",
          "Космос, оборона:",
          "надійність понад",
          "гнучкість."]),
    ]
    for x, fill, stroke, title, lines in cols:
        frags.append(fitbox(x, 60, 200, 34, title, size=13, bold=True, fill=fill, stroke=stroke))
        y = 116
        for ln in lines:
            if ln:
                frags.append(text(x + 8, y, ln, size=11, color=INK, anchor="start"))
            y += 21

    frags.append(fitbox(120, 350, 500, 40,
                        "Летка SRAM — панівний вибір: її ЩОРАЗУ наповнюють ззовні.\n"
                        "Нелетку тримають там, де важать миттєвий старт, захист чи радіація.",
                        size=12, fill=FILL, stroke=LINE))
    render(os.path.join(IMG, 'where-lives.svg'), W, H, *frags)


def fig_two_paths():
    """Два шляхи доставки бітстріму: JTAG (розробка) і флеш (виробництво); master/slave."""
    W, H = 740, 420
    frags = []
    frags.append(text(W / 2, 28, "Два шляхи бітстріму в чип і хто дає такт", size=17, bold=True))

    # чип по центру-низу
    cx, cy = 300, 250
    frags.append(rect(cx, cy, 150, 96, fill="#f4f6f8", stroke=INK, sw=2))
    frags.append(text(cx + 75, cy + 36, "FPGA", size=16, bold=True))
    frags.append(text(cx + 75, cy + 60, "(летка SRAM", size=11, color=MUTED))
    frags.append(text(cx + 75, cy + 76, "конфігурації)", size=11, color=MUTED))

    # ШЛЯХ 1: JTAG зверху — розробка
    frags.append(fitbox(70, 70, 240, 74,
                        "JTAG — під час розробки\n"
                        "з ПК через програматор\n"
                        "ПРЯМО в SRAM, повз флеш\n"
                        "миттєво бачиш зміну",
                        size=12, bold=True, fill="#e9f7ef", stroke=FIELD))
    frags.append(arrow(190, 146, cx + 40, cy - 2, color=FIELD, sw=2.2))
    frags.append(text(150, 200, "щойно зібрав →", size=11, color=FIELD))
    frags.append(text(150, 216, "залив і глянув", size=11, color=FIELD))

    # ШЛЯХ 2: флеш праворуч — виробництво, автозавантаження
    frags.append(fitbox(500, 150, 210, 96,
                        "Флеш поряд — у виробі\n"
                        "чип САМ читає при старті\n"
                        "(master: чип дає такт)\n"
                        "або зовнішній контролер\n"
                        "заливає (slave: такт ззовні)",
                        size=11, bold=True, fill="#eef2ff", stroke=NEG))
    frags.append(arrow(500, 210, cx + 152, cy + 40, color=NEG, sw=2.2))
    frags.append(text(468, 290, "автозавантаження", size=11, color=NEG, anchor="end"))
    frags.append(text(468, 306, "при кожному ввімкненні", size=11, color=NEG, anchor="end"))

    frags.append(fitbox(150, 366, 440, 40,
                        "Master чи slave — це ХТО веде такт конфігурації:\n"
                        "сам чип зі свого генератора чи зовнішній контролер.",
                        size=12, fill=FILL, stroke=LINE))
    render(os.path.join(IMG, 'two-paths.svg'), W, H, *frags)


def fig_bitbang_wave():
    """Такт slave-serial: DIN виставили ЗАЗДАЛЕГІДЬ, чип бере його на висхідному DCLK."""
    W, H = 720, 330
    frags = []
    frags.append(text(W / 2, 26, "Один такт slave-serial: коли виставляти біт і коли цокати", size=16, bold=True))

    x0 = 90            # ліва межа хвиль
    span = 560         # ширина області хвиль
    bits = "10110"     # 5 показових бітів
    n = len(bits)
    step = span / n
    # рівні для DCLK
    ck_hi, ck_lo = 92, 128
    # рівні для DIN
    dn_hi, dn_lo = 190, 226

    frags.append(text(x0 - 12, ck_lo - 6, "DCLK", size=12, bold=True, anchor="end", color=NEG))
    frags.append(text(x0 - 12, dn_lo - 6, "DIN", size=12, bold=True, anchor="end", color=POS))

    # DCLK: у кожній клітинці — низько (перша половина), високо (друга)
    px, py = x0, ck_lo
    ck_pts = [(x0, ck_lo)]
    for i in range(n):
        cx = x0 + i * step
        ck_pts.append((cx + step * 0.5, ck_lo))   # тримаємо низько
        ck_pts.append((cx + step * 0.5, ck_hi))   # ↑ висхідний фронт — тут беруть біт
        ck_pts.append((cx + step, ck_hi))
        ck_pts.append((cx + step, ck_lo))          # ↓ спадний — тут міняємо DIN
    d = "M " + " L ".join("%.1f %.1f" % p for p in ck_pts)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d, NEG))

    # DIN: значення тримається всю клітинку; змінюється на межі клітинки (спадний DCLK)
    dn_pts = []
    for i, b in enumerate(bits):
        y = dn_hi if b == "1" else dn_lo
        cx = x0 + i * step
        dn_pts.append((cx, y))
        dn_pts.append((cx + step, y))
    # вертикальні переходи додаються самим ламаним шляхом
    path = "M %.1f %.1f" % dn_pts[0]
    prev_y = dn_pts[0][1]
    for (xx, yy) in dn_pts[1:]:
        if yy != prev_y:
            path += " L %.1f %.1f" % (xx, prev_y)
        path += " L %.1f %.1f" % (xx, yy)
        prev_y = yy
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (path, POS))

    # пунктир на КОЖНОМУ висхідному фронті DCLK — саме там чип бере біт;
    # підпис значення — під центром своєї клітинки
    for i, b in enumerate(bits):
        cx = x0 + i * step
        edge = cx + step * 0.5      # висхідний фронт DCLK усередині клітинки
        frags.append(line(edge, ck_hi - 4, edge, dn_lo + 16, color=MUTED, sw=1, dash="3,3"))
        frags.append(text(edge, dn_lo + 32, b, size=13, bold=True,
                          color=(POS if b == "1" else NEG)))
    frags.append(text(x0 + span, 62, "↑ висхідний фронт DCLK — чип клацає біт",
                      size=11, color=NEG, anchor="end"))

    frags.append(text(W / 2, dn_lo + 56, "DIN виставили РАНІШЕ й тримаємо — на висхідному DCLK чип бере його; "
                                          "міняємо DIN на спадному", size=11, color=MUTED))
    b, bw, bh = textbox(W / 2, 308, "Порядок бітів у байті — старший біт (MSB) першим", size=12,
                        fill=FILL, stroke=LINE)
    frags.append(b)
    render(os.path.join(IMG, 'bitbang-wave.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_blank_to_fabric()
    fig_where_lives()
    fig_two_paths()
    fig_bitbang_wave()
    print("figs written to", IMG)

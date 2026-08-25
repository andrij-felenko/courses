# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_lines():
    """Карта родини Power HD: одне дерево «серва + мотори» розгалужується на
    лінійки за призначенням. Показуємо, ЯК влаштований модельний ряд, щоб
    читач міг покласти будь-яку модель на своє місце. Кожна гілка — окрема
    колонка з прикладом моделі; жоден напис не лягає на чужі лінії."""
    W, H = 940, 560
    frags = []
    frags.append(text(W / 2, 34, "Родина Power HD: гілки модельного ряду за призначенням", size=17, bold=True))

    # корінь
    root_x, root_y, root_w, root_h = W / 2 - 150, 60, 300, 46
    frags.append(rect(root_x, root_y, root_w, root_h, fill="#eef2ff", stroke=NEG, sw=1.8))
    frags.append(text(W / 2, root_y + 20, "HuiDa RC International", size=13, bold=True, color=NEG))
    frags.append(text(W / 2, root_y + 37, "бренд Power HD — серва, мотори, ESC", size=10.5, color=INK))

    # дві великі гілки — СЕРВА (керування кутом) і ТЯГА (мотори+ESC)
    join_y = 128
    frags.append(line(W / 2, root_y + root_h, W / 2, join_y, color=MUTED, sw=1.6))

    servo_x = 245
    drive_x = 760
    frags.append(line(servo_x, join_y, drive_x, join_y, color=MUTED, sw=1.6))
    frags.append(line(servo_x, join_y, servo_x, join_y + 22, color=MUTED, sw=1.6))
    frags.append(line(drive_x, join_y, drive_x, join_y + 22, color=MUTED, sw=1.6))

    # заголовок гілки СЕРВА
    frags.append(text(servo_x, join_y + 40, "СЕРВА — тримають кут", size=13, bold=True, color=FIELD))
    frags.append(text(servo_x, join_y + 57, "той самий 3-дротовий PWM для всіх", size=10, color=MUTED))

    # чотири колонки серв
    col_y = join_y + 78
    col_h = 118
    cols = [
        (70, "#eafaf1", FIELD, "ANALOG (HD-…A)", ["проста плата,", "мертва зона ширша", "дешеві, легкі", "HD-1370A, 1900A"]),
        (240, "#fff7ed", "#d9822b", "DIGITAL (…MG)", ["мікро-контролер,", "тримає жорсткіше,", "п'є більше струму", "HD-1501MG"]),
        (410, "#fdecea", POS, "HV / водозахист", ["живлення 7.4–8.4 В,", "більше сили;", "LW — герметичні", "LF-20MG, LW-30MG"]),
        (580, "#f0f5ff", NEG, "ROBOT (AR-…)", ["безперервний оберт", "або кут; підшипники", "під роботів", "AR-3606HB"]),
    ]
    for (cx0, fill, col, head, rows) in cols:
        cx = cx0 + 65
        b = rect(cx0, col_y, 150, col_h, fill=fill, stroke=col, sw=1.5)
        frags.append(b)
        frags.append(text(cx, col_y + 20, head, size=11.5, bold=True, color=col))
        for i, r in enumerate(rows):
            last = (i == len(rows) - 1)
            frags.append(text(cx, col_y + 40 + i * 18, r, size=9.5,
                              color=(MUTED if last else INK), italic=last))
    # з'єднати заголовок гілки серв із рядком колонок
    frags.append(line(servo_x, col_y - 14, servo_x, col_y, color=MUTED, sw=1.4))
    frags.append(line(145, col_y - 14, 655, col_y - 14, color=MUTED, sw=1.4))
    for cx0 in (70, 240, 410, 580):
        frags.append(line(cx0 + 75, col_y - 14, cx0 + 75, col_y, color=MUTED, sw=1.1))

    # заголовок гілки ТЯГА
    frags.append(text(drive_x, join_y + 40, "ТЯГА — крутять безупинно", size=12.5, bold=True, color=POS))
    frags.append(text(drive_x, join_y + 57, "інша мова керування", size=10, color=MUTED))

    d_y = col_y
    d_cols = [
        (700, "#fdecea", POS, "BRUSHLESS MOTOR", ["безколекторні,", "тяга моделі;", "оберти від ESC"]),
        (830, "#fff7ed", "#d9822b", "ESC (STORM)", ["регулятор оборотів,", "живить мотор,", "слухає той самий", "PWM 1–2 мс"]),
    ]
    for (cx0, fill, col, head, rows) in d_cols:
        cx = cx0 + 55
        frags.append(rect(cx0, d_y, 110, col_h, fill=fill, stroke=col, sw=1.5))
        frags.append(text(cx, d_y + 20, head, size=10, bold=True, color=col))
        for i, r in enumerate(rows):
            frags.append(text(cx, d_y + 40 + i * 17, r, size=9, color=INK))
    frags.append(line(drive_x, d_y - 14, drive_x, d_y, color=MUTED, sw=1.4))
    frags.append(line(755, d_y - 14, 885, d_y - 14, color=MUTED, sw=1.4))
    frags.append(line(755, d_y - 14, 755, d_y, color=MUTED, sw=1.1))
    frags.append(line(885, d_y - 14, 885, d_y, color=MUTED, sw=1.1))

    # спільна нитка внизу
    b, _, _ = textbox(W / 2, 522,
                      ["Спільне для всіх гілок: один виробник, роз'єм JR (Futaba-сумісний),",
                       "протокол RC-імпульсу 1–2 мс. Модель добирають за силою, швидкістю",
                       "й напругою — фізика керування скрізь однакова."],
                      size=11, color=INK, pad=11, fill="#f4f6f8", stroke=LINE)
    frags.append(b)

    render(os.path.join(OUT, 'lines.svg'), W, H, *frags)


def fig_decode():
    """Розшифровка партномера Power HD: як HD-1501MG чи LF-20MG розкладається
    на префікс-лінійку + число (клас моменту) + суфікс матеріалу шестерень і
    напруги. Дає читачеві ключ читати будь-яку назву з полиці. Поля рознесені
    з великим запасом, підписи стоять під своїми сегментами, не налазять."""
    W, H = 900, 470
    frags = []
    frags.append(text(W / 2, 32, "Як читати назву моделі Power HD", size=17, bold=True))

    # приклад 1: HD-1501MG
    def decode(y, parts, note):
        # parts: список (текст, колір, підпис-знизу)
        seg_w = 118
        total = seg_w * len(parts)
        x0 = (W - total) / 2
        for i, (txt, col, sub) in enumerate(parts):
            x = x0 + i * seg_w
            frags.append(rect(x + 6, y, seg_w - 12, 46, fill="#f7f9fc", stroke=col, sw=1.8))
            frags.append(text(x + seg_w / 2, y + 30, txt, size=18, bold=True, color=col))
            # підпис під сегментом
            frags.append(text(x + seg_w / 2, y + 70, sub[0], size=10, bold=True, color=col))
            if len(sub) > 1:
                frags.append(text(x + seg_w / 2, y + 86, sub[1], size=9.5, color=MUTED))
        b, _, _ = textbox(W / 2, y + 122, note, size=10.5, color=INK, pad=8,
                          min_w=total, fill="#eef2ff", stroke=NEG)
        frags.append(b)

    decode(70,
           [("HD-", FIELD, ["лінійка", "HD = аналог"]),
            ("1501", NEG, ["клас моменту", "≈ 17 кг·см"]),
            ("MG", POS, ["шестерні", "MG = метал"])],
           "HD-1501MG — аналогове силове серво з металевим редуктором")

    decode(280,
           [("LF-", FIELD, ["лінійка", "цифрова HV"]),
            ("20", NEG, ["момент", "≈ 20 кг·см"]),
            ("MG", POS, ["шестерні", "метал"])],
           "LF-20MG — цифрове високовольтне 20-кілограмове серво (метал)")

    render(os.path.join(OUT, 'decode.svg'), W, H, *frags)


def fig_torque_geo():
    """Геометрія моменту на розі серва: сила F тисне на тягу на плечі r від осі
    вала; момент = F · r. Показуємо, ЧОМУ довше плече = більший потрібний момент
    при тій самій силі, і що момент рахують на РОБОЧОМУ плечі, а не на будь-якому.
    Написи стоять з великим запасом збоку від осі, лінія тяги не перетинає їх."""
    W, H = 900, 460
    frags = []
    frags.append(text(W / 2, 32, "Момент на розі серва: сила на плечі", size=17, bold=True))

    # вісь вала серва
    ax, ay = 250, 300          # центр вихідного вала
    frags.append(circle(ax, ay, 13, fill="#eef2ff", stroke=NEG, sw=2))
    frags.append(circle(ax, ay, 3.2, fill=NEG, stroke=NEG, sw=1))
    frags.append(text(ax, ay + 42, "вісь вала серва", size=11, bold=True, color=NEG))
    frags.append(text(ax, ay + 59, "(центр обертання)", size=9.5, color=MUTED))

    # ріг / качалка — горизонтальне плече вправо
    horn_len = 360
    hx = ax + horn_len
    frags.append(line(ax, ay, hx, ay, color=INK, sw=6))          # тіло рога
    frags.append(circle(hx, ay, 6, fill=FILL, stroke=INK, sw=1.6))  # отвір тяги

    # плече r — розмірна лінія НАД рогом (щоб не лягти на тіло рога)
    dim_y = ay - 40
    frags.append(line(ax, ay - 14, ax, dim_y - 6, color=MUTED, sw=1))
    frags.append(line(hx, ay - 14, hx, dim_y - 6, color=MUTED, sw=1))
    frags.append(line(ax, dim_y, hx, dim_y, color=MUTED, sw=1.3))
    frags.append(text((ax + hx) / 2, dim_y - 8, "плече r  (від осі до точки тяги)", size=11.5, bold=True, color=FIELD))

    # сила F — стрілка вниз на кінці рога (тяга керма тисне)
    fx = hx
    frags.append(arrow(fx, ay + 8, fx, ay + 78, color=POS, sw=2.6))
    frags.append(text(fx + 6, ay + 55, "F", size=16, bold=True, color=POS, anchor="start"))
    frags.append(text(fx + 20, ay + 74, "сила на тязі", size=10.5, color=POS, anchor="start"))

    # формула — у своїй рамці, праворуч угорі, поза геометрією
    b, _, _ = textbox(700, 150,
                      ["момент  M = F · r",
                       "",
                       "F — сила на тязі (кгс),",
                       "r — робоче плече (см),",
                       "M — момент (кг·см)"],
                      size=12, color=INK, pad=12, fill="#eef2ff", stroke=NEG)
    frags.append(b)

    # висновок унизу
    b2, _, _ = textbox(W / 2, 418,
                       ["Та сама сила на вдвічі довшому плечі вимагає вдвічі більшого моменту.",
                        "Рахуй момент на РОБОЧОМУ плечі своєї тяги — не на паспортному прикладі."],
                       size=11, color=INK, pad=10, fill="#f4f6f8", stroke=LINE)
    frags.append(b2)

    render(os.path.join(OUT, 'torque-geo.svg'), W, H, *frags)


def fig_margin():
    """Чому запас ×2: паспортне число — стеля в ідеалі; реально під навантаженням
    і на просілій батареї серво слабше; додай розкид екземпляра — і робочий момент,
    на який МОЖНА покластися, десь удвічі нижчий за паспорт. Стовпчики звужуються
    зліва направо; кожен підписаний під собою з запасом, написи не налазять."""
    W, H = 900, 470
    frags = []
    frags.append(text(W / 2, 32, "Чому запас ×2: паспорт → реальність", size=17, bold=True))

    base_y = 340          # низ стовпчиків
    unit = 12.0           # px на 1 кг·см
    bars = [
        (150, 20.0, POS, "#fdecea", "Паспорт", ["20 кг·см", "ідеал: свіжа", "батарея, коротко"]),
        (360, 15.0, "#d9822b", "#fff7ed", "Реально під", ["~15 кг·см", "навантаженням", "і на просілій 6 В"]),
        (570, 12.0, FIELD, "#eafaf1", "Мінус розкид", ["~12 кг·см", "цей екземпляр", "може бути слабший"]),
        (770, 10.0, NEG, "#eef2ff", "На що клади", ["≈10 кг·см", "паспорт ÷ 2 —", "безпечна опора"]),
    ]
    bw = 120
    for (cx, val, col, fill, head, rows) in bars:
        h = val * unit
        x0 = cx - bw / 2
        frags.append(rect(x0, base_y - h, bw, h, fill=fill, stroke=col, sw=1.8))
        frags.append(text(cx, base_y - h - 10, "%.0f" % val, size=15, bold=True, color=col))
        frags.append(text(cx, base_y + 22, head, size=11.5, bold=True, color=col))
        for i, r in enumerate(rows):
            frags.append(text(cx, base_y + 40 + i * 16, r, size=9.5,
                              color=(INK if i == 0 else MUTED)))

    # базова лінія
    frags.append(line(70, base_y, 840, base_y, color=INK, sw=1.6))
    frags.append(text(78, base_y - 6, "кг·см", size=10, color=MUTED, anchor="start"))

    # дужка «÷2» від паспорта до робочого: горизонталь розірвана навколо напису
    lbl_hw = (text_width("падіння приблизно вдвічі  (÷2)", 11) + 16) / 2
    frags.append(line(150, 70, 460 - lbl_hw - 6, 70, color=MUTED, sw=1.2, dash="4 3"))
    frags.append(line(460 + lbl_hw + 6, 70, 770, 70, color=MUTED, sw=1.2, dash="4 3"))
    frags.append(line(150, 70, 150, base_y - 20.0 * unit - 24, color=MUTED, sw=1.2, dash="4 3"))
    frags.append(line(770, 70, 770, base_y - 10.0 * unit - 24, color=MUTED, sw=1.2, dash="4 3"))
    b, _, _ = textbox(460, 70, "падіння приблизно вдвічі  (÷2)",
                      size=11, color=INK, pad=8, fill="#ffffff", stroke=MUTED)
    frags.append(b)

    b2, _, _ = textbox(W / 2, 440,
                       ["Проєктуй так, щоб ПОТРІБНИЙ момент навантаження вкладався в правий стовпчик,",
                        "а не в паспортний лівий — тоді серво тягне і на межі, а не «попливе» на ній."],
                       size=11, color=INK, pad=10, fill="#f4f6f8", stroke=LINE)
    frags.append(b2)

    render(os.path.join(OUT, 'margin.svg'), W, H, *frags)


def fig_timeline():
    """Історична смуга (для вставки hist-powerhd-brand): на який ринок увійшов
    Power HD. Три епохи RC-серва — каліфорнійські піонери 1960-х, японська
    олігополія зі спільним роз'ємом (1970–1991) і китайський масовий вал 2000-х,
    куди 2005-го стає Power HD. Показуємо, що бренд НЕ винаходив нішу — він зайшов
    у вже готову, зі спільним роз'ємом і протоколом. Підписи по черзі над і під
    віссю з великим відступом, мітки-роки біля осі; ніщо не налазить."""
    W, H = 940, 430
    frags = []
    frags.append(text(W / 2, 32, "На який ринок увійшов Power HD: три епохи RC-серва", size=16, bold=True))

    axis_y = 215
    x_left, x_right = 60, 872
    frags.append(line(x_left, axis_y, x_right, axis_y, color=INK, sw=2.2))
    frags.append(arrow(x_right - 2, axis_y, x_right + 16, axis_y, color=INK, sw=2.2))
    frags.append(text(x_right + 8, axis_y + 22, "час", size=10, color=MUTED, anchor="start"))

    eras = [
        (195, "1960-і", MUTED, True, "Каліфорнійські піонери",
         ["Orbit, Bonner, Kraft —", "перші пропорційні системи;", "дорого, дрібними серіями"]),
        (468, "1970 – 1991", NEG, False, "Японці + спільний роз'єм",
         ["Futaba (у RC з 1962), JR, Sanwa", "перебирають ринок; близько 1991", "роз'єм і протокол — сумісні між брендами"]),
        (752, "2000-і →", POS, True, "Китайський масовий вал",
         ["дешеві «достатньо хороші» серва;", "TowerPro, Hextronic… і Power HD (2005)", "тиснуть дорогі японські на масі"]),
    ]
    for (cx, yr, col, up, head, rows) in eras:
        frags.append(circle(cx, axis_y, 7, fill=col, stroke=col, sw=1.5))
        if up:
            frags.append(text(cx, axis_y + 26, yr, size=11.5, bold=True, color=col))
        else:
            frags.append(text(cx, axis_y - 16, yr, size=11.5, bold=True, color=col))

    def era_box(cx, col, up, head, rows):
        bw = 258
        bh = 20 + 16 * len(rows) + 14
        if up:
            by = axis_y - 46 - bh
            conn0, conn1 = axis_y - 7, by + bh
        else:
            by = axis_y + 46
            conn0, conn1 = axis_y + 7, by
        bx = cx - bw / 2
        frags.append(line(cx, conn0, cx, conn1, color=col, sw=1.2, dash="3 3"))
        frags.append(rect(bx, by, bw, bh, fill="#f7f9fc", stroke=col, sw=1.6))
        frags.append(text(cx, by + 19, head, size=11.5, bold=True, color=col))
        for i, r in enumerate(rows):
            frags.append(text(cx, by + 39 + i * 16, r, size=9.5, color=INK))

    for (cx, yr, col, up, head, rows) in eras:
        era_box(cx, col, up, head, rows)

    b, _, _ = textbox(W / 2, 410,
                      ["Power HD не винайшов нішу — він зайшов у ГОТОВУ: спільний роз'єм JR і протокол 1–2 мс",
                       "уже були мовою сумісності, тож дешеве серво ставало на місце дорогого без переробки."],
                      size=10.5, color=INK, pad=10, fill="#eef2ff", stroke=NEG)
    frags.append(b)

    render(os.path.join(OUT, 'timeline.svg'), W, H, *frags)


if __name__ == "__main__":
    fig_lines()
    fig_decode()
    fig_torque_geo()
    fig_margin()
    fig_timeline()
    print("figs done")

# -*- coding: utf-8 -*-
"""Фігури до теми «Налаштування виконавчих механізмів: геометрія, виходи, перевірка»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def box(cx, cy, s, **kw):
    """textbox + межі рамки, щоб приєднувати стрілки."""
    body, w, h = textbox(cx, cy, s, **kw)
    return body, cx - w / 2.0, cx + w / 2.0, cy - h / 2.0, cy + h / 2.0


# ── 1. Номер функції як єдина скріпа ───────────────────────────────────────
def fig_function_link():
    W, H = 1320, 620
    f = []

    f.append(text(230, 92, "ГЕОМЕТРІЯ", size=15, bold=True))
    f.append(text(230, 116, "де мотор стоїть", size=12, color=MUTED))
    f.append(text(660, 92, "НОМЕР ФУНКЦІЇ", size=15, bold=True))
    f.append(text(660, 116, "спільний словник", size=12, color=MUTED))
    f.append(text(1095, 92, "ВИХОДИ", size=15, bold=True))
    f.append(text(1095, 116, "до якого контакту припаяно", size=12, color=MUTED))

    rows = [
        ("CA_ROTOR0_PX = 0.25\nCA_ROTOR0_PY = 0.25\nCA_ROTOR0_KM = 0.05",
         "101\nMotor 1",
         "PWM_AUX_FUNC3 = 101"),
        ("CA_ROTOR1_PX = −0.25\nCA_ROTOR1_PY = −0.25\nCA_ROTOR1_KM = 0.05",
         "102\nMotor 2",
         "PWM_AUX_FUNC1 = 102"),
        ("CA_SV_CS0_TYPE = 3\n(кермо висоти)",
         "201\nServo 1",
         "PWM_MAIN_FUNC2 = 201"),
        ("—\nгеометрії не потребує",
         "400\nLanding Gear",
         "PWM_MAIN_FUNC6 = 400"),
    ]

    y0, dy = 190, 105
    for i, (left, mid, right) in enumerate(rows):
        y = y0 + i * dy
        b, lx0, lx1, _, _ = box(230, y, left, size=12, min_w=300)
        f.append(b)
        b, mx0, mx1, _, _ = box(660, y, mid, size=13, bold=True, min_w=150,
                                fill="#eaf0fd", stroke=NEG)
        f.append(b)
        b, rx0, rx1, _, _ = box(1095, y, right, size=12, min_w=300)
        f.append(b)
        if i != 3:
            f.append(arrow(lx1 + 12, y, mx0 - 12, y))
        f.append(arrow(rx0 - 12, y, mx1 + 12, y))

    f.append(text(W / 2.0, H - 60,
                  "жодна зі сторін не називає іншу: ліворуч немає номерів контактів,",
                  size=13, color=MUTED))
    f.append(text(W / 2.0, H - 36,
                  "праворуч немає координат — обидві посилаються лише на номер функції",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'function-as-link.svg'), W, H, *f,
           title="Номер функції — єдине, що поєднує геометрію апарата з розпаянням")


# ── 2. Один опис породжує всю сторінку ─────────────────────────────────────
def fig_metadata_to_page():
    W, H = 1280, 700
    f = []

    b, jx0, jx1, jy0, jy1 = box(640, 100, "опис ACTUATORS з борту (JSON)", size=15,
                                bold=True, min_w=460)
    f.append(b)

    b, gx0, gx1, gy0, gy1 = box(640, 200, "show-ui-if", size=14,
                                fill="#fdecea", stroke=POS, min_w=200)
    f.append(b)
    f.append(arrow(640, jy1 + 8, 640, gy0 - 8))
    f.append(text(1010, 205, "умова хибна → сторінки немає,", size=12,
                  color=MUTED, anchor="middle"))
    f.append(text(1010, 227, "станція показує стару вкладку «Мотори»", size=12,
                  color=MUTED, anchor="middle"))
    f.append(line(gx1 + 10, 200, 800, 200, color=MUTED, dash="5,4"))

    keys = [
        (245, "mixer_v1", "типи механізмів,\nваріанти геометрії,\nправила"),
        (640, "outputs_v1", "групи виходів,\nканали,\nномери параметрів"),
        (1035, "functions_v1", "перелік функцій\nі людських підписів"),
    ]
    key_bottom = {}
    for cx, name, sub in keys:
        b, kx0, kx1, ky0, ky1 = box(cx, 330, name + "\n" + sub, size=13, bold=False,
                                    min_w=290)
        f.append(b)
        key_bottom[cx] = ky1
        f.append(arrow(640, gy1 + 8, cx, ky0 - 8))

    outs = [
        (245, "розділ «Геометрія»\n+ малюнок апарата"),
        (640, "таблиця виходів"),
        (1035, "список того,\nщо можна крутити"),
    ]
    for cx, s in outs:
        b, ox0, ox1, oy0, oy1 = box(cx, 500, s, size=13, min_w=290,
                                    fill="#eafaf0", stroke=FIELD)
        f.append(b)
        f.append(arrow(cx, key_bottom[cx] + 8, cx, oy0 - 8))

    # functions_v1 живить і таблицю виходів, і перелік перевірки
    f.append(line(1035, 372, 1035, 430, color=MUTED, dash="4,4"))
    f.append(arrow(890, 430, 700, 470, color=MUTED))
    f.append(line(890, 430, 1035, 430, color=MUTED, dash="4,4"))
    f.append(text(880, 452, "той самий словник", size=12, color=MUTED, anchor="middle"))

    f.append(text(W / 2.0, H - 46,
                  "у коді станції немає ні переліку геометрій, ні переліку функцій:",
                  size=13, color=MUTED))
    f.append(text(W / 2.0, H - 22,
                  "усі три частини сторінки складаються з того, що надіслав апарат",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'metadata-to-page.svg'), W, H, *f,
           title="Три ключі опису — три частини сторінки")


# ── 3. Команда з власним терміном придатності ──────────────────────────────
def fig_test_timeout():
    W, H = 1260, 560
    f = []

    x0, x1 = 150, 1120
    lane_qgc, lane_px4 = 150, 300

    f.append(text(80, lane_qgc + 5, "станція", size=13, bold=True, anchor="start"))
    f.append(text(80, lane_px4 + 5, "борт", size=13, bold=True, anchor="start"))
    f.append(line(x0, lane_qgc, x1, lane_qgc, color=MUTED))
    f.append(line(x0, lane_px4, x1, lane_px4, color=MUTED))

    # повтори команди кожні 100 мс
    sends = [x0 + 90 * i for i in range(6)]
    for i, sx in enumerate(sends):
        f.append(circle(sx, lane_qgc, 7, fill="#eaf0fd", stroke=NEG, sw=2))
        f.append(arrow(sx, lane_qgc + 12, sx, lane_px4 - 12, color=NEG))
    f.append(text((sends[0] + sends[-1]) / 2.0, lane_qgc - 30,
                  "ACTUATOR_TEST кожні 100 мс, доки повзунок утримують",
                  size=13, color=NEG))

    last = sends[-1]
    expire = last + 300
    f.append(rect(x0, lane_px4 + 20, expire - x0, 46, fill="#eafaf0", stroke=FIELD))
    f.append(text((x0 + expire) / 2.0, lane_px4 + 49, "вихід під керуванням перевірки",
                  size=13))

    f.append(line(expire, lane_px4 - 20, expire, lane_px4 + 100, color=POS, sw=2,
                  dash="6,4"))
    f.append(text(expire + 14, lane_px4 + 96, "останній наказ вичерпав свій час",
                  size=12, color=POS, anchor="start"))

    f.append(rect(expire, lane_px4 + 20, x1 - expire, 46, fill="#fdecea", stroke=POS))
    f.append(text((expire + x1) / 2.0, lane_px4 + 49, "вихід повернуто до значення DIS",
                  size=13))

    # обрив зв'язку
    f.append(line(last + 45, 100, last + 45, lane_qgc - 12, color=POS, sw=2))
    f.append(text(last + 45, 88, "тут обірвався зв'язок", size=13, color=POS))

    f.append(text(W / 2.0, 420,
                  "жодної команди «зупинись» не надсилають і не чекають:",
                  size=14))
    f.append(text(W / 2.0, 448,
                  "кожен наказ несе власний термін, тому мовчання каналу означає зупинку,",
                  size=14))
    f.append(text(W / 2.0, 476,
                  "а прошивка ще й обрізає цей термін до трьох секунд згори",
                  size=14))

    render(os.path.join(IMG, 'test-timeout.svg'), W, H, *f,
           title="Перевірка виходу: наказ, що сам себе відпускає")


# ── 4. Перехід від файлів мікшера до розподілу керування (вставка hist) ────
def fig_mixer_timeline():
    W, H = 1380, 520
    f = []

    AX = 280.0          # вісь часу
    X0, X1 = 90.0, 1300.0
    X_PR, X_113, X_114 = 215.0, 585.0, 950.0

    # вісь
    f.append(line(X0, AX, X1, AX, color=INK, sw=2))
    f.append(arrow(X1 - 30, AX, X1, AX, color=INK, sw=2))

    # смуги епох під віссю
    for x, s in ((0.5 * (X0 + X_113), "рама = вибір файла мікшера"),
                 (0.5 * (X_113 + X_114), "два світи: файл або параметри"),
                 (0.5 * (X_114 + X1), "лише параметри")):
        f.append(text(x, AX + 36, s, size=13, color=MUTED, italic=True))

    # межі епох
    for x in (X_113, X_114):
        f.append(line(x, AX + 12, x, AX + 50, color=MUTED, sw=1, dash="4,4"))

    # віхи на осі
    for x in (X_PR, X_113, X_114):
        f.append(line(x, AX - 12, x, AX + 12, color=INK, sw=2))

    # нижня доріжка — PX4
    f.append(text(X0, AX + 95, "PX4", size=15, bold=True, anchor="start"))
    px4 = ((X_PR, "PR #18776 · грудень 2021\nрозподіл керування влито,\nавтор Beat Küng"),
           (X_113, "PX4 v1.13 · 22.11.2022\nSYS_CTRL_ALLOC=1 — опція,\nмікшери ще на місці"),
           (X_114, "PX4 v1.14 · 20.10.2023\nмікшери прибрано,\nіншого способу немає"))
    for x, s in px4:
        body, _, _, ty, _ = box(x, AX + 150, s, size=13)
        f.append(body)
        f.append(line(x, AX + 12, x, ty, color=MUTED, sw=1.2, dash="3,4"))

    # верхня доріжка — станція
    f.append(text(X0, AX - 95, "QGroundControl", size=15, bold=True, anchor="start"))
    body, _, qgx1, _, qgy1 = box(X_PR, AX - 150,
                                 "QGC v4.2.0 · грудень 2021\nсторінка виконавчих\nмеханізмів уже є",
                                 size=13)
    f.append(body)
    f.append(line(X_PR, AX - 12, X_PR, qgy1, color=MUTED, sw=1.2, dash="3,4"))

    # проміжок очікування
    BL, BR = X_PR + 24, X_113 - 6
    f.append(line(BL, AX - 45, BR, AX - 45, color=FIELD, sw=2))
    f.append(line(BL, AX - 53, BL, AX - 37, color=FIELD, sw=2))
    f.append(line(BR, AX - 53, BR, AX - 37, color=FIELD, sw=2))
    f.append(text(0.5 * (BL + BR), AX - 59,
                  "одинадцять місяців сторінка чекала на прошивку",
                  size=13, color=FIELD, bold=True))

    render(os.path.join(IMG, 'mixer-to-allocation.svg'), W, H, *f,
           title="Від файлів мікшера до розподілу керування")


# ── 5. Дві нумерації в одному полі param5 (вставка proj) ───────────────────
def fig_param5_dialects():
    W, H = 1300, 690
    f = []

    b, px0, px1, py0, py1 = box(650, 105, "param5 команди ACTUATOR_TEST",
                                size=15, bold=True, min_w=430)
    f.append(b)

    bl, lx0, lx1, ly0, ly1 = box(340, 245,
                                 "param5 < 1000\nстандартна нумерація MAVLink",
                                 size=13, min_w=400)
    br, rx0, rx1, ry0, ry1 = box(960, 245,
                                 "param5 ≥ 1000\nдіалект PX4",
                                 size=13, min_w=400, fill="#eaf0fd", stroke=NEG)
    f.append(bl)
    f.append(br)
    f.append(arrow(px0 + 60, py1 + 10, 340, ly0 - 10))
    f.append(arrow(px1 - 60, py1 + 10, 960, ry0 - 10))

    b, _, _, my0, my1 = box(340, 390,
                            "1…12 → Motor 1…12\n33…47 → Servo 1…15",
                            size=13, min_w=400)
    f.append(b)
    f.append(arrow(340, ly1 + 10, 340, my0 - 10))

    b, _, _, ey0, _ = box(340, 535, "будь-яке інше число\n→ UNSUPPORTED",
                          size=13, min_w=400, fill="#fdecea", stroke=POS)
    f.append(b)
    f.append(arrow(340, my1 + 10, 340, ey0 - 10))

    b, _, _, ky0, ky1 = box(960, 390, "функція = param5 − 1000",
                            size=13, min_w=400)
    f.append(b)
    f.append(arrow(960, ry1 + 10, 960, ky0 - 10))

    b, _, _, gy0, _ = box(960, 535,
                          "101 Motor · 201 Servo\n400 шасі · 430 захват · 2000 камера",
                          size=13, min_w=400, fill="#eafaf0", stroke=FIELD)
    f.append(b)
    f.append(arrow(960, ky1 + 10, 960, gy0 - 10))

    f.append(text(W / 2.0, H - 60,
                  "клієнт починає з діалекту PX4; почувши UNSUPPORTED, падає на стандартну нумерацію,",
                  size=13, color=MUTED))
    f.append(text(W / 2.0, H - 34,
                  "але нею адресуються лише мотори й серви — шасі, захвата й камери там немає",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'param5-dialects.svg'), W, H, *f,
           title="Одне поле, дві нумерації функцій")


if __name__ == '__main__':
    fig_function_link()
    fig_metadata_to_page()
    fig_test_timeout()
    fig_mixer_timeline()
    fig_param5_dialects()
    print("ok")

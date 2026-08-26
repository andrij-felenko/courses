# -*- coding: utf-8 -*-
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

def tbox(x, y, s, size=14, bold=False, fill=FILL, stroke=LINE, sw=1.5, color=INK, rx=4, pad=10, min_w=0):
    b, _, _ = textbox(x, y, s, size=size, bold=bold, fill=fill, stroke=stroke, sw=sw, color=color, rx=rx, pad=pad, min_w=min_w)
    return b


def fig_threat_model():
    W, H = 820, 460
    p = []

    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#ffffff", sw=0))

    # Заголовок / фон категорій
    p.append(rect(20, 20, 230, 410, fill="#fcf3f2", stroke=POS, sw=1.5, rx=8))
    p.append(text(135, 48, "1. Вторинний ринок", size=14, color=POS, bold=True))
    p.append(text(135, 68, "Списання без зачистки", size=11, color=MUTED))

    p.append(rect(295, 20, 230, 410, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=8))
    p.append(text(410, 48, "2. Апаратне вилучення", size=14, color=INK, bold=True))
    p.append(text(410, 68, "Дамп фізичних носіїв", size=11, color=MUTED))

    p.append(rect(570, 20, 230, 410, fill="#fdf2e9", stroke=POS, sw=1.5, rx=8))
    p.append(text(685, 48, "3. Наслідки витоку", size=14, color=POS, bold=True))
    p.append(text(685, 68, "Компрометація систем", size=11, color=MUTED))

    # Блоки колонки 1
    p.append(tbox(135, 120, "Списаний пристрій\nна звалищі / аукціоні", size=11, bold=True, fill="#ffffff", stroke=POS, min_w=190, pad=8))
    p.append(tbox(135, 220, "Купівля зловмисником\nза $10 на вторинці", size=11, fill="#ffffff", stroke=LINE, min_w=190, pad=8))
    p.append(tbox(135, 330, "Плата неушкоджена:\nFlash і чип збережені", size=11, fill="#ffffff", stroke=LINE, min_w=190, pad=8))

    # Стрілка 1 -> 2
    p.append(arrow(250, 220, 290, 220, color=POS, sw=2))

    # Блоки колонки 2
    p.append(tbox(410, 120, "Випоювання Flash\nабо прищіпка SOIC-8", size=11, fill="#ffffff", stroke=LINE, min_w=190, pad=8))
    p.append(tbox(410, 220, "Підключення до JTAG/UART\nдамп NVS / LittleFS", size=11, bold=True, fill="#ffffff", stroke=LINE, min_w=190, pad=8))
    p.append(tbox(410, 330, "Видобуто: mTLS ключі,\nWi-Fi PSK, JWT токени", size=11, bold=True, fill="#ffffff", stroke=POS, min_w=190, pad=8))

    # Стрілка 2 -> 3
    p.append(arrow(525, 330, 565, 330, color=POS, sw=2))

    # Блоки колонки 3
    p.append(tbox(685, 120, "Хмарний бекенд:\nпідміна телеметрії парку", size=11, fill="#ffffff", stroke=POS, min_w=190, pad=8))
    p.append(tbox(685, 220, "Корпоративна мережа:\nвхід через збережений Wi-Fi", size=11, fill="#ffffff", stroke=POS, min_w=190, pad=8))
    p.append(tbox(685, 330, "Реверс алгоритмів:\nкрадіжка прошивки", size=11, fill="#ffffff", stroke=POS, min_w=190, pad=8))

    render(os.path.join(IMG, "decommission-threat-model.svg"), W, H, *p)


def fig_zeroization_levels():
    W, H = 820, 460
    p = []

    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#ffffff", sw=0))

    # 4 рівні зачистки
    levels = [
        ("1. Логічне видалення", "Видалення індексу ФС", "Видалено лише індекс;\nфізичні байти лишаються", POS, "#fcf3f2"),
        ("2. Перезапис секторів", "Перезапис логічного блоку", "Логічний блок затерто,\nале є копії у Flash", POS, "#fdf2e9"),
        ("3. Повне стирання", "Тунелювання Фаулера-Нордгейма", "Усі блоки = 0xFF;\nповне фізичне стирання", FIELD, "#eafaf0"),
        ("4. Крипто-стирання", "Знищення KEK в eFuse / TPM", "Знищено KEK в eFuse;\nдані стають білим шумом", FIELD, "#eafaf0")
    ]

    col_w = 180
    gap = 16
    start_x = 30

    for i, (title, sub, desc, col, bg_col) in enumerate(levels):
        x = start_x + i * (col_w + gap)
        # Карточка рівня
        p.append(rect(x, 30, col_w, 390, fill=bg_col, stroke=col, sw=1.8, rx=6))
        p.append(text(x + col_w/2, 60, title, size=11, color=col, bold=True))
        p.append(text(x + col_w/2, 80, sub, size=9, color=MUTED))

        # Ілюстрація стану Flash
        box_y = 120
        p.append(rect(x + 15, box_y, col_w - 30, 160, fill="#ffffff", stroke=LINE, sw=1, rx=4))
        p.append(text(x + col_w/2, box_y + 24, "Фізична матриця Flash", size=10, color=MUTED, bold=True))

        if i == 0:
            p.append(rect(x + 25, box_y + 40, col_w - 50, 45, fill="#fadbd8", stroke=POS, sw=1))
            p.append(text(x + col_w/2, box_y + 66, "Секрети (цілі)", size=10, color=POS, bold=True))
            p.append(rect(x + 25, box_y + 95, col_w - 50, 45, fill="#f4f6f8", stroke=LINE, sw=1))
            p.append(text(x + col_w/2, box_y + 121, "Індекс: [видалено]", size=9, color=MUTED))
        elif i == 1:
            p.append(rect(x + 25, box_y + 40, col_w - 50, 45, fill="#d5f5e3", stroke=FIELD, sw=1))
            p.append(text(x + col_w/2, box_y + 66, "Логічний блок: 0x00", size=10, color=FIELD))
            p.append(rect(x + 25, box_y + 95, col_w - 50, 45, fill="#fdebd0", stroke=POS, sw=1))
            p.append(text(x + col_w/2, box_y + 121, "Резервний блок: СЕКРЕТ", size=9, color=POS, bold=True))
        elif i == 2:
            p.append(rect(x + 25, box_y + 40, col_w - 50, 100, fill="#e8f8f5", stroke=FIELD, sw=1))
            p.append(text(x + col_w/2, box_y + 80, "Усі блоки = 0xFF", size=11, color=FIELD, bold=True))
            p.append(text(x + col_w/2, box_y + 105, "Повний Chip Erase", size=9, color=MUTED))
        elif i == 3:
            p.append(rect(x + 25, box_y + 40, col_w - 50, 50, fill="#f2f4f4", stroke=LINE, sw=1))
            p.append(text(x + col_w/2, box_y + 68, "AES-XTS шифротекст", size=9, color=MUTED))
            p.append(rect(x + 25, box_y + 100, col_w - 50, 40, fill="#fadbd8", stroke=POS, sw=1))
            p.append(text(x + col_w/2, box_y + 124, "KEK eFuse: [СПАЛЕНО]", size=9, color=POS, bold=True))

        # Опис наслідків
        p.append(tbox(x + col_w/2, 350, desc, size=10, fill="#ffffff", stroke=col, min_w=140, pad=4))

    render(os.path.join(IMG, "zeroization-levels.svg"), W, H, *p)


def fig_decommission_handshake():
    W, H = 820, 480
    p = []

    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#ffffff", sw=0))

    cloud_x = 160
    dev_x = W - 160

    # Заголовки сторін
    p.append(circle(cloud_x, 48, 22, fill="#eaf0fd", stroke=NEG, sw=2))
    p.append(text(cloud_x, 52, "☁", size=16, color=NEG))
    p.append(text(cloud_x, 82, "Хмарний бекенд / PKI", size=12, color=NEG, bold=True))

    p.append(circle(dev_x, 48, 22, fill="#eafaf0", stroke=FIELD, sw=2))
    p.append(text(dev_x, 52, "⬡", size=16, color=FIELD))
    p.append(text(dev_x, 82, "IoT-пристрій у полі", size=12, color=FIELD, bold=True))

    # Доріжки життя
    p.append(line(cloud_x, 96, cloud_x, 440, color=NEG, sw=1, dash="3 5"))
    p.append(line(dev_x, 96, dev_x, 440, color=FIELD, sw=1, dash="3 5"))

    mid_x = (cloud_x + dev_x) / 2

    # Крок 1: Команда на списання від хмари
    y1 = 135
    p.append(arrow(cloud_x + 20, y1, dev_x - 20, y1, color=NEG, sw=2))
    p.append(tbox(mid_x, y1 - 16, "1 · DECOMMISSION_ORDER (підпис Cloud Root + Nonce)", size=10, bold=True, fill="#ffffff", stroke=NEG, min_w=340, pad=6))

    # Крок 2: Локальна перевірка та підготовка
    y2 = 205
    p.append(rect(dev_x - 110, y2 - 18, 220, 36, fill="#ffffff", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(dev_x, y2 + 4, "2 · Перевірка підпису, зупинка сервісів", size=10, color=FIELD, bold=True))

    # Крок 3: Підтвердження списання (ACK)
    y3 = 275
    p.append(arrow(dev_x - 20, y3, cloud_x + 20, y3, color=FIELD, sw=2))
    p.append(tbox(mid_x, y3 - 16, "3 · DECOMMISSION_ACK (підпис пристрою + хеш стану)", size=10, bold=True, fill="#ffffff", stroke=FIELD, min_w=340, pad=6))

    # Крок 4: Хмара відкликає сертифікат
    y4 = 345
    p.append(rect(cloud_x - 110, y4 - 18, 220, 36, fill="#ffffff", stroke=NEG, sw=1.5, rx=4))
    p.append(text(cloud_x, y4 + 4, "4 · Відкликання сертифіката (CRL/OCSP)", size=10, color=NEG, bold=True))

    # Крок 5: Пристрій виконує Zeroization
    y5 = 415
    p.append(rect(dev_x - 110, y5 - 18, 220, 36, fill="#fadbd8", stroke=POS, sw=2, rx=4))
    p.append(text(dev_x, y5 + 4, "5 · Crypto-Erase + спалювання eFuse", size=10, color=POS, bold=True))

    render(os.path.join(IMG, "decommission-handshake.svg"), W, H, *p)


def fig_efuse_lifecycle():
    W, H = 820, 440
    p = []

    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#ffffff", sw=0))

    states = [
        ("1. ЧИП З ЗАВОДУ", "Virgin / Blank", "JTAG відкритий\neFuses = 0\nЗавантажувач UART", "#2457d6", "#eaf0fd"),
        ("2. ПРОВІЗІОНОВАНИЙ", "Provisioned", "KEK записано в OTP\nВідкритий ключ Root CA\nІдентичність прошита", "#27ae60", "#eafaf0"),
        ("3. В ЕКСПЛУАТАЦІЇ", "Secured In-Field", "JTAG апаратно відрізано\nSecure Boot активний\nFlash Encryption увімкнено", "#27ae60", "#eafaf0"),
        ("4. СПИСАНИЙ", "Decommissioned", "KEK знищено в eFuse\nBootloader вимкнено\nКремній інертний", "#c0392b", "#fadbd8")
    ]

    box_w = 170
    box_h = 240
    gap = 30
    start_x = 25
    y = 100

    for i, (title, sub, details, col, bg_col) in enumerate(states):
        x = start_x + i * (box_w + gap)

        # Рамка стану
        p.append(rect(x, y, box_w, box_h, fill=bg_col, stroke=col, sw=2, rx=6))
        p.append(text(x + box_w/2, y + 30, title, size=11, color=col, bold=True))
        p.append(text(x + box_w/2, y + 50, sub, size=9, color=MUTED, italic=True))

        p.append(line(x + 10, y + 65, x + box_w - 10, y + 65, color=col, sw=1))

        # Опис характеристик
        p.append(tbox(x + box_w/2, y + 145, details, size=10, fill="#ffffff", stroke=col, min_w=box_w - 20, pad=8))

        # Стрілка переходу
        if i < 3:
            arrow_x1 = x + box_w + 4
            arrow_x2 = arrow_x1 + gap - 8
            p.append(arrow(arrow_x1, y + box_h/2, arrow_x2, y + box_h/2, color=LINE, sw=2))
            # Напис на стрілці
            labels = ["OTP запис", "Lock eFuses", "Kill eFuse"]
            p.append(text((arrow_x1 + arrow_x2)/2, y + box_h/2 - 12, labels[i], size=9, color=MUTED, bold=True))

    p.append(text(W/2, 50, "Апаратний життєвий цикл мікроконтролера (eFuse State Transitions)", size=14, color=INK, bold=True))
    p.append(text(W/2, 390, "Переходи між станами є незворотними: плавлений запобіжник eFuse неможливо відновити", size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "efuse-lifecycle-lockdown.svg"), W, H, *p)


if __name__ == '__main__':
    fig_threat_model()
    fig_zeroization_levels()
    fig_decommission_handshake()
    fig_efuse_lifecycle()
    print("All figures generated successfully.")

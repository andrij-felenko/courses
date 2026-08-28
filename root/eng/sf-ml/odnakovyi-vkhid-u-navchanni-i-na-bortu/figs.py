# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_pipeline_divergence():
    W, H = 880, 470
    p = []

    # Заголовки конвеєрів
    p.append(text(230, 40, 'Конвеєр навчання (Python / PyTorch / GPU)', size=14, color=NEG, bold=True))
    p.append(text(230, 260, 'Конвеєр виводу на борту (CMOS / ISP / MCU)', size=14, color=POS, bold=True))

    # Верхній конвеєр (Навчання)
    b1 = fitbox(40, 60, 170, 70, 'Кадр датасету\nsRGB 24-bit RGB\nчистий студійний', size=12, fill='#eaf0fd', stroke=NEG)
    b2 = fitbox(250, 60, 170, 70, 'Масштабування\nPIL / OpenCV Resize\nfloat32 half_pixel', size=12, fill='#eaf0fd', stroke=NEG)
    b3 = fitbox(460, 60, 170, 70, 'Нормалізація\n(x - mean) / std\nfloat32 ділення', size=12, fill='#eaf0fd', stroke=NEG)
    b4 = fitbox(670, 60, 170, 70, 'Тензор моделі\nФормат NCHW\nfloat32 пам\'ять GPU', size=12, fill='#eaf0fd', stroke=NEG)
    p.extend([b1, b2, b3, b4])

    p.append(arrow(210, 95, 245, 95, color=NEG, sw=1.8))
    p.append(arrow(420, 95, 455, 95, color=NEG, sw=1.8))
    p.append(arrow(630, 95, 665, 95, color=NEG, sw=1.8))

    # Нижній конвеєр (Борт)
    b5 = fitbox(40, 280, 170, 70, 'Камера сенсора\nRGB565 / YUV422\nшум, AEC / AWB', size=12, fill='#fdecea', stroke=POS)
    b6 = fitbox(250, 280, 170, 70, 'Масштабування\nC цілочисельний resize\nQ16.16 line-buffer', size=12, fill='#fdecea', stroke=POS)
    b7 = fitbox(460, 280, 170, 70, 'Злите квантування\n(x * K_eff) >> n + Z_eff\nint8 афінна сітка', size=12, fill='#fdecea', stroke=POS)
    b8 = fitbox(670, 280, 170, 70, 'Тензор моделі\nФормат NHWC\nint8 буфер SRAM', size=12, fill='#fdecea', stroke=POS)
    p.extend([b5, b6, b7, b8])

    p.append(arrow(210, 315, 245, 315, color=POS, sw=1.8))
    p.append(arrow(420, 315, 455, 315, color=POS, sw=1.8))
    p.append(arrow(630, 315, 665, 315, color=POS, sw=1.8))

    # Порівняльні лінії розбіжностей (розбиті на 2 відрізки, щоб не перетинати рамку напису)
    diffs = [
        (125, 130, 280, 'Розрядність і колір\n24b RGB vs RGB565'),
        (335, 130, 280, 'Алгоритм сітки\nfloat coords vs Q16.16'),
        (545, 130, 280, 'Математика шкали\nfloat ділення vs int8 зсув'),
        (755, 130, 280, 'Розкладка пам\'яті\nNCHW vs NHWC'),
    ]

    for xc, y_top, y_bot, label in diffs:
        box_h = 44
        box_w = 170
        by = (y_top + y_bot) / 2 - box_h / 2
        bx = xc - box_w / 2
        p.append(line(xc, y_top, xc, by, color=MUTED, sw=1.4, dash='4 3'))
        p.append(line(xc, by + box_h, xc, y_bot, color=MUTED, sw=1.4, dash='4 3'))
        db = fitbox(bx, by, box_w, box_h, label, size=10, fill='#fff9db', stroke='#d48800', color='#7a4b00')
        p.append(db)

    # Підсумок внизу
    res_box = fitbox(180, 390, 520, 50, 'Наслідок: Training-Serving Skew\nНепомітні для ока розбіжності руйнують активації згорткових шарів', size=12, fill='#f9f0ff', stroke='#722ed1', color='#391085', bold=True)
    p.append(res_box)

    render(os.path.join(OUT, 'pipeline-divergence.svg'), W, H, *p)


def fig_quantization_error_propagation():
    W, H = 880, 440
    p = []

    p.append(text(W / 2, 35, 'Каскадне накопичення похибок конвеєра та руйнування активацій', size=15, color=INK, bold=True))

    stages = [
        (40, 75, 180, 80, '1. Сенсор та ISP', 'Шум фотодіодів,\nдрейф AWB і AEC\nΔ ≈ 3..6 LSB', '#e6f7ff', '#1890ff'),
        (255, 75, 180, 80, '2. Зрізання бітів', 'Конверсія кольору\nRGB888 → RGB565\nΔ ≈ 2..4 LSB', '#fff7e6', '#fa8c16'),
        (470, 75, 180, 80, '3. Сітка Resize', 'Q16.16 субокруглення,\nзсув півпікселя\nΔ ≈ 1..3 LSB', '#fff1f0', '#f5222d'),
        (685, 75, 180, 80, '4. Квантування', 'int8 афінний clamp,\nокруглення нуль-пункту\nΔ ≈ 0.5..1 LSB', '#f6ffed', '#52c41a'),
    ]

    for x, y, w, h, header, desc, fill, stroke in stages:
        box = fitbox(x, y, w, h, '%s\n%s' % (header, desc), size=11, fill=fill, stroke=stroke, color=INK)
        p.append(box)

    p.append(arrow(225, 115, 250, 115, color=MUTED, sw=1.8))
    p.append(arrow(440, 115, 465, 115, color=MUTED, sw=1.8))
    p.append(arrow(655, 115, 680, 115, color=MUTED, sw=1.8))

    # Стрілка вниз до тензора першого шару
    p.append(arrow(775, 160, 775, 230, color=POS, sw=2.0))
    p.append(line(130, 160, 130, 195, color=MUTED, sw=1.4, dash='3 3'))
    p.append(line(130, 195, 775, 195, color=MUTED, sw=1.4, dash='3 3'))

    # Наслідки в шарах моделі
    b_lyr0 = fitbox(50, 240, 360, 80, 'Шар 0: Перша згортка (Conv 3x3)\nВисокочастотні фільтри градієнтів\nПохибки підсилюються вагами (x2..x5)\nCosine Similarity падає: 0.999 → 0.982', size=11, fill='#fdecea', stroke=POS, color=INK)
    b_relu = fitbox(470, 240, 360, 80, 'Функція активації (ReLU / Hard-Swish)\nЗсув знаку перетворює слабкий сигнал на 0\nЗанулення каналів (Neuron Death)\nМаска активацій розходиться на 15-30%', size=11, fill='#fdecea', stroke=POS, color=INK)
    p.extend([b_lyr0, b_relu])

    p.append(arrow(415, 280, 465, 280, color=POS, sw=1.8))

    # Фінал
    p.append(arrow(650, 325, 650, 360, color=POS, sw=2.0))
    b_out = fitbox(170, 365, 600, 48, 'Фінальний вихід моделі: деградація метрик (Top-1: 98% → 42%)\nПаритет препроцесингу — єдиний захист від Training-Serving Skew', size=12, fill='#fff2e8', stroke='#d4380d', color='#871400', bold=True)
    p.append(b_out)

    render(os.path.join(OUT, 'quantization-error-propagation.svg'), W, H, *p)


if __name__ == '__main__':
    fig_pipeline_divergence()
    fig_quantization_error_propagation()
    print('Done')

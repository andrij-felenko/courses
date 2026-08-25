# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для статті «NOR Flash: комірка, побайтове читання і блокове стирання».
Тека: book/electronics/microelectronics/nor-flash-cell/img/
"""

import sys
import os

# Підключення svgkit із scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_cell_cross_section():
    """Фігура 1: Будова комірки NOR Flash — плаваючий затвор (Floating Gate) та пастка заряду (Charge Trap / SONOS)."""
    w, h = 880, 430
    out = []

    # Заголовок панелей
    tb1, _, _ = textbox(225, 25, "Комірка з плаваючим затвором (Floating Gate)", size=13, bold=True, fill="#eef2f7", min_w=400)
    tb2, _, _ = textbox(655, 25, "Комірка з пасткою заряду (Charge Trap / SONOS)", size=13, bold=True, fill="#eef2f7", min_w=400)
    out.extend([tb1, tb2])

    # === Ліва панель: Floating Gate ===
    # Кремнієва підкладка p-типу
    out.append(rect(30, 240, 390, 120, fill="#e8edf2", stroke=LINE, sw=1.5, rx=4))
    out.append(text(225, 335, "Кремнієва підкладка p-типу (p-Si substrate / p-well)", size=11, color=MUTED, bold=True))

    # Області Source (N+) та Drain (N+)
    out.append(rect(40, 240, 80, 50, fill="#fbeae8", stroke=POS, sw=1.5, rx=3))
    out.append(text(80, 270, "Витік N+", size=12, color=POS, bold=True))
    out.append(rect(330, 240, 80, 50, fill="#fbeae8", stroke=POS, sw=1.5, rx=3))
    out.append(text(370, 270, "Стік N+", size=12, color=POS, bold=True))

    # Канал
    out.append(rect(120, 240, 210, 15, fill="#f0fdf4", stroke=FIELD, sw=1.0, rx=2))
    out.append(text(225, 252, "Інверсійний канал провідності", size=10, color=FIELD, bold=True))

    # Тунельний оксид (SiO2, 8-10 нм)
    out.append(rect(120, 215, 210, 22, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=2))
    out.append(text(225, 230, "Тунельний оксид SiO₂ (8–10 нм)", size=10, color="#92400e", bold=True))

    # Плаваючий затвор (провідний полікремній n+ Poly)
    out.append(rect(120, 160, 210, 50, fill="#fee2e2", stroke=POS, sw=1.8, rx=4))
    out.append(text(225, 180, "Плаваючий затвор (Floating Gate)", size=11, color=POS, bold=True))
    out.append(text(225, 197, "провідний полікремній (n⁺ Poly-Si)", size=10, color=MUTED))

    # Міжзатворний діелектрик (ONO)
    out.append(rect(120, 130, 210, 25, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=2))
    out.append(text(225, 147, "Міжзатворний діелектрик ONO (15–20 нм)", size=10, color="#92400e", bold=True))

    # Керівний затвор (Control Gate)
    out.append(rect(120, 65, 210, 60, fill="#e0e7ff", stroke=NEG, sw=1.8, rx=4))
    out.append(text(225, 92, "Керівний затвор (Control Gate)", size=12, color=NEG, bold=True))
    out.append(text(225, 110, "підключено до лінії слів WL", size=10, color=MUTED))

    # Виводи зліва
    out.append(line(80, 290, 80, 380, color=LINE, sw=1.5))
    tb_sl, _, _ = textbox(80, 395, "Лінія витоків SL", size=10, fill="#ffffff", min_w=90)
    out.append(tb_sl)

    out.append(line(370, 290, 370, 380, color=LINE, sw=1.5))
    tb_bl, _, _ = textbox(370, 395, "Бітова лінія BL", size=10, fill="#ffffff", min_w=90)
    out.append(tb_bl)

    # === Права панель: Charge Trap (SONOS) ===
    # Кремнієва підкладка p-типу
    out.append(rect(460, 240, 390, 120, fill="#e8edf2", stroke=LINE, sw=1.5, rx=4))
    out.append(text(655, 335, "Кремнієва підкладка p-типу (p-Si substrate / p-well)", size=11, color=MUTED, bold=True))

    # Області Source (N+) та Drain (N+)
    out.append(rect(470, 240, 80, 50, fill="#fbeae8", stroke=POS, sw=1.5, rx=3))
    out.append(text(510, 270, "Витік N+", size=12, color=POS, bold=True))
    out.append(rect(760, 240, 80, 50, fill="#fbeae8", stroke=POS, sw=1.5, rx=3))
    out.append(text(800, 270, "Стік N+", size=12, color=POS, bold=True))

    # Канал
    out.append(rect(550, 240, 210, 15, fill="#f0fdf4", stroke=FIELD, sw=1.0, rx=2))
    out.append(text(655, 252, "Інверсійний канал провідності", size=10, color=FIELD, bold=True))

    # Тунельний оксид (SiO2, 3-5 нм)
    out.append(rect(550, 218, 210, 18, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=2))
    out.append(text(655, 231, "Тунельний оксид SiO₂ (3–5 нм)", size=10, color="#92400e", bold=True))

    # Пастковий діелектрик (нітрид кремнію Si3N4)
    out.append(rect(550, 165, 210, 48, fill="#ecfdf5", stroke=FIELD, sw=1.8, rx=4))
    out.append(text(655, 183, "Пастка заряду: нітрид Si₃N₄", size=11, color=FIELD, bold=True))
    out.append(text(655, 200, "дискретні пастки (ізолятор)", size=10, color=MUTED))

    # Блокуючий оксид (SiO2 / Al2O3)
    out.append(rect(550, 135, 210, 25, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=2))
    out.append(text(655, 152, "Блокуючий оксид SiO₂ / Al₂O₃", size=10, color="#92400e", bold=True))

    # Керівний затвор (Control Gate / Metal Gate)
    out.append(rect(550, 65, 210, 65, fill="#e0e7ff", stroke=NEG, sw=1.8, rx=4))
    out.append(text(655, 92, "Керівний затвор (Metal / Poly Gate)", size=12, color=NEG, bold=True))
    out.append(text(655, 110, "підключено до лінії слів WL", size=10, color=MUTED))

    # Виводи справа
    out.append(line(510, 290, 510, 380, color=LINE, sw=1.5))
    tb_sl2, _, _ = textbox(510, 395, "Лінія витоків SL", size=10, fill="#ffffff", min_w=90)
    out.append(tb_sl2)

    out.append(line(800, 290, 800, 380, color=LINE, sw=1.5))
    tb_bl2, _, _ = textbox(800, 395, "Бітова лінія BL", size=10, fill="#ffffff", min_w=90)
    out.append(tb_bl2)

    render(os.path.join(OUT_DIR, "nor-cell-cross-section.svg"), w, h, "".join(out))


def fig_che_fn_mechanisms():
    """Фігура 2: Механізми програмування (CHE) та стирання (FN тунелювання) комірки NOR Flash."""
    w, h = 880, 440
    out = []

    # Заголовки режимів
    tb1, _, _ = textbox(225, 25, "Програмування («0»): інжекція гарячих електронів (CHE)", size=12, bold=True, fill="#fee2e2", stroke=POS, min_w=410)
    tb2, _, _ = textbox(655, 25, "Стирання («1»): тунелювання Фаулера–Нордгейма (FN)", size=12, bold=True, fill="#e0e7ff", stroke=NEG, min_w=410)
    out.extend([tb1, tb2])

    # === Ліва частина: CHE ===
    # Потенціали
    tb_vg, _, _ = textbox(225, 65, "V_CG = +9..+12 В (сильне вертикальне поле)", size=11, bold=True, color=POS, fill="#fff1f2")
    out.append(tb_vg)

    # Транзистор CHE
    out.append(rect(30, 260, 390, 110, fill="#f8fafc", stroke=LINE, sw=1.5, rx=4))
    out.append(rect(40, 260, 70, 50, fill="#fbeae8", stroke=POS, sw=1.2))
    out.append(text(75, 290, "Витік 0 В", size=11, color=POS, bold=True))
    out.append(rect(340, 260, 70, 50, fill="#fbeae8", stroke=POS, sw=1.2))
    out.append(text(375, 290, "Стік +5 В", size=11, color=POS, bold=True))

    # Канал з прискоренням
    out.append(rect(110, 260, 230, 20, fill="#fef08a", stroke="#ca8a04", sw=1.0))
    out.append(text(225, 275, "Канальний струм I_D ~ 0.5–1 мА", size=10, color="#854d0e", bold=True))

    # Плаваючий затвор
    out.append(rect(120, 160, 210, 45, fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
    out.append(text(225, 185, "Плаваючий затвор (FG)", size=11, color=POS, bold=True))

    # Керівний затвор
    out.append(rect(120, 95, 210, 40, fill="#e0e7ff", stroke=NEG, sw=1.5, rx=3))
    out.append(text(225, 120, "Керівний затвор (CG = +10 В)", size=11, color=NEG, bold=True))

    # Стрілка гарячих електронів через оксид
    out.append(arrow(290, 255, 270, 210, color=POS, sw=2.5))
    out.append(text(315, 230, "e⁻ (>3.1 еВ)", size=11, color=POS, bold=True))
    out.append(text(225, 335, "Горизонтальне поле прискорює e⁻ до стоку,", size=10, color=INK))
    out.append(text(225, 355, "вертикальне поле затягує гарячі e⁻ у затвор", size=10, color=INK))

    # === Права частина: FN Tunneling ===
    # Потенціали
    tb_fn_v, _, _ = textbox(655, 65, "V_CG = -10 В, V_well = +10 В (поле ~10 МВ/см)", size=11, bold=True, color=NEG, fill="#eff6ff")
    out.append(tb_fn_v)

    # Транзистор FN
    out.append(rect(460, 260, 390, 110, fill="#f8fafc", stroke=LINE, sw=1.5, rx=4))
    out.append(rect(470, 260, 70, 50, fill="#e8edf2", stroke=LINE, sw=1.2))
    out.append(text(505, 290, "Витік (flt)", size=10, color=MUTED))
    out.append(rect(770, 260, 70, 50, fill="#e8edf2", stroke=LINE, sw=1.2))
    out.append(text(805, 290, "Стік (flt)", size=10, color=MUTED))

    # Плаваючий затвор
    out.append(rect(550, 160, 210, 45, fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
    out.append(text(655, 185, "Плаваючий затвор (FG)", size=11, color=POS, bold=True))

    # Керівний затвор
    out.append(rect(550, 95, 210, 40, fill="#e0e7ff", stroke=NEG, sw=1.5, rx=3))
    out.append(text(655, 120, "Керівний затвор (CG = -10 В)", size=11, color=NEG, bold=True))

    # Стрілки квантового тунелювання
    out.append(arrow(620, 210, 620, 255, color=NEG, sw=2.0))
    out.append(arrow(655, 210, 655, 255, color=NEG, sw=2.0))
    out.append(arrow(690, 210, 690, 255, color=NEG, sw=2.0))
    out.append(text(725, 235, "e⁻ тунелюють", size=10, color=NEG, bold=True))

    out.append(text(655, 335, "Величезне електричне поле звужує бар'єр SiO₂,", size=10, color=INK))
    out.append(text(655, 355, "електрони квантово виходять у підкладку p-well", size=10, color=INK))

    render(os.path.join(OUT_DIR, "che-fn-mechanisms.svg"), w, h, "".join(out))


def fig_nor_matrix_parallel():
    """Фігура 3: Паралельна матриця NOR Flash, читання та небезпека перезастирання (Over-Erase)."""
    w, h = 920, 500
    out = []

    # Заголовок
    tb_h, _, _ = textbox(460, 25, "Топологія матриці NOR Flash: паралельне підключення комірок до бітових ліній", size=13, bold=True, fill="#eef2f7", min_w=700)
    out.append(tb_h)

    # Лінії слів (Wordlines) горизонтально
    out.append(line(160, 110, 640, 110, color=NEG, sw=2.0))
    tb_wl0, _, _ = textbox(85, 110, "WL0 (обрано: +3.3 В)", size=10, bold=True, color=NEG, fill="#eff6ff")
    out.append(tb_wl0)

    out.append(line(160, 240, 640, 240, color=MUTED, sw=2.0))
    tb_wl1, _, _ = textbox(85, 240, "WL1 (не обрано: 0 В)", size=10, bold=True, color=MUTED, fill="#f8fafc")
    out.append(tb_wl1)

    out.append(line(160, 370, 640, 370, color=MUTED, sw=2.0))
    tb_wl2, _, _ = textbox(85, 370, "WL2 (не обрано: 0 В)", size=10, bold=True, color=MUTED, fill="#f8fafc")
    out.append(tb_wl2)

    # Бітові лінії (Bitlines) вертикально: рознесені на x=220, x=520; витік на x=370
    out.append(line(220, 75, 220, 420, color=POS, sw=2.0))
    tb_bl0, _, _ = textbox(220, 60, "BL0 (Precharge +1.2 В)", size=10, bold=True, color=POS, fill="#fff1f2")
    out.append(tb_bl0)

    out.append(line(520, 75, 520, 420, color=POS, sw=2.0))
    tb_bl1, _, _ = textbox(520, 60, "BL1 (Precharge +1.2 В)", size=10, bold=True, color=POS, fill="#fff1f2")
    out.append(tb_bl1)

    # Спільна лінія витоків (Source Line)
    out.append(line(370, 80, 370, 420, color=LINE, sw=2.0, dash="4,4"))
    tb_sl, _, _ = textbox(370, 460, "Лінія витоків SL (0 В)", size=10, bold=True, fill="#f1f5f9", min_w=120)
    out.append(tb_sl)

    # Підсилювачі зчитування (Sense Amplifiers) знизу
    tb_sa0, _, _ = textbox(220, 460, "Sense Amp 0", size=10, bold=True, fill="#e0e7ff", min_w=100)
    tb_sa1, _, _ = textbox(520, 460, "Sense Amp 1", size=10, bold=True, fill="#e0e7ff", min_w=100)
    out.extend([tb_sa0, tb_sa1])

    # Комірки (транзистори)
    # Комірка (0,0) - Стерта ('1'): провідна під WL0
    out.append(rect(185, 90, 70, 40, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=3))
    out.append(text(220, 115, "«1» (ON)", size=11, color=FIELD, bold=True))

    # Комірка (0,1) - Запрограмована ('0'): закрита під WL0
    out.append(rect(485, 90, 70, 40, fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
    out.append(text(520, 115, "«0» (OFF)", size=11, color=POS, bold=True))

    # Комірка (1,0) - Нормальна під WL1=0В: закрита
    out.append(rect(185, 220, 70, 40, fill="#f1f5f9", stroke=MUTED, sw=1.2, rx=3))
    out.append(text(220, 245, "OFF (0 В)", size=9, color=MUTED))

    # Комірка (1,1) - ПЕРЕЗАСТЕРТА (Over-erased!): протікає навіть при WL1=0В!
    out.append(rect(485, 220, 70, 40, fill="#fef08a", stroke="#ca8a04", sw=2.0, rx=3))
    out.append(text(520, 236, "Over-Erase!", size=10, color="#854d0e", bold=True))
    out.append(text(520, 250, "V_th < 0 В", size=9, color="#854d0e"))

    # Стрілка витоку від перезатертої комірки
    out.append(arrow(520, 265, 520, 400, color="#ca8a04", sw=2.0))
    tb_leak, _, _ = textbox(595, 325, "Паразитний витік\nтягне BL1 на GND!", size=9, color="#854d0e", bold=True, fill="#fef9c3", stroke="#ca8a04")
    out.append(tb_leak)

    # Пояснювальний блок праворуч
    tb_info, _, _ = textbox(775, 240,
                            "ПРОБЛЕМА OVER-ERASE:\n"
                            "Якщо комірка втрачає забагато e⁻,\n"
                            "вона стає збідненою (V_th < 0 В).\n"
                            "Вона проводить навіть при V_WL = 0 В\n"
                            "і садить усю колонку BL1 на GND.\n"
                            "Усі інші комірки в колонці хибно\n"
                            "читаються як «1» (коротке замикання).\n"
                            "Лікування: Soft-Programming.",
                            size=10, fill="#fffbeb", stroke="#d97706", min_w=220)
    out.append(tb_info)

    render(os.path.join(OUT_DIR, "nor-matrix-parallel.svg"), w, h, "".join(out))


def fig_nor_vs_nand_density():
    """Фігура 4: Порівняння площі та підключення комірок NOR (10 F^2) проти NAND (4 F^2)."""
    w, h = 880, 430
    out = []

    # Заголовки колонок
    tb1, _, _ = textbox(225, 25, "NOR Flash: паралельні комірки (~10 F²)", size=13, bold=True, fill="#fee2e2", stroke=POS, min_w=390)
    tb2, _, _ = textbox(655, 25, "NAND Flash: послідовний стек (~4 F²)", size=13, bold=True, fill="#dcfce7", stroke=FIELD, min_w=390)
    out.extend([tb1, tb2])

    # === Ліва частина: NOR layout ===
    out.append(rect(30, 60, 390, 345, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))

    # Комірка 1
    out.append(rect(80, 85, 290, 60, fill="#ffffff", stroke=POS, sw=1.5, rx=4))
    out.append(circle(110, 115, 11, fill="#fed7aa", stroke="#ea580c", sw=1.5))
    out.append(text(110, 119, "C", size=10, color="#9a3412", bold=True))
    out.append(text(230, 108, "Транзистор комірки 1 (WL0)", size=11, color=INK, bold=True))
    out.append(text(230, 126, "Окремий контакт C до лінії BL", size=9, color=MUTED))

    # Контакт між комірками
    out.append(line(60, 160, 390, 160, color=LINE, sw=1.5, dash="3,3"))
    out.append(text(225, 156, "Спільний контакт Source (SL)", size=9, color=MUTED))

    # Комірка 2
    out.append(rect(80, 175, 290, 60, fill="#ffffff", stroke=POS, sw=1.5, rx=4))
    out.append(circle(110, 205, 11, fill="#fed7aa", stroke="#ea580c", sw=1.5))
    out.append(text(110, 209, "C", size=10, color="#9a3412", bold=True))
    out.append(text(230, 198, "Транзистор комірки 2 (WL1)", size=11, color=INK, bold=True))
    out.append(text(230, 216, "Окремий контакт C до лінії BL", size=9, color=MUTED))

    tb_nor_desc, _, _ = textbox(225, 315,
                                "• Площа комірки: ~9–12 F²\n"
                                "• Кожна пара комірок вимагає металевого контакту до BL\n"
                                "• Швидке випадкове читання байта: 50–90 нс\n"
                                "• Низька щільність, висока ціна за біт (1–256 МБ)",
                                size=10, fill="#fff1f2", stroke=POS, min_w=340)
    out.append(tb_nor_desc)

    # === Права частина: NAND layout ===
    out.append(rect(460, 60, 390, 345, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))

    # Стек послідовних комірок
    out.append(rect(510, 85, 290, 165, fill="#ffffff", stroke=FIELD, sw=1.5, rx=4))
    out.append(circle(535, 100, 10, fill="#fed7aa", stroke="#ea580c", sw=1.2))
    out.append(text(535, 104, "C", size=9, color="#9a3412", bold=True))
    out.append(text(655, 102, "Контакт BL (1 на весь ланцюг)", size=10, color=FIELD, bold=True))

    out.append(rect(540, 118, 230, 18, fill="#f0fdf4", stroke=FIELD, sw=1.0))
    out.append(text(655, 131, "Комірка WL0 (послідовно)", size=9, color=INK))

    out.append(rect(540, 140, 230, 18, fill="#f0fdf4", stroke=FIELD, sw=1.0))
    out.append(text(655, 153, "Комірка WL1 (послідовно)", size=9, color=INK))

    out.append(rect(540, 162, 230, 18, fill="#f0fdf4", stroke=FIELD, sw=1.0))
    out.append(text(655, 175, "Комірка WL2 (послідовно)", size=9, color=INK))

    out.append(rect(540, 184, 230, 18, fill="#f0fdf4", stroke=FIELD, sw=1.0))
    out.append(text(655, 197, "Комірки WL3..WL63 (без контактів!)", size=9, color=MUTED))

    out.append(circle(535, 230, 10, fill="#fed7aa", stroke="#ea580c", sw=1.2))
    out.append(text(535, 234, "C", size=9, color="#9a3412", bold=True))
    out.append(text(655, 233, "Контакт Source SL (1 на ланцюг)", size=10, color=FIELD, bold=True))

    tb_nand_desc, _, _ = textbox(655, 315,
                                 "• Площа комірки: ~4–5 F² (2D) / надвисока (3D BiCS)\n"
                                 "• 32–128 комірок з'єднані послідовно без контактів\n"
                                 "• Читання лише сторінками (2–16 КБ) за 25–50 мкс\n"
                                 "• Колосальна щільність, низька ціна (ГБ / ТБ)",
                                 size=10, fill="#ecfdf5", stroke=FIELD, min_w=340)
    out.append(tb_nand_desc)

    render(os.path.join(OUT_DIR, "nor-vs-nand-density.svg"), w, h, "".join(out))


if __name__ == '__main__':
    fig_cell_cross_section()
    fig_che_fn_mechanisms()
    fig_nor_matrix_parallel()
    fig_nor_vs_nand_density()
    print("Всі фігури згенеровано успішно.")

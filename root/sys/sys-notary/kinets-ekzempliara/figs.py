# -*- coding: utf-8 -*-
import os
import sys

# Додаємо шлях до спільного модуля svgkit у scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import (
    render, rect, line, arrow, text, mtext, textbox, fitbox, circle,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG
)

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def make_fig_device_decommission_workflow():
    """Етапи виведення пристрою з експлуатації: від логічного відв'язування до WEEE-переробки."""
    w, h = 980, 520
    frags = []

    # Заголовок зверху
    frags.append(text(w / 2, 28, "Повний життєвий цикл виведення з експлуатації та санітизації екземпляра", size=15, bold=True))

    col_w = 215
    col_gap = 25
    top_y = 55
    col_h = 440

    # Етап 1: Логічне відв'язування
    x1 = 25
    frags.append(rect(x1, top_y, col_w, col_h, fill="#f4f8fe", stroke=NEG, sw=2, rx=8))
    frags.append(rect(x1, top_y, col_w, 42, fill="#e2edfd", stroke=NEG, sw=1.5, rx=8))
    frags.append(text(x1 + col_w / 2, top_y + 26, "1. Логічне відв'язування", size=13, color=NEG, bold=True))

    items1 = [
        ("Хмарна ідентичність", "Відкликання OAuth2/mTLS,\nвидалення з Fleet Manager"),
        ("Криптографічні ключі", "Анулювання сертифікатів,\nрозірвання Trust Anchors"),
        ("Дані власника", "Відв'язка облікового запису,\nскасування підписок"),
        ("Апаратний статус", "Встановлення прапорця\nDecommissioned в eFuse"),
    ]
    cur_y = top_y + 55
    for title, desc in items1:
        frags.append(fitbox(x1 + 8, cur_y, col_w - 16, 75, f"{title}\n{desc}", size=11, pad=4, fill="#ffffff", stroke="#c4d8fa", bold=False))
        cur_y += 85

    # Стрілка 1 -> 2
    frags.append(arrow(x1 + col_w, top_y + col_h / 2, x1 + col_w + col_gap, top_y + col_h / 2, color=MUTED, sw=2))

    # Етап 2: Санітизація даних (NIST SP 800-88)
    x2 = x1 + col_w + col_gap
    frags.append(rect(x2, top_y, col_w, col_h, fill="#fef8f0", stroke="#d97706", sw=2, rx=8))
    frags.append(rect(x2, top_y, col_w, 42, fill="#fde68a", stroke="#d97706", sw=1.5, rx=8))
    frags.append(text(x2 + col_w / 2, top_y + 26, "2. Санітизація (NIST 800-88)", size=13, color="#b45309", bold=True))

    items2 = [
        ("Crypto-Erase (Purge)", "Миттєве занулення KEK/MEK\nу TPM / Secure Element"),
        ("NVMe / ATA Sanitize", "Низькорівневе очищення комірок\nNAND Flash повз шар FTL"),
        ("eMMC / UFS Erase", "Команди Secure Erase/Trim,\nверифікація нульових байтів"),
        ("Аудит результату", "Генерація криптографічного\nсертифіката санітизації"),
    ]
    cur_y = top_y + 55
    for title, desc in items2:
        frags.append(fitbox(x2 + 8, cur_y, col_w - 16, 75, f"{title}\n{desc}", size=11, pad=4, fill="#ffffff", stroke="#fcd34d", bold=False))
        cur_y += 85

    # Стрілка 2 -> 3
    frags.append(arrow(x2 + col_w, top_y + col_h / 2, x2 + col_w + col_gap, top_y + col_h / 2, color=MUTED, sw=2))

    # Етап 3: Інженерний тріаж
    x3 = x2 + col_w + col_gap
    frags.append(rect(x3, top_y, col_w, col_h, fill="#f4fbf7", stroke=FIELD, sw=2, rx=8))
    frags.append(rect(x3, top_y, col_w, 42, fill="#e1f5eb", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(x3 + col_w / 2, top_y + 26, "3. Інженерний тріаж", size=13, color=FIELD, bold=True))

    items3 = [
        ("Діагностика стану", "Перевірка працездатності SoC,\nшини живлення, датчиків"),
        ("Гілка А: Рециклінг/ReUse", "Повторне калібрування,\nпередача новому власникові"),
        ("Гілка Б: Списання", "Фізичне пошкодження/знос,\nнаправлення на утилізацію"),
        ("Знищення чіпів", "Механічна деінтеграція чіпів\nFlash/TPM (DIN 66399 H-4/5)"),
    ]
    cur_y = top_y + 55
    for title, desc in items3:
        frags.append(fitbox(x3 + 8, cur_y, col_w - 16, 75, f"{title}\n{desc}", size=11, pad=4, fill="#ffffff", stroke="#c3e6d5", bold=False))
        cur_y += 85

    # Стрілка 3 -> 4
    frags.append(arrow(x3 + col_w, top_y + col_h / 2, x3 + col_w + col_gap, top_y + col_h / 2, color=MUTED, sw=2))

    # Етап 4: Екологічний демонтаж (WEEE & RoHS)
    x4 = x3 + col_w + col_gap
    frags.append(rect(x4, top_y, col_w, col_h, fill="#fdf4f4", stroke=POS, sw=2, rx=8))
    frags.append(rect(x4, top_y, col_w, 42, fill="#fde2e2", stroke=POS, sw=1.5, rx=8))
    frags.append(text(x4 + col_w / 2, top_y + 26, "4. Демонтаж (WEEE/RoHS)", size=13, color=POS, bold=True))

    items4 = [
        ("Вилучення АКБ", "Безпечний розряд і демонтаж\nLi-Ion / LiFePO4 (EU 2023/1542)"),
        ("Селективна розбірка", "Вилучення плат PCB >10 см²,\nдисплеїв, рідких кристалів"),
        ("Сортування фракцій", "Розділення кольорових металів,\nпластиків, вторинної сировини"),
        ("Звітність EPR", "Фіксація маси в системі WEEE,\nзакриття паспорта виробу"),
    ]
    cur_y = top_y + 55
    for title, desc in items4:
        frags.append(fitbox(x4 + 8, cur_y, col_w - 16, 75, f"{title}\n{desc}", size=11, pad=4, fill="#ffffff", stroke="#fca5a5", bold=False))
        cur_y += 85

    out_file = os.path.join(OUT_DIR, 'device-decommission-workflow.svg')
    render(out_file, w, h, *frags)


def make_fig_weee_material_recycling_stream():
    """Розподіл матеріальних потоків переробки електроніки згідно з вимогами WEEE 2012/19/EU."""
    w, h = 980, 520
    frags = []

    frags.append(text(w / 2, 28, "Матеріальні потоки селективної переробки електронних відходів (WEEE Annex VII)", size=15, bold=True))

    # Лівий блок: Вхідний пристрій
    x_in = 30
    y_in = 160
    w_in = 200
    h_in = 200
    frags.append(rect(x_in, y_in, w_in, h_in, fill="#f4f6f8", stroke=LINE, sw=2, rx=8))
    frags.append(rect(x_in, y_in, w_in, 40, fill="#e5e7eb", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(x_in + w_in / 2, y_in + 25, "Знятий пристрій (WEEE)", size=13, color=INK, bold=True))
    frags.append(mtext(x_in + w_in / 2, y_in + 75, ["Комплексний електронний", "виріб у зборі:", "• Корпус і кріплення", "• Li-Ion / LiFePO4 АКБ", "• Плати PCB з мікросхемами", "• Дисплейний модуль"], size=11, color=INK))

    # Центральний блок: Селективна розбірка
    x_mid = 290
    y_mid = 180
    w_mid = 210
    h_mid = 160
    frags.append(arrow(x_in + w_in, y_in + h_in / 2, x_mid, y_mid + h_mid / 2, color=MUTED, sw=2))
    frags.append(rect(x_mid, y_mid, w_mid, h_mid, fill="#eff6ff", stroke=NEG, sw=2, rx=8))
    frags.append(rect(x_mid, y_mid, w_mid, 38, fill="#dbeafe", stroke=NEG, sw=1.5, rx=8))
    frags.append(text(x_mid + w_mid / 2, y_mid + 24, "Селективна обробка", size=13, color=NEG, bold=True))
    frags.append(mtext(x_mid + w_mid / 2, y_mid + 70, ["Вимоги WEEE Annex VII:", "• Обов'язкове зняття АКБ", "• Сепарація плат >10 см²", "• Відокремлення РК-панелей", "• Демонтаж BFR-пластиків"], size=11, color=INK))

    # Праві вихідні потоки (4 штуки)
    x_out = 570
    w_out = 380
    h_out = 95
    y_out_start = 55
    y_gap = 18

    # Потік 1: Небезпечні відходи та АКБ
    y1 = y_out_start
    frags.append(arrow(x_mid + w_mid, y_mid + 20, x_out, y1 + h_out / 2, color=POS, sw=2))
    frags.append(rect(x_out, y1, w_out, h_out, fill="#fdf2f2", stroke=POS, sw=1.5, rx=6))
    frags.append(text(x_out + 12, y1 + 22, "1. Небезпечні субстанції та АКБ (EU 2023/1542)", size=12, color=POS, bold=True, anchor="start"))
    frags.append(mtext(x_out + 12, y1 + 45, ["• Li-Ion / LiFePO4 батареї, електроліти, ртутні перемикачі", "• Спеціалізована гідрометалургія: регенерація Li, Co, Ni", "• Повне запобігання термічному розгону та викидам HF"], size=10.5, color=INK, anchor="start"))

    # Потік 2: Друковані плати та дорогоцінні метали
    y2 = y1 + h_out + y_gap
    frags.append(arrow(x_mid + w_mid, y_mid + 55, x_out, y2 + h_out / 2, color="#d97706", sw=2))
    frags.append(rect(x_out, y2, w_out, h_out, fill="#fffbeb", stroke="#d97706", sw=1.5, rx=6))
    frags.append(text(x_out + 12, y2 + 22, "2. Друковані вузли PCB (Піро- та гідрометалургія)", size=12, color="#b45309", bold=True, anchor="start"))
    frags.append(mtext(x_out + 12, y2 + 45, ["• Вилучення дорогоцінних металів: Au, Ag, Pd, Pt", "• Регенерація мідної основи дорожок та олов'яного припою", "• Шлакування епоксидного склотекстоліту FR4"], size=10.5, color=INK, anchor="start"))

    # Потік 3: Полімери та корпусні матеріали
    y3 = y2 + h_out + y_gap
    frags.append(arrow(x_mid + w_mid, y_mid + 105, x_out, y3 + h_out / 2, color=FIELD, sw=2))
    frags.append(rect(x_out, y3, w_out, h_out, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(x_out + 12, y3 + 22, "3. Корпусні термопласти (RoHS-сумісні ABS, PC, PA)", size=12, color=FIELD, bold=True, anchor="start"))
    frags.append(mtext(x_out + 12, y3 + 45, ["• Оптична спектроскопічна сепарація (NIR / XRF)", "• Подрібнення у гранулят для вторинного лиття", "• Ізоляція фракцій із бромованими антипіренами (BFR)"], size=10.5, color=INK, anchor="start"))

    # Потік 4: Конструкційні метали
    y4 = y3 + h_out + y_gap
    frags.append(arrow(x_mid + w_mid, y_mid + 140, x_out, y4 + h_out / 2, color=MUTED, sw=2))
    frags.append(rect(x_out, y4, w_out, h_out, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=6))
    frags.append(text(x_out + 12, y4 + 22, "4. Конструкційні метали (Алюміній, сталь, мідь)", size=12, color=INK, bold=True, anchor="start"))
    frags.append(mtext(x_out + 12, y4 + 45, ["• Магнітна та вихрострумова (Eddy Current) сепарація", "• 100% переплавка радіаторів, шасі, екранів та кріплень", "• Мінімальний вуглецевий слід вторинного алюмінію"], size=10.5, color=INK, anchor="start"))

    out_file = os.path.join(OUT_DIR, 'weee-material-recycling-stream.svg')
    render(out_file, w, h, *frags)


if __name__ == '__main__':
    make_fig_device_decommission_workflow()
    make_fig_weee_material_recycling_stream()
    print("SVG figures generated successfully in img/")

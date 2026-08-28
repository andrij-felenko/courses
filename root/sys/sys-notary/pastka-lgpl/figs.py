# -*- coding: utf-8 -*-
"""Фігури теми «Пастка LGPL». Вивід — ./img/*.svg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)

REDFILL = "#fdecea"
GRNFILL = "#e7f6ec"
BLUFILL = "#eaf0fd"
AMBFILL = "#fef9e7"
AMBCOL  = "#d4ac0d"


# ── 1. Динамічне лінкування проти статичного в контексті LGPL ──────────────────
def fig_static_vs_dynamic():
    W, H = 1040, 480
    f = []

    # Заголовок лівої колонки: Десктоп / ОС із динамічним завантажувачем
    f.append(fitbox(40, 30, 450, 40, "Динамічне лінкування (ОС / POSIX / ld.so)", size=13, bold=True, fill=BLUFILL, stroke=NEG))

    # Схема динамічного: Пропрієтарний бінарник + окрема lib.so
    b_app, w_app, h_app = textbox(135, 150, "Пропрієтарний бінарник\n(ELF / Mach-O / PE)\n\n• Тільки виклики символів\n• Закритий код у бінарнику", size=11, fill=FILL, stroke=LINE, pad=8)
    f.append(b_app)

    b_so, w_so, h_so = textbox(405, 150, "Бібліотека LGPL\n(libcrypto.so / libav.so)\n\n• Окремий файл на диску\n• Динамічні таблиці PLT/GOT", size=11, fill=GRNFILL, stroke=FIELD, pad=8)
    f.append(b_so)

    f.append(arrow(135 + w_app / 2 + 4, 150, 230, 150, color=MUTED))
    f.append(text(270, 154, "Динамічний виклик", size=9, color=MUTED, anchor="middle"))
    f.append(arrow(310, 150, 405 - w_so / 2 - 4, 150, color=MUTED))

    b_dyn_action, _, _ = textbox(270, 270, "Механізм оновлення користувачем:\n\n1. Користувач компілює власну модифіковану версію libfoo.so\n2. Підміняє файл на диску або задає LD_LIBRARY_PATH\n3. Пропрієтарний бінарник підхоплює нову .so при запуску", size=11, fill=GRNFILL, stroke=FIELD, pad=10)
    f.append(b_dyn_action)

    b_dyn_status, _, _ = textbox(270, 395, "Статус виконання LGPLv2.1 §6 / LGPLv3 §4:\n\nПовна відповідність без розкриття пропрієтарного коду\nта без надання об'єктних файлів (.o)", size=11, fill=GRNFILL, stroke=FIELD, bold=True, pad=8)
    f.append(b_dyn_status)

    # Розділювальна лінія
    f.append(line(520, 20, 520, 460, color=LINE, sw=1.5, dash="4,4"))

    # Заголовок правої колонки: Bare-metal / RTOS моноліт
    f.append(fitbox(550, 30, 450, 40, "Статичне лінкування (Bare-metal / RTOS / MCU)", size=13, bold=True, fill=REDFILL, stroke=POS))

    # Схема статичного: Об'єднання .o + .a в єдиний flat binary
    b_mono, w_mono, h_mono = textbox(775, 150, "Єдиний монолітний образ (firmware.bin)\n\n┌──────────────────────┬──────────────────────┐\n│ Пропрієтарні .o      │ Бібліотека LGPL (.a) │\n│ (алгоритми, драйвери)│ (mbedtls, ffmpeg)    │\n└──────────────────────┴──────────────────────┘\nУсі символи та адреси жорстко зв'язані лінкером", size=11, fill=FILL, stroke=POS, pad=10)
    f.append(b_mono)

    b_stat_action, _, _ = textbox(775, 270, "Вимога LGPL для монолітного образу:\n\nОскільки підміна .so неможлива, вендор ЗОБОВ'ЯЗАНИЙ надати:\n• Усі пропрієтарні об'єктні файли (.o) або вихідний код\n• Скрипти лінкування (.ld), Makefile та версію toolchain\n• Інструкцію для повторного збирання firmware.bin", size=11, fill=REDFILL, stroke=POS, pad=10)
    f.append(b_stat_action)

    b_stat_status, _, _ = textbox(775, 395, "Пастка вендора:\n\nРозкриття .o файлів відкриває структури даних, назви функцій,\nалгоритми для декомпіляції та ламає комерційну таємницю", size=11, fill=REDFILL, stroke=POS, bold=True, pad=8)
    f.append(b_stat_status)

    render(out("static-vs-dynamic-lgpl.svg"), W, H, *f,
           title="Порівняння динамічного та статичного лінкування в контексті зобов'язань LGPL")


# ── 2. Анатомія пастки перелінкування ──────────────────────────────────────────
def fig_embedded_relink_trap():
    W, H = 1040, 430
    f = []

    # Крок 1: Збирання прошивки на заводі
    b1, w1, h1 = textbox(160, 110, "1. Збирання прошивки\n\n• proprietary_main.o\n• motor_control.o\n• liblgpl_codec.a (LGPL)\n  ↓ (ld / arm-none-eabi-gcc)\n  firmware.bin", size=11, fill=FILL, stroke=LINE, pad=8)
    f.append(b1)

    # Крок 2: Прошивання пристрою та продаж
    b2, w2, h2 = textbox(450, 110, "2. Продаж пристрою\n\n• Прошивка записана у Flash\n• Secure Boot активний\n• Пристрій передано клієнту", size=11, fill=AMBFILL, stroke=AMBCOL, pad=8)
    f.append(b2)

    # Крок 3: Юридичний запит клієнта
    b3, w3, h3 = textbox(770, 110, "3. Запит користувача\n\n«Я бажаю модифікувати LGPL-код\nта перелінкувати прошивку\nзгідно з LGPLv2.1 §6 / LGPLv3 §4»", size=11, fill=BLUFILL, stroke=NEG, pad=8)
    f.append(b3)

    f.append(arrow(160 + w1 / 2 + 4, 110, 450 - w2 / 2 - 6, 110))
    f.append(arrow(450 + w2 / 2 + 4, 110, 770 - w3 / 2 - 6, 110))

    # Нижня частина: Розгалуження наслідків для вендора
    f.append(line(770, 110 + h3 / 2, 770, 230, color=POS, sw=1.5))
    f.append(arrow(770, 230, 480, 280, color=POS))
    f.append(arrow(770, 230, 800, 280, color=POS))

    b_res_fail, _, _ = textbox(300, 340, "Варіант А: Відмова надати .o файли\n\n• Порушення умов ліцензії LGPL\n• Автоматичне анулювання ліцензії\n• Судовий позов за порушення авторських прав\n• Заборона на імпорт та продаж пристрою", size=11, fill=REDFILL, stroke=POS, pad=10)
    f.append(b_res_fail)

    b_res_pass, _, _ = textbox(770, 340, "Варіант Б: Надання .o файлів та скриптів\n\n• Витік комерційної таємниці (декомпіляція .o)\n• Вимога дати ключі прошивання (LGPLv3)\n• Зобов'язання підтримувати toolchain роками\n• Ризик зламу апаратного захисту пристрою", size=11, fill=REDFILL, stroke=POS, pad=10)
    f.append(b_res_pass)

    render(out("embedded-relink-trap.svg"), W, H, *f,
           title="Анатомія пастки LGPL у вбудованих пристроях: вибір між витоком коду та судовим позовом")


# ── 3. Архітектурні моделі уникнення пастки ────────────────────────────────────
def fig_isolation_architectures():
    W, H = 1040, 460
    f = []

    # Схема 1: Ізоляція через IPC / Процеси
    f.append(fitbox(30, 30, 300, 40, "Патерн 1: Ізоляція через IPC", size=12, bold=True, fill=BLUFILL, stroke=NEG))

    b1_app, _, _ = textbox(180, 130, "Пропрієтарний процес\n(Керування, алгоритми)", size=11, fill=FILL, stroke=LINE, pad=8)
    f.append(b1_app)

    f.append(line(180, 160, 180, 210, color=MUTED, sw=1.5, dash="3,3"))
    f.append(fitbox(80, 180, 200, 30, "IPC / Sockets / UART / SPI", size=10, fill=AMBFILL, stroke=AMBCOL))

    b1_lgpl, _, _ = textbox(180, 260, "Окремий процес LGPL\n(Кодек, мережевий стек)", size=11, fill=GRNFILL, stroke=FIELD, pad=8)
    f.append(b1_lgpl)

    b1_desc, _, _ = textbox(180, 370, "Властивості:\n• Незалежні адресні простори\n• Відкритий протокол обміну\n• LGPL не заражає сусідній процес", size=11, fill=GRNFILL, stroke=FIELD, pad=8)
    f.append(b1_desc)

    # Схема 2: Динамічний модуль / ELF loader на MCU
    f.append(fitbox(370, 30, 300, 40, "Патерн 2: Модульний завантажувач", size=12, bold=True, fill=BLUFILL, stroke=NEG))

    b2_app, _, _ = textbox(520, 130, "Пропрієтарна прошивка\nТаблиця стрибків (Jump Table)", size=11, fill=FILL, stroke=LINE, pad=8)
    f.append(b2_app)

    f.append(arrow(520, 165, 520, 220, color=FIELD))
    f.append(text(532, 195, "Виклик за адресою", size=10, color=FIELD, anchor="start"))

    b2_mod, _, _ = textbox(520, 260, "LGPL-модуль у Flash\n(Окремий сектор пам'яті)", size=11, fill=GRNFILL, stroke=FIELD, pad=8)
    f.append(b2_mod)

    b2_desc, _, _ = textbox(520, 370, "Властивості:\n• Незалежне прошивання сектора\n• Користувач може оновити модуль\n• Пропрієтарний код лишається закритим", size=11, fill=GRNFILL, stroke=FIELD, pad=8)
    f.append(b2_desc)

    # Схема 3: Заміна бібліотеки або комерційна ліцензія
    f.append(fitbox(710, 30, 300, 40, "Патерн 3: Чиста заміна або Dual-License", size=12, bold=True, fill=BLUFILL, stroke=NEG))

    b3_sub, _, _ = textbox(860, 130, "Дозвільні аналоги:\n• mbedTLS (Apache 2.0)\n• lwIP (BSD-3-Clause)\n• miniz (MIT)", size=11, fill=GRNFILL, stroke=FIELD, pad=8)
    f.append(b3_sub)

    b3_dual, _, _ = textbox(860, 260, "Комерційна ліцензія:\n• Викуп у правовласника\n• Скасування умов LGPL\n• Повна свобода лінкування", size=11, fill=AMBFILL, stroke=AMBCOL, pad=8)
    f.append(b3_dual)

    b3_desc, _, _ = textbox(860, 370, "Властивості:\n• Нульові копілефтні зобов'язання\n• Можливе статичне лінкування\n• Повний захист комерційної таємниці", size=11, fill=GRNFILL, stroke=FIELD, pad=8)
    f.append(b3_desc)

    render(out("isolation-architectures.svg"), W, H, *f,
           title="Архітектурні патерни безпечного використання або заміни LGPL-компонентів")


if __name__ == "__main__":
    fig_static_vs_dynamic()
    fig_embedded_relink_trap()
    fig_isolation_architectures()
    print("All figures generated successfully.")

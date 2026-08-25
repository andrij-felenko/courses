# -*- coding: utf-8 -*-
"""Генерація SVG-діаграм для теми «Модель застосунку Android: маніфест, дозволи, наміри»."""

import os
import sys

# scripts/ знаходиться на 4 рівні вище: book/programming/client-architecture/android-app-model -> ../../../..
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts")))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_android_sandbox_binder():
    """Діаграма 1: Ізоляція процесів (UID Sandbox) та зв'язок через Binder IPC."""
    W, H = 840, 430
    p = []

    # Фон простору користувача (User Space)
    p.append(rect(15, 15, 810, 245, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    p.append(text(140, 38, "Простір користувача (User Space)", size=13, color=MUTED, bold=True))

    # Процес A (Клієнт)
    p.append(rect(35, 55, 230, 185, fill="#eff6ff", stroke=NEG, sw=1.8, rx=6))
    p.append(text(150, 78, "Процес A: Клієнт", size=13, color=NEG, bold=True))
    p.append(text(150, 96, "UID: 10045 (u0_a45)", size=11, color=MUTED))
    p.append(rect(50, 115, 200, 42, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=4))
    p.append(text(150, 133, "Activity / Component", size=12, color=INK, bold=True))
    p.append(text(150, 148, "/data/data/com.app.a", size=10, color=MUTED))
    p.append(rect(50, 170, 200, 55, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=4))
    p.append(text(150, 190, "libbinder / Binder Proxy", size=11, color=INK))
    p.append(text(150, 208, "transact(CODE, data, reply)", size=10, color=MUTED))

    # Процес B (Сервер застосунку)
    p.append(rect(575, 55, 230, 185, fill="#eff6ff", stroke=NEG, sw=1.8, rx=6))
    p.append(text(690, 78, "Процес B: Служба", size=13, color=NEG, bold=True))
    p.append(text(690, 96, "UID: 10082 (u0_a82)", size=11, color=MUTED))
    p.append(rect(590, 115, 200, 42, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=4))
    p.append(text(690, 133, "Service / Component", size=12, color=INK, bold=True))
    p.append(text(690, 148, "/data/data/com.app.b", size=10, color=MUTED))
    p.append(rect(590, 170, 200, 55, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=4))
    p.append(text(690, 190, "Binder Stub / BBinder", size=11, color=INK))
    p.append(text(690, 208, "onTransact(CODE, data, reply)", size=10, color=MUTED))

    # System Server (Центральний координатор)
    p.append(rect(295, 55, 250, 185, fill="#fdf4ff", stroke="#a855f7", sw=1.8, rx=6))
    p.append(text(420, 78, "System Server (OS)", size=13, color="#7e22ce", bold=True))
    p.append(text(420, 96, "UID: 1000 (system)", size=11, color=MUTED))
    p.append(rect(310, 115, 220, 50, fill="#ffffff", stroke="#e9d5ff", sw=1.2, rx=4))
    p.append(text(420, 135, "ActivityTaskManager (ATMS)", size=11, color=INK, bold=True))
    p.append(text(420, 152, "PackageManagerService (PKMS)", size=10, color=MUTED))
    p.append(rect(310, 175, 220, 50, fill="#ffffff", stroke="#e9d5ff", sw=1.2, rx=4))
    p.append(text(420, 195, "ServiceManager / Context", size=11, color=INK))
    p.append(text(420, 212, "Контроль дозволів і прав", size=10, color=MUTED))

    # Фон простору ядра (Kernel Space)
    p.append(rect(15, 275, 810, 140, fill="#fef2f2", stroke=POS, sw=1.5, rx=8))
    p.append(text(145, 298, "Простір ядра Linux (Kernel Space)", size=13, color=POS, bold=True))

    # Драйвер /dev/binder
    p.append(rect(35, 315, 770, 85, fill="#ffffff", stroke=POS, sw=1.8, rx=6))
    p.append(text(420, 336, "Драйвер /dev/binder (IPC Транспорт)", size=13, color=POS, bold=True))
    p.append(text(420, 354, "Спільна сторінкова пам'ять (mmap) · Буфер транзакцій (~1 МБ на процес)", size=11, color=INK))
    p.append(text(420, 376, "Автентифікація ядра: binder_get_calling_uid() та binder_get_calling_pid() (неможливо підробити)", size=10.5, color=MUTED))

    # Стрілки IPC викликів між просторами
    p.append(arrow(150, 225, 150, 315, color=NEG, sw=1.6))
    p.append(arrow(420, 225, 420, 315, color="#7e22ce", sw=1.6))
    p.append(arrow(690, 315, 690, 225, color=POS, sw=1.6))

    # Підписи на стрілках
    p.append(text(95, 255, "ioctl(BINDER_WRITE_READ)", size=9.5, color=NEG, anchor="middle"))
    p.append(text(480, 255, "Перевірка UID/дозволу", size=9.5, color="#7e22ce", anchor="middle"))
    p.append(text(745, 255, "Вручення виклику", size=9.5, color=POS, anchor="middle"))

    render(os.path.join(OUT, "android-sandbox-binder.svg"), W, H, *p)


def fig_activity_lifecycle_process_death():
    """Діаграма 2: Скінченний автомат життєвого циклу Activity та відновлення після смерті процесу."""
    W, H = 820, 460
    p = []

    # Головні стани життєвого циклу
    states = [
        (410, 45, "Не існує (Dead / Not Created)", 220, 34, "#f1f5f9", LINE),
        (410, 115, "Створено (Created)", 180, 34, "#eff6ff", NEG),
        (410, 185, "Запущено (Started - Видимо)", 210, 34, "#eff6ff", NEG),
        (410, 260, "Активно (Resumed / Focused)", 220, 38, "#dcfce7", FIELD),
        (410, 340, "Призупинено (Paused)", 200, 34, "#fef9c3", "#ca8a04"),
        (410, 415, "Зупинено (Stopped - Фоновий)", 210, 34, "#fee2e2", POS),
    ]

    for cx, cy, title, w, h, fill, stroke in states:
        p.append(rect(cx - w / 2, cy - h / 2, w, h, fill=fill, stroke=stroke, sw=1.6, rx=6))
        p.append(text(cx, cy + 4, title, size=11.5, color=INK, bold=True))

    # Стрілки прямих переходів (Створення -> Активність)
    p.append(arrow(410, 62, 410, 98, color=LINE, sw=1.5))
    p.append(text(470, 83, "onCreate()", size=10, color=NEG, bold=True))

    p.append(arrow(410, 132, 410, 168, color=LINE, sw=1.5))
    p.append(text(465, 153, "onStart()", size=10, color=NEG, bold=True))

    p.append(arrow(410, 202, 410, 241, color=LINE, sw=1.5))
    p.append(text(472, 224, "onResume()", size=10, color=FIELD, bold=True))

    # Прямі переходи вниз (Втрата фокусу -> Зупинка)
    p.append(arrow(410, 279, 410, 323, color=LINE, sw=1.5))
    p.append(text(468, 304, "onPause()", size=10, color="#ca8a04", bold=True))

    p.append(arrow(410, 357, 410, 398, color=LINE, sw=1.5))
    p.append(text(465, 380, "onStop()", size=10, color=POS, bold=True))

    # Зворотні переходи (Paused -> Resumed, Stopped -> Started)
    # Зворотний loop Paused -> Resumed
    p.append(line(310, 340, 260, 340, color=LINE, sw=1.3))
    p.append(line(260, 340, 260, 260, color=LINE, sw=1.3))
    p.append(arrow(260, 260, 300, 260, color=LINE, sw=1.3))
    p.append(text(210, 300, "onResume()", size=9.5, color=FIELD, bold=True))

    # Зворотний loop Stopped -> Started
    p.append(line(305, 415, 200, 415, color=LINE, sw=1.3))
    p.append(line(200, 415, 200, 185, color=LINE, sw=1.3))
    p.append(arrow(200, 185, 305, 185, color=LINE, sw=1.3))
    p.append(text(145, 290, "onRestart() → onStart()", size=9.5, color=NEG, bold=True))

    # Знищення Activity через onDestroy()
    p.append(line(515, 415, 620, 415, color=LINE, sw=1.3))
    p.append(line(620, 415, 620, 45, color=LINE, sw=1.3))
    p.append(arrow(620, 45, 520, 45, color=LINE, sw=1.3))
    p.append(text(675, 230, "onDestroy() (штатне закриття)", size=9.5, color=MUTED))

    # Блок смерті процесу (Low Memory Killer)
    p.append(rect(610, 300, 195, 130, fill="#fff1f2", stroke=POS, sw=1.6, rx=6))
    p.append(text(707, 320, "Смерть процесу (LMK)", size=11, color=POS, bold=True))
    p.append(text(707, 338, "Ядро вбиває фоновий процес", size=9.5, color=INK))
    p.append(text(707, 355, "Пам'ять RAM звільняється", size=9.5, color=MUTED))
    p.append(text(707, 372, "ViewModel ЗНИЩУЄТЬСЯ", size=9.5, color=POS, bold=True))
    p.append(text(707, 390, "Зберігається лише Bundle", size=9.5, color=INK))
    p.append(text(707, 408, "через onSaveInstanceState()", size=9.5, color=MUTED))

    # Стрілка від Stopped до смерті процесу
    p.append(line(515, 415, 595, 375, color=POS, sw=1.5, dash="4,3"))
    p.append(arrow(595, 375, 610, 368, color=POS, sw=1.5))

    # Стрілка відродження зі збереженого стану
    p.append(line(707, 300, 707, 25, color=FIELD, sw=1.5, dash="4,3"))
    p.append(line(707, 25, 430, 25, color=FIELD, sw=1.5, dash="4,3"))
    p.append(arrow(430, 25, 410, 28, color=FIELD, sw=1.5))
    p.append(text(560, 18, "Відродження: onCreate(savedInstanceState)", size=9.5, color=FIELD, bold=True))

    render(os.path.join(OUT, "activity-lifecycle-process-death.svg"), W, H, *p)


def fig_intent_resolution_flow():
    """Діаграма 3: Алгоритм резолюції намірів (Intent Resolution Flow)."""
    W, H = 840, 380
    p = []

    # Ліва колонка: Вхідний намір (Intent)
    p.append(rect(20, 45, 230, 290, fill="#eff6ff", stroke=NEG, sw=1.8, rx=6))
    p.append(text(135, 70, "Вхідний Intent (Намір)", size=13, color=NEG, bold=True))

    p.append(rect(35, 90, 200, 45, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=4))
    p.append(text(135, 108, "Явний (Explicit)", size=11, color=INK, bold=True))
    p.append(text(135, 124, "Вказано точний ComponentName", size=9.5, color=MUTED))

    p.append(rect(35, 145, 200, 175, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=4))
    p.append(text(135, 163, "Неявний (Implicit)", size=11, color=INK, bold=True))
    p.append(text(135, 182, "Action: android.intent.action.VIEW", size=9.5, color=INK))
    p.append(text(135, 200, "Data: https://example.com/item/42", size=9.5, color=INK))
    p.append(text(135, 218, "Type (MIME): text/html", size=9.5, color=INK))
    p.append(text(135, 236, "Category: CATEGORY_DEFAULT", size=9.5, color=INK))
    p.append(text(135, 256, "Extras: Bundle (Parcelable)", size=9.5, color=MUTED))
    p.append(text(135, 274, "Flags: FLAG_ACTIVITY_NEW_TASK", size=9.5, color=MUTED))
    p.append(text(135, 292, "Package / ClipData", size=9.5, color=MUTED))

    # Центральна колонка: PackageManagerService та фільтрація
    p.append(rect(285, 45, 270, 290, fill="#fdf4ff", stroke="#a855f7", sw=1.8, rx=6))
    p.append(text(420, 70, "PackageManagerService (PKMS)", size=12.5, color="#7e22ce", bold=True))
    p.append(text(420, 88, "Алгоритм резолюції фільтрів", size=10.5, color=MUTED))

    # Кроки фільтрації
    steps = [
        (110, "1. Звіряння Action", "Повинен збігатися з <action> у фільтрі"),
        (160, "2. Звіряння Data / MIME", "Схема (https, geo), хост, шлях і MIME-тип"),
        (210, "3. Звіряння Category", "Усі категорії Intent мусять бути у фільтрі"),
        (260, "4. Перевірка безпеки", "Exported=true або збіг підпису/UID"),
    ]

    for y, title, desc in steps:
        p.append(rect(300, y, 240, 42, fill="#ffffff", stroke="#e9d5ff", sw=1.2, rx=4))
        p.append(text(420, y + 16, title, size=10.5, color=INK, bold=True))
        p.append(text(420, y + 32, desc, size=9.5, color=MUTED))

    # Права колонка: Результати доставки
    p.append(rect(590, 45, 230, 290, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(705, 70, "Цільова активація", size=13, color=FIELD, bold=True))

    p.append(rect(605, 95, 200, 65, fill="#ffffff", stroke="#bbf7d0", sw=1.2, rx=4))
    p.append(text(705, 115, "Прямий запуск", size=11, color=FIELD, bold=True))
    p.append(text(705, 132, "Для явного наміру або", size=9.5, color=INK))
    p.append(text(705, 148, "якщо знайдено 1 компонент", size=9.5, color=MUTED))

    p.append(rect(605, 175, 200, 70, fill="#ffffff", stroke="#bbf7d0", sw=1.2, rx=4))
    p.append(text(705, 195, "Системний вибір (Chooser)", size=11, color="#ca8a04", bold=True))
    p.append(text(705, 213, "Якщо збіглося >1 застосунків", size=9.5, color=INK))
    p.append(text(705, 230, "Діалог вибору користувача", size=9.5, color=MUTED))

    p.append(rect(605, 260, 200, 60, fill="#ffffff", stroke="#bbf7d0", sw=1.2, rx=4))
    p.append(text(705, 280, "ActivityNotFoundException", size=10.5, color=POS, bold=True))
    p.append(text(705, 298, "Якщо збігів 0 або заборонено", size=9.5, color=MUTED))

    # Стрілки переходу
    # Прямий перехід від Explicit до Прямий запуск
    p.append(line(235, 112, 260, 112, color=NEG, sw=1.5))
    p.append(line(260, 112, 260, 28, color=NEG, sw=1.5))
    p.append(line(260, 28, 570, 28, color=NEG, sw=1.5))
    p.append(line(570, 28, 570, 125, color=NEG, sw=1.5))
    p.append(arrow(570, 125, 605, 125, color=NEG, sw=1.5))
    p.append(text(415, 22, "Явний намір оминає фільтрацію PKMS", size=9, color=NEG, bold=True))

    # Від Implicit до PKMS
    p.append(arrow(235, 215, 285, 215, color="#7e22ce", sw=1.6))

    # Від PKMS до результатів
    p.append(arrow(555, 130, 605, 130, color=FIELD, sw=1.5))
    p.append(arrow(555, 210, 605, 210, color="#ca8a04", sw=1.5))
    p.append(arrow(555, 290, 605, 290, color=POS, sw=1.5))

    render(os.path.join(OUT, "intent-resolution-flow.svg"), W, H, *p)


if __name__ == "__main__":
    fig_android_sandbox_binder()
    fig_activity_lifecycle_process_death()
    fig_intent_resolution_flow()
    print("All figures generated successfully.")

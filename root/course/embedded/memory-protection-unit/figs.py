# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_mpu_architecture():
    w, h = 980, 520
    frags = []

    # 1. Заголовок і фон
    frags.append(rect(10, 10, 960, 500, fill="#ffffff", stroke="#d1d5db", sw=1.5, rx=8))

    # Ліва колонка: Ядро процесора Cortex-M
    frags.append(rect(30, 40, 240, 440, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=6))
    frags.append(text(150, 68, "Процесорне ядро Cortex-M", size=14, bold=True, color="#0f172a"))

    frags.append(fitbox(45, 90, 210, 55, "Конвеєр виконання\n(Instruction Pipeline)", size=12, fill="#ffffff", stroke="#94a3b8"))
    frags.append(fitbox(45, 155, 210, 55, "Регістри режиму доступу\n(CONTROL.nPRIV, IPSR)", size=12, fill="#ffffff", stroke="#94a3b8"))
    frags.append(fitbox(45, 220, 210, 55, "Блок вибірки інструкцій\n(Instruction Fetch Unit)", size=12, fill="#ffffff", stroke="#94a3b8"))
    frags.append(fitbox(45, 285, 210, 55, "Блок завантаження / запису\n(Load / Store Unit - LSU)", size=12, fill="#ffffff", stroke="#94a3b8"))
    frags.append(fitbox(45, 360, 210, 100, "Векторний контролер\nпереривань NVIC / SCB\n(Обробка винятків)", size=12, fill="#fef2f2", stroke="#ef4444"))

    # Центральна колонка: Блок захисту пам'яті (MPU)
    frags.append(rect(320, 40, 340, 440, fill="#eff6ff", stroke="#3b82f6", sw=1.8, rx=6))
    frags.append(text(490, 68, "Блок захисту пам'яті (MPU)", size=15, bold=True, color="#1e3a8a"))

    frags.append(fitbox(340, 90, 300, 45, "Керування MPU (MPU_CTRL, MPU_TYPE)\nENABLE / HFNMIENA / PRIVDEFENA", size=11, fill="#ffffff", stroke="#60a5fa"))
    frags.append(fitbox(340, 145, 300, 120, "Банк компараторів регіонів (0..N)\n- Порівняння базової адреси та ліміту\n- Оцінка прав доступу (AP: Priv / Unpriv)\n- Перевірка виконання коду (XN)\n- Пріоритет перекриття номерів", size=11, fill="#ffffff", stroke="#60a5fa"))
    frags.append(fitbox(340, 275, 300, 65, "Генератор атрибутів пам'яті\n(Normal / Device, Кешованість,\nВпорядкування операцій)", size=11, fill="#ffffff", stroke="#60a5fa"))
    frags.append(fitbox(340, 360, 300, 100, "Логіка фіксації порушень\n- Формування винятку MemManage\n- Запис бітів помилки в SCB->CFSR\n- Фіксація адреси в SCB->MMFAR", size=11, fill="#fee2e2", stroke="#dc2626"))

    # Права колонка: Шинна матриця та фізична пам'ять
    frags.append(rect(710, 40, 240, 440, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=6))
    frags.append(text(830, 68, "Шинна матриця та адреси", size=14, bold=True, color="#0f172a"))

    frags.append(fitbox(725, 90, 210, 45, "Системна шина AHB / AXI\n(Транзакція без затримок)", size=11, fill="#ffffff", stroke="#94a3b8"))
    frags.append(fitbox(725, 150, 210, 60, "Flash-пам'ять (Код / Конст)\n0x08000000 (Priv RO / Unpriv RO)", size=11, fill="#f0fdf4", stroke="#22c55e"))
    frags.append(fitbox(725, 220, 210, 60, "SRAM (Стек, Купа, Дані)\n0x20000000 (RW / Ізоляція)", size=11, fill="#f0fdf4", stroke="#22c55e"))
    frags.append(fitbox(725, 290, 210, 60, "Периферія MMIO\n0x40000000 (Device / XN)", size=11, fill="#fefce8", stroke="#eab308"))
    frags.append(fitbox(725, 360, 210, 100, "Системні регістри ядра PPB\n0xE0000000 (NVIC, SCB, MPU)\nТільки Privileged доступ", size=11, fill="#f1f5f9", stroke="#64748b"))

    # Зв'язки (Стрілки)
    # 1. Від процесора до MPU (Адреса + Режим доступу)
    frags.append(arrow(270, 200, 320, 200, color="#2563eb", sw=2))
    frags.append(text(295, 190, "Адреса", size=10, color="#1e40af", bold=True))

    # 2. Від MPU до пам'яті (Дозволений доступ)
    frags.append(arrow(660, 200, 710, 200, color="#16a34a", sw=2))
    frags.append(text(685, 190, "OK", size=10, color="#15803d", bold=True))

    # 3. Від MPU до NVIC/SCB (Порушення MemManage)
    frags.append(arrow(340, 410, 255, 410, color="#dc2626", sw=2))
    frags.append(text(297, 400, "Fault", size=10, color="#b91c1c", bold=True))

    # 4. Зворотний зв'язок: NVIC зупиняє або переводить ядро в обробник
    frags.append(arrow(150, 360, 150, 340, color="#dc2626", sw=1.8))

    render(os.path.join(OUT, "mpu-architecture.svg"), w, h, *frags)


def fig_pmsav7_vs_pmsav8():
    w, h = 980, 520
    frags = []

    frags.append(rect(10, 10, 960, 500, fill="#ffffff", stroke="#d1d5db", sw=1.5, rx=8))

    # Ліва колонка: PMSAv7 (ARMv7-M: Cortex-M3 / M4 / M7)
    frags.append(rect(25, 35, 455, 455, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=6))
    frags.append(text(252, 65, "Архітектура PMSAv7 (ARMv7-M)", size=15, bold=True, color="#0f172a"))
    frags.append(text(252, 85, "Cortex-M3 / M4 / M7", size=12, color="#64748b"))

    frags.append(fitbox(45, 105, 415, 65, "Розмір регіону: Ступінь двійки 2^N\nМінімум 32 байти, максимум 4 Гігабайти\n(32B, 64B, 128B, 256B ... 512KB, 1MB, 4GB)", size=11, fill="#ffffff", stroke="#cbd5e1"))
    frags.append(fitbox(45, 180, 415, 65, "Суворе вирівнювання адреси:\nБазова адреса мусить бути кратною розміру!\nПриклад: регіон 64 КБ має починатися з 0x...0000", size=11, fill="#ffffff", stroke="#cbd5e1"))
    frags.append(fitbox(45, 255, 415, 75, "Субрегіони (Subregion Disable - SRD):\n8 рівних частин (розмір / 8) для регіонів >= 256 байт.\nМаска 8 біт у MPU_RASR дозволяє вимикати окремі 1/8 частини.", size=11, fill="#ffffff", stroke="#cbd5e1"))
    frags.append(fitbox(45, 340, 415, 65, "Пріоритет перекриття (Overlap Priority):\nПри збігу кількох регіонів перемагає регіон\nіз найвищим числовим номером (регіон 7 > регіон 0).", size=11, fill="#ffffff", stroke="#cbd5e1"))
    frags.append(fitbox(45, 415, 415, 60, "Регістри: MPU_RBAR (База + індекс) та\nMPU_RASR (Розмір, SRD, права AP, атрибути TEX/C/B, XN)", size=11, fill="#eff6ff", stroke="#3b82f6"))

    # Права колонка: PMSAv8 (ARMv8-M: Cortex-M23 / M33 / M55 / M85)
    frags.append(rect(500, 35, 455, 455, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=6))
    frags.append(text(727, 65, "Архітектура PMSAv8 (ARMv8-M)", size=15, bold=True, color="#14532d"))
    frags.append(text(727, 85, "Cortex-M23 / M33 / M55 / M85", size=12, color="#16a34a"))

    frags.append(fitbox(520, 105, 415, 65, "Довільний розмір із кроком 32 байти:\nНемає обмеження степенем двійки!\nБудь-який блок пам'яті захищається точно за розміром.", size=11, fill="#ffffff", stroke="#86efac"))
    frags.append(fitbox(520, 180, 415, 65, "Гнучке вирівнювання (32-byte Alignment):\nБаза (Base) та Ліміт (Limit) вирівнюються на 32 байти.\nРозмір = (LimitAddress - BaseAddress) + 32 байти.", size=11, fill="#ffffff", stroke="#86efac"))
    frags.append(fitbox(520, 255, 415, 75, "Відсутність субрегіонів (No SRD):\nНемає потреби у фрагментації та масці SRD,\nоскільки межі задаються точно через Base та Limit.", size=11, fill="#ffffff", stroke="#86efac"))
    frags.append(fitbox(520, 340, 415, 65, "Заборона конфліктного перекриття:\nПерекриття з різними атрибутами заборонено.\nСпрощена й надійна апаратна перевірка без колізій.", size=11, fill="#ffffff", stroke="#86efac"))
    frags.append(fitbox(520, 415, 415, 60, "Регістри: MPU_RBAR (Base, AP, XN, SH) та MPU_RLAR (Limit, Enable, AttrIndx) + MPU_MAIR0/1 (Непрямі атрибути).", size=11, fill="#ecfdf5", stroke="#10b981"))

    render(os.path.join(OUT, "pmsav7-vs-pmsav8-regions.svg"), w, h, *frags)


def fig_stack_guard_and_isolation():
    w, h = 980, 530
    frags = []

    frags.append(rect(10, 10, 960, 510, fill="#ffffff", stroke="#d1d5db", sw=1.5, rx=8))

    # Спільний простір пам'яті (Зліва)
    frags.append(rect(30, 40, 280, 460, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=6))
    frags.append(text(170, 65, "Глобальна системна карта", size=14, bold=True, color="#0f172a"))

    frags.append(fitbox(45, 85, 250, 65, "Регіон 0: Flash (Код та константи)\n0x08000000 - 0x08080000 (512 КБ)\nPrivileged RO / Unprivileged RO\nВиконання дозволено (XN = 0)", size=11, fill="#f0fdf4", stroke="#22c55e"))
    frags.append(fitbox(45, 160, 250, 65, "Регіон 1: Ядро RTOS та ОС Дані\n0x20000000 - 0x20004000 (16 КБ)\nPrivileged RW / Unprivileged No Access\nВиконання заборонено (XN = 1)", size=11, fill="#fef2f2", stroke="#ef4444"))
    frags.append(fitbox(45, 235, 250, 65, "Регіон 2: Периферійний простір MMIO\n0x40000000 - 0x5FFFFFFF (512 МБ)\nPrivileged RW / Unprivileged No Access\nТип: Device Memory, XN = 1", size=11, fill="#fefce8", stroke="#eab308"))
    frags.append(fitbox(45, 310, 250, 65, "Регіон 3: Захист нульового покажчика\n0x00000000 - 0x0000001F (32 байти)\nNo Access (Всі рівні)\nМиттєвий перехоплювач NULL Pointer", size=11, fill="#fee2e2", stroke="#dc2626"))
    frags.append(fitbox(45, 385, 250, 100, "Регіон 4: Системний стек ядра MSP\n0x2001F000 - 0x20020000 (4 КБ)\nЗахисна смуга MSP Guard Band\n0x2001EFE0 (32 байти No Access)", size=11, fill="#f1f5f9", stroke="#64748b"))

    # Карта задачі 1 (По центру)
    frags.append(rect(340, 40, 290, 460, fill="#eff6ff", stroke="#3b82f6", sw=1.8, rx=6))
    frags.append(text(485, 65, "Задача 1 (Критичний контур)", size=14, bold=True, color="#1e3a8a"))

    frags.append(fitbox(355, 85, 260, 60, "Регіон 5: Приватні дані Задачі 1\n0x20004000 - 0x20005000 (4 КБ)\nUnprivileged RW, XN = 1", size=11, fill="#ffffff", stroke="#60a5fa"))
    frags.append(fitbox(355, 155, 260, 110, "Регіон 6: Стек Задачі 1 (PSP)\n0x20005040 - 0x20006000 (~4 КБ)\nUnprivileged RW, XN = 1\nСтек росте вниз (<- SP)\nНормальна робоча зона", size=11, fill="#ffffff", stroke="#60a5fa"))
    frags.append(fitbox(355, 275, 260, 65, "Регіон 7: Захисна смуга стека 1\n0x20005000 - 0x2000503F (64 байти)\nNo Access (Unprivileged / Privileged)\nВиявлення переповнення стека", size=11, fill="#fee2e2", stroke="#dc2626"))
    frags.append(fitbox(355, 350, 260, 135, "Ізоляція від інших задач:\n- Доступ до Задачі 2: ЗАБОРОНЕНО\n- Доступ до регістрів NVIC: ЗАБОРОНЕНО\n- Доступ до пам'яті ядра: ЗАБОРОНЕНО\nБудь-яка несанкціонована спроба\nгенерує виняток MemManage!", size=11, fill="#f8fafc", stroke="#94a3b8"))

    # Карта задачі 2 (Справа)
    frags.append(rect(660, 40, 290, 460, fill="#fdf4ff", stroke="#a855f7", sw=1.5, rx=6))
    frags.append(text(805, 65, "Задача 2 (Мережевий стек)", size=14, bold=True, color="#581c87"))

    frags.append(fitbox(675, 85, 260, 60, "Регіон 5: Приватні дані Задачі 2\n0x20006000 - 0x20008000 (8 КБ)\nUnprivileged RW, XN = 1", size=11, fill="#ffffff", stroke="#c084fc"))
    frags.append(fitbox(675, 155, 260, 110, "Регіон 6: Стек Задачі 2 (PSP)\n0x20008040 - 0x20009000 (~4 КБ)\nUnprivileged RW, XN = 1\nСтек росте вниз (<- SP)\nНормальна робоча зона", size=11, fill="#ffffff", stroke="#c084fc"))
    frags.append(fitbox(675, 275, 260, 65, "Регіон 7: Захисна смуга стека 2\n0x20008000 - 0x2000803F (64 байти)\nNo Access (Unprivileged / Privileged)\nВиявлення переповнення стека", size=11, fill="#fee2e2", stroke="#dc2626"))
    frags.append(fitbox(675, 350, 260, 135, "Динамічне перемикання (PendSV):\nПід час перемикання контексту\nядро RTOS перезаписує Регіони 5, 6, 7\nзначеннями нової задачі за 30-40 тактів\nіз бар'єрами __DSB() та __ISB().", size=11, fill="#f8fafc", stroke="#94a3b8"))

    # Стрілка динамічного перемикання між задачами
    frags.append(arrow(630, 200, 660, 200, color="#9333ea", sw=2))
    frags.append(arrow(660, 220, 630, 220, color="#2563eb", sw=2))

    render(os.path.join(OUT, "stack-guard-and-task-isolation.svg"), w, h, *frags)


def fig_memmanage_handling():
    w, h = 980, 520
    frags = []

    frags.append(rect(10, 10, 960, 500, fill="#ffffff", stroke="#d1d5db", sw=1.5, rx=8))

    # Крок 1: Подія збою
    frags.append(fitbox(30, 40, 200, 70, "1. Порушення захисту MPU\n- Запис у чужий регіон\n- Переповнення стека (Guard)\n- Вибірка з зони XN", size=11, fill="#fee2e2", stroke="#dc2626"))

    frags.append(arrow(130, 110, 130, 140, color="#dc2626", sw=2))

    # Крок 2: Апаратне збереження стек-фрейму
    frags.append(fitbox(30, 140, 200, 100, "2. Апаратний стек-фрейм\nЯдро зберігає на PSP/MSP:\n- R0, R1, R2, R3\n- R12, LR (R14)\n- PC (Адреса збою!)\n- xPSR", size=11, fill="#eff6ff", stroke="#3b82f6"))

    frags.append(arrow(130, 240, 130, 270, color="#2563eb", sw=2))

    # Крок 3: Вхід у MemManage_Handler
    frags.append(fitbox(30, 270, 200, 90, "3. Вхід у виняток\nMemManage_Handler()\nВизначення активного стека:\nТест біта 2 у EXC_RETURN\n(PSP чи MSP)", size=11, fill="#fefce8", stroke="#eab308"))

    frags.append(arrow(130, 360, 130, 390, color="#ca8a04", sw=2))

    # Крок 4: Аналіз SCB->CFSR (MMFSR)
    frags.append(fitbox(30, 390, 200, 100, "4. Зчитування SCB->CFSR\nАналіз бітів MMFSR:\n- DACCVIOL / IACCVIOL\n- MSTKERR / MUNSTKERR\n- MLSPERR / MMARVALID", size=11, fill="#f0fdf4", stroke="#16a34a"))

    # Центральна діагностична панель
    frags.append(rect(260, 40, 420, 450, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=6))
    frags.append(text(470, 68, "Анатомія та аналіз регістрів винятку", size=15, bold=True, color="#0f172a"))

    frags.append(fitbox(280, 90, 380, 75, "Регістр статусу MMFSR (SCB->CFSR[7:0]):\n[0] IACCVIOL - Помилка вибірки інструкції (XN / NoExec)\n[1] DACCVIOL - Помилка читання або запису даних (RW)\n[3] MUNSTKERR - Збій розгортання стека при виході", size=11, fill="#ffffff", stroke="#cbd5e1"))

    frags.append(fitbox(280, 175, 380, 75, "Регістр статусу MMFSR (Продовження):\n[4] MSTKERR - Збій збереження стек-фрейму при вході\n[5] MLSPERR - Збій збереження регістрів FPU (Lazy)\n[7] MMARVALID - Адреса в MMFAR дійсна (1 = так, 0 = ні)", size=11, fill="#ffffff", stroke="#cbd5e1"))

    frags.append(fitbox(280, 260, 380, 85, "Регістр адреси збою SCB->MMFAR:\nМістить точну 32-бітну адресу пам'яті,\nзвернення до якої викликало порушення.\n(Дійсний тільки якщо MMARVALID == 1).\nЯкщо DACCVIOL=1 та MMARVALID=1 -> бачимо битий покажчик!", size=11, fill="#eff6ff", stroke="#3b82f6"))

    frags.append(fitbox(280, 355, 380, 120, "Відновлення винного коду через Stack Frame:\nВказівник стека SP -> StackFrame[6] = PC\nЗначення PC вказує на точну інструкцію (LDR / STR),\nщо спричинила збій.\nУтиліта arm-none-eabi-addr2line перетворює\nPC у точний файл і рядок вихідного коду C/C++.", size=11, fill="#f0fdf4", stroke="#16a34a"))

    # Права панель: Рішення та реакція системи
    frags.append(rect(710, 40, 240, 450, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=6))
    frags.append(text(830, 68, "Реакція системи (Recovery)", size=14, bold=True, color="#0f172a"))

    frags.append(fitbox(725, 90, 210, 80, "Сценарій А: Ізоляція задачі\n- Збій стався у Unprivileged Thread\n- Завершення винної задачі\n- Звільнення ресурсів\n- Сповіщення супервізора", size=11, fill="#eff6ff", stroke="#3b82f6"))

    frags.append(fitbox(725, 180, 210, 80, "Сценарій Б: Перезапуск задачі\n- Очищення стека задачі\n- Скидання черг та м'ютексів\n- Повторна ініціалізація\n- Робота системи триває!", size=11, fill="#f0fdf4", stroke="#16a34a"))

    frags.append(fitbox(725, 270, 210, 100, "Сценарій В: Паніка ядра\n- Збій у Privileged Handler або MSP\n- Запис Core Dump у EEPROM/Flash\n- Переведення виходів у безпечний стан\n- Кероване апаратне перезавантаження", size=11, fill="#fee2e2", stroke="#dc2626"))

    frags.append(fitbox(725, 380, 210, 95, "Очищення прапорців:\nSCB->CFSR = SCB_CFSR_MEMFAULTSR_Msk;\n(Запис 1 у біти помилок очищає їх\nперед поверненням або рестартом)", size=11, fill="#ffffff", stroke="#94a3b8"))

    # Стрілки взаємодії між панелями
    frags.append(arrow(230, 440, 260, 440, color="#16a34a", sw=2))
    frags.append(arrow(680, 130, 710, 130, color="#2563eb", sw=2))
    frags.append(arrow(680, 220, 710, 220, color="#16a34a", sw=2))
    frags.append(arrow(680, 310, 710, 310, color="#dc2626", sw=2))

    render(os.path.join(OUT, "memmanage-fault-handling.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_mpu_architecture()
    fig_pmsav7_vs_pmsav8()
    fig_stack_guard_and_isolation()
    fig_memmanage_handling()
    print("All figures generated successfully.")

# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми: Критична секція на МК: як правильно вимкнути переривання."""

import sys
import os

# Додаємо шлях до scripts/ у корені репо (4 рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

def fig_race_condition_rmw():
    """Ілюстрація 1: Анатомія стану гонки Read-Modify-Write (RMW) між фоновим потоком та ISR."""
    W, H = 880, 480
    f = [text(W / 2, 28, "Анатомія стану гонки: руйнування даних при неатомарній модифікації (RMW)", size=16, bold=True)]

    # ── Блок фонового потоку (Thread Mode) ──
    f.append(rect(20, 50, 410, 390, fill="#f8fafc", stroke=NEG, sw=1.5, rx=8))
    f.append(text(225, 75, "Фоновий потік (Thread Mode / main)", size=14, color=NEG, bold=True, anchor="middle"))

    # ── Блок переривання (Handler Mode / ISR) ──
    f.append(rect(450, 50, 410, 390, fill="#fff5f5", stroke=POS, sw=1.5, rx=8))
    f.append(text(655, 75, "Обробник переривання (ISR / Handler)", size=14, color=POS, bold=True, anchor="middle"))

    # Часова вісь вниз
    f.append(line(435, 95, 435, 420, color=LINE, sw=1.5, dash="4,4"))
    f.append(arrow(435, 420, 435, 435, color=LINE, sw=1.5))
    f.append(text(435, 452, "Час (t)", size=11, color=MUTED, anchor="middle"))

    # Крок 1: Thread зчитує counter (LDR)
    b1, _, _ = textbox(225, 125, "1. LDR r0, [counter]   (r0 = 42)\nЗчитування значення з ОЗП у регістр", size=11, pad=6, fill="#ebf8ff", stroke=NEG, color=INK)
    f.append(b1)

    # Крок 2: Thread модифікує регістр (ADDS)
    b2, _, _ = textbox(225, 190, "2. ADDS r0, r0, #1      (r0 = 43)\nІнкремент у регістрі ядра (ОЗП ще = 42!)", size=11, pad=6, fill="#ebf8ff", stroke=NEG, color=INK)
    f.append(b2)

    # Апаратне переривання!
    f.append(arrow(340, 220, 530, 240, color=POS, sw=2))
    f.append(text(435, 220, "Апаратне переривання!", size=11, color=POS, bold=True, anchor="middle"))

    # Крок 3: ISR зчитує, модифікує і записує counter
    b3, _, _ = textbox(655, 275, "3. ISR виконує counter++:\n   LDR  r1, [counter] (r1 = 42)\n   ADDS r1, r1, #1    (r1 = 43)\n   STR  r1, [counter] (ОЗП = 43)", size=11, pad=6, fill="#fed7d7", stroke=POS, color=INK)
    f.append(b3)

    # Повернення з переривання
    f.append(arrow(530, 315, 340, 335, color=NEG, sw=2))
    f.append(text(435, 320, "BX LR (повернення)", size=11, color=NEG, bold=True, anchor="middle"))

    # Крок 4: Thread записує свій застарілий результат (STR)
    b4, _, _ = textbox(225, 370, "4. STR r0, [counter]   (ОЗП = 43!)\nЗапис старого результату поверх даних ISR", size=11, pad=6, fill="#fee2e2", stroke=POS, color=POS, bold=True)
    f.append(b4)

    # Підсумок знизу
    f.append(rect(30, 445, 820, 28, fill="#fee2e2", stroke=POS, sw=1, rx=4))
    f.append(text(440, 463, "КАТАСТРОФА: Було 2 інкременти (потік + ISR), а значення лічильника збільшилося лише на 1! Дані втрачено.", size=11.5, color=POS, bold=True, anchor="middle"))

    render(os.path.join(IMG, "race-condition-rmw.svg"), W, H, *f)

def fig_naive_disable_nesting_bug():
    """Ілюстрація 2: Порушення вкладеності при наївному виклику __disable_irq() / __enable_irq()."""
    W, H = 880, 460
    f = [text(W / 2, 28, "Пастка наївного вимкнення: руйнування вкладених критичних секцій", size=16, bold=True)]

    # Зовнішня функція
    f.append(rect(20, 50, 840, 390, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=8))
    f.append(text(40, 75, "Зовнішня функція: OuterProcess()", size=13.5, color=INK, bold=True, anchor="start"))

    # 1. Outer disables IRQ
    b1, _, _ = textbox(230, 115, "__disable_irq();  /* CPSID i: PRIMASK = 1 */\nПереривання глобально вимкнено", size=11, pad=6, fill="#dcfce7", stroke=FIELD, color=INK)
    f.append(b1)

    # 2. Outer protected work 1
    b2, _, _ = textbox(230, 175, "Критична робота 1: оновлення буфера\n[ Секція надійно захищена ]", size=11, pad=6, fill="#f0fdf4", stroke=FIELD, color=FIELD, bold=True)
    f.append(b2)

    # Внутрішня функція (вкладений виклик)
    f.append(rect(430, 100, 410, 210, fill="#fff7ed", stroke="#ea580c", sw=1.5, rx=6))
    f.append(text(450, 122, "Вкладений виклик: HelperSendByte()", size=12.5, color="#c2410c", bold=True, anchor="start"))

    b_in1, _, _ = textbox(635, 155, "__disable_irq();  /* PRIMASK вже був 1 */", size=10.5, pad=5, fill="#ffedd5", stroke="#f97316", color=INK)
    f.append(b_in1)

    b_in2, _, _ = textbox(635, 205, "Запис у FIFO регістра периферії", size=10.5, pad=5, fill="#ffffff", stroke="#f97316", color=INK)
    f.append(b_in2)

    b_in3, _, _ = textbox(635, 260, "__enable_irq();   /* CPSIE i: PRIMASK = 0 ! */\nСліпе увімкнення переривань!", size=10.5, pad=5, fill="#fee2e2", stroke=POS, color=POS, bold=True)
    f.append(b_in3)

    # Стрілка виклику та повернення
    f.append(arrow(340, 195, 430, 195, color="#ea580c", sw=1.5))
    f.append(arrow(430, 285, 340, 285, color=POS, sw=1.5))

    # 3. Outer unprotected work 2 (FAIL)
    b3, _, _ = textbox(230, 335, "Критична робота 2: оновлення вказівників\n[ УВАГА: Переривання вже УВІМКНЕНІ! ]", size=11, pad=6, fill="#fee2e2", stroke=POS, color=POS, bold=True)
    f.append(b3)

    # Подія під час незахищеної роботи
    f.append(line(230, 375, 230, 395, color=POS, sw=2, dash="3,3"))
    f.append(circle(230, 375, 4, fill=POS, stroke=POS, sw=1))
    f.append(text(230, 415, "ISR вклинюється сюди і ламає інваріант структури!", size=11, color=POS, bold=True, anchor="middle"))

    # 4. Outer enables IRQ
    b4, _, _ = textbox(635, 360, "__enable_irq();  /* Запізно: катастрофа вже сталася */", size=11, pad=6, fill="#f3f4f6", stroke=MUTED, color=MUTED)
    f.append(b4)

    render(os.path.join(IMG, "naive-disable-nesting-bug.svg"), W, H, *f)

def fig_primask_vs_basepri():
    """Ілюстрація 3: Порівняння маскування через PRIMASK та BASEPRI (Zero-Latency ISR)."""
    W, H = 880, 440
    f = [text(W / 2, 28, "Ієрархія маскування: повне блокування (PRIMASK) проти селективного (BASEPRI)", size=16, bold=True)]

    # ── Ліва колонка: PRIMASK ──
    f.append(rect(20, 50, 410, 370, fill="#fff5f5", stroke=POS, sw=1.5, rx=8))
    f.append(text(225, 75, "PRIMASK = 1 (__disable_irq)", size=14, color=POS, bold=True, anchor="middle"))
    f.append(text(225, 95, "Глобальне маскування всіх стандартних переривань", size=11, color=MUTED, anchor="middle"))

    # Рівні для PRIMASK
    b_p_nmi, _, _ = textbox(225, 130, "NMI (Пріоритет -2) & HardFault (-1)\nНЕ маскуються (виконуються завжди)", size=10.5, pad=5, fill="#f0fdf4", stroke=FIELD, color=FIELD, bold=True)
    f.append(b_p_nmi)

    b_p_hi, _, _ = textbox(225, 195, "Високопріоритетні ISR (0 .. 4)\n(Керування двигуном, силова аварія)\nЗАБЛОКОВАНО! Зрив детермінізму", size=10.5, pad=5, fill="#fee2e2", stroke=POS, color=POS, bold=True)
    f.append(b_p_hi)

    b_p_rtos, _, _ = textbox(225, 275, "RTOS SysTick, PendSV, Драйвери (5 .. 15)\n(UART, I2C, SPI, таймери)\nЗАБЛОКОВАНО", size=10.5, pad=5, fill="#fee2e2", stroke=POS, color=POS)
    f.append(b_p_rtos)

    b_p_thread, _, _ = textbox(225, 360, "Фоновий потік (Thread Mode)\nВиконує критичну секцію", size=10.5, pad=5, fill="#ebf8ff", stroke=NEG, color=NEG, bold=True)
    f.append(b_p_thread)

    # ── Права колонка: BASEPRI ──
    f.append(rect(450, 50, 410, 370, fill="#f0fff4", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(655, 75, "BASEPRI = 0x50 (taskENTER_CRITICAL)", size=14, color=FIELD, bold=True, anchor="middle"))
    f.append(text(655, 95, "Селективне маскування переривань з пріоритетом >= 5", size=11, color=MUTED, anchor="middle"))

    # Рівні для BASEPRI
    b_b_nmi, _, _ = textbox(655, 130, "NMI & HardFault\nНЕ маскуються", size=10.5, pad=5, fill="#f0fdf4", stroke=FIELD, color=FIELD, bold=True)
    f.append(b_b_nmi)

    b_b_hi, _, _ = textbox(655, 195, "Zero-Latency ISR (Пріоритет 0 .. 4)\n(FOC ШІМ 20 кГц, струмовий захист)\nАКТИВНІ! Нульова затримка реакції", size=10.5, pad=5, fill="#dcfce7", stroke=FIELD, color=FIELD, bold=True)
    f.append(b_b_hi)

    # Лінія відсікання BASEPRI
    f.append(line(460, 248, 850, 248, color=POS, sw=2, dash="4,4"))
    f.append(text(655, 242, "Поріг BASEPRI = configMAX_SYSCALL_INTERRUPT_PRIORITY", size=10, color=POS, bold=True, anchor="middle"))

    b_b_rtos, _, _ = textbox(655, 285, "Системні переривання RTOS (5 .. 15)\n(SysTick, API-переривання периферії)\nЗАБЛОКОВАНО (захист структур RTOS)", size=10.5, pad=5, fill="#fee2e2", stroke=POS, color=POS)
    f.append(b_b_rtos)

    b_b_thread, _, _ = textbox(655, 360, "Фоновий потік / RTOS Task\nВиконує критичну секцію", size=10.5, pad=5, fill="#ebf8ff", stroke=NEG, color=NEG, bold=True)
    f.append(b_b_thread)

    render(os.path.join(IMG, "primask-vs-basepri.svg"), W, H, *f)

def fig_ldrex_strex_exclusive_monitor():
    """Ілюстрація 4: Апаратний ексклюзивний монітор ARM (LDREX/STREX) для Lock-Free операцій."""
    W, H = 880, 440
    f = [text(W / 2, 28, "Апаратний монітор ексклюзивності ARM (LDREX / STREX)", size=16, bold=True)]

    # ── Ліва панель: Успішний атомарний запис ──
    f.append(rect(20, 50, 410, 370, fill="#f0fff4", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(225, 75, "Сценарій 1: Успішна транзакція (без колізій)", size=13, color=FIELD, bold=True, anchor="middle"))

    b_s1_1, _, _ = textbox(225, 115, "1. LDREX r1, [addr]\nЗавантаження значення + монітор -> EXCLUSIVE", size=10.5, pad=5, fill="#ffffff", stroke=FIELD, color=INK)
    f.append(b_s1_1)

    b_s1_mon1, _, _ = textbox(225, 175, "Монітор ядра: Стан EXCLUSIVE для [addr]", size=10.5, pad=5, fill="#dcfce7", stroke=FIELD, color=FIELD, bold=True)
    f.append(b_s1_mon1)

    b_s1_2, _, _ = textbox(225, 235, "2. ADDS r1, r1, #1\nМодифікація значення в регістрі ядра", size=10.5, pad=5, fill="#ffffff", stroke=MUTED, color=INK)
    f.append(b_s1_2)

    b_s1_3, _, _ = textbox(225, 305, "3. STREX r2, r1, [addr]\nМонітор у стані EXCLUSIVE -> Запис дозволено!\nВ ОЗП записано нове значення; r2 = 0 (УСПІХ)", size=10.5, pad=5, fill="#dcfce7", stroke=FIELD, color=FIELD, bold=True)
    f.append(b_s1_3)

    b_s1_res, _, _ = textbox(225, 380, "Результат: Швидкий атомарний запис без вимкнення IRQ", size=10.5, pad=5, fill="#f0fdf4", stroke=FIELD, color=FIELD)
    f.append(b_s1_res)

    # ── Права панель: Колізія з перериванням і відкат ──
    f.append(rect(450, 50, 410, 370, fill="#fff5f5", stroke=POS, sw=1.5, rx=8))
    f.append(text(655, 75, "Сценарій 2: Втручання ISR під час операції", size=13, color=POS, bold=True, anchor="middle"))

    b_s2_1, _, _ = textbox(655, 115, "1. Thread: LDREX r1, [addr]\nМонітор переходить у стан EXCLUSIVE", size=10.5, pad=5, fill="#ffffff", stroke=MUTED, color=INK)
    f.append(b_s2_1)

    b_s2_isr, _, _ = textbox(655, 180, "2. Апаратний ISR вклинюється і виконує STR!\nБудь-який запис у пам'ять скидає монітор -> OPEN", size=10.5, pad=5, fill="#fee2e2", stroke=POS, color=POS, bold=True)
    f.append(b_s2_isr)

    b_s2_mon2, _, _ = textbox(655, 245, "Монітор ядра: Стан OPEN (ексклюзивність втрачено)", size=10.5, pad=5, fill="#fed7d7", stroke=POS, color=POS)
    f.append(b_s2_mon2)

    b_s2_3, _, _ = textbox(655, 315, "3. Thread: STREX r2, r1, [addr]\nМонітор у стані OPEN -> ЗАПИС В ОЗП СКАСОВАНО!\nЗначення в ОЗП не пошкоджено; r2 = 1 (НЕВДАЧА)", size=10.5, pad=5, fill="#fee2e2", stroke=POS, color=POS, bold=True)
    f.append(b_s2_3)

    b_s2_res, _, _ = textbox(655, 380, "4. CBNZ r2, retry_loop -> Повторення спроби заново", size=10.5, pad=5, fill="#ebf8ff", stroke=NEG, color=NEG, bold=True)
    f.append(b_s2_res)

    render(os.path.join(IMG, "ldrex-strex-exclusive-monitor.svg"), W, H, *f)

def main():
    fig_race_condition_rmw()
    fig_naive_disable_nesting_bug()
    fig_primask_vs_basepri()
    fig_ldrex_strex_exclusive_monitor()
    print("Усі фігури успішно згенеровано у теці img/")

if __name__ == "__main__":
    main()

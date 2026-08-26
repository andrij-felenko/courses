# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми: Дисципліна обробника: що в ISR робити не можна."""

import sys
import os

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

def fig_isr_execution_cost():
    """Ілюстрація 1: Порівняння тривалого (поганого) ISR та швидкого ISR за моделлю Top-Half."""
    W, H = 880, 440
    f = [text(W / 2, 28, "Ціна затримки: чому тривалий ISR блокує критичні події", size=16, bold=True)]
    
    # ── Блок 1: Поганий обробник (Блокування системи) ──
    f.append(rect(20, 50, 840, 175, fill="#fff5f5", stroke=POS, sw=1.5, rx=8))
    f.append(text(40, 75, "Поганий ISR: Блокування, затримки (delay) та printf()", size=14, color=POS, bold=True, anchor="start"))
    
    # Часова шкала 1
    f.append(line(40, 130, 820, 130, color=LINE, sw=1.5))
    f.append(arrow(800, 130, 830, 130, color=LINE, sw=1.5))
    f.append(text(825, 150, "Час", size=11, color=MUTED, anchor="end"))
    
    # Подія 1: Переривання UART
    f.append(line(80, 100, 80, 130, color=POS, sw=2))
    f.append(circle(80, 100, 4, fill=POS, stroke=POS, sw=1))
    f.append(text(80, 92, "UART RX ISR", size=11, color=POS, bold=True, anchor="middle"))
    
    # Блок виконання поганого ISR (довгий)
    b_bad, _, _ = textbox(225, 130, "Поганий ISR: delay(), printf(), парсинг (3.5 мс)", size=10.5, pad=6, fill="#fed7d7", stroke=POS, color=POS, bold=True)
    f.append(b_bad)
    
    # Подія 2: Термінове переривання під час поганого ISR
    f.append(line(230, 170, 230, 130, color=POS, sw=2, dash="3,3"))
    f.append(circle(230, 170, 4, fill=POS, stroke=POS, sw=1))
    f.append(text(230, 190, "Аварія (Overcurrent)", size=11, color=POS, bold=True, anchor="middle"))
    f.append(arrow(230, 202, 430, 202, color=POS, sw=1.5))
    f.append(text(330, 217, "Заблоковане! Латентність зірвана", size=11, color=POS, italic=True, anchor="middle"))
    
    # Виконання термінового після завершення поганого
    b_urg, _, _ = textbox(525, 130, "Аварійний обробник (запізнілий)", size=10.5, pad=6, fill="#feebc8", stroke="#dd6b20", color="#7b341e", bold=True)
    f.append(b_urg)
    
    # Фоновий потік
    b_bg1, _, _ = textbox(730, 130, "Фоновий main()", size=10.5, pad=6, fill=FILL, stroke=MUTED, color=INK)
    f.append(b_bg1)
    
    # ── Блок 2: Дисциплінований обробник (Top-Half / Bottom-Half) ──
    f.append(rect(20, 240, 840, 180, fill="#f0fff4", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(40, 265, "Дисциплінований ISR: Top-Half (квитування + буфер) + Bottom-Half (потік)", size=14, color=FIELD, bold=True, anchor="start"))
    
    # Часова шкала 2
    f.append(line(40, 320, 820, 320, color=LINE, sw=1.5))
    f.append(arrow(800, 320, 830, 320, color=LINE, sw=1.5))
    f.append(text(825, 340, "Час", size=11, color=MUTED, anchor="end"))
    
    # Подія 1: Переривання UART
    f.append(line(80, 290, 80, 320, color=FIELD, sw=2))
    f.append(circle(80, 290, 4, fill=FIELD, stroke=FIELD, sw=1))
    f.append(text(80, 282, "UART RX ISR", size=11, color=FIELD, bold=True, anchor="middle"))
    
    # Короткий ISR
    b_good, _, _ = textbox(165, 320, "Top-Half (2 мкс)\nКвитувати + в буфер", size=10.5, pad=6, fill="#c6f6d5", stroke=FIELD, color=FIELD, bold=True)
    f.append(b_good)
    
    # Термінове переривання обслуговується миттєво
    f.append(line(270, 290, 270, 320, color=POS, sw=2))
    f.append(circle(270, 290, 4, fill=POS, stroke=POS, sw=1))
    f.append(text(270, 282, "Аварійне переривання", size=11, color=POS, bold=True, anchor="middle"))
    
    b_urg2, _, _ = textbox(375, 320, "Аварійний обробник\n(негайне виконання)", size=10.5, pad=6, fill="#fed7d7", stroke=POS, color=POS, bold=True)
    f.append(b_urg2)
    
    # Bottom-half таск
    b_bh, _, _ = textbox(635, 320, "Bottom-Half (фоновий таск / main)\nПарсинг пакетів, логування, обчислення", size=10.5, pad=6, fill="#ebf8ff", stroke=NEG, color=NEG, bold=True)
    f.append(b_bh)
    
    f.append(arrow(210, 355, 500, 355, color=FIELD, sw=1.5))
    f.append(text(355, 372, "Сигнал сповіщення (Task Notify / Event Flag)", size=10.5, color=FIELD, italic=True, anchor="middle"))
    
    render(os.path.join(IMG, "isr-execution-cost.svg"), W, H, *f)

def fig_top_bottom_half():
    """Ілюстрація 2: Архітектурний шаблон Top-Half / Bottom-Half у мікроконтролері."""
    W, H = 840, 410
    f = [text(W / 2, 28, "Архітектурний шаблон «Верхня та нижня половина» (Top-Half / Bottom-Half)", size=16, bold=True)]
    
    # ── Ліва частина: Апаратний рівень і Top-Half ──
    f.append(rect(20, 50, 380, 340, fill="#fefcbf", stroke="#d69e2e", sw=1.5, rx=8))
    f.append(text(210, 75, "Top-Half: Апаратний контекст (ISR)", size=13.5, color="#744210", bold=True, anchor="middle"))
    
    b_s1, _, _ = textbox(210, 115, "1. Апаратне переривання периферії\n(UART RXNE, Timer Update, ADC EOC)", size=10.5, pad=5, fill="#ffffff", stroke="#d69e2e", color=INK)
    f.append(b_s1)
    
    b_s2, _, _ = textbox(210, 180, "2. Вичитування регістру даних\n(DR / RDR) та квитування прапорця (SR)", size=10.5, pad=5, fill="#ffffff", stroke="#d69e2e", color=INK)
    f.append(b_s2)
    
    b_s3, _, _ = textbox(210, 250, "3. Запис у Lock-Free кільцевий буфер\nабо атомарний прапорець події", size=10.5, pad=5, fill="#ffffff", stroke="#d69e2e", color=INK)
    f.append(b_s3)
    
    b_s4, _, _ = textbox(210, 325, "4. Розблокування Bottom-Half таска\n(vTaskNotifyGiveFromISR / Flag)", size=10.5, pad=5, fill="#feebc8", stroke=POS, color=POS, bold=True)
    f.append(b_s4)
    
    f.append(arrow(210, 137, 210, 158, color="#744210", sw=1.5))
    f.append(arrow(210, 202, 210, 228, color="#744210", sw=1.5))
    f.append(arrow(210, 272, 210, 303, color="#744210", sw=1.5))
    
    # ── Міст передачі: Lock-Free міст ──
    f.append(arrow(400, 250, 440, 250, color=FIELD, sw=2))
    f.append(text(420, 238, "Дані", size=10.5, color=FIELD, bold=True, anchor="middle"))
    
    f.append(arrow(400, 325, 440, 325, color=POS, sw=2))
    f.append(text(420, 313, "Сигнал", size=10.5, color=POS, bold=True, anchor="middle"))
    
    # ── Права частина: Нижня половина (Bottom-Half) ──
    f.append(rect(440, 50, 380, 340, fill="#ebf8ff", stroke=NEG, sw=1.5, rx=8))
    f.append(text(630, 75, "Bottom-Half: Потоковий контекст (Task / main)", size=13.5, color=NEG, bold=True, anchor="middle"))
    
    b_t1, _, _ = textbox(630, 115, "Очікування сигналу в стані сну (Blocked)\n(ulTaskNotifyTake / перевірка прапорця)", size=10.5, pad=5, fill="#ffffff", stroke=NEG, color=INK)
    f.append(b_t1)
    
    b_t2, _, _ = textbox(630, 185, "Пробудження та вичитування байтів\nіз кільцевого буфера (без блокувань)", size=10.5, pad=5, fill="#ffffff", stroke=NEG, color=INK)
    f.append(b_t2)
    
    b_t3, _, _ = textbox(630, 260, "Важка бізнес-логіка та операції:\n• Перевірка CRC та парсинг протоколу\n• Запис у Flash / EEPROM\n• Форматований вивід (printf/лог)", size=10.5, pad=5, fill="#ffffff", stroke=NEG, color=INK)
    f.append(b_t3)
    
    b_t4, _, _ = textbox(630, 340, "Перехід у режим очікування нової події", size=10.5, pad=5, fill="#c3dafe", stroke=NEG, color=NEG, bold=True)
    f.append(b_t4)
    
    f.append(arrow(630, 137, 630, 163, color=NEG, sw=1.5))
    f.append(arrow(630, 207, 630, 230, color=NEG, sw=1.5))
    f.append(arrow(630, 290, 630, 320, color=NEG, sw=1.5))
    
    render(os.path.join(IMG, "top-bottom-half.svg"), W, H, *f)

def fig_write_buffer_delay():
    """Ілюстрація 3: Пастка затримки буфера запису (Write Buffer Delay) на шині ARM Cortex-M."""
    W, H = 840, 380
    f = [text(W / 2, 28, "Механізм пастки Write Buffer Delay та повторного входу в ISR", size=16, bold=True)]
    
    # Ядро CPU
    f.append(rect(25, 60, 215, 290, fill="#f4f6f8", stroke="#4a5568", sw=1.5, rx=8))
    f.append(text(132, 85, "Ядро Cortex-M", size=13, color=INK, bold=True, anchor="middle"))
    b_c1, _, _ = textbox(132, 130, "1. STR (скинути прапорець)\nTIMx->SR = ~TIM_SR_UIF", size=10, pad=5, fill="#ffffff", stroke=MUTED, color=INK)
    f.append(b_c1)
    b_c2, _, _ = textbox(132, 200, "2. BX LR (вихід з ISR)\nЯдро повертає контекст", size=10, pad=5, fill="#fed7d7", stroke=POS, color=POS, bold=True)
    f.append(b_c2)
    b_c3, _, _ = textbox(132, 275, "3. NVIC бачить активну лінію!\nЯдро ЗНОВУ входить в ISR!", size=10, pad=5, fill="#fed7d7", stroke=POS, color=POS, bold=True)
    f.append(b_c3)
    
    # Буфер запису шини (Write Buffer)
    f.append(rect(270, 60, 250, 290, fill="#feebc8", stroke="#dd6b20", sw=1.5, rx=8))
    f.append(text(395, 85, "Буфер запису (Bus Matrix)", size=13, color="#7b341e", bold=True, anchor="middle"))
    
    b_wb1, _, _ = textbox(395, 145, "Операція скидання прапорця\nзависла в конвеєрі запису шини\n(затримка шин APB/AHB: 2-4 такти)", size=10, pad=6, fill="#ffffff", stroke="#dd6b20", color=INK)
    f.append(b_wb1)
    
    b_wb2, _, _ = textbox(395, 255, "Ліки: DSB або читання регістра\n(dummy = TIMx->SR)\nзмушує шину завершити запис", size=10, pad=6, fill="#c6f6d5", stroke=FIELD, color=FIELD, bold=True)
    f.append(b_wb2)
    
    # Периферійний блок (Таймер)
    f.append(rect(550, 60, 265, 290, fill="#edf2f7", stroke="#4a5568", sw=1.5, rx=8))
    f.append(text(682, 85, "Периферія (Таймер / UART)", size=13, color=INK, bold=True, anchor="middle"))
    
    b_p1, _, _ = textbox(682, 145, "Регістр статусу (SR):\nПрапорець UIF ще НЕ скинутий!\n(запис іде повільною шиною)", size=10, pad=6, fill="#fed7d7", stroke=POS, color=POS)
    f.append(b_p1)
    
    b_p2, _, _ = textbox(682, 255, "Лінія переривання до NVIC:\nЗалишається активною (HIGH)!", size=10, pad=6, fill="#ffffff", stroke=POS, color=POS, bold=True)
    f.append(b_p2)
    
    # Зв'язки між блоками
    f.append(arrow(240, 130, 270, 130, color="#dd6b20", sw=1.5))
    f.append(arrow(520, 145, 550, 145, color="#dd6b20", sw=1.5))
    f.append(arrow(550, 260, 240, 275, color=POS, sw=1.5))
    
    render(os.path.join(IMG, "write-buffer-delay.svg"), W, H, *f)

def main():
    fig_isr_execution_cost()
    fig_top_bottom_half()
    fig_write_buffer_delay()
    print("All figures generated successfully.")

if __name__ == '__main__':
    main()

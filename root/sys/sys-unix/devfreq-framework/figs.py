# -*- coding: utf-8 -*-
"""Генератор SVG-ілюстрацій для статті devfreq-framework."""

import os
import sys

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, textbox, rect, line, arrow, text, mtext, circle,
    INK, MUTED, POS, NEG, FIELD, FILL, BG
)

def fig_architecture(out_path):
    """Діаграма архітектури підсистеми devfreq та її взаємодії з ядром і залізом."""
    w, h = 920, 570
    frags = [
        # Загальні зони
        rect(20, 20, 880, 110, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8),
        text(460, 42, "Рівень простору користувача (User Space) та Sysfs", size=14, color=MUTED, bold=True),

        rect(20, 150, 880, 240, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8),
        text(460, 172, "Підсистема devfreq у ядрі Linux (Kernel Space)", size=14, color=FIELD, bold=True),

        rect(20, 410, 880, 140, fill="#fef2f2", stroke="#fca5a5", sw=1.5, rx=8),
        text(460, 432, "Апаратний рівень SoC та драйвери пристроїв", size=14, color=POS, bold=True),
    ]

    # Елементи User Space
    b_sysfs, _, _ = textbox(240, 85, "/sys/class/devfreq/<dev>/\n(cur_freq, governor, trans_stat)", size=12, pad=8, fill="#ffffff", stroke=MUTED)
    b_daemon, _, _ = textbox(670, 85, "Демони енергозбереження / PM QoS\n(налаштування порогів, моніторинг)", size=12, pad=8, fill="#ffffff", stroke=MUTED)
    frags.extend([b_sysfs, b_daemon])

    # Елементи Kernel Core
    b_gov, _, _ = textbox(170, 255, "Регулятори (Governors)\n• simple_ondemand\n• passive\n• performance / powersave\n• userspace", size=12, pad=8, fill="#ffffff", stroke=FIELD)
    b_core, _, _ = textbox(460, 255, "Ядро devfreq (Core)\n• struct devfreq\n• struct devfreq_dev_profile\n• Workqueue devfreq_monitor\n• Розрахунок busy_time / total_time", size=12, pad=8, fill="#ffffff", stroke=FIELD)
    b_opp, _, _ = textbox(750, 255, "OPP Framework\n• Таблиці (частота, напруга)\n• dev_pm_opp_set_rate()\n• Clock & Regulator API", size=12, pad=8, fill="#ffffff", stroke=FIELD)
    frags.extend([b_gov, b_core, b_opp])

    # Елементи Hardware
    b_gpu, _, _ = textbox(160, 490, "GPU / NPU\nЛічильники завантаження\n(busy cycles / idle)", size=12, pad=8, fill="#ffffff", stroke=POS)
    b_dram, _, _ = textbox(460, 490, "Контролер пам'яті / NoC\nКількість транзакцій шини\n(DMA / FIFO bandwidth)", size=12, pad=8, fill="#ffffff", stroke=POS)
    b_clk_reg, _, _ = textbox(760, 490, "Апаратні PLL та PMIC\nГенератори частот (CCF)\nРегулятори живлення (Regulator)", size=12, pad=8, fill="#ffffff", stroke=POS)
    frags.extend([b_gpu, b_dram, b_clk_reg])

    # Зв'язки (стрілки)
    frags.append(arrow(240, 115, 380, 205, color=MUTED, sw=1.5))
    frags.append(arrow(670, 115, 540, 205, color=MUTED, sw=1.5))

    frags.append(arrow(295, 255, 320, 255, color=FIELD, sw=1.5))
    frags.append(arrow(600, 255, 635, 255, color=FIELD, sw=1.5))

    frags.append(arrow(160, 445, 370, 310, color=POS, sw=1.5))
    frags.append(arrow(460, 445, 460, 310, color=POS, sw=1.5))

    frags.append(arrow(760, 305, 760, 445, color=FIELD, sw=1.5))

    render(out_path, w, h, *frags)

def fig_passive_interconnect(out_path):
    """Діаграма каскадного масштабування шин та периферії через регулятор passive."""
    w, h = 900, 450
    frags = [
        # Головний пристрій (Master)
        rect(25, 25, 395, 400, fill="#eff6ff", stroke="#93c5fd", sw=1.5, rx=8),
        text(220, 50, "Головний пристрій (Master Devfreq)", size=14, color=NEG, bold=True),
        
        # Підлеглий пристрій (Slave / Interconnect)
        rect(480, 25, 395, 400, fill="#fdf4ff", stroke="#f0abfc", sw=1.5, rx=8),
        text(675, 50, "Підлеглий пристрій (Passive Devfreq)", size=14, color="#a21caf", bold=True),
    ]

    # Master вузли
    b_m_hw, _, _ = textbox(220, 110, "Графічний прискорювач (GPU)\nАктивне навантаження (3D шейдери)", size=12, pad=8, fill="#ffffff", stroke=NEG)
    b_m_gov, _, _ = textbox(220, 225, "Регулятор: simple_ondemand\nОпитування лічильників GPU\nРозрахунок частоти: 800 МГц", size=12, pad=8, fill="#ffffff", stroke=NEG)
    b_m_opp, _, _ = textbox(220, 345, "Застосування OPP для GPU\nПідвищення VDD_GPU + PLL", size=12, pad=8, fill="#ffffff", stroke=NEG)
    frags.extend([b_m_hw, b_m_gov, b_m_opp])

    # Slave вузли
    b_s_gov, _, _ = textbox(675, 110, "Регулятор: passive\nПідписаний на сповіщення Master\nСпіввідношення: 800 МГц GPU → 2133 МГц DRAM", size=12, pad=8, fill="#ffffff", stroke="#a21caf")
    b_s_opp, _, _ = textbox(675, 225, "Застосування OPP для шини\nПеремикання шини NoC / DRAM", size=12, pad=8, fill="#ffffff", stroke="#a21caf")
    b_s_hw, _, _ = textbox(675, 345, "Шина пам'яті (DDR Controller / NoC)\nЗабезпечення смуги пропускання 25.6 ГБ/с", size=12, pad=8, fill="#ffffff", stroke="#a21caf")
    frags.extend([b_s_gov, b_s_opp, b_s_hw])

    # Зв'язки всередині Master
    frags.append(arrow(220, 145, 220, 185, color=NEG, sw=1.5))
    frags.append(arrow(220, 265, 220, 305, color=NEG, sw=1.5))

    # Сповіщення між Master та Slave через textbox
    b_notify, _, _ = textbox(450, 175, "Сповіщення про\nзміну частоти", size=11, pad=6, fill="#ffffff", stroke=POS, color=POS, bold=True)
    frags.append(b_notify)

    frags.append(arrow(345, 225, 400, 185, color=POS, sw=1.5))
    frags.append(arrow(500, 165, 555, 125, color=POS, sw=1.5))

    # Зв'язки всередині Slave
    frags.append(arrow(675, 145, 675, 185, color="#a21caf", sw=1.5))
    frags.append(arrow(675, 265, 675, 305, color="#a21caf", sw=1.5))

    render(out_path, w, h, *frags)

def main():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)

    fig_architecture(os.path.join(img_dir, "devfreq-architecture.svg"))
    print("Згенеровано: img/devfreq-architecture.svg")

    fig_passive_interconnect(os.path.join(img_dir, "devfreq-passive-interconnect.svg"))
    print("Згенеровано: img/devfreq-passive-interconnect.svg")

if __name__ == "__main__":
    main()

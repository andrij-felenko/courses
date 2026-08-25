# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: Порівняння RSSI та RSRP у сітці OFDM ─────────────────────────────

def fig_rssi_vs_rsrp():
    W, H = 780, 400
    p = []

    # Заголовок блоку OFDM
    p.append(text(W / 2, 28, "OFDM-сітка частота-час: інтегрування RSSI проти вибірковості RSRP",
                  size=15, color=INK, bold=True))

    # Вісь часу та частоти
    ox, oy = 70, 310
    grid_w, grid_h = 440, 220
    
    # Осі
    p.append(line(ox, oy, ox + grid_w + 30, oy, color=INK, sw=1.8)) # Час
    p.append(arrow(ox + grid_w + 20, oy, ox + grid_w + 30, oy, color=INK, sw=1.8))
    p.append(text(ox + grid_w + 35, oy + 4, "Час (t)", size=12, color=INK, bold=True))

    p.append(line(ox, oy, ox, oy - grid_h - 20, color=INK, sw=1.8)) # Частота
    p.append(arrow(ox, oy - grid_h - 10, ox, oy - grid_h - 20, color=INK, sw=1.8))
    p.append(text(ox - 10, oy - grid_h - 25, "Частота (f / Піднесні)", size=12, color=INK, bold=True))

    # Малювання елементів сітки (Resource Elements)
    num_sub = 8 # кількість піднесних
    num_sym = 10 # кількість символів
    cw = grid_w / num_sym
    ch = grid_h / num_sub

    # CRS / SSB елементи (позначені як RSRP)
    rsrp_cells = {(1, 2), (1, 7), (5, 2), (5, 7), (3, 4), (7, 4)}
    # Завади / чужі сигнали
    interf_cells = {(0, 5), (0, 6), (1, 5), (6, 8), (7, 8)}

    for r in range(num_sub):
        for c in range(num_sym):
            x = ox + c * cw
            y = oy - (r + 1) * ch
            
            if (r, c) in rsrp_cells:
                # Опорний сигнал (RSRP) - яскравий зелений
                p.append(rect(x + 1, y + 1, cw - 2, ch - 2, fill="#27ae60", stroke="#1e8449", sw=1.2, rx=2))
                p.append(text(x + cw/2, y + ch/2 + 4, "RS", size=10, color="#ffffff", bold=True))
            elif (r, c) in interf_cells:
                # Завада / Шум
                p.append(rect(x + 1, y + 1, cw - 2, ch - 2, fill="#e74c3c", stroke="#c0392b", sw=1.2, rx=2))
                p.append(text(x + cw/2, y + ch/2 + 4, "N/I", size=9, color="#ffffff"))
            else:
                # Звичайний блок даних
                p.append(rect(x + 1, y + 1, cw - 2, ch - 2, fill="#ebf5fb", stroke="#aed6f1", sw=0.8, rx=2))

    # Виносні рамки та пояснення праворуч
    rx0 = 540
    
    # RSSI рамка
    b_rssi = fitbox(rx0, 70, 210, 130,
                    "RSSI (Wideband Power):\n"
                    "Сумує ПОТУЖНІСТЬ УСЬОГО прямокутника:\n"
                    "• Корисні дані (Data)\n"
                    "• Опорні пилоти (RS)\n"
                    "• Завади сусідів (N/I)\n"
                    "• Тепловий шум",
                    size=11.5, color=INK, fill="#fdedec", stroke="#e74c3c")
    p.append(b_rssi)

    # RSRP рамка
    b_rsrp = fitbox(rx0, 215, 210, 135,
                    "RSRP (Reference Signal Power):\n"
                    "Вимірює СЕРЕДНЮ потужність ЛИШЕ в клітинках RS (зелені):\n"
                    "• Ігнорує завади N/I\n"
                    "• Точна оцінка корисного сигналу від БС",
                    size=11.5, color=INK, fill="#eafaf1", stroke="#27ae60")
    p.append(b_rsrp)

    # Охоплювальна рамка для RSSI на сітці
    p.append(rect(ox - 4, oy - grid_h - 4, grid_w + 8, grid_h + 8, fill="none", stroke="#e74c3c", sw=1.8))
    p.append(text(ox + grid_w/2, oy + 26, "Вся смуга каналу (наприклад, 20 МГц / 100 Resource Blocks)",
                  size=11, color="#c0392b", italic=True))

    render(os.path.join(OUT, "rssi-vs-rsrp-ofdm.svg"), W, H, *p,
           title="Порівняння обсягу вимірювання RSSI та RSRP у сітці OFDM")


# ── Фігура 2: Апаратний тракт вимірювання RSSI та AGC ────────────────────────

def fig_rssi_agc_chain():
    W, H = 780, 360
    p = []

    p.append(text(W / 2, 28, "Апаратний тракт приймача: від радіочастоти до цифрового RSSI",
                  size=15, color=INK, bold=True))

    # Схема блоків
    blocks = [
        ("Антена", "RF in", "#f4f6f7", INK, 50, 110, 80, 54),
        ("LNA", "Низькошумний\nпідсилювач", "#e8f8f5", FIELD, 165, 110, 100, 54),
        ("VGA / AGC", "Кероване\nпідсилення", "#feaf9d", NEG, 300, 110, 105, 54),
        ("ADC", "АЦП (IQ)\nвідліки", "#eaf2f8", "#2980b9", 440, 110, 95, 54),
        ("DSP", "Обчислення\nI² + Q²", "#f9ebea", "#c0392b", 570, 110, 100, 54),
    ]

    for title, desc, bg, border, x, y, bw, bh in blocks:
        p.append(rect(x, y, bw, bh, fill=bg, stroke=border, sw=1.8, rx=4))
        p.append(text(x + bw/2, y + 20, title, size=12, color=border, bold=True))
        lines = desc.split('\n')
        if len(lines) == 1:
            p.append(text(x + bw/2, y + 38, lines[0], size=10, color=INK))
        else:
            p.append(text(x + bw/2, y + 35, lines[0], size=9.5, color=INK))
            p.append(text(x + bw/2, y + 47, lines[1], size=9.5, color=INK))

    # Стрілки між блоками
    connections = [
        (130, 137, 165, 137),
        (265, 137, 300, 137),
        (405, 137, 440, 137),
        (535, 137, 570, 137),
    ]
    for x1, y1, x2, y2 in connections:
        p.append(line(x1, y1, x2, y2, color=INK, sw=1.6))
        p.append(arrow(x2 - 8, y2, x2, y2, color=INK, sw=1.6))

    # Петля AGC (зворотний зв'язок від DSP/ADC до VGA)
    p.append(line(620, 164, 620, 215, color="#c0392b", sw=1.6, dash="4,3"))
    p.append(line(620, 215, 352, 215, color="#c0392b", sw=1.6, dash="4,3"))
    p.append(line(352, 215, 352, 164, color="#c0392b", sw=1.6, dash="4,3"))
    p.append(arrow(352, 172, 352, 164, color="#c0392b", sw=1.6))
    p.append(text(486, 230, "Петля автоматичного регулювання підсилення (AGC Feedback)",
                  size=10.5, color="#c0392b", bold=True))

    # Вихідний блок RSSI дБм
    p.append(line(670, 137, 715, 137, color=INK, sw=1.6))
    p.append(arrow(707, 137, 715, 137, color=INK, sw=1.6))
    p.append(rect(700, 105, 70, 64, fill="#27ae60", stroke="#1e8449", sw=1.8, rx=4))
    p.append(text(735, 132, "RSSI", size=13, color="#ffffff", bold=True))
    p.append(text(735, 150, "(дБм)", size=11, color="#ffffff"))

    # Нижня рамка з формулою компенсованого виміру
    b_formula = fitbox(50, 260, 680, 75,
                       "Формула розрахунку цифрового RSSI у DSP:\n"
                       "RSSI (дБм) = 10 · log₁₀( ∑(Iₖ² + Qₖ²) / N ) − Gain_AGC + Calibration_Offset\n"
                       "DSP сумує цифрову потужність відліків і віднімає поточний коефіцієнт підсилення AGC.",
                       size=11.5, color=INK, fill="#fcf3cf", stroke="#f1c40f")
    p.append(b_formula)

    render(os.path.join(OUT, "rssi-agc-measurement-chain.svg"), W, H, *p,
           title="Апаратний тракт приймача та обчислення RSSI")


if __name__ == "__main__":
    fig_rssi_vs_rsrp()
    fig_rssi_agc_chain()
    print("Figures generated successfully!")

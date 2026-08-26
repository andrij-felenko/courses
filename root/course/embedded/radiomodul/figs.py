# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def block(cx, cy, w, h, label, sub=None, fill=FILL, stroke=LINE, sw=1.5):
    out = rect(cx - w / 2, cy - h / 2, w, h, fill=fill, stroke=stroke, sw=sw)
    if sub:
        if "\n" in sub:
            lines = sub.split("\n")
            out += text(cx, cy - len(lines) * 7, label, size=13, bold=True)
            for idx, ln in enumerate(lines):
                out += text(cx, cy + 8 + idx * 14, ln, size=10, color=MUTED)
        else:
            out += text(cx, cy - 3, label, size=13, bold=True)
            out += text(cx, cy + 13, sub, size=10, color=MUTED)
    else:
        out += text(cx, cy + 5, label, size=13, bold=True)
    return out


# ── 1. Архітектура апаратного трансивера ─────────────────────────────────────
def fig_transceiver_arch():
    W, H = 840, 480
    f = []
    f.append(text(W / 2, 24, "Архітектура сучасного прямого/Low-IF радіотрансивера", size=15, bold=True))

    # Антена ліворуч
    ax, ay = 45, 230
    f.append(line(ax, ay, ax, ay - 35, sw=2))
    f.append(line(ax - 16, ay - 35, ax + 16, ay - 35, sw=2))
    f.append(line(ax - 16, ay - 35, ax - 6, ay - 50, sw=2))
    f.append(line(ax + 16, ay - 35, ax + 6, ay - 50, sw=2))
    f.append(text(ax, ay + 20, "RF", size=11, bold=True))
    f.append(text(ax, ay + 34, "50 Ω", size=10, color=MUTED))

    # T/R перемикач
    sx, sy = 115, 230
    f.append(line(ax, ay, sx - 20, ay, sw=2))
    f.append(circle(sx, sy, 20, fill="#fff7e6", stroke="#b8860b", sw=1.8))
    f.append(text(sx, sy + 4, "T/R", size=12, bold=True, color="#7a5b00"))

    # RF фронтенд: верхня гілка Rx (LNA), нижня Tx (PA)
    lna_x, lna_y = 205, 150
    pa_x, pa_y = 205, 310

    f.append(line(sx + 14, sy - 14, lna_x - 42, lna_y, sw=1.8))
    f.append(block(lna_x, lna_y, 80, 46, "LNA", "малошумний", fill="#eaf0fd", stroke=NEG))

    f.append(line(pa_x + 40, pa_y, sx + 14, sy + 14, sw=1.8))
    f.append(block(pa_x, pa_y, 80, 46, "PA", "підсилювач Tx", fill="#fdecea", stroke=POS))

    # Квадратурні змішувачі Rx (I та Q)
    mix_i_x, mix_i_y = 330, 115
    mix_q_x, mix_q_y = 330, 185

    f.append(line(lna_x + 40, lna_y, mix_i_x - 40, mix_i_y, sw=1.5))
    f.append(line(lna_x + 40, lna_y, mix_q_x - 40, mix_q_y, sw=1.5))

    f.append(block(mix_i_x, mix_i_y, 76, 40, "Mixer I", "0° LO", fill="#eef7f0", stroke=FIELD))
    f.append(block(mix_q_x, mix_q_y, 76, 40, "Mixer Q", "90° LO", fill="#eef7f0", stroke=FIELD))

    # Синтезатор частоти PLL / VCO посередині
    pll_x, pll_y = 330, 252
    f.append(block(pll_x, pll_y, 105, 50, "PLL / Synth", "VCO + Frac-N", fill="#fdf8e2", stroke="#b8860b"))

    # Кварц біля PLL
    xo_x, xo_y = 330, 335
    f.append(line(xo_x, xo_y - 18, pll_x, pll_y + 25, sw=1.5))
    f.append(block(xo_x, xo_y, 90, 36, "XO / TCXO", "26 / 32 MHz", fill=FILL, stroke=LINE))

    # Зв'язок гетеродина з мікшерами та передавачем
    f.append(line(pll_x, pll_y - 25, mix_q_x, mix_q_y + 20, sw=1.5, dash="3,3"))
    f.append(line(pll_x - 30, pll_y + 15, pa_x + 40, pa_y, sw=1.5, dash="3,3"))

    # АЦП / Фільтри (Rx)
    adc_x = 450
    f.append(line(mix_i_x + 38, mix_i_y, adc_x - 36, mix_i_y, sw=1.5))
    f.append(line(mix_q_x + 38, mix_q_y, adc_x - 36, mix_q_y, sw=1.5))
    f.append(block(adc_x, mix_i_y, 72, 40, "ADC I", "LPF + ΣΔ", fill="#eaf0fd", stroke=NEG))
    f.append(block(adc_x, mix_q_y, 72, 40, "ADC Q", "LPF + ΣΔ", fill="#eaf0fd", stroke=NEG))

    # Цифровий модем (DSP Modem)
    dsp_x, dsp_y = 585, 150
    f.append(line(adc_x + 36, mix_i_y, dsp_x - 65, mix_i_y, sw=1.5))
    f.append(line(adc_x + 36, mix_q_y, dsp_x - 65, mix_q_y, sw=1.5))
    f.append(block(dsp_x, dsp_y, 130, 95, "DSP Модем", "AGC · CFO · Demod\nRSSI / LQI\nFSK / LoRa CSS", fill="#eef2ff", stroke="#4f46e5", sw=2))

    # Кадровий процесор (Packet Engine & FIFO)
    pe_x, pe_y = 585, 305
    f.append(line(dsp_x, dsp_y + 48, pe_x, pe_y - 45, sw=1.8))
    f.append(block(pe_x, pe_y, 130, 90, "Packet Handler", "Preamble · SyncWord\nCRC-16 · Whitening\nFIFO (64-256 B)", fill="#f0fdf4", stroke=FIELD, sw=2))

    # Зв'язок Packet Handler з мікроконтролером (SPI)
    spi_x, spi_y = 735, 305
    f.append(arrow(pe_x + 65, pe_y - 15, spi_x - 15, spi_y - 15, color=LINE, sw=1.5))
    f.append(arrow(spi_x - 15, spi_y + 15, pe_x + 65, pe_y + 15, color=LINE, sw=1.5))
    f.append(text(spi_x + 10, spi_y - 15, "MISO / IRQ", size=10, bold=True, anchor="start"))
    f.append(text(spi_x + 10, spi_y + 15, "MOSI / SCK / CS", size=10, bold=True, anchor="start"))
    f.append(text(spi_x + 10, spi_y + 35, "до МК (SPI)", size=11, color=MUTED, anchor="start"))

    # Пунктирний контур навколо чипа
    f.append(rect(80, 50, 640, 410, fill="none", stroke="#94a3b8", sw=1.5, rx=8))
    f.append(text(95, 70, "Кремнієвий кристал RFIC трансивера", size=11, color="#64748b", anchor="start", bold=True))

    render(os.path.join(IMG, 'transceiver-architecture.svg'), W, H, *f)


# ── 2. Zero-IF проти Low-IF архітектур ──────────────────────────────────────
def fig_iq_architectures():
    W, H = 760, 320
    f = []
    f.append(text(W / 2, 24, "Архітектури приймача: Пряме перетворення (Zero-IF) та Низька ПЧ (Low-IF)", size=14, bold=True))

    # Секція Zero-IF
    y1 = 105
    f.append(rect(30, 55, 340, 240, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    f.append(text(200, 78, "Zero-IF (Direct Conversion, f_IF = 0)", size=13, bold=True, color=NEG))
    f.append(block(115, y1 + 35, 120, 44, "RF Mixer", "f_LO = f_RF", fill="#eaf0fd", stroke=NEG))
    f.append(arrow(175, y1 + 35, 220, y1 + 35))
    f.append(block(280, y1 + 35, 95, 44, "Baseband (DC)", "ФНЧ + ADC", fill="#eef7f0", stroke=FIELD))
    f.append(text(200, y1 + 90, "Переваги: прості ФНЧ, без дзеркального каналу", size=11, color=FIELD, anchor="middle"))
    f.append(text(200, y1 + 110, "Вразливість: DC Offset (зсув нуля), флікер-шум 1/f", size=11, color=POS, anchor="middle"))
    f.append(text(200, y1 + 130, "Типово: Wi-Fi, BLE, широкосмугові системи", size=10, color=MUTED, anchor="middle"))

    # Секція Low-IF
    f.append(rect(390, 55, 340, 240, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    f.append(text(560, 78, "Low-IF (f_IF = 100 .. 450 kHz)", size=13, bold=True, color=POS))
    f.append(block(475, y1 + 35, 120, 44, "RF Mixer", "f_LO = f_RF ± f_IF", fill="#fdecea", stroke=POS))
    f.append(arrow(535, y1 + 35, 580, y1 + 35))
    f.append(block(640, y1 + 35, 95, 44, "ПЧ (f_IF)", "Смуговий + ADC", fill="#eef7f0", stroke=FIELD))
    f.append(text(560, y1 + 90, "Переваги: немає DC offset і 1/f шуму на нулі", size=11, color=FIELD, anchor="middle"))
    f.append(text(560, y1 + 110, "Вразливість: потрібне цифрове придушення дзеркала", size=11, color=POS, anchor="middle"))
    f.append(text(560, y1 + 130, "Типово: Sub-GHz FSK (CC1101, SX1262), Zigbee", size=10, color=MUTED, anchor="middle"))

    render(os.path.join(IMG, 'iq-zero-if-low-if.svg'), W, H, *f)


# ── 3. Структура апаратного пакета та FIFO ──────────────────────────────────
def fig_packet_frame():
    W, H = 760, 310
    f = []
    f.append(text(W / 2, 24, "Структура кадру в ефірі та апаратна обробка Packet Handler", size=14, bold=True))

    # Кадр у ефірі
    y0 = 85
    f.append(text(40, y0 - 15, "Кадр в ефірі (Over-The-Air Frame):", size=11, bold=True, anchor="start"))

    # Блоки кадру
    # 1. Преамбула (120px)
    f.append(rect(40, y0, 130, 50, fill="#e0e7ff", stroke="#4338ca", sw=1.5, rx=4))
    f.append(text(105, y0 + 20, "Преамбула", size=12, bold=True, color="#312e81"))
    f.append(text(105, y0 + 38, "0xAA / 0x55 (4-8B)", size=10, color=MUTED))

    # 2. Синхрослово (110px)
    f.append(rect(175, y0, 120, 50, fill="#fef3c7", stroke="#b45309", sw=1.5, rx=4))
    f.append(text(235, y0 + 20, "Sync Word", size=12, bold=True, color="#78350f"))
    f.append(text(235, y0 + 38, "Мережевий ID (2-4B)", size=10, color=MUTED))

    # 3. Довжина (70px)
    f.append(rect(300, y0, 80, 50, fill="#f3e8ff", stroke="#7e22ce", sw=1.5, rx=4))
    f.append(text(340, y0 + 20, "Length", size=11, bold=True, color="#581c87"))
    f.append(text(340, y0 + 38, "0..255 (1B)", size=10, color=MUTED))

    # 4. Корисні дані / Payload (200px)
    f.append(rect(385, y0, 200, 50, fill="#dcfce7", stroke="#15803d", sw=1.5, rx=4))
    f.append(text(485, y0 + 20, "Дані (Payload) + Скремблювання", size=12, bold=True, color="#14532d"))
    f.append(text(485, y0 + 38, "Data Whitening LFSR (1..64/255 байтів)", size=10, color=MUTED))

    # 5. CRC (120px)
    f.append(rect(590, y0, 130, 50, fill="#fee2e2", stroke="#b91c1c", sw=1.5, rx=4))
    f.append(text(655, y0 + 20, "CRC-16 / 32", size=12, bold=True, color="#7f1d1d"))
    f.append(text(655, y0 + 38, "Контрольна сума (2B)", size=10, color=MUTED))

    # Функції апаратної обробки нижче
    y1 = 180
    f.append(line(105, y0 + 50, 105, y1 - 10, sw=1.2, dash="3,3"))
    f.append(text(105, y1 + 5, "Бітова синхронізація", size=10, bold=True))
    f.append(text(105, y1 + 20, "AGC + Clock Slicer", size=9, color=MUTED))

    f.append(line(235, y0 + 50, 235, y1 - 10, sw=1.2, dash="3,3"))
    f.append(text(235, y1 + 5, "Вирівнювання байтів", size=10, bold=True))
    f.append(text(235, y1 + 20, "Початок пакетного FIFO", size=9, color=MUTED))

    f.append(line(485, y0 + 50, 485, y1 - 10, sw=1.2, dash="3,3"))
    f.append(text(485, y1 + 5, "Дескремблювання LFSR", size=10, bold=True))
    f.append(text(485, y1 + 20, "Запис у буфер RX FIFO", size=9, color=MUTED))

    f.append(line(655, y0 + 50, 655, y1 - 10, sw=1.2, dash="3,3"))
    f.append(text(655, y1 + 5, "Перевірка CRC", size=10, bold=True))
    f.append(text(655, y1 + 20, "Сигнал переривання IRQ", size=9, color=MUTED))

    # FIFO блок внизу
    y2 = 250
    f.append(rect(240, y2, 280, 45, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=4))
    f.append(text(380, y2 + 18, "Апаратний FIFO Буфер (Tx / Rx 64B)", size=12, bold=True))
    f.append(text(380, y2 + 35, "Автоматичне відкидання при помилці CRC", size=10, color=MUTED))

    render(os.path.join(IMG, 'packet-frame-structure.svg'), W, H, *f)


# ── 4. Автомат станів трансивера ─────────────────────────────────────────────
def fig_state_machine():
    W, H = 760, 360
    f = []
    f.append(text(W / 2, 24, "Автомат станів (FSM) та енергетичні профілі радіочіпа", size=14, bold=True))

    # Стани
    # SLEEP
    s1_x, s1_y = 100, 160
    f.append(block(s1_x, s1_y, 110, 60, "SLEEP", "0.2 .. 1.5 µA\nXO вимкнено", fill="#f1f5f9", stroke="#64748b"))

    # STANDBY / IDLE
    s2_x, s2_y = 290, 160
    f.append(block(s2_x, s2_y, 120, 60, "STANDBY / IDLE", "1.2 .. 2.0 mA\nXO працює", fill="#e0f2fe", stroke="#0284c7"))

    # SYNTH / FS
    s3_x, s3_y = 480, 160
    f.append(block(s3_x, s3_y, 110, 60, "SYNTH / FS", "4.0 .. 7.0 mA\nPLL залочено", fill="#fef3c7", stroke="#d97706"))

    # RX
    s4_x, s4_y = 660, 95
    f.append(block(s4_x, s4_y, 110, 56, "RX (Прийом)", "5.0 .. 12.0 mA\nLNA + DSP активні", fill="#eaf0fd", stroke=NEG))

    # TX
    s5_x, s5_y = 660, 225
    f.append(block(s5_x, s5_y, 110, 56, "TX (Передача)", "20 .. 140 mA\nPA активний", fill="#fdecea", stroke=POS))

    # Переходи
    # Sleep -> Standby
    f.append(arrow(s1_x + 55, s1_y - 12, s2_x - 60, s2_y - 12, color=LINE))
    f.append(text(195, s1_y - 20, "CSN low / Wakeup (~200µs)", size=9, color=MUTED))

    # Standby -> Sleep
    f.append(arrow(s2_x - 60, s2_y + 12, s1_x + 55, s1_y + 12, color=MUTED))
    f.append(text(195, s1_y + 24, "CMD_SLEEP", size=9, color=MUTED))

    # Standby -> Synth
    f.append(arrow(s2_x + 60, s2_y, s3_x - 55, s3_y, color=LINE))
    f.append(text(385, s2_y - 10, "PLL Lock (~50µs)", size=9, color=MUTED))

    # Synth -> RX
    f.append(arrow(s3_x + 55, s3_y - 15, s4_x - 55, s4_y + 10, color=NEG))
    f.append(text(560, 110, "CMD_RX", size=10, bold=True, color=NEG))

    # Synth -> TX
    f.append(arrow(s3_x + 55, s3_y + 15, s5_x - 55, s5_y - 10, color=POS))
    f.append(text(560, 205, "CMD_TX", size=10, bold=True, color=POS))

    # RX -> Standby (RxDone / Timeout)
    f.append(line(s4_x, s4_y - 28, s4_x, 40, sw=1.2, color=MUTED))
    f.append(line(s4_x, 40, s2_x, 40, sw=1.2, color=MUTED))
    f.append(arrow(s2_x, 40, s2_x, s2_y - 30, color=MUTED))
    f.append(text(480, 52, "RX_DONE / Timeout (Auto Standby)", size=9, color=MUTED))

    # TX -> Standby (TxDone)
    f.append(line(s5_x, s5_y + 28, s5_x, 310, sw=1.2, color=MUTED))
    f.append(line(s5_x, 310, s2_x, 310, sw=1.2, color=MUTED))
    f.append(arrow(s2_x, 310, s2_x, s2_y + 30, color=MUTED))
    f.append(text(480, 300, "TX_DONE (Packet Sent)", size=9, color=MUTED))

    render(os.path.join(IMG, 'transceiver-state-machine.svg'), W, H, *f)


if __name__ == '__main__':
    fig_transceiver_arch()
    fig_iq_architectures()
    fig_packet_frame()
    fig_state_machine()
    print("All figures generated successfully.")

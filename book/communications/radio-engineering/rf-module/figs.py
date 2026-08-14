# -*- coding: utf-8 -*-
import sys
import os

# Adjust path to import svgkit from scripts directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

out_dir = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(out_dir, exist_ok=True)

def fig_architecture():
    w, h = 800, 380
    frags = []

    # Title
    frags.append(text(w / 2, 28, "Архітектура радіомодуля та межа з хост-контролером", size=16, bold=True))

    # Host MCU Box (Left)
    mcu_box = rect(30, 60, 160, 280, fill="#eef2f7", stroke="#4a5568", sw=2, rx=8)
    frags.append(mcu_box)
    frags.append(text(110, 85, "Хост-контролер", size=14, bold=True, color="#1a365d"))
    frags.append(text(110, 105, "(MCU / SoC)", size=12, italic=True, color="#4a5568"))

    # MCU Pins / Blocks
    frags.append(fitbox(45, 125, 130, 32, "SPI (SCK, MOSI, MISO, CS)", size=11, fill="#ffffff", stroke="#cbd5e1"))
    frags.append(fitbox(45, 165, 130, 32, "Переривання (IRQ/DIO)", size=11, fill="#ffffff", stroke="#cbd5e1"))
    frags.append(fitbox(45, 205, 130, 32, "GPIO (T/R, EN, RST)", size=11, fill="#ffffff", stroke="#cbd5e1"))
    frags.append(fitbox(45, 275, 130, 45, "LDO 3.3V\n+ Фільтрація", size=11, fill="#dcfce7", stroke="#16a34a"))

    # RF Module Shielding Box (Center)
    shield_box = rect(230, 60, 420, 280, fill="#f8fafc", stroke="#2563eb", sw=2, rx=10)
    frags.append(shield_box)
    frags.append(text(440, 85, "Металевий екран радіомодуля (Shielding Can)", size=13, bold=True, color="#1e40af"))

    # Transceiver IC inside module
    rfic_box = fitbox(250, 115, 140, 140, "Трансивер (RFIC)\n\n• Модем & Квадратура\n• Синтезатор (PLL/VCO)\n• ЦАП / АЦП & FIFO", size=11, fill="#dbeafe", stroke="#2563eb", bold=True)
    frags.append(rfic_box)

    # TCXO Box
    tcxo_box = fitbox(250, 270, 140, 50, "Опорний генератор\nTCXO (26-32 МГц)", size=11, fill="#fef3c7", stroke="#d97706", bold=True)
    frags.append(tcxo_box)
    frags.append(line(320, 255, 320, 270, color="#d97706", sw=1.5))

    # Matching & Balun Box
    balun_box = fitbox(420, 150, 95, 70, "Узгодження &\nБалун\n(50 Ом)", size=11, fill="#ffffff", stroke="#64748b")
    frags.append(balun_box)

    # FEM Box
    fem_box = fitbox(540, 120, 95, 130, "Фронтенд (FEM)\n\n• PA (+20 dBm)\n• LNA (Low NF)\n• T/R Перемикач", size=10, fill="#fee2e2", stroke="#dc2626", bold=True)
    frags.append(fem_box)

    # Bandpass Filter Box
    bpf_box = fitbox(540, 265, 95, 55, "Фільтр гармонік\n(BPF / LPF)", size=10, fill="#ffffff", stroke="#64748b")
    frags.append(bpf_box)

    # Connections inside Module
    frags.append(arrow(390, 185, 420, 185, color="#2563eb", sw=1.8))
    frags.append(arrow(515, 185, 540, 185, color="#2563eb", sw=1.8))
    frags.append(arrow(587, 250, 587, 265, color="#dc2626", sw=1.5))

    # Antenna Port (Right)
    ant_box = fitbox(680, 155, 90, 80, "Роз'єм антени\n(IPEX / SMA)\n50 Ом", size=11, fill="#f1f5f9", stroke="#334155", bold=True)
    frags.append(ant_box)
    frags.append(arrow(635, 185, 680, 185, color="#dc2626", sw=2))

    # Interconnect arrows Host <-> Module
    frags.append(arrow(175, 140, 250, 140, color="#2563eb", sw=1.5))
    frags.append(arrow(250, 180, 175, 180, color="#2563eb", sw=1.5))
    frags.append(arrow(175, 220, 250, 220, color="#475569", sw=1.5))
    frags.append(arrow(175, 295, 230, 295, color="#16a34a", sw=1.8))

    render(os.path.join(out_dir, "rf-module-architecture.svg"), w, h, *frags)

def fig_fem():
    w, h = 760, 320
    frags = []

    frags.append(text(w / 2, 26, "Тракт сигналу у фронтенд-модулі (FEM): Передача і Прийом", size=16, bold=True))

    # Transceiver Interface (Left)
    frags.append(rect(30, 70, 120, 210, fill="#dbeafe", stroke="#2563eb", sw=1.5, rx=6))
    frags.append(text(90, 160, "Трансивер\n(RFIC)", size=13, bold=True, color="#1e40af"))

    # TX Path (Top) - Red
    frags.append(text(280, 85, "Тракт передачі (TX Path)", size=12, bold=True, color="#dc2626"))
    frags.append(arrow(150, 115, 210, 115, color="#dc2626", sw=2))
    frags.append(fitbox(210, 90, 140, 50, "Підсилювач потужності\n(PA, +20...+30 dBm)", size=11, fill="#fee2e2", stroke="#dc2626", bold=True))
    frags.append(arrow(350, 115, 470, 115, color="#dc2626", sw=2))

    # RX Path (Bottom) - Blue
    frags.append(text(280, 265, "Тракт прийому (RX Path)", size=12, bold=True, color="#2563eb"))
    frags.append(arrow(470, 235, 350, 235, color="#2563eb", sw=2))
    frags.append(fitbox(210, 210, 140, 50, "Малошумний підсилювач\n(LNA, Gain 15dB, NF 1.5dB)", size=11, fill="#dbeafe", stroke="#2563eb", bold=True))
    frags.append(arrow(210, 235, 150, 235, color="#2563eb", sw=2))

    # T/R Switch (Center-Right)
    frags.append(rect(470, 90, 100, 170, fill="#fef3c7", stroke="#d97706", sw=1.8, rx=6))
    frags.append(mtext(520, 140, "T/R\nПеремикач\n(RF Switch)", size=11, bold=True, color="#78350f"))
    frags.append(arrow(520, 280, 520, 260, color="#d97706", sw=1.5))
    frags.append(text(520, 295, "Сигнал CTRL (GPIO)", size=11, color="#78350f"))

    # BPF and Antenna (Right)
    frags.append(arrow(570, 175, 610, 175, color="#334155", sw=2))
    frags.append(fitbox(610, 145, 110, 60, "Фільтр гармонік\n& Антена (50 Ом)", size=11, fill="#f1f5f9", stroke="#334155", bold=True))

    render(os.path.join(out_dir, "fem-signal-path.svg"), w, h, *frags)

def fig_layout():
    w, h = 760, 320
    frags = []

    frags.append(text(w / 2, 26, "Топологія розведення радіомодуля на системній платі", size=16, bold=True))

    # Host PCB Frame
    frags.append(rect(20, 50, 720, 240, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))

    # RF Module (Left)
    frags.append(rect(40, 70, 180, 200, fill="#e2e8f0", stroke="#334155", sw=2, rx=6))
    frags.append(mtext(130, 140, "Радіомодуль\nз екраном\n\n[ Castellated Pads ]", size=12, bold=True, color="#1e293b"))

    # 50 Ohm Microstrip (Middle)
    frags.append(line(220, 170, 480, 170, color="#dc2626", sw=4))
    frags.append(text(350, 155, "Мікросмужкова лінія 50 Ом", size=12, bold=True, color="#dc2626"))

    # Via Fencing
    for x in range(230, 480, 25):
        frags.append(circle(x, 140, 3, fill="#94a3b8", stroke="#475569", sw=1))
        frags.append(circle(x, 200, 3, fill="#94a3b8", stroke="#475569", sw=1))
    frags.append(text(350, 220, "Захисний паркан із переходів на землю (Via Fencing)", size=11, italic=True, color="#475569"))

    # Keepout Zone (Right)
    frags.append(rect(500, 70, 210, 200, fill="#fef2f2", stroke="#ef4444", sw=1.5, rx=6))
    frags.append(mtext(605, 120, "Зона відчуження\n(Antenna Keepout)\n\n• Без міді й землі\n• Без трасування\n• Антена PCB / IPEX", size=11, bold=True, color="#991b1b"))

    render(os.path.join(out_dir, "matching-and-layout.svg"), w, h, *frags)

if __name__ == "__main__":
    fig_architecture()
    fig_fem()
    fig_layout()
    print("Figures generated successfully.")

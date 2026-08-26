# -*- coding: utf-8 -*-
import sys
import os

# Four levels up to scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), "img"), exist_ok=True)

def fig_topologies():
    w, h = 920, 540
    frags = []
    
    # Title & Subtitle
    frags.append(text(w / 2, 28, "Топології шин на польотному контролері", size=18, bold=True))
    frags.append(text(w / 2, 48, "Розподіл датчиків і зв'язку за фізичним рівнем та лініями сигналів", size=13, color=MUTED))
    
    # Central MCU block
    mcu_x, mcu_y, mcu_w, mcu_h = 320, 75, 260, 395
    frags.append(rect(mcu_x, mcu_y, mcu_w, mcu_h, fill="#eef2f7", stroke="#2c3e50", sw=2, rx=8))
    frags.append(text(mcu_x + mcu_w / 2, mcu_y + 24, "Мікроконтролер (MCU)", size=15, bold=True, color="#2c3e50"))
    frags.append(text(mcu_x + mcu_w / 2, mcu_y + 40, "STM32H7 / F7 / RP2040", size=12, color=MUTED))
    
    # --- UART Section (Top Left) ---
    gps_box = fitbox(30, 95, 170, 60, "GPS / GNSS модуль\n(UBX / NMEA потік)", size=12, fill="#fdfefe", stroke=LINE)
    frags.append(gps_box)
    
    telem_box = fitbox(30, 185, 170, 60, "Радіомодем / ELRS\n(Телеметрія польоту)", size=12, fill="#fdfefe", stroke=LINE)
    frags.append(telem_box)
    
    # MCU UART Ports (Inside MCU on left side)
    frags.append(rect(mcu_x + 8, 120, 85, 45, fill="#ffffff", stroke="#7f8c8d", sw=1.2, rx=4))
    frags.append(text(mcu_x + 50, 138, "UART 1", size=12, bold=True))
    frags.append(text(mcu_x + 50, 153, "RX1 / TX1", size=10, color=MUTED))
    
    frags.append(rect(mcu_x + 8, 195, 85, 45, fill="#ffffff", stroke="#7f8c8d", sw=1.2, rx=4))
    frags.append(text(mcu_x + 50, 213, "UART 2", size=12, bold=True))
    frags.append(text(mcu_x + 50, 228, "RX2 / TX2", size=10, color=MUTED))
    
    # UART connection lines
    frags.append(line(200, 130, mcu_x + 8, 130, color=POS, sw=1.8))
    frags.append(line(200, 150, mcu_x + 8, 150, color=NEG, sw=1.8))
    frags.append(text(250, 122, "TX → RX", size=10, color=POS))
    frags.append(text(250, 162, "RX ← TX", size=10, color=NEG))
    
    frags.append(line(200, 205, mcu_x + 8, 205, color=POS, sw=1.8))
    frags.append(line(200, 225, mcu_x + 8, 225, color=NEG, sw=1.8))
    frags.append(text(250, 197, "TX → RX", size=10, color=POS))
    frags.append(text(250, 237, "RX ← TX", size=10, color=NEG))
    
    # --- I2C Section (Bottom Left) ---
    frags.append(rect(mcu_x + 8, 295, 85, 55, fill="#ffffff", stroke="#7f8c8d", sw=1.2, rx=4))
    frags.append(text(mcu_x + 50, 317, "I²C 1", size=12, bold=True))
    frags.append(text(mcu_x + 50, 335, "SCL / SDA", size=10, color=MUTED))
    
    # I2C Devices
    baro_box = fitbox(30, 290, 170, 50, "Барометр (MS5611)\nАдреса 0x77", size=12, fill="#fdfefe", stroke=LINE)
    frags.append(baro_box)
    mag_box = fitbox(30, 370, 170, 50, "Компас (IST8310)\nАдреса 0x0E", size=12, fill="#fdfefe", stroke=LINE)
    frags.append(mag_box)
    
    # I2C Shared Bus Lines
    frags.append(line(235, 310, mcu_x + 8, 310, color="#d35400", sw=2)) # SCL
    frags.append(line(225, 330, mcu_x + 8, 330, color="#2980b9", sw=2)) # SDA
    frags.append(line(235, 310, 235, 405, color="#d35400", sw=2))
    frags.append(line(225, 330, 225, 385, color="#2980b9", sw=2))
    
    # Taps to devices
    frags.append(line(200, 310, 235, 310, color="#d35400", sw=2))
    frags.append(line(200, 330, 225, 330, color="#2980b9", sw=2))
    frags.append(line(200, 385, 225, 385, color="#2980b9", sw=2))
    frags.append(line(200, 405, 235, 405, color="#d35400", sw=2))
    
    # Pull-ups to 3.3V
    frags.append(line(230, 255, 230, 268, color=LINE, sw=1.5))
    frags.append(text(230, 250, "+3.3V", size=11, bold=True, color=POS))
    frags.append(rect(220, 268, 8, 16, fill="#ffffff", stroke=LINE, sw=1.2, rx=1))
    frags.append(rect(232, 268, 8, 16, fill="#ffffff", stroke=LINE, sw=1.2, rx=1))
    frags.append(line(224, 284, 224, 330, color="#2980b9", sw=1.5)) # to SDA
    frags.append(line(236, 284, 236, 310, color="#d35400", sw=1.5)) # to SCL
    frags.append(text(190, 276, "Rp 2.2k", size=9, color=MUTED))
    
    frags.append(text(275, 302, "SCL", size=10, color="#d35400", bold=True))
    frags.append(text(275, 342, "SDA", size=10, color="#2980b9", bold=True))
    
    # --- SPI Section (Right) ---
    frags.append(rect(mcu_x + mcu_w - 95, 120, 85, 120, fill="#ffffff", stroke="#7f8c8d", sw=1.2, rx=4))
    frags.append(text(mcu_x + mcu_w - 52, 140, "SPI 1", size=12, bold=True))
    frags.append(text(mcu_x + mcu_w - 52, 156, "SCK / MOSI", size=10, color=MUTED))
    frags.append(text(mcu_x + mcu_w - 52, 170, "MISO", size=10, color=MUTED))
    frags.append(text(mcu_x + mcu_w - 52, 198, "CS1..CS3", size=10, bold=True, color="#8e44ad"))
    
    # SPI Devices (Right)
    imu1_box = fitbox(700, 95, 180, 55, "Головний IMU\n(ICM-42688-P 8kHz)", size=12, fill="#fdfefe", stroke=LINE)
    frags.append(imu1_box)
    
    imu2_box = fitbox(700, 185, 180, 55, "Резервний IMU\n(BMI270 1.6kHz)", size=12, fill="#fdfefe", stroke=LINE)
    frags.append(imu2_box)
    
    flash_box = fitbox(700, 275, 180, 55, "Flash Blackbox\n(W25Q128 50MHz)", size=12, fill="#fdfefe", stroke=LINE)
    frags.append(flash_box)
    
    # Shared SPI bus trunk (SCK, MOSI, MISO)
    frags.append(line(mcu_x + mcu_w - 10, 135, 650, 135, color="#16a085", sw=2)) # SCK
    frags.append(line(mcu_x + mcu_w - 10, 148, 640, 148, color="#27ae60", sw=2)) # MOSI
    frags.append(line(mcu_x + mcu_w - 10, 161, 630, 161, color="#2980b9", sw=2)) # MISO
    
    # Vertical trunk
    frags.append(line(650, 135, 650, 290, color="#16a085", sw=2))
    frags.append(line(640, 148, 640, 305, color="#27ae60", sw=2))
    frags.append(line(630, 161, 630, 320, color="#2980b9", sw=2))
    
    # Taps to IMU1
    frags.append(line(650, 110, 700, 110, color="#16a085", sw=2))
    frags.append(line(640, 120, 700, 120, color="#27ae60", sw=2))
    frags.append(line(630, 130, 700, 130, color="#2980b9", sw=2))
    
    # Taps to IMU2
    frags.append(line(650, 200, 700, 200, color="#16a085", sw=2))
    frags.append(line(640, 210, 700, 210, color="#27ae60", sw=2))
    frags.append(line(630, 220, 700, 220, color="#2980b9", sw=2))
    
    # Taps to Flash
    frags.append(line(650, 290, 700, 290, color="#16a085", sw=2))
    frags.append(line(640, 305, 700, 305, color="#27ae60", sw=2))
    frags.append(line(630, 320, 700, 320, color="#2980b9", sw=2))
    
    # Dedicated CS lines
    frags.append(line(mcu_x + mcu_w - 10, 185, 700, 140, color="#8e44ad", sw=1.8, dash="4,3"))
    frags.append(line(mcu_x + mcu_w - 10, 195, 700, 230, color="#8e44ad", sw=1.8, dash="4,3"))
    frags.append(line(mcu_x + mcu_w - 10, 205, 620, 335, color="#8e44ad", sw=1.8, dash="4,3"))
    frags.append(line(620, 335, 700, 335, color="#8e44ad", sw=1.8, dash="4,3"))
    
    frags.append(text(615, 100, "SCK / MOSI / MISO", size=10, color="#16a085", bold=True))
    frags.append(text(595, 245, "Окремі CS (Active Low)", size=10, color="#8e44ad", bold=True))
    
    # Summary footer box
    frags.append(rect(30, 480, 860, 45, fill="#ffffff", stroke="#bdc3c7", sw=1.2, rx=6))
    frags.append(text(w / 2, 507, "UART: точка-точка, асинхронний • I²C: 2 дроти, мультидроп, до 1 Мбіт/с • SPI: 4+N дротів, push-pull, 10–50+ Мбіт/с", size=12, color=INK, bold=True))
    
    render(os.path.join(os.path.dirname(__file__), "img", "bus-topologies.svg"), w, h, *frags)

def fig_timing():
    w, h = 900, 520
    frags = []
    
    frags.append(text(w / 2, 26, "Порівняння часових діаграм транзакцій (UART, I²C, SPI)", size=18, bold=True))
    frags.append(text(w / 2, 46, "Фізичне кодування, синхронізація та накладні витрати передачі одного байта", size=13, color=MUTED))
    
    # --- UART TIMING BLOCK ---
    frags.append(rect(20, 65, 860, 125, fill="#fcfcfc", stroke="#bdc3c7", sw=1.2, rx=6))
    frags.append(text(90, 86, "UART (8-N-1): Немає лінії тактування, стробування по біт-рейту", size=13, bold=True, anchor="start"))
    
    tx_y_hi, tx_y_lo = 118, 152
    tx_points = [
        (50, tx_y_hi), (110, tx_y_hi), (110, tx_y_lo), # Start edge
        (160, tx_y_lo), (160, tx_y_hi),                 # D0 = 1
        (210, tx_y_hi), (210, tx_y_lo),                 # D1 = 0
        (260, tx_y_lo), (260, tx_y_hi),                 # D2 = 1
        (310, tx_y_hi), (310, tx_y_hi),                 # D3 = 1
        (360, tx_y_hi), (360, tx_y_lo),                 # D4 = 0
        (410, tx_y_lo), (410, tx_y_lo),                 # D5 = 0
        (460, tx_y_lo), (460, tx_y_hi),                 # D6 = 1
        (510, tx_y_hi), (510, tx_y_lo),                 # D7 = 0
        (560, tx_y_lo), (560, tx_y_hi),                 # Stop = 1
        (630, tx_y_hi)
    ]
    for i in range(len(tx_points) - 1):
        frags.append(line(tx_points[i][0], tx_points[i][1], tx_points[i+1][0], tx_points[i+1][1], color=INK, sw=2))
        
    frags.append(text(40, 138, "TX", size=13, bold=True, color=INK))
    
    frags.append(text(80, 108, "IDLE", size=10, color=MUTED))
    frags.append(text(135, 170, "START", size=10, bold=True, color=POS))
    frags.append(text(185, 108, "D0 (1)", size=10, color=NEG))
    frags.append(text(235, 170, "D1 (0)", size=10, color=NEG))
    frags.append(text(285, 108, "D2 (1)", size=10, color=NEG))
    frags.append(text(335, 108, "D3 (1)", size=10, color=NEG))
    frags.append(text(385, 170, "D4 (0)", size=10, color=NEG))
    frags.append(text(435, 170, "D5 (0)", size=10, color=NEG))
    frags.append(text(485, 108, "D6 (1)", size=10, color=NEG))
    frags.append(text(535, 170, "D7 (0)", size=10, color=NEG))
    frags.append(text(595, 108, "STOP", size=10, bold=True, color=FIELD))
    
    for x in [135, 185, 235, 285, 335, 385, 435, 485, 535, 595]:
        frags.append(line(x, 130, x, 142, color=POS, sw=1.5))
    frags.append(text(740, 135, "Вибірка (стробування)\nпо центру біта (16x оверсемплінг)", size=11, color=POS))
    
    # --- I2C TIMING BLOCK ---
    frags.append(rect(20, 200, 860, 155, fill="#fcfcfc", stroke="#bdc3c7", sw=1.2, rx=6))
    frags.append(text(90, 220, "I²C: Синхронна передача (START, адреса / дані, ACK/NACK, STOP)", size=13, bold=True, anchor="start"))
    
    scl_y_hi, scl_y_lo = 245, 275
    frags.append(text(40, 260, "SCL", size=13, bold=True, color="#d35400"))
    
    scl_pts = [(50, scl_y_hi), (110, scl_y_hi)]
    x_curr = 110
    for pulse in range(9):
        scl_pts.extend([
            (x_curr, scl_y_lo), (x_curr + 25, scl_y_lo),
            (x_curr + 25, scl_y_hi), (x_curr + 50, scl_y_hi)
        ])
        x_curr += 50
    scl_pts.extend([(x_curr, scl_y_hi), (x_curr + 40, scl_y_hi)])
    for i in range(len(scl_pts) - 1):
        frags.append(line(scl_pts[i][0], scl_pts[i][1], scl_pts[i+1][0], scl_pts[i+1][1], color="#d35400", sw=2))
        
    sda_y_hi, sda_y_lo = 295, 325
    frags.append(text(40, 310, "SDA", size=13, bold=True, color="#2980b9"))
    
    sda_pts = [
        (50, sda_y_hi), (80, sda_y_hi), (80, sda_y_lo), # START at x=80
        (130, sda_y_lo), (130, sda_y_hi),               # D7 = 1
        (180, sda_y_hi), (180, sda_y_lo),               # D6 = 0
        (230, sda_y_lo), (230, sda_y_hi),               # D5 = 1
        (280, sda_y_hi), (280, sda_y_hi),               # D4 = 1
        (330, sda_y_hi), (330, sda_y_lo),               # D3 = 0
        (380, sda_y_lo), (380, sda_y_lo),               # D2 = 0
        (430, sda_y_lo), (430, sda_y_hi),               # D1 = 1
        (480, sda_y_hi), (480, sda_y_lo),               # D0 = 0
        (530, sda_y_lo), (530, sda_y_lo),               # ACK (Slave pulls low)
        (570, sda_y_lo), (570, sda_y_hi), (620, sda_y_hi) # STOP
    ]
    for i in range(len(sda_pts) - 1):
        frags.append(line(sda_pts[i][0], sda_pts[i][1], sda_pts[i+1][0], sda_pts[i+1][1], color="#2980b9", sw=2))
        
    frags.append(text(80, 340, "START", size=10, bold=True, color=POS))
    frags.append(text(535, 340, "ACK (9-й такт)", size=10, bold=True, color=FIELD))
    frags.append(text(590, 340, "STOP", size=10, bold=True, color=POS))
    frags.append(text(740, 290, "Дані стабільні при SCL=1;\nзміна дозволена лише при SCL=0", size=11, color=MUTED))
    
    # --- SPI TIMING BLOCK ---
    frags.append(rect(20, 365, 860, 145, fill="#fcfcfc", stroke="#bdc3c7", sw=1.2, rx=6))
    frags.append(text(90, 385, "SPI (Mode 0: CPOL=0, CPHA=0): Повний дуплекс без підтверджень", size=13, bold=True, anchor="start"))
    
    # CS line
    frags.append(text(40, 410, "CS", size=13, bold=True, color="#8e44ad"))
    frags.append(line(50, 400, 80, 400, color="#8e44ad", sw=2))
    frags.append(line(80, 400, 80, 420, color="#8e44ad", sw=2))
    frags.append(line(80, 420, 560, 420, color="#8e44ad", sw=2))
    frags.append(line(560, 420, 560, 400, color="#8e44ad", sw=2))
    frags.append(line(560, 400, 630, 400, color="#8e44ad", sw=2))
    
    # SCK line (8 pulses)
    frags.append(text(40, 445, "SCK", size=13, bold=True, color="#16a085"))
    sck_pts = [(50, 455), (100, 455)]
    x_sck = 100
    for p in range(8):
        sck_pts.extend([
            (x_sck, 455), (x_sck + 25, 435),
            (x_sck + 25, 435), (x_sck + 50, 455)
        ])
        x_sck += 50
    sck_pts.append((630, 455))
    for i in range(len(sck_pts) - 1):
        frags.append(line(sck_pts[i][0], sck_pts[i][1], sck_pts[i+1][0], sck_pts[i+1][1], color="#16a085", sw=2))
        
    # MOSI / MISO lines
    frags.append(text(40, 480, "MOSI", size=11, bold=True, color="#27ae60"))
    frags.append(text(40, 495, "MISO", size=11, bold=True, color="#2980b9"))
    
    frags.append(line(50, 485, 100, 485, color="#27ae60", sw=1.8))
    frags.append(line(100, 485, 500, 485, color="#27ae60", sw=2))
    frags.append(line(500, 485, 630, 485, color="#27ae60", sw=1.8))
    
    frags.append(text(300, 478, "Одночасний побітовий зсув MSB..LSB на кожному фронті SCK", size=10, color=INK))
    frags.append(text(740, 435, "Full Duplex (двосторонній обмін)\nЧастоти: 10–50+ МГц\nБез адресних та ACK байтів", size=11, color=FIELD))
    
    render(os.path.join(os.path.dirname(__file__), "img", "bus-timing-comparison.svg"), w, h, *frags)

def fig_hal():
    w, h = 880, 520
    frags = []
    
    frags.append(text(w / 2, 28, "Архітектура уніфікованого шару абстракції датчиків (HAL)", size=18, bold=True))
    frags.append(text(w / 2, 48, "Ізоляція алгоритмів стабілізації від конкретної фізичної шини та контролера", size=13, color=MUTED))
    
    l1_box = fitbox(60, 75, 760, 60, "Рівень застосунку: Оцінка стану (EKF) та Контур стабілізації (PID 1–8 кГц)\nОтримує стандартизовані структури: imu_data_t (рад/с, м/с²), baro_data_t (Па, °C)", size=13, fill="#ebf5fb", stroke="#2980b9", sw=1.8, bold=True)
    frags.append(l1_box)
    
    frags.append(arrow(w / 2, 135, w / 2, 160, color=LINE, sw=2))
    
    frags.append(rect(60, 165, 760, 100, fill="#fdfefe", stroke="#7f8c8d", sw=1.5, rx=6))
    frags.append(text(180, 185, "Драйвери конкретних чипів (Sensor Drivers)", size=14, bold=True))
    
    d1 = fitbox(80, 195, 220, 55, "Драйвер ICM-42688-P\nКонфігурація ODR, FIFO, зчитування 14B", size=12, fill="#f4f6f8", stroke=LINE)
    d2 = fitbox(330, 195, 220, 55, "Драйвер MS5611 / BMP388\nКоманди перетворення, компенсація", size=12, fill="#f4f6f8", stroke=LINE)
    d3 = fitbox(580, 195, 220, 55, "Драйвер IST8310\nКалібрування поля, періодичне опитування", size=12, fill="#f4f6f8", stroke=LINE)
    frags.extend([d1, d2, d3])
    
    frags.append(arrow(190, 265, 190, 290, color=LINE, sw=2))
    frags.append(arrow(440, 265, 440, 290, color=LINE, sw=2))
    frags.append(arrow(690, 265, 690, 290, color=LINE, sw=2))
    
    l3_box = fitbox(60, 295, 760, 80, "Уніфікований інтерфейс шини (Bus Device Interface / C++ Concept)\ntransfer(tx_buf, tx_len, rx_buf, rx_len) • write_reg() • read_reg() • read_burst()\nАвтоматичне керування Chip Select (RAII), транзакціями та повторними спробами", size=13, fill="#fef9e7", stroke="#d35400", sw=2, bold=True)
    frags.append(l3_box)
    
    frags.append(arrow(200, 375, 200, 400, color=LINE, sw=2))
    frags.append(arrow(440, 375, 440, 400, color=LINE, sw=2))
    frags.append(arrow(680, 375, 680, 400, color=LINE, sw=2))
    
    h1 = fitbox(80, 405, 220, 75, "Реалізація SPI HAL\nКерування лінією CS,\nPrescaler, DMA Burst потік", size=12, fill="#f4f6f8", stroke="#16a085", sw=1.5)
    h2 = fitbox(330, 405, 220, 75, "Реалізація I²C HAL\nАдресація, ACK перевірка,\nBus Recovery авторозблокування", size=12, fill="#f4f6f8", stroke="#2980b9", sw=1.5)
    h3 = fitbox(580, 405, 220, 75, "Реалізація UART HAL\nКільцевий буфер (Ring Buffer),\nIDLE Interrupt + DMA RX", size=12, fill="#f4f6f8", stroke="#8e44ad", sw=1.5)
    frags.extend([h1, h2, h3])
    
    render(os.path.join(os.path.dirname(__file__), "img", "sensor-hal-architecture.svg"), w, h, *frags)

if __name__ == "__main__":
    fig_topologies()
    fig_timing()
    fig_hal()
    print("All figures generated successfully.")

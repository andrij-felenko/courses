# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
WARM_FILL = "#fff6e5"
RED_FILL = "#fdecea"
GREY_FILL = "#eceff1"
PURPLE_FILL = "#f3e8ff"

# ── 1. Схема архітектури NVMe-oF (Initiator -> Transport -> Target) ──
def fig_nvme_of_capsule_arch():
    W, H = 1000, 480
    p = []

    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="none"))

    # Контейнер Ініціатора
    p.append(rect(20, 20, 290, 440, fill=BLUE_FILL, stroke=LINE, rx=8))
    p.append(text(165, 45, "Хост Ініціатор (Initiator)", size=15, bold=True))

    p.append(rect(40, 70, 250, 110, fill="#ffffff", stroke=LINE, rx=4))
    p.append(text(165, 95, "Застосунок / Файлова система", size=13, bold=True))
    p.append(text(165, 120, "Буфери сторінок RAM", size=12, color="#555555"))
    p.append(text(165, 140, "Scatter-Gather List (SGL)", size=12, color="#555555"))

    p.append(rect(40, 200, 250, 130, fill=GREEN_FILL, stroke=LINE, rx=4))
    p.append(text(165, 225, "Драйвер nvme-fabrics", size=13, bold=True))
    p.append(text(165, 250, "Черги SQ / CQ (по ядрах)", size=12))
    p.append(text(165, 275, "Капсуляція SQE (64 Б)", size=12))
    p.append(text(165, 300, "Транспортний модуль (tcp/rdma)", size=11, color="#333333"))

    p.append(rect(40, 350, 250, 90, fill=GREY_FILL, stroke=LINE, rx=4))
    p.append(text(165, 375, "Мережевий адаптер (NIC / HCA)", size=13, bold=True))
    p.append(text(165, 400, "TCP Offload / RDMA Engine", size=12, color="#444444"))

    # Мережева фабрика
    p.append(rect(340, 140, 320, 220, fill=WARM_FILL, stroke=LINE, rx=8))
    p.append(text(500, 170, "Мережева фабрика (Fabric)", size=16, bold=True))
    p.append(text(500, 200, "Ethernet (TCP/IP) / InfiniBand / RoCEv2", size=12, color="#555555"))
    
    # Капсули в польоті
    p.append(rect(370, 230, 260, 45, fill="#ffffff", stroke=LINE, rx=4))
    p.append(text(500, 255, "Command Capsule (SQE + SGL)", size=12, bold=True, color="#1a5fb4"))
    
    p.append(rect(370, 290, 260, 45, fill="#ffffff", stroke=LINE, rx=4))
    p.append(text(500, 315, "Response Capsule (CQE Status)", size=12, bold=True, color="#26a269"))

    # Контейнер Таргета
    p.append(rect(690, 20, 290, 440, fill=PURPLE_FILL, stroke=LINE, rx=8))
    p.append(text(835, 45, "Сервер Таргет (Target)", size=15, bold=True))

    p.append(rect(710, 70, 250, 90, fill=GREY_FILL, stroke=LINE, rx=4))
    p.append(text(835, 95, "Мережевий адаптер Таргета", size=13, bold=True))
    p.append(text(835, 120, "Прийом капсул / DMA в RAM", size=12, color="#444444"))

    p.append(rect(710, 180, 250, 150, fill=GREEN_FILL, stroke=LINE, rx=4))
    p.append(text(835, 205, "Підсистема ядра nvmet", size=13, bold=True))
    p.append(text(835, 230, "Транспортний шар nvmet-tcp/rdma", size=12))
    p.append(text(835, 255, "Декапсуляція команд SQE", size=12))
    p.append(text(835, 280, "Парсинг NQN та NSID", size=12))
    p.append(text(835, 305, "Власна пара черг SQ/CQ", size=11, color="#333333"))

    p.append(rect(710, 350, 250, 90, fill="#ffffff", stroke=LINE, rx=4))
    p.append(text(835, 375, "Локальні NVMe SSD / Block Devices", size=13, bold=True))
    p.append(text(835, 400, "Фізичний PCIe DMA / NVM", size=12, color="#555555"))

    # Стрілки
    p.append(arrow(290, 395, 340, 395))
    p.append(arrow(340, 250, 290, 250))
    p.append(arrow(660, 250, 690, 250))
    p.append(arrow(690, 395, 660, 395))

    render(os.path.join(IMG, 'nvme-of-capsule-arch.svg'), W, H, *p)


# ── 2. Схема обміну PDU у NVMe/TCP (Read & Write) ──
def fig_nvme_tcp_pdu_sequence():
    W, H = 960, 520
    p = []

    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="none"))

    # Вертикальні лінії лінійок часу
    hx, tx = 220, 740
    p.append(line(hx, 60, hx, 480, color="#999999", sw=2, dash="4,4"))
    p.append(line(tx, 60, tx, 480, color="#999999", sw=2, dash="4,4"))

    p.append(textbox(hx, 35, ["Хост (Initiator)"], size=14, bold=True, fill=BLUE_FILL, stroke=LINE)[0])
    p.append(textbox(tx, 35, ["Контролер (Target)"], size=14, bold=True, fill=PURPLE_FILL, stroke=LINE)[0])

    # 1. Ініціалізація з'єднання
    p.append(arrow(hx, 90, tx, 90))
    p.append(textbox(480, 80, ["ICReq (Initialize Connection Request)"], size=11, fill="#ffffff", stroke=LINE)[0])

    p.append(arrow(tx, 120, hx, 120))
    p.append(textbox(480, 110, ["ICResp (Initialize Connection Response)"], size=11, fill="#ffffff", stroke=LINE)[0])

    p.append(line(80, 145, 880, 145, color="#dddddd", sw=1))
    p.append(text(480, 160, "--- Операція Читання (NVMe Read Command) ---", size=12, bold=True, color="#555555"))

    # 2. Читання
    p.append(arrow(hx, 185, tx, 185))
    p.append(textbox(480, 175, ["CmdKVec PDU (SQE Read + SGL Descriptor)"], size=11, fill=BLUE_FILL, stroke=LINE)[0])

    p.append(arrow(tx, 235, hx, 235))
    p.append(textbox(480, 225, ["C2HData PDU (Data Payload + Data Digest CRC32)"], size=11, fill=GREEN_FILL, stroke=LINE)[0])

    p.append(arrow(tx, 280, hx, 280))
    p.append(textbox(480, 270, ["RspKVec PDU (CQE Completion Status)"], size=11, fill=WARM_FILL, stroke=LINE)[0])

    p.append(line(80, 310, 880, 310, color="#dddddd", sw=1))
    p.append(text(480, 325, "--- Операція Запису (NVMe Write Command) ---", size=12, bold=True, color="#555555"))

    # 3. Запис
    p.append(arrow(hx, 350, tx, 350))
    p.append(textbox(480, 340, ["CmdKVec PDU (SQE Write + In-capsule or SGL)"], size=11, fill=BLUE_FILL, stroke=LINE)[0])

    p.append(arrow(tx, 395, hx, 395))
    p.append(textbox(480, 385, ["R2T PDU (Ready to Transfer: Offset & Length)"], size=11, fill=RED_FILL, stroke=LINE)[0])

    p.append(arrow(hx, 440, tx, 440))
    p.append(textbox(480, 430, ["H2CData PDU (Host to Controller Data Payload)"], size=11, fill=GREEN_FILL, stroke=LINE)[0])

    p.append(arrow(tx, 475, hx, 475))
    p.append(textbox(480, 465, ["RspKVec PDU (CQE Status Success)"], size=11, fill=WARM_FILL, stroke=LINE)[0])

    render(os.path.join(IMG, 'nvme-tcp-pdu-sequence.svg'), W, H, *p)


# ── 3. Схема прямого доступу RDMA (Zero-Copy RDMA Read/Write) ──
def fig_nvme_rdma_direct_transfer():
    W, H = 960, 460
    p = []

    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="none"))

    # Хост RAM
    p.append(rect(30, 40, 380, 380, fill=BLUE_FILL, stroke=LINE, rx=8))
    p.append(text(220, 70, "Оперативна пам'ять Хоста (Host RAM)", size=15, bold=True))

    p.append(rect(50, 100, 340, 100, fill="#ffffff", stroke=LINE, rx=4))
    p.append(text(220, 125, "Зареєстрований буфер даних (MR)", size=13, bold=True))
    p.append(text(220, 150, "Віртуальна адреса: 0x7fff8000", size=11, color="#555555"))
    p.append(text(220, 170, "rkey (Remote Key): 0x0042a1b0", size=11, color="#880000", bold=True))

    p.append(rect(50, 230, 340, 160, fill=GREEN_FILL, stroke=LINE, rx=4))
    p.append(text(220, 255, "RDMA Queue Pair (QP)", size=13, bold=True))
    p.append(text(220, 280, "Send Queue (SQ) / Receive Queue (RQ)", size=12))
    p.append(text(220, 310, "Капсула команди містить Keyed SGL Descriptor:", size=11, color="#333333"))
    p.append(text(220, 335, "[Address: 0x7fff8000 | Length: 64KB | Key: 0x0042a1b0]", size=10, bold=True))

    # Таргет RAM та NIC
    p.append(rect(550, 40, 380, 380, fill=PURPLE_FILL, stroke=LINE, rx=8))
    p.append(text(740, 70, "Сервер Таргет (Target NVMe)", size=15, bold=True))

    p.append(rect(570, 100, 340, 120, fill=WARM_FILL, stroke=LINE, rx=4))
    p.append(text(740, 125, "RDMA NIC (RNIC / InfiniBand HCA)", size=13, bold=True))
    p.append(text(740, 150, "Апаратний HW Engine прямого DMA", size=12))
    p.append(text(740, 175, "Автономна валідація rkey та прав", size=11, color="#555555"))

    p.append(rect(570, 250, 340, 140, fill="#ffffff", stroke=LINE, rx=4))
    p.append(text(740, 275, "Локальний NVMe Контролер", size=13, bold=True))
    p.append(text(740, 300, "Прямий DMA у буфер RNIC", size=12))
    p.append(text(740, 325, "Низькі затримки без виклику CPU", size=11, color="#26a269", bold=True))

    # Зв'язки RDMA Operations
    p.append(arrow(390, 300, 570, 160))
    p.append(textbox(475, 215, ["1. RDMA Send: Command Capsule + Keyed SGL"], size=10, fill="#ffffff", stroke=LINE)[0])

    p.append(arrow(570, 180, 390, 150))
    p.append(textbox(475, 275, ["2. RDMA Read/Write: Пряме DMA по rkey"], size=10, fill=GREEN_FILL, stroke=LINE)[0])

    p.append(arrow(570, 200, 390, 340))
    p.append(textbox(475, 335, ["3. RDMA Send: Response Capsule (CQE)"], size=10, fill=WARM_FILL, stroke=LINE)[0])

    render(os.path.join(IMG, 'nvme-rdma-direct-transfer.svg'), W, H, *p)


if __name__ == '__main__':
    fig_nvme_of_capsule_arch()
    fig_nvme_tcp_pdu_sequence()
    fig_nvme_rdma_direct_transfer()
    print("SVG figures generated successfully.")

import os
import sys

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import render, textbox, fitbox, rect, line, arrow, text, mtext, circle, POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG

def build_fig1():
    # Порівняння Традиційного мережевого стека Linux та RDMA (Kernel Bypass + Zero-Copy)
    w, h = 820, 480
    frags = []

    # Заголовок
    frags.append(text(w / 2, 25, "Порівняння шляху даних: Традиційний TCP/IP стек vs RDMA", size=16, bold=True))

    # Скляний бокс для TCP/IP
    frags.append(rect(20, 55, 375, 395, fill="#fdfefe", stroke="#bdc3c7", sw=1.5, rx=8))
    frags.append(text(207, 78, "Традиційний стек (TCP/IP)", size=15, bold=True, color="#c0392b"))

    # Скляний бокс для RDMA
    frags.append(rect(425, 55, 375, 395, fill="#f4f9f4", stroke="#abebc6", sw=1.5, rx=8))
    frags.append(text(612, 78, "Шлях RDMA (Kernel Bypass)", size=15, bold=True, color="#27ae60"))

    # TCP/IP шари
    tb_u1, _, _ = textbox(207, 120, "Користувацький додаток\n(User Space Buffer)", size=12, pad=8, fill="#ebf5fb", stroke="#2980b9")
    tb_k1, _, _ = textbox(207, 210, "Ядро Linux (Kernel Space)\nБуфери socket & sk_buff\nКопіювання пам'яті CPU", size=12, pad=8, fill="#fadbd8", stroke="#e74c3c")
    tb_d1, _, _ = textbox(207, 300, "Драйвер та мережева карта\n(NIC DMA / Ring Buffer)", size=12, pad=8, fill="#eaeded", stroke="#7f8c8d")
    tb_n1, _, _ = textbox(207, 390, "Мережевий дріт (Ethernet)", size=12, pad=8, fill="#d5dbdb", stroke="#34495e")

    frags.extend([tb_u1, tb_k1, tb_d1, tb_n1])

    # TCP/IP стрілки
    frags.append(arrow(207, 145, 207, 182, color="#c0392b", sw=2))
    frags.append(text(217, 163, "Копіювання + Syscall", size=10, color="#c0392b", anchor="left"))

    frags.append(arrow(207, 245, 207, 278, color="#c0392b", sw=2))
    frags.append(text(217, 261, "Переривання + DMA", size=10, color="#c0392b", anchor="left"))

    frags.append(arrow(207, 325, 207, 368, color="#7f8c8d", sw=2))

    # RDMA шари
    tb_u2, _, _ = textbox(612, 120, "Користувацький додаток\n(Закріплена пам'ять / MR)", size=12, pad=8, fill="#e8f8f5", stroke="#1abc9c")
    tb_k2, _, _ = textbox(612, 210, "Ядро Linux (Control Path)\nРеєстрація MR / Налаштування QP\n(Критичний шлях ОБІЙДЕНО)", size=11, pad=8, fill="#f9ebf9", stroke="#8e44ad", sw=1.0)
    tb_d2, _, _ = textbox(612, 300, "RDMA Адаптер (RNIC / HCA)\nHardware Transport Engine", size=12, pad=8, fill="#d4efdf", stroke="#27ae60")
    tb_n2, _, _ = textbox(612, 390, "Фабрика (InfiniBand / RoCE)", size=12, pad=8, fill="#d5dbdb", stroke="#27ae60")

    frags.extend([tb_u2, tb_k2, tb_d2, tb_n2])

    # RDMA Пряма стрілка (Zero-Copy)
    frags.append(line(520, 140, 480, 140, color="#27ae60", sw=2))
    frags.append(line(480, 140, 480, 280, color="#27ae60", sw=2, dash="4,4"))
    frags.append(arrow(480, 280, 520, 280, color="#27ae60", sw=2))
    frags.append(text(473, 210, "Прямий DMA\n(Zero-Copy)", size=11, color="#27ae60", anchor="end", bold=True))

    frags.append(arrow(612, 325, 612, 368, color="#27ae60", sw=2))

    # Пунктирна лінія від ядра до HCA (керування)
    frags.append(line(612, 240, 612, 275, color="#8e44ad", sw=1.2, dash="2,2"))
    frags.append(text(622, 258, "Лише Setup", size=10, color="#8e44ad", anchor="left"))

    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    out_path = os.path.join(img_dir, 'rdma-arch.svg')
    render(out_path, w, h, *frags)
    print(f"Generated {out_path}")

def build_fig2():
    # Архітектура абстракцій RDMA: PD, QP (SQ/RQ), CQ, MR та HCA
    w, h = 820, 480
    frags = []

    frags.append(text(w / 2, 25, "Внутрішні абстракції RDMA: Protection Domain, QP, CQ та MR", size=16, bold=True))

    # Рамка процесу користувача
    frags.append(rect(20, 50, 780, 290, fill="#fbfcfc", stroke="#34495e", sw=1.5, rx=8))
    frags.append(text(40, 72, "Пам'ять процесу у просторі користувача (User Space Process)", size=13, bold=True, color="#2c3e50", anchor="left"))

    # Protection Domain (PD)
    frags.append(rect(40, 85, 740, 245, fill="#f4f6f7", stroke="#8e44ad", sw=1.5, rx=6))
    frags.append(text(55, 105, "Protection Domain (PD) — Домен безпеки", size=12, bold=True, color="#8e44ad", anchor="left"))

    # Queue Pair (QP)
    frags.append(rect(55, 120, 310, 125, fill="#ebf5fb", stroke="#2980b9", sw=1.5, rx=6))
    frags.append(text(210, 140, "Queue Pair (QP)", size=13, bold=True, color="#1b4f72"))

    tb_sq, _, _ = textbox(130, 185, "Send Queue (SQ)\n[WQE1 -> WQE2]", size=11, pad=6, fill="#d4e6f1", stroke="#2980b9")
    tb_rq, _, _ = textbox(290, 185, "Receive Queue (RQ)\n[WQE1 -> WQE2]", size=11, pad=6, fill="#d4e6f1", stroke="#2980b9")
    frags.extend([tb_sq, tb_rq])

    # Memory Region (MR)
    frags.append(rect(380, 120, 385, 125, fill="#e8f8f5", stroke="#16a085", sw=1.5, rx=6))
    frags.append(text(572, 140, "Memory Region (MR) [Pinned RAM]", size=13, bold=True, color="#0e6655"))

    tb_mr, _, _ = textbox(572, 185, "Віртуальні сторінки пам'яті\nL_Key: Локальний доступ | R_Key: Віддалений доступ", size=11, pad=6, fill="#a3e4d7", stroke="#16a085")
    frags.append(tb_mr)

    # Completion Queue (CQ) внизу всередині PD
    frags.append(rect(55, 255, 710, 60, fill="#fef9e7", stroke="#f39c12", sw=1.5, rx=6))
    tb_cqe, _, _ = textbox(410, 285, "Completion Queue (CQ): [CQE1] [CQE2] [CQE3] (Асинхронний статус виконання)", size=11, pad=6, fill="#fdebd0", stroke="#f39c12")
    frags.append(tb_cqe)

    # Апаратний рівень HCA
    frags.append(rect(20, 365, 780, 95, fill="#eaeded", stroke="#2c3e50", sw=2, rx=8))
    frags.append(text(410, 390, "RDMA Network Interface Card (RNIC / HCA Hardware)", size=14, bold=True, color="#1b2631"))

    tb_hca_engine, _, _ = textbox(410, 425, "Hardware DMA Controller  |  Translation & Protection Table (TPT)  |  Transport Engine", size=11, pad=6, fill="#d5dbdb", stroke="#34495e")
    frags.append(tb_hca_engine)

    # Зв'язки між пластами
    frags.append(arrow(130, 230, 130, 365, color="#2980b9", sw=1.5))
    frags.append(arrow(290, 230, 290, 365, color="#2980b9", sw=1.5))
    frags.append(arrow(572, 230, 572, 365, color="#16a085", sw=1.5))

    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    out_path = os.path.join(img_dir, 'rdma-qp-mr.svg')
    render(out_path, w, h, *frags)
    print(f"Generated {out_path}")

if __name__ == '__main__':
    build_fig1()
    build_fig2()

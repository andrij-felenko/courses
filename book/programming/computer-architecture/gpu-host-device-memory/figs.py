# -*- coding: utf-8 -*-
"""Генератор фігур для теми 'Моделі пам'яті Host і Device'."""

import sys
import os

# scripts/ знаходиться на 4 рівні вище
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, text, mtext, rect, line, arrow, circle, textbox, fitbox,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG, FONT
)

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_heterogeneous_topology():
    """Фігура 1: Архітектурна топологія гетерогенної пам'яті."""
    w, h = 880, 430
    frags = []

    # Заголовок / Підкладки систем
    frags.append(rect(20, 45, 340, 365, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(190, 75, "ХОСТ (Host CPU System)", size=16, color=INK, bold=True))
    frags.append(text(190, 95, "Оптимізовано під мінімальну затримку (Latency-oriented)", size=11, color=MUTED))

    frags.append(rect(520, 45, 340, 365, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    frags.append(text(690, 75, "ПРИСТРІЙ (Device GPU System)", size=16, color=INK, bold=True))
    frags.append(text(690, 95, "Оптимізовано під масивну пропускну здатність (Throughput)", size=11, color=MUTED))

    # Вузли всередині Host
    b_cpu, _, _ = textbox(190, 140, "Багатоядерний CPU\n(Кеші L1 / L2 / L3)", size=13, pad=10, fill="#ffffff", stroke=LINE, min_w=280)
    frags.append(b_cpu)

    b_hram, _, _ = textbox(190, 240, "Системна пам'ять DDR4 / DDR5\nЄмність: 64–512 ГБ\nПропускна здатність: ~50–120 ГБ/с\nЗатримка: ~60–90 нс", size=12, pad=10, fill="#ffffff", stroke=NEG, min_w=280)
    frags.append(b_hram)

    frags.append(arrow(190, 172, 190, 203, color=LINE, sw=2))
    frags.append(text(190, 190, "Шинний контролер ОЗП (128-біт)", size=11, color=MUTED))

    b_iommu, _, _ = textbox(190, 360, "IOMMU / Контролер PCIe Root\nТрансляція адрес DMA", size=12, pad=8, fill="#ffffff", stroke=LINE, min_w=280)
    frags.append(b_iommu)
    frags.append(arrow(190, 285, 190, 335, color=LINE, sw=2))

    # Вузли всередині Device
    b_gpu, _, _ = textbox(690, 140, "Масив обчислювальних ядер GPU\n(Потокові мультипроцесори SM / CU)", size=13, pad=10, fill="#ffffff", stroke=LINE, min_w=280)
    frags.append(b_gpu)

    b_vram, _, _ = textbox(690, 240, "Відеопам'ять GDDR6 / HBM3\nЄмність: 16–96 ГБ\nПропускна здатність: 1 000–3 300 ГБ/с\nШирина шини: 384–4096 біт", size=12, pad=10, fill="#ffffff", stroke=FIELD, min_w=280)
    frags.append(b_vram)

    frags.append(arrow(690, 172, 690, 203, color=LINE, sw=2))
    frags.append(text(690, 190, "Локальна надширока шина VRAM", size=11, color=FIELD, bold=True))

    b_dma, _, _ = textbox(690, 360, "Апаратний DMA Engine GPU\nКерування копіюванням через PCIe", size=12, pad=8, fill="#ffffff", stroke=LINE, min_w=280)
    frags.append(b_dma)
    frags.append(arrow(690, 285, 690, 335, color=LINE, sw=2))

    # Міжсистемна шина PCIe (Вузьке горло)
    frags.append(rect(370, 320, 140, 80, fill="#fef2f2", stroke=POS, sw=2, rx=6))
    frags.append(mtext(440, 345, "Шина PCIe 4.0/5.0 x16\n31.5 – 63 ГБ/с\n(Вузьке горло)", size=12, color=POS, bold=True, lh=1.2))

    frags.append(arrow(330, 360, 370, 360, color=POS, sw=2.2))
    frags.append(arrow(510, 360, 550, 360, color=POS, sw=2.2))

    # Порівняльна винесення різниці пропускної здатності
    frags.append(rect(370, 110, 140, 170, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(440, 130, "Розрив швидкості:", size=11, color=INK, bold=True))
    frags.append(mtext(440, 155, "VRAM швидша за\nPCIe у 30–100 разів!\n\nЯкщо дані не в\nлокальній VRAM —\nGPU простоює.", size=11, color=POS, lh=1.25))

    render(os.path.join(IMG_DIR, "heterogeneous-memory-topology.svg"), w, h, *frags)


def fig_pageable_vs_pinned():
    """Фігура 2: Порівняння Pageable Memory (подвійний буфер) та Pinned Memory (прямий DMA)."""
    w, h = 880, 410
    frags = []

    # Верхня частина: Pageable
    frags.append(rect(15, 30, 850, 170, fill="#fff7ed", stroke="#fdba74", sw=1.5, rx=8))
    frags.append(text(440, 55, "СХЕМА А: Звичайна сторінкова пам'ять (Pageable Memory, malloc)", size=14, color=POS, bold=True))

    b1, _, _ = textbox(110, 115, "Сторінковий буфер\nHost Virtual Memory\n(malloc / new)", size=11, pad=8, fill="#ffffff", stroke=LINE, min_w=160)
    frags.append(b1)

    b2, _, _ = textbox(360, 115, "Транзитний буфер ядра\n(Pinned Staging Buffer)\nВиділений драйвером", size=11, pad=8, fill="#fee2e2", stroke=POS, min_w=170)
    frags.append(b2)

    b3, _, _ = textbox(620, 115, "Контролер DMA\nна карті GPU", size=11, pad=8, fill="#ffffff", stroke=LINE, min_w=140)
    frags.append(b3)

    b4, _, _ = textbox(795, 115, "Пам'ять GPU\n(Device VRAM)", size=11, pad=8, fill="#f0fdf4", stroke=FIELD, min_w=110)
    frags.append(b4)

    frags.append(arrow(190, 115, 275, 115, color=POS, sw=2))
    frags.append(text(232, 100, "Крок 1: CPU memcpy", size=10, color=POS, bold=True))
    frags.append(text(232, 135, "(копіювання в ядрі)", size=9, color=MUTED))

    frags.append(arrow(445, 115, 550, 115, color=POS, sw=2))
    frags.append(text(497, 100, "Крок 2: PCIe DMA", size=10, color=POS, bold=True))
    frags.append(text(497, 135, "(пересилка в залізі)", size=9, color=MUTED))

    frags.append(arrow(690, 115, 740, 115, color=FIELD, sw=2))

    frags.append(text(440, 175, "Подвійне копіювання: CPU зайнятий переписуванням байтів, подвійне навантаження на шину ОЗП", size=11, color=POS, italic=True))

    # Нижня частина: Pinned
    frags.append(rect(15, 220, 850, 170, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    frags.append(text(440, 245, "СХЕМА Б: Фіксована пам'ять (Pinned / Page-Locked Memory, cudaMallocHost)", size=14, color=FIELD, bold=True))

    b5, _, _ = textbox(140, 305, "Фіксований буфер Host\n(Фізичні сторінки заблоковані\nвід витискання ОС)", size=11, pad=8, fill="#ffffff", stroke=FIELD, min_w=200)
    frags.append(b5)

    b6, _, _ = textbox(520, 305, "Контролер DMA на GPU\n(Знає точні фізичні адреси RAM)", size=11, pad=8, fill="#ffffff", stroke=LINE, min_w=220)
    frags.append(b6)

    b7, _, _ = textbox(780, 305, "Пам'ять GPU\n(Device VRAM)", size=11, pad=8, fill="#ffffff", stroke=FIELD, min_w=120)
    frags.append(b7)

    frags.append(arrow(240, 305, 410, 305, color=FIELD, sw=2.5))
    frags.append(text(325, 290, "Прямий трансфер PCIe DMA (1 крок)", size=11, color=FIELD, bold=True))
    frags.append(text(325, 325, "CPU повністю вільний, 100% утилізація шини", size=10, color=INK))

    frags.append(arrow(630, 305, 720, 305, color=FIELD, sw=2))

    frags.append(text(440, 365, "Прямий DMA: максимальна пропускна здатність PCIe, нульове навантаження на процесорні ядра", size=11, color=FIELD, italic=True))

    render(os.path.join(IMG_DIR, "pageable-vs-pinned-dma.svg"), w, h, *frags)


def fig_unified_page_fault():
    """Фігура 3: Життєвий цикл апаратного Page Fault у Unified Memory."""
    w, h = 880, 420
    frags = []

    # 6 послідовних кроків обробки
    frags.append(rect(15, 20, 850, 385, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(440, 45, "Життєвий цикл апаратного GPU Page Fault (Unified Memory)", size=16, color=INK, bold=True))

    # Стовпчик 1: Кроки 1-3
    s1, _, _ = textbox(230, 110, "1. Потік GPU звертається до адреси\n(Сторінка фізично знаходиться в Host RAM)", size=12, pad=8, fill="#ffffff", stroke=LINE, min_w=390)
    frags.append(s1)

    s2, _, _ = textbox(230, 195, "2. GPU MMU фіксує промах сторінки\n(Invalid bit в таблиці сторінок GPU → Page Fault)", size=12, pad=8, fill="#fef2f2", stroke=POS, min_w=390)
    frags.append(s2)
    frags.append(arrow(230, 140, 230, 165, color=LINE, sw=1.8))

    s3, _, _ = textbox(230, 280, "3. Апаратний блок GPU зупиняє варп\n(Генерує переривання/подію до драйвера на Host)", size=12, pad=8, fill="#ffffff", stroke=LINE, min_w=390)
    frags.append(s3)
    frags.append(arrow(230, 225, 230, 250, color=LINE, sw=1.8))

    # Стовпчик 2: Кроки 4-6
    s4, _, _ = textbox(650, 110, "4. Драйвер виділяє сторінку у VRAM\n(Ініціює фоновий DMA-трансфер 64 КБ / 2 МБ через PCIe)", size=12, pad=8, fill="#fffbeb", stroke="#f59e0b", min_w=390)
    frags.append(s4)
    frags.append(arrow(425, 280, 455, 110, color=POS, sw=2))
    frags.append(text(440, 200, "PCIe подія", size=10, color=POS, bold=True))

    s5, _, _ = textbox(650, 195, "5. Оновлення сторінкових таблиць\n(Запис нового фізичного фрейму у GPU TLB)", size=12, pad=8, fill="#ffffff", stroke=LINE, min_w=390)
    frags.append(s5)
    frags.append(arrow(650, 140, 650, 165, color=LINE, sw=1.8))

    s6, _, _ = textbox(650, 280, "6. Відновлення виконання варпу\n(Інструкція повторюється і читає вже з швидкої VRAM)", size=12, pad=8, fill="#f0fdf4", stroke=FIELD, min_w=390)
    frags.append(s6)
    frags.append(arrow(650, 225, 650, 250, color=FIELD, sw=1.8))

    # Висновок унизу
    frags.append(rect(35, 340, 810, 50, fill="#f1f5f9", stroke="#94a3b8", sw=1.2, rx=6))
    frags.append(mtext(440, 365, "Ціна гнучкості: кожен Page Fault займає кілька мікросекунд на обслуговування переривання.\nБез попереднього підтягування (cudaMemPrefetchAsync) масивні промахи руйнують продуктивність.", size=11, color=INK, bold=False, lh=1.25))

    render(os.path.join(IMG_DIR, "unified-page-fault-lifecycle.svg"), w, h, *frags)


def fig_stream_pipelining():
    """Фігура 4: Часова діаграма конвеєризації передачі та обчислень (Streams + Double Buffering)."""
    w, h = 880, 390
    frags = []

    frags.append(rect(15, 20, 850, 355, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(440, 45, "Порівняння: Послідовне виконання vs Асинхронний конвеєр потоків (CUDA Streams)", size=15, color=INK, bold=True))

    # Частина 1: Послідовне виконання
    frags.append(text(40, 80, "Синхронно (1 потік / Default Stream):", size=12, color=INK, anchor="start", bold=True))

    # 3 блоки по черзі
    # Блок 0
    frags.append(rect(40, 95, 120, 30, fill="#fed7aa", stroke="#ea580c", sw=1.2))
    frags.append(text(100, 115, "H2D [0]", size=11, color="#9a3412", bold=True))

    frags.append(rect(160, 95, 120, 30, fill="#bbf7d0", stroke="#16a34a", sw=1.2))
    frags.append(text(220, 115, "Обчислення [0]", size=11, color="#166534", bold=True))

    frags.append(rect(280, 95, 120, 30, fill="#bfdbfe", stroke="#2563eb", sw=1.2))
    frags.append(text(340, 115, "D2H [0]", size=11, color="#1e40af", bold=True))

    # Блок 1
    frags.append(rect(400, 95, 120, 30, fill="#fed7aa", stroke="#ea580c", sw=1.2))
    frags.append(text(460, 115, "H2D [1]", size=11, color="#9a3412", bold=True))

    frags.append(rect(520, 95, 120, 30, fill="#bbf7d0", stroke="#16a34a", sw=1.2))
    frags.append(text(580, 115, "Обчислення [1]", size=11, color="#166534", bold=True))

    frags.append(rect(640, 95, 120, 30, fill="#bfdbfe", stroke="#2563eb", sw=1.2))
    frags.append(text(700, 115, "D2H [1]", size=11, color="#1e40af", bold=True))

    frags.append(line(40, 140, 840, 140, color="#e2e8f0", sw=1.5, dash="4,4"))

    # Частина 2: Конвеєр з 3 чергами
    frags.append(text(40, 165, "Асинхронний конвеєр (3 Streams / Double Buffering):", size=12, color=FIELD, anchor="start", bold=True))

    # Рядок DMA H2D Engine
    frags.append(text(110, 205, "Рушій DMA H2D:", size=11, color=INK, anchor="end"))
    frags.append(rect(120, 190, 110, 26, fill="#fed7aa", stroke="#ea580c", sw=1.2))
    frags.append(text(175, 207, "H2D [0]", size=10, color="#9a3412", bold=True))

    frags.append(rect(230, 190, 110, 26, fill="#fed7aa", stroke="#ea580c", sw=1.2))
    frags.append(text(285, 207, "H2D [1]", size=10, color="#9a3412", bold=True))

    frags.append(rect(340, 190, 110, 26, fill="#fed7aa", stroke="#ea580c", sw=1.2))
    frags.append(text(395, 207, "H2D [2]", size=10, color="#9a3412", bold=True))

    frags.append(rect(450, 190, 110, 26, fill="#fed7aa", stroke="#ea580c", sw=1.2))
    frags.append(text(505, 207, "H2D [3]", size=10, color="#9a3412", bold=True))

    # Рядок Compute SMs Engine
    frags.append(text(110, 245, "Рушій SMs (Ядра):", size=11, color=INK, anchor="end"))
    frags.append(rect(230, 230, 110, 26, fill="#bbf7d0", stroke="#16a34a", sw=1.2))
    frags.append(text(285, 247, "Обчисл [0]", size=10, color="#166534", bold=True))

    frags.append(rect(340, 230, 110, 26, fill="#bbf7d0", stroke="#16a34a", sw=1.2))
    frags.append(text(395, 247, "Обчисл [1]", size=10, color="#166534", bold=True))

    frags.append(rect(450, 230, 110, 26, fill="#bbf7d0", stroke="#16a34a", sw=1.2))
    frags.append(text(505, 247, "Обчисл [2]", size=10, color="#166534", bold=True))

    frags.append(rect(560, 230, 110, 26, fill="#bbf7d0", stroke="#16a34a", sw=1.2))
    frags.append(text(615, 247, "Обчисл [3]", size=10, color="#166534", bold=True))

    # Рядок DMA D2H Engine
    frags.append(text(110, 285, "Рушій DMA D2H:", size=11, color=INK, anchor="end"))
    frags.append(rect(340, 270, 110, 26, fill="#bfdbfe", stroke="#2563eb", sw=1.2))
    frags.append(text(395, 287, "D2H [0]", size=10, color="#1e40af", bold=True))

    frags.append(rect(450, 270, 110, 26, fill="#bfdbfe", stroke="#2563eb", sw=1.2))
    frags.append(text(505, 287, "D2H [1]", size=10, color="#1e40af", bold=True))

    frags.append(rect(560, 270, 110, 26, fill="#bfdbfe", stroke="#2563eb", sw=1.2))
    frags.append(text(615, 287, "D2H [2]", size=10, color="#1e40af", bold=True))

    frags.append(rect(670, 270, 110, 26, fill="#bfdbfe", stroke="#2563eb", sw=1.2))
    frags.append(text(725, 287, "D2H [3]", size=10, color="#1e40af", bold=True))

    # Стрілка часу
    frags.append(arrow(40, 325, 820, 325, color=LINE, sw=2))
    frags.append(text(830, 328, "Час", size=11, color=INK, anchor="start", bold=True))

    frags.append(rect(230, 345, 440, 22, fill="#f0fdf4", stroke=FIELD, sw=1, rx=4))
    frags.append(text(450, 360, "Зона 100% утилізації: обчислення і пересилки виконуються паралельно!", size=10, color=FIELD, bold=True))

    render(os.path.join(IMG_DIR, "stream-pipelining-timeline.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_heterogeneous_topology()
    fig_pageable_vs_pinned()
    fig_unified_page_fault()
    fig_stream_pipelining()
    print("Всі 4 фігури успішно згенеровано.")

# -*- coding: utf-8 -*-
"""Фігури до статті «NVMe». Вивід — ./img/*.svg. Швидко, без залежностей."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_flow():
    """Шлях однієї команди: хост → дзвінок → контролер (DMA) → завершення → перепин."""
    W, H = 780, 470
    p = []

    # --- дві зони: RAM хоста (ліворуч) і накопичувач (праворуч) ---
    p.append(rect(20, 60, 430, 390, fill="#ffffff", stroke=MUTED, sw=1.5, rx=10))
    p.append(text(235, 82, "RAM хоста", size=14, color=MUTED, bold=True))
    p.append(rect(560, 60, 200, 390, fill="#ffffff", stroke=MUTED, sw=1.5, rx=10))
    p.append(text(660, 82, "Накопичувач NVMe", size=13, color=MUTED, bold=True))

    # шина PCIe між ними
    p.append(rect(470, 200, 72, 110, fill="#eef6ef", stroke=FIELD, sw=1.5, rx=8))
    p.append(mtext(506, 245, ["шина", "PCIe"], size=13, color=FIELD, bold=True))

    # --- черга подавання SQ (кільце-масив клітинок) ---
    p.append(text(120, 118, "черга подавання (SQ)", size=13, bold=True))
    cx = 55
    for i in range(6):
        fill = "#fdecea" if i < 3 else FILL   # перші три — заповнені командами
        p.append(rect(cx + i * 62, 128, 58, 34, fill=fill, stroke=LINE, sw=1.3, rx=5))
    p.append(text(55 + 1 * 62 + 29, 150, "cmd", size=12, color=POS))
    p.append(text(55 + 0 * 62 + 29, 150, "cmd", size=12, color=POS))
    p.append(text(55 + 2 * 62 + 29, 150, "cmd", size=12, color=POS))
    p.append(text(55 + 0 * 62 + 29, 178, "голова", size=10, color=MUTED))
    p.append(text(55 + 3 * 62 + 29, 178, "хвіст", size=10, color=MUTED))

    # --- черга завершення CQ ---
    p.append(text(120, 300, "черга завершення (CQ)", size=13, bold=True))
    for i in range(6):
        fill = "#eef6ef" if i < 2 else FILL
        p.append(rect(cx + i * 62, 310, 58, 34, fill=fill, stroke=LINE, sw=1.3, rx=5))
    p.append(text(55 + 0 * 62 + 29, 332, "done", size=12, color=FIELD))
    p.append(text(55 + 1 * 62 + 29, 332, "done", size=12, color=FIELD))

    # --- дзвінок (регістр на пристрої) ---
    db = fitbox(575, 120, 170, 46, "ДЗВІНОК\n(регістр на пристрої)",
                size=12, fill="#fdecea", stroke=POS, sw=1.6, bold=True, color=POS)
    p.append(db)

    # --- ядро-контролер ---
    p.append(rect(575, 200, 170, 60, fill=FILL, stroke=LINE, sw=1.6, rx=8))
    p.append(mtext(660, 226, ["контролер", "(бере команду, веде DMA)"], size=12, bold=False))

    # --- перепин ---
    ir = fitbox(575, 300, 170, 46, "ПЕРЕПИН MSI-X\n(будить ядро хоста)",
                size=12, fill="#eef0fd", stroke=NEG, sw=1.6, bold=True, color=NEG)
    p.append(ir)

    # --- стрілки потоку (нумеровані) ---
    # 1: хост дзвонить (SQ хвіст → дзвінок)
    p.append(arrow(300, 145, 573, 143, color=POS, sw=2))
    p.append(text(430, 133, "① дзвінок: новий хвіст", size=11, color=POS, bold=True))
    # 2: контролер читає команду з SQ
    p.append(arrow(660, 200, 300, 162, color=INK, sw=1.8))
    p.append(text(455, 190, "② читає команду", size=11, color=INK))
    # 3: DMA даних у RAM (жирна зелена)
    p.append(arrow(575, 235, 300, 235, color=FIELD, sw=2.4))
    p.append(text(415, 226, "③ DMA даних (повз процесор)", size=11, color=FIELD, bold=True))
    # 4: контролер пише завершення в CQ
    p.append(arrow(660, 260, 300, 322, color=INK, sw=1.8))
    p.append(text(455, 300, "④ пише завершення", size=11, color=INK))
    # 5: перепин у хост
    p.append(arrow(575, 323, 300, 345, color=NEG, sw=2))
    p.append(text(430, 368, "⑤ перепин: «готово»", size=11, color=NEG, bold=True))

    # процесор хоста (унизу ліворуч) — лише роздає/приймає
    p.append(rect(40, 388, 200, 46, fill=FILL, stroke=LINE, sw=1.4, rx=8))
    p.append(mtext(140, 412, ["процесор хоста", "роздає команди, приймає готове"], size=11))

    render(os.path.join(IMG, "nvme-flow.svg"), W, H, *p,
           title="Одна команда NVMe: увесь шлях по спільній пам'яті")


def fig_queues():
    """Стара розмова (одна черга на 32, замок) проти NVMe (багато глибоких черг)."""
    W, H = 780, 420
    p = []

    # === ліворуч: AHCI/SATA — одне віконце ===
    p.append(text(200, 66, "AHCI / SATA — одне віконце", size=15, bold=True, color=POS))
    # чотири ядра тиснуться до однієї черги
    for i in range(4):
        y = 100 + i * 46
        p.append(rect(40, y, 92, 34, fill=FILL, stroke=LINE, sw=1.3, rx=6))
        p.append(text(86, y + 22, "ядро %d" % (i + 1), size=12))
        p.append(arrow(134, y + 17, 236, 190, color=MUTED, sw=1.5))

    # замок на вході
    lk = fitbox(210, 168, 70, 44, "ЗАМОК", size=12, fill="#fdecea",
                stroke=POS, sw=1.8, bold=True, color=POS)
    p.append(lk)
    # єдина коротка черга (32)
    p.append(rect(210, 232, 150, 40, fill=FILL, stroke=LINE, sw=1.6, rx=6))
    p.append(mtext(285, 250, ["1 черга", "глибина 32"], size=12, bold=True))
    p.append(arrow(285, 214, 285, 230, color=POS, sw=2))
    # накопичувач
    p.append(rect(210, 312, 150, 40, fill="#eef6ef", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(285, 336, "накопичувач", size=12))
    p.append(arrow(285, 274, 285, 310, color=INK, sw=1.6))
    p.append(text(200, 388, "усі ядра чекають на замок", size=12, color=POS, italic=True))

    # роздільна лінія
    p.append(line(400, 56, 400, 396, color=MUTED, sw=1.2, dash="5,5"))

    # === праворуч: NVMe — кожному своя пара черг ===
    p.append(text(590, 66, "NVMe — кожному своя пара", size=15, bold=True, color=FIELD))
    for i in range(4):
        y = 100 + i * 62
        p.append(rect(430, y, 84, 30, fill=FILL, stroke=LINE, sw=1.3, rx=6))
        p.append(text(472, y + 20, "ядро %d" % (i + 1), size=12))
        # своя SQ+CQ, без замка
        p.append(rect(540, y - 4, 118, 18, fill="#fdecea", stroke=LINE, sw=1.1, rx=4))
        p.append(text(599, y + 9, "SQ (глибока)", size=10, color=POS))
        p.append(rect(540, y + 16, 118, 18, fill="#eef6ef", stroke=LINE, sw=1.1, rx=4))
        p.append(text(599, y + 29, "CQ", size=10, color=FIELD))
        p.append(arrow(516, y + 15, 538, y + 15, color=FIELD, sw=1.6))
        p.append(arrow(660, y + 15, 700, y + 15, color=INK, sw=1.4))

    # накопичувач праворуч
    p.append(rect(700, 100, 60, 216, fill="#eef6ef", stroke=FIELD, sw=1.5, rx=8))
    p.append(mtext(730, 200, ["на", "ко", "пи", "чу", "вач"], size=11))
    p.append(text(590, 388, "до 65535 черг · без замка", size=12, color=FIELD, italic=True))

    render(os.path.join(IMG, "nvme-queues.svg"), W, H, *p,
           title="Чому нова розмова: одне віконце проти багатьох черг")


def fig_timeline():
    """Стрічка часу: як дорослішала розмова — від AHCI/NVMHCI до NVMe 2.0."""
    W, H = 820, 430
    p = []

    # головна вісь часу
    axis_y = 150
    x0, x1 = 60, 760
    p.append(line(x0, axis_y, x1, axis_y, color=MUTED, sw=2))
    p.append(arrow(x1 - 4, axis_y, x1 + 4, axis_y, color=MUTED, sw=2))

    # віхи: (x, рік, підпис, колір, вгору?)
    milestones = [
        (110, "2004", ["AHCI", "черга 32"], MUTED, True),
        (250, "2007–08", ["NVMHCI", "(попередниця)"], MUTED, False),
        (400, "2011", ["NVMe 1.0", "1 берез."], POS, True),
        (530, "2012", ["NVMe 1.1", "multipath"], INK, False),
        (710, "2021", ["NVMe 2.0", "Base+набори"], FIELD, True),
    ]
    for x, year, cap, col, up in milestones:
        p.append(circle(x, axis_y, 7, fill=BG, stroke=col, sw=2.5))
        p.append(text(x, axis_y - 16 if up else axis_y + 26, year, size=13, bold=True, color=col))
        if up:
            box = fitbox(x - 58, axis_y - 92, 116, 40, "\n".join(cap),
                         size=12, fill=BG, stroke=col, sw=1.6, bold=True, color=col)
            p.append(box)
            p.append(line(x, axis_y - 52, x, axis_y - 9, color=col, sw=1.3, dash="3,3"))
        else:
            box = fitbox(x - 58, axis_y + 40, 116, 40, "\n".join(cap),
                         size=12, fill=BG, stroke=col, sw=1.6, bold=True, color=col)
            p.append(box)
            p.append(line(x, axis_y + 9, x, axis_y + 38, color=col, sw=1.3, dash="3,3"))

    # дві епохи під віссю
    p.append(text(180, axis_y + 118, "доба механічного диска", size=12, color=MUTED, italic=True))
    p.append(line(60, axis_y + 130, 320, axis_y + 130, color=MUTED, sw=1, dash="4,4"))
    p.append(text(560, axis_y + 118, "доба паралельного флеша", size=12, color=FIELD, italic=True))
    p.append(line(400, axis_y + 130, 760, axis_y + 130, color=FIELD, sw=1, dash="4,4"))

    # підпис-думка внизу
    note = fitbox(140, axis_y + 158, 540, 34,
                  "одна ідея з першого дня: багато черг у пам'яті хоста, без спільного замка",
                  size=12, fill="#eef6ef", stroke=FIELD, sw=1.3, color=INK)
    p.append(note)

    render(os.path.join(IMG, "nvme-timeline.svg"), W, H, *p,
           title="Як дорослішала розмова: віхи NVMe")


if __name__ == "__main__":
    fig_flow()
    fig_queues()
    fig_timeline()
    print("OK: nvme-flow.svg, nvme-queues.svg, nvme-timeline.svg")

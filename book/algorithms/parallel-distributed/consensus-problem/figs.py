# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фіг. 1: Властивості консенсусу (Agreement, Validity, Termination) ───────────
def fig_properties():
    W, H = 960, 380
    p = []

    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#ffffff", sw=0))
    p.append(text(W / 2, 32, "Три обов'язкові вимоги задачі розподіленого консенсусу", size=18, color=INK, bold=True))

    cards = [
        ("Узгодженість (Agreement)", "Одностайність рішення",
         "Жодні два коректні вузли не можуть\nприйняти різні рішення.\nФормально: якщо p вирішив v,\nа q вирішив u, то v = u.",
         "Без неї: розкол на табори (split-brain),\nсуперечливі стани реплік.", POS),
        ("Слушність (Validity)", "Змістовність вибору",
         "Прийняте значення мусить бути\nзапропоноване бодай одним вузлом.\nВиключає тривіальні алгоритми,\nде вузли завжди повертають 0.",
         "Без неї: фальшивий консенсус,\nсистема ігнорує реальні запити.", FIELD),
        ("Завершуваність (Termination)", "Гарантія живості",
         "Кожен коректний вузол рано чи пізно\nзобов'язаний прийняти рішення.\nПроцес не може зависнути\nв очікуванні назавжди.",
         "Без неї: вічний deadlock, система\nблокується під час збоїв (як у 2PC).", NEG),
    ]

    card_w = 285.0
    card_h = 280.0
    gap = 26.0
    start_x = (W - (3 * card_w + 2 * gap)) / 2
    top_y = 65.0

    for i, (title, sub, body, fail_note, col) in enumerate(cards):
        cx = start_x + i * (card_w + gap)
        p.append(rect(cx, top_y, card_w, card_h, fill="#fbfcfd", stroke="#d2d7df", sw=1.5, rx=10))
        # Top color accent bar
        p.append(rect(cx, top_y, card_w, 8, fill=col, stroke=col, sw=0, rx=4))
        p.append(text(cx + card_w / 2, top_y + 34, title, size=13.5, color=col, bold=True))
        p.append(text(cx + card_w / 2, top_y + 54, sub, size=11.5, color=MUTED, italic=True))
        p.append(line(cx + 15, top_y + 68, cx + card_w - 15, top_y + 68, color="#e5e9f0", sw=1.2))

        # Body explanation
        p.append(fitbox(cx + 12, top_y + 78, card_w - 24, 102, body, size=12,
                        fill="#ffffff", stroke="#e6ebf1", color=INK))

        # Failure consequence
        p.append(fitbox(cx + 12, top_y + 190, card_w - 24, 76, fail_note, size=11.5,
                        fill="#fdf7f7" if col == POS else ("#f7fbf8" if col == FIELD else "#f7f9fd"),
                        stroke=col, color=INK, bold=True))

    render(os.path.join(OUT, "consensus-properties.svg"), W, H, *p,
           title="Властивості розподіленого консенсусу")


# ── Фіг. 2: Спектр синхронності та межа FLP ─────────────────────────────────────
def fig_synchrony_spectrum():
    W, H = 960, 440
    p = []

    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#ffffff", sw=0))
    p.append(text(W / 2, 32, "Спектр моделей синхронності та теоретична межа консенсусу", size=18, color=INK, bold=True))

    models = [
        (40, 75, 270, 320, "Синхронна модель",
         "Відома верхня межа затримки Δ.\nГодинники синхронізовані.",
         "Консенсус розв'язний детерміновано\nнавіть за f збоїв за f+1 раундів.\nТайм-аут точно виявляє збій вузла.",
         "Практика: локальні шини, авіоніка,\nжорсткий реальний час.", FIELD),
        (345, 75, 270, 320, "Частково синхронна (DLS)",
         "Асинхронний хаос до часу GST;\nпісля GST затримки обмежені Δ.",
         "Безпека (Safety) гарантована завжди.\nЖивість (Liveness) гарантована\nпісля стабілізації мережі (GST).",
         "Практика: Paxos, Raft, Zab, etcd,\nZooKeeper, сучасні СУБД.", POS),
        (650, 75, 270, 320, "Асинхронна модель",
         "Затримки повідомлень довільні.\nГодинники дрейфують, збій невідрізнимий.",
         "Теорема FLP (1985):\nДетермінований консенсус неможливий\nнавіть при f = 1 збої аварійної зупинки.",
         "Вихід: рандомізація (Ben-Or),\nевристичні детектори збоїв (◇S).", NEG),
    ]

    for (bx, by, bw, bh, title, sub, desc, tech, col) in models:
        p.append(rect(bx, by, bw, bh, fill="#fafbfc", stroke="#d0d7de", sw=1.5, rx=10))
        p.append(rect(bx, by, bw, 6, fill=col, stroke=col, sw=0, rx=3))
        p.append(text(bx + bw / 2, by + 32, title, size=14, color=col, bold=True))
        p.append(fitbox(bx + 10, by + 48, bw - 20, 54, sub, size=11.5,
                        fill="#ffffff", stroke="#e1e4e8", color=MUTED))
        p.append(fitbox(bx + 10, by + 112, bw - 20, 108, desc, size=12,
                        fill="#ffffff", stroke="#d0d7de", color=INK, bold=True))
        p.append(fitbox(bx + 10, by + 230, bw - 20, 76, tech, size=11.5,
                        fill="#f6f8fa", stroke="#c3c8d0", color=INK))

    render(os.path.join(OUT, "synchrony-spectrum.svg"), W, H, *p,
           title="Спектр моделей синхронності")


# ── Фіг. 3: Дерево конфігурацій FLP (Бівалентність) ─────────────────────────────
def fig_flp_bivalence():
    W, H = 960, 480
    p = []

    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#ffffff", sw=0))
    p.append(text(W / 2, 30, "Бівалентність конфігурацій і нескінченний цикл затримки FLP", size=18, color=INK, bold=True))

    # Initial bivalent state C0
    c0_x, c0_y = 480.0, 80.0
    p.append(rect(c0_x - 110, c0_y - 20, 220, 42, fill="#fdf6e2", stroke="#b58900", sw=2, rx=8))
    p.append(text(c0_x, c0_y + 6, "C₀: Бівалентний стан (0 або 1)", size=13, color="#7d5a00", bold=True))

    # Branch left to 0-valent, right to 1-valent
    p.append(arrow(c0_x - 60, c0_y + 24, 210, 190, color=FIELD, sw=1.8))
    p.append(arrow(c0_x + 60, c0_y + 24, 750, 190, color=NEG, sw=1.8))

    # 0-valent node
    p.append(rect(100, 195, 220, 45, fill="#eef9f0", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(210, 223, "C₁: 0-валентний (вирішить 0)", size=13, color=FIELD, bold=True))

    # 1-valent node
    p.append(rect(640, 195, 220, 45, fill="#edf2fc", stroke=NEG, sw=1.8, rx=8))
    p.append(text(750, 223, "C₂: 1-валентний (вирішить 1)", size=13, color=NEG, bold=True))

    # Center branch: adversary delays message e, keeping it bivalent!
    p.append(arrow(c0_x, c0_y + 24, c0_x, 195, color=POS, sw=2.2))
    p.append(rect(340, 200, 280, 50, fill="#fdf0ed", stroke=POS, sw=2, rx=8))
    p.append(text(480, 222, "C': Знову бівалентний стан!", size=13, color=POS, bold=True))
    p.append(text(480, 238, "Супротивник затримав подію e = (p, m)", size=11, color=MUTED))

    # Cycle down
    p.append(arrow(c0_x, 252, c0_x, 320, color=POS, sw=2.2))
    p.append(rect(320, 325, 320, 52, fill="#fdf0ed", stroke=POS, sw=2, rx=8))
    p.append(text(480, 347, "C'': Нескінченне блукання бівалентністю", size=13, color=POS, bold=True))
    p.append(text(480, 364, "Система ніколи не переходить у 0- або 1-валентний стан", size=11, color=MUTED))

    p.append(line(480, 380, 480, 420, color=POS, sw=2, dash="4,4"))
    p.append(text(480, 440, "Завершуваність (Termination) не гарантується за асинхронного розкладу", size=13, color=POS, bold=True))

    # Side notes
    p.append(fitbox(40, 270, 240, 140, "Якщо алгоритм рухається\nдо 0-валентного стану,\nсупротивник доставляє подію e,\nяка повертає систему\nдо бівалентності.",
                    size=12, fill="#f8fafc", stroke="#cbd5e1", color=INK))
    p.append(fitbox(680, 270, 240, 140, "Лема алмазу (Diamond Lemma):\nякщо дві події e₁ та e₂\nстосуються різних вузлів,\nвони комутують:\ne₁(e₂(C)) = e₂(e₁(C)).",
                    size=12, fill="#f8fafc", stroke="#cbd5e1", color=INK))

    render(os.path.join(OUT, "flp-bivalence-tree.svg"), W, H, *p,
           title="Дерево конфігурацій FLP та бівалентність")


# ── Фіг. 4: Перетин кворумів (CFT: N >= 2f+1 vs BFT: N >= 3f+1) ─────────────────
def fig_quorum_intersection():
    W, H = 960, 420
    p = []

    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#ffffff", sw=0))
    p.append(text(W / 2, 32, "Геометрія кворумів: відмови із зупинкою (CFT) проти візантійських (BFT)", size=18, color=INK, bold=True))

    # Left Panel: CFT (N = 2f + 1, e.g. N = 5, f = 2)
    lx = 40.0
    lw = 420.0
    p.append(rect(lx, 65, lw, 330, fill="#fafbfc", stroke="#d0d7de", sw=1.5, rx=10))
    p.append(text(lx + lw / 2, 95, "CFT: Відмови з аварійною зупинкою", size=15, color=FIELD, bold=True))
    p.append(text(lx + lw / 2, 116, "Формула: N ≥ 2f + 1 (наприклад, N = 5, f = 2)", size=12, color=MUTED))

    # Segmented quorum representation: [Вузли лише Q1] [Перетин Q1 ∩ Q2] [Вузли лише Q2]
    # Q1 = {A, B, C}, Q2 = {C, D, E}
    box_y = 145.0
    box_h = 85.0
    # Left segment: Q1 unique {A, B}
    p.append(rect(lx + 25, box_y, 110, box_h, fill="#e8f5e9", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(lx + 80, box_y + 28, "Лише Q1", size=11, color=FIELD, bold=True))
    p.append(text(lx + 80, box_y + 54, "{A, B}", size=14, color=INK, bold=True))

    # Middle segment: Intersection {C}
    p.append(rect(lx + 150, box_y, 120, box_h, fill="#fff9c4", stroke="#fbc02d", sw=2.2, rx=6))
    p.append(text(lx + 210, box_y + 26, "Перетин (≥ 1)", size=11, color="#b78103", bold=True))
    p.append(text(lx + 210, box_y + 54, "Вузол {C}", size=15, color="#b78103", bold=True))

    # Right segment: Q2 unique {D, E}
    p.append(rect(lx + 285, box_y, 110, box_h, fill="#e3f2fd", stroke=NEG, sw=1.8, rx=6))
    p.append(text(lx + 340, box_y + 28, "Лише Q2", size=11, color=NEG, bold=True))
    p.append(text(lx + 340, box_y + 54, "{D, E}", size=14, color=INK, bold=True))

    p.append(fitbox(lx + 20, 250, lw - 40, 125,
                    "Будь-які два кворуми більшості (f+1 = 3) перетинаються:\n(f+1) + (f+1) - (2f+1) = 1 вузол.\nВузол {C} бачив попередній стан і голосування,\nтому новий лідер дізнається найсвіжіший запис.",
                    size=11.5, fill="#ffffff", stroke="#e1e4e8", color=INK))

    # Right Panel: BFT (N = 3f + 1, e.g. N = 4, f = 1 or N = 7, f = 2)
    rx = 500.0
    rw = 420.0
    p.append(rect(rx, 65, rw, 330, fill="#fafbfc", stroke="#d0d7de", sw=1.5, rx=10))
    p.append(text(rx + rw / 2, 95, "BFT: Візантійські (довільні) збої", size=15, color=POS, bold=True))
    p.append(text(rx + rw / 2, 116, "Формула: N ≥ 3f + 1 (наприклад, N = 4, f = 1, кворум 2f+1 = 3)", size=12, color=MUTED))

    # Segmented quorum representation: [Лише Q1] [Перетин Q1 ∩ Q2] [Лише Q2]
    # Q1 = {A, B, C}, Q2 = {B, C, D}, Intersection = {B, C} (size 2 = f+1)
    p.append(rect(rx + 25, box_y, 100, box_h, fill="#fbe9e7", stroke=POS, sw=1.8, rx=6))
    p.append(text(rx + 75, box_y + 28, "Лише Q1", size=11, color=POS, bold=True))
    p.append(text(rx + 75, box_y + 54, "{A}", size=14, color=INK, bold=True))

    # Middle segment: Intersection {B, C}
    p.append(rect(rx + 140, box_y, 140, box_h, fill="#fff9c4", stroke="#fbc02d", sw=2.2, rx=6))
    p.append(text(rx + 210, box_y + 26, "Перетин (≥ f+1 = 2)", size=11, color="#b78103", bold=True))
    p.append(text(rx + 210, box_y + 54, "Вузли {B, C}", size=14, color="#b78103", bold=True))

    # Right segment: Q2 unique {D}
    p.append(rect(rx + 295, box_y, 100, box_h, fill="#ede7f6", stroke="#673ab7", sw=1.8, rx=6))
    p.append(text(rx + 345, box_y + 28, "Лише Q2", size=11, color="#673ab7", bold=True))
    p.append(text(rx + 345, box_y + 54, "{D}", size=14, color=INK, bold=True))

    p.append(fitbox(rx + 20, 250, rw - 40, 125,
                    "Будь-які два кворуми розміру 2f+1 перетинаються по f+1 вузлах:\n(2f+1) + (2f+1) - (3f+1) = f+1 вузлів.\nОскільки зрадників щонайбільше f, у перетині {B, C}\nгарантовано є щонайменше 1 чесний вузол.",
                    size=11.5, fill="#ffffff", stroke="#e1e4e8", color=INK))

    render(os.path.join(OUT, "quorum-intersection.svg"), W, H, *p,
           title="Перетин кворумів у CFT та BFT моделях")


def main():
    fig_properties()
    fig_synchrony_spectrum()
    fig_flp_bivalence()
    fig_quorum_intersection()
    print("Усі 4 фігури успішно згенеровано.")


if __name__ == "__main__":
    main()

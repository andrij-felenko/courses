# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фіг. 1: Дворушництво лідера у CFT проти перехресного контролю в BFT ──────────
def fig_equivocation_failure():
    W, H = 960, 430
    p = []

    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#ffffff", sw=0))
    p.append(text(W / 2, 28, "Провал моделі аварійних зупинок (CFT) проти візантійського захисту (BFT)", size=17, color=INK, bold=True))

    # Ліва колонка: Провал CFT (Raft / Paxos)
    p.append(rect(30, 50, 435, 360, fill="#fdfbfb", stroke="#e8c4c4", sw=1.5, rx=8))
    p.append(rect(30, 50, 435, 32, fill="#f9e8e8", stroke="#e8c4c4", sw=1.5, rx=8))
    p.append(text(247, 72, "CFT (Raft / Paxos): довіра до лідера", size=13.5, color=POS, bold=True))

    p.append(fitbox(45, 90, 405, 45, "Лідер надсилає суперечливі пропозиції двом групам реплік.", size=12, fill="#ffffff", stroke="#f0d0d0", color=INK))

    # Лідер зверху
    p.append(rect(185, 145, 125, 36, fill="#fee2e2", stroke=POS, sw=1.5, rx=6))
    p.append(text(247, 168, "Лідер (зрадник)", size=12, color=POS, bold=True))

    # Репліки знизу
    p.append(rect(55, 205, 160, 46, fill="#f3f4f6", stroke="#9ca3af", sw=1.5, rx=6))
    p.append(text(135, 224, "Вузол 1 (кворум A)", size=11.5, color=INK, bold=True))
    p.append(text(135, 241, "Прийнято: x = 1", size=11, color=POS, bold=True))

    p.append(rect(280, 205, 160, 46, fill="#f3f4f6", stroke="#9ca3af", sw=1.5, rx=6))
    p.append(text(360, 224, "Вузол 2 (кворум B)", size=11.5, color=INK, bold=True))
    p.append(text(360, 241, "Прийнято: x = 2", size=11, color=NEG, bold=True))

    p.append(arrow(215, 181, 155, 203, color=POS, sw=1.5))
    p.append(arrow(280, 181, 340, 203, color=POS, sw=1.5))

    p.append(fitbox(45, 265, 405, 135, "Чому CFT ламається:\n• Репліки не перевіряють пропозицію з іншими вузлами.\n• Вузол 1 і Вузол 2 утворюють кворуми з лідером окремо.\n• Наслідок: розкол системи (Split-Brain) та незворотне пошкодження реплікованого журналу.", size=11.5, fill="#ffffff", stroke="#e5e7eb", color=INK))

    # Права колонка: Рішення BFT (Перехресне голосування)
    p.append(rect(495, 50, 435, 360, fill="#f8fbf9", stroke="#c3e6cb", sw=1.5, rx=8))
    p.append(rect(495, 50, 435, 32, fill="#e2f5e8", stroke="#c3e6cb", sw=1.5, rx=8))
    p.append(text(712, 72, "BFT (PBFT): нульова довіра й перехресний контроль", size=13.5, color=FIELD, bold=True))

    p.append(fitbox(510, 90, 405, 45, "Репліки обмінюються підписаними підтвердженнями між собою.", size=12, fill="#ffffff", stroke="#d4edda", color=INK))

    # Лідер зверху
    p.append(rect(650, 145, 125, 36, fill="#fee2e2", stroke=POS, sw=1.5, rx=6))
    p.append(text(712, 168, "Лідер (зрадник)", size=12, color=POS, bold=True))

    # Репліки знизу
    p.append(rect(520, 205, 160, 46, fill="#e8f5e9", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(600, 224, "Вузол 1 (BFT)", size=11.5, color=INK, bold=True))
    p.append(text(600, 241, "Перевірка гешу", size=10.5, color=MUTED))

    p.append(rect(745, 205, 160, 46, fill="#e8f5e9", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(825, 224, "Вузол 2 (BFT)", size=11.5, color=INK, bold=True))
    p.append(text(825, 241, "Перевірка гешу", size=10.5, color=MUTED))

    p.append(arrow(680, 181, 620, 203, color=POS, sw=1.5))
    p.append(arrow(745, 181, 805, 203, color=POS, sw=1.5))

    # Перехресний обмін між вузлами
    p.append(arrow(682, 220, 743, 220, color=FIELD, sw=1.5))
    p.append(arrow(743, 235, 682, 235, color=FIELD, sw=1.5))

    p.append(fitbox(510, 265, 405, 135, "Чому BFT працює:\n• Репліки вимагають кворум 2f + 1 ідентичних голосів від сусідів.\n• Брехня лідера виявляється негайно: репліки бачать різні геші й блокують фіксацію.\n• Запускається тайм-аут і скидання зрадника через зміну виду (View Change).", size=11.5, fill="#ffffff", stroke="#e5e7eb", color=INK))

    render(os.path.join(OUT, "byzantine-equivocation-failure.svg"), W, H, *p,
           title="Порівняння моделей CFT та BFT при дворушництві лідера")


# ── Фіг. 2: Межа Лампорта 3f+1 та перетин кворумів 2f+1 ──────────────────────────
def fig_lamport_quorums():
    W, H = 960, 440
    p = []

    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#ffffff", sw=0))
    p.append(text(W / 2, 30, "Межа Лампорта N ≥ 3f + 1 та перетин візантійських кворумів", size=17, color=INK, bold=True))

    # Схема системи з N = 3f + 1 (наприклад, f = 1, N = 4)
    p.append(rect(30, 55, 895, 365, fill="#fafbfc", stroke="#d0d7de", sw=1.5, rx=8))

    # Блок загальної кількості вузлів
    p.append(rect(50, 75, 855, 95, fill="#ffffff", stroke="#b0b8c4", sw=1.5, rx=6))
    p.append(text(477, 97, "Загальний пул реплік системи N = 3f + 1 (прикладом для f = 1 маємо N = 4)", size=13, color=INK, bold=True))

    p.append(rect(70, 112, 250, 44, fill="#e8f5e9", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(195, 138, "Чесні вузли групи A (f + 1 = 2)", size=11.5, color=FIELD, bold=True))

    p.append(rect(350, 112, 250, 44, fill="#eaf2fd", stroke=NEG, sw=1.5, rx=6))
    p.append(text(475, 138, "Чесні вузли групи B (f = 1)", size=11.5, color=NEG, bold=True))

    p.append(rect(630, 112, 270, 44, fill="#fee2e2", stroke=POS, sw=1.5, rx=6))
    p.append(text(765, 138, "Візантійські вузли (f = 1, зрадники)", size=11.5, color=POS, bold=True))

    # Два кворуми розміром 2f + 1
    p.append(rect(50, 190, 410, 210, fill="#ffffff", stroke="#c3e6cb", sw=1.5, rx=6))
    p.append(rect(50, 190, 410, 30, fill="#e2f5e8", stroke="#c3e6cb", sw=1.5, rx=6))
    p.append(text(255, 211, "Кворум Q1 (розмір 2f + 1 = 3)", size=12.5, color=FIELD, bold=True))

    p.append(fitbox(65, 230, 380, 155, "Властивість живучості (Liveness):\n• Кворум складається з (f + 1) чесних вузлів A та f візантійських.\n• Система не чекає на f вузлів групи B, бо вони можуть бути повільними або зупиненими.\n• Розмір 2f + 1 гарантує завершення без участі f відсутніх вузлів.", size=11.5, fill="#f8fbf9", stroke="#d4edda", color=INK))

    p.append(rect(495, 190, 410, 210, fill="#ffffff", stroke="#b8daff", sw=1.5, rx=6))
    p.append(rect(495, 190, 410, 30, fill="#e3f0fd", stroke="#b8daff", sw=1.5, rx=6))
    p.append(text(700, 211, "Перетин кворумів |Q1 ∩ Q2| ≥ f + 1", size=12.5, color=NEG, bold=True))

    p.append(fitbox(510, 230, 380, 155, "Властивість безпеки (Safety):\n• Перетин: 2(2f + 1) - (3f + 1) = f + 1 вузол.\n• Навіть якщо всі f візантійських вузлів голосують двічі й брешуть у двох кворумах одночасно,\nу перетині лишається (f + 1) - f = 1 чесний вузол, який унеможливить два різні рішення.", size=11.5, fill="#f7fafd", stroke="#cfe2ff", color=INK))

    render(os.path.join(OUT, "lamport-3f1-quorum-overlap.svg"), W, H, *p,
           title="Межа Лампорта та перетин кворумів у візантійських системах")


# ── Фіг. 3: Три фази PBFT (Pre-Prepare, Prepare, Commit) ─────────────────────────
def fig_pbft_phases():
    W, H = 980, 460
    p = []

    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#ffffff", sw=0))
    p.append(text(W / 2, 28, "Трифазний протокол узгодження PBFT (Castro & Liskov, 1999)", size=17, color=INK, bold=True))

    phases = [
        (25, 55, 220, 380, "1. Pre-Prepare",
         "Первинний вузол (Primary)\nотримує запит клієнта m,\nприсвоює номер послідовності n,\nвид v та транслює повідомлення\n<PRE-PREPARE, v, n, d>.",
         "Ціль:\nОднозначно задати чергу\nзапитів у поточному виді.", FIELD),
        (260, 55, 225, 380, "2. Prepare",
         "Репліки перевіряють підпис\nта геш d і транслюють\n<PREPARE, v, n, d, i>.\nВузол чекає 2f підтверджень\nвід різних реплік.",
         "Результат:\nPrepared Certificate.\nПорядок зафіксовано у виді v.", NEG),
        (500, 55, 225, 380, "3. Commit",
         "Після збору сертифіката\nрепліка транслює\n<COMMIT, v, n, d, i>.\nВузол чекає 2f + 1 повідомлень\nCommit від різних учасників.",
         "Результат:\nCommitted-Local стан.\nЗапит виконується в автоматі.", POS),
        (740, 55, 215, 380, "4. Відповідь (Reply)",
         "Кожна репліка надсилає\nрезультат виконання клієнту:\n<REPLY, v, t, c, i, r>.",
         "Клієнт чекає:\nf + 1 однакових відповідей\nдля фіксації успіху.", INK),
    ]

    for (bx, by, bw, bh, title, desc, purpose, col) in phases:
        p.append(rect(bx, by, bw, bh, fill="#fafbfc", stroke="#d0d7de", sw=1.5, rx=8))
        header_fill = col if col != INK else "#e5e7eb"
        p.append(rect(bx, by, bw, 32, fill=header_fill, stroke=header_fill, sw=1.5, rx=8))
        text_col = "#ffffff" if col != INK else INK
        p.append(text(bx + bw / 2, by + 22, title, size=13, color=text_col, bold=True))

        p.append(fitbox(bx + 8, by + 42, bw - 16, 175, desc, size=11, fill="#ffffff", stroke="#e1e4e8", color=INK))
        p.append(fitbox(bx + 8, by + 230, bw - 16, 135, purpose, size=11, fill="#f4f6f8", stroke="#d0d7de", color=INK, bold=True))

    render(os.path.join(OUT, "pbft-three-phases.svg"), W, H, *p,
           title="Фази протоколу PBFT")


# ── Фіг. 4: Механізм зміни виду (View Change) при падінні чи зраді лідера ────────
def fig_view_change():
    W, H = 960, 440
    p = []

    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#ffffff", sw=0))
    p.append(text(W / 2, 28, "Протокол зміни виду (View Change) у PBFT при збоях первинного вузла", size=17, color=INK, bold=True))

    steps = [
        (35, 55, 275, 360, "1. Тайм-аут лідера",
         "Якщо репліка надіслала запит,\nале первинний вузол мовчить\nабо надсилає підроблені геші,\nспрацьовує локальний таймер.",
         "Дія вузла:\nРепліка переходить у новий стан,\nвідкидає старі повідомлення\nі розсилає усім реплікам пакет\n<VIEW-CHANGE, v+1, n, C, P, i>.", POS),
        (345, 55, 275, 360, "2. Збір доказів",
         "Новий первинний вузол\np = (v + 1) mod N збирає\nнабір із 2f повідомлень\nView-Change від інших реплік.",
         "Формування New-View:\nЛідер аналізує надіслані сертифікати P,\nвизначає останній стабільний стан\nі формує зведений доказ V.", NEG),
        (655, 55, 275, 360, "3. Вхід у новий вид v + 1",
         "Новий первинний вузол транслює\n<NEW-VIEW, v+1, V, O>,\nде O — узгоджені Pre-Prepare.",
         "Верифікація репліками:\nУсі вузли перевіряють доказ V.\nЯкщо докази валідні, система\nвідновлює консенсус у виді v+1.", FIELD),
    ]

    for (bx, by, bw, bh, title, desc, action, col) in steps:
        p.append(rect(bx, by, bw, bh, fill="#fafbfc", stroke="#d0d7de", sw=1.5, rx=8))
        p.append(rect(bx, by, bw, 32, fill="#ffffff", stroke=col, sw=1.5, rx=8))
        p.append(text(bx + bw / 2, by + 22, title, size=13, color=col, bold=True))

        p.append(fitbox(bx + 10, by + 44, bw - 20, 140, desc, size=11.5, fill="#ffffff", stroke="#e1e4e8", color=INK))
        p.append(fitbox(bx + 10, by + 200, bw - 20, 140, action, size=11, fill="#f8f9fa", stroke="#d0d7de", color=INK, bold=True))

    render(os.path.join(OUT, "view-change-protocol.svg"), W, H, *p,
           title="Процедура View Change у PBFT")


if __name__ == "__main__":
    fig_equivocation_failure()
    fig_lamport_quorums()
    fig_pbft_phases()
    fig_view_change()
    print("All figures generated successfully.")

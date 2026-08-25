# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

def path_el(d, stroke=LINE, sw=1.5, fill="none", dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" stroke="{stroke}" stroke-width="{sw:.1f}" fill="{fill}"{d_attr}/>'


# ── Фігура 1: Інтервал невизначеності TrueTime [earliest, latest] ───────────
def fig_uncertainty_interval():
    W, H = 760, 360
    parts = []
    parts.append(text(W/2, 24, "Шкала TrueTime: інтервал невизначеності [earliest, latest]", size=15, bold=True))

    # Вісь абсолютного фізичного часу
    ax_y = 230
    parts.append(line(50, ax_y, 710, ax_y, color=LINE, sw=2))
    parts.append(text(720, ax_y + 4, "t (фізичний еталонний час)", size=12, color=MUTED, anchor="start"))

    # Позначки на осі часу
    for tx in [120, 260, 400, 540, 680]:
        parts.append(line(tx, ax_y - 5, tx, ax_y + 5, color=MUTED, sw=1))

    # Центр вимірювання - t_local
    cx = 380
    eps = 140
    earliest_x = cx - eps
    latest_x = cx + eps

    # Справжній фізичний час t_real десь усередині інтервалу
    real_x = 425
    parts.append(line(real_x, 80, real_x, ax_y, color=POS, sw=2, dash="4 3"))
    parts.append(circle(real_x, ax_y, 5, fill=POS, stroke=POS, sw=1))
    
    b_real, _, _ = textbox(real_x, 60, "t_real (істинний невідомий момент)", size=11,
                           fill="#fdecea", stroke=POS, color=POS, bold=True)
    parts.append(b_real)

    # Інтервал TrueTime: діапазон [earliest, latest]
    int_y = 145
    int_h = 36
    parts.append(rect(earliest_x, int_y, 2 * eps, int_h, fill="#eaf0fd", stroke=NEG, sw=2, rx=4))
    
    # Центральна точка інтервалу t_local (без перетину тексту лініями)
    parts.append(text(cx, int_y + int_h / 2 + 4, "t_local (показ лічильника)", size=12, color=NEG, bold=True))

    # Стрілки похибки epsilon
    parts.append(line(earliest_x, int_y - 12, latest_x, int_y - 12, color=LINE, sw=1.2))
    parts.append(line(earliest_x, int_y - 17, earliest_x, int_y - 7, color=LINE, sw=1.2))
    parts.append(line(latest_x, int_y - 17, latest_x, int_y - 7, color=LINE, sw=1.2))
    parts.append(line(cx, int_y - 17, cx, int_y - 7, color=LINE, sw=1.2))
    
    parts.append(text((earliest_x + cx)/2, int_y - 20, "−ε", size=12, color=LINE, bold=True))
    parts.append(text((latest_x + cx)/2, int_y - 20, "+ε", size=12, color=LINE, bold=True))

    # Лінії проєкції на вісь
    parts.append(line(earliest_x, int_y + int_h, earliest_x, ax_y, color=NEG, sw=1.2, dash="3 3"))
    parts.append(line(latest_x, int_y + int_h, latest_x, ax_y, color=NEG, sw=1.2, dash="3 3"))
    parts.append(circle(earliest_x, ax_y, 4, fill=NEG, stroke=NEG, sw=1))
    parts.append(circle(latest_x, ax_y, 4, fill=NEG, stroke=NEG, sw=1))

    parts.append(text(earliest_x, ax_y + 22, "earliest = t_local − ε", size=11, color=NEG, bold=True))
    parts.append(text(latest_x, ax_y + 22, "latest = t_local + ε", size=11, color=NEG, bold=True))

    # Гарантія TrueTime знизу
    b_gar, _, _ = textbox(W/2, 315, "Фундаментальний інваріант: earliest ≤ t_real ≤ latest (похибка гарантовано обмежена ±ε)",
                          size=11.5, fill="#eafaf1", stroke=FIELD, color=FIELD, bold=True)
    parts.append(b_gar)

    render(os.path.join(IMG, "truetime-uncertainty-interval.svg"), W, H, *parts)


# ── Фігура 2: Порушення лінеаризовності без очікування та порятунок через Commit Wait ──
def fig_commit_wait_linearizability():
    W, H = 760, 440
    parts = []
    parts.append(text(W/2, 24, "Гарантія порядку причинності через бар'єр Commit Wait", size=15, bold=True))

    # Вісь часу зверху
    parts.append(line(60, 60, 700, 60, color=MUTED, sw=1.5))
    parts.append(text(710, 64, "Реальний час t", size=12, color=MUTED, anchor="start"))

    # Секція А: Наївні мітки без очікування (аномалія інверсії)
    box_a_y = 75
    parts.append(rect(40, box_a_y, 680, 145, fill="none", stroke=POS, sw=1.2, rx=6))
    parts.append(text(55, box_a_y + 20, "1. Наївні скалярні мітки (вузол В відстає від вузла А): порушення порядку",
                      size=12, color=POS, bold=True, anchor="start"))

    # Транзакція Т1 на вузлі А
    t1_s, t1_e = 80, 220
    parts.append(rect(t1_s, box_a_y + 35, t1_e - t1_s, 32, fill="#fdecea", stroke=POS, sw=1.2, rx=4))
    parts.append(text((t1_s + t1_e)/2, box_a_y + 55, "T1 на Вузлі A: мітка s₁ = 100", size=11, color=POS, bold=True))

    # Причинний зв'язок між клієнтами (повідомлення по мережі)
    parts.append(line(t1_e, box_a_y + 51, 330, box_a_y + 85, color=LINE, sw=1.5, dash="4 2"))
    parts.append(text(285, box_a_y + 60, "зовнішній зв'язок (клієнт)", size=10, color=MUTED, italic=True))

    # Транзакція Т2 на вузлі В
    t2_s, t2_e = 330, 480
    parts.append(rect(t2_s, box_a_y + 70, t2_e - t2_s, 32, fill="#fdecea", stroke=POS, sw=1.2, rx=4))
    parts.append(text((t2_s + t2_e)/2, box_a_y + 90, "T2 на Вузлі B: мітка s₂ = 95 (дрейф!)", size=11, color=POS, bold=True))

    # Висновок секції А
    parts.append(text(540, box_a_y + 75, "Аномалія: T1 завершилась ДО T2,", size=11, color=POS, bold=True, anchor="start"))
    parts.append(text(540, box_a_y + 93, "але s₂ < s₁ (T2 виглядає давнішою!)", size=11, color=POS, bold=True, anchor="start"))

    # Секція Б: TrueTime + Commit Wait (лінеаризовність гарантована)
    box_b_y = 235
    parts.append(rect(40, box_b_y, 680, 185, fill="none", stroke=FIELD, sw=1.2, rx=6))
    parts.append(text(55, box_b_y + 20, "2. TrueTime з правилом Commit Wait: розведення інтервалів у реальному часі",
                      size=12, color=FIELD, bold=True, anchor="start"))

    # Т1 виконання + вибір s1 = latest1
    tt1_s, tt1_m = 70, 190
    parts.append(rect(tt1_s, box_b_y + 35, tt1_m - tt1_s, 30, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=4))
    parts.append(text((tt1_s + tt1_m)/2, box_b_y + 54, "T1: вибір s₁ = latest₁", size=11, color=NEG, bold=True))

    # Бар'єр Commit Wait (очікування 2*epsilon)
    tt1_w = tt1_m + 110
    parts.append(rect(tt1_m, box_b_y + 35, tt1_w - tt1_m, 30, fill="#fff2cc", stroke="#d6b656", sw=1.2, rx=4))
    parts.append(text((tt1_m + tt1_w)/2, box_b_y + 54, "Commit Wait (≥ 2ε)", size=11, color="#8a6d00", bold=True))
    parts.append(line(tt1_w, box_b_y + 30, tt1_w, box_b_y + 70, color=FIELD, sw=2))
    parts.append(text(tt1_w, box_b_y + 82, "Відповідь клієнту: s₁ гарантовано в минулому", size=10, color=FIELD, bold=True))

    # Причинний перехід
    parts.append(line(tt1_w, box_b_y + 50, 420, box_b_y + 110, color=LINE, sw=1.5, dash="4 2"))

    # Т2 починається ПІСЛЯ завершення T1
    tt2_s, tt2_e = 420, 560
    parts.append(rect(tt2_s, box_b_y + 100, tt2_e - tt2_s, 30, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=4))
    parts.append(text((tt2_s + tt2_e)/2, box_b_y + 119, "T2: вибір s₂ = latest₂", size=11, color=NEG, bold=True))

    # Гарантована нерівність
    b_cw, _, _ = textbox(470, box_b_y + 155, "s₁ < earliest(T2) ≤ s₂  ⇒  s₁ < s₂ завжди!", size=11.5,
                         fill="#eafaf1", stroke=FIELD, color=FIELD, bold=True)
    parts.append(b_cw)

    render(os.path.join(IMG, "commit-wait-linearizability.svg"), W, H, *parts)


# ── Фігура 3: Динамічний конус дрейфу та періодична ресинхронізація ─────────
def fig_drift_envelope():
    W, H = 760, 390
    parts = []
    parts.append(text(W/2, 24, "Динаміка похибки ε(t): періодична синхронізація та дрейф без зв'язку", size=15, bold=True))

    ox, oy = 80, 300
    w_ax, h_ax = 620, 230
    parts.append(line(ox, oy, ox + w_ax, oy, color=MUTED, sw=1.5))
    parts.append(line(ox, oy, ox, oy - h_ax, color=MUTED, sw=1.5))
    parts.append(text(ox + w_ax + 10, oy + 4, "Час відліку t", size=12, color=MUTED, anchor="start"))
    parts.append(text(ox, oy - h_ax - 10, "Похибка ε(t)", size=12, color=MUTED, anchor="middle"))

    # Період синхронізації 1: 0 до 160 px
    # Базова похибка eps0 = 20 px, зростає до 70 px
    p1 = [(ox, oy - 20), (ox + 160, oy - 70)]
    parts.append(line(p1[0][0], p1[0][1], p1[1][0], p1[1][1], color=NEG, sw=2))
    parts.append(line(ox + 160, oy - 70, ox + 160, oy - 20, color=FIELD, sw=2, dash="3 2"))

    # Період синхронізації 2: 160 до 320 px
    p2 = [(ox + 160, oy - 20), (ox + 320, oy - 70)]
    parts.append(line(p2[0][0], p2[0][1], p2[1][0], p2[1][1], color=NEG, sw=2))
    parts.append(line(ox + 320, oy - 70, ox + 320, oy - 20, color=FIELD, sw=2, dash="3 2"))

    # Період 3: втрата GPS (дрейф триває довше, похибка зростає до 170 px)
    p3 = [(ox + 320, oy - 20), (ox + 560, oy - 170)]
    parts.append(line(p3[0][0], p3[0][1], p3[1][0], p3[1][1], color=POS, sw=2.2))

    # Скидання після відновлення зв'язку
    parts.append(line(ox + 560, oy - 170, ox + 560, oy - 20, color=FIELD, sw=2, dash="3 2"))
    parts.append(line(ox + 560, oy - 20, ox + 610, oy - 40, color=NEG, sw=2))

    # Позначки базової похибки eps0
    parts.append(line(ox - 5, oy - 20, ox + 5, oy - 20, color=MUTED, sw=1.5))
    parts.append(text(ox - 10, oy - 16, "ε₀", size=12, color=MUTED, anchor="end", bold=True))

    # Пояснювальні підписи
    b_sync1, _, _ = textbox(ox + 80, oy - 95, "ε(t) = ε₀ + ρ·t (кварцовий дрейф)", size=10.5,
                            fill="#eaf0fd", stroke=NEG, color=NEG)
    parts.append(b_sync1)

    b_resync, _, _ = textbox(ox + 240, oy - 110, "Синхронізація з GPS / Rubidium\nскидає ε(t) назад до ε₀",
                             size=10.5, fill="#eafaf1", stroke=FIELD, color=FIELD)
    parts.append(b_resync)

    b_loss, _, _ = textbox(ox + 450, oy - 195, "Втрата зв'язку з еталоном:\nε(t) безпечно росте,\nзберігаючи інваріант безпеки!",
                           size=11, fill="#fdecea", stroke=POS, color=POS, bold=True)
    parts.append(b_loss)

    # Підписи під віссю - з чітким розділенням
    exp_y = oy + 42
    b1, _, _ = textbox(190, exp_y, "Регулярний цикл (кожні 30 с)", size=10.5, fill=FILL, stroke=MUTED, color=INK)
    b2, _, _ = textbox(520, exp_y, "Аварійний режим (holdover mode): зростає затримка коміту",
                       size=10.5, fill=FILL, stroke=MUTED, color=INK)
    parts.append(b1)
    parts.append(b2)

    render(os.path.join(IMG, "drift-envelope-resync.svg"), W, H, *parts)


# ── Фігура 4: Конвеєр транзакції з TrueTime: вибір мітки та очікування фіксації ──
def fig_transaction_commit_pipeline():
    W, H = 760, 420
    parts = []
    parts.append(text(W/2, 24, "Конвеєр розподіленої транзакції: 2PC, вибір мітки та Commit Wait", size=15, bold=True))

    stages = [
        ("1. Читання і запис", "Отримання блокувань (Locks)\nта виконання локальних змін", NEG, "#eaf0fd"),
        ("2. Фаза Prepare 2PC", "Учасники надсилають Prepare;\nЛідер збирає кворум голосів", NEG, "#eaf0fd"),
        ("3. Вибір мітки коміту", "Лідер викликає TT.now()\nі обирає s = latest (s ≥ t_real)", FIELD, "#eafaf1"),
        ("4. Бар'єр Commit Wait", "Лідер блокує відповідь,\nдоки TT.now().earliest > s", POS, "#fdecea"),
        ("5. Фіксація і відповідь", "Запис у журнал, зняття замків,\nвідповідь клієнту з міткою s", FIELD, "#eafaf1")
    ]

    sw_w = 126
    gap = 14
    start_x = 35
    top_y = 70
    h_box = 90

    for i, (title_st, desc_st, col, f_col) in enumerate(stages):
        bx = start_x + i * (sw_w + gap)
        parts.append(rect(bx, top_y, sw_w, h_box, fill=f_col, stroke=col, sw=1.5, rx=5))
        parts.append(text(bx + sw_w/2, top_y + 20, title_st, size=11, color=col, bold=True))
        
        lines_desc = desc_st.split("\n")
        for j, ld in enumerate(lines_desc):
            parts.append(text(bx + sw_w/2, top_y + 44 + j * 16, ld, size=9.5, color=INK))

        if i < len(stages) - 1:
            arr_x1 = bx + sw_w
            arr_x2 = bx + sw_w + gap
            parts.append(line(arr_x1, top_y + h_box/2, arr_x2, top_y + h_box/2, color=MUTED, sw=1.5))
            parts.append(line(arr_x2 - 4, top_y + h_box/2 - 4, arr_x2, top_y + h_box/2, color=MUTED, sw=1.5))
            parts.append(line(arr_x2 - 4, top_y + h_box/2 + 4, arr_x2, top_y + h_box/2, color=MUTED, sw=1.5))

    # Нижня секція: Читання без блокувань (Snapshot Reads)
    snap_y = 200
    parts.append(rect(start_x, snap_y, 690, 185, fill="none", stroke=MUTED, sw=1.2, rx=6))
    parts.append(text(start_x + 20, snap_y + 24, "Транзакції читання за знімком (Snapshot Isolation) без жодних блокувань:",
                      size=12, color=INK, bold=True, anchor="start"))

    # Кроки читання
    parts.append(rect(start_x + 20, snap_y + 45, 300, 115, fill="#f4f6f8", stroke=MUTED, sw=1, rx=4))
    parts.append(text(start_x + 170, snap_y + 68, "Читання в теперішньому (Read at Now):", size=11, color=NEG, bold=True))
    parts.append(text(start_x + 170, snap_y + 90, "1. Клієнт викликає t_read = TT.now().latest", size=10, color=INK))
    parts.append(text(start_x + 170, snap_y + 110, "2. Якщо версія s > t_read — вона ще не існує", size=10, color=INK))
    parts.append(text(start_x + 170, snap_y + 130, "3. Читання повністю узгоджене й лінеаризовне", size=10, color=INK))

    parts.append(rect(start_x + 360, snap_y + 45, 330, 115, fill="#f4f6f8", stroke=MUTED, sw=1, rx=4))
    parts.append(text(start_x + 525, snap_y + 68, "Читання в минулому (Read at Timestamp T):", size=11, color=FIELD, bold=True))
    parts.append(text(start_x + 525, snap_y + 90, "1. Клієнт обирає t_hist < TT.now().earliest", size=10, color=INK))
    parts.append(text(start_x + 525, snap_y + 110, "2. Читає дані з версією s ≤ t_hist напряму з диска", size=10, color=INK))
    parts.append(text(start_x + 525, snap_y + 130, "3. Жодної взаємодії з лідером чи активними замками!", size=10, color=FIELD, bold=True))

    render(os.path.join(IMG, "transaction-commit-pipeline.svg"), W, H, *parts)


def main():
    fig_uncertainty_interval()
    fig_commit_wait_linearizability()
    fig_drift_envelope()
    fig_transaction_commit_pipeline()
    print("All figures generated successfully.")

if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
Фігури для вставки ch23-s6-a-atomics-barriers.md
Рис. 4.5.6a.3 — спінлок vs atomic fetch_add (часові доріжки двох ядер)
Рис. 4.5.6a.4 — переставлення пам'яті без бар'єра / з бар'єром

Чистий Python, без сторонніх залежностей. Вивід → ./img/.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.5.6a.3 — спінлок vs atomic fetch_add
# ══════════════════════════════════════════════════════════════════════════════
def fig3_spinlock_vs_atomic():
    W, H = 760, 380
    frags = []

    # ── Заголовок секцій ──────────────────────────────────────────────────────
    frags.append(text(195, 32, "Спінлок (portENTER_CRITICAL)", size=13, bold=True, color=INK))
    frags.append(text(565, 32, "atomic fetch_add", size=13, bold=True, color=FIELD))

    # Роздільна вертикаль між двома колонками
    frags.append(line(380, 20, 380, H - 20, color=MUTED, dash="6,4"))

    # ── Вісь часу ─────────────────────────────────────────────────────────────
    # Ліва колонка: Core0 зверху, Core1 нижче
    TL_Y0 = 70   # Core0 ліворуч
    TL_Y1 = 200  # Core1 ліворуч
    TR_Y0 = 70   # Core0 праворуч
    TR_Y1 = 200  # Core1 праворуч

    # Підписи ядер — ліворуч
    frags.append(text(50, TL_Y0 + 2, "Core 0", size=12, bold=True, color=INK, anchor="middle"))
    frags.append(text(50, TL_Y1 + 2, "Core 1", size=12, bold=True, color=POS, anchor="middle"))

    # Підписи ядер — праворуч
    frags.append(text(420, TR_Y0 + 2, "Core 0", size=12, bold=True, color=INK, anchor="middle"))
    frags.append(text(420, TR_Y1 + 2, "Core 1", size=12, bold=True, color=FIELD, anchor="middle"))

    # Горизонтальні лінії (шкали часу)
    # ліва колонка
    frags.append(arrow(70, TL_Y0, 350, TL_Y0, color=INK))
    frags.append(arrow(70, TL_Y1, 350, TL_Y1, color=POS))
    # права колонка
    frags.append(arrow(440, TR_Y0, 730, TR_Y0, color=INK))
    frags.append(arrow(440, TR_Y1, 730, TR_Y1, color=FIELD))

    # ── ЛІВА: Спінлок ─────────────────────────────────────────────────────────
    # Core0: секція (100..200) — замок взяли
    x_lock_s, x_lock_e = 100, 220
    frags.append(('<rect x="%.0f" y="%.0f" width="%.0f" height="20" rx="4" fill="%s" stroke="%s" stroke-width="1.5"/>'
                  % (x_lock_s, TL_Y0 - 10, x_lock_e - x_lock_s, "#fdecea", POS)))
    frags.append(text((x_lock_s + x_lock_e) / 2, TL_Y0 + 5, "count++ під замком", size=10, color=POS, anchor="middle"))

    # Стрілки-мітки: ENTER і EXIT
    frags.append(line(x_lock_s, TL_Y0 - 22, x_lock_s, TL_Y0 + 14, color=POS, dash="3,2"))
    frags.append(text(x_lock_s, TL_Y0 - 28, "ENTER", size=9, color=POS, anchor="middle"))
    frags.append(line(x_lock_e, TL_Y0 - 22, x_lock_e, TL_Y0 + 14, color=POS, dash="3,2"))
    frags.append(text(x_lock_e, TL_Y0 - 28, "EXIT", size=9, color=POS, anchor="middle"))

    # Core1: крутиться (spin) поки Core0 тримає замок
    x_spin_s, x_spin_e = 100, 220
    frags.append(('<rect x="%.0f" y="%.0f" width="%.0f" height="20" rx="4" fill="%s" stroke="%s" stroke-width="1.5" stroke-dasharray="5,3"/>'
                  % (x_spin_s, TL_Y1 - 10, x_spin_e - x_spin_s, "#fff6e0", "#c0a020")))
    frags.append(text((x_spin_s + x_spin_e) / 2, TL_Y1 + 5, "КРУТИТЬСЯ — чекає", size=10, color="#b07800", anchor="middle"))

    # Core1: після EXIT — своя секція
    x2_s, x2_e = 222, 310
    frags.append(('<rect x="%.0f" y="%.0f" width="%.0f" height="20" rx="4" fill="%s" stroke="%s" stroke-width="1.5"/>'
                  % (x2_s, TL_Y1 - 10, x2_e - x2_s, "#fdecea", POS)))
    frags.append(text((x2_s + x2_e) / 2, TL_Y1 + 5, "count++", size=10, color=POS, anchor="middle"))

    # Зв'язувальна стрілка: ENTER core1 тільки після EXIT core0
    frags.append(('<path d="M %.0f %.0f Q %.0f %.0f %.0f %.0f" fill="none" stroke="%s" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow)"/>'
                  % (x_lock_e, TL_Y0 + 10, x_lock_e + 10, (TL_Y0 + TL_Y1) / 2, x2_s, TL_Y1 + 5, "#b07800")))

    # Легенда: надмірний замок
    tb, _, _ = textbox(195, 310, "Замок надмірний:\nCore1 простоює даремно", size=11, fill="#fff6e0", stroke="#c0a020")
    frags.append(tb)

    # ── ПРАВА: atomic fetch_add ────────────────────────────────────────────────
    # Core0 і Core1 виконують fetch_add незалежно — паралельно, без чекання
    # Core0: fetch_add
    fa0_s, fa0_e = 480, 560
    frags.append(('<rect x="%.0f" y="%.0f" width="%.0f" height="20" rx="4" fill="%s" stroke="%s" stroke-width="1.5"/>'
                  % (fa0_s, TR_Y0 - 10, fa0_e - fa0_s, "#eef6ef", FIELD)))
    frags.append(text((fa0_s + fa0_e) / 2, TR_Y0 + 5, "fetch_add (RMW)", size=10, color=FIELD, anchor="middle"))

    # Core1: fetch_add (трохи зміщено вправо, але паралельно)
    fa1_s, fa1_e = 510, 590
    frags.append(('<rect x="%.0f" y="%.0f" width="%.0f" height="20" rx="4" fill="%s" stroke="%s" stroke-width="1.5"/>'
                  % (fa1_s, TR_Y1 - 10, fa1_e - fa1_s, "#eef6ef", FIELD)))
    frags.append(text((fa1_s + fa1_e) / 2, TR_Y1 + 5, "fetch_add (RMW)", size=10, color=FIELD, anchor="middle"))

    # Підпис — апаратна неподільність
    frags.append(text(565, 150, "Апаратна LL/SC:", size=10, color=MUTED, anchor="middle"))
    frags.append(text(565, 163, "ніхто не чекає", size=10, color=FIELD, anchor="middle", bold=True))

    # Легенда: lock-free
    tb2, _, _ = textbox(565, 310, "Lock-free: обидва ядра\nпрацюють без блокування", size=11, fill="#eef6ef", stroke=FIELD)
    frags.append(tb2)

    # ── Підпис осі часу ──────────────────────────────────────────────────────
    frags.append(text(195, H - 15, "час →", size=10, color=MUTED, anchor="middle"))
    frags.append(text(565, H - 15, "час →", size=10, color=MUTED, anchor="middle"))

    render(os.path.join(OUT, "fig-23-6a-3-spinlock-vs-atomic.svg"), W, H, *frags,
           title="Рис. 4.5.6a.3. Спінлок vs atomic fetch_add — часові доріжки двох ядер")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.5.6a.4 — переставлення пам'яті: без бар'єра / з бар'єром
# ══════════════════════════════════════════════════════════════════════════════
def fig4_barrier_reorder():
    W, H = 760, 410
    frags = []

    # Заголовок колонок
    frags.append(text(195, 32, "БЕЗ бар'єра (store buffer переставляє)", size=12, bold=True, color=POS))
    frags.append(text(565, 32, "З бар'єром (release + acquire)", size=12, bold=True, color=FIELD))
    frags.append(line(380, 20, 380, H - 20, color=MUTED, dash="6,4"))

    # ── Спільні підписи ──────────────────────────────────────────────────────
    # Core0 = письменник, Core1 = читач — обидві колонки
    for cx in (195, 565):
        frags.append(text(cx - 80, 62, "Core 0 (пише)", size=11, bold=True, color=INK, anchor="middle"))
        frags.append(text(cx + 80, 62, "Core 1 (читає)", size=11, bold=True, color=NEG, anchor="middle"))

    # ── ЛІВОРУЧ: без бар'єра ──────────────────────────────────────────────────
    # Core0 writes: data, then head (в коді — цей порядок)
    # Але store buffer може переставити видимість: head стає видимим РАНІШЕ за дані
    lx0 = 115   # центр Core0 ліворуч
    lx1 = 275   # центр Core1 ліворуч

    # Core0 — дії
    tb, _, _ = textbox(lx0, 115, "① пишемо data[i]", size=11, fill=FILL, stroke=INK)
    frags.append(tb)
    tb, _, _ = textbox(lx0, 170, "② пишемо head++", size=11, fill=FILL, stroke=INK)
    frags.append(tb)

    # Store buffer — переставляє
    tb, _, _ = textbox(195, 225, "store buffer\nперевпорядковує!", size=11, fill="#fdecea", stroke=POS)
    frags.append(tb)

    # Core1 — бачить head РАНІШЕ за дані
    tb, _, _ = textbox(lx1, 280, "① бачить head++", size=11, fill="#fdecea", stroke=POS)
    frags.append(tb)
    tb, _, _ = textbox(lx1, 335, "② data — ще стара\n→ читає СМІТТЯ", size=11, fill="#fdecea", stroke=POS)
    frags.append(tb)

    # Стрілки — порядок видимості (перекручений)
    frags.append(arrow(lx0, 133, lx0, 152, color=INK))  # ① → ②
    frags.append(arrow(lx0, 188, 195, 208, color=POS))   # ② → buffer
    frags.append(arrow(195, 248, lx1, 262, color=POS))   # buffer → Core1 head
    frags.append(arrow(lx1, 298, lx1, 317, color=POS))   # head → data (сміття)

    # Хрестик (помилка)
    frags.append(text(195, 372, "✗ гонка даних: читач бачить недописаний слот", size=10, color=POS, anchor="middle"))

    # ── ПРАВОРУЧ: з бар'єром ─────────────────────────────────────────────────
    rx0 = 485   # Core0
    rx1 = 645   # Core1

    # Core0 — дії з release
    tb, _, _ = textbox(rx0, 115, "① пишемо data[i]", size=11, fill=FILL, stroke=INK)
    frags.append(tb)
    tb, _, _ = textbox(rx0, 170, "RELEASE бар'єр", size=11, fill="#eef6ef", stroke=FIELD, bold=True)
    frags.append(tb)
    tb, _, _ = textbox(rx0, 225, "③ head.store(release)", size=11, fill="#eef6ef", stroke=FIELD)
    frags.append(tb)

    # Стрілки Core0
    frags.append(arrow(rx0, 133, rx0, 152, color=INK))
    frags.append(arrow(rx0, 188, rx0, 207, color=FIELD))

    # Core1 — читає з acquire
    tb, _, _ = textbox(rx1, 225, "head.load(acquire)", size=11, fill="#eef6ef", stroke=FIELD)
    frags.append(tb)
    tb, _, _ = textbox(rx1, 280, "ACQUIRE гарантія:", size=11, fill="#eef6ef", stroke=FIELD, bold=True)
    frags.append(tb)
    tb, _, _ = textbox(rx1, 335, "data — цілий запис", size=11, fill="#eef6ef", stroke=FIELD)
    frags.append(tb)

    # Стрілки з Core0 head → Core1 acquire
    frags.append(arrow(rx0, 243, rx1, 207, color=FIELD))
    frags.append(arrow(rx1, 243, rx1, 262, color=FIELD))
    frags.append(arrow(rx1, 298, rx1, 317, color=FIELD))

    # Пояснення бар'єра
    frags.append(text(565, 380, "✓ release+acquire: дані видимі ДО head", size=10, color=FIELD, anchor="middle", bold=True))

    render(os.path.join(OUT, "fig-23-6a-4-barrier-reorder.svg"), W, H, *frags,
           title="Рис. 4.5.6a.4. Переставлення пам'яті між ядрами: без / з бар'єром")


if __name__ == "__main__":
    fig3_spinlock_vs_atomic()
    print("OK: fig-23-6a-3-spinlock-vs-atomic.svg")
    fig4_barrier_reorder()
    print("OK: fig-23-6a-4-barrier-reorder.svg")

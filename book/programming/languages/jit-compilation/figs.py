# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── 1. tiered-compilation: Багаторівневий JIT і зворотна деоптимізація ───────
def fig_tiered_compilation():
    W, H = 820, 390
    p = []

    # Рівні компіляції (зліва направо)
    # Tier 0: Інтерпретатор
    t0_x, t0_y, t0_w, t0_h = 30, 80, 190, 180
    p.append(rect(t0_x, t0_y, t0_w, t0_h, fill="#f8fafc", stroke=LINE, sw=1.8, rx=8))
    p.append(text(t0_x + t0_w / 2, t0_y + 26, "Tier 0: Інтерпретатор", size=13, color=INK, bold=True))
    p.append(text(t0_x + t0_w / 2, t0_y + 48, "миттєвий старт програми", size=10, color=MUTED))
    p.append(rect(t0_x + 15, t0_y + 64, t0_w - 30, 48, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=5))
    p.append(text(t0_x + t0_w / 2, t0_y + 84, "Побайтне виконання", size=11, color=INK))
    p.append(text(t0_x + t0_w / 2, t0_y + 102, "+ збір профілю типів", size=10, color=MUTED, italic=True))
    p.append(rect(t0_x + 15, t0_y + 120, t0_w - 30, 42, fill="#fef2f2", stroke="#f87171", sw=1.2, rx=5))
    p.append(text(t0_x + t0_w / 2, t0_y + 138, "Лічильники викликів", size=11, color=POS, bold=True))
    p.append(text(t0_x + t0_w / 2, t0_y + 152, "гарячі методи й цикли", size=9, color=POS))

    # Tier 1: Базовий JIT
    t1_x, t1_y, t1_w, t1_h = 285, 80, 210, 180
    p.append(rect(t1_x, t1_y, t1_w, t1_h, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(t1_x + t1_w / 2, t1_y + 26, "Tier 1: Базовий JIT", size=13, color="#166534", bold=True))
    p.append(text(t1_x + t1_w / 2, t1_y + 48, "швидка трансляція коду", size=10, color=MUTED))
    p.append(rect(t1_x + 15, t1_y + 64, t1_w - 30, 48, fill="#ffffff", stroke="#86efac", sw=1.2, rx=5))
    p.append(text(t1_x + t1_w / 2, t1_y + 84, "Простий машинний код", size=11, color=INK))
    p.append(text(t1_x + t1_w / 2, t1_y + 102, "без дорогих оптимізацій", size=10, color=MUTED, italic=True))
    p.append(rect(t1_x + 15, t1_y + 120, t1_w - 30, 42, fill="#fef2f2", stroke="#f87171", sw=1.2, rx=5))
    p.append(text(t1_x + t1_w / 2, t1_y + 138, "Поглиблений профіль", size=11, color=POS, bold=True))
    p.append(text(t1_x + t1_w / 2, t1_y + 152, "типи полів, гілки, виклики", size=9, color=POS))

    # Tier 2: Оптимізуючий JIT
    t2_x, t2_y, t2_w, t2_h = 560, 80, 230, 180
    p.append(rect(t2_x, t2_y, t2_w, t2_h, fill="#eff6ff", stroke=NEG, sw=2.0, rx=8))
    p.append(text(t2_x + t2_w / 2, t2_y + 26, "Tier 2: Оптимізуючий JIT", size=13, color="#1e40af", bold=True))
    p.append(text(t2_x + t2_w / 2, t2_y + 48, "пікова швидкодія процесора", size=10, color=MUTED))
    p.append(rect(t2_x + 15, t2_y + 64, t2_w - 30, 98, fill="#ffffff", stroke="#93c5fd", sw=1.2, rx=5))
    p.append(text(t2_x + t2_w / 2, t2_y + 84, "Спекулятивні оптимізації:", size=11, color="#1e40af", bold=True))
    p.append(text(t2_x + t2_w / 2, t2_y + 104, "• Агресивний інлайнінг", size=10, color=INK))
    p.append(text(t2_x + t2_w / 2, t2_y + 122, "• Спеціалізація типів", size=10, color=INK))
    p.append(text(t2_x + t2_w / 2, t2_y + 140, "• Усунення меж (BCE), SSA", size=10, color=INK))

    # Прямі стрілки компіляції між ярусами
    p.append(arrow(t0_x + t0_w, 140, t1_x, 140, color=FIELD, sw=2.2))
    p.append(text((t0_x + t0_w + t1_x) / 2, 130, "поріг 1", size=10, color=FIELD, bold=True))

    p.append(arrow(t1_x + t1_w, 140, t2_x, 140, color=NEG, sw=2.2))
    p.append(text((t1_x + t1_w + t2_x) / 2, 130, "поріг 2", size=10, color=NEG, bold=True))

    # Зворотна стрілка деоптимізації (Bailout)
    deopt_y = 310
    p.append(line(t2_x + t2_w / 2, t2_y + t2_h, t2_x + t2_w / 2, deopt_y, color=POS, sw=2.0, dash="5,4"))
    p.append(line(t2_x + t2_w / 2, deopt_y, t0_x + t0_w / 2, deopt_y, color=POS, sw=2.0, dash="5,4"))
    p.append(arrow(t0_x + t0_w / 2, deopt_y, t0_x + t0_w / 2, t0_y + t0_h + 4, color=POS, sw=2.0))

    p.append(rect(300, deopt_y - 20, 220, 40, fill="#fff1f2", stroke=POS, sw=1.4, rx=6))
    p.append(text(410, deopt_y - 3, "Деоптимізація (Bailout)", size=11, color=POS, bold=True))
    p.append(text(410, deopt_y + 13, "припущення про тип порушено", size=9, color=POS))

    # Верхній пояснювальний блок
    p.append(text(W / 2, 35, "Багаторівнева адаптивна компіляція та відкат на безпечний рівень", size=14, color=INK, bold=True))

    render(os.path.join(OUT, "tiered-compilation.svg"), W, H, *p,
           title="Багаторівневий JIT і зворотна деоптимізація")


# ── 2. inline-caching-states: Стани інлайн-кешування ─────────────────────────
def fig_inline_caching_states():
    W, H = 820, 310
    p = []

    # 4 стани зліва направо
    box_w = 160
    box_h = 170
    gap = 35
    start_x = 30
    y = 75

    states = [
        ("Неініціалізований", "(Uninitialized)", "#f1f5f9", LINE, [
            "Виклик уперше",
            "Кеш порожній",
            "Звернення до рантайму",
            "Пошук типу об'єкта"
        ]),
        ("Мономорфний", "(Monomorphic)", "#ecfdf5", FIELD, [
            "1 форма (Shape / Map)",
            "Пряме зміщення поля",
            "Перевірка форми: 1 cmp",
            "Швидкість прямого C"
        ]),
        ("Поліморфний", "(Polymorphic)", "#eff6ff", NEG, [
            "2–4 форми в кеші",
            "Коротка таблиця / switch",
            "Швидкий перебір форм",
            "Окреме зміщення кожній"
        ]),
        ("Мегаморфний", "(Megamorphic)", "#fef2f2", POS, [
            "≥ 5 різних форм",
            "Інлайн-кеш здається",
            "Глобальна хеш-таблиця",
            "Найповільніший шлях"
        ])
    ]

    for i, (title_uk, title_en, bg_col, border_col, bullets) in enumerate(states):
        bx = start_x + i * (box_w + gap)
        p.append(rect(bx, y, box_w, box_h, fill=bg_col, stroke=border_col, sw=1.8, rx=8))
        p.append(text(bx + box_w / 2, y + 24, title_uk, size=12, color=INK, bold=True))
        p.append(text(bx + box_w / 2, y + 40, title_en, size=10, color=MUTED, italic=True))
        p.append(line(bx + 10, y + 50, bx + box_w - 10, y + 50, color=border_col, sw=1.0))
        for j, b in enumerate(bullets):
            p.append(text(bx + 12, y + 72 + j * 22, "• " + b, size=10, color=INK, anchor="start"))

        # Стрілка переходу до наступного стану
        if i < len(states) - 1:
            ax = bx + box_w + 3
            p.append(arrow(ax, y + box_h / 2, ax + gap - 6, y + box_h / 2, color=INK, sw=1.8))
            p.append(text(ax + (gap - 6) / 2, y + box_h / 2 - 10, "+тип", size=9, color=MUTED, bold=True))

    p.append(text(W / 2, 35, "Еволюція станів інлайн-кешу (Inline Cache) на місці динамічного виклику", size=14, color=INK, bold=True))
    p.append(text(W / 2, H - 20, "90%+ викликів у реальному коді лишаються мономорфними, що дає машинну швидкість читання", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "inline-caching-states.svg"), W, H, *p,
           title="Чотири фази інлайн-кешування")


# ── 3. wx-memory-transition: Життєвий цикл пам'яті JIT під W^X ───────────────
def fig_wx_memory_transition():
    W, H = 820, 320
    p = []

    # 4 етапи виділення, запису, захисту та виконання
    steps = [
        ("1. Виділення буфера", "mmap() / VirtualAlloc", "PROT_READ | PROT_WRITE", "#f8fafc", LINE, [
            "Анонімна сторінка",
            "W = 1, X = 0 (запис)",
            "Виконання заборонено"
        ]),
        ("2. Генерація коду", "JIT Emitter (Асемблер)", "Запис машинних байтів", "#fef3c7", "#d97706", [
            "Запис x86-64 інструкцій",
            "Пролог та епілог",
            "Резолв адрес і зміщень"
        ]),
        ("3. Перемикання W^X", "mprotect() / APRR", "PROT_READ | PROT_EXEC", "#dbeafe", NEG, [
            "W = 0, X = 1 (виконання)",
            "Запис заблоковано",
            "Очищення I-Cache"
        ]),
        ("4. Виконання коду", "Виклик покажчика на fn", "Регістри CPU -> fn()", "#dcfce7", FIELD, [
            "Стрибок CPU в код",
            "Повна швидкість заліза",
            "Звільнення: munmap()"
        ])
    ]

    col_w = 175
    gap = 22
    start_x = 22
    y = 70
    bh = 190

    for i, (title, sub, perm, bg_col, border_col, bullets) in enumerate(steps):
        bx = start_x + i * (col_w + gap)
        p.append(rect(bx, y, col_w, bh, fill=bg_col, stroke=border_col, sw=1.8, rx=8))
        p.append(text(bx + col_w / 2, y + 24, title, size=12, color=INK, bold=True))
        p.append(text(bx + col_w / 2, y + 42, sub, size=10, color=MUTED, italic=True))

        # Бейдж прав пам'яті
        p.append(rect(bx + 8, y + 54, col_w - 16, 26, fill="#ffffff", stroke=border_col, sw=1.2, rx=4))
        p.append(text(bx + col_w / 2, y + 71, perm, size=9, color=border_col, bold=True))

        for j, b in enumerate(bullets):
            p.append(text(bx + 10, y + 100 + j * 24, "• " + b, size=9.5, color=INK, anchor="start"))

        if i < len(steps) - 1:
            ax = bx + col_w + 2
            p.append(arrow(ax, y + bh / 2, ax + gap - 4, y + bh / 2, color=INK, sw=2.0))

    p.append(text(W / 2, 35, "Життєвий цикл виконуваної пам'яті за правилом W^X (Write XOR Execute)", size=14, color=INK, bold=True))
    p.append(text(W / 2, H - 18, "Сучасні ОС ніколи не дозволяють сторінці мати одночасно права запису й виконання", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "wx-memory-transition.svg"), W, H, *p,
           title="Життєвий цикл динамічної пам'яті під захистом W^X")


# ── 4. osr-stack-replacement: On-Stack Replacement та карта деоптимізації ────
def fig_osr_stack_replacement():
    W, H = 820, 360
    p = []

    # Лівий блок: Стек інтерпретатора
    lx, ly, lw, lh = 30, 80, 220, 220
    p.append(rect(lx, ly, lw, lh, fill="#f8fafc", stroke=LINE, sw=1.8, rx=8))
    p.append(text(lx + lw / 2, ly + 24, "Кадр інтерпретатора", size=13, color=INK, bold=True))
    p.append(text(lx + lw / 2, ly + 42, "байткод і віртуальний стек", size=10, color=MUTED, italic=True))

    interp_slots = [
        ("Локальна змінна [0]: i = 5000", "#e2e8f0"),
        ("Локальна змінна [1]: sum = 12502500", "#e2e8f0"),
        ("Стек операндів: [пусто / проміжне]", "#f1f5f9"),
        ("Покажчик байткоду (PC): 0x004A", "#fee2e2")
    ]
    for i, (slot, bg) in enumerate(interp_slots):
        sy = ly + 58 + i * 36
        p.append(rect(lx + 10, sy, lw - 20, 30, fill=bg, stroke="#94a3b8", sw=1.0, rx=4))
        p.append(text(lx + lw / 2, sy + 19, slot, size=9, color=INK))

    # Правий блок: Рідний машинний кадр JIT
    rx, ry, rw, rh = 570, 80, 220, 220
    p.append(rect(rx, ry, rw, rh, fill="#eff6ff", stroke=NEG, sw=1.8, rx=8))
    p.append(text(rx + rw / 2, ry + 24, "Машинний кадр JIT (x86-64)", size=13, color=NEG, bold=True))
    p.append(text(rx + rw / 2, ry + 42, "апаратні регістри процесора", size=10, color=MUTED, italic=True))

    jit_slots = [
        ("Регістр RAX: i = 5000", "#dbeafe"),
        ("Регістр RDX: sum = 12502500", "#dbeafe"),
        ("Стек [RSP+8]: збережений RBP", "#e0e7ff"),
        ("Лічильник RIP: 0x7FFF1004A020", "#fee2e2")
    ]
    for i, (slot, bg) in enumerate(jit_slots):
        sy = ry + 58 + i * 36
        p.append(rect(rx + 10, sy, rw - 20, 30, fill=bg, stroke="#93c5fd", sw=1.0, rx=4))
        p.append(text(rx + rw / 2, sy + 19, slot, size=9, color=INK))

    # Центральний блок: Карта безпеки / трансляції станів (Safepoint / Deopt Map)
    cx, cy, cw, ch = 275, 95, 270, 190
    p.append(rect(cx, cy, cw, ch, fill="#fefce8", stroke="#ca8a04", sw=1.8, rx=8))
    p.append(text(cx + cw / 2, cy + 24, "Карта станів (Deopt Map)", size=12, color="#854d0e", bold=True))
    p.append(text(cx + cw / 2, cy + 40, "відповідність змінних і регістрів", size=10, color=MUTED, italic=True))

    mappings = [
        "v0 (локальна i)    <--->  RAX",
        "v1 (локальна sum)  <--->  RDX",
        "байткод PC=0x4A   <--->  RIP=0x...020",
        "стан стека         <--->  RSP / RBP"
    ]
    for i, m in enumerate(mappings):
        my = cy + 56 + i * 28
        p.append(rect(cx + 8, my, cw - 16, 24, fill="#ffffff", stroke="#fde047", sw=1.0, rx=4))
        p.append(text(cx + cw / 2, my + 16, m, size=9, color=INK))

    # Стрілки OSR та Deopt
    # OSR зверху
    p.append(arrow(lx + lw + 2, 130, cx - 4, 130, color=FIELD, sw=2.0))
    p.append(arrow(cx + cw + 4, 130, rx - 4, 130, color=FIELD, sw=2.0))
    p.append(text(W / 2, 76, "OSR: підміна кадру на льоту в гарячому циклі →", size=10, color=FIELD, bold=True))

    # Deopt знизу
    p.append(arrow(rx - 4, 250, cx + cw + 4, 250, color=POS, sw=2.0))
    p.append(arrow(cx - 4, 250, lx + lw + 2, 250, color=POS, sw=2.0))
    p.append(text(W / 2, 314, "← Деоптимізація: реконструкція кадру інтерпретатора", size=10, color=POS, bold=True))

    p.append(text(W / 2, 35, "Взаємна трансляція стеків: заміна кадру (OSR) та реконструкція (Деоптимізація)", size=14, color=INK, bold=True))

    render(os.path.join(OUT, "osr-stack-replacement.svg"), W, H, *p,
           title="On-Stack Replacement та деоптимізація стека")


if __name__ == "__main__":
    fig_tiered_compilation()
    fig_inline_caching_states()
    fig_wx_memory_transition()
    fig_osr_stack_replacement()

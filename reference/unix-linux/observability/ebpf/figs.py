# -*- coding: utf-8 -*-
"""Генератор векторних діаграм для теми eBPF."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts")))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_architecture_overview():
    """Схема архітектури eBPF: користувацький простір, ядро, верифікатор, JIT, карти та хуки."""
    w, h = 880, 520
    frags = []

    # Заголовок / фонові зони
    # Користувацький простір (зліва)
    frags.append(rect(30, 40, 380, 440, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(220, 68, "ПРОСТІР КОРИСТУВАЧА (USER SPACE)", size=13, color=MUTED, bold=True))

    # Простір ядра (справа)
    frags.append(rect(450, 40, 400, 440, fill="#f1f5f9", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(650, 68, "ПРОСТІР ЯДРА (KERNEL SPACE / RING 0)", size=13, color=POS, bold=True))

    # 1. User space blocks
    b_src, _, _ = textbox(220, 115, "Сирцевий код C / Rust\n(eBPF Program Source)", size=12, pad=8, fill="#ffffff", stroke="#64748b")
    frags.append(b_src)
    b_llvm, _, _ = textbox(220, 195, "Clang / LLVM Компілятор\n(Target: BPF Bytecode + BTF)", size=12, pad=8, fill="#ffffff", stroke="#64748b")
    frags.append(b_llvm)
    b_loader, _, _ = textbox(220, 280, "Програма-завантажувач (libbpf / C / C++)\nРозбір ELF, створення мап, bpf()", size=12, pad=8, fill="#e2e8f0", stroke="#475569", bold=True)
    frags.append(b_loader)
    b_user_read, _, _ = textbox(220, 410, "Зчитування метрик і подій\n(Ring Buffer / Map Lookup)", size=12, pad=8, fill="#ffffff", stroke="#64748b")
    frags.append(b_user_read)

    frags.append(arrow(220, 142, 220, 168, color=LINE, sw=1.5))
    frags.append(arrow(220, 222, 220, 252, color=LINE, sw=1.5))

    # Системний виклик sys_bpf
    frags.append(arrow(360, 280, 490, 280, color=NEG, sw=2.0))
    frags.append(text(425, 270, "sys_bpf()", size=11, color=NEG, bold=True))

    # 2. Kernel space blocks
    b_verif, _, _ = textbox(650, 120, "Верифікатор eBPF (In-Kernel Verifier)\nПеревірка DAG, меж діапазонів, типів і вказівників", size=12, pad=10, fill="#ffffff", stroke=POS, bold=True)
    frags.append(b_verif)
    b_jit, _, _ = textbox(650, 205, "JIT-компілятор ядра (x86_64 / ARM64)\nГенерація нативного машинного коду", size=12, pad=8, fill="#ffffff", stroke=FIELD)
    frags.append(b_jit)
    b_attach, _, _ = textbox(650, 290, "Точки інструментування (Hooks)\nTracepoints / kprobes / fentry / XDP / cgroups", size=12, pad=8, fill="#ffffff", stroke="#64748b")
    frags.append(b_attach)
    b_maps, _, _ = textbox(650, 410, "BPF Maps & Ring Buffer\nСпільна пам'ять ядра для стану та подій", size=12, pad=10, fill="#ffffff", stroke=NEG, bold=True)
    frags.append(b_maps)

    # Зв'язки всередині ядра
    frags.append(arrow(570, 260, 570, 155, color=LINE, sw=1.5))
    frags.append(arrow(650, 155, 650, 178, color=FIELD, sw=1.8))
    frags.append(text(690, 168, "Безпечно", size=10, color=FIELD, bold=True))
    frags.append(arrow(650, 232, 650, 262, color=LINE, sw=1.5))

    # Виконання на події -> оновлення мап
    frags.append(arrow(650, 320, 650, 378, color=LINE, sw=1.5))
    frags.append(text(730, 350, "Оновлення стану", size=10, color=MUTED))

    # Передача даних назад у Userspace
    frags.append(arrow(530, 410, 345, 410, color=NEG, sw=1.8))
    frags.append(text(435, 400, "Читання без копіювання", size=10, color=NEG))

    render(os.path.join(OUT_DIR, "ebpf-architecture-overview.svg"), w, h, *frags)


def fig_verifier_state_machine():
    """Схема роботи верифікатора eBPF: аналіз графу, перевірка меж і стану регістрів."""
    w, h = 880, 420
    frags = []

    # 1. Байт-код на вході
    b_in, _, _ = textbox(130, 70, "BPF Байт-код\n(Інструкції програми)", size=12, pad=10, fill="#ffffff", stroke="#64748b", bold=True)
    frags.append(b_in)
    frags.append(arrow(130, 102, 130, 148, color=LINE, sw=1.5))

    # 2. CFG перевірка
    b_cfg, _, _ = textbox(130, 190, "1. Контроль графу (CFG)\n• Пошук недосяжного коду\n• Доведення завершення\n• Контроль обмежених циклів", size=11, pad=10, fill="#f8fafc", stroke="#64748b")
    frags.append(b_cfg)
    frags.append(arrow(245, 190, 305, 190, color=LINE, sw=1.5))

    # 3. Аналіз станів та абстрактна інтерпретація
    b_states, _, _ = textbox(450, 190, "2. Аналіз станів і типів\n• Типи регістрів (SCALAR, PTR)\n• Відстеження меж [min, max]\n• Контроль валідності вказівників\n• Глибина стеку (<= 512 байтів)", size=11, pad=10, fill="#f8fafc", stroke=POS, bold=True)
    frags.append(b_states)
    frags.append(arrow(595, 190, 655, 190, color=LINE, sw=1.5))

    # 4. Прунінг та фінал
    b_prune, _, _ = textbox(760, 190, "3. Прунінг станів\n• Порівняння з еквівалентними\n• Захист від вибуху станів\n• Ліміт інструкцій (1M)", size=11, pad=10, fill="#f8fafc", stroke="#64748b")
    frags.append(b_prune)

    # Гілки результату
    # Успіх (вгору)
    frags.append(arrow(760, 140, 760, 85, color=FIELD, sw=2.0))
    b_pass, _, _ = textbox(760, 60, "СХВАЛЕНО (Pass)\nПередача до JIT-компілятора", size=12, pad=10, fill="#eafaf1", stroke=FIELD, bold=True, color=FIELD)
    frags.append(b_pass)

    # Помилка (вниз)
    frags.append(arrow(450, 260, 450, 330, color=POS, sw=2.0))
    frags.append(text(500, 295, "Порушення правил", size=11, color=POS, bold=True))
    b_fail, _, _ = textbox(450, 365, "ВІДХИЛЕНО (Verifier Log / -EACCES)\n• NULL dereference • Вихід за межі масиву\n• Неініціалізована пам'ять • Нескінченний цикл", size=11, pad=10, fill="#fdf2f2", stroke=POS, color=POS)
    frags.append(b_fail)

    render(os.path.join(OUT_DIR, "ebpf-verifier-state-machine.svg"), w, h, *frags)


def fig_registers_and_stack():
    """Схема архітектури віртуального процесора eBPF: регістри R0-R10 та кадр стеку."""
    w, h = 880, 460
    frags = []

    # Заголовок регістрового файлу
    frags.append(text(260, 40, "Регістровий файл eBPF (11 x 64-бітних регістрів)", size=14, color=INK, bold=True))

    # Таблиця регістрів
    regs = [
        ("R0", "Результат виконання / Код повернення", "rax / x0", FIELD),
        ("R1", "1-й аргумент / Контекст виконання (ctx)", "rdi / x0", NEG),
        ("R2", "2-й аргумент функції-хелпера", "rsi / x1", NEG),
        ("R3", "3-й аргумент функції-хелпера", "rdx / x2", NEG),
        ("R4", "4-й аргумент функції-хелпера", "rcx / x3", NEG),
        ("R5", "5-й аргумент функції-хелпера", "r8 / x4", NEG),
        ("R6", "Збережений регістр (Callee-saved)", "rbx / x19", INK),
        ("R7", "Збережений регістр (Callee-saved)", "r13 / x20", INK),
        ("R8", "Збережений регістр (Callee-saved)", "r14 / x21", INK),
        ("R9", "Збережений регістр (Callee-saved)", "r15 / x22", INK),
        ("R10", "Вказівник стеку (Frame Pointer, Read-Only)", "rbp / x29", POS),
    ]

    y_start = 70
    for i, (reg, role, mapping, col) in enumerate(regs):
        y = y_start + i * 32
        frags.append(rect(50, y, 60, 26, fill="#f1f5f9", stroke=col, sw=1.5, rx=4))
        frags.append(text(80, y + 18, reg, size=12, color=col, bold=True))
        frags.append(rect(120, y, 260, 26, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
        frags.append(text(250, y + 17, role, size=11, color=INK))
        frags.append(rect(390, y, 90, 26, fill="#f8fafc", stroke="#cbd5e1", sw=1.0, rx=4))
        frags.append(text(435, y + 17, mapping, size=11, color=MUTED))

    # Кадр стеку eBPF справа
    frags.append(text(670, 40, "Кадр стеку програми eBPF (512 B)", size=14, color=INK, bold=True))
    frags.append(rect(540, 70, 270, 345, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=6))

    # Слот R10
    frags.append(rect(555, 85, 240, 40, fill="#fee2e2", stroke=POS, sw=1.5, rx=4))
    frags.append(text(675, 105, "R10: Верхня межа кадру (0B)", size=12, color=POS, bold=True))
    frags.append(text(675, 120, "Фіксований Read-Only вказівник", size=10, color=MUTED))

    # Стек росте вниз
    frags.append(arrow(530, 110, 530, 390, color=POS, sw=1.8))
    frags.append(text(505, 250, "Зростання стеку вниз (-offset)", size=11, color=POS, bold=True))

    frags.append(rect(555, 145, 240, 60, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    frags.append(text(675, 170, "Локальні змінні та структури", size=11, color=INK, bold=True))
    frags.append(text(675, 190, "[R10 - 8] ... [R10 - 64]", size=11, color=MUTED))

    frags.append(rect(555, 225, 240, 70, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    frags.append(text(675, 250, "Буфери для ключів / значень мап", size=11, color=INK, bold=True))
    frags.append(text(675, 272, "Передача адреси в R2 / R3 для helper", size=10, color=MUTED))

    frags.append(rect(555, 315, 240, 40, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    frags.append(text(675, 340, "Нижня межа стеку (-512 B)", size=11, color=POS, bold=True))

    render(os.path.join(OUT_DIR, "ebpf-registers-and-stack.svg"), w, h, *frags)


def fig_maps_memory_model():
    """Схема архітектури та моделі пам'яті BPF Maps: зв'язок між ядром і userspace."""
    w, h = 880, 440
    frags = []

    # Користувацький простір зверху
    frags.append(rect(40, 30, 800, 100, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(440, 55, "ПРОСТІР КОРИСТУВАЧА (USER SPACE)", size=12, color=MUTED, bold=True))
    b_u1, _, _ = textbox(220, 95, "Процес моніторингу A (fd: 4)", size=11, pad=6, fill="#ffffff", stroke="#64748b")
    frags.append(b_u1)
    b_u2, _, _ = textbox(440, 95, "Процес конфігурації B (fd: 7)", size=11, pad=6, fill="#ffffff", stroke="#64748b")
    frags.append(b_u2)
    b_u3, _, _ = textbox(660, 95, "Колектор метрик C (fd: 9)", size=11, pad=6, fill="#ffffff", stroke="#64748b")
    frags.append(b_u3)

    # Стрілки між просторами та центральний блок системного виклику
    b_call, _, _ = textbox(440, 150, "Системні виклики bpf(BPF_MAP_*_ELEM) через файлові дескриптори", size=11, pad=6, fill="#ffffff", stroke=NEG, bold=True, color=NEG)
    frags.append(b_call)

    frags.append(arrow(220, 115, 220, 135, color=NEG, sw=1.5))
    frags.append(arrow(440, 115, 440, 135, color=NEG, sw=1.5))
    frags.append(arrow(660, 115, 660, 135, color=NEG, sw=1.5))

    frags.append(arrow(220, 165, 220, 190, color=NEG, sw=1.5))
    frags.append(arrow(440, 165, 440, 190, color=NEG, sw=1.5))
    frags.append(arrow(660, 165, 660, 190, color=NEG, sw=1.5))

    # Простір ядра знизу
    frags.append(rect(40, 190, 800, 220, fill="#f1f5f9", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(440, 215, "ПРОСТІР ЯДРА: ТИПИ СТРУКТУР BPF MAPS", size=12, color=POS, bold=True))

    # Типи мап
    b_m1, _, _ = textbox(160, 280, "BPF_MAP_TYPE_HASH\nХеш-таблиця ключ-значення\nДинамічна пам'ять, колізії", size=11, pad=8, fill="#ffffff", stroke="#64748b")
    frags.append(b_m1)
    b_m2, _, _ = textbox(350, 280, "BPF_MAP_TYPE_ARRAY\nМасив фіксованого розміру\nШвидкий доступ O(1), індекс uint32", size=11, pad=8, fill="#ffffff", stroke="#64748b")
    frags.append(b_m2)
    b_m3, _, _ = textbox(540, 280, "BPF_MAP_TYPE_PERCPU_ARRAY\nОкремий масив на кожне CPU\nБез блокувань, без cache bouncing", size=11, pad=8, fill="#ffffff", stroke=FIELD, bold=True)
    frags.append(b_m3)
    b_m4, _, _ = textbox(720, 280, "BPF_MAP_TYPE_RINGBUF\nКільцевий буфер подій MPSC\nЕфективний стрімінг у userspace", size=11, pad=8, fill="#ffffff", stroke=NEG, bold=True)
    frags.append(b_m4)

    # Програми eBPF у ядрі звертаються до мап
    b_progs, _, _ = textbox(440, 375, "eBPF Програми (XDP / kprobe / tracepoint) -> bpf_map_lookup_elem() / bpf_ringbuf_output()", size=11, pad=6, fill="#fee2e2", stroke=POS, color=POS, bold=True)
    frags.append(b_progs)
    frags.append(arrow(240, 360, 160, 320, color=POS, sw=1.5))
    frags.append(arrow(380, 360, 350, 320, color=POS, sw=1.5))
    frags.append(arrow(500, 360, 540, 320, color=POS, sw=1.5))
    frags.append(arrow(640, 360, 720, 320, color=POS, sw=1.5))

    render(os.path.join(OUT_DIR, "ebpf-maps-memory-model.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_architecture_overview()
    fig_verifier_state_machine()
    fig_registers_and_stack()
    fig_maps_memory_model()
    print("Усі фігури успішно згенеровано.")

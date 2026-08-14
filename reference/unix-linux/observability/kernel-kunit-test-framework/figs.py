import sys
import os

# Four levels up to reach scripts/ directory from reference/unix-linux/observability/kernel-kunit-test-framework
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts")))

from svgkit import render, fitbox, rect, text, arrow

def fig_kunit_architecture(out_dir):
    w, h = 820, 520
    frags = []

    # 1. User Space / Host
    frags.append(rect(20, 45, 780, 100, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(35, 65, "Хост-система та інструментарій розробника (User Space / Host)", size=12, color="#64748b", anchor="start", bold=True))

    b1 = fitbox(40, 80, 220, 50, "kunit.py CLI\n(Python runner)", fill="#e0f2fe", stroke="#0284c7", bold=True)
    b2 = fitbox(295, 80, 230, 50, ".kunitconfig\n(Мінімальний Kconfig)", fill="#f1f5f9", stroke="#64748b")
    b3 = fitbox(550, 80, 230, 50, "TAP 14 Parser\n(Аналіз результатів)", fill="#e0e7ff", stroke="#4f46e5", bold=True)

    frags.extend([b1, b2, b3])

    # Arrow from kunit.py to UML Kernel
    frags.append(arrow(150, 145, 150, 180, color="#0284c7", sw=2))
    frags.append(arrow(665, 180, 665, 145, color="#4f46e5", sw=2))
    frags.append(text(160, 168, "Запуск UML / QEMU", size=11, color="#0284c7", anchor="start"))
    frags.append(text(655, 168, "TAP поток stdout", size=11, color="#4f46e5", anchor="end"))

    # 2. Kernel Space
    frags.append(rect(20, 185, 780, 315, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=8))
    frags.append(text(35, 205, "Простір ядра Linux (Kernel Space / User Mode Linux)", size=12, color="#15803d", anchor="start", bold=True))

    # ELF Section
    b_elf = fitbox(40, 225, 740, 45, "Спеціальна секція компонувальника ELF: .kunit_test_suites (масив вказівників struct kunit_suite*)", fill="#dcfce7", stroke="#16a34a", bold=True)
    frags.append(b_elf)

    # KUnit Executor
    b_exec = fitbox(40, 290, 740, 45, "Ядро KUnit (kunit_run_tests / initcall) — ініціалізація struct kunit та управління ресурсами", fill="#ffffff", stroke="#15803d")
    frags.append(b_exec)

    frags.append(arrow(410, 270, 410, 290, color="#16a34a", sw=2))

    # Test Suites and Cases
    b_s1 = fitbox(40, 360, 230, 120, "Suite: ring_buffer_test\n\n- Case: test_enqueue_ok\n- Case: test_buffer_full\n- Case: test_overflow", fill="#ffffff", stroke="#059669")
    b_s2 = fitbox(295, 360, 230, 120, "Suite: hash_table_test\n\n- Case: test_insert_find\n- Case: test_bucket_collision\n- Case: test_resize", fill="#ffffff", stroke="#059669")
    b_s3 = fitbox(550, 360, 230, 120, "Контекст тесту (struct kunit)\n\n- kunit_kmalloc()\n- KUNIT_EXPECT_EQ()\n- KUNIT_ASSERT_NOT_NULL()", fill="#fef3c7", stroke="#d97706")

    frags.extend([b_s1, b_s2, b_s3])

    frags.append(arrow(150, 335, 150, 360, color="#059669", sw=1.8))
    frags.append(arrow(410, 335, 410, 360, color="#059669", sw=1.8))
    frags.append(arrow(665, 335, 665, 360, color="#d97706", sw=1.8))

    path = os.path.join(out_dir, "kunit-architecture.svg")
    render(path, w, h, *frags, title="Архітектура та потік виконання фреймворку KUnit")

def fig_sanitizers_comparison(out_dir):
    w, h = 820, 480
    frags = []

    col_w = 245
    gap = 15
    top_y = 50
    box_h = 410

    # KASAN Column
    x1 = 20
    frags.append(rect(x1, top_y, col_w, box_h, fill="#fef2f2", stroke="#dc2626", sw=1.5, rx=8))
    frags.append(text(x1 + col_w/2, top_y + 25, "KASAN", size=16, color="#991b1b", bold=True))
    frags.append(text(x1 + col_w/2, top_y + 45, "Kernel Address Sanitizer", size=11, color="#64748b"))

    b_kasan_desc = fitbox(x1 + 10, top_y + 60, col_w - 20, 110, "Принцип:\nShadow Memory (1B тіні на 8B RAM).\nПокриває 100% виділень slab/page.\n\nПомилки: UAF, Out-of-Bounds.", fill="#ffffff", stroke="#fca5a5")
    b_kasan_stats = fitbox(x1 + 10, top_y + 180, col_w - 20, 100, "Накладні витрати:\n- Пам'ять: +12.5% .. +100%\n- CPU: 2x .. 3x уповільнення", fill="#fee2e2", stroke="#ef4444")
    b_kasan_target = fitbox(x1 + 10, top_y + 295, col_w - 20, 100, "Цільове середовище:\n- Тестові CI/CD стенди\n- UML / QEMU запуск\n- Локальне розробницьке\n  відлагодження", fill="#ffffff", stroke="#dc2626")

    frags.extend([b_kasan_desc, b_kasan_stats, b_kasan_target])

    # KFENCE Column
    x2 = x1 + col_w + gap
    frags.append(rect(x2, top_y, col_w, box_h, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=8))
    frags.append(text(x2 + col_w/2, top_y + 25, "KFENCE", size=16, color="#166534", bold=True))
    frags.append(text(x2 + col_w/2, top_y + 45, "Kernel Electric-Fence", size=11, color="#64748b"))

    b_kfence_desc = fitbox(x2 + 10, top_y + 60, col_w - 20, 110, "Принцип:\nSampling Electric Guard Pages.\nЗахисні сторінки PROT_NONE навколо 1 з N виділень.", fill="#ffffff", stroke="#86efac")
    b_kfence_stats = fitbox(x2 + 10, top_y + 180, col_w - 20, 100, "Накладні витрати:\n- Пам'ять: ~1-2 MB\n- CPU: < 1% уповільнення", fill="#dcfce7", stroke="#22c55e")
    b_kfence_target = fitbox(x2 + 10, top_y + 295, col_w - 20, 100, "Цільове середовище:\n- Production бойові ядра\n- Довготривале стрес-тестування\n- Неперервний моніторинг у продакшні", fill="#ffffff", stroke="#16a34a")

    frags.extend([b_kfence_desc, b_kfence_stats, b_kfence_target])

    # KCSAN Column
    x3 = x2 + col_w + gap
    frags.append(rect(x3, top_y, col_w, box_h, fill="#fffbebe", stroke="#d97706", sw=1.5, rx=8))
    frags.append(text(x3 + col_w/2, top_y + 25, "KCSAN", size=16, color="#92400e", bold=True))
    frags.append(text(x3 + col_w/2, top_y + 45, "Kernel Concurrency Sanitizer", size=11, color="#64748b"))

    b_kcsan_desc = fitbox(x3 + 10, top_y + 60, col_w - 20, 110, "Принцип:\nКомпіляторна інструментація + Watchpoints та мікро-затримки.\nДетектує конфлікти читання/запису.", fill="#ffffff", stroke="#fde68a")
    b_kcsan_stats = fitbox(x3 + 10, top_y + 180, col_w - 20, 100, "Накладні витрати:\n- Пам'ять: мінімальні\n- CPU: 2x .. 4x уповільнення", fill="#fef3c7", stroke="#f59e0b")
    b_kcsan_target = fitbox(x3 + 10, top_y + 295, col_w - 20, 100, "Цільове середовище:\n- Пошук Race Conditions\n- Тестування паралельних\n  структур даних у CI\n- Стрес-тести SMP", fill="#ffffff", stroke="#d97706")

    frags.extend([b_kcsan_desc, b_kcsan_stats, b_kcsan_target])

    path = os.path.join(out_dir, "sanitizers-comparison.svg")
    render(path, w, h, *frags, title="Порівняння механізмів відлагоджувачів: KASAN vs KFENCE vs KCSAN")

def fig_kunit_ci_pipeline(out_dir):
    w, h = 820, 360
    frags = []

    steps = [
        ("1. Git Commit / PR", "Розробник надсилає\nпатч ядра або тесту", "#f1f5f9", "#475569"),
        ("2. kunit.py Run", "Компіляція UML\nз .kunitconfig", "#e0f2fe", "#0284c7"),
        ("3. Sanitizer Execution", "Виконання тестів під\nKASAN / KCSAN / KFENCE", "#fee2e2", "#dc2626"),
        ("4. TAP Parsing", "Форматування результатів\nу TAP 14 / Junit XML", "#fef3c7", "#d97706"),
        ("5. CI Gate & Coverage", "Аналіз gcov/kcov,\nблокування при багах", "#dcfce7", "#16a34a")
    ]

    bx_w = 144
    gap = 16
    start_x = 20
    cy = 180

    for i, (title_str, desc_str, fill_c, stroke_c) in enumerate(steps):
        x = start_x + i * (bx_w + gap)
        b = fitbox(x, cy - 80, bx_w, 160, f"{title_str}\n\n{desc_str}", fill=fill_c, stroke=stroke_c, bold=True)
        frags.append(b)

        if i < len(steps) - 1:
            arrow_start_x = x + bx_w
            arrow_end_x = arrow_start_x + gap
            frags.append(arrow(arrow_start_x, cy, arrow_end_x, cy, color=stroke_c, sw=2))

    path = os.path.join(out_dir, "kunit-ci-pipeline.svg")
    render(path, w, h, *frags, title="Конвеєр автоматизованого тестування ядра у CI/CD")

def main():
    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "img"))
    os.makedirs(out_dir, exist_ok=True)
    fig_kunit_architecture(out_dir)
    fig_sanitizers_comparison(out_dir)
    fig_kunit_ci_pipeline(out_dir)
    print("Figures generated successfully in", out_dir)

if __name__ == "__main__":
    main()

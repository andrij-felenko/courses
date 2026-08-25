# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── 1. Вбудований асемблер у конвеєрі компілятора ──
def fig_compiler_pipeline_asm():
    W, H = 820, 360
    p = []
    
    p.append(rect(20, 20, 780, 320, fill="#f8fafc", stroke=LINE, sw=1.2, rx=12))
    p.append(text(W / 2, 44, "Інтеграція Extended Asm у проміжне представлення та генератор коду", size=14, bold=True))
    
    b1_x, b1_y, b1_w, b1_h = 40, 75, 220, 235
    p.append(rect(b1_x, b1_y, b1_w, b1_h, fill=BG, stroke=NEG, sw=1.5, rx=8))
    p.append(text(b1_x + b1_w/2, b1_y + 24, "1. Синтаксичний аналіз (IR)", size=12, color=NEG, bold=True))
    p.append(fitbox(b1_x + 12, b1_y + 45, b1_w - 24, 75,
                    "asm volatile (\n  \"template\"\n  : outputs\n  : inputs\n)", size=11, fill="#edf2f7", stroke="#cbd5e1"))
    p.append(fitbox(b1_x + 12, b1_y + 130, b1_w - 24, 85,
                    "Компілятор будує вузол IR:\n• список змінних-виходів\n• список змінних-входів\n• рядки обмежень (constraints)", size=10.5, fill=BG, stroke=LINE, sw=1))

    p.append(arrow(b1_x + b1_w + 5, b1_y + b1_h/2, b1_x + b1_w + 35, b1_y + b1_h/2, color=LINE, sw=2))

    b2_x, b2_y, b2_w, b2_h = 300, 75, 220, 235
    p.append(rect(b2_x, b2_y, b2_w, b2_h, fill=BG, stroke=FIELD, sw=1.5, rx=8))
    p.append(text(b2_x + b2_w/2, b2_y + 24, "2. Розподіл регістрів", size=12, color=FIELD, bold=True))
    p.append(fitbox(b2_x + 12, b2_y + 45, b2_w - 24, 75,
                    "Розбір обмежень:\n\"r\" -> довільний GP регістр\n\"=a\" -> фіксований RAX/EAX\n\"m\" -> адреса в пам'яті", size=10.5, fill="#f0fdf4", stroke="#bbf7d0"))
    p.append(fitbox(b2_x + 12, b2_y + 130, b2_w - 24, 85,
                    "Генерація пересилань:\n• завантаження входів у регістри\n• резервування clobbers\n• виділення пам'яті для виходів", size=10.5, fill=BG, stroke=LINE, sw=1))

    p.append(arrow(b2_x + b2_w + 5, b2_y + b2_h/2, b2_x + b2_w + 35, b2_y + b2_h/2, color=LINE, sw=2))

    b3_x, b3_y, b3_w, b3_h = 560, 75, 220, 235
    p.append(rect(b3_x, b3_y, b3_w, b3_h, fill=BG, stroke=POS, sw=1.5, rx=8))
    p.append(text(b3_x + b3_w/2, b3_y + 24, "3. Емісія тексту асемблера", size=12, color=POS, bold=True))
    p.append(fitbox(b3_x + 12, b3_y + 45, b3_w - 24, 75,
                    "Підстановка операндів:\n%0 -> %rax, %1 -> %rbx\nРядок-шаблон перетворюється\nна чисті інструкції", size=10.5, fill="#fef2f2", stroke="#fecaca"))
    p.append(fitbox(b3_x + 12, b3_y + 130, b3_w - 24, 85,
                    "Фінальний вивід:\nКомпілятор передає текст\nпрямо у системний асемблер\n(GNU as / LLVM MC)", size=10.5, fill=BG, stroke=LINE, sw=1))

    render(os.path.join(OUT, "fig1-compiler-pipeline-asm.svg"), W, H, *p)


# ── 2. Модифікатори обмежень: звичайний вихід vs Earlyclobber ──
def fig_constraint_modifiers():
    W, H = 820, 380
    p = []
    
    p.append(rect(20, 20, 780, 340, fill="#f8fafc", stroke=LINE, sw=1.2, rx=12))
    p.append(text(W / 2, 45, "Механізм розподілу регістрів: звичайний вихід (=r) проти Earlyclobber (=&amp;r)", size=14, bold=True))
    
    x1, y1, w1, h1 = 40, 70, 360, 270
    p.append(rect(x1, y1, w1, h1, fill=BG, stroke=POS, sw=1.5, rx=8))
    p.append(text(x1 + w1/2, y1 + 24, "Небезпека: вихід \"=r\" без раннього клірингу", size=12, color=POS, bold=True))
    
    p.append(fitbox(x1 + 15, y1 + 45, w1 - 30, 50,
                    "asm (\"add %1, %0\\n  inc %0\"\n     : \"=r\" (out) : \"r\" (in1));", size=11, fill="#fef2f2", stroke="#fecaca"))
    
    p.append(fitbox(x1 + 15, y1 + 105, w1 - 30, 75,
                    "1. Компілятор вважає, що in1 читається ДО запису out\n2. Алокатор призначає out та in1 ОДИН регістр (наприклад RAX)\n3. Підстановка: add %rax, %rax (in1 пошкоджено на першому кроці!)", size=10, fill=BG, stroke=LINE, sw=1))
    
    p.append(fitbox(x1 + 15, y1 + 190, w1 - 30, 65,
                    "НАСЛІДОК: тихий збій обчислень при -O2,\nколи оптимізатор мінімізує кількість регістрів", size=10.5, fill="#fff1f2", stroke=POS, bold=True, color=POS))

    x2, y2, w2, h2 = 420, 70, 360, 270
    p.append(rect(x2, y2, w2, h2, fill=BG, stroke=FIELD, sw=1.5, rx=8))
    p.append(text(x2 + w2/2, y2 + 24, "Коректно: Earlyclobber \"=&amp;r\" гарантує унікальність", size=12, color=FIELD, bold=True))
    
    p.append(fitbox(x2 + 15, y2 + 45, w2 - 30, 50,
                    "asm (\"add %1, %0\\n  inc %0\"\n     : \"=&r\" (out) : \"r\" (in1));", size=11, fill="#f0fdf4", stroke="#bbf7d0"))
    
    p.append(fitbox(x2 + 15, y2 + 105, w2 - 30, 75,
                    "1. Модифікатор & забороняє повторне використання регістрів\n2. Алокатор зобов'язаний обрати різні регістри:\n   out -> RDX, in1 -> RAX\n3. Підстановка: add %rax, %rdx — вхідні дані непошкоджені!", size=10, fill=BG, stroke=LINE, sw=1))
    
    p.append(fitbox(x2 + 15, y2 + 190, w2 - 30, 65,
                    "РЕЗУЛЬТАТ: коректна робота за будь-якого рівня\nоптимізації та тиску на регістровий файл", size=10.5, fill="#f0fdf4", stroke=FIELD, bold=True, color=FIELD))

    render(os.path.join(OUT, "fig2-constraint-modifiers.svg"), W, H, *p)


# ── 3. Порівняння моделей: MSVC __asm vs GCC Extended Asm ──
def fig_msvc_vs_gcc():
    W, H = 820, 370
    p = []
    
    p.append(rect(20, 20, 780, 330, fill="#f8fafc", stroke=LINE, sw=1.2, rx=12))
    p.append(text(W / 2, 45, "Архітектурний розрив: непрозорий MSVC __asm проти декларативного GCC/Clang Asm", size=14, bold=True))
    
    mx, my, mw, mh = 40, 70, 360, 260
    p.append(rect(mx, my, mw, mh, fill=BG, stroke=MUTED, sw=1.5, rx=8))
    p.append(text(mx + mw/2, my + 24, "MSVC x86: Блоковий __asm", size=12, color=INK, bold=True))
    p.append(fitbox(mx + 15, my + 45, mw - 30, 65,
                    "__asm {\n  mov eax, x\n  add eax, y\n  mov z, eax\n}", size=11, fill="#f1f5f9", stroke="#cbd5e1"))
    p.append(fitbox(mx + 15, my + 120, mw - 30, 125,
                    "ВЛАСТИВОСТІ МОДЕЛІ:\n• Непрозорий чорний ящик для оптимізатора\n• Компілятор змушений скидати всі регістри на стек\n• Неможливо вказати вхідні/вихідні залежності\n• Зламав глобальний розподіл регістрів у SSA\n• ПОВНІСТЮ ВИДАЛЕНО у MSVC для x86-64 та ARM64", size=10, fill="#fff1f2", stroke="#fca5a5"))

    gx, gy, gw, gh = 420, 70, 360, 260
    p.append(rect(gx, gy, gw, gh, fill=BG, stroke=FIELD, sw=1.5, rx=8))
    p.append(text(gx + gw/2, gy + 24, "GCC / Clang: Extended Asm Contract", size=12, color=FIELD, bold=True))
    p.append(fitbox(gx + 15, gy + 45, gw - 30, 65,
                    "asm volatile (\n  \"add %1, %0\"\n  : \"=r\" (z)\n  : \"r\" (x), \"0\" (y) : \"cc\"\n);", size=10.5, fill="#f0fdf4", stroke="#bbf7d0"))
    p.append(fitbox(gx + 15, gy + 120, gw - 30, 125,
                    "ВЛАСТИВОСТІ МОДЕЛІ:\n• Чіткий контракт залежностей (inputs, outputs, clobbers)\n• Повна інтеграція у граф SSA та конвеєр оптимізацій\n• Регістри виділяються компілятором без зайвих spill\n• Працює на всіх архітектурах (x86, x64, ARM, RISC-V)\n• Загальновизнаний промисловий стандарт", size=10, fill="#f0fdf4", stroke="#86efac"))

    render(os.path.join(OUT, "fig3-msvc-vs-gcc.svg"), W, H, *p)


# ── 4. Бар'єр компілятора vs Апаратний бар'єр пам'яті ──
def fig_barrier_reordering():
    W, H = 820, 370
    p = []
    
    p.append(rect(20, 20, 780, 330, fill="#f8fafc", stroke=LINE, sw=1.2, rx=12))
    p.append(text(W / 2, 45, "Бар'єр компілятора (\"memory\" clobber) проти Апаратного бар'єра процесора", size=14, bold=True))
    
    bx1, by1, bw1, bh1 = 40, 70, 360, 260
    p.append(rect(bx1, by1, bw1, bh1, fill=BG, stroke=NEG, sw=1.5, rx=8))
    p.append(text(bx1 + bw1/2, by1 + 24, "Програмний бар'єр компілятора", size=12, color=NEG, bold=True))
    p.append(fitbox(bx1 + 15, by1 + 45, bw1 - 30, 45,
                    "asm volatile (\"\" ::: \"memory\");", size=11, fill="#eff6ff", stroke="#bfdbfe"))
    p.append(fitbox(bx1 + 15, by1 + 100, bw1 - 30, 80,
                    "ДІЯ НА ЕТАПІ КОМПІЛЯЦІЇ:\n• Забороняє компілятору переставляти читання й записи\n• Скидає кешовані в регістрах значення змінних у RAM\n• Не генерує ЖОДНОЇ машинної інструкції (0 байтів коду)", size=10, fill=BG, stroke=LINE, sw=1))
    p.append(fitbox(bx1 + 15, by1 + 190, bw1 - 30, 60,
                    "МЕЖА ДІЇ: безсилий проти апаратного\nпозачергового виконання інструкцій CPU (Out-of-Order)", size=10, fill="#fef2f2", stroke=POS, color=POS, bold=True))

    bx2, by2, bw2, bh2 = 420, 70, 360, 260
    p.append(rect(bx2, by2, bw2, bh2, fill=BG, stroke=FIELD, sw=1.5, rx=8))
    p.append(text(bx2 + bw2/2, by2 + 24, "Апаратний бар'єр процесора (CPU Barrier)", size=12, color=FIELD, bold=True))
    p.append(fitbox(bx2 + 15, by2 + 45, bw2 - 30, 45,
                    "asm volatile (\"mfence\" ::: \"memory\"); // x86\nasm volatile (\"dmb ish\" ::: \"memory\"); // ARM", size=10.5, fill="#f0fdf4", stroke="#bbf7d0"))
    p.append(fitbox(bx2 + 15, by2 + 100, bw2 - 30, 80,
                    "ДІЯ НА ЕТАПІ ВИКОНАННЯ (РУХ У КРЕМНІЇ):\n• Зупиняє конвеєр вибірки/виконання CPU\n• Скидає буфери запису (Store Buffers) у кеш L1/L2\n• Забезпечує когерентність та видимість для інших ядер", size=10, fill=BG, stroke=LINE, sw=1))
    p.append(fitbox(bx2 + 15, by2 + 190, bw2 - 30, 60,
                    "РЕЗУЛЬТАТ: гарантує фізичний порядок доступу\nдо оперативної пам'яті між різними ядрами", size=10, fill="#f0fdf4", stroke=FIELD, color=FIELD, bold=True))

    render(os.path.join(OUT, "fig4-barrier-reordering.svg"), W, H, *p)


# ── 5. Intrinsics проти Inline Assembly: шлях оптимізацій ──
def fig_intrinsics_vs_inline_asm():
    W, H = 820, 380
    p = []
    
    p.append(rect(20, 20, 780, 340, fill="#f8fafc", stroke=LINE, sw=1.2, rx=12))
    p.append(text(W / 2, 45, "Порівняння оптимізаційного шляху: Вбудовані функції (Intrinsics) vs Inline Asm", size=14, bold=True))
    
    ix, iy, iw, ih = 40, 70, 360, 270
    p.append(rect(ix, iy, iw, ih, fill=BG, stroke=FIELD, sw=1.5, rx=8))
    p.append(text(ix + iw/2, iy + 24, "Вбудовані функції (Intrinsics)", size=12, color=FIELD, bold=True))
    p.append(fitbox(ix + 15, iy + 45, iw - 30, 45,
                    "__m128 c = _mm_add_ps(a, b);\nint lz = __builtin_clz(x);", size=11, fill="#f0fdf4", stroke="#bbf7d0"))
    p.append(fitbox(ix + 15, iy + 100, iw - 30, 95,
                    "ПЕРЕВАГИ ОПТИМІЗАЦІЇ:\n• Повна видимість у проміжному графі (SSA IR)\n• Constant Folding: вираховування констант під час компіляції\n• Dead Code Elimination: видалення непотрібного коду\n• Автовекторизація та вільне планування інструкцій\n• Сувора типізація та захист від помилок типів", size=10, fill=BG, stroke=LINE, sw=1))
    p.append(fitbox(ix + 15, iy + 205, iw - 30, 45,
                    "ВИСНОВОК: Оптимальний вибір для обчислень, SIMD та бітових операцій", size=10.5, fill="#f0fdf4", stroke=FIELD, color=FIELD, bold=True))

    ax, ay, aw, ah = 420, 70, 360, 270
    p.append(rect(ax, ay, aw, ah, fill=BG, stroke=POS, sw=1.5, rx=8))
    p.append(text(ax + aw/2, ay + 24, "Вбудований асемблер (Inline Asm)", size=12, color=POS, bold=True))
    p.append(fitbox(ax + 15, ay + 45, aw - 30, 45,
                    "asm (\"addps %1, %0\" : \"+x\"(a) : \"x\"(b));\nasm (\"bsr %1, %0\" : \"=r\"(r) : \"r\"(x));", size=10.5, fill="#fef2f2", stroke="#fecaca"))
    p.append(fitbox(ax + 15, ay + 100, aw - 30, 95,
                    "ОБМЕЖЕННЯ ОПТИМІЗАЦІЇ:\n• Непрозорий текст для оптимізатора IR\n• Неможливо згорнути константи всередині рядка\n• Жорсткі обмеження регістрів створюють зайві копіювання\n• Легко помилитися з clobbers та пошкодити стан процесора\n• Не переноситься між різними архітектурами", size=10, fill=BG, stroke=LINE, sw=1))
    p.append(fitbox(ax + 15, ay + 205, aw - 30, 45,
                    "ВИСНОВОК: Потрібен виключно для керування залізом (MSR, CR3, порти, бар'єри)", size=10, fill="#fff1f2", stroke=POS, color=POS, bold=True))

    render(os.path.join(OUT, "fig5-intrinsics-vs-inline-asm.svg"), W, H, *p)


if __name__ == "__main__":
    fig_compiler_pipeline_asm()
    fig_constraint_modifiers()
    fig_msvc_vs_gcc()
    fig_barrier_reordering()
    fig_intrinsics_vs_inline_asm()
    print("All figures generated successfully.")

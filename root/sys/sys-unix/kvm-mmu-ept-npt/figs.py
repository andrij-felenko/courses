# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE = "#eaf0fd"
GREEN = "#eaf6ef"
WARM = "#fff6e5"
RED = "#fdecea"
GREY = "#eceff1"
PURPLE = "#f3e8fd"


# ── 1. Чотири адресні простори: GVA -> GPA -> HVA -> HPA ─────────────────────
def fig_address_spaces_translation():
    W, H = 1050, 480
    p = []

    # Заголовок / фон
    p.append(rect(30, 30, 990, 420, fill="#fafbfc", stroke=MUTED, sw=1.0, rx=8))

    # Ліва половина: Гостьовий світ
    p.append(rect(50, 60, 430, 370, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(265, 95, "Гостьовий простір (Guest Domain)", size=15, bold=True, color=INK))

    # Права половина: Хостовий світ
    p.append(rect(570, 60, 430, 370, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(785, 95, "Хостовий простір і KVM (Host Domain)", size=15, bold=True, color=INK))

    # Блоки адрес
    # GVA
    f_gva, w1, h1 = textbox(265, 170, ["GVA (Guest Virtual Address)", "Віртуальна адреса процесу в гостьовій ОС"],
                            size=13, pad=12, fill=BLUE, stroke=LINE, min_w=360)
    p.append(f_gva)

    # GPA
    f_gpa, w2, h2 = textbox(265, 330, ["GPA (Guest Physical Address)", "«Фізична» адреса з погляду гостьового ядра"],
                            size=13, pad=12, fill=WARM, stroke=LINE, min_w=360)
    p.append(f_gpa)

    # HVA
    f_hva, w3, h3 = textbox(785, 170, ["HVA (Host Virtual Address)", "Віртуальна адреса буфера ОЗП у процесі QEMU/VMM"],
                            size=13, pad=12, fill=PURPLE, stroke=LINE, min_w=360)
    p.append(f_hva)

    # HPA
    f_hpa, w4, h4 = textbox(785, 330, ["HPA (Host Physical Address)", "Справжня фізична адреса в планках DRAM хоста"],
                            size=13, pad=12, fill=GREEN, stroke=LINE, min_w=360)
    p.append(f_hpa)

    # Стрілки та підписи переходів
    # GVA -> GPA
    p.append(arrow(160, 205, 160, 295, color=POS, sw=2.0))
    f_t1, wt1, ht1 = textbox(300, 250, ["Гостьові таблиці сторінок (CR3 гостя)"],
                             size=11, pad=5, fill="#ffffff", stroke=MUTED, sw=1.0)
    p.append(f_t1)

    # GPA -> HVA (memslots)
    p.append(arrow(450, 310, 595, 190, color=MUTED, sw=1.5))
    f_t2, wt2, ht2 = textbox(520, 220, ["mmap / memslots", "userspace VMM"],
                             size=11, pad=5, fill="#ffffff", stroke=MUTED, sw=1.0)
    p.append(f_t2)

    # GPA -> HPA (EPT/NPT)
    p.append(arrow(450, 340, 595, 340, color=POS, sw=2.2))
    f_t3, wt3, ht3 = textbox(522, 385, ["Апаратне EPT / NPT", "(або KVM Shadow MMU)"],
                             size=11, pad=6, fill="#ffffff", stroke=POS, sw=1.2)
    p.append(f_t3)

    # HVA -> HPA
    p.append(arrow(680, 205, 680, 295, color=LINE, sw=1.5))
    f_t4, wt4, ht4 = textbox(820, 250, ["Таблиці сторінок ядра хоста"],
                             size=11, pad=5, fill="#ffffff", stroke=MUTED, sw=1.0)
    p.append(f_t4)

    render(os.path.join(IMG, 'address-spaces-translation.svg'), W, H, *p,
           title="Чотири рівні адрес і зв'язки між ними")


# ── 2. Тіньові таблиці сторінок (Shadow Page Tables) ──────────────────────────
def fig_shadow_page_tables():
    W, H = 1100, 560
    p = []

    p.append(rect(30, 30, 1040, 500, fill="#fafbfc", stroke=MUTED, sw=1.0, rx=8))

    # Гостьовий світ зверху
    p.append(rect(50, 55, 470, 450, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(285, 85, "Гостьова ОС (Емуляція / Read-Only)", size=14, bold=True))

    # Справжнє залізо і KVM знизу/праворуч
    p.append(rect(560, 55, 490, 450, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(805, 85, "KVM і фізичний MMU процесора", size=14, bold=True))

    # Гостьовий CR3 та таблиці
    f1, _, _ = textbox(285, 140, ["Віртуальний CR3 гостя", "Вказує на GPA таблиць гостя"],
                       size=12, pad=10, fill=WARM, stroke=LINE, min_w=380)
    p.append(f1)

    f2, _, _ = textbox(285, 260, ["Гостьові таблиці сторінок (GPT)",
                                  "GVA ───(відображає)───> GPA",
                                  "⚠️ Позначені KVM як Read-Only в SPT"],
                       size=12, pad=10, fill=RED, stroke=POS, min_w=380)
    p.append(f2)
    p.append(arrow(285, 175, 285, 215, color=LINE, sw=1.5))

    # Спроба запису гостем
    f_wr, _, _ = textbox(285, 410, ["Гостьовий потік пише в GPT",
                                   "(наприклад, fork / mmap / alloc)",
                                   "❌ Спроба запису викликає #PF / VM-exit"],
                         size=12, pad=10, fill=RED, stroke=POS, min_w=380)
    p.append(f_wr)
    p.append(arrow(285, 315, 285, 360, color=POS, sw=1.8))

    # Справжній апаратний CR3 та тіньові таблиці
    f3, _, _ = textbox(805, 140, ["Фізичний регістр CR3 процесора", "Вказує на HPA тіньової таблиці KVM"],
                       size=12, pad=10, fill=GREEN, stroke=LINE, min_w=400)
    p.append(f3)

    f4, _, _ = textbox(805, 260, ["Тіньова таблиця KVM (SPT)",
                                  "GVA ───(пряме зшивання)───> HPA",
                                  "Завантажується напряму в апаратний MMU"],
                       size=12, pad=10, fill=BLUE, stroke=LINE, min_w=400)
    p.append(f4)
    p.append(arrow(805, 175, 805, 215, color=LINE, sw=1.5))

    # Обробник пастки KVM
    f5, _, _ = textbox(805, 410, ["Обробник перехоплення KVM (VM-exit)",
                                  "1. Емулює інструкцію запису гостя",
                                  "2. Синхронізує тіньовий запис SPT (GVA->HPA)",
                                  "3. Повертає виконання у vCPU"],
                       size=12, pad=10, fill=WARM, stroke=LINE, min_w=400)
    p.append(f5)

    # Стрілка перехоплення
    p.append(arrow(485, 410, 595, 410, color=POS, sw=2.2))
    p.append(arrow(805, 350, 805, 315, color=FIELD, sw=1.8))

    render(os.path.join(IMG, 'shadow-page-tables.svg'), W, H, *p,
           title="Принцип роботи тіньових таблиць сторінок")


# ── 3. Двовимірний обхід таблиць сторінок (2D Page Walk) ──────────────────────
def fig_two_dimensional_paging_walk():
    W, H = 1150, 680
    p = []

    p.append(rect(20, 20, 1110, 640, fill="#fafbfc", stroke=MUTED, sw=1.0, rx=8))

    # Гостьовий рівень (зліва направо)
    g_x = [140, 390, 640, 890]
    levels = ["1. PML4 гостя", "2. PDPT гостя", "3. PD гостя", "4. PT гостя"]

    # Зверху блок vCPU
    f_vcpu, _, _ = textbox(515, 60, ["vCPU: Доступ до пам'яті за адресою GVA",
                                     "CR3 гостя містить GPA таблиці PML4"],
                           size=13, pad=10, fill=BLUE, stroke=LINE, min_w=450)
    p.append(f_vcpu)

    for i in range(4):
        # Гостьовий крок
        fg, _, _ = textbox(g_x[i], 160, [levels[i], "Адреса: GPA", "Повертає наступний GPA"],
                           size=12, pad=8, fill=WARM, stroke=LINE, min_w=200)
        p.append(fg)

        # Стовпчик трансляції EPT під кожним рівнем
        p.append(arrow(g_x[i], 200, g_x[i], 245, color=POS, sw=1.5))

        f_ept, _, _ = textbox(g_x[i], 390,
                              ["EPT трансляція GPA → HPA",
                               "4 звернення до DRAM:",
                               "• EPT PML4 (1)",
                               "• EPT PDPT (2)",
                               "• EPT PD   (3)",
                               "• EPT PT   (4)",
                               "─────────────────",
                               "+ 1 читання запису",
                               "= 5 звернень до DRAM"],
                              size=11, pad=8, fill=GREEN, stroke=LINE, min_w=200)
        p.append(f_ept)

        # Стрілка до наступного гостьового рівня
        if i < 3:
            p.append(arrow(g_x[i] + 105, 160, g_x[i+1] - 105, 160, color=LINE, sw=1.8))

    # Фінальний крок: читання даних
    p.append(arrow(890 + 105, 160, 1050, 160, color=LINE, sw=1.8))
    f_fin, _, _ = textbox(1050, 260, ["Фінальний GPA даних",
                                      "Трансляція через EPT:",
                                      "4 рівні EPT",
                                      "+ 1 доступ до байтів",
                                      "──────────────────",
                                      "= 4 звернення до EPT"],
                          size=11, pad=8, fill=PURPLE, stroke=LINE, min_w=160)
    p.append(f_fin)

    # Підсумок внизу
    f_sum, _, _ = textbox(575, 590,
                          ["Підсумок 2D Page Walk (4-рівневий гість + 4-рівневий EPT хоста):",
                           "Формула: N = (n + 1) · (m + 1) − 1 = (4 + 1) · (4 + 1) − 1 = 24 звернення до DRAM на один промах TLB!",
                           "4 кроки гостя × (4 рівні EPT + 1 читання) + 4 рівні EPT для фінальної сторінки = 4 × 5 + 4 = 24"],
                          size=13, pad=12, fill=RED, stroke=POS, sw=1.5, min_w=950)
    p.append(f_sum)

    render(os.path.join(IMG, 'two-dimensional-paging-walk.svg'), W, H, *p,
           title="Двовимірний обхід таблиць сторінок: 24 звернення до пам'яті")


# ── 4. EPT Violation проти EPT Misconfiguration ──────────────────────────────
def fig_ept_violation_vs_misconfig():
    W, H = 1080, 520
    p = []

    p.append(rect(25, 25, 1030, 470, fill="#fafbfc", stroke=MUTED, sw=1.0, rx=8))

    # Вихідна подія
    f_root, _, _ = textbox(540, 70, ["Апаратний MMU виконує трансляцію через EPT",
                                     "Зустрічає проблему з записом SPTE (EPT Entry)"],
                           size=13, pad=10, fill=GREY, stroke=LINE, min_w=500)
    p.append(f_root)

    # Розгалуження
    p.append(arrow(400, 105, 290, 165, color=POS, sw=2.0))
    p.append(arrow(680, 105, 790, 165, color=POS, sw=2.0))

    # Ліва гілка: EPT Violation
    f_viol_h, _, _ = textbox(290, 195, ["EPT Violation (код виходу 48)",
                                        "Аналог звичайного #PF у просторі EPT"],
                             size=13, pad=10, fill=WARM, stroke=LINE, bold=True, min_w=420)
    p.append(f_viol_h)

    f_viol_b, _, _ = textbox(290, 330,
                             ["Причини:",
                              "• Запис відсутній (P = 0): сторінку ще не виділено",
                              "• Порушення прав: спроба запису при R/W = Read-Only",
                              "  (наприклад, Dirty Logging або CoW)",
                              "• Спроба виконання при X = 0",
                              "──────────────────────────────────────────────",
                              "Обробка KVM:",
                              "• Виділяє сторінку HPA або оновлює біт брудності",
                              "• Нормальна штатна робота гіпервізора"],
                             size=11, pad=10, fill=GREEN, stroke=LINE, min_w=420)
    p.append(f_viol_b)

    # Права гілка: EPT Misconfiguration
    f_misc_h, _, _ = textbox(790, 195, ["EPT Misconfiguration (код виходу 49)",
                                        "Неприпустимий формат запису в EPT"],
                             size=13, pad=10, fill=RED, stroke=POS, bold=True, min_w=420)
    p.append(f_misc_h)

    f_misc_b, _, _ = textbox(790, 330,
                             ["Причини:",
                              "• Встановлено зарезервовані біти (Reserved Bits)",
                              "• Неприпустимий тип пам'яті (Memory Type)",
                              "• Біти прав мають неприпустиму комбінацію",
                              "  (наприклад, W=1, але R=0 на старому залізі)",
                              "──────────────────────────────────────────────",
                              "Обробка KVM:",
                              "• Швидка емуляція MMIO (KVM Fast MMIO)",
                              "• АБО фатальна помилка ядра гіпервізора"],
                             size=11, pad=10, fill=PURPLE, stroke=LINE, min_w=420)
    p.append(f_misc_b)

    render(os.path.join(IMG, 'ept-violation-vs-misconfig.svg'), W, H, *p,
           title="Порівняння EPT Violation та EPT Misconfiguration")


# ── 5. Скорочення 2D Walk за допомогою Huge Pages ──────────────────────────────
def fig_huge_pages_2d_walk_reduction():
    W, H = 1100, 500
    p = []

    p.append(rect(25, 25, 1050, 450, fill="#fafbfc", stroke=MUTED, sw=1.0, rx=8))

    # Три стовпці конфігурацій
    cols_x = [195, 550, 905]

    # Стовпець 1: Базові 4KB + 4KB
    f_h1, _, _ = textbox(cols_x[0], 75, ["4 КіБ Гість + 4 КіБ Хост", "4 рівні гостя × 4 рівні EPT"],
                         size=13, pad=10, fill=RED, stroke=POS, bold=True, min_w=300)
    p.append(f_h1)

    f_b1, _, _ = textbox(cols_x[0], 255,
                         ["Обхід 4 рівнів гостя:",
                          "1. PML4e: 4 EPT + 1 = 5",
                          "2. PDPTe: 4 EPT + 1 = 5",
                          "3. PDe:   4 EPT + 1 = 5",
                          "4. PTe:   4 EPT + 1 = 5",
                          "Фінальна сторінка: 4 EPT",
                          "──────────────────────",
                          "Разом: 24 звернення",
                          "Максимальне навантаження",
                          "на шину пам'яті DRAM"],
                         size=12, pad=12, fill="#ffffff", stroke=LINE, min_w=300)
    p.append(f_b1)

    # Стовпець 2: 2MB Гість + 2MB Хост
    f_h2, _, _ = textbox(cols_x[1], 75, ["2 МіБ Гість + 2 МіБ Хост", "3 рівні гостя × 3 рівні EPT"],
                         size=13, pad=10, fill=WARM, stroke=LINE, bold=True, min_w=300)
    p.append(f_h2)

    f_b2, _, _ = textbox(cols_x[1], 255,
                         ["Обхід 3 рівнів гостя:",
                          "1. PML4e: 3 EPT + 1 = 4",
                          "2. PDPTe: 3 EPT + 1 = 4",
                          "3. PDe (2MB): 3 EPT + 1 = 4",
                          "Фінальна сторінка: 3 EPT",
                          "──────────────────────",
                          "Разом: 15 звернень",
                          "Економія: −37.5% звернень",
                          "В 512 разів менше",
                          "записів у TLB"],
                         size=12, pad=12, fill="#ffffff", stroke=LINE, min_w=300)
    p.append(f_b2)

    # Стовпець 3: 1GB Гість + 1GB Хост
    f_h3, _, _ = textbox(cols_x[2], 75, ["1 ГіБ Гість + 1 ГіБ Хост", "2 рівні гостя × 2 рівні EPT"],
                         size=13, pad=10, fill=GREEN, stroke=LINE, bold=True, min_w=300)
    p.append(f_h3)

    f_b3, _, _ = textbox(cols_x[2], 255,
                         ["Обхід 2 рівнів гостя:",
                          "1. PML4e: 2 EPT + 1 = 3",
                          "2. PDPTe (1GB): 2 EPT + 1 = 3",
                          "Фінальна сторінка: 2 EPT",
                          "──────────────────────",
                          "Разом: 8 звернень",
                          "Економія: −66.7% звернень",
                          "Мінімальна затримка",
                          "промаху TLB"],
                         size=12, pad=12, fill="#ffffff", stroke=LINE, min_w=300)
    p.append(f_b3)

    # Загальний рядок внизу
    p.append(text(550, 440, "Формула кількості звернень: N = (n + 1) · (m + 1) − 1", size=13, bold=True, color=INK))

    render(os.path.join(IMG, 'huge-pages-2d-walk-reduction.svg'), W, H, *p,
           title="Вплив розміру сторінок на кількість звернень при 2D Walk")


# ── 6. Архітектура KVM TDP MMU проти Legacy Shadow MMU ─────────────────────────
def fig_tdp_mmu_scalability():
    W, H = 1120, 540
    p = []

    p.append(rect(25, 25, 1070, 490, fill="#fafbfc", stroke=MUTED, sw=1.0, rx=8))

    # Лівий блок: Спадковий MMU
    p.append(rect(50, 60, 470, 430, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(285, 95, "Спадковий MMU (Legacy Shadow MMU)", size=14, bold=True))

    f_leg_lock, _, _ = textbox(285, 160, ["Глобальний mmu_lock (Spinlock)", "Єдине вузьке місце для всіх vCPU"],
                               size=12, pad=10, fill=RED, stroke=POS, min_w=400)
    p.append(f_leg_lock)

    f_leg_desc, _, _ = textbox(285, 310,
                               ["Особливості реалізації:",
                                "• Спільна кодова база для Shadow PT та EPT",
                                "• Зворотні відображення rmap (важкі списки)",
                                "• Будь-який page fault або dirty logging",
                                "  бере spinlock у монопольному режимі",
                                "• Проблема: при сотнях vCPU процесори",
                                "  проводять 90% часу в очікуванні замка",
                                "• Масштабування падає до нуля"],
                               size=11, pad=10, fill=WARM, stroke=LINE, min_w=400)
    p.append(f_leg_desc)

    # Правий блок: Сучасний TDP MMU
    p.append(rect(600, 60, 470, 430, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(835, 95, "Сучасний TDP MMU (Linux 5.10+)", size=14, bold=True))

    f_tdp_lock, _, _ = textbox(835, 160, ["Паралельний RCU + Атомарний CAS", "mmu_lock береться в режимі читання (Read Lock)"],
                               size=12, pad=10, fill=GREEN, stroke=LINE, min_w=400)
    p.append(f_tdp_lock)

    f_tdp_desc, _, _ = textbox(835, 310,
                               ["Особливості реалізації:",
                                "• Відокремлений рушій суто для EPT/NPT",
                                "• Обхід дерева таблиць без блокувань через RCU",
                                "• Модифікація записів через atomic cmpxchg",
                                "• Паралельна обробка page faults усіма vCPU",
                                "• Швидке встановлення Write Protection для",
                                "  живої міграції (Live Migration)",
                                "• Масштабується лінійно на 512+ vCPU та ТБ ОЗП"],
                               size=11, pad=10, fill=BLUE, stroke=LINE, min_w=400)
    p.append(f_tdp_desc)

    render(os.path.join(IMG, 'tdp-mmu-scalability.svg'), W, H, *p,
           title="Порівняння спадкового KVM MMU та масштабованого TDP MMU")


if __name__ == "__main__":
    fig_address_spaces_translation()
    fig_shadow_page_tables()
    fig_two_dimensional_paging_walk()
    fig_ept_violation_vs_misconfig()
    fig_huge_pages_2d_walk_reduction()
    fig_tdp_mmu_scalability()
    print("Всі фігури згенеровано успішно.")

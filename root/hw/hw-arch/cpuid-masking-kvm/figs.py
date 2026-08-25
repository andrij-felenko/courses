# -*- coding: utf-8 -*-
"""Фігури до статті «Маскування та емуляція CPUID у KVM». Вивід — ./img/*.svg."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

GREEN_FILL = "#eafaf1"
RED_FILL   = "#fdecea"
BLUE_FILL  = "#eaf0fd"
AMBER_FILL = "#fff7e6"
AMBER_STK  = "#c98a00"
PURPLE_FILL = "#f3e8fd"
PURPLE_STK  = "#8e44ad"


# ── Фігура 1: Перехоплення та емуляція CPUID у KVM ─────────────────────────
def fig_intercept_flow():
    W, H = 960, 520
    p = []

    p.append(text(480, 28, "Перехоплення та емуляція інструкції CPUID у гіпервізорі KVM", size=16, bold=True))

    # Верхня зона: Гість (VMX Non-Root)
    p.append(rect(30, 50, 900, 150, fill="#f9fafb", stroke=MUTED, sw=1.2))
    p.append(text(160, 75, "Гостьовий простір (VMX Non-Root)", size=13, bold=True, color=NEG))

    p.append(fitbox(50, 95, 230, 85, "Гостьова програма / ОС\nВиконує: CPUID (0F A2)\nEAX = Leaf, ECX = Sub-leaf", size=12, fill=BLUE_FILL, stroke=NEG, bold=True))

    p.append(fitbox(340, 95, 270, 85, "Апаратне перехоплення VT-x / AMD-V\nБезумовний вихід у гіпервізор\nEXIT_REASON_CPUID (причина 10)", size=12, fill=RED_FILL, stroke=POS, bold=True))

    p.append(fitbox(670, 95, 240, 85, "Відновлення роботи гостя\nОновлені регістри EAX, EBX, ECX, EDX\nRIP = RIP + 2 (пропуск 0F A2)", size=12, fill=GREEN_FILL, stroke=FIELD, bold=True))

    # Стрілки між верхніми блоками
    p.append(arrow(280, 137, 340, 137, color=POS, sw=2))
    p.append(arrow(610, 137, 670, 137, color=FIELD, sw=2))

    # Нижня зона: Хост і KVM (VMX Root)
    p.append(rect(30, 240, 900, 250, fill=FILL, stroke=LINE, sw=1.5))
    p.append(text(200, 265, "Простір ядра хоста: модуль KVM (VMX Root Ring 0)", size=13, bold=True, color=INK))

    p.append(fitbox(50, 285, 250, 95, "kvm_emulate_cpuid(vcpu)\nЗчитує гостьові RAX та RCX\nВизначає запитаний листок/підлисток", size=12, fill=AMBER_FILL, stroke=AMBER_STK, bold=True))

    p.append(fitbox(340, 285, 270, 95, "kvm_find_cpuid_entry(vcpu, leaf, idx)\nПошук у масиві kvm_cpuid_entry2\n(або кешованих покажчиках vcpu)", size=12, fill=PURPLE_FILL, stroke=PURPLE_STK, bold=True))

    p.append(fitbox(650, 285, 260, 95, "Запис змодельованих значень\nkvm_rax_write, rbx, rcx, rdx\nkvm_skip_emulated_instruction", size=12, fill=GREEN_FILL, stroke=FIELD, bold=True))

    # Додатковий блок: таблиця vCPU CPUID
    p.append(fitbox(200, 405, 560, 65, "Конфігурація vCPU (завантажена VMM через ioctl KVM_SET_CPUID2):\nЛистки 0x0..0x23 (базові), 0x40000000..0x40000001 (PV), 0x80000000..0x80000028 (AMD/Ext)", size=11.5, fill=BG, stroke=MUTED))

    # Міжрівневі стрілки (VM-Exit та VM-Entry)
    p.append(arrow(475, 180, 475, 235, color=POS, sw=2.2))
    p.append(text(535, 212, "VM-Exit", size=12, bold=True, color=POS))

    p.append(arrow(175, 285, 175, 185, color=NEG, sw=1.8))
    p.append(arrow(780, 285, 780, 185, color=FIELD, sw=2.2))
    p.append(text(835, 212, "VM-Entry", size=12, bold=True, color=FIELD))

    # Внутрішні стрілки KVM
    p.append(arrow(300, 332, 340, 332, color=INK, sw=1.8))
    p.append(arrow(610, 332, 650, 332, color=INK, sw=1.8))
    p.append(arrow(475, 380, 475, 405, color=MUTED, sw=1.5))

    render(os.path.join(IMG, "kvm-cpuid-intercept-flow.svg"), W, H, *p)


# ── Фігура 2: Ієрархія фільтрації та маскування CPUID ────────────────────────
def fig_masking_hierarchy():
    W, H = 960, 480
    p = []

    p.append(text(480, 26, "Чотирирівневий конвеєр формування CPUID для віртуальної машини", size=16, bold=True))

    # Рівень 1: Хостовий кремній
    p.append(fitbox(40, 60, 200, 100, "1. Фізичний кремній хоста\nАпаратні можливості CPU\n(Intel Core / AMD EPYC)\nРеальні тригери та мікрокод", size=11.5, fill=AMBER_FILL, stroke=AMBER_STK, bold=True))

    # Рівень 2: Ядро KVM
    p.append(fitbox(275, 60, 210, 100, "2. Ядро Linux (KVM)\nKVM_GET_SUPPORTED_CPUID\nKVM_GET_EMULATED_CPUID\nФільтрація небезпечних бітів", size=11.5, fill=BLUE_FILL, stroke=NEG, bold=True))

    # Рівень 3: Користувацький VMM
    p.append(fitbox(520, 60, 210, 100, "3. Простір VMM (QEMU/Cloud)\nВибір моделі (-cpu Haswell)\nМаскування розширень\nСинтез PV-листків (0x40000000)", size=11.5, fill=PURPLE_FILL, stroke=PURPLE_STK, bold=True))

    # Рівень 4: Активний vCPU
    p.append(fitbox(765, 60, 160, 100, "4. Активний vCPU\nKVM_SET_CPUID2\nІзольований паспорт\nСтабільний для міграції", size=11.5, fill=GREEN_FILL, stroke=FIELD, bold=True))

    # Стрілки верхнього конвеєра
    p.append(arrow(240, 110, 275, 110, color=AMBER_STK, sw=2))
    p.append(arrow(485, 110, 520, 110, color=NEG, sw=2))
    p.append(arrow(730, 110, 765, 110, color=PURPLE_STK, sw=2))

    # Нижня частина: деталізація операцій маскування
    p.append(rect(40, 190, 885, 260, fill="#f8fafc", stroke=MUTED, sw=1.2))
    p.append(text(480, 215, "Трансформація бітових прапорців у просторі VMM перед завантаженням у KVM", size=13, bold=True, color=INK))

    p.append(fitbox(60, 240, 260, 95, "Базова модель процесора\nНаприклад: x86-64-v3 / Haswell\nФіксований набір інструкцій\n(AVX2, FMA, BMI2, SSE4.2)", size=11.5, fill=BLUE_FILL, stroke=NEG))

    p.append(fitbox(350, 240, 260, 95, "Операція маскування (Політика):\nTarget = (Host & Model) | PV_Bits\nВимикання: AVX-512, AMX, MPX\nПриховування топології сокетів", size=11.5, fill=AMBER_FILL, stroke=AMBER_STK, bold=True))

    p.append(fitbox(640, 240, 265, 95, "Спеціальні розширення безпеки:\nСинтетичні прапорці захисту\nIBRS, IBPB, SSBD, ARCH_CAPS\nІмунітет проти Spectre/Meltdown", size=11.5, fill=GREEN_FILL, stroke=FIELD))

    # Пояснювальний підсумок знизу
    p.append(fitbox(60, 360, 845, 65, "Результат: Гість отримує однаковий паспорт CPUID незалежно від того, на якому сервері кластера запущено VM.\nЦе унеможливлює виникнення виключень #UD (Invalid Opcode) при живій міграції між різними поколіннями CPU.", size=11.5, fill=BG, stroke=FIELD, bold=True))

    render(os.path.join(IMG, "cpuid-masking-hierarchy.svg"), W, H, *p)


# ── Фігура 3: Жива міграція та узгодження базової моделі CPU ─────────────────
def fig_live_migration():
    W, H = 960, 500
    p = []

    p.append(text(480, 28, "Сумісність CPUID при живій міграції віртуальних машин між різними вузлами", size=16, bold=True))

    # Ліва колонка: Хост A (Сучасний)
    p.append(rect(40, 60, 270, 380, fill="#f8fafc", stroke=MUTED, sw=1.2))
    p.append(text(175, 88, "Хост A: Новий сервер", size=13, bold=True, color=FIELD))
    p.append(fitbox(55, 110, 240, 85, "Апаратний CPU: Sapphire Rapids\nПідтримка: AVX-512, AMX,\nAVX2, FMA, BMI2, SSE4.2\n64 фізичних ядра", size=11.5, fill=GREEN_FILL, stroke=FIELD))

    p.append(fitbox(55, 215, 240, 100, "Маскування KVM / VMM:\nПрофіль: x86-64-v3 (Haswell)\nAVX-512 примусово приховано\nAMX вимкнено в Leaf 7", size=11.5, fill=AMBER_FILL, stroke=AMBER_STK, bold=True))

    p.append(fitbox(55, 335, 240, 85, "Стан гостя на Хості A:\nКод компілюється під v3\nВикористовує лише AVX2/FMA\nЖодних інструкцій AVX-512", size=11.5, fill=BLUE_FILL, stroke=NEG))

    # Права колонка: Хост B (Старіший)
    p.append(rect(650, 60, 270, 380, fill="#f8fafc", stroke=MUTED, sw=1.2))
    p.append(text(785, 88, "Хост B: Старіший сервер", size=13, bold=True, color=NEG))
    p.append(fitbox(665, 110, 240, 85, "Апаратний CPU: Haswell\nПідтримка: AVX2, FMA, BMI2,\nSSE4.2 (БЕЗ AVX-512, БЕЗ AMX)\n16 фізичних ядер", size=11.5, fill=BLUE_FILL, stroke=NEG))

    p.append(fitbox(665, 215, 240, 100, "Маскування KVM / VMM:\nПрофіль: x86-64-v3 (Haswell)\nІдентичний набір бітів\nПовний збіг таблиці CPUID", size=11.5, fill=AMBER_FILL, stroke=AMBER_STK, bold=True))

    p.append(fitbox(665, 335, 240, 85, "Стан гостя після міграції:\nВиконання продовжується без збоїв\nНемає спроб виконати AVX-512\nНуль виключень #UD", size=11.5, fill=GREEN_FILL, stroke=FIELD, bold=True))

    # Центральний канал міграції
    p.append(rect(340, 140, 280, 220, fill=FILL, stroke=LINE, sw=1.5))
    p.append(text(480, 170, "Жива міграція (Live Migration)", size=13, bold=True, color=INK))
    p.append(fitbox(355, 195, 250, 75, "Перенесення RAM та vCPU:\nРегістри RIP, RAX, RBX...\nСтан XSAVE / XCR0\nЗбережена таблиця CPUID", size=11.5, fill=BG, stroke=MUTED))

    p.append(fitbox(355, 285, 250, 60, "Критерій успіху:\nCPUID(A) == CPUID(B)\nКонтракт інструкцій збережено", size=11.5, fill=GREEN_FILL, stroke=FIELD, bold=True))

    # Стрілки міграції
    p.append(arrow(295, 250, 340, 250, color=FIELD, sw=2.5))
    p.append(arrow(620, 250, 665, 250, color=FIELD, sw=2.5))

    p.append(text(480, 465, "Без маскування: виконання коду AVX-512 на Хості B призвело б до паніки ядра #UD (Invalid Opcode)", size=12, bold=True, color=POS))

    render(os.path.join(IMG, "live-migration-cpu-baseline.svg"), W, H, *p)


if __name__ == "__main__":
    fig_intercept_flow()
    fig_masking_hierarchy()
    fig_live_migration()
    print("Усі фігури успішно згенеровано.")

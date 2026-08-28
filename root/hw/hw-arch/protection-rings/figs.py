# -*- coding: utf-8 -*-
"""Фігури для теми «Кільця захисту й рівні привілеїв»."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def _box(cx, cy, s, **kw):
    """textbox із центром (cx,cy); повертає (frag, (left,right,top,bottom))."""
    frag, w, h = textbox(cx, cy, s, **kw)
    return frag, (cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2)


def fig_rings():
    W, H = 900, 660
    cx, cy = 300, 340
    rc, r0, r3 = 72, 152, 232
    F = []
    # смуги (спершу зовнішня, щоб внутрішні перекрили)
    F.append(circle(cx, cy, r3, fill="#eaf0fd", stroke=LINE, sw=1.6))
    F.append(circle(cx, cy, r0, fill="#fff2df", stroke=LINE, sw=1.6))
    F.append(circle(cx, cy, rc, fill="#fdecea", stroke=LINE, sw=1.6))
    # підписи смуг — на вертикальній осі над центром (розведені по y)
    F.append(text(cx, cy - 200, "Застосунки", size=18, bold=True))
    F.append(text(cx, cy - 178, "кільце 3", size=13, color=MUTED))
    F.append(text(cx, cy - 118, "Ядро ОС", size=18, bold=True))
    F.append(text(cx, cy - 96, "кільце 0", size=13, color=MUTED))
    F.append(text(cx, cy - 6, "Гіпервізор, залізо", size=15, bold=True))
    F.append(text(cx, cy + 16, "кільце −1", size=13, color=MUTED))
    # ворота — зелена стрілка по діагоналі в порожній правий-нижній сектор
    th = math.radians(35)
    ct, st = math.cos(th), math.sin(th)
    p_out = (cx + 192 * ct, cy + 192 * st)   # у смузі застосунків
    p_in = (cx + 112 * ct, cy + 112 * st)    # у смузі ядра
    F.append(arrow(p_out[0], p_out[1], p_in[0], p_in[1], color=FIELD, sw=3.2))
    # підпис воріт — назовні по тій самій діагоналі, з пунктирним поводком
    lc = (cx + 322 * ct, cy + 322 * st)
    gate, gw, gh = textbox(lc[0], lc[1], "єдиний законний вхід —\nпастка (system call)",
                           size=14, color=FIELD, stroke=FIELD, fill="#eafaf0")
    F.append(line(p_out[0], p_out[1], lc[0] - gw / 2 + 8, lc[1] - gh / 2 + 6,
                  color=FIELD, sw=1.2, dash="4 3"))
    F.append(gate)
    render(os.path.join(IMG, 'rings.svg'), W, H, *F,
           title="Рівні привілею як вкладені кільця")


def fig_gate():
    W, H = 960, 520
    F = []
    # ── A. Законний запит послуги ──────────────────────────────
    yA = 150
    F.append(text(56, 96, "A. Законний запит послуги", size=14, bold=True, anchor="start"))
    b1, e1 = _box(120, yA, "Застосунок\n(кільце 3)", size=14, bold=True)
    b2, e2 = _box(440, yA, ["CPU: підняти рівень 3→0", "і стрибнути на", "фіксовану адресу ядра"],
                  size=13, fill="#eafaf0", stroke=FIELD)
    b3, e3 = _box(780, yA, ["Ядро ОС (кільце 0):", "обробник виклику"], size=13)
    F += [b1, b2, b3]
    F.append(arrow(e1[1], yA, e2[0], yA, color=FIELD, sw=2.4))
    F.append(text((e1[1] + e2[0]) / 2, yA - 12, "system call", size=12, color=FIELD, bold=True))
    F.append(arrow(e2[1], yA, e3[0], yA, color=FIELD, sw=2.4))
    # повернення — пунктирна дуга під рядком A
    yr = 250
    F.append(line(780, e3[3], 780, yr, color=MUTED, sw=1.4, dash="5 3"))
    F.append(line(120, e1[3], 120, yr, color=MUTED, sw=1.4, dash="5 3"))
    F.append(arrow(780, yr, 120, yr, color=MUTED, sw=1.6))
    F.append(text(450, yr - 9, "повернення, рівень 0→3", size=12, color=MUTED))
    # розділювач
    F.append(line(40, 300, W - 40, 300, color="#d0d0d0", sw=1.2, dash="2 5"))
    # ── B. Спроба зробити напряму ──────────────────────────────
    yB = 388
    F.append(text(56, 340, "B. Спроба зробити напряму", size=14, bold=True, anchor="start"))
    c1, f1 = _box(120, yB, "Застосунок\n(кільце 3)", size=14, bold=True)
    c2, f2 = _box(440, yB, ["CPU: рівень ≠ 0?", "команду відхилено"],
                  size=13, fill="#fdecea", stroke=POS, color=POS, bold=True)
    c3, f3 = _box(780, yB, ["Ядро ОС:", "обробник помилки"], size=13)
    F += [c1, c2, c3]
    F.append(arrow(f1[1], yB, f2[0], yB, color=POS, sw=2.4))
    F.append(text((f1[1] + f2[0]) / 2, yB - 12, "hlt (привілейована)", size=12, color=POS, bold=True))
    F.append(arrow(f2[1], yB, f3[0], yB, color=POS, sw=2.4))
    F.append(text((f2[1] + f3[0]) / 2, yB - 12, "пастка-помилка", size=12, color=POS, bold=True))
    F.append(text(W / 2, 476,
                  "Привілейовану команду так і не виконано — керування перехоплено на перевірці рівня.",
                  size=13))
    render(os.path.join(IMG, 'gate.svg'), W, H, *F,
           title="Дві дороги до привілейованих дій")


def fig_trap_roundtrip():
    """Шлях однієї відмови: hlt → #GP → ядро → обробник → siglongjmp."""
    W, H = 1020, 560
    F = []
    yA, yB = 140, 350

    a1, e1 = _box(170, yA, ["Ваш код, кільце 3:", "hlt"], size=13, bold=True)
    a2, e2 = _box(510, yA, ["Процесор: рівень ≠ 0 —", "команду відхилено, #GP(13)"],
                  size=13, fill="#fdecea", stroke=POS, color=POS)
    a3, e3 = _box(860, yA, ["Апаратна пастка:", "вектор 13 у таблиці"], size=13)
    F += [a1, a2, a3]
    F.append(arrow(e1[1], yA, e2[0], yA, color=POS, sw=2.4))
    F.append(arrow(e2[1], yA, e3[0], yA, color=POS, sw=2.4))

    # вертикальний перехід у кільце 0
    F.append(arrow(860, e3[3], 860, yB - 40, color=POS, sw=2.4))
    F.append(text(845, 250, "рівень 3 → 0", size=12, color=POS, anchor="end"))

    b3, f3 = _box(860, yB, ["Ядро: обробник #GP", "→ SIGSEGV процесові"], size=13)
    b2, f2 = _box(510, yB, ["Ядро кладе кадр сигналу", "на стек користувача", "й вертає в кільце 3"], size=13)
    b1, f1 = _box(170, yB, ["on_trap(): запам'ятати", "сигнал → siglongjmp"], size=13, bold=True)
    F += [b1, b2, b3]
    F.append(arrow(f3[0], yB, f2[1], yB, color=MUTED, sw=2.2))
    F.append(arrow(f2[0], yB, f1[1], yB, color=MUTED, sw=2.2))

    # виноска про RIP — у вільній смузі між рядами
    nb, nbw, nbh = textbox(300, 242, ["RIP лишається НА команді hlt:", "просте return з обробника",
                                      "виконало б її знову — і знову"],
                           size=12, fill="#eafaf0", stroke=FIELD, color=FIELD)
    F.append(line(e2[0] + 14, e2[3], 340, 242 - nbh / 2, color=FIELD, sw=1.2, dash="4 3"))
    F.append(nb)

    F.append(text(W / 2, 502,
                  "Команду так і не виконано, програма живе далі — але дорога туди й назад "
                  "коштує кілька мікросекунд.", size=13))
    render(os.path.join(IMG, 'trap-roundtrip.svg'), W, H, *F,
           title="Шлях однієї відмови: від hlt до вашого обробника")


def fig_three_fates():
    """Одне й те саме #GP ядро може передати, підмінити або проковтнути."""
    W, H = 980, 460
    F = []
    F.append(fitbox(230, 60, 520, 54,
                    ["Процесор: привілейована команда в кільці 3", "→ #GP(13), команду не виконано"],
                    size=14, fill="#fdecea", stroke=POS, color=POS, bold=True))

    cols = [
        (170, "Передати далі",
         ["ядро шле процесові SIGSEGV —", "програма бачить відмову", "hlt · rdmsr · mov %cr0"]),
        (490, "Підмінити результат",
         ["ядро емулює команду й вертає", "правдоподібне число", "smsw · sgdt · sidt під UMIP"]),
        (810, "Проковтнути",
         ["ядро вважає команду за", "порожню, як nop", "cli · sti після iopl(3)"]),
    ]
    for cx, head, body in cols:
        F.append(arrow(490, 118, cx, 186, color=POS, sw=2.0))
        F.append(fitbox(cx - 140, 190, 280, 46, [head], size=15, bold=True,
                        fill="#eaf0fd", stroke=NEG, color=NEG))
        F.append(fitbox(cx - 140, 248, 280, 80, body, size=13))

    F.append(text(W / 2, 388,
                  "Апаратна відмова однакова завжди — різниться тільки те, що з нею робить ядро.",
                  size=13))
    render(os.path.join(IMG, 'three-fates.svg'), W, H, *F,
           title="Одне #GP — три різні долі")


def fig_multics_rings():
    """Мапа восьми апаратних кілець Honeywell 6180 (вставка hist-rings-multics)."""
    W, H = 980, 560
    F = []
    F.append(text(96, 72, "кільце", size=13, color=MUTED))
    F.append(text(180, 72, "хто там жив", size=13, color=MUTED, anchor="start"))
    F.append(text(880, 68, "менше влади", size=13, color=MUTED))
    F.append(arrow(880, 84, 880, 520, color=MUTED, sw=2))

    rows = [
        ("0", "Ядро (hardcore supervisor): уся влада над машиною", "#fdecea", POS),
        ("1", "Менеджери захищених об'єктів: поштові сегменти, TCP/IP", "#fff2df", LINE),
        ("2", "Резерв під спільні служби самої системи", "#fff2df", LINE),
        ("3", "Служби майданчика: пошта, менеджер БД, дошка Forum", "#fff2df", LINE),
        ("4", "Звичайний користувач — сюди потрапляв ваш власний код", "#eaf0fd", NEG),
        ("5", "Обмежені підсистеми, писані самими користувачами", "#f4f6f8", LINE),
        ("6", "Дуже обмежений код: до воріт ядра не дотягнеться", "#f4f6f8", LINE),
        ("7", "Те саме, ще жорсткіше", "#f4f6f8", LINE),
    ]
    y0, step, rh = 92, 58, 42
    for i, (num, desc, fill, stroke) in enumerate(rows):
        y = y0 + i * step
        F.append(fitbox(60, y - rh / 2, 72, rh, num, size=20, bold=True,
                        fill=fill, stroke=stroke, sw=1.8))
        F.append(fitbox(160, y - rh / 2, 640, rh, desc, size=15,
                        fill=fill, stroke=stroke, sw=1.4))
    render(os.path.join(IMG, 'multics-rings.svg'), W, H, *F,
           title="Вісім кілець Multics і їхні мешканці")


def fig_ring_count():
    """Як спадало число рівнів привілею (вставка hist-rings-multics)."""
    W, H = 1000, 430
    F = []
    F.append(arrow(70, 240, 950, 240, color=MUTED, sw=2))
    F.append(text(70, 228, "час", size=12, color=MUTED, anchor="start"))

    stations = [
        (140, "GE-645\n1967", "64", "у програмі", FILL, MUTED),
        (380, "Honeywell 6180\n1973", "8", "у залізі", "#fff2df", LINE),
        (620, "Intel 80286\n1982", "4", "у залізі", "#eaf0fd", NEG),
        (860, "Linux · Windows · macOS\nсьогодні", "2", "в ужитку в ОС", "#eafaf0", FIELD),
    ]
    for x, cap, n, sub, fill, stroke in stations:
        box, bw, bh = textbox(x, 105, cap, size=14, bold=True)
        F.append(line(x, 105 + bh / 2, x, 269, color=MUTED, sw=1.4, dash="4 3"))
        F.append(box)
        F.append(circle(x, 305, 36, fill=fill, stroke=stroke, sw=2.2))
        F.append(text(x, 316, n, size=30, bold=True, color=INK))
        F.append(text(x, 372, sub, size=13, color=MUTED))
    F.append(text(W / 2, 410,
                  "Кожне врізання — плата за біти в дескрипторах і швидкість перевірки.",
                  size=13))
    render(os.path.join(IMG, 'ring-count.svg'), W, H, *F,
           title="Скільки рівнів привілею — від Multics до сьогодні")


def fig_cortex_m_modes():
    """Матриця режимів та рівнів привілеїв ARM Cortex-M."""
    W, H = 980, 580
    F = []
    
    # ── Заголовок колонок ─────────────────────────────────────
    F.append(text(280, 48, "Привілейований рівень (Privileged)", size=15, bold=True, color=POS))
    F.append(text(730, 48, "Непривілейований рівень (Unprivileged)", size=15, bold=True, color=NEG))
    
    # ── Верхній ряд: Handler Mode ──────────────────────────────
    F.append(text(50, 150, "Handler\nMode", size=15, bold=True, color=INK))
    F.append(text(50, 185, "(обробка\nвинятків)", size=12, color=MUTED))
    
    # Handler завжди привілейований
    b_h, e_h = _box(280, 160, ["Handler Mode (Privileged)", "Виконує ISR / винятки", "Завжди стек MSP", "Повний доступ до SCB / NVIC / MPU"],
                    size=13, fill="#fdecea", stroke=POS, sw=1.8)
    F.append(b_h)
    
    # Непривілейованого Handler не існує в залізі
    b_hx, e_hx = _box(730, 160, ["Апаратно неможливо", "Handler Mode завжди", "виконується з повними", "привілеями"],
                      size=13, fill="#f4f6f8", stroke="#d0d0d0", color=MUTED)
    F.append(b_hx)
    
    # ── Нижній ряд: Thread Mode ────────────────────────────────
    F.append(text(50, 340, "Thread\nMode", size=15, bold=True, color=INK))
    F.append(text(50, 375, "(основний\nпотік задач)", size=12, color=MUTED))
    
    b_tp, e_tp = _box(280, 350, ["Privileged Thread Mode", "Ядро RTOS / ініціалізація", "Стек MSP або PSP", "CONTROL.nPRIV = 0"],
                      size=13, fill="#fff2df", stroke=LINE, sw=1.6)
    b_tu, e_tu = _box(730, 350, ["Unprivileged Thread Mode", "Користувацькі задачі RTOS", "Зазвичай стек PSP", "CONTROL.nPRIV = 1"],
                      size=13, fill="#eaf0fd", stroke=NEG, sw=1.8)
    F += [b_tp, b_tu]
    
    # ── Стрілки переходів ─────────────────────────────────────
    # Privileged Thread -> Unprivileged Thread (MSR CONTROL)
    F.append(arrow(e_tp[1], 335, e_tu[0], 335, color=NEG, sw=2.2))
    F.append(text((e_tp[1] + e_tu[0]) / 2, 322, "MSR CONTROL (nPRIV=1)", size=12, bold=True, color=NEG))
    
    # Unprivileged Thread -> Privileged Thread (ЗАБОРОНЕНО програмно)
    F.append(line(e_tu[0], 370, e_tp[1], 370, color=POS, sw=1.8, dash="4 3"))
    F.append(text((e_tp[1] + e_tu[0]) / 2, 385, "Прямий запис у CONTROL проігноровано!", size=11, bold=True, color=POS))
    
    # Thread -> Handler (SVC / Interrupt)
    F.append(arrow(680, e_tu[2], 370, e_h[3] - 10, color=FIELD, sw=2.2))
    F.append(text(540, 240, "Виклик SVC / Переривання (IRQs)", size=12, bold=True, color=FIELD))
    
    # Handler -> Thread (EXC_RETURN)
    F.append(arrow(240, e_h[3], 240, e_tp[2], color=MUTED, sw=2.0))
    F.append(text(210, 255, "EXC_RETURN", size=11, color=MUTED, anchor="end"))
    
    # ── Регістр CONTROL (панель внизу) ─────────────────────────
    F.append(rect(120, 460, 740, 90, fill="#f9fbfd", stroke=LINE, sw=1.4, rx=6))
    F.append(text(490, 482, "Системний регістр процесора CONTROL", size=14, bold=True))
    F.append(text(240, 515, "Біт 0: nPRIV (0 = Privileged, 1 = Unprivileged)", size=12, color=INK))
    F.append(text(580, 515, "Біт 1: SPSEL (0 = MSP, 1 = PSP)", size=12, color=INK))
    F.append(text(490, 538, "Біт 2: FPCA (активність контексту апаратного FPU)", size=11, color=MUTED))
    
    render(os.path.join(IMG, 'cortex-m-modes.svg'), W, H, *F,
           title="Модель привілеїв ARM Cortex-M")


def fig_armv8_el_trustzone():
    """Рівні винятків ARMv8-A EL0-EL3 та домени безпеки TrustZone."""
    W, H = 1020, 620
    F = []
    
    # Колонки доменів безпеки
    F.append(text(300, 40, "Non-Secure World (Normal)", size=15, bold=True, color=NEG))
    F.append(text(720, 40, "Secure World (TrustZone)", size=15, bold=True, color=POS))
    
    # EL0 (Applications)
    y0 = 100
    F.append(fitbox(60, y0, 900, 60, "", fill="#f4f6f8", stroke="#d0d0d0", sw=1.0))
    F.append(text(100, y0 + 35, "EL0", size=18, bold=True, color=INK))
    F.append(fitbox(180, y0 + 10, 240, 40, "Звичайні застосунки (Apps)", size=13, fill="#eaf0fd", stroke=NEG))
    F.append(fitbox(600, y0 + 10, 240, 40, "Довірені застосунки (TA)", size=13, fill="#fdecea", stroke=POS))
    
    # EL1 (OS Kernel)
    y1 = 200
    F.append(fitbox(60, y1, 900, 60, "", fill="#f4f6f8", stroke="#d0d0d0", sw=1.0))
    F.append(text(100, y1 + 35, "EL1", size=18, bold=True, color=INK))
    F.append(fitbox(180, y1 + 10, 240, 40, "Rich OS Kernel (Linux / Win)", size=13, fill="#fff2df", stroke=LINE))
    F.append(fitbox(600, y1 + 10, 240, 40, "Secure OS (OP-TEE / Trusty)", size=13, fill="#fdecea", stroke=POS))
    
    # EL2 (Hypervisor)
    y2 = 300
    F.append(fitbox(60, y2, 900, 60, "", fill="#f4f6f8", stroke="#d0d0d0", sw=1.0))
    F.append(text(100, y2 + 35, "EL2", size=18, bold=True, color=INK))
    F.append(fitbox(180, y2 + 10, 240, 40, "Hypervisor (KVM / Xen)", size=13, fill="#eafaf0", stroke=FIELD))
    F.append(fitbox(600, y2 + 10, 240, 40, "Secure EL2 (Virtualization)", size=13, fill="#fff2df", stroke=LINE))
    
    # EL3 (Secure Monitor)
    y3 = 410
    F.append(fitbox(60, y3, 900, 74, "", fill="#fdecea", stroke=POS, sw=2.0))
    F.append(text(100, y3 + 42, "EL3", size=20, bold=True, color=POS))
    F.append(text(510, y3 + 28, "Secure Monitor & Firmware (TF-A / Root of Trust)", size=15, bold=True, color=POS))
    F.append(text(510, y3 + 52, "Керує SCR_EL3, перемикає контексти світів, маршрутизує переривання SMC/FIQ", size=12, color=INK))
    
    # Інструкції переходів (стрілки збоку)
    # EL0 -> EL1: SVC
    F.append(arrow(300, y0 + 50, 300, y1 + 10, color=FIELD, sw=2.0))
    F.append(text(340, 180, "SVC (Syscall)", size=11, bold=True, color=FIELD))
    
    # EL1 -> EL2: HVC
    F.append(arrow(300, y1 + 50, 300, y2 + 10, color=FIELD, sw=2.0))
    F.append(text(340, 280, "HVC (Hypercall)", size=11, bold=True, color=FIELD))
    
    # EL1/EL2 -> EL3: SMC
    F.append(arrow(430, y1 + 30, 480, y3 + 10, color=POS, sw=2.2))
    F.append(text(475, 370, "SMC (Secure Monitor Call)", size=12, bold=True, color=POS))
    
    # Повернення ERET
    F.append(arrow(170, y3 + 10, 170, y1 + 50, color=MUTED, sw=1.8))
    F.append(text(155, 360, "ERET", size=11, color=MUTED, anchor="end"))
    
    # Виноска знизу
    F.append(text(W / 2, 530,
                  "Рівні винятків суворо ізольовані: перехід угору (підвищення прав) відбувається ТІЛЬКИ через виняток,",
                  size=13))
    F.append(text(W / 2, 555,
                  "а повернення вниз — інструкцією ERET з відновленням стану з SPSR_ELx та адреси з ELR_ELx.",
                  size=13))
    
    render(os.path.join(IMG, 'armv8-el-trustzone.svg'), W, H, *F,
           title="Рівні винятків ARMv8-A та домени TrustZone")


def fig_x86_privilege_check():
    """Перевірка прав x86 CPL, DPL, RPL та перемикання стеків через TSS."""
    W, H = 980, 580
    F = []
    
    # Ліва колонка: 4 Кільця
    cx, cy = 230, 240
    r3, r2, r1, r0 = 190, 145, 100, 55
    F.append(circle(cx, cy, r3, fill="#eaf0fd", stroke=LINE, sw=1.4))
    F.append(circle(cx, cy, r2, fill="#f4f6f8", stroke=LINE, sw=1.2))
    F.append(circle(cx, cy, r1, fill="#fff2df", stroke=LINE, sw=1.2))
    F.append(circle(cx, cy, r0, fill="#fdecea", stroke=POS, sw=1.8))
    
    F.append(text(cx, cy - 165, "Ring 3: User Space (CPL=3)", size=12, bold=True))
    F.append(text(cx, cy - 120, "Ring 2: OS Services", size=11, color=MUTED))
    F.append(text(cx, cy - 75, "Ring 1: Drivers", size=11, color=MUTED))
    F.append(text(cx, cy + 5, "Ring 0", size=14, bold=True, color=POS))
    F.append(text(cx, cy + 22, "Kernel", size=11, bold=True, color=POS))
    
    # Права колонка: Правила перевірки в кремнії
    rx = 480
    F.append(rect(rx, 50, 460, 400, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    F.append(text(rx + 230, 80, "Апаратна логіка перевірки привілеїв x86", size=14, bold=True))
    
    # CPL, DPL, RPL
    F.append(fitbox(rx + 20, 105, 420, 56,
                    ["CPL (CS[1:0]): поточний рівень виконання",
                     "DPL: рівень дескриптора (сегмента або шлюзу)",
                     "RPL (Selector[1:0]): запитаний рівень селектора"],
                    size=12, fill="#f9fbfd", stroke="#d0d0d0"))
    
    # Правило доступу до даних
    F.append(text(rx + 20, 185, "1. Доступ до сегмента даних:", size=13, bold=True, anchor="start"))
    b_data, _ = _box(rx + 230, 220,
                     ["max(CPL, RPL) ≤ DPL", "Користувач (CPL=3) не може прочитати дескриптор з DPL < 3"],
                     size=12, fill="#eafaf0", stroke=FIELD)
    F.append(b_data)
    
    # Правило переходу між кільцями
    F.append(text(rx + 20, 275, "2. Перехід у Кільце 0 (Syscall / Interrupt):", size=13, bold=True, anchor="start"))
    b_sys, _ = _box(rx + 230, 330,
                    ["SYSCALL: MSR_LSTAR → RIP, MSR_STAR → CS/SS",
                     "CPU автоматично встановлює CPL = 0",
                     "Апаратна зміна стека: читання RSP0 з TSS"],
                    size=12, fill="#fff2df", stroke=LINE)
    F.append(b_sys)
    
    # Виноска про захист стека
    F.append(text(rx + 20, 395, "3. Ізоляція стеків ядра:", size=13, bold=True, anchor="start"))
    F.append(text(rx + 20, 420, "Ядро не довіряє стеку Ring 3: стек підміняється на захищений RSP0.", size=12, color=POS, anchor="start"))
    
    # Підпис внизу
    F.append(text(W / 2, 510,
                  "Будь-яка спроба прямого переходу на кодовий сегмент вищого привілею без виклику шлюзу або syscall",
                  size=13))
    F.append(text(W / 2, 535,
                  "негайно генерує апаратне виключення General Protection Fault (#GP, вектор 13).",
                  size=13, bold=True, color=POS))
    
    render(os.path.join(IMG, 'x86-privilege-check.svg'), W, H, *F,
           title="Апаратна перевірка привілеїв x86")


def fig_mpu_task_isolation():
    """Апаратне розмежування пам'яті через MPU в RTOS."""
    W, H = 1000, 560
    F = []
    
    # Заголовки
    F.append(text(220, 45, "Фізичний адресний простір MCU", size=14, bold=True))
    F.append(text(540, 45, "Регіони MPU для Задачі (Task A)", size=14, bold=True))
    F.append(text(840, 45, "Реакція MPU на доступ", size=14, bold=True))
    
    # ── Блоки пам'яті ─────────────────────────────────────────
    # 1. Flash
    F.append(rect(80, 80, 280, 70, fill="#eaf0fd", stroke=NEG, sw=1.5))
    F.append(text(220, 108, "Flash Memory (0x08000000)", size=13, bold=True))
    F.append(text(220, 130, "Код ядра ОС та застосунку", size=11, color=MUTED))
    
    F.append(rect(400, 80, 280, 70, fill="#eafaf0", stroke=FIELD, sw=1.5))
    F.append(text(540, 108, "MPU Region 0 (Code Flash)", size=13, bold=True, color=FIELD))
    F.append(text(540, 130, "Privileged: RO/X | Unprivileged: RO/X", size=11, color=INK))
    
    F.append(arrow(690, 115, 780, 115, color=FIELD, sw=2.0))
    F.append(text(840, 115, "Дозволено (Fetch)", size=12, bold=True, color=FIELD))
    
    # 2. Task Private SRAM
    F.append(rect(80, 175, 280, 70, fill="#eafaf0", stroke=FIELD, sw=1.5))
    F.append(text(220, 203, "Task A RAM & Stack (PSP)", size=13, bold=True))
    F.append(text(220, 225, "0x20001000 — 0x20001FFF", size=11, color=MUTED))
    
    F.append(rect(400, 175, 280, 70, fill="#eafaf0", stroke=FIELD, sw=1.5))
    F.append(text(540, 203, "MPU Region 1 (Task Data)", size=13, bold=True, color=FIELD))
    F.append(text(540, 225, "Privileged: RW | Unprivileged: RW", size=11, color=INK))
    
    F.append(arrow(690, 210, 780, 210, color=FIELD, sw=2.0))
    F.append(text(840, 210, "Дозволено (RW)", size=12, bold=True, color=FIELD))
    
    # 3. Kernel RAM / Task B RAM (Захищена)
    F.append(rect(80, 270, 280, 70, fill="#fdecea", stroke=POS, sw=1.8))
    F.append(text(220, 298, "Kernel RAM & Task B Stack", size=13, bold=True, color=POS))
    F.append(text(220, 320, "0x20000000 (MSP) / 0x20002000", size=11, color=MUTED))
    
    F.append(rect(400, 270, 280, 70, fill="#fdecea", stroke=POS, sw=1.8))
    F.append(text(540, 298, "Поза регіонами Task A", size=13, bold=True, color=POS))
    F.append(text(540, 320, "Unprivileged: NO ACCESS", size=11, bold=True, color=POS))
    
    F.append(arrow(690, 305, 780, 305, color=POS, sw=2.4))
    F.append(text(840, 298, "Апаратна пастка:", size=12, bold=True, color=POS))
    F.append(text(840, 320, "MemManage Fault (#4)", size=11, bold=True, color=POS))
    
    # 4. System Control Space (SCB / NVIC / MPU registers)
    F.append(rect(80, 365, 280, 70, fill="#fff2df", stroke=LINE, sw=1.5))
    F.append(text(220, 393, "System Control Space (SCS)", size=13, bold=True))
    F.append(text(220, 415, "0xE000E000 (NVIC, MPU, SCB)", size=11, color=MUTED))
    
    F.append(rect(400, 365, 280, 70, fill="#fff2df", stroke=LINE, sw=1.5))
    F.append(text(540, 393, "Апаратний захист ядра", size=13, bold=True))
    F.append(text(540, 415, "Тільки Privileged доступ", size=11, color=POS))
    
    F.append(arrow(690, 400, 780, 400, color=POS, sw=2.4))
    F.append(text(840, 393, "Запис відхилено:", size=12, bold=True, color=POS))
    F.append(text(840, 415, "CFSR.MMFSR = DACCVIOL", size=11, color=POS))
    
    # Нижня плашка
    F.append(text(W / 2, 490,
                  "При кожному перемиканні контексту планувальник RTOS перепрограмує регістри MPU (RBAR, RLAR/RASR)",
                  size=13))
    F.append(text(W / 2, 515,
                  "під адресні межі поточної задачі, унеможливлюючи пошкодження чужої пам'яті.",
                  size=13))
    
    render(os.path.join(IMG, 'mpu-task-isolation.svg'), W, H, *F,
           title="Розмежування пам'яті через MPU в RTOS")


if __name__ == '__main__':
    fig_rings()
    fig_gate()
    fig_trap_roundtrip()
    fig_three_fates()
    fig_multics_rings()
    fig_ring_count()
    fig_cortex_m_modes()
    fig_armv8_el_trustzone()
    fig_x86_privilege_check()
    fig_mpu_task_isolation()
    print("OK:", os.listdir(IMG))


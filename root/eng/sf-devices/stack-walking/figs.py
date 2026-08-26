# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. fp-chain: Ланцюг покажчиків кадру на стеку ────────────────────────────
def fig_fp_chain():
    W, H = 840, 480
    p = []

    # Загальний фон і підписи напрямку пам'яті
    p.append(rect(20, 45, 800, 415, fill="#fafbfc", stroke="#d0d7de", sw=1.2, rx=8))

    # Стрілка росту стека
    p.append(line(55, 390, 55, 90, color=MUTED, sw=1.5, dash="4,4"))
    p.append(arrow(55, 110, 55, 80, color=MUTED, sw=1.8))
    p.append(text(45, 240, "Зростання стека (до менших адрес)", size=10, color=MUTED, anchor="middle"))

    # Три кадри стека: main, worker, leaf
    fx, fw = 170, 320
    
    # Секція: Кадр main()
    p.append(rect(fx, 340, fw, 70, fill="#f6f8fa", stroke="#656d76", sw=1.4, rx=4))
    p.append(rect(fx, 340, fw, 22, fill="#eaeef2", stroke="#656d76", sw=1.0, rx=4))
    p.append(text(fx + fw/2, 355, "Кадр 0: main()", size=11, color=INK, bold=True))
    p.append(text(fx + 15, 375, "Збережений RIP (повернення в __libc_start_main)", size=9.5, color=MUTED, anchor="start"))
    p.append(text(fx + 15, 395, "Збережений RBP (попередній кадр = 0x0)", size=9.5, color=NEG, anchor="start", bold=True))

    # Секція: Кадр worker()
    p.append(rect(fx, 210, fw, 95, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=4))
    p.append(rect(fx, 210, fw, 22, fill="#d0e1fd", stroke=NEG, sw=1.0, rx=4))
    p.append(text(fx + fw/2, 225, "Кадр 1: worker()", size=11, color=NEG, bold=True))
    p.append(text(fx + 15, 245, "Локальні змінні worker()", size=9.5, color=MUTED, anchor="start"))
    p.append(text(fx + 15, 268, "[RBP_1 + 8] = Збережений RIP (адреса в main)", size=9.5, color=POS, anchor="start", bold=True))
    p.append(text(fx + 15, 290, "[RBP_1 + 0] = Збережений RBP (покажчик на RBP_0)", size=9.5, color=NEG, anchor="start", bold=True))

    # Секція: Кадр leaf()
    p.append(rect(fx, 80, fw, 95, fill="#fdecea", stroke=POS, sw=1.6, rx=4))
    p.append(rect(fx, 80, fw, 22, fill="#fad1cc", stroke=POS, sw=1.0, rx=4))
    p.append(text(fx + fw/2, 95, "Кадр 2: leaf() (активна функція)", size=11, color=POS, bold=True))
    p.append(text(fx + 15, 115, "Локальні змінні leaf()", size=9.5, color=MUTED, anchor="start"))
    p.append(text(fx + 15, 138, "[RBP_2 + 8] = Збережений RIP (адреса у worker)", size=9.5, color=POS, anchor="start", bold=True))
    p.append(text(fx + 15, 160, "[RBP_2 + 0] = Збережений RBP (покажчик на RBP_1)", size=9.5, color=NEG, anchor="start", bold=True))

    # Регістр RBP
    p.append(rect(540, 145, 110, 36, fill="#fdecea", stroke=POS, sw=1.8, rx=6))
    p.append(text(595, 168, "RBP", size=13, color=POS, bold=True))
    p.append(arrow(540, 163, fx + fw + 4, 160, color=POS, sw=2.0))

    # Стрілка зв'язку RBP_2 -> RBP_1
    p.append(arrow(fx + 290, 165, fx + 290, 280, color=NEG, sw=2.2))
    p.append(circle(fx + 290, 165, 3.5, fill=NEG, stroke=NEG))

    # Стрілка зв'язку RBP_1 -> RBP_0
    p.append(arrow(fx + 290, 295, fx + 290, 385, color=NEG, sw=2.2))
    p.append(circle(fx + 290, 295, 3.5, fill=NEG, stroke=NEG))

    # Пояснювальний блок праворуч: алгоритм проходження
    px, py, pw, ph = 540, 220, 260, 190
    p.append(rect(px, py, pw, ph, fill="#ffffff", stroke="#d0d7de", sw=1.4, rx=6))
    p.append(text(px + pw/2, py + 22, "Алгоритм розмотування FP", size=11.5, color=INK, bold=True))
    
    steps = [
        "1. fp = %rbp (поточний кадр)",
        "2. return_ip = *(fp + 8)",
        "3. Зберегти return_ip у трейс",
        "4. fp = *fp (перехід до caller)",
        "5. Повторювати, доки fp != 0",
    ]
    for i, st in enumerate(steps):
        col = POS if "return_ip" in st else (NEG if "fp =" in st or "fp !=" in st else INK)
        p.append(text(px + 12, py + 52 + i * 26, st, size=10, color=col, anchor="start", bold=("=" in st)))

    render(os.path.join(OUT, "fp-chain.svg"), W, H, *p,
           title="Ланцюг покажчиків кадру: [RBP] веде до попереднього кадру, [RBP+8] — до адреси повернення")


# ── 2. dwarf-cfi-table: Таблиця DWARF CFI та обчислення CFA ───────────────────
def fig_dwarf_cfi_table():
    W, H = 860, 470
    p = []

    p.append(rect(20, 45, 820, 405, fill="#fafbfc", stroke="#d0d7de", sw=1.2, rx=8))

    # Верхній блок: Код асемблера
    ax, ay, aw, ah = 35, 65, 235, 210
    p.append(rect(ax, ay, aw, ah, fill="#ffffff", stroke="#656d76", sw=1.4, rx=6))
    p.append(rect(ax, ay, aw, 24, fill="#eaeef2", stroke="#656d76", sw=1.0, rx=6))
    p.append(text(ax + aw/2, ay + 17, "Машинні інструкції (PC)", size=11, color=INK, bold=True))
    
    asm_lines = [
        ("0x401000", "push %rbp"),
        ("0x401001", "mov  %rsp, %rbp"),
        ("0x401004", "push %r12"),
        ("0x401006", "sub  $0x20, %rsp"),
        ("0x40100a", "... тіло функції ..."),
        ("0x401030", "add  $0x20, %rsp"),
        ("0x401034", "pop  %r12"),
        ("0x401036", "pop  %rbp"),
        ("0x401037", "ret"),
    ]
    for i, (addr, ins) in enumerate(asm_lines):
        p.append(text(ax + 10, ay + 42 + i * 19, addr, size=9.5, color=MUTED, anchor="start"))
        p.append(text(ax + 85, ay + 42 + i * 19, ins, size=9.5, color=INK, anchor="start", bold=(ins.startswith("push") or ins.startswith("pop"))))

    # Правий блок: Віртуальна таблиця DWARF CFI
    tx, ty, tw, th = 285, 65, 540, 210
    p.append(rect(tx, ty, tw, th, fill="#ffffff", stroke=NEG, sw=1.5, rx=6))
    p.append(rect(tx, ty, tw, 24, fill="#d0e1fd", stroke=NEG, sw=1.0, rx=6))
    p.append(text(tx + tw/2, ty + 17, "Матриця DWARF CFI (Call Frame Information)", size=11.5, color=NEG, bold=True))

    headers = [("Діапазон PC", 110), ("Правило CFA", 120), ("Збережений RIP", 130), ("Регістри (RBP, R12)", 150)]
    hx = tx + 10
    for htitle, hw in headers:
        p.append(rect(hx, ty + 30, hw, 22, fill="#f6f8fa", stroke="#d0d7de", sw=1.0))
        p.append(text(hx + hw/2, ty + 45, htitle, size=9.5, color=INK, bold=True))
        hx += hw + 5

    rows_cfi = [
        ("0x401000", "RSP + 8", "cfa - 8", "RBP: не змінено"),
        ("0x401001", "RSP + 16", "cfa - 8", "RBP: [cfa - 16]"),
        ("0x401004", "RBP + 16", "cfa - 8", "RBP: [cfa - 16]"),
        ("0x401006", "RBP + 16", "cfa - 8", "R12: [cfa - 24]"),
        ("0x40100a", "RBP + 16", "cfa - 8", "R12: [cfa - 24]"),
        ("0x401036", "RSP + 8", "cfa - 8", "RBP: відновлено"),
    ]
    for r_idx, rdata in enumerate(rows_cfi):
        ry = ty + 56 + r_idx * 24
        hx = tx + 10
        for c_idx, val in enumerate(rdata):
            hw = headers[c_idx][1]
            p.append(rect(hx, ry, hw, 20, fill="#ffffff" if r_idx % 2 == 0 else "#f9fbfd", stroke="#eaeef2", sw=0.8))
            col = POS if c_idx == 1 else (NEG if c_idx == 2 else INK)
            p.append(text(hx + hw/2, ry + 14, val, size=9.5, color=col))
            hx += hw + 5

    # Нижній блок: Двійкові секції у ELF
    bx, by, bw, bh = 35, 295, 790, 135
    p.append(rect(bx, by, bw, bh, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    p.append(rect(bx, by, bw, 24, fill="#d5e8d4", stroke=FIELD, sw=1.0, rx=6))
    p.append(text(bx + bw/2, by + 17, "Двійкова організація секцій: .eh_frame_hdr та .eh_frame у ELF", size=11, color=FIELD, bold=True))

    p.append(rect(bx + 15, by + 38, 220, 82, fill="#fff8e1", stroke="#e67e22", sw=1.4, rx=4))
    p.append(text(bx + 125, by + 58, ".eh_frame_hdr", size=11, color="#e67e22", bold=True))
    p.append(text(bx + 125, by + 78, "Впорядкований двійковий масив", size=9.5, color=INK))
    p.append(text(bx + 125, by + 100, "Двійковий пошук FDE за O(log N)", size=9.5, color=POS, bold=True))

    p.append(arrow(bx + 240, by + 79, bx + 275, by + 79, color=POS, sw=2.0))

    p.append(rect(bx + 280, by + 38, 495, 82, fill="#eaf0fd", stroke=NEG, sw=1.4, rx=4))
    p.append(text(bx + 527, by + 58, ".eh_frame (Байт-код віртуальної машини DWARF CFI)", size=11, color=NEG, bold=True))
    
    p.append(rect(bx + 295, by + 70, 145, 42, fill="#ffffff", stroke=NEG, sw=1.0, rx=3))
    p.append(text(bx + 367, by + 87, "CIE", size=10, color=NEG, bold=True))
    p.append(text(bx + 367, by + 102, "Базове вирівнювання", size=9, color=MUTED))

    p.append(rect(bx + 455, by + 70, 150, 42, fill="#ffffff", stroke=NEG, sw=1.0, rx=3))
    p.append(text(bx + 530, by + 87, "FDE (Функція A)", size=10, color=NEG, bold=True))
    p.append(text(bx + 530, by + 102, "Інструкції DW_CFA_*", size=9, color=MUTED))

    p.append(rect(bx + 620, by + 70, 145, 42, fill="#ffffff", stroke=NEG, sw=1.0, rx=3))
    p.append(text(bx + 692, by + 87, "FDE (Функція B)", size=10, color=NEG, bold=True))
    p.append(text(bx + 692, by + 102, "Інструкції DW_CFA_*", size=9, color=MUTED))

    render(os.path.join(OUT, "dwarf-cfi-table.svg"), W, H, *p,
           title="Табличне розмотування DWARF CFI: матриця правил CFA та двійкові секції ELF")


# ── 3. cpp-two-phase-unwinding: Двофазне розмотування винятків C++ ─────────────
def fig_cpp_two_phase_unwinding():
    W, H = 860, 460
    p = []

    p.append(rect(20, 45, 820, 395, fill="#fafbfc", stroke="#d0d7de", sw=1.2, rx=8))

    # Стек викликів ліворуч
    sx, sy, sw, sh = 40, 70, 230, 350
    p.append(rect(sx, sy, sw, sh, fill="#ffffff", stroke="#656d76", sw=1.4, rx=6))
    p.append(rect(sx, sy, sw, 26, fill="#eaeef2", stroke="#656d76", sw=1.0, rx=6))
    p.append(text(sx + sw/2, sy + 18, "Стек під час throw Exception", size=11, color=INK, bold=True))

    frames = [
        ("Кадр 3: do_parse()", "Тут виконано throw", POS, "#fdecea"),
        ("Кадр 2: handle_msg()", "Має деструктор RAII socket", "#e67e22", "#fff8e1"),
        ("Кадр 1: server_run()", "Має блок catch(const Exception&)", FIELD, "#d5e8d4"),
        ("Кадр 0: main()", "Кореневий кадр потоку", MUTED, "#f6f8fa"),
    ]
    for i, (fname, fdesc, col, fill) in enumerate(frames):
        fy = sy + 40 + i * 74
        p.append(rect(sx + 10, fy, sw - 20, 62, fill=fill, stroke=col, sw=1.5, rx=4))
        p.append(text(sx + 20, fy + 24, fname, size=10.5, color=col, anchor="start", bold=True))
        p.append(text(sx + 20, fy + 46, fdesc, size=9.5, color=INK, anchor="start"))

    # Фаза 1: Пошук обробника (Search Phase)
    p1x, p1y, p1w, p1h = 300, 70, 245, 350
    p.append(rect(p1x, p1y, p1w, p1h, fill="#ffffff", stroke=NEG, sw=1.5, rx=6))
    p.append(rect(p1x, p1y, p1w, 26, fill="#d0e1fd", stroke=NEG, sw=1.0, rx=6))
    p.append(text(p1x + p1w/2, p1y + 18, "Фаза 1: Пошук (Search Phase)", size=11, color=NEG, bold=True))

    p1_steps = [
        ("Сканування кадрів знизу вгору", MUTED),
        ("Виклик Personality Routine", NEG),
        ("Перевірка таблиць LSDA / типів", INK),
        ("Деструктори НЕ викликаються!", POS),
        ("Якщо обробника немає:", MUTED),
        ("-> Негайний std::terminate()", POS),
        ("Стек лишається для Core Dump", FIELD),
    ]
    for i, (s_txt, s_col) in enumerate(p1_steps):
        p.append(text(p1x + 15, p1y + 55 + i * 40, s_txt, size=9.5, color=s_col, anchor="start", bold=(s_col == POS or s_col == FIELD)))

    # Стрілка пошуку
    p.append(arrow(p1x + 120, p1y + 280, p1x + 120, p1y + 315, color=NEG, sw=2.0))

    # Фаза 2: Очищення та виклики деструкторів (Cleanup Phase)
    p2x, p2y, p2w, p2h = 575, 70, 245, 350
    p.append(rect(p2x, p2y, p2w, p2h, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    p.append(rect(p2x, p2y, p2w, 26, fill="#d5e8d4", stroke=FIELD, sw=1.0, rx=6))
    p.append(text(p2x + p2w/2, p2y + 18, "Фаза 2: Очищення (Cleanup Phase)", size=11, color=FIELD, bold=True))

    p2_steps = [
        ("Повторний прохід до цільового кадру", MUTED),
        ("Стрибок у Landing Pad кадру 2", "#e67e22"),
        ("Виконання деструктора ~Socket()", "#e67e22"),
        ("Відновлення регістрів кадру 1", INK),
        ("Стрибок у блок catch { ... }", FIELD),
        ("Нормальне продовження коду", FIELD),
    ]
    for i, (s_txt, s_col) in enumerate(p2_steps):
        p.append(text(p2x + 15, p2y + 55 + i * 44, s_txt, size=9.5, color=s_col, anchor="start", bold=(s_col == FIELD or s_col == "#e67e22")))

    # Сполучні стрілки між фазами
    p.append(arrow(sx + sw, sy + 180, p1x - 5, sy + 180, color=NEG, sw=2.0))
    p.append(arrow(p1x + p1w, sy + 180, p2x - 5, sy + 180, color=FIELD, sw=2.0))

    render(os.path.join(OUT, "cpp-two-phase-unwinding.svg"), W, H, *p,
           title="Двофазне розмотування винятків C++: пошук обробника без деструкторів та наступне очищення")


# ── 4. unwinding-matrix-tradeoffs: Порівняння підходів розмотування ───────────
def fig_unwinding_matrix_tradeoffs():
    W, H = 860, 440
    p = []

    p.append(rect(20, 45, 820, 375, fill="#fafbfc", stroke="#d0d7de", sw=1.2, rx=8))

    cols = [
        (40, "Frame Pointer (RBP / FP)", POS, "#fdecea", [
            ("Накладні витрати коду", "1–3% CPU (мінус 1 регістр)"),
            ("Швидкість розмотування", "Надшвидка (<50 нс)"),
            ("Розмір двійкового коду", "Мінімальний (+0.5%)"),
            ("Робота в eBPF / Signal", "Безпечна (прості читання)"),
            ("Повнота відновлення", "Лише FP та Return IP"),
        ]),
        (305, "DWARF CFI (.eh_frame)", NEG, "#eaf0fd", [
            ("Накладні витрати коду", "0% (Zero-cost на виконання)"),
            ("Швидкість розмотування", "Повільна (інтерпретатор VM)"),
            ("Розмір двійкового коду", "+15–30% до розміру ELF"),
            ("Робота в eBPF / Signal", "Небезпечна (складний парсинг)"),
            ("Повнота відновлення", "Повне відновлення регістрів"),
        ]),
        (570, "SFrame (Simple Frame Format)", FIELD, "#d5e8d4", [
            ("Накладні витрати коду", "0% (не потребує RBP)"),
            ("Швидкість розмотування", "Дуже швидка (прямий масив)"),
            ("Розмір двійкового коду", "+2–4% до розміру ELF"),
            ("Робота в eBPF / Signal", "Ідеальна для ядра Linux"),
            ("Повнота відновлення", "Лише CFA, FP та Return IP"),
        ]),
    ]

    cw, ch = 250, 335
    for cx, title, col, fill, items in cols:
        p.append(rect(cx, 65, cw, ch, fill="#ffffff", stroke=col, sw=1.6, rx=6))
        p.append(rect(cx, 65, cw, 34, fill=fill, stroke=col, sw=1.0, rx=6))
        p.append(text(cx + cw/2, 87, title, size=11, color=col, bold=True))

        for idx, (param, val) in enumerate(items):
            iy = 115 + idx * 56
            p.append(rect(cx + 8, iy, cw - 16, 48, fill="#f8fafc", stroke="#eaeef2", sw=1.0, rx=4))
            p.append(text(cx + 14, iy + 17, param, size=9.0, color=MUTED, anchor="start"))
            vcol = POS if "1–3%" in val or "Повільна" in val or "Небезпечна" in val else (FIELD if "Надшвидка" in val or "0%" in val or "Ідеальна" in val or "Дуже швидка" in val else INK)
            p.append(text(cx + 14, iy + 36, val, size=9.5, color=vcol, anchor="start", bold=True))

    render(os.path.join(OUT, "unwinding-matrix-tradeoffs.svg"), W, H, *p,
           title="Порівняння методів розмотування: Frame Pointer, DWARF CFI та SFrame")


if __name__ == "__main__":
    fig_fp_chain()
    fig_dwarf_cfi_table()
    fig_cpp_two_phase_unwinding()
    fig_unwinding_matrix_tradeoffs()
    print("All figures generated successfully.")

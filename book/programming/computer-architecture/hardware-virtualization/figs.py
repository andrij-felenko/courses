# -*- coding: utf-8 -*-
"""Фігури до статті «Апаратна віртуалізація». Вивід — ./img/*.svg."""
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


# ── Фігура 1: два способи поставити гіпервізор нижче за гостя ────────────────
def fig_privilege():
    W, H = 940, 600
    p = []
    # підписи колонок
    p.append(text(235, 60, "Класична деривілегізація", size=15, bold=True))
    p.append(text(705, 60, "Апаратна (VT-x / AMD-V)", size=15, bold=True))
    # роздільник
    p.append(line(470, 74, 470, 410, color=MUTED, sw=1.2, dash="5,5"))

    # ── ліва модель ──
    p.append(fitbox(85, 85, 300, 54, "Застосунки гостя  ·  ring 3", size=14))
    p.append(fitbox(85, 180, 300, 54, "Ядро гостя  ·  ring 1  (знижений)", size=14))
    p.append(fitbox(85, 340, 300, 54, "Гіпервізор  ·  ring 0",
                    size=14, fill=GREEN_FILL, stroke=FIELD, bold=True))
    # пастка вниз
    p.append(arrow(360, 236, 360, 338, color=POS, sw=2.2))
    p.append(text(348, 292, "пастка", size=12, color=POS, anchor="end"))
    p.append(text(348, 308, "(trap)", size=12, color=POS, anchor="end"))
    note1, _, _ = textbox(235, 470,
        "Гостя виконують зниженим (ring 1).\n"
        "Привілейована команда падає пасткою\n"
        "вниз — гіпервізор її емулює.",
        size=12.5, color=MUTED, fill=BG, stroke=BG)
    p.append(note1)

    # ── права модель ──
    # контейнер non-root
    p.append(rect(555, 80, 300, 172, fill="#f9fbff", stroke=NEG, sw=1.6))
    p.append(text(705, 102, "NON-ROOT  ·  світ гостя", size=12.5, color=NEG, bold=True))
    p.append(fitbox(575, 116, 260, 44, "Застосунки  ·  ring 3", size=13))
    p.append(fitbox(575, 172, 260, 46, "Ядро гостя  ·  ring 0  (повний!)",
                    size=13, bold=True))
    # root
    p.append(fitbox(555, 340, 300, 60, "ROOT  ·  «ring −1»  ·  гіпервізор",
                    size=14, fill=GREEN_FILL, stroke=FIELD, bold=True))
    # exit / entry
    p.append(arrow(640, 256, 640, 338, color=POS, sw=2.2))
    p.append(text(628, 302, "VM exit", size=12, color=POS, anchor="end"))
    p.append(arrow(770, 338, 770, 256, color=NEG, sw=2.2))
    p.append(text(782, 302, "VM entry", size=12, color=NEG, anchor="start"))
    note2, _, _ = textbox(705, 470,
        "Гість працює на повному ring 0 у non-root.\n"
        "Лише налаштовані події дають VM exit\n"
        "у root-режим («ring −1»).",
        size=12.5, color=MUTED, fill=BG, stroke=BG)
    p.append(note2)

    render(os.path.join(IMG, "privilege-stack.svg"), W, H, *p,
           title="Два способи поставити гіпервізор нижче за гостя")


# ── Фігура 2: пульс віртуалізації — VM exit / VM entry ──────────────────────
def fig_cycle():
    W, H = 900, 480
    p = []
    # чотири стани
    p.append(fitbox(300, 76, 300, 58, "Гість виконує код · non-root\n(повна швидкість)", size=13.5))
    p.append(fitbox(590, 208, 290, 64, "VM EXIT\nзалізо зберігає стан гостя",
                    size=13.5, fill=RED_FILL, stroke=POS, bold=True))
    p.append(fitbox(280, 366, 340, 58, "Гіпервізор обробляє подію · root", size=13.5,
                    fill=GREEN_FILL, stroke=FIELD))
    p.append(fitbox(20, 208, 290, 64, "VM ENTRY\nзалізо відновлює стан",
                    size=13.5, fill=BLUE_FILL, stroke=NEG, bold=True))
    # центр — VMCS
    p.append(fitbox(375, 205, 150, 70, "VMCS /\nVMCB", size=14, bold=True,
                    fill="#fff7e6", stroke="#c98a00"))
    # кільце стрілок (за годинниковою)
    p.append(arrow(598, 130, 618, 206, color=INK, sw=2))          # T → R
    p.append(arrow(700, 274, 620, 366, color=INK, sw=2))          # R → B
    p.append(arrow(278, 388, 198, 274, color=INK, sw=2))          # B → L
    p.append(arrow(198, 206, 300, 128, color=INK, sw=2))          # L → T
    # звʼязок із VMCS
    p.append(line(525, 240, 588, 240, color="#c98a00", sw=1.4, dash="4,4"))
    p.append(text(556, 232, "зберегти", size=11, color="#8a6100"))
    p.append(line(312, 240, 375, 240, color="#c98a00", sw=1.4, dash="4,4"))
    p.append(text(343, 232, "відновити", size=11, color="#8a6100"))

    render(os.path.join(IMG, "vmexit-cycle.svg"), W, H, *p,
           title="Пульс віртуалізації: VM exit і VM entry")


# ── Фігура 3: двовимірний обхід сторінок (EPT / NPT) ────────────────────────
def fig_nested():
    W, H = 780, 640
    p = []
    cx = 230
    p.append(fitbox(80, 52, 300, 56, "GVA · гостьова віртуальна адреса", size=13.5))
    p.append(arrow(cx, 110, cx, 158, color=INK, sw=2))
    p.append(fitbox(80, 160, 300, 60, "Гостьові таблиці сторінок\n(керує гість)",
                    size=13.5))
    p.append(arrow(cx, 222, cx, 270, color=INK, sw=2))
    p.append(fitbox(80, 272, 300, 56, "GPA · гостьова фізична", size=13.5))
    p.append(arrow(cx, 330, cx, 378, color=INK, sw=2))
    p.append(fitbox(80, 380, 300, 60, "Таблиці хоста · EPT / NPT\n(керує гіпервізор)",
                    size=13.5, fill=BLUE_FILL, stroke=NEG))
    p.append(arrow(cx, 442, cx, 490, color=INK, sw=2))
    p.append(fitbox(80, 492, 300, 56, "HPA · справжня фізична (RAM)",
                    size=13.5, fill=GREEN_FILL, stroke=FIELD, bold=True))

    # бокова панель-пояснення
    note, _, _ = textbox(590, 300,
        "Двовимірний обхід\n"
        "\n"
        "Кожен доступ до гостьової\n"
        "таблиці — теж GPA →\n"
        "знову через таблиці хоста.\n"
        "\n"
        "4 рівні × 4 рівні →\n"
        "до 24 звернень до пам'яті\n"
        "на промах TLB.\n"
        "Готовий переклад кешує TLB.",
        size=12.5, color=INK, fill="#fbfbfb", stroke=MUTED, sw=1.2)
    p.append(note)

    render(os.path.join(IMG, "nested-paging.svg"), W, H, *p,
           title="Двовимірний обхід: таблиці гостя + таблиці хоста")


# ── Фігура 4 (вставка KVM): драбина дескрипторів ────────────────────────────
def fig_kvm_handles():
    W, H = 960, 620
    p = []
    sx = 290           # вісь спини
    bw = 300
    # рівень 1 — /dev/kvm
    p.append(fitbox(sx - bw / 2, 74, bw, 54, "/dev/kvm\nсистемний дескриптор", size=13.5))
    p.append(arrow(sx, 128, sx, 178, color=INK, sw=2))
    p.append(text(sx + 16, 160, "ioctl(KVM_CREATE_VM)", size=11.5, color=MUTED, anchor="start"))
    # рівень 2 — VM fd
    p.append(fitbox(sx - bw / 2, 180, bw, 54, "VM fd\nодна віртуальна машина", size=13.5, bold=True))
    # відгалуження вправо до буфера
    p.append(arrow(sx + bw / 2, 207, 638, 207, color=INK, sw=2))
    p.append(text(545, 198, "KVM_SET_USER_MEMORY_REGION", size=10.5, color=MUTED))
    p.append(fitbox(640, 180, 250, 54, "хостовий буфер (mmap)\n= пам'ять гостя",
                    size=12, fill=BLUE_FILL, stroke=NEG))
    # вниз до vCPU
    p.append(arrow(sx, 234, sx, 302, color=INK, sw=2))
    p.append(text(sx + 16, 272, "ioctl(KVM_CREATE_VCPU)", size=11.5, color=MUTED, anchor="start"))
    # рівень 3 — vCPU fd
    p.append(fitbox(sx - bw / 2, 304, bw, 54, "vCPU fd\nвіртуальний процесор", size=13.5, bold=True))
    p.append(arrow(sx, 358, sx, 426, color=INK, sw=2))
    p.append(text(sx + 16, 396, "mmap(vcpu fd)", size=11.5, color=MUTED, anchor="start"))
    # рівень 4 — kvm_run
    p.append(fitbox(sx - bw / 2, 428, bw, 58, "struct kvm_run\nспільна поштова скринька",
                    size=13.5, fill=GREEN_FILL, stroke=FIELD, bold=True))
    # бокова нотатка
    note, _, _ = textbox(710, 474,
        "ioctl(KVM_RUN) діє на vCPU fd.\n"
        "Після кожного виходу ядро лишає\n"
        "тут exit_reason і деталі —\n"
        "userspace читає їх прямо з mmap.",
        size=12, color=INK, fill=BG, stroke=MUTED, sw=1.2)
    p.append(note)
    render(os.path.join(IMG, "kvm-handles.svg"), W, H, *p,
           title="Драбина дескрипторів: від /dev/kvm до kvm_run")


# ── Фігура 5 (вставка KVM): пам'ять гостя і CS:IP ───────────────────────────
def fig_kvm_memory():
    W, H = 980, 560
    p = []
    # ── хост ──
    p.append(text(215, 56, "Хост · простір процесу", size=13.5, bold=True))
    p.append(rect(120, 74, 190, 400, fill=BG, stroke=LINE, sw=1.5))
    p.append(fitbox(120, 250, 190, 150, "буфер mmap\nвирівняний\nна 4 КіБ",
                    size=12.5, fill=BLUE_FILL, stroke=NEG, sw=1.8))
    p.append(text(112, 256, "userspace_addr", size=11, color=NEG, anchor="end"))
    p.append(circle(120, 250, 3.2, fill=NEG, stroke=NEG))
    # ── гість ──
    p.append(text(760, 56, "Гостьова фізична пам'ять", size=13.5, bold=True))
    p.append(rect(670, 74, 200, 400, fill=BG, stroke=LINE, sw=1.5))
    p.append(rect(670, 250, 200, 150, fill=GREEN_FILL, stroke=FIELD, sw=1.8))
    p.append(fitbox(670, 250, 200, 62, "ba f8 03 00 d8 …\n16-біт гість",
                    size=12, fill=GREEN_FILL, stroke=FIELD))
    p.append(mtext(662, 252, ["guest_phys_addr", "= 0x1000"],
                   size=11, color=FIELD, anchor="end"))
    p.append(circle(670, 250, 3.2, fill=FIELD, stroke=FIELD))
    # ── мапування ──
    p.append(arrow(310, 322, 668, 322, color=INK, sw=2))
    p.append(text(489, 312, "KVM_SET_USER_MEMORY_REGION", size=11, color=MUTED))
    # ── CS:IP ──
    csnote, _, _ = textbox(770, 452,
        "CS.base(0) + IP(0x1000)\n= лінійна 0x1000\n→ перша команда гостя",
        size=12, color=INK, fill=BG, stroke=FIELD, sw=1.3)
    p.append(csnote)
    p.append(arrow(760, 424, 715, 320, color=FIELD, sw=1.8))
    # ── нотатка про вирівнювання ──
    aln, _, _ = textbox(300, 516,
        "guest_phys_addr і memory_size — кратні 4 КіБ.\n"
        "mmap дає вирівняну пам'ять, malloc — ні.",
        size=11.5, color=MUTED, fill=BG, stroke=MUTED, sw=1)
    p.append(aln)
    render(os.path.join(IMG, "kvm-memory.svg"), W, H, *p,
           title="Пам'ять гостя: хостовий буфер, відображення й CS:IP")


# ── Фігура 6 (вставка math): сітка двовимірного обходу — звідки 24 ───────────
def fig_nested_grid():
    W, H = 940, 690
    p = []
    p.append(text(W / 2, 48, "повний промах TLB: 4 рівні в гостя × 4 в хоста",
                  size=13, color=MUTED))
    colw, colgap, x0 = 148, 6, 158
    rowh, rowgap, y0 = 82, 6, 104

    def cx_col(c): return x0 + c * (colw + colgap)
    def cy_row(r): return y0 + r * (rowh + rowgap)

    heads = [("gCR3", "→ gL4-табл."), ("з gL4", "→ gL3-табл."),
             ("з gL3", "→ gL2-табл."), ("з gL2", "→ gL1-табл."),
             ("з gL1", "→ дані")]
    for c, (a, b) in enumerate(heads):
        xc = cx_col(c) + colw / 2
        p.append(text(xc, 78, a, size=13, bold=True))
        p.append(text(xc, 95, b, size=11.5, color=MUTED))

    rowlab = ["hL4", "hL3", "hL2", "hL1", "читання"]
    for r, lab in enumerate(rowlab):
        p.append(text(82, cy_row(r) + rowh / 2 + 4, lab, size=12.5,
                      color=INK if r < 4 else "#8a6100", bold=(r == 4)))
    p.append(text(82, 95, "хост ↓", size=11, color=MUTED))

    guest_cap = {0: "чит. gL4", 1: "чит. gL3", 2: "чит. gL2", 3: "чит. gL1"}
    for c in range(5):
        for r in range(5):
            x, y = cx_col(c), cy_row(r)
            n = c * 5 + r + 1
            if r < 4:
                fill, stroke, cap, capcol = BLUE_FILL, NEG, "хост", MUTED
            elif c < 4:
                fill, stroke, cap, capcol = "#fff3d6", "#c98a00", guest_cap[c], "#8a6100"
            else:
                fill, stroke, cap, capcol = GREEN_FILL, FIELD, "ДАНІ", "#1b7a43"
            p.append(rect(x, y, colw, rowh, fill=fill, stroke=stroke, sw=1.5))
            p.append(text(x + colw / 2, y + 40, str(n), size=22, bold=True))
            p.append(text(x + colw / 2, y + 62, cap, size=11, color=capcol))

    ly = 566
    def swatch(sx, fill, stroke, label):
        return [rect(sx, ly - 13, 20, 16, fill=fill, stroke=stroke, sw=1.4, rx=3),
                text(sx + 28, ly, label, size=12, color=INK, anchor="start")]
    p += swatch(120, BLUE_FILL, NEG, "хостове звернення  (×20)")
    p += swatch(400, "#fff3d6", "#c98a00", "читання гост. запису  (×4)")
    p += swatch(700, GREEN_FILL, FIELD, "дані  (×1)")

    note, _, _ = textbox(W / 2, 628,
        "20 хостових звернень (5 × 4)  +  4 читання гостьових записів  =  24 обходу;   25-те — самі дані.\n"
        "(g+1)(h+1) − 1 = 5·5 − 1 = 24",
        size=13, color=INK, fill="#fbfbfb", stroke=MUTED, sw=1.2)
    p.append(note)

    render(os.path.join(IMG, "nested-grid.svg"), W, H, *p,
           title="Двовимірний обхід: 5 × 5 = 25 звернень, 24 з них — обхід")


# ── Фігура 7 (вставка math): великі сторінки коротшають обхід ────────────────
def fig_hugepage_bars():
    W, H = 840, 520
    p = []
    p.append(text(W / 2, 50, "звернень до пам'яті на один промах TLB (найгірший обхід)",
                  size=12.5, color=MUTED))
    base_y, top_y, axis_x = 410, 78, 96
    scale = (base_y - top_y) / 25.0

    p.append(line(axis_x, top_y - 6, axis_x, base_y, color=INK, sw=1.6))
    p.append(line(axis_x, base_y, 800, base_y, color=INK, sw=1.6))
    for v in (0, 8, 16, 24):
        yv = base_y - v * scale
        p.append(line(axis_x - 5, yv, axis_x, yv, color=INK, sw=1.2))
        p.append(text(axis_x - 12, yv + 4, str(v), size=12, color=MUTED, anchor="end"))
        if v > 0:
            p.append(line(axis_x, yv, 800, yv, color="#e8e8e8", sw=1))

    ny = base_y - 4 * scale
    p.append(line(axis_x, ny, 800, ny, color=FIELD, sw=1.6, dash="6,5"))
    p.append(text(792, ny - 8, "голий метал = 4", size=12, color=FIELD, anchor="end"))

    bars = [("4К / 4К", 24, RED_FILL, POS),
            ("4К / 2М", 19, BLUE_FILL, NEG),
            ("4К / 1Г", 14, BLUE_FILL, NEG),
            ("2М / 2М", 15, BLUE_FILL, NEG),
            ("1Г / 1Г", 8, GREEN_FILL, FIELD)]
    x_left, bw = 120, 82
    slot = (790 - x_left) / len(bars)
    for i, (lab, val, fill, stroke) in enumerate(bars):
        cxb = x_left + i * slot + slot / 2
        h = val * scale
        y = base_y - h
        p.append(rect(cxb - bw / 2, y, bw, h, fill=fill, stroke=stroke, sw=1.8, rx=4))
        p.append(text(cxb, y - 10, str(val), size=19, bold=True))
        p.append(text(cxb, base_y + 22, lab, size=13, bold=True))
    p.append(text((x_left + 790) / 2, base_y + 44,
                  "розмір сторінки:  гість / хост", size=12, color=MUTED))

    render(os.path.join(IMG, "hugepage-bars.svg"), W, H, *p,
           title="Великі сторінки коротшають вкладений обхід")


# ── Фігура 8 (вставка hist): стрічка часу віртуальної машини ─────────────────
def fig_vm_timeline():
    W, H = 900, 720
    p = []
    ax = 300
    p.append(line(ax, 108, ax, 678, color=MUTED, sw=2))
    rows = [
        ("1964",    ("M44/44X (Йорктаун): народжується сам термін",
                     "«віртуальна машина» — та лише ЧАСТКОВА"),             FILL,       LINE),
        ("1967",    ("CP-40 (Кембридж, Кризі й Комо): в експлуатації —",
                     "перша ПОВНА віртуальна машина, за 7 років до теорії"), GREEN_FILL, FIELD),
        ("1972",    ("VM/370: віртуалізація стає товаром IBM",
                     "(System/370 з апаратним перекладом адрес)"),          GREEN_FILL, FIELD),
        ("1974",    ("Теорема Попека–Ґолдберґа (CACM 17):",
                     "«чутливе ⊆ привілейоване» — коли ВМ можлива"),        BLUE_FILL,  NEG),
        ("1999",    ("VMware: двійкова трансляція на льоту",
                     "обходить діру x86, не змінюючи гостя"),               AMBER_FILL, AMBER_STK),
        ("2000",    ("Робін·Ірвайн (USENIX): ~17 команд x86 —",
                     "чутливі, але НЕ привілейовані; умову порушено"),      RED_FILL,   POS),
        ("2003",    ("Xen (SOSP): паравіртуалізація —",
                     "гостя правлять на гіпервиклики"),                     AMBER_FILL, AMBER_STK),
        ("2005–06", ("Intel VT-x і AMD-V: залізо додає кореневий",
                     "режим і закриває діру — гість біжить незмінний"),     GREEN_FILL, FIELD),
    ]
    cy = 148
    for year, (l1, l2), fill, stroke in rows:
        p.append(circle(ax, cy, 8, fill=stroke, stroke=stroke))
        p.append(text(ax - 22, cy + 5, year, size=15, bold=True, anchor="end"))
        p.append(fitbox(ax + 32, cy - 30, 552, 60, l1 + "\n" + l2,
                        size=13, fill=fill, stroke=stroke))
        cy += 70
    render(os.path.join(IMG, "vm-timeline.svg"), W, H, *p,
           title="Сорок років віртуальної машини: реалізація випередила теорію")


# ── Фігура 9 (вставка hist): умова Попека–Ґолдберґа як множини ───────────────
def fig_pg_condition():
    W, H = 940, 560
    p = []
    p.append(line(468, 118, 468, 500, color=MUTED, sw=1.2, dash="6,6"))

    # ── ліва панель: умову виконано ──
    p.append(text(238, 100, "Умова виконана — S/360 · VM/370", size=14.5, bold=True))
    p.append(circle(238, 300, 150, fill=GREEN_FILL, stroke=FIELD, sw=2))
    p.append(circle(238, 330, 82, fill=BLUE_FILL, stroke=NEG, sw=2))
    p.append(text(238, 205, "привілейовані", size=13.5, color=FIELD, bold=True))
    p.append(text(238, 335, "чутливі", size=13, color=NEG, bold=True))
    cap1, _, _ = textbox(238, 500, "чутливе ⊆ привілейоване:\nусе ловиться пасткою",
                         size=12.5, color=INK, fill=GREEN_FILL, stroke=FIELD, sw=1.4)
    p.append(cap1)

    # ── права панель: умову порушено ──
    p.append(text(700, 100, "Умова порушена — x86", size=14.5, bold=True))
    p.append(circle(648, 300, 132, fill=GREEN_FILL, stroke=FIELD, sw=2))
    p.append(circle(780, 300, 92, fill=RED_FILL, stroke=POS, sw=2))
    p.append(text(600, 214, "привілейовані", size=13, color=FIELD, bold=True))
    p.append(text(742, 250, "чутливі", size=13, color=POS, bold=True))
    p.append(arrow(820, 428, 842, 330, color=POS, sw=1.8))
    call, _, _ = textbox(812, 468,
        "POPF · SGDT · SIDT\nSLDT · …  ~17 команд:\nне падають пасткою",
        size=12, color=INK, fill=RED_FILL, stroke=POS, sw=1.4)
    p.append(call)
    render(os.path.join(IMG, "pg-condition.svg"), W, H, *p,
           title="Умова Попека–Ґолдберґа: чутливе ⊆ привілейоване")


if __name__ == "__main__":
    fig_privilege()
    fig_cycle()
    fig_nested()
    fig_kvm_handles()
    fig_kvm_memory()
    fig_nested_grid()
    fig_hugepage_bars()
    fig_vm_timeline()
    fig_pg_condition()
    print("figs done:", os.listdir(IMG))

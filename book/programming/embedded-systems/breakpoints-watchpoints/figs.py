# -*- coding: utf-8 -*-
"""Фігури до теми «Брейкпоінти й вотчпоінти» (базова версія).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).

Фігури теми (імена-слаги, без номерів):
  hw-breakpoint · sw-breakpoint · watchpoint · two-units · budget
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def _cell(f, x, y, addr, fill=FILL, stroke=LINE, note="інструкція", note_col=MUTED):
    f.append(rect(x, y, 74, 42, fill=fill, stroke=stroke, sw=1.3, rx=4))
    f.append(text(x + 37, y + 18, addr, size=11, color=INK))
    f.append(text(x + 37, y + 33, note, size=9, color=note_col))


# ── 1. Апаратний брейкпоінт: компаратор стежить за PC ────────────────────────
def fig_hw_breakpoint():
    W, H = 760, 330
    f = []
    f.append(text(W / 2, 30, "Апаратний брейк: компаратор стежить за лічильником команд", size=14, bold=True))

    f.append(text(150, 70, "Потік вибірки команд (Flash)", size=11, color=MUTED))
    addrs = ["0x0800", "0x0804", "0x0808", "0x080C"]
    for i, a in enumerate(addrs):
        hit = (a == "0x0808")
        _cell(f, 40 + i * 80, 84, a,
              fill="#fdecea" if hit else FILL,
              stroke=POS if hit else LINE,
              note="← цільовий рядок" if hit else "інструкція",
              note_col=POS if hit else MUTED)

    f.append(text(190, 168, "байт у Flash НЕ змінено", size=10.5, color=FIELD, bold=True))

    f.append(line(370, 105, 430, 105, color=INK, sw=2))
    f.append(text(400, 96, "PC", size=11, color=INK, bold=True))

    box, bw, bh = textbox(560, 110, ["Компаратор адрес (FPB)",
                                     "збережено: 0x0808"], size=11, bold=False,
                          fill="#eaf0fd", stroke=NEG, sw=2, min_w=230)
    f.append(box)
    f.append(line(434, 105, 560 - bw / 2, 105, color=INK, sw=1.8))

    f.append(arrow(560, 110 + bh / 2, 560, 200, color=POS, sw=2.4))
    halt, hw, hh = textbox(560, 226, ["PC == 0x0808 → HALT",
                                      "(ще до виконання)"], size=12, bold=True,
                           fill="#fdecea", stroke=POS, sw=2)
    f.append(halt)

    f.append(text(W / 2, 308, "Компаратор у залізі, тож точка працює і у Flash — але компараторів лічена кількість.",
                  size=10, color=MUTED))
    render(os.path.join(IMG, "hw-breakpoint.svg"), W, H, *f)


# ── 2. Програмний брейкпоінт: підміна інструкції на BKPT ─────────────────────
def fig_sw_breakpoint():
    W, H = 760, 320
    f = []
    f.append(text(W / 2, 30, "Програмний брейк: інструкцію тимчасово підмінює пастка BKPT", size=14, bold=True))

    # before
    f.append(text(190, 72, "БУЛО (у RAM)", size=11, color=MUTED, bold=True))
    _cell(f, 60, 86, "0x2008", note="ldr  r0,[r1]", note_col=INK)
    f.append(text(97, 142, "оригінал", size=9, color=MUTED))

    f.append(arrow(150, 107, 250, 107, color=INK, sw=2.2))
    f.append(text(200, 96, "запис BKPT", size=10, color=POS, bold=True))

    # after
    _cell(f, 260, 86, "0x2008", fill="#fdecea", stroke=POS, note="BKPT  #0", note_col=POS)
    f.append(text(297, 142, "пастка", size=9, color=POS))

    # restore loop
    steps = [
        "1. зберегти оригінальну інструкцію",
        "2. на її місце записати BKPT",
        "3. ядро дійшло до BKPT → HALT",
        "4. повернути оригінал, виконати крок",
        "5. знову поставити BKPT назад",
    ]
    f.append(rect(440, 70, 290, 150, fill=FILL, stroke=LINE, sw=1.4, rx=8))
    for i, s in enumerate(steps):
        f.append(text(456, 96 + i * 26, s, size=10.5, color=INK, anchor="start"))

    f.append(text(200, 200, "скільки завгодно — обмежує лише пам'ять хоста", size=10.5, color=FIELD, bold=True))
    f.append(text(200, 222, "у чистому Flash так «на льоту» не вийде:", size=10, color=POS))
    f.append(text(200, 240, "щоб змінити байт, сектор треба стерти й перезаписати", size=10, color=POS))

    f.append(text(W / 2, 300, "На ESP32 цей бар'єр обходить OpenOCD: він перепрошиває сторінку Flash і дає «програмні» брейки і там.",
                  size=10, color=MUTED))
    render(os.path.join(IMG, "sw-breakpoint.svg"), W, H, *f)


# ── 3. Вотчпоінт: пастка на адресу ДАНИХ ─────────────────────────────────────
def fig_watchpoint():
    W, H = 760, 330
    f = []
    f.append(text(W / 2, 30, "Вотчпоінт: пастка спрацьовує на доступ до адреси даних", size=14, bold=True))

    # suspects
    f.append(text(160, 70, "Хто завгодно пише в пам'ять", size=11, color=MUTED))
    who = ["Задача A", "Задача B", "ISR таймера"]
    for i, w in enumerate(who):
        f.append(rect(60, 86 + i * 50, 200, 38, fill=FILL, stroke=LINE, sw=1.3, rx=6))
        f.append(text(160, 110 + i * 50, w, size=11, color=INK))
        f.append(arrow(264, 105 + i * 50, 330, 150, color=MUTED, sw=1.6))

    # variable + DWT
    box, bw, bh = textbox(440, 150, ["g_config.rate",
                                     "адреса 0x20000110"], size=11,
                          fill="#fff8e6", stroke="#caa24a", sw=2, min_w=180)
    f.append(box)

    f.append(arrow(440 + bw / 2, 150, 560, 150, color=POS, sw=2.2))
    cmp_box, cw, ch = textbox(640, 150, ["Компаратор даних",
                                         "(DWT)",
                                         "addr == 0x...0110",
                                         "умова: запис"], size=10,
                              fill="#eaf0fd", stroke=NEG, sw=2, min_w=150)
    f.append(cmp_box)

    f.append(arrow(640, 150 + ch / 2, 640, 250, color=POS, sw=2.4))
    halt, hw2, hh2 = textbox(640, 274, ["ЗБІГ → HALT",
                                        "видно рядок і стек"], size=11, bold=True,
                             fill="#fdecea", stroke=POS, sw=2)
    f.append(halt)

    f.append(text(290, 300, "Ловить винуватця псування пам'яті,", size=10.5, color=INK))
    f.append(text(290, 318, "ким би він не був.", size=10.5, color=INK))
    render(os.path.join(IMG, "watchpoint.svg"), W, H, *f)


# ── 4. Два різні блоки: FPB (код) і DWT (дані) — окремі ──────────────────────
def fig_two_units():
    W, H = 720, 300
    f = []
    f.append(text(W / 2, 30, "На Cortex-M це ДВА окремі блоки з власними лічильниками", size=14, bold=True))

    f.append(rect(50, 60, 290, 190, fill="#eef4ff", stroke=NEG, sw=2, rx=12))
    f.append(text(195, 88, "FPB — Flash Patch & Breakpoint", size=12, color=NEG, bold=True))
    f.append(text(195, 110, "стежить за адресою КОДУ (PC)", size=10.5, color=INK))
    for i, ln in enumerate([
        "• ~6 компараторів інструкцій",
        "• апаратні брейки у Flash",
        "• плюс «латка» — підміна слова",
    ]):
        f.append(text(70, 140 + i * 26, ln, size=10.5, color=INK, anchor="start"))
    f.append(text(195, 232, "адреса 0xE0002000", size=9.5, color=MUTED))

    f.append(rect(380, 60, 290, 190, fill="#fff6f5", stroke=POS, sw=2, rx=12))
    f.append(text(525, 88, "DWT — Data Watchpoint & Trace", size=12, color=POS, bold=True))
    f.append(text(525, 110, "стежить за адресою ДАНИХ", size=10.5, color=INK))
    for i, ln in enumerate([
        "• до 4 компараторів",
        "• вотчпоінти (читання/запис)",
        "• пастка на значення з'їдає два",
    ]):
        f.append(text(400, 140 + i * 26, ln, size=10.5, color=INK, anchor="start"))
    f.append(text(525, 232, "адреса 0xE0001000", size=9.5, color=MUTED))

    f.append(text(W / 2, 282, "Брейки й вотчпоінти не «крадуть» лічильники один в одного — це різне залізо.",
                  size=10, color=MUTED))
    render(os.path.join(IMG, "two-units.svg"), W, H, *f)


# ── 5. Бюджет пасток на ESP32: як вкластись у 2+2 ────────────────────────────
def fig_budget():
    W, H = 720, 320
    f = []
    f.append(text(W / 2, 30, "Бюджет апаратних пасток на ESP32 (2 брейки + 2 вотчпоінти)", size=14, bold=True))

    f.append(rect(50, 60, 300, 150, fill="#eef4ff", stroke=NEG, sw=2, rx=12))
    f.append(text(200, 86, "2 апаратні брейки", size=12, color=NEG, bold=True))
    slots_b = ["hbreak flash_handler", "(вільний)"]
    for i, s in enumerate(slots_b):
        used = i == 0
        f.append(rect(66, 102 + i * 40, 268, 32, fill="#fdecea" if used else FILL,
                      stroke=POS if used else LINE, sw=1.4, rx=5))
        f.append(text(200, 123 + i * 40, s, size=10.5, color=POS if used else MUTED))
    f.append(text(200, 198, "працюють у Flash і в IRAM", size=9.5, color=MUTED))

    f.append(rect(370, 60, 300, 150, fill="#fff6f5", stroke=POS, sw=2, rx=12))
    f.append(text(520, 86, "2 вотчпоінти", size=12, color=POS, bold=True))
    slots_w = ["watch g_queue_len", "зайнятий RTOS-вартою стека"]
    for i, s in enumerate(slots_w):
        f.append(rect(386, 102 + i * 40, 268, 32, fill="#fff8e6",
                      stroke="#caa24a", sw=1.4, rx=5))
        f.append(text(520, 123 + i * 40, s, size=10, color="#8a6d1f"))
    f.append(text(520, 198, "один уже може бути зайнятий!", size=9.5, color=POS, bold=True))

    f.append(rect(50, 232, 620, 60, fill=FILL, stroke=FIELD, sw=1.6, rx=10))
    f.append(text(360, 256, "Третій брейк — у RAM/Flash як ПРОГРАМНИЙ (OpenOCD): апаратних не їсть.",
                  size=11, color=INK, bold=True))
    f.append(text(360, 278, "break ram_buffer_fill   # хост сам підмінює інструкцію",
                  size=10.5, color=FIELD))
    render(os.path.join(IMG, "budget.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
#  Детальна версія (-d): глибший механізм FPB/DWT
# ════════════════════════════════════════════════════════════════════════════

# ── D1. FPB зсередини: компаратори інструкцій/літералів + ремап у RAM ────────
def fig_fpb_remap():
    W, H = 760, 380
    f = []
    f.append(text(W / 2, 30, "FPB зсередини: брейк (HALT) і латка (remap) — той самий блок", size=14, bold=True))

    # Flash side
    f.append(text(120, 70, "Flash (код прошивки)", size=11, color=MUTED, bold=True))
    _cell(f, 40, 86, "0x0800", note="bl  init", note_col=INK)
    _cell(f, 40, 132, "0x0804", fill="#fdecea", stroke=POS, note="(брейк тут)", note_col=POS)
    _cell(f, 40, 178, "0x0808", fill="#fff8e6", stroke="#caa24a", note="(латка тут)", note_col="#8a6d1f")

    # FPB unit
    f.append(rect(280, 70, 230, 230, fill="#eef4ff", stroke=NEG, sw=2, rx=12))
    f.append(text(395, 94, "FPB", size=13, color=NEG, bold=True))
    f.append(text(395, 114, "6 компараторів інструкцій", size=10, color=INK))
    f.append(text(395, 132, "2 компаратори літералів", size=10, color=INK))
    f.append(rect(296, 146, 198, 28, fill="#fdecea", stroke=POS, sw=1.3, rx=4))
    f.append(text(395, 164, "CMP: 0x0804 → BKPT (halt)", size=10, color=POS))
    f.append(rect(296, 180, 198, 28, fill="#fff8e6", stroke="#caa24a", sw=1.3, rx=4))
    f.append(text(395, 198, "CMP: 0x0808 → remap", size=10, color="#8a6d1f"))
    f.append(rect(296, 214, 198, 28, fill=FILL, stroke=LINE, sw=1.0, rx=4))
    f.append(text(395, 232, "REMAP base → таблиця в RAM", size=9.5, color=INK))
    f.append(text(395, 268, "обидва режими — одне залізо", size=10, color=NEG, bold=True))
    f.append(text(395, 286, "тому компаратори лічені", size=9.5, color=MUTED))

    f.append(arrow(118, 153, 280, 160, color=POS, sw=1.8))
    f.append(arrow(118, 199, 280, 194, color="#caa24a", sw=1.8))

    # RAM patch
    f.append(rect(560, 150, 170, 110, fill="#fbfdfb", stroke=FIELD, sw=2, rx=10))
    f.append(text(645, 174, "Латка в RAM", size=11, color=FIELD, bold=True))
    f.append(text(645, 198, "виправлена", size=10, color=INK))
    f.append(text(645, 214, "інструкція", size=10, color=INK))
    f.append(text(645, 238, "Flash не чіпано", size=9.5, color=MUTED))
    f.append(arrow(510, 196, 560, 200, color=FIELD, sw=2))

    f.append(text(W / 2, 350, "Брейк підставляє ядру BKPT; латка підставляє слово з RAM — Flash в обох випадках лишається незмінним.",
                  size=10, color=MUTED))
    render(os.path.join(IMG, "fpb-remap.svg"), W, H, *f)


# ── D2. DWT: пастка на значення коштує ДВА компаратори ───────────────────────
def fig_dwt_value():
    W, H = 740, 320
    f = []
    f.append(text(W / 2, 30, "DWT: вотчпоінт на ЗНАЧЕННЯ зчіплює два компаратори", size=14, bold=True))

    # address-only
    f.append(rect(40, 60, 320, 110, fill="#eef4ff", stroke=NEG, sw=2, rx=12))
    f.append(text(200, 86, "«спинись на ДОСТУПІ до адреси»", size=11, color=NEG, bold=True))
    f.append(rect(60, 100, 280, 30, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=5))
    f.append(text(200, 120, "CMP0: addr == 0x20000110", size=10.5, color=INK))
    f.append(text(200, 152, "1 компаратор → лишилось 3", size=10, color=FIELD, bold=True))

    # value match
    f.append(rect(40, 190, 320, 110, fill="#fff6f5", stroke=POS, sw=2, rx=12))
    f.append(text(200, 216, "«спинись, коли стане == 0xFF»", size=11, color=POS, bold=True))
    f.append(rect(60, 230, 280, 24, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=5))
    f.append(text(200, 246, "CMP0: addr == 0x20000110", size=10, color=INK))
    f.append(rect(60, 258, 280, 24, fill="#fdecea", stroke=POS, sw=1.2, rx=5))
    f.append(text(200, 274, "CMP1: value == 0xFF", size=10, color=POS))

    f.append(rect(400, 190, 320, 110, fill=FILL, stroke=POS, sw=1.6, rx=12))
    f.append(text(560, 214, "2 компаратори → лишилось 2", size=10.5, color=POS, bold=True))
    f.append(text(560, 240, "На чотирьох DWT-комірках це", size=10, color=INK))
    f.append(text(560, 258, "лише ДВІ пастки-на-значення", size=10, color=INK))
    f.append(text(560, 278, "одночасно.", size=10, color=INK))

    f.append(rect(400, 60, 320, 110, fill=FILL, stroke=FIELD, sw=1.6, rx=12))
    f.append(text(560, 86, "Звідси правило:", size=11, color=FIELD, bold=True))
    f.append(text(560, 112, "якщо досить «будь-який запис»,", size=10, color=INK))
    f.append(text(560, 130, "не проси збіг значення —", size=10, color=INK))
    f.append(text(560, 148, "збережеш дефіцитний компаратор.", size=10, color=INK))

    render(os.path.join(IMG, "dwt-value.svg"), W, H, *f)


# ── D3. Умовний брейк: чому при частих влученнях він повзе ────────────────────
def fig_conditional_cost():
    W, H = 760, 300
    f = []
    f.append(text(W / 2, 30, "Умовний брейк: ядро спиняється на КОЖНОМУ влученні", size=14, bold=True))

    cycle = [
        ("HALT", POS, "#fdecea"),
        ("хост читає\nрегістри/стек", NEG, "#eaf0fd"),
        ("GDB рахує\nумову", INK, FILL),
        ("умова хибна →\nresume", FIELD, "#fbfdfb"),
    ]
    x = 50
    cx_list = []
    for i, (label, col, fill) in enumerate(cycle):
        box, bw, bh = textbox(x + 75, 110, label, size=10.5, fill=fill, stroke=col, sw=1.8, min_w=140)
        f.append(box)
        cx_list.append((x + 75, bw))
        if i > 0:
            px, pw = cx_list[i - 1]
            f.append(arrow(px + pw / 2, 110, x + 75 - bw / 2, 110, color=MUTED, sw=2))
        x += 175

    f.append(text(W / 2, 168, "кожен оберт — зупинка ядра + round-trip по SWD до хоста", size=11, color=POS, bold=True))

    f.append(rect(90, 196, 580, 80, fill=FILL, stroke=LINE, sw=1.4, rx=10))
    f.append(text(380, 220, "1000 влучень × ~частка мілісекунди на оберт = відчутні секунди простою",
                  size=11, color=INK, bold=True))
    f.append(text(380, 246, "висновок: умову треба робити рідкісною, або краще — апаратний вотчпоінт за даними",
                  size=10, color=MUTED))
    f.append(text(380, 264, "(там фільтрує залізо, ядро не спиняється намарно)", size=10, color=MUTED))
    render(os.path.join(IMG, "conditional-cost.svg"), W, H, *f)


# ── D4. ESP32: як OpenOCD підставляє програмний брейк у Flash ─────────────────
def fig_esp32_flash_bp():
    W, H = 760, 330
    f = []
    f.append(text(W / 2, 30, "ESP32: OpenOCD дає «програмний» брейк навіть у Flash", size=14, bold=True))

    steps = [
        ("break\nflash_func", NEG, "#eaf0fd"),
        ("апаратні\nскінчились?", INK, FILL),
        ("прочитати\nсторінку Flash", MUTED, FILL),
        ("вписати BREAK,\nперепрошити", POS, "#fdecea"),
        ("ядро спиниться\nна BREAK", FIELD, "#fbfdfb"),
    ]
    x = 40
    prev = None
    for i, (label, col, fill) in enumerate(steps):
        box, bw, bh = textbox(x + 68, 110, label, size=10, fill=fill, stroke=col, sw=1.8, min_w=130)
        f.append(box)
        if prev:
            f.append(arrow(prev[0] + prev[1] / 2, 110, x + 68 - bw / 2, 110, color=MUTED, sw=1.9))
        prev = (x + 68, bw)
        x += 144

    f.append(rect(60, 170, 300, 110, fill="#fbfdfb", stroke=FIELD, sw=1.8, rx=12))
    f.append(text(210, 194, "Чим платимо", size=11, color=FIELD, bold=True))
    for i, ln in enumerate(["• час на стирання+запис сторінки", "• ресурс стирань Flash", "• до 32 таких у Flash + 32 в IRAM"]):
        f.append(text(78, 220 + i * 22, ln, size=10, color=INK, anchor="start"))

    f.append(rect(400, 170, 320, 110, fill="#fff6f5", stroke=POS, sw=1.8, rx=12))
    f.append(text(560, 194, "Пастка FreeRTOS", size=11, color=POS, bold=True))
    for i, ln in enumerate([
        "вартовий кінця стека з'їдає",
        "один із ДВОХ вотчпоінтів —",
        "тоді твій watch без ресурсу",
        "(CONFIG_FREERTOS_WATCHPOINT_…)"]):
        f.append(text(418, 220 + i * 22, ln, size=9.5, color=INK, anchor="start"))

    f.append(text(W / 2, 306, "Тому «у Flash тільки апаратні» — міф для ESP32: бар'єр обходить перепрошивання сторінки.",
                  size=10, color=MUTED))
    render(os.path.join(IMG, "esp32-flash-bp.svg"), W, H, *f)


if __name__ == "__main__":
    fig_hw_breakpoint()
    fig_sw_breakpoint()
    fig_watchpoint()
    fig_two_units()
    fig_budget()
    fig_fpb_remap()
    fig_dwt_value()
    fig_conditional_cost()
    fig_esp32_flash_bp()
    print("OK base: hw-breakpoint, sw-breakpoint, watchpoint, two-units, budget")
    print("OK -d: fpb-remap, dwt-value, conditional-cost, esp32-flash-bp")

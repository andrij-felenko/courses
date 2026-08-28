# -*- coding: utf-8 -*-
"""Фігури до теми «Протокол SCPI для керування приладами (SCPI Protocol)».
Запуск: python figs.py -> генерує SVG у ./img/
Спільні помічники: scripts/svgkit.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def path_elem(d, stroke="#718096", sw=1.5, fill="none"):
    return '<path d="%s" stroke="%s" stroke-width="%.1f" fill="%s"/>' % (d, stroke, sw, fill)


# ── 1. Ієрархічне дерево підсистем команд SCPI ─────────────────────────────────
def fig_command_tree():
    W, H = 1000, 560
    f = [
        text(W / 2, 28, "Ієрархічне дерево команд SCPI та правила навігації вузлами",
             size=16, bold=True)
    ]

    # Кореневий рівень
    root_x, root_y = 110, 280
    f.append(rect(root_x - 65, root_y - 25, 130, 50, fill="#2c3e50", stroke=LINE, sw=1.5, rx=6))
    f.append(text(root_x, root_y + 6, "КОРІНЬ «:»", size=13, color="#ffffff", bold=True))

    # Спільні команди IEEE 488.2 (поза деревом)
    ieee_x, ieee_y = 110, 100
    f.append(rect(ieee_x - 90, ieee_y - 35, 180, 70, fill="#edf2f7", stroke="#4a5568", sw=1.5, rx=6))
    f.append(text(ieee_x, ieee_y - 12, "Команди IEEE 488.2", size=11, bold=True, color="#2d3748"))
    f.append(text(ieee_x, ieee_y + 12, "*IDN? *RST *CLS *OPC", size=10.5, bold=True, color=POS))

    # Підсистеми
    subs = [
        (":SOURce", 110, "#ebf8ff", "#2b6cb0", [
            (":VOLTage", 80, [("[:LEVel] <val>", 65), (":PROTection", 95)]),
            (":CURRent", 145, [("[:LEVel] <val>", 130), (":RANGe", 160)])
        ]),
        (":SENSe", 260, "#f0fff4", "#276749", [
            (":VOLTage[:DC]", 230, [(":RANGe <val>", 215), (":NPLC <val>", 245)]),
            (":CURRent[:DC]", 290, [(":RANGe <val>", 290)])
        ]),
        (":MEASure", 385, "#fffaf0", "#c05621", [
            (":VOLTage[:DC]?", 365, []),
            (":CURRent[:DC]?", 405, [])
        ]),
        (":SYSTem", 475, "#faf5ff", "#6b46c1", [
            (":ERRor[:NEXT]?", 455, []),
            (":VERSion?", 495, [])
        ]),
    ]

    sub_x = 320
    node_x = 550
    leaf_x = 790

    for sub_name, sub_y, bg_col, stroke_col, nodes in subs:
        # Лінія від кореня до підсистеми
        f.append(path_elem("M %d %d C %d %d, %d %d, %d %d" % (
            root_x + 65, root_y,
            (root_x + sub_x) / 2, root_y,
            (root_x + sub_x) / 2, sub_y,
            sub_x - 65, sub_y
        ), stroke="#718096", sw=1.5))

        # Блок підсистеми
        f.append(rect(sub_x - 65, sub_y - 20, 130, 40, fill=bg_col, stroke=stroke_col, sw=1.5, rx=5))
        f.append(text(sub_x, sub_y + 5, sub_name, size=12, bold=True, color=stroke_col))

        for node_name, node_y, leaves in nodes:
            # Лінія від підсистеми до вузла
            f.append(path_elem("M %d %d C %d %d, %d %d, %d %d" % (
                sub_x + 65, sub_y,
                (sub_x + node_x) / 2, sub_y,
                (sub_x + node_x) / 2, node_y,
                node_x - 75, node_y
            ), stroke="#718096", sw=1.2))

            # Блок вузла
            f.append(rect(node_x - 75, node_y - 16, 150, 32, fill="#ffffff", stroke=stroke_col, sw=1.2, rx=4))
            f.append(text(node_x, node_y + 5, node_name, size=11, bold=True, color=INK))

            for leaf_name, leaf_y in leaves:
                # Лінія від вузла до листка
                f.append(path_elem("M %d %d C %d %d, %d %d, %d %d" % (
                    node_x + 75, node_y,
                    (node_x + leaf_x) / 2, node_y,
                    (node_x + leaf_x) / 2, leaf_y,
                    leaf_x - 85, leaf_y
                ), stroke="#a0aec0", sw=1.0))

                # Блок листка
                f.append(rect(leaf_x - 85, leaf_y - 13, 170, 26, fill="#f7fafc", stroke="#a0aec0", sw=1.0, rx=4))
                f.append(text(leaf_x, leaf_y + 4, leaf_name, size=10, bold=False, color=INK))

    # Пояснювальний блок унизу
    info_y = 535
    f.append(rect(20, info_y - 16, W - 40, 30, fill="#f7fafc", stroke="#cbd5e0", sw=1, rx=4))
    f.append(text(W / 2, info_y + 4,
                  "Синтаксис: [:SUBsystem]:NODE:LEAF [параметр] ; відносний перехід: «:SOUR:VOLT 5; CURR 2» ; повернення в корінь: «; :MEAS:VOLT?»",
                  size=10.5, color="#4a5568"))

    render(os.path.join(IMG, "scpi-command-tree-hierarchy.svg"), W, H, *f)


# ── 2. Регістри стану IEEE 488.2 та SCPI ───────────────────────────────────────
def fig_status_registers():
    W, H = 1040, 620
    f = [
        text(W / 2, 28, "Архітектура регістрів стану IEEE 488.2 та підсистем SCPI",
             size=16, bold=True)
    ]

    # 1. Standard Event Status Register (ESR & ESE)
    esr_x, esr_y = 195, 115
    f.append(rect(esr_x - 175, esr_y - 50, 350, 100, fill="#f0fff4", stroke="#276749", sw=1.5, rx=6))
    f.append(text(esr_x, esr_y - 28, "Standard Event Status Register (ESR / *ESR?)", size=11, bold=True, color="#276749"))
    f.append(text(esr_x, esr_y - 9, "Біти: PON(7) | URQ(6) | CME(5) | EXE(4) | DDE(3) | QYE(2) | OPC(0)", size=9, color=INK))
    f.append(text(esr_x, esr_y + 11, "Маска дозволу: ESE (*ESE / *ESE?)", size=10, bold=True, color="#2f855a"))
    f.append(text(esr_x, esr_y + 31, "Підсумок (Bitwise AND -> OR) -> ESB (біт 5 STB)", size=9, color="#22543d"))

    # 2. Questionable Status Subsystem
    ques_x, ques_y = 195, 245
    f.append(rect(ques_x - 175, ques_y - 45, 350, 90, fill="#fffaf0", stroke="#c05621", sw=1.5, rx=6))
    f.append(text(ques_x, ques_y - 23, "Questionable Status Subsystem (:STAT:QUES)", size=11, bold=True, color="#c05621"))
    f.append(text(ques_x, ques_y - 6, "Condition -> Transition (PTR/NTR) -> Event -> Enable", size=9, color=INK))
    f.append(text(ques_x, ques_y + 13, "Події: перегрів, перевантаження, нестабільність шкали", size=9, color=MUTED))
    f.append(text(ques_x, ques_y + 30, "Підсумок -> QUES (біт 3 STB)", size=9, color="#7b341e"))

    # 3. Operation Status Subsystem
    oper_x, oper_y = 195, 365
    f.append(rect(oper_x - 175, oper_y - 45, 350, 90, fill="#ebf8ff", stroke="#2b6cb0", sw=1.5, rx=6))
    f.append(text(oper_x, oper_y - 23, "Operation Status Subsystem (:STAT:OPER)", size=11, bold=True, color="#2b6cb0"))
    f.append(text(oper_x, oper_y - 6, "Condition -> Transition (PTR/NTR) -> Event -> Enable", size=9, color=INK))
    f.append(text(oper_x, oper_y + 13, "Події: калібрування, очікування тригера, вимірювання", size=9, color=MUTED))
    f.append(text(oper_x, oper_y + 30, "Підсумок -> OPER (біт 7 STB)", size=9, color="#2c5282"))

    # 4. Error Queue & Output Buffer
    err_x, err_y = 195, 480
    f.append(rect(err_x - 175, err_y - 35, 350, 70, fill="#faf5ff", stroke="#6b46c1", sw=1.5, rx=6))
    f.append(text(err_x, err_y - 13, "Черга помилок FIFO (:SYST:ERR?) -> EAV (біт 2 STB)", size=10, bold=True, color="#6b46c1"))
    f.append(text(err_x, err_y + 13, "Вихідний буфер відповідей -> MAV (біт 4 STB)", size=10, bold=True, color="#553c9a"))

    # 5. Status Byte Register (STB) & SRE
    stb_x, stb_y = 655, 300
    f.append(rect(stb_x - 130, stb_y - 190, 260, 380, fill="#fff5f5", stroke=POS, sw=2, rx=8))
    f.append(text(stb_x, stb_y - 165, "Status Byte Register (STB)", size=13, bold=True, color=POS))
    f.append(text(stb_x, stb_y - 145, "Опитування: *STB? / Serial Poll", size=10.5, color="#742a2a"))

    # Розпис бітів STB
    bits = [
        ("Біт 7", "OPER", "Operation Status Summary", "#2b6cb0"),
        ("Біт 6", "MSS/RQS", "Master Summary / SRQ", POS),
        ("Біт 5", "ESB", "Standard Event Summary", "#276749"),
        ("Біт 4", "MAV", "Message Available", "#553c9a"),
        ("Біт 3", "QUES", "Questionable Summary", "#c05621"),
        ("Біт 2", "EAV", "Error Queue Available", "#6b46c1"),
        ("Біт 1", "PROT", "Protection Event", MUTED),
        ("Біт 0", "—", "User / Device Defined", MUTED),
    ]

    for idx, (b_num, b_name, b_desc, col) in enumerate(bits):
        row_y = (stb_y - 115) + idx * 34
        f.append(rect(stb_x - 118, row_y - 12, 236, 26, fill="#ffffff", stroke="#feb2b2", sw=1, rx=3))
        f.append(text(stb_x - 90, row_y + 5, b_num, size=10, bold=True, color=INK))
        f.append(text(stb_x - 40, row_y + 5, b_name, size=10.5, bold=True, color=col))
        f.append(text(stb_x + 45, row_y + 5, b_desc, size=9, color="#4a5568"))

    # Маска SRE
    sre_x, sre_y = 655, 535
    f.append(rect(sre_x - 130, sre_y - 22, 260, 44, fill="#edf2f7", stroke="#4a5568", sw=1.5, rx=5))
    f.append(text(sre_x, sre_y - 4, "Service Request Enable (SRE)", size=11, bold=True, color="#2d3748"))
    f.append(text(sre_x, sre_y + 14, "Команди: *SRE <val> / *SRE?", size=10, color="#4a5568"))

    # Стрілки від підсистем до STB
    # ESR -> ESB (bit 5)
    f.append(path_elem("M %d %d L %d %d" % (esr_x + 175, esr_y + 10, stb_x - 118, stb_y - 47), stroke="#276749", sw=1.5))
    # QUES -> QUES (bit 3)
    f.append(path_elem("M %d %d L %d %d" % (ques_x + 175, ques_y + 10, stb_x - 118, stb_y + 21), stroke="#c05621", sw=1.5))
    # OPER -> OPER (bit 7)
    f.append(path_elem("M %d %d L %d %d" % (oper_x + 175, oper_y + 10, stb_x - 118, stb_y - 115), stroke="#2b6cb0", sw=1.5))
    # ERR -> EAV (bit 2)
    f.append(path_elem("M %d %d L %d %d" % (err_x + 175, err_y - 13, stb_x - 118, stb_y + 55), stroke="#6b46c1", sw=1.5))
    # BUF -> MAV (bit 4)
    f.append(path_elem("M %d %d L %d %d" % (err_x + 175, err_y + 13, stb_x - 118, stb_y - 13), stroke="#553c9a", sw=1.5))

    # Фізичний перерив SRQ
    srq_x, srq_y = 920, 300
    f.append(rect(srq_x - 70, srq_y - 50, 140, 100, fill="#feebc8", stroke="#dd6b20", sw=2, rx=8))
    f.append(text(srq_x, srq_y - 24, "Апаратне / Мережеве", size=9.5, color="#7b341e"))
    f.append(text(srq_x, srq_y - 6, "Сповіщення", size=11, bold=True, color="#7b341e"))
    f.append(text(srq_x, srq_y + 14, "SRQ / USB Interrupt", size=10, bold=True, color=POS))
    f.append(text(srq_x, srq_y + 32, "HiSLIP Async Msg", size=9, color="#7b341e"))

    # Стрілка від STB/SRE до SRQ
    f.append(path_elem("M %d %d L %d %d" % (stb_x + 118, stb_y - 81, srq_x - 70, srq_y), stroke=POS, sw=2))

    render(os.path.join(IMG, "ieee488-status-byte-registers.svg"), W, H, *f)


if __name__ == "__main__":
    fig_command_tree()
    fig_status_registers()
    print("OK: generated 2 figures in img/")

# -*- coding: utf-8 -*-
"""Фігури до теми «Сокети домену Unix і передача дескрипторів»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

GREEN = "#eaf7ee"
SAND = "#f8f4ea"
COLD = "#eef2f7"
WARN = "#fdecea"


def fig_what_travels():
    """Після SCM_RIGHTS два різні числа вказують на один опис відкритого файлу."""
    W, H = 980, 380
    g = []

    # ── процес A ───────────────────────────────────────────────────────
    g.append(text(145, 48, "процес A", size=15, bold=True))
    g.append(rect(30, 62, 230, 232, fill=BG))
    g.append(fitbox(46, 78, 198, 34, "0 1 2 — стандартні", size=13))
    g.append(fitbox(46, 122, 198, 34, "3 → сокет до B", size=13))
    g.append(fitbox(46, 166, 198, 40, "7 → журнал", size=13, fill=GREEN))
    g.append(fitbox(46, 222, 198, 56,
                    "sendmsg кладе\nу керівну смугу число 7", size=12, fill=SAND))

    # ── ядро ───────────────────────────────────────────────────────────
    g.append(text(490, 48, "ядро", size=15, bold=True))
    g.append(fitbox(370, 78, 240, 118,
                    "опис відкритого файлу\nпозиція · прапорці\nлічильник посилань: 2",
                    size=13, fill=COLD))
    g.append(arrow(490, 200, 490, 232, color=MUTED, sw=1.4))
    g.append(fitbox(390, 234, 200, 44, "inode журналу", size=13))

    # ── процес B ───────────────────────────────────────────────────────
    g.append(text(845, 48, "процес B", size=15, bold=True))
    g.append(rect(730, 62, 220, 232, fill=BG))
    g.append(fitbox(746, 78, 188, 34, "0 1 2 — стандартні", size=13))
    g.append(fitbox(746, 122, 188, 34, "3 → сокет до A", size=13))
    g.append(fitbox(746, 166, 188, 40, "5 → журнал", size=13, fill=GREEN))
    g.append(fitbox(746, 222, 188, 56,
                    "число 5 обрало ядро,\nа не відправник", size=12, fill=SAND))

    # ── зв'язки з описом ───────────────────────────────────────────────
    g.append(arrow(266, 182, 366, 152, color=LINE, sw=1.6))
    g.append(arrow(724, 182, 614, 152, color=LINE, sw=1.6))

    g.append(text(490, 344,
                  "передається не число, а посилання на той самий об'єкт у ядрі",
                  size=13, color=MUTED))
    render(os.path.join(IMG, 'what-travels.svg'), W, H, *g)


def fig_message_lanes():
    """Одне повідомлення має дві смуги: байти ядро несе, керівну смугу — виконує."""
    W, H = 940, 410
    g = []

    g.append(text(295, 56, "повідомлення, віддане в sendmsg()", size=15, bold=True))
    g.append(rect(60, 76, 470, 268, fill=BG))
    g.append(fitbox(80, 96, 430, 80,
                    "смуга даних — msg_iov\nбайти, які програма набрала сама",
                    size=13, fill=COLD))
    g.append(fitbox(80, 196, 430, 130,
                    "керівна смуга — msg_control\ncmsg_level = SOL_SOCKET\ncmsg_type = SCM_RIGHTS\nдані: [ 7 ]",
                    size=13, fill=SAND))

    g.append(text(765, 56, "що дістав отримувач", size=15, bold=True))
    g.append(fitbox(620, 96, 290, 80,
                    "ті самі байти\nв буфері recvmsg", size=13, fill=COLD))
    g.append(fitbox(620, 196, 290, 130,
                    "новий дескриптор 5:\nчисло 7 ядро прочитало саме\nй підмінило посиланням",
                    size=13, fill=GREEN))

    g.append(arrow(534, 136, 616, 136, sw=1.6))
    g.append(arrow(534, 261, 616, 261, sw=1.6))

    g.append(text(470, 380,
                  "дані ядро лише переносить; керівну смугу воно читає й виконує",
                  size=13, color=MUTED))
    render(os.path.join(IMG, 'message-lanes.svg'), W, H, *g)


def fig_inflight_cycle():
    """Два сокети тримають один одного в польоті — лічильник посилань не нульовий."""
    W, H = 940, 390
    g = []

    g.append(text(220, 70, "сокет X", size=15, bold=True))
    g.append(rect(70, 84, 300, 176, fill=BG))
    g.append(fitbox(90, 100, 260, 44, "черга непрочитаного", size=13, fill=COLD))
    g.append(fitbox(90, 178, 260, 62, "у польоті:\nопис сокета Y", size=13, fill=SAND))

    g.append(text(720, 70, "сокет Y", size=15, bold=True))
    g.append(rect(570, 84, 300, 176, fill=BG))
    g.append(fitbox(590, 100, 260, 44, "черга непрочитаного", size=13, fill=COLD))
    g.append(fitbox(590, 178, 260, 62, "у польоті:\nопис сокета X", size=13, fill=SAND))

    g.append(text(470, 150, "тримає", size=12, color=MUTED))
    g.append(arrow(376, 172, 564, 172, color=MUTED, sw=1.5))
    g.append(arrow(564, 226, 376, 226, color=MUTED, sw=1.5))
    g.append(text(470, 250, "тримає", size=12, color=MUTED))

    g.append(fitbox(160, 292, 620, 62,
                    "процеси закрили свої дескриптори — ззовні на цю пару не посилається ніхто,\nа лічильники не нульові: саме такі замкнені кола шукає збирач сміття ядра",
                    size=12, fill=WARN))
    render(os.path.join(IMG, 'inflight-cycle.svg'), W, H, *g)


def fig_cmsg_layout():
    """Де фізично лежить доповнення і чим CMSG_LEN відрізняється від CMSG_SPACE."""
    W, H = 980, 350
    g = []

    g.append(text(490, 46, "керівний блок із трьома дескрипторами (x86-64)",
                  size=15, bold=True))

    g.append(fitbox(60, 96, 200, 68, "struct cmsghdr\n16 байтів", size=13, fill=COLD))
    g.append(fitbox(260, 96, 180, 68, "3 × int\n12 байтів", size=13, fill=GREEN))
    g.append(fitbox(440, 96, 90, 68, "доповнення\n4", size=12, fill=SAND))
    g.append(fitbox(530, 96, 200, 68, "наступний\nstruct cmsghdr", size=13, fill=BG))

    # ── дужка CMSG_LEN ─────────────────────────────────────────────────
    g.append(line(60, 200, 440, 200, color=MUTED, sw=1.4))
    g.append(line(60, 192, 60, 208, color=MUTED, sw=1.4))
    g.append(line(440, 192, 440, 208, color=MUTED, sw=1.4))
    g.append(text(250, 228, "CMSG_LEN(12) = 28  →  у поле cmsg_len", size=13))

    # ── дужка CMSG_SPACE ───────────────────────────────────────────────
    g.append(line(60, 262, 530, 262, color=MUTED, sw=1.4))
    g.append(line(60, 254, 60, 270, color=MUTED, sw=1.4))
    g.append(line(530, 254, 530, 270, color=MUTED, sw=1.4))
    g.append(text(295, 290, "CMSG_SPACE(12) = 32  →  розмір буфера й крок до наступного блоку",
                  size=13))

    g.append(text(490, 328,
                  "уся різниця — хвостове доповнення; виділити буфер за CMSG_LEN означає не долічити його",
                  size=12, color=MUTED))
    render(os.path.join(IMG, 'cmsg-layout.svg'), W, H, *g)


def fig_shared_offset_proof():
    """Два можливі результати досліду: спільна позиція проти власної."""
    W, H = 960, 430
    g = []

    g.append(text(480, 40, "той самий файл після трьох write", size=15, bold=True))

    # ── як воно є: позиція спільна ─────────────────────────────────────
    g.append(text(480, 78, "позиція спільна — так виходить насправді",
                  size=13, color=MUTED))
    g.append(fitbox(180, 92, 180, 56, "aaaa\nбатько", size=13, fill=GREEN))
    g.append(fitbox(360, 92, 180, 56, "bbbb\nдитина", size=13, fill=SAND))
    g.append(fitbox(540, 92, 180, 56, "cccc\nбатько", size=13, fill=GREEN))

    g.append(line(180, 172, 720, 172, color=MUTED, sw=1.2))
    for x, lab in ((180, "0"), (360, "4"), (540, "8"), (720, "12")):
        g.append(line(x, 166, x, 178, color=MUTED, sw=1.2))
        g.append(text(x, 198, lab, size=12, color=MUTED))

    # ── контрприклад: у дитини власна позиція ──────────────────────────
    g.append(text(480, 250, "якби дитина дістала власну позицію",
                  size=13, color=MUTED))
    g.append(fitbox(180, 264, 180, 56, "bbbb\nдитина", size=13, fill=WARN))
    g.append(fitbox(360, 264, 180, 56, "cccc\nбатько", size=13, fill=WARN))
    g.append(mtext(670, 286, ["літери батька затерті,",
                              "файл на 4 байти коротший"], size=12, color=MUTED))

    g.append(fitbox(170, 352, 620, 54,
                    "результати різні — тому запуск програми справді щось доводить",
                    size=12, fill=COLD))
    render(os.path.join(IMG, 'shared-offset-proof.svg'), W, H, *g)


if __name__ == '__main__':
    fig_what_travels()
    fig_message_lanes()
    fig_inflight_cycle()
    fig_cmsg_layout()
    fig_shared_offset_proof()
    print('ok')

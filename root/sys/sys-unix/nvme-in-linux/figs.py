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
PANEL = "#f8f9fb"


# ── 1. Пара черг: що лежить у пам'яті, що на шині ───────────────────────────
def fig_queue_pair():
    W, H = 1380, 800
    p = []

    hx, dx = 350, 1140          # осі колонок
    gap = 795                   # вісь підписів між колонками

    # панелі
    p.append(rect(50, 70, 600, 650, fill=PANEL, stroke=MUTED, sw=1.2))
    p.append(rect(960, 70, 360, 650, fill=PANEL, stroke=MUTED, sw=1.2))
    p.append(text(hx, 100, "пам'ять хоста (своя пара на ядро)", size=15, bold=True))
    p.append(text(dx, 100, "контролер NVMe", size=15, bold=True))

    f_sq, w_sq, h_sq = textbox(hx, 200,
                               ["черга подань SQ",
                                "1024 комірки × 64 Б",
                                "хвіст рухає хост"],
                               size=14, pad=15, fill=BLUE, stroke=LINE)
    p.append(f_sq)

    f_n1, w_n1, h_n1 = textbox(hx, 320,
                               ["① команду записано у вільну комірку —",
                                "звичайний запис у пам'ять, шини PCIe тут немає"],
                               size=13, pad=13, fill=GREY, stroke=MUTED, sw=1.2)
    p.append(f_n1)

    f_cq, w_cq, h_cq = textbox(hx, 480,
                               ["черга завершень CQ",
                                "1024 комірки × 16 Б",
                                "у кожній — фазовий біт",
                                "голову рухає хост"],
                               size=14, pad=15, fill=GREEN, stroke=LINE)
    p.append(f_cq)

    f_n2, w_n2, h_n2 = textbox(hx, 640,
                               ["⑥ свіжу комірку хост упізнає за фазовим бітом:",
                                "читання з власної пам'яті, а не з пристрою"],
                               size=13, pad=13, fill=GREY, stroke=MUTED, sw=1.2)
    p.append(f_n2)

    f_db, w_db, h_db = textbox(dx, 200,
                               ["регістри-дзвінки",
                                "хвіст SQ / голова CQ"],
                               size=14, pad=15, fill=WARM, stroke=LINE)
    p.append(f_db)

    f_ex, w_ex, h_ex = textbox(dx, 420,
                               ["④ виконавець:",
                                "забирає команди DMA,",
                                "працює з мікросхемами пам'яті"],
                               size=14, pad=15, fill=GREY, stroke=LINE)
    p.append(f_ex)

    f_ms, w_ms, h_ms = textbox(dx, 610,
                               ["MSI-X: своє переривання",
                                "на кожну чергу завершень"],
                               size=14, pad=15, fill=WARM, stroke=LINE)
    p.append(f_ms)

    def cross(y, to_right, lines):
        x1, x2 = (655, 955) if to_right else (955, 655)
        p.append(arrow(x1, y, x2, y))
        f, w, h = textbox(gap, y - 52, lines, size=13, pad=12,
                          fill="#ffffff", stroke=MUTED, sw=1.2)
        p.append(f)

    cross(160, True, ["② один запис у регістр:", "«мій хвіст тепер тут»"])
    cross(280, False, ["③ контролер сам читає", "команду з пам'яті хоста"])
    cross(455, False, ["⑤ завершення лягає в CQ,", "далі — переривання"])
    cross(640, True, ["⑦ дзвінок голови CQ:", "комірки знову вільні"])

    render(os.path.join(IMG, 'queue-pair.svg'), W, H, *p)


# ── 2. Підсистема, контролери, спільний простір імен ────────────────────────
def fig_subsystem_topology():
    W, H = 1320, 800
    p = []

    lx, rx, cx = 340, 980, 660

    f, w, h = textbox(cx, 95,
                      ["підсистема NVM   NQN nqn.2014-08.org.nvmexpress:uuid:9f2e…c1"],
                      size=14, pad=16, fill=WARM, stroke=LINE, bold=True)
    p.append(f)

    f_c0, w_c0, h_c0 = textbox(lx, 230,
                               ["контролер nvme0", "порт A / TCP 10.0.0.1",
                                "стан ANA: optimized"],
                               size=13, pad=14, fill=BLUE, stroke=LINE)
    f_c1, w_c1, h_c1 = textbox(rx, 230,
                               ["контролер nvme1", "порт B / TCP 10.0.0.2",
                                "стан ANA: non-optimized"],
                               size=13, pad=14, fill=BLUE, stroke=LINE)
    p.append(f_c0)
    p.append(f_c1)
    p.append(arrow(cx - 120, 95 + h / 2 + 6, lx, 230 - h_c0 / 2 - 6))
    p.append(arrow(cx + 120, 95 + h / 2 + 6, rx, 230 - h_c1 / 2 - 6))

    f_ns, w_ns, h_ns = textbox(cx, 400,
                               ["простір імен NSID 1",
                                "NGUID 0025385a…c4f2",
                                "спільний: видно з обох контролерів"],
                               size=14, pad=15, fill=GREEN, stroke=LINE)
    p.append(f_ns)
    p.append(arrow(lx, 230 + h_c0 / 2 + 6, cx - 150, 400 - h_ns / 2 - 6))
    p.append(arrow(rx, 230 + h_c1 / 2 + 6, cx + 150, 400 - h_ns / 2 - 6))

    f_p0, w_p0, h_p0 = textbox(lx, 570,
                               ["nvme0c0n1 — шлях",
                                "прихований: є в sysfs,",
                                "вузла в /dev немає"],
                               size=13, pad=14, fill=GREY, stroke=MUTED, sw=1.2)
    f_p1, w_p1, h_p1 = textbox(rx, 570,
                               ["nvme0c1n1 — шлях",
                                "прихований: є в sysfs,",
                                "вузла в /dev немає"],
                               size=13, pad=14, fill=GREY, stroke=MUTED, sw=1.2)
    p.append(f_p0)
    p.append(f_p1)
    p.append(line(lx, 400 + h_ns / 2 + 6, lx, 570 - h_p0 / 2 - 6,
                  color=MUTED, dash="6 5"))
    p.append(line(rx, 400 + h_ns / 2 + 6, rx, 570 - h_p1 / 2 - 6,
                  color=MUTED, dash="6 5"))

    f_hd, w_hd, h_hd = textbox(cx, 720,
                               ["/dev/nvme0n1 — головний диск:",
                                "єдиний, який бачать файлова система, lsblk і fstab"],
                               size=14, pad=16, fill=GREEN, stroke=LINE, bold=True)
    p.append(f_hd)
    p.append(arrow(lx, 570 + h_p0 / 2 + 6, cx - 190, 720 - h_hd / 2 - 6))
    p.append(arrow(rx, 570 + h_p1 / 2 + 6, cx + 190, 720 - h_hd / 2 - 6))

    render(os.path.join(IMG, 'subsystem-topology.svg'), W, H, *p)


# ── 3. Шлях запиту й підміна шляху після відмови ────────────────────────────
def fig_failover_path():
    W, H = 1340, 760
    p = []

    cx, lx, rx = 680, 380, 1010

    f_bio, w_b, h_b = textbox(cx, 90, ["bio від файлової системи"],
                              size=14, pad=15, fill=GREEN, stroke=LINE)
    p.append(f_bio)

    f_hd, w_h, h_h = textbox(cx, 200,
                             ["головний диск nvme0n1:",
                              "власної черги запитів немає"],
                             size=14, pad=15, fill=BLUE, stroke=LINE)
    p.append(f_hd)
    p.append(arrow(cx, 90 + h_b / 2 + 6, cx, 200 - h_h / 2 - 6))

    f_ch, w_c, h_c = textbox(cx, 350,
                             ["вибір шляху:",
                              "спершу стан ANA,",
                              "потім політика iopolicy"],
                             size=14, pad=15, fill=WARM, stroke=LINE)
    p.append(f_ch)
    p.append(arrow(cx, 200 + h_h / 2 + 6, cx, 350 - h_c / 2 - 6))

    f_a, w_a, h_a = textbox(lx, 510,
                            ["шлях через nvme0:",
                             "своя пара черг, свій blk-mq"],
                            size=13, pad=14, fill=GREY, stroke=LINE)
    f_b2, w_b2, h_b2 = textbox(rx, 510,
                               ["шлях через nvme1:",
                                "своя пара черг, свій blk-mq"],
                               size=13, pad=14, fill=GREY, stroke=LINE)
    p.append(f_a)
    p.append(f_b2)
    p.append(arrow(cx - w_c / 2, 350, lx + w_a / 2, 510 - h_a / 2 - 6))
    p.append(arrow(cx + w_c / 2, 350, rx - w_b2 / 2, 510 - h_b2 / 2 - 6))

    f_err, w_e, h_e = textbox(lx, 660,
                              ["помилка транспорту", "або скидання контролера"],
                              size=13, pad=14, fill=RED, stroke=POS)
    p.append(f_err)
    p.append(arrow(lx, 510 + h_a / 2 + 6, lx, 660 - h_e / 2 - 6))

    f_ok, w_o, h_o = textbox(rx, 660,
                             ["виконано; нагору повернувся", "звичайний успіх"],
                             size=13, pad=14, fill=GREEN, stroke=FIELD)
    p.append(f_ok)
    p.append(arrow(rx, 510 + h_b2 / 2 + 6, rx, 660 - h_o / 2 - 6))

    # повернення на голову й друга спроба
    p.append(line(lx - w_e / 2, 660, 90, 660, color=POS))
    p.append(line(90, 660, 90, 350, color=POS))
    p.append(arrow(90, 350, cx - w_c / 2 - 8, 350, color=POS))
    f_note, w_n, h_n = textbox(255, 268,
                               ["той самий bio —", "назад до голови", "й на інший шлях"],
                               size=13, pad=12, fill="#ffffff", stroke=POS, sw=1.2)
    p.append(f_note)

    render(os.path.join(IMG, 'failover-path.svg'), W, H, *p)


# ── 4. Що стирчить у /dev і /sys: імена вузлів у двох режимах ───────────────
def fig_node_names():
    W, H = 1400, 760
    p = []

    lx, rx = 365, 1045

    p.append(rect(40, 60, 650, 660, fill=PANEL, stroke=MUTED, sw=1.2))
    p.append(rect(710, 60, 650, 660, fill=PANEL, stroke=MUTED, sw=1.2))

    p.append(text(lx, 96, "nvme_core.multipath=Y   (типово)", size=16, bold=True))
    p.append(text(lx, 124, "перше число диска — номер ПІДСИСТЕМИ", size=13, color=MUTED))
    p.append(text(rx, 96, "nvme_core.multipath=N", size=16, bold=True))
    p.append(text(rx, 124, "перше число диска — номер КОНТРОЛЕРА", size=13, color=MUTED))

    # ── ліва колонка ──────────────────────────────────────────────────────
    f, w1, h1 = textbox(lx, 210,
                        ["/dev/nvme0     /dev/nvme1",
                         "символьні — КОНТРОЛЕРИ",
                         "адмінкоманди, reset, rescan"],
                        size=14, pad=14, fill=BLUE, stroke=LINE)
    p.append(f)

    f, w2, h2 = textbox(lx, 350,
                        ["/dev/nvme0n1",
                         "блоковий — ГОЛОВА простору імен",
                         "видно всім: fstab, lsblk, ФС"],
                        size=14, pad=14, fill=GREEN, stroke=FIELD)
    p.append(f)
    p.append(arrow(lx, 210 + h1 / 2 + 6, lx, 350 - h2 / 2 - 6))

    f, w3, h3 = textbox(lx, 490,
                        ["/sys/block/nvme0c0n1",
                         "/sys/block/nvme0c1n1",
                         "ШЛЯХИ — приховані:",
                         "вузлів у /dev не мають"],
                        size=14, pad=14, fill=GREY, stroke=MUTED, sw=1.2)
    p.append(f)
    p.append(arrow(lx, 490 - h3 / 2 - 6, lx, 350 + h2 / 2 + 6, color=MUTED))

    f, w4, h4 = textbox(lx, 640,
                        ["/dev/ng0n1",
                         "символьний двійник голови:",
                         "команди повз блоковий рівень"],
                        size=14, pad=14, fill=WARM, stroke=LINE)
    p.append(f)

    # ── права колонка ─────────────────────────────────────────────────────
    f, q1, g1 = textbox(rx, 210,
                        ["/dev/nvme0     /dev/nvme1",
                         "символьні — КОНТРОЛЕРИ"],
                        size=14, pad=14, fill=BLUE, stroke=LINE)
    p.append(f)

    f, q2, g2 = textbox(rx, 360,
                        ["/dev/nvme0n1     /dev/nvme1n1",
                         "ДВА блокові диски",
                         "на ОДИН простір імен"],
                        size=14, pad=14, fill=RED, stroke=POS)
    p.append(f)
    p.append(arrow(rx, 210 + g1 / 2 + 6, rx, 360 - g2 / 2 - 6))

    f, q3, g3 = textbox(rx, 500,
                        ["/dev/ng0n1     /dev/ng1n1",
                         "по символьному на кожен шлях"],
                        size=14, pad=14, fill=WARM, stroke=LINE)
    p.append(f)

    f, q4, g4 = textbox(rx, 640,
                        ["зводити докупи мусить",
                         "device mapper — власною чергою",
                         "поверх обох дисків"],
                        size=14, pad=14, fill=GREY, stroke=MUTED, sw=1.2)
    p.append(f)

    render(os.path.join(IMG, 'node-names.svg'), W, H, *p)


# ── 5. Один ioctl — дві різні відповіді ─────────────────────────────────────
def fig_ioctl_two_answers():
    W, H = 1460, 880
    p = []

    ux, kx, dx = 270, 770, 1240

    p.append(text(ux, 80, "процес", size=15, bold=True))
    p.append(text(kx, 80, "ядро", size=15, bold=True))
    p.append(text(dx, 80, "контролер", size=15, bold=True))

    f_cmd, w_cmd, h_cmd = textbox(ux, 190,
                                  ["struct nvme_passthru_cmd — 72 Б",
                                   "opcode 0x06 · nsid · cdw10 = CNS",
                                   "addr · data_len = 4096",
                                   "result — сюди ляже CDW0"],
                                  size=13, pad=14, fill=BLUE, stroke=LINE)
    p.append(f_cmd)

    f_krn, w_krn, h_krn = textbox(kx, 190,
                                  ["перевірка прав,",
                                   "копія 72 Б із процесу,",
                                   "з неї ядро складає 64 Б команди"],
                                  size=13, pad=14, fill=GREY, stroke=LINE)
    p.append(f_krn)

    f_ctl, w_ctl, h_ctl = textbox(dx, 190,
                                  ["адміністративна", "пара черг (номер 0)"],
                                  size=13, pad=14, fill=WARM, stroke=LINE)
    p.append(f_ctl)

    p.append(arrow(ux + w_cmd / 2 + 8, 190, kx - w_krn / 2 - 8, 190))
    p.append(arrow(kx + w_krn / 2 + 8, 190, dx - w_ctl / 2 - 8, 190))

    f_buf, w_buf, h_buf = textbox(ux, 380,
                                  ["буфер 4096 Б,", "вирівняний на сторінку"],
                                  size=13, pad=14, fill=GREEN, stroke=LINE)
    p.append(f_buf)
    p.append(line(ux, 190 + h_cmd / 2 + 6, ux, 380 - h_buf / 2 - 6,
                  color=MUTED, dash="6 5"))

    f_map, w_map, h_map = textbox(kx, 380,
                                  ["сторінки буфера відображено",
                                   "для DMA — а якщо адреса",
                                   "не вирівняна, зроблено копію"],
                                  size=13, pad=14, fill=GREY, stroke=MUTED, sw=1.2)
    p.append(f_map)
    p.append(arrow(ux + w_buf / 2 + 8, 380, kx - w_map / 2 - 8, 380))
    p.append(arrow(kx + w_map / 2 + 8, 380, dx + 40, 380))
    p.append(text(dx + 40, 420, "відповідь пише сам пристрій", size=12, color=MUTED))

    f_cqe, w_cqe, h_cqe = textbox(dx, 610,
                                  ["комірка завершення, 16 Б:",
                                   "статус (15 бітів) і CDW0"],
                                  size=13, pad=14, fill=WARM, stroke=LINE)
    p.append(f_cqe)
    p.append(line(dx, 440, dx, 610 - h_cqe / 2 - 6, color=MUTED, dash="6 5"))

    f_spl, w_spl, h_spl = textbox(kx, 610,
                                  ["ядро розводить відповідь", "на два різні канали"],
                                  size=13, pad=14, fill=GREY, stroke=LINE)
    p.append(f_spl)
    p.append(arrow(dx - w_cqe / 2 - 8, 610, kx + w_spl / 2 + 8, 610))

    f_st, w_st, h_st = textbox(ux, 530,
                               ["що повернув ioctl — це СТАТУС:",
                                "0 — виконано · > 0 — SCT/SC",
                                "−1 і errno — до пристрою не дійшло"],
                               size=13, pad=14, fill=RED, stroke=POS)
    p.append(f_st)

    f_rs, w_rs, h_rs = textbox(ux, 750,
                               ["cmd.result — це CDW0:",
                                "число, своє для кожної команди,",
                                "ознакою успіху воно не є"],
                               size=13, pad=14, fill=BLUE, stroke=NEG)
    p.append(f_rs)

    p.append(arrow(kx - w_spl / 2 - 8, 588, ux + w_st / 2 + 8, 545))
    p.append(arrow(kx - w_spl / 2 - 8, 632, ux + w_rs / 2 + 8, 735))

    render(os.path.join(IMG, 'ioctl-two-answers.svg'), W, H, *p)


# ── 6. Розкладка сторінки журналу ANA ───────────────────────────────────────
def fig_ana_log_layout():
    W, H = 1420, 660
    p = []

    p.append(text(710, 70, "сторінка журналу ANA (LID 0x0C): довжину рахують наперед",
                  size=16, bold=True))

    y, h = 120, 92
    cells = [(70, 250, ["заголовок", "16 Б"], WARM),
             (330, 330, ["дескриптор групи", "32 Б"], BLUE),
             (670, 250, ["список NSID", "4 Б × NNSIDS"], GREEN),
             (930, 330, ["дескриптор групи", "32 Б"], BLUE),
             (1270, 80, ["…"], GREY)]
    for x, w, s, fill in cells:
        p.append(fitbox(x, y, w, h, s, size=14, pad=10, fill=fill, stroke=LINE))

    for x, lab in ((70, "байт 0"), (330, "байт 16"), (670, "байт 48"),
                   (930, "байт 48 + 4·NNSIDS")):
        p.append(text(x + 4, y + h + 26, lab, size=12, color=MUTED, anchor="start"))

    y2, h2 = 350, 82
    p.append(line(340, y + h + 42, 200, y2 - 18, color=MUTED, dash="5 4"))
    p.append(line(650, y + h + 42, 1230, y2 - 18, color=MUTED, dash="5 4"))

    fields = [(190, 235, ["ANAGRPID", "байти 0:3"]),
              (445, 235, ["NNSIDS", "байти 4:7"]),
              (700, 245, ["лічильник змін", "байти 8:15"]),
              (965, 265, ["стан ANA — 4 біти", "байт 16"])]
    for x, w, s in fields:
        p.append(fitbox(x, y2, w, h2, s, size=13, pad=10, fill=PANEL,
                        stroke=MUTED, sw=1.2))
    p.append(fitbox(1250, y2, 110, h2, ["решта —", "нулі"], size=12, pad=8,
                    fill=GREY, stroke=MUTED, sw=1.2))

    f, w_st, h_st = textbox(710, 510,
                            ["стан: 1 optimized · 2 non-optimized · 3 inaccessible · "
                             "4 persistent-loss · 0xF change"],
                            size=13, pad=13, fill="#ffffff", stroke=LINE)
    p.append(f)

    f, w_sz, h_sz = textbox(710, 600,
                            ["довжина = 16 + NANAGRPID × 32 + MNAN × 4; "
                             "обидва числа беруть з Identify Controller"],
                            size=13, pad=13, fill=GREEN, stroke=FIELD)
    p.append(f)

    render(os.path.join(IMG, 'ana-log-layout.svg'), W, H, *p)


fig_queue_pair()
fig_subsystem_topology()
fig_failover_path()
fig_node_names()
fig_ioctl_two_answers()
fig_ana_log_layout()
print("ok")

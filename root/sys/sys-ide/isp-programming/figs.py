# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GOLD = "#a9791f"
PURPLE = "#6c3483"


def fig_hardware_interface_timing():
    W, H = 840, 530
    p = []

    # ── Загальні панелі для програматора та цільового МК ────────────────────
    prog_x, prog_y, prog_w, prog_h = 30, 40, 200, 180
    p.append(rect(prog_x, prog_y, prog_w, prog_h, fill="#f4f6f8", stroke=LINE, sw=2))
    p.append(text(prog_x + prog_w / 2, prog_y + 24, "Програматор ISP", size=13, bold=True, color=INK))
    p.append(text(prog_x + prog_w / 2, prog_y + 44, "(USBasp / STK500 / MCU)", size=10, bold=False, color=MUTED))

    # Виводи програматора
    targ_x, targ_y, targ_w, targ_h = 600, 40, 210, 180
    p.append(rect(targ_x, targ_y, targ_w, targ_h, fill="#fbfcff", stroke=INK, sw=2))
    p.append(text(targ_x + targ_w / 2, targ_y + 24, "Цільовий мікроконтролер", size=13, bold=True, color=INK))
    p.append(text(targ_x + targ_w / 2, targ_y + 44, "(AVR / ATmega / ATtiny)", size=10, bold=False, color=MUTED))

    # Лінії зв'язку
    lines_info = [
        (prog_y + 45, "Живлення VCC", POS, True),
        (prog_y + 75, "MOSI (Master Out -> Slave In)", INK, False),
        (prog_y + 105, "MISO (Master In <- Slave Out)", FIELD, False),
        (prog_y + 135, "SCK (Serial Clock: f_ISP <= f_CPU / 4)", NEG, False),
        (prog_y + 165, "RESET (Утримання в 0V блокує CPU)", GOLD, False),
    ]

    for y_pos, label_text, col, is_pwr in lines_info:
        # малюємо лінії двома сегментами, щоб не перетинати центральний textbox (x=415, w~210)
        tb_box, tb_w, tb_h = textbox(415, y_pos, label_text, size=10, pad=4, fill="#ffffff", stroke=col, sw=1)
        
        if is_pwr:
            p.append(line(prog_x + prog_w, y_pos, 415 - tb_w/2, y_pos, color=col, sw=2.0))
            p.append(line(415 + tb_w/2, y_pos, targ_x, y_pos, color=col, sw=2.0))
        elif "MISO" in label_text:
            p.append(arrow(415 - tb_w/2, y_pos, prog_x + prog_w + 2, y_pos, color=col, sw=2.0))
            p.append(line(targ_x, y_pos, 415 + tb_w/2, y_pos, color=col, sw=2.0))
        else:
            p.append(line(prog_x + prog_w, y_pos, 415 - tb_w/2, y_pos, color=col, sw=2.0))
            p.append(arrow(415 + tb_w/2, y_pos, targ_x - 2, y_pos, color=col, sw=2.0))
        
        p.append(tb_box)

    # Внутрішні блоки цільового чіпа
    p.append(rect(targ_x + 15, targ_y + 60, targ_w - 30, 45, fill="#fdedec", stroke=POS, sw=1.2))
    p.append(text(targ_x + targ_w / 2, targ_y + 78, "Ядро CPU (Halted)", size=10, bold=True, color=POS))
    p.append(text(targ_x + targ_w / 2, targ_y + 94, "Виводи в Z-стані", size=9.5, color=MUTED))

    p.append(rect(targ_x + 15, targ_y + 115, targ_w - 30, 50, fill="#eafaf1", stroke=FIELD, sw=1.2))
    p.append(text(targ_x + targ_w / 2, targ_y + 133, "SPI/ISP Flash Controller", size=10, bold=True, color=FIELD))
    p.append(text(targ_x + targ_w / 2, targ_y + 150, "Прямий доступ до пам'яті", size=9.5, color=MUTED))

    # ── Нижня часова діаграма входження в режим ISP ──────────────────────────
    dia_y = 250
    p.append(rect(30, dia_y, 780, 255, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(420, dia_y + 22, "Часова діаграма входу в режим програмування та тактування SPI", size=12, bold=True, color=INK))

    # Сигнал VCC
    sig_vcc_y = dia_y + 55
    p.append(text(80, sig_vcc_y + 4, "VCC", size=11, bold=True, color=POS, anchor="end"))
    p.append(line(95, sig_vcc_y, 140, sig_vcc_y, color=POS, sw=2))
    p.append(line(140, sig_vcc_y, 160, sig_vcc_y - 15, color=POS, sw=2))
    p.append(line(160, sig_vcc_y - 15, 770, sig_vcc_y - 15, color=POS, sw=2))

    # Сигнал RESET
    sig_rst_y = dia_y + 95
    p.append(text(80, sig_rst_y + 4, "RESET", size=11, bold=True, color=GOLD, anchor="end"))
    p.append(line(95, sig_rst_y - 15, 180, sig_rst_y - 15, color=GOLD, sw=2))
    p.append(line(180, sig_rst_y - 15, 195, sig_rst_y, color=GOLD, sw=2))
    p.append(line(195, sig_rst_y, 770, sig_rst_y, color=GOLD, sw=2))
    p.append(textbox(280, sig_rst_y + 22, "t_RST >= 20 мс (активація апаратного скидання)", size=9.5, pad=3, fill="#fef9e7", stroke=GOLD, sw=1)[0])

    # Сигнал SCK
    sig_sck_y = dia_y + 155
    p.append(text(80, sig_sck_y + 4, "SCK", size=11, bold=True, color=NEG, anchor="end"))
    p.append(line(95, sig_sck_y, 350, sig_sck_y, color=NEG, sw=1.8))
    # Серія тактових імпульсів
    cur_x = 350
    period = 24
    for i in range(16):
        p.append(line(cur_x, sig_sck_y, cur_x, sig_sck_y - 18, color=NEG, sw=1.8))
        p.append(line(cur_x, sig_sck_y - 18, cur_x + period/2, sig_sck_y - 18, color=NEG, sw=1.8))
        p.append(line(cur_x + period/2, sig_sck_y - 18, cur_x + period/2, sig_sck_y, color=NEG, sw=1.8))
        p.append(line(cur_x + period/2, sig_sck_y, cur_x + period, sig_sck_y, color=NEG, sw=1.8))
        cur_x += period

    p.append(textbox(540, sig_sck_y + 20, "T_SCK > 4 * T_CPU (обмеження f_ISP < f_CPU / 4)", size=9.5, pad=3, fill="#eaf0fd", stroke=NEG, sw=1)[0])

    # Сигнал MOSI
    sig_mosi_y = dia_y + 205
    p.append(text(80, sig_mosi_y + 4, "MOSI", size=11, bold=True, color=INK, anchor="end"))
    p.append(line(95, sig_mosi_y, 350, sig_mosi_y, color=MUTED, sw=1.5, dash="4,3"))
    # Байти команди 0xAC, 0x53, 0x00, 0x00
    p.append(rect(350, sig_mosi_y - 12, 90, 22, fill="#eaecee", stroke=INK, sw=1.2))
    p.append(text(395, sig_mosi_y + 3, "0xAC (Cmd)", size=9.5, bold=True, color=INK))

    p.append(rect(445, sig_mosi_y - 12, 90, 22, fill="#eaecee", stroke=INK, sw=1.2))
    p.append(text(490, sig_mosi_y + 3, "0x53 (Key)", size=9.5, bold=True, color=INK))

    p.append(rect(540, sig_mosi_y - 12, 90, 22, fill="#eaecee", stroke=INK, sw=1.2))
    p.append(text(585, sig_mosi_y + 3, "0x00 (Addr)", size=9.5, bold=True, color=INK))

    p.append(rect(635, sig_mosi_y - 12, 90, 22, fill="#eaecee", stroke=INK, sw=1.2))
    p.append(text(680, sig_mosi_y + 3, "0x00 (Null)", size=9.5, bold=True, color=INK))

    # Сигнал MISO (луна)
    sig_miso_y = dia_y + 235
    p.append(text(80, sig_miso_y + 4, "MISO", size=11, bold=True, color=FIELD, anchor="end"))
    p.append(line(95, sig_miso_y, 540, sig_miso_y, color=MUTED, sw=1.5, dash="4,3"))
    p.append(rect(540, sig_miso_y - 10, 90, 18, fill="#d5f5e3", stroke=FIELD, sw=1.2))
    p.append(text(585, sig_miso_y + 3, "Echo: 0x53", size=9.5, bold=True, color=FIELD))
    p.append(line(630, sig_miso_y, 770, sig_miso_y, color=MUTED, sw=1.5, dash="4,3"))

    render(os.path.join(OUT, "isp-hardware-interface-timing.svg"), W, H, *p,
           title="Фізичні лінії та часові діаграми апаратного інтерфейсу ISP")


def fig_page_programming_fsm():
    W, H = 860, 520
    p = []

    p.append(rect(20, 20, 820, 480, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(430, 48, "Скінченний автомат процедури посторінкового програмування Flash (ISP)", size=13, bold=True, color=INK))

    # Стан 1: RESET & Sync
    s1, s1w, s1h = textbox(115, 120, "1. Подача RESET\nта синхронізація\n(Cmd: 0xAC 0x53 0x00 0x00)", size=10, bold=True,
                           fill="#fef9e7", stroke=GOLD, sw=1.8, min_w=160)
    p.append(s1)

    # Перехід 1 -> 2
    p.append(arrow(115 + s1w/2, 120, 275 - 80, 120, color=INK, sw=1.8))
    p.append(text(195, 108, "Echo == 0x53", size=9.5, bold=True, color=FIELD))

    # Стан 2: Read Signature
    s2, s2w, s2h = textbox(355, 120, "2. Зчитування\nсигнатури кристала\n(Cmd: 0x30 0x00 [0..2])", size=10, bold=True,
                           fill="#eaf0fd", stroke=NEG, sw=1.8, min_w=160)
    p.append(s2)

    # Перехід 2 -> 3
    p.append(arrow(355 + s2w/2, 120, 515 - 80, 120, color=INK, sw=1.8))
    p.append(text(435, 108, "ID валідний", size=9.5, bold=True, color=FIELD))

    # Стан 3: Chip Erase
    s3, s3w, s3h = textbox(595, 120, "3. Повне стирання\n(Chip Erase)\n(Cmd: 0xAC 0x80 0x00 0x00)", size=10, bold=True,
                           fill="#fdedec", stroke=POS, sw=1.8, min_w=160)
    p.append(s3)

    # Перехід 3 -> 4 (вниз і вліво до циклу сторінок)
    tb_erase, tb_erase_w, tb_erase_h = textbox(750, 180, "Пауза t_WD_ERASE\n(Flash = 0xFF)", size=9.5, pad=4, fill="#ffffff", stroke=MUTED, sw=1)
    p.append(arrow(595 + s3w/2, 120, 750, 120, color=INK, sw=1.8))
    p.append(line(750, 120, 750, 180 - tb_erase_h/2, color=INK, sw=1.8))
    p.append(tb_erase)
    p.append(line(750, 180 + tb_erase_h/2, 750, 240, color=INK, sw=1.8))
    p.append(arrow(750, 240, 690, 240, color=INK, sw=1.8))

    # ── Контур циклу посторінкового запису ──────────────────────────────────
    p.append(rect(40, 200, 650, 170, fill="#f4f6f8", stroke="#a6acaf", sw=1.5, rx=8))
    p.append(text(170, 222, "Цикл запису сторінок (Page Programming Loop)", size=11, bold=True, color=INK))

    # Стан 4: Load Page Buffer
    s4, s4w, s4h = textbox(160, 285, "4. Завантаження буфера\nLow: 0x40 [Addr] [DataL]\nHigh: 0x48 [Addr] [DataH]", size=10, bold=True,
                           fill="#ffffff", stroke=INK, sw=1.5, min_w=180)
    p.append(s4)

    # Перехід 4 -> 5
    p.append(arrow(160 + s4w/2, 285, 380 - 95, 285, color=INK, sw=1.8))
    p.append(text(270, 272, "Буфер заповнено", size=9.5, bold=True, color=INK))

    # Стан 5: Flash Page Write
    s5, s5w, s5h = textbox(475, 285, "5. Фіксація сторінки\nу фізичний Flash\n(Cmd: 0x4C [PageAddr])", size=10, bold=True,
                           fill="#fdedec", stroke=POS, sw=1.5, min_w=180)
    p.append(s5)

    # Стан 6: Poll Ready / Busy
    s6, s6w, s6h = textbox(475, 430, "6. Опитування готовності\n(Poll Ready / 0xF0 або Data Polling)\nЗатримка t_WD_FLASH (4.5 мс)", size=10, bold=True,
                           fill="#eafaf1", stroke=FIELD, sw=1.5, min_w=240)
    p.append(s6)

    # Перехід 5 -> 6 (вниз)
    p.append(arrow(475, 285 + s5h/2, 475, 430 - s6h/2, color=INK, sw=1.8))
    p.append(text(535, 360, "Запуск HV Pump", size=9.5, color=MUTED))

    # Петля: Ще сторінки? (із стану 6 назад у стан 4)
    tb_loop, tb_loop_w, tb_loop_h = textbox(290, 430, "Наступна сторінка Flash", size=9.5, pad=4, fill="#ffffff", stroke=INK, sw=1)
    p.append(line(475 - s6w/2, 430, 290 + tb_loop_w/2, 430, color=INK, sw=1.8))
    p.append(tb_loop)
    p.append(line(290 - tb_loop_w/2, 430, 160, 430, color=INK, sw=1.8))
    p.append(arrow(160, 430, 160, 285 + s4h/2, color=INK, sw=1.8))

    # Вихід із циклу: Усі сторінки записано -> Стан 7: Lock Bits & Release Reset
    s7, s7w, s7h = textbox(740, 430, "7. Запис Lock Bits\nта зняття RESET\n(Запуск нової прошивки)", size=10, bold=True,
                           fill="#fef9e7", stroke=GOLD, sw=1.8, min_w=160)
    p.append(s7)

    # Перехід 6 -> 7
    p.append(arrow(475 + s6w/2, 430, 740 - s7w/2, 430, color=INK, sw=1.8))
    p.append(text(610, 416, "Усі сторінки OK", size=9.5, bold=True, color=FIELD))

    render(os.path.join(OUT, "isp-page-programming-fsm.svg"), W, H, *p,
           title="Скінченний автомат посторінкового програмування Flash і EEPROM")


if __name__ == "__main__":
    fig_hardware_interface_timing()
    fig_page_programming_fsm()
    print("Figures generated successfully.")

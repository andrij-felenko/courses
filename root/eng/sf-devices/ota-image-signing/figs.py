#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми ota-image-signing (Підписаний образ і захист від відкату)."""

import os
import sys

# Шлях до спільних помічників svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_chain_of_trust():
    """Ланцюг довіри від апаратного eFuse/ROM до прошивки застосунку."""
    w, h = 920, 480
    frags = []

    # Рівні апаратного ланцюга
    # 1. Залізо / Апаратний корінь
    b1 = rect(40, 60, 220, 320, fill="#fdf2f0", stroke=POS, sw=2, rx=8)
    t1 = text(150, 90, "Апаратний корінь (RoT)", size=15, color=POS, bold=True)
    t1_sub = mtext(150, 125, ["Масковане ROM", "OTP eFuse (хеш ключа)", "Апаратні криптоакселератори"], size=12, color=INK, lh=1.4)
    frags.extend([b1, t1, t1_sub])

    # Стрілка 1
    a1 = arrow(260, 220, 350, 220, color=POS, sw=2.5)
    lbl1 = fitbox(265, 175, 80, 36, "ROM валідує\nMCUboot", size=10, fill="#ffffff", stroke=POS, bold=True)
    frags.extend([a1, lbl1])

    # 2. Завантажувач 2-го рівня (MCUboot)
    b2 = rect(350, 60, 220, 320, fill="#f0f4fd", stroke=NEG, sw=2, rx=8)
    t2 = text(460, 90, "Завантажувач (MCUboot)", size=15, color=NEG, bold=True)
    t2_sub = mtext(460, 125, ["Вбудований відкритий ключ", "Перевірка SHA-256/підпису", "Звірка лічильника eFuse", "Керування A/B слотами"], size=12, color=INK, lh=1.4)
    frags.extend([b2, t2, t2_sub])

    # Стрілка 2
    a2 = arrow(570, 220, 660, 220, color=NEG, sw=2.5)
    lbl2 = fitbox(575, 175, 80, 36, "MCUboot валідує\nпідпис App", size=10, fill="#ffffff", stroke=NEG, bold=True)
    frags.extend([a2, lbl2])

    # 3. Образ застосунку
    b3 = rect(660, 60, 220, 320, fill="#f4fbf6", stroke=FIELD, sw=2, rx=8)
    t3 = text(770, 90, "Образ застосунку (App)", size=15, color=FIELD, bold=True)
    t3_sub = mtext(770, 125, ["Заголовок (Header)", "Виконуваний бінарний код", "Захищені TLV (Anti-Rollback)", "TLV підпису (ECDSA/Ed25519)"], size=12, color=INK, lh=1.4)
    frags.extend([b3, t3, t3_sub])

    # Нижній блок висновку
    summary = fitbox(40, 400, 840, 42, "Незмінний апаратний якір (eFuse Hash) → Безпечний завантажувач → Перевірений застосунок", size=13, fill="#ffffff", stroke=LINE, bold=True)
    frags.append(summary)

    render(os.path.join(OUT, "chain-of-trust.svg"), w, h, *frags, title="Апаратний ланцюг довіри (Chain of Trust)")


def fig_mcuboot_layout():
    """Структура образу прошивки MCUboot (Header, Code, Protected TLV, TLV Trailer)."""
    w, h = 900, 520
    frags = []

    # Заголовок образу (32 байти)
    h_box = rect(50, 70, 800, 85, fill="#eaf0fd", stroke=NEG, sw=2, rx=6)
    h_title = text(450, 95, "Заголовок образу — MCUboot Image Header (32 байти)", size=15, color=NEG, bold=True)
    h_fields = mtext(450, 122, [
        "Magic (0x96f3b83d)  |  Load Addr (4B)  |  Hdr Size (2B)  |  Protected TLV Size (2B)",
        "Image Size (4B)     |  Flags (4B)      |  Version (Major.Minor.Revision.Build, 8B)"
    ], size=12, color=INK, lh=1.3)
    frags.extend([h_box, h_title, h_fields])

    # Тіло прошивки (Вектори + Код)
    payload_box = rect(50, 170, 800, 100, fill="#f4f6f8", stroke=LINE, sw=2, rx=6)
    p_title = text(450, 198, "Тіло прошивки — Executable Payload", size=15, color=INK, bold=True)
    p_desc = mtext(450, 228, [
        "Векторна таблиця переривань (Vector Table: Initial SP, Reset_Handler)",
        "Секції .text (код програми), .rodata (константи), .data (початкові значення змінних)"
    ], size=12, color=MUTED, lh=1.3)
    frags.extend([payload_box, p_title, p_desc])

    # Захищені TLV (Protected TLVs)
    ptlv_box = rect(50, 285, 800, 90, fill="#fef6e7", stroke="#d97706", sw=2, rx=6)
    ptlv_title = text(450, 310, "Захищені дескриптори — Protected TLV Area (Включаються в підпис)", size=14, color="#b45309", bold=True)
    ptlv_desc = mtext(450, 338, [
        "TLV Header (Magic 0x6908, Length)  |  TAG_SEC_CNT (Апаратний лічильник захисту від відкату, 4B)",
        "TAG_BOOT_RECORD (CBOR-запис вимірюваного завантаження)"
    ], size=12, color=INK, lh=1.3)
    frags.extend([ptlv_box, ptlv_title, ptlv_desc])

    # Трейлер TLV (TLV Trailer)
    tlv_box = rect(50, 390, 800, 95, fill="#fdecea", stroke=POS, sw=2, rx=6)
    tlv_title = text(450, 415, "Трейлер підпису — Non-Protected TLV Trailer", size=14, color=POS, bold=True)
    tlv_desc = mtext(450, 445, [
        "TLV Header (Magic 0x6907, Length)  |  TAG_SHA256 (32B дайджест: Header + Payload + Protected TLV)",
        "TAG_SIGNATURE (Криптографічний підпис: ECDSA secp256r1 64B або Ed25519 64B)"
    ], size=12, color=INK, lh=1.3)
    frags.extend([tlv_box, tlv_title, tlv_desc])

    render(os.path.join(OUT, "mcuboot-image-layout.svg"), w, h, *frags, title="Анатомія підписаного двійкового образу MCUboot")


def fig_anti_rollback():
    """Механізм захисту від відкату (Anti-Rollback) через апаратні OTP eFuses."""
    w, h = 900, 500
    frags = []

    # Ліва колонка: Легітимне оновлення v1 -> v2
    b_ok = rect(40, 60, 390, 330, fill="#f4fbf6", stroke=FIELD, sw=2, rx=8)
    t_ok_title = text(235, 90, "Легітимне оновлення (Успіх)", size=16, color=FIELD, bold=True)
    step1 = fitbox(60, 115, 350, 55, "1. Образ v2 (Sec Counter = 2) залито в слот\nПідпис дійсний (ECDSA / Ed25519 OK)", size=11, fill="#ffffff", stroke=LINE)
    step2 = fitbox(60, 185, 350, 55, "2. MCUboot читає eFuse (NV Counter = 1)\nПеревірка: Image Sec (2) ≥ eFuse (1) → УСПІХ", size=11, fill="#ffffff", stroke=FIELD, bold=True)
    step3 = fitbox(60, 255, 350, 65, "3. Самотестування пройдено вдало!\nАпаратне спалювання eFuse: NV Counter = 2\n(Одноразовий необоротний запис 0b0011)", size=11, fill="#ffffff", stroke=LINE)
    frags.extend([b_ok, t_ok_title, step1, step2, step3])

    # Права колонка: Спроба відкату (Атака)
    b_atk = rect(470, 60, 390, 330, fill="#fdecea", stroke=POS, sw=2, rx=8)
    t_atk_title = text(665, 90, "Спроба Downgrade-атаки (Блокування)", size=16, color=POS, bold=True)
    a_step1 = fitbox(490, 115, 350, 55, "1. Зловмисник заливає стару прошивку v1\n(Має легітимний підпис виробника!)", size=11, fill="#ffffff", stroke=LINE)
    a_step2 = fitbox(490, 185, 350, 55, "2. MCUboot читає образ (Sec Counter = 1)\nта апаратний eFuse (NV Counter = 2)", size=11, fill="#ffffff", stroke=LINE)
    a_step3 = fitbox(490, 255, 350, 65, "3. Перевірка: Image Sec (1) < eFuse (2)!\nВІДМОВА ЗАВАНТАЖЕННЯ (Downgrade Rejected)\nЗапуск блокується, перехід у Safe Recovery", size=11, fill="#ffffff", stroke=POS, bold=True)
    frags.extend([b_atk, t_atk_title, a_step1, a_step2, a_step3])

    # Підсумок внизу
    ft = fitbox(40, 415, 820, 42, "Криптопідпис гарантує АВТОРСТВО, а апаратний eFuse гарантує СВІЖІСТЬ версії", size=13, fill="#ffffff", stroke=LINE, bold=True)
    frags.append(ft)

    render(os.path.join(OUT, "anti-rollback-efuse.svg"), w, h, *frags, title="Захист від відкату версій за допомогою eFuse лічильника")


def fig_dual_slot_swap():
    """Двоетапне A/B тестування образу та автоматичний відкат."""
    w, h = 920, 460
    frags = []

    # Етап 1: Запис у вторинний слот
    s1 = fitbox(40, 70, 250, 130, "1. Завантаження OTA\nНовий підписаний образ\nзаписується у Slot 1\n(Вторинний / Пасивний).\nSlot 0 працює в штатному режимі.", size=11, fill="#f4f6f8", stroke=LINE)
    # Етап 2: Валідація та Swap
    s2 = fitbox(335, 70, 250, 130, "2. Перевірка підпису\nMCUboot перевіряє хеш,\nкриптографічний підпис\nта Sec Counter у Slot 1.\nВиконується swap у Slot 0.", size=11, fill="#eaf0fd", stroke=NEG, bold=True)
    # Етап 3: Тестовий старт
    s3 = fitbox(630, 70, 250, 130, "3. Тестовий запуск (Trial)\nЗапуск у стані TESTING.\nАктивація сторожового\nтаймера (Hardware Watchdog).\nОчікування самотесту.", size=11, fill="#fef6e7", stroke="#d97706")
    frags.extend([s1, s2, s3])

    arr1 = arrow(290, 135, 335, 135, color=LINE, sw=2)
    arr2 = arrow(585, 135, 630, 135, color=LINE, sw=2)
    frags.extend([arr1, arr2])

    # Розгалуження результатів
    # Гілка успіху
    ok_box = fitbox(500, 260, 380, 120, "УСПІХ: Самотест пройдено!\nПрошивка викликає mcuboot_mark_confirmed()\nОбраз закріплюється назавжди (PERMANENT).\nОновлюється eFuse Counter при потребі.", size=11, fill="#f4fbf6", stroke=FIELD, bold=True)
    arr_ok = arrow(755, 200, 755, 260, color=FIELD, sw=2.5)
    frags.extend([ok_box, arr_ok])

    # Гілка аварії / невдачі
    fail_box = fitbox(40, 260, 380, 120, "АВАРІЯ: Падіння коду або спрацювання Watchdog!\nMCUboot фіксує незавершений стан тесту.\nАвтоматичний зворотний SWAP у Slot 0.\nПовернення попередньої робочої версії!", size=11, fill="#fdecea", stroke=POS, bold=True)
    arr_fail = arrow(630, 160, 420, 290, color=POS, sw=2.5)
    frags.extend([fail_box, arr_fail])

    render(os.path.join(OUT, "dual-slot-swap.svg"), w, h, *frags, title="Життєвий цикл оновлення: A/B Swap, пробний запуск та автоматичний відкат")


def main():
    fig_chain_of_trust()
    fig_mcuboot_layout()
    fig_anti_rollback()
    fig_dual_slot_swap()
    print("Всі 4 фігури успішно згенеровано у", OUT)


if __name__ == "__main__":
    main()

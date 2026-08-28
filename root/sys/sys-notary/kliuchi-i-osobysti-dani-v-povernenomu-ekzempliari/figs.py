#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор векторних діаграм для теми «Ключі й особисті дані в поверненому екземплярі»."""

import sys
import os

# scripts/ лежить 4 рівні вгору від кореня теми: root/sys/sys-notary/<topic>/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def fig_crypto_shredding(path):
    """Схема архітектури криптографічного стирання (Crypto-Shredding) та нуліфікації ключів."""
    w, h = 940, 530
    frags = []

    # Заголовок блоків
    frags.append(text(235, 45, "Апаратний корінь довіри (Root of Trust)", size=15, bold=True, color=INK))
    frags.append(text(705, 45, "Енергонезалежна Flash-пам'ять (NAND / eMMC)", size=15, bold=True, color=INK))

    # Ліва колонка: Secure Element / TPM / eFuse (зовнішня рамка без заливки, щоб уникнути конфлікту solid_boxes)
    frags.append(rect(40, 65, 390, 435, fill="none", stroke="#64748b", sw=1.5, rx=8))
    
    b1, _, _ = textbox(235, 110, "Secure Element / TPM 2.0 / BBRAM\nАпаратно ізольоване захищене сховище", size=13, bold=True, fill="#e2e8f0", stroke="#475569", min_w=350)
    frags.append(b1)

    b2, _, _ = textbox(235, 195, "Master Key / KEK (Key Encryption Key)\n256-бітний симетричний ключ обгортки", size=12, fill="#fef3c7", stroke="#d97706", min_w=330)
    frags.append(b2)

    b3, _, _ = textbox(235, 280, "DEK (Data Encryption Key)\nКлюч шифрування розділів даних", size=12, fill="#fee2e2", stroke=POS, bold=True, min_w=330)
    frags.append(b3)

    b_shred, _, _ = textbox(235, 395, "КОМАНДА САНІТИЗАЦІЇ / НУЛІФІКАЦІЯ\nАпаратний скид (Zeroization) / TPM2_Clear\nDEK знищується за < 1 мс у захищеній пам'яті", size=12, bold=True, fill="#fee2e2", stroke=POS, color=POS, min_w=350)
    frags.append(b_shred)

    # Права колонка: Flash-сховище та FTL
    frags.append(rect(510, 65, 390, 435, fill="none", stroke="#64748b", sw=1.5, rx=8))

    b4, _, _ = textbox(705, 110, "Шифротекст розділів Flash\nAES-256-XTS / AES-CBC з апаратним крипторушієм", size=12, bold=True, fill="#e2e8f0", stroke="#475569", min_w=350)
    frags.append(b4)

    b5, _, _ = textbox(705, 195, "Користувацькі дані та облікові записи\nWi-Fi PSK, TLS сертифікати, телеметрія, PII", size=12, fill="#ffffff", stroke="#94a3b8", min_w=330)
    frags.append(b5)

    b6, _, _ = textbox(705, 280, "Службові зони та резерв FTL (Over-Provisioning)\nЗносостійкі сторінки, журнали помилок, зняті блоки", size=11, fill="#f1f5f9", stroke="#94a3b8", min_w=330)
    frags.append(b6)

    b7, _, _ = textbox(705, 395, "КРИПТОГРАФІЧНИЙ БАР'ЄР (ШУМ)\nБез DEK усі фізичні комірки Flash стають\nнезворотно закритим білим шумом (2²⁵⁶ операцій)", size=12, bold=True, fill="#dcfce7", stroke=FIELD, color="#14532d", min_w=350)
    frags.append(b7)

    # Зв'язки та стрілки
    frags.append(arrow(235, 140, 235, 170, color=LINE, sw=1.5))
    frags.append(arrow(235, 222, 235, 252, color=LINE, sw=1.5))
    frags.append(arrow(235, 308, 235, 350, color=POS, sw=2.0))

    frags.append(arrow(705, 140, 705, 170, color=LINE, sw=1.5))
    frags.append(arrow(705, 222, 705, 252, color=LINE, sw=1.5))
    frags.append(arrow(705, 308, 705, 350, color=FIELD, sw=2.0))

    # Горизонтальні потоки
    frags.append(arrow(405, 280, 530, 110, color=POS, sw=1.8))
    frags.append(text(470, 185, "Шифрування", size=11, color=MUTED, bold=True))
    frags.append(text(470, 202, "потоку даних", size=11, color=MUTED, bold=True))

    frags.append(arrow(415, 395, 525, 395, color=FIELD, sw=2.2))
    frags.append(text(470, 425, "Миттєве стирання", size=11, color=FIELD, bold=True))
    frags.append(text(470, 442, "O(1) без зносу Flash", size=11, color=FIELD, bold=True))

    render(path, w, h, *frags)


def fig_nist_levels(path):
    """Порівняння трьох рівнів санітизації накопичувачів за стандартом NIST SP 800-88 Rev 1."""
    w, h = 960, 500
    frags = []

    frags.append(text(480, 35, "Рівні санітизації носіїв даних за стандартом NIST SP 800-88 Rev 1", size=16, bold=True, color=INK))

    # Колонка 1: Clear (рамка без заливки)
    frags.append(rect(25, 65, 285, 410, fill="none", stroke="#94a3b8", sw=1.5, rx=8))
    t1, _, _ = textbox(167, 105, "1. Clear (Очищення)", size=14, bold=True, fill="#e2e8f0", stroke="#64748b", min_w=255)
    frags.append(t1)
    
    b1_desc, _, _ = textbox(167, 190, "Логічне перезаписування\n• Команди dd, blkdiscard, zeros\n• Запис шаблонів у логічні LBA\n• Стандартні файлові операції", size=11, fill="#ffffff", stroke="#cbd5e1", min_w=255)
    frags.append(b1_desc)

    b1_risk, _, _ = textbox(167, 290, "Обмеження та ризики\n• Дані лишаються в FTL Over-Provisioning\n• Не стирає збійні (bad) блоки\n• Вразливе до апаратної випайки Flash", size=11, fill="#fee2e2", stroke=POS, color=POS, min_w=255)
    frags.append(b1_risk)

    b1_target, _, _ = textbox(167, 400, "Сфера застосування\nПовторне використання всередині\nтієї самої безпекової зони організації", size=11, fill="#f1f5f9", stroke="#94a3b8", min_w=255)
    frags.append(b1_target)

    # Колонка 2: Purge (рамка без заливки)
    frags.append(rect(337, 65, 285, 410, fill="none", stroke=FIELD, sw=1.8, rx=8))
    t2, _, _ = textbox(480, 105, "2. Purge (Знешкодження)", size=14, bold=True, fill="#dcfce7", stroke=FIELD, color="#166534", min_w=255)
    frags.append(t2)

    b2_desc, _, _ = textbox(480, 190, "Апаратне / криптостирання\n• ATA/NVMe Enhanced Secure Erase\n• eMMC SECURE_ERASE / TRIM\n• Crypto-Shredding (знищення DEK)", size=11, fill="#ffffff", stroke="#86efac", min_w=255)
    frags.append(b2_desc)

    b2_risk, _, _ = textbox(480, 290, "Стійкість до атак\n• Очищає OP-зони, кеші та збійні блоки\n• Захист від лабораторій (Chip-Off, SEM)\n• Зберігає працездатність плати", size=11, fill="#f0fdf4", stroke=FIELD, color="#14532d", bold=True, min_w=255)
    frags.append(b2_risk)

    b2_target, _, _ = textbox(480, 400, "Сфера застосування\nПовернення виробнику, гарантійний\nремонт (RMA), вторинний ринок / лізинг", size=11, fill="#dcfce7", stroke=FIELD, min_w=255)
    frags.append(b2_target)

    # Колонка 3: Destroy (рамка без заливки)
    frags.append(rect(650, 65, 285, 410, fill="none", stroke=POS, sw=1.5, rx=8))
    t3, _, _ = textbox(792, 105, "3. Destroy (Знищення)", size=14, bold=True, fill="#fee2e2", stroke=POS, color=POS, min_w=255)
    frags.append(t3)

    b3_desc, _, _ = textbox(792, 190, "Фізична деструкція\n• Подрібнення шредером (< 2 мм)\n• Спалювання / піроліз (> 1000 °C)\n• Хімічне розчинення кристала", size=11, fill="#ffffff", stroke="#fca5a5", min_w=255)
    frags.append(b3_desc)

    b3_risk, _, _ = textbox(792, 290, "Результат\n• 100% неможливість відновлення\n• Повна втрата обладнання\n• Висока вартість та відходи WEEE", size=11, fill="#fee2e2", stroke=POS, color=POS, min_w=255)
    frags.append(b3_risk)

    b3_target, _, _ = textbox(792, 400, "Сфера застосування\nКінець життєвого циклу (EOL),\nдефектні носії, надсекретні модулі", size=11, fill="#fee2e2", stroke=POS, min_w=255)
    frags.append(b3_target)

    render(path, w, h, *frags)


if __name__ == "__main__":
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    fig_crypto_shredding(os.path.join(img_dir, "crypto-shredding-key-destruction.svg"))
    fig_nist_levels(os.path.join(img_dir, "nist-sanitization-levels.svg"))
    print("Фігури успішно згенеровано.")

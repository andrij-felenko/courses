# -*- coding: utf-8 -*-
import sys, os

# Шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Кольорова палітра теми ──────────────────────────────────────────
CLR_ERR   = "#c0392b"     # Помилка, витік, небезпека
CLR_ERR_F = "#fdecea"
CLR_OK    = "#27ae60"     # Безпечно, успіх, цілісність
CLR_OK_F  = "#eafaf0"
CLR_WARN  = "#d97706"     # Попередження, вразливість
CLR_WARN_F= "#fef3c7"
CLR_INFO  = "#2457d6"     # Інформація, ключі, операції
CLR_INFO_F= "#eaf0fd"
CLR_DATA  = "#4b5563"     # Відкритий/зашифрований текст
CLR_DATA_F= "#f3f4f6"
CLR_MATH  = "#6b21a8"     # Математичні поля GF, твіки
CLR_MATH_F= "#f5f3ff"


# ── 1. Порівняння режимів шифрування для блокових пристроїв ───────────
def fig_modes_comparison():
    W, H = 1060, 520
    p = []

    p.append(text(W / 2, 28, "Порівняння режимів шифрування на секторах накопичувача", size=16, color=INK, bold=True))

    cols = [
        (140, "ECB (Codebook)", "Витік структури",
         [("Відкритий текст P", CLR_DATA_F, CLR_DATA),
          ("C[j] = AES(K, P[j])", CLR_ERR_F, CLR_ERR),
          ("Катастрофа:\nоднакові блоки дають\nоднаковий шифротекст;\nвитік карти файлів", CLR_ERR_F, CLR_ERR)]),

        (380, "CBC (Chaining)", "Послідовна залежність",
         [("C[j] = AES(K, P[j] ⊕ C[j-1])", CLR_DATA_F, CLR_DATA),
          ("Bit-flipping:\nΔ в C[j-1] змінює P[j],\nруйнує P[j-1]", CLR_WARN_F, CLR_WARN),
          ("Обмеження:\nнеможливий паралельний\nзапис; атака на IV", CLR_WARN_F, CLR_WARN)]),

        (620, "CTR / GCM (AEAD)", "Неможливість на дисках",
         [("C = P ⊕ AES(K, Nonce || j)", CLR_DATA_F, CLR_DATA),
          ("Катастрофа Nonce-reuse:\nперезапис сектора розкриває\nP1 ⊕ P2 = C1 ⊕ C2", CLR_ERR_F, CLR_ERR),
          ("Немає місця:\n512B/4KB сектор не вміщує\n16B тег без переформатування", CLR_WARN_F, CLR_WARN)]),

        (860, "XTS-AES (IEEE 1619)", "Стандарт для накопичувачів",
         [("Два ключі K1, K2\nТвік T = AES(K2, LBA) ⊗ αʲ", CLR_INFO_F, CLR_INFO),
          ("C[j] = AES(K1, P[j] ⊕ T) ⊕ T", CLR_OK_F, CLR_OK),
          ("Переваги:\nповний паралелізм,\nнемає розширення секторів,\nприв'язка до позиції LBA", CLR_OK_F, CLR_OK)]),
    ]

    for cx, title, subtitle, boxes in cols:
        p.append(rect(cx - 105, 52, 210, 448, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
        p.append(text(cx, 76, title, size=13, color=INK, bold=True))
        p.append(text(cx, 94, subtitle, size=11, color=MUTED, italic=True))

        y_pos = [118, 222, 340]
        for i, (txt, fill_c, strk_c) in enumerate(boxes):
            p.append(fitbox(cx - 95, y_pos[i], 190, 94, txt, size=12, fill=fill_c, stroke=strk_c, sw=1.4))

    return render(os.path.join(OUT, "block-device-modes-comparison.svg"), W, H, *p)


# ── 2. Внутрішня будова блоку XTS-AES ──────────────────────────────────
def fig_xts_block_structure():
    W, H = 1000, 560
    p = []

    p.append(text(W / 2, 28, "Схема шифрування та дешифрування блоку в режимі XTS-AES", size=16, color=INK, bold=True))

    # Ліва колонка: Генерація твіка
    p.append(rect(40, 55, 260, 475, fill="#fbfbfe", stroke=CLR_MATH, sw=1.5, rx=8))
    p.append(text(170, 80, "Генерація маски-твіка T[j]", size=13, color=CLR_MATH, bold=True))

    p.append(fitbox(60, 105, 220, 50, "Номер сектора (LBA) i\n(128-бітне число)", size=12, fill=CLR_MATH_F, stroke=CLR_MATH))
    p.append(arrow(170, 155, 170, 185, color=CLR_MATH))

    p.append(fitbox(60, 185, 220, 50, "AES-Enc(Key2, i)\nБазовий твік T[0]", size=12, fill=CLR_INFO_F, stroke=CLR_INFO, bold=True))
    p.append(arrow(170, 235, 170, 270, color=CLR_MATH))

    p.append(fitbox(60, 270, 220, 65, "Множення в GF(2¹²⁸):\nT[j] = T[0] ⊗ αʲ\n(α = x, mod P(x))", size=12, fill=CLR_MATH_F, stroke=CLR_MATH))

    p.append(fitbox(60, 375, 220, 135, "Властивість поля:\nМноження на α — це\nпобітовий зсув вліво\nіз умовним XOR 0x87\nпри переповненні", size=11, fill="#ffffff", stroke=LINE, sw=1.0))

    # Центральна колонка: Шифрування
    p.append(rect(340, 55, 300, 475, fill="#ffffff", stroke=CLR_OK, sw=1.5, rx=8))
    p.append(text(490, 80, "Шифрування блоку j", size=13, color=CLR_OK, bold=True))

    p.append(fitbox(380, 105, 220, 45, "Відкритий блок P[j]", size=12, fill=CLR_DATA_F, stroke=CLR_DATA, bold=True))
    p.append(arrow(490, 150, 490, 180, color=LINE))

    # Перший XOR
    p.append(circle(490, 195, 15, fill=CLR_MATH_F, stroke=CLR_MATH, sw=1.5))
    p.append(text(490, 200, "⊕", size=16, color=CLR_MATH, bold=True))
    # Стрілка від твіка
    p.append(arrow(280, 300, 475, 195, color=CLR_MATH, sw=1.5))

    p.append(arrow(490, 210, 490, 250, color=LINE))
    p.append(fitbox(370, 250, 240, 50, "PP[j] = P[j] ⊕ T[j]\n(Вхідне відбілювання)", size=11, fill=CLR_DATA_F, stroke=LINE))
    p.append(arrow(490, 300, 490, 335, color=LINE))

    p.append(fitbox(370, 335, 240, 55, "AES-Enc(Key1, PP[j])\n(Основне шифрування)", size=12, fill=CLR_INFO_F, stroke=CLR_INFO, bold=True))
    p.append(arrow(490, 390, 490, 420, color=LINE))

    # Другий XOR
    p.append(circle(490, 435, 15, fill=CLR_MATH_F, stroke=CLR_MATH, sw=1.5))
    p.append(text(490, 440, "⊕", size=16, color=CLR_MATH, bold=True))
    # Стрілка від твіка до другого XOR
    p.append(arrow(280, 310, 475, 435, color=CLR_MATH, sw=1.5))

    p.append(arrow(490, 450, 490, 475, color=LINE))
    p.append(fitbox(380, 475, 220, 45, "Шифротекст C[j]", size=12, fill=CLR_OK_F, stroke=CLR_OK, bold=True))

    # Права колонка: Дешифрування
    p.append(rect(670, 55, 300, 475, fill="#ffffff", stroke=CLR_INFO, sw=1.5, rx=8))
    p.append(text(820, 80, "Дешифрування блоку j", size=13, color=CLR_INFO, bold=True))

    p.append(fitbox(710, 105, 220, 45, "Шифротекст C[j]", size=12, fill=CLR_OK_F, stroke=CLR_OK, bold=True))
    p.append(arrow(820, 150, 820, 180, color=LINE))

    # Перший XOR дешифрування
    p.append(circle(820, 195, 15, fill=CLR_MATH_F, stroke=CLR_MATH, sw=1.5))
    p.append(text(820, 200, "⊕", size=16, color=CLR_MATH, bold=True))
    # Лінія твіка праворуч
    p.append(arrow(280, 290, 805, 195, color=CLR_MATH, sw=1.2))

    p.append(arrow(820, 210, 820, 250, color=LINE))
    p.append(fitbox(700, 250, 240, 50, "CC[j] = C[j] ⊕ T[j]\n(Зняття вихідної маски)", size=11, fill=CLR_DATA_F, stroke=LINE))
    p.append(arrow(820, 300, 820, 335, color=LINE))

    p.append(fitbox(700, 335, 240, 55, "AES-Dec(Key1, CC[j])\n(Основне дешифрування)", size=12, fill=CLR_INFO_F, stroke=CLR_INFO, bold=True))
    p.append(arrow(820, 390, 820, 420, color=LINE))

    # Другий XOR дешифрування
    p.append(circle(820, 435, 15, fill=CLR_MATH_F, stroke=CLR_MATH, sw=1.5))
    p.append(text(820, 440, "⊕", size=16, color=CLR_MATH, bold=True))
    p.append(arrow(280, 320, 805, 435, color=CLR_MATH, sw=1.2))

    p.append(arrow(820, 450, 820, 475, color=LINE))
    p.append(fitbox(710, 475, 220, 45, "Відкритий блок P[j]", size=12, fill=CLR_DATA_F, stroke=CLR_DATA, bold=True))

    return render(os.path.join(OUT, "xts-block-structure.svg"), W, H, *p)


# ── 3. Механіка Ciphertext Stealing (CTS) ──────────────────────────────
def fig_ciphertext_stealing():
    W, H = 1000, 520
    p = []

    p.append(text(W / 2, 28, "Механізм викрадення шифротексту (Ciphertext Stealing) для неповних секторів", size=16, color=INK, bold=True))

    # Верхня половина: Вхідні дані
    p.append(rect(50, 60, 900, 110, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    p.append(text(160, 82, "Вхідні відкриті дані сектора:", size=12, color=MUTED, bold=True))

    p.append(fitbox(80, 100, 200, 50, "Блоки P[0] .. P[m-2]\n(Повні 16-байтні блоки)", size=11, fill=CLR_DATA_F, stroke=LINE))
    p.append(fitbox(340, 100, 260, 50, "Останній повний блок P[m-1]\n(16 байтів)", size=12, fill=CLR_INFO_F, stroke=CLR_INFO, bold=True))
    p.append(fitbox(660, 100, 240, 50, "Хвіст сектора P[m]\n(Неповний: b байтів, b < 16)", size=12, fill=CLR_WARN_F, stroke=CLR_WARN, bold=True))

    # Центральна частина: Проміжний етап
    p.append(arrow(470, 150, 470, 195, color=LINE))
    p.append(fitbox(320, 195, 300, 50, "Шифрування P[m-1] з твіком T[m-1]\nОтримуємо проміжний C'[m-1] (16 Б)", size=11, fill=CLR_INFO_F, stroke=CLR_INFO))

    p.append(arrow(410, 245, 410, 280, color=LINE))
    p.append(arrow(530, 245, 600, 280, color=CLR_MATH))
    p.append(arrow(780, 150, 680, 280, color=CLR_WARN))

    # Конструювання P'[m-1]
    p.append(fitbox(320, 280, 180, 55, "Голова C'[m-1] (b байтів)\nСтає фінальним C[m]", size=11, fill=CLR_OK_F, stroke=CLR_OK, bold=True))
    p.append(fitbox(550, 280, 360, 55, "Формування блоку P'[m-1] (16 байтів):\nP[m] (b байтів) || Хвіст C'[m-1] (16-b байтів)", size=11, fill=CLR_MATH_F, stroke=CLR_MATH, bold=True))

    p.append(arrow(730, 335, 730, 375, color=LINE))
    p.append(fitbox(550, 375, 360, 45, "Шифрування P'[m-1] з твіком T[m] → C[m-1] (16 Б)", size=11, fill=CLR_OK_F, stroke=CLR_OK))

    # Нижня частина: Фінальний шифротекст
    p.append(rect(50, 440, 900, 65, fill="#ffffff", stroke=CLR_OK, sw=1.5, rx=8))
    p.append(text(150, 460, "Фінальний вихідний сектор:", size=12, color=CLR_OK, bold=True))

    p.append(fitbox(80, 450, 200, 45, "C[0] .. C[m-2]\n(Повні блоки)", size=11, fill=CLR_DATA_F, stroke=LINE))
    p.append(fitbox(340, 450, 280, 45, "C[m-1] (16 байтів)\n(Зсунутий повний блок)", size=11, fill=CLR_OK_F, stroke=CLR_OK, bold=True))
    p.append(fitbox(680, 450, 220, 45, "C[m] (b байтів)\n(Викрадений хвіст)", size=11, fill=CLR_OK_F, stroke=CLR_OK, bold=True))

    # Стрілки вниз
    p.append(arrow(410, 335, 790, 450, color=CLR_OK, sw=1.5))
    p.append(arrow(730, 420, 480, 450, color=CLR_OK, sw=1.5))

    return render(os.path.join(OUT, "ciphertext-stealing-flow.svg"), W, H, *p)


# ── 4. Поверхня атак та межі стійкості XTS-AES ─────────────────────────
def fig_attack_surface():
    W, H = 1040, 500
    p = []

    p.append(text(W / 2, 28, "Модель загроз та обмеження стійкості режиму AES-XTS", size=16, color=INK, bold=True))

    cards = [
        (150, "Відсутність AEAD", "Підробка секторів",
         "Зловмисник інвертує\nбіти в блоці C[j].\nПри дешифруванні блок\nперетворюється на сміття,\nале помилка НЕ виникає!",
         CLR_ERR_F, CLR_ERR),

        (410, "Атака повтором (Replay)", "Підміна версій",
         "Зловмисник записує старий\nзашифрований сектор S (час t1)\nповерх нового сектора S (час t2).\nДиск успішно розшифрує\nзастарілі дані.",
         CLR_WARN_F, CLR_WARN),

        (670, "Перестановка блоків", "У межах сектора",
         "Перестановка блоків C[j]\nта C[k] у секторі призводить\nдо розшифрування обох у\nнепередбачуване сміття через\nрізні твіки αʲ ≠ αᵏ.",
         CLR_INFO_F, CLR_INFO),

        (930, "Межі обсягу даних", "Колізії блоків",
         "IEEE 1619 обмежує\nрозмір сектора до 2²⁰ блоків.\nNIST SP 800-38E лімітує\nзагальний обсяг шифрування\nодним ключем до 2⁶⁴ блоків.",
         CLR_MATH_F, CLR_MATH),
    ]

    for cx, title, subtitle, desc, fill_c, strk_c in cards:
        p.append(rect(cx - 110, 60, 220, 410, fill="#ffffff", stroke=strk_c, sw=1.4, rx=8))
        p.append(text(cx, 88, title, size=13, color=strk_c, bold=True))
        p.append(text(cx, 108, subtitle, size=11, color=MUTED, italic=True))

        p.append(fitbox(cx - 95, 130, 190, 160, desc, size=12, fill=fill_c, stroke=strk_c, sw=1.2))

        p.append(fitbox(cx - 95, 310, 190, 140,
                        "Захисні заходи:\n• dm-integrity / HMAC\n• ФС із контрольними сумами\n  (ZFS, Btrfs)\n• Регулярна ротація ключів",
                        size=11, fill="#ffffff", stroke=LINE, sw=1.0))

    return render(os.path.join(OUT, "xts-attack-surface.svg"), W, H, *p)


if __name__ == "__main__":
    fig_modes_comparison()
    fig_xts_block_structure()
    fig_ciphertext_stealing()
    fig_attack_surface()
    print("Усі 4 фігури успішно згенеровано.")

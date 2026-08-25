# -*- coding: utf-8 -*-
"""Генерація SVG-ілюстрацій для теми 'RSA'."""
import sys, os

# Додаємо scripts/ до шляху пошуку модулів (4 рівні вгору від root/eng/sf-security/rsa)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

def fig_trapdoor_permutation():
    """Фігура 1: Принцип односторонньої функції з таємним входом (Trapdoor Permutation)."""
    w, h = 880, 420
    frags = []

    # Заголовок
    frags.append(text(440, 28, "Одностороння функція з таємним входом (Trapdoor One-Way Permutation)", size=16, bold=True))

    # Зона відкритого тексту m (ліворуч)
    b_m, _, _ = textbox(130, 140, "Відкритий текст m\n(0 <= m < N)\nm in Z_N*", size=13, pad=12, fill="#eff6ff", stroke="#3b82f6", min_w=170)
    frags.append(b_m)

    # Зона шифротексту c (праворуч)
    b_c, _, _ = textbox(750, 140, "Шифротекст c\n(0 <= c < N)\nc in Z_N*", size=13, pad=12, fill="#fef2f2", stroke="#ef4444", min_w=170)
    frags.append(b_c)

    # Прямий напрямок: легке обчислення з відкритим ключем (верхня стрілка)
    frags.append(arrow(220, 120, 660, 120, color="#10b981", sw=3))
    b_fwd, _, _ = textbox(440, 95, "Прямий напрямок (Шифрування): c = m^e mod N\nОбчислювально легке: O(log e * log^2 N) операцій\nПотрібен лише відкритий ключ (e, N)", size=11, pad=8, fill="#ecfdf5", stroke="#10b981", min_w=380)
    frags.append(b_fwd)

    # Зворотний напрямок БЕЗ секрету (середина): стіна факторизації
    frags.append(rect(300, 180, 280, 80, fill="#fef2f2", stroke="#b91c1c", sw=2, rx=8))
    frags.append(text(440, 205, "Обернення БЕЗ таємного входу", size=12, bold=True, color="#b91c1c"))
    frags.append(text(440, 225, "Добування кореня e-го степеня mod N", size=11, color="#7f1d1d"))
    frags.append(text(440, 245, "Еквівалентно факторизації N: O(exp(c * (ln N)^1/3))", size=10, bold=True, color="#991b1b"))

    frags.append(arrow(660, 220, 585, 220, color="#b91c1c", sw=2))
    frags.append(line(295, 210, 295, 230, color="#b91c1c", sw=3))
    frags.append(line(290, 215, 300, 225, color="#b91c1c", sw=3))
    frags.append(line(290, 225, 300, 215, color="#b91c1c", sw=3))

    # Зворотний напрямок З таємним входом (нижня дуга/стрілка)
    frags.append(rect(60, 310, 760, 90, fill="#f5f3ff", stroke="#8b5cf6", sw=1.5, rx=8))
    frags.append(text(440, 332, "ТАЄМНИЙ ВХІД (Trapdoor): Знання розкладу N = p * q", size=13, bold=True, color="#6d28d9"))
    frags.append(text(440, 355, "Дозволяє знайти порядок групи lambda(N) = lcm(p-1, q-1) та секретну експоненту d = e^-1 mod lambda(N)", size=11, color="#4c1d95"))
    frags.append(text(440, 378, "Розшифрування: m = c^d mod N виконується миттєво за O(log d * log^2 N)", size=11, bold=True, color="#5b21b6"))

    frags.append(arrow(660, 310, 220, 310, color="#8b5cf6", sw=3))

    out_path = os.path.join(IMG_DIR, "rsa-trapdoor-permutation.svg")
    render(out_path, w, h, *frags)
    print("Generated:", out_path)

def fig_key_generation_and_crt():
    """Фігура 2: Конвеєр генерації ключів RSA та прискорення CRT."""
    w, h = 900, 480
    frags = []

    frags.append(text(450, 26, "Генерація ключів RSA та 4-кратне прискорення розшифрування через CRT", size=16, bold=True))

    # Фаза 1: Генерація простих чисел (ліворуч)
    frags.append(rect(15, 55, 260, 405, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(145, 80, "1. Генерація p і q", size=14, bold=True, color="#1e293b"))

    b_rng, _, _ = textbox(145, 130, "CSPRNG (/dev/urandom)\nГенерація 1024-біт випадкових чисел", size=11, pad=8, fill=BG, stroke=LINE, min_w=230)
    b_sieve, _, _ = textbox(145, 210, "Відсів малих дільників\n(ділення на прості до 1000)", size=11, pad=8, fill=BG, stroke=LINE, min_w=230)
    b_mr, _, _ = textbox(145, 300, "Тест Міллера - Рабіна\n(40+ раундів для P(error) < 2^-80)", size=11, pad=8, fill="#eff6ff", stroke="#3b82f6", min_w=230)
    b_res, _, _ = textbox(145, 395, "Отримано два простих числа:\np != q довжиною 1024 біти кожне", size=11, pad=8, fill="#ecfdf5", stroke="#10b981", bold=True, min_w=230)
    frags.extend([b_rng, b_sieve, b_mr, b_res])

    frags.append(arrow(145, 160, 145, 180, color=MUTED, sw=1.5))
    frags.append(arrow(145, 245, 145, 265, color=MUTED, sw=1.5))
    frags.append(arrow(145, 335, 145, 360, color=MUTED, sw=1.5))

    # Фаза 2: Ключова пара (Центр)
    frags.append(rect(290, 55, 290, 405, fill="#fffdf5", stroke="#d97706", sw=1.5, rx=8))
    frags.append(text(435, 80, "2. Розрахунок ключів", size=14, bold=True, color="#92400e"))

    b_n, _, _ = textbox(435, 125, "Модуль: N = p * q (2048 бітів)\nПорядок: lambda(N) = lcm(p-1, q-1)", size=11, pad=8, fill=BG, stroke=LINE, min_w=260)
    b_e, _, _ = textbox(435, 205, "Відкрита експонента: e = 65537\n(F4 = 2^16 + 1, вага Хеммінга = 2)", size=11, pad=8, fill="#ecfdf5", stroke="#10b981", min_w=260)
    b_d, _, _ = textbox(435, 285, "Приватна експонента: d\nd = e^-1 mod lambda(N)\n(розширений алгоритм Евкліда)", size=11, pad=8, fill="#fee2e2", stroke="#ef4444", min_w=260)
    b_keys, _, _ = textbox(435, 385, "Відкритий ключ: (e, N)\nПриватний ключ: (d, N) або CRT-набір", size=11, pad=8, fill="#fef3c7", stroke="#d97706", bold=True, min_w=260)
    frags.extend([b_n, b_e, b_d, b_keys])

    frags.append(arrow(435, 155, 435, 175, color=MUTED, sw=1.5))
    frags.append(arrow(435, 235, 435, 255, color=MUTED, sw=1.5))
    frags.append(arrow(435, 325, 435, 355, color=MUTED, sw=1.5))

    # Фаза 3: Прискорення CRT (Праворуч)
    frags.append(rect(595, 55, 290, 405, fill="#f5f3ff", stroke="#7c3aed", sw=1.5, rx=8))
    frags.append(text(740, 80, "3. Оптимізація CRT (~4x)", size=14, bold=True, color="#5b21b6"))

    b_crt_params, _, _ = textbox(740, 130, "Попередній розрахунок:\nd_p = d mod (p-1)  [1024 біти]\nd_q = d mod (q-1)  [1024 біти]\nq_inv = q^-1 mod p [1024 біти]", size=10, pad=8, fill=BG, stroke=LINE, min_w=260)
    b_crt_split, _, _ = textbox(740, 235, "Паралельне розшифрування:\nm_p = c^d_p mod p  (1024-біт)\nm_q = c^d_q mod q  (1024-біт)\nСкладність: 2 * (k/2)^3 = k^3 / 4", size=10, pad=8, fill="#ede9fe", stroke="#8b5cf6", min_w=260)
    b_garner, _, _ = textbox(740, 350, "Реконструкція Гарнера:\nh = (q_inv * (m_p - m_q)) mod p\nm = m_q + h * q\nРезультат ідентичний m = c^d mod N", size=10, pad=8, fill="#ecfdf5", stroke="#10b981", bold=True, min_w=260)
    b_speedup, _, _ = textbox(740, 430, "Прискорення у ~4 рази порівняно з сирим d", size=10, pad=4, fill="#fef3c7", stroke="#d97706", bold=True, min_w=260)
    frags.extend([b_crt_params, b_crt_split, b_garner, b_speedup])

    frags.append(arrow(740, 175, 740, 195, color=MUTED, sw=1.5))
    frags.append(arrow(740, 280, 740, 310, color=MUTED, sw=1.5))

    # З'єднувальні стрілки між фазами
    frags.append(arrow(275, 205, 290, 205, color="#d97706", sw=2))
    frags.append(arrow(580, 205, 595, 205, color="#7c3aed", sw=2))

    out_path = os.path.join(IMG_DIR, "rsa-key-generation-and-crt.svg")
    render(out_path, w, h, *frags)
    print("Generated:", out_path)

def fig_oaep_padding():
    """Фігура 3: Схема криптографічного доповнення RSA-OAEP."""
    w, h = 880, 460
    frags = []

    frags.append(text(440, 26, "Схема безпечного доповнення шифрування RSA-OAEP (RFC 8017)", size=16, bold=True))

    # Верхній рівень: формування блоку даних DB та випадкового зерна seed
    frags.append(rect(40, 60, 470, 70, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=6))
    frags.append(text(275, 80, "Блок даних DB (Data Block)", size=12, bold=True, color="#1d4ed8"))
    frags.append(rect(50, 95, 120, 25, fill="#dbeafe", stroke="#3b82f6", rx=4))
    frags.append(text(110, 112, "lHash (SHA-256)", size=10))
    frags.append(rect(175, 95, 90, 25, fill="#dbeafe", stroke="#3b82f6", rx=4))
    frags.append(text(220, 112, "PS (0x00...)", size=10))
    frags.append(rect(270, 95, 50, 25, fill="#bfdbfe", stroke="#2563eb", rx=4))
    frags.append(text(295, 112, "0x01", size=10, bold=True))
    frags.append(rect(325, 95, 175, 25, fill="#93c5fd", stroke="#1d4ed8", rx=4))
    frags.append(text(412, 112, "Повідомлення M", size=10, bold=True))

    frags.append(rect(570, 60, 270, 70, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=6))
    frags.append(text(705, 80, "Випадкове зерно (CSPRNG)", size=12, bold=True, color="#b45309"))
    frags.append(rect(585, 95, 240, 25, fill="#fde68a", stroke="#d97706", rx=4))
    frags.append(text(705, 112, "seed (довжина hLen, напр. 32 байти)", size=10, bold=True))

    # Двораундова мережа Фейстеля
    # 1. seed іде в MGF1 -> dbMask, що ксориться з DB
    frags.append(arrow(705, 130, 705, 160, color="#d97706", sw=2))
    b_mgf1, _, _ = textbox(520, 185, "MGF1 (Mask Generation Function)\nна базі SHA-256", size=10, pad=6, fill="#f3e8ff", stroke="#9333ea", min_w=200)
    frags.append(b_mgf1)
    frags.append(arrow(705, 160, 620, 185, color="#9333ea", sw=1.5))
    frags.append(arrow(420, 185, 275, 220, color="#9333ea", sw=1.5))

    # Коло XOR для DB
    frags.append(circle(275, 235, 14, fill="#ffffff", stroke="#2563eb", sw=2))
    frags.append(line(265, 235, 285, 235, color="#2563eb", sw=2))
    frags.append(line(275, 225, 275, 245, color="#2563eb", sw=2))
    frags.append(arrow(275, 130, 275, 221, color="#2563eb", sw=2))

    # Отримуємо maskedDB
    frags.append(arrow(275, 249, 275, 285, color="#2563eb", sw=2))
    b_mdb, _, _ = textbox(275, 310, "maskedDB = DB XOR MGF1(seed)\n(довжина k - hLen - 1 байтів)", size=11, pad=8, fill="#eff6ff", stroke="#3b82f6", min_w=290)
    frags.append(b_mdb)

    # 2. maskedDB іде в MGF1 -> seedMask, що ксориться з seed
    b_mgf2, _, _ = textbox(520, 285, "MGF1 (на базі SHA-256)\nseedMask = MGF1(maskedDB)", size=10, pad=6, fill="#f3e8ff", stroke="#9333ea", min_w=180)
    frags.append(b_mgf2)
    frags.append(arrow(420, 310, 430, 285, color="#9333ea", sw=1.5))
    frags.append(arrow(610, 285, 705, 310, color="#9333ea", sw=1.5))

    # Коло XOR для seed
    frags.append(circle(705, 325, 14, fill="#ffffff", stroke="#d97706", sw=2))
    frags.append(line(695, 325, 715, 325, color="#d97706", sw=2))
    frags.append(line(705, 315, 705, 335, color="#d97706", sw=2))
    frags.append(arrow(705, 130, 705, 311, color="#d97706", sw=2))

    # Отримуємо maskedSeed
    frags.append(arrow(705, 339, 705, 370, color="#d97706", sw=2))
    b_ms, _, _ = textbox(705, 395, "maskedSeed = seed XOR MGF1(maskedDB)\n(довжина hLen байтів)", size=11, pad=8, fill="#fef3c7", stroke="#d97706", min_w=250)
    frags.append(b_ms)

    # Фінальний закодований блок EM
    frags.append(rect(40, 410, 800, 40, fill="#ecfdf5", stroke="#10b981", sw=2, rx=6))
    frags.append(rect(50, 417, 60, 25, fill="#a7f3d0", stroke="#059669", rx=4))
    frags.append(text(80, 434, "0x00", size=11, bold=True))
    frags.append(rect(115, 417, 240, 25, fill="#fde68a", stroke="#d97706", rx=4))
    frags.append(text(235, 434, "maskedSeed (hLen)", size=11, bold=True))
    frags.append(rect(360, 417, 470, 25, fill="#bfdbfe", stroke="#2563eb", rx=4))
    frags.append(text(595, 434, "maskedDB (k - hLen - 1 байтів)", size=11, bold=True))

    out_path = os.path.join(IMG_DIR, "rsa-oaep-padding-pipeline.svg")
    render(out_path, w, h, *frags)
    print("Generated:", out_path)

def fig_bleichenbacher_attack():
    """Фігура 4: Атака оракула заповнення Блейхенбахера (PKCS#1 v1.5)."""
    w, h = 900, 450
    frags = []

    frags.append(text(450, 26, "Атака мільйона повідомлень Блейхенбахера на PKCS#1 v1.5 (Оракул заповнення)", size=16, bold=True))

    # Ліва колонка: Атакуючий
    frags.append(rect(20, 60, 280, 375, fill="#fff5f5", stroke="#ef4444", sw=1.5, rx=8))
    frags.append(text(160, 85, "Атакуючий (Криптоаналітик)", size=13, bold=True, color="#b91c1c"))

    b_init, _, _ = textbox(160, 130, "Має цільовий шифротекст c\n(c = m^e mod N, m невідоме)", size=10, pad=6, fill=BG, stroke=LINE, min_w=250)
    b_step1, _, _ = textbox(160, 205, "Крок 1: Підбір множника s_i\nc' = c * (s_i)^e mod N\nГомоморфне зміщення: m' = m * s_i mod N", size=10, pad=6, fill="#fee2e2", stroke="#ef4444", min_w=250)
    b_step2, _, _ = textbox(160, 290, "Крок 2: Звуження інтервалів\nНа основі відповідей оракула\nграниці для m стискаються", size=10, pad=6, fill="#fee2e2", stroke="#ef4444", min_w=250)
    b_rec, _, _ = textbox(160, 385, "Результат (~10^6 запитів):\nІнтервал звужується до одного m!\nВідкритий текст m відновлено!", size=10, pad=6, fill="#fef2f2", stroke="#991b1b", bold=True, min_w=250)
    frags.extend([b_init, b_step1, b_step2, b_rec])

    # Права колонка: Сервер з оракулом
    frags.append(rect(600, 60, 280, 375, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=8))
    frags.append(text(740, 85, "TLS-сервер (Оракул розшифрування)", size=13, bold=True, color="#1d4ed8"))

    b_dec, _, _ = textbox(740, 135, "Розшифровує c':\nm' = (c')^d mod N", size=10, pad=6, fill=BG, stroke=LINE, min_w=250)
    b_chk, _, _ = textbox(740, 210, "Перевірка PKCS#1 v1.5:\nЧи починається m' з байтів 0x00 0x02 ?\n(Тобто 2*B <= m' < 3*B, де B = 2^(8*(k-2)))", size=10, pad=6, fill="#dbeafe", stroke="#2563eb", min_w=250)
    b_leak, _, _ = textbox(740, 310, "Витік через побічний канал:\n- Код помилки (Decryption Error)\n- Або різниця в часі обробки запиту\nОракул повертає 1 біт: ТАК чи НІ", size=10, pad=6, fill="#fee2e2", stroke="#b91c1c", bold=True, min_w=250)
    frags.extend([b_dec, b_chk, b_leak])

    # Центральні інтерактивні стрілки
    frags.append(arrow(300, 195, 600, 195, color="#ef4444", sw=2))
    frags.append(text(450, 185, "Запит: c' = c * s_i^e mod N", size=10, bold=True, color="#b91c1c"))

    frags.append(arrow(600, 310, 300, 310, color="#2563eb", sw=2))
    frags.append(text(450, 300, "Відповідь: 0x00 0x02 валідне? (1 / 0)", size=10, bold=True, color="#1d4ed8"))

    out_path = os.path.join(IMG_DIR, "rsa-bleichenbacher-oracle-attack.svg")
    render(out_path, w, h, *frags)
    print("Generated:", out_path)

def fig_blinding_defense():
    """Фігура 5: Захист від атак побічними каналами через криптографічне засліплення."""
    w, h = 880, 420
    frags = []

    frags.append(text(440, 26, "Криптографічне засліплення (Blinding) проти часових атак та DPA", size=16, bold=True))

    # Зона 1: Вхідний шифротекст c
    b_c, _, _ = textbox(110, 100, "Вхідний шифротекст c\n(або геш для підпису m)", size=11, pad=8, fill="#eff6ff", stroke="#3b82f6", min_w=160)
    frags.append(b_c)

    # Зона 2: Генерація випадкового засліплювача r
    b_r, _, _ = textbox(110, 220, "Генерація CSPRNG:\nВипадковий множник r\nНСД(r, N) = 1", size=11, pad=8, fill="#fef3c7", stroke="#d97706", min_w=160)
    frags.append(b_r)

    # Зона 3: Операція засліплення
    b_blind, _, _ = textbox(340, 160, "Засліплення входу:\nc' = c * (r^e) mod N\n(Множення на публічний ступінь r)", size=11, pad=10, fill="#ecfdf5", stroke="#10b981", bold=True, min_w=240)
    frags.append(b_blind)

    frags.append(arrow(190, 100, 270, 140, color="#3b82f6", sw=1.5))
    frags.append(arrow(190, 220, 270, 180, color="#d97706", sw=1.5))

    # Зона 4: Приватна операція (розшифрування або підпис)
    frags.append(rect(480, 80, 200, 230, fill="#f5f3ff", stroke="#7c3aed", sw=2, rx=8))
    frags.append(text(580, 105, "Приватна операція", size=12, bold=True, color="#5b21b6"))
    frags.append(text(580, 125, "(Піднесення до степеня d)", size=10, color="#6d28d9"))

    b_exp, _, _ = textbox(580, 190, "Обчислення з секретом:\ns' = (c')^d mod N\n= (c * r^e)^d mod N\n= c^d * r^(e*d) mod N\n= m * r mod N", size=10, pad=8, fill=BG, stroke=LINE, min_w=180)
    frags.append(b_exp)
    frags.append(text(580, 275, "Час і струм залежать від c',\nа не від секретних бітів m!", size=9, bold=True, color="#15803d"))

    frags.append(arrow(460, 160, 480, 160, color="#10b981", sw=2))

    # Зона 5: Розсліплення (Unblinding)
    b_unblind, _, _ = textbox(775, 160, "Розсліплення результату:\nm = s' * (r^-1) mod N\n= (m * r) * r^-1 mod N\n= m mod N", size=11, pad=10, fill="#ecfdf5", stroke="#10b981", bold=True, min_w=220)
    frags.append(b_unblind)

    frags.append(arrow(680, 160, 720, 160, color="#7c3aed", sw=2))

    # Пояснювальна плашка внизу
    frags.append(rect(40, 335, 800, 65, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=6))
    frags.append(text(440, 355, "ЧОМУ ЦЕ ПРАЦЮЄ ПРОТИ БУДЬ-ЯКИХ ЧАСОВИХ ВИТОКІВ:", size=11, bold=True, color="#334155"))
    frags.append(text(440, 375, "Оскільки r генерується заново для кожного запиту, вхід c' є повністю випадковим елементом групи.", size=10, color="#475569"))
    frags.append(text(440, 390, "Атакуючий не може контролювати вхідні дані алгоритму exponentiation і не може зіставити час із бітами d.", size=10, color="#475569"))

    out_path = os.path.join(IMG_DIR, "rsa-blinding-side-channel-defense.svg")
    render(out_path, w, h, *frags)
    print("Generated:", out_path)

if __name__ == "__main__":
    fig_trapdoor_permutation()
    fig_key_generation_and_crt()
    fig_oaep_padding()
    fig_bleichenbacher_attack()
    fig_blinding_defense()

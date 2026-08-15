# -*- coding: utf-8 -*-
"""Фігури до теми «Підсистема ключів ядра (Kernel Keyring)»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def fig_kernel_keyring_arch():
    """Архітектура підсистеми ключів ядра Linux: простори, структури, LSM та споживачі."""
    W, H = 1040, 580
    f = [text(520, 28, "Архітектура підсистеми ключів ядра (Kernel Key Retention Service)", size=16, bold=True)]

    # 1. User Space Block (Верхній блок)
    f.append(rect(30, 55, 980, 110, fill="#fdfbf7", stroke="#d97706", sw=1.5, rx=8))
    f.append(text(50, 75, "ПРОСТІР КОРИСТУВАЧА (USER SPACE)", size=12, color="#b45309", bold=True, anchor="start"))

    b1, _, _ = textbox(160, 115, "Процес користувача\n(keyctl / app)", size=13, fill="#fff", min_w=180)
    f.append(b1)

    b2, _, _ = textbox(520, 115, "Системні виклики\nadd_key() / request_key() / keyctl()", size=13, fill="#fef3c7", stroke="#d97706", min_w=300)
    f.append(b2)

    b3, _, _ = textbox(870, 115, "Помічник upcall\n/sbin/request-key", size=13, fill="#fff", min_w=190)
    f.append(b3)

    f.append(arrow(250, 115, 370, 115))
    f.append(arrow(670, 115, 775, 115))

    # Вертикальні стрілки викликів системного інтерфейсу
    f.append(arrow(520, 150, 520, 195))

    # 2. Kernel Space Block (Центральний великий блок)
    f.append(rect(30, 195, 980, 255, fill="#f0f7ff", stroke="#2563eb", sw=1.5, rx=8))
    f.append(text(50, 215, "ПРОСТІР ЯДРА (KERNEL SPACE)", size=12, color="#1d4ed8", bold=True, anchor="start"))

    # Спрощена ієрархія кілець
    f.append(rect(50, 235, 270, 195, fill="#fff", stroke="#93c5fd", sw=1))
    f.append(text(185, 253, "Контекст процесів (struct cred)", size=12, bold=True))
    b_t, _, _ = textbox(185, 280, "Thread Keyring (@t)", size=11, fill="#eff6ff", min_w=220)
    b_p, _, _ = textbox(185, 320, "Process Keyring (@p)", size=11, fill="#eff6ff", min_w=220)
    b_s, _, _ = textbox(185, 360, "Session Keyring (@s)", size=11, fill="#eff6ff", min_w=220)
    b_u, _, _ = textbox(185, 400, "User Keyring (@u)", size=11, fill="#eff6ff", min_w=220)
    f.extend([b_t, b_p, b_s, b_u])

    # Дерево пошуку та LSM
    f.append(rect(345, 235, 340, 195, fill="#fff", stroke="#93c5fd", sw=1))
    f.append(text(515, 253, "Пошук та перевірка привілеїв", size=12, bold=True))

    b_perm, _, _ = textbox(515, 290, "Маска прав: key_perm_t\nPossessor (0x3f) | User | Group | Other", size=11, fill="#fef2f2", stroke="#ef4444", min_w=310)
    b_lsm, _, _ = textbox(515, 340, "Контролер безпеки LSM\nsecurity_key_permission()", size=11, fill="#fcf5ff", stroke="#a855f7", min_w=310)
    b_tree, _, _ = textbox(515, 395, "Асоціативний масив ключів (assoc_array)\nПошук ключів за типом і описом", size=11, fill="#f0fdf4", stroke="#22c55e", min_w=310)
    f.extend([b_perm, b_lsm, b_tree])

    # Типи ключів
    f.append(rect(710, 235, 285, 195, fill="#fff", stroke="#93c5fd", sw=1))
    f.append(text(852, 253, "Типи ключів (struct key_type)", size=12, bold=True))
    b_k1, _, _ = textbox(852, 285, "user / logon (секрети в пам'яті)", size=11, fill="#f8fafc", min_w=250)
    b_k2, _, _ = textbox(852, 320, "trusted / encrypted (TPM / AES)", size=11, fill="#f8fafc", min_w=250)
    b_k3, _, _ = textbox(852, 355, "big_key (tmpfs + шифрування)", size=11, fill="#f8fafc", min_w=250)
    b_k4, _, _ = textbox(852, 395, "asymmetric (X.509 / RSA / ECDSA)", size=11, fill="#f8fafc", min_w=250)
    f.extend([b_k1, b_k2, b_k3, b_k4])

    # Зв'язки між блоками ядра
    f.append(arrow(320, 320, 345, 320))
    f.append(arrow(685, 320, 710, 320))

    # Стрілка вниз до споживачів
    f.append(arrow(520, 450, 520, 475))

    # 3. Hardware & Consumers Block (Нижній блок)
    f.append(rect(30, 475, 980, 90, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=8))
    f.append(text(50, 493, "СПОЖИВАЧІ ТА АПАРАТНІ МОДУЛІ БЕЗПЕКИ", size=12, color="#15803d", bold=True, anchor="start"))

    b_c1, _, _ = textbox(150, 530, "Шифрування диска\ndm-crypt / fscrypt", size=11, fill="#fff", min_w=170)
    b_c2, _, _ = textbox(380, 530, "Мережева автентифікація\nNFSv4 / Kerberos / AFS", size=11, fill="#fff", min_w=200)
    b_c3, _, _ = textbox(620, 530, "Підписи та цілісність\nIMA/EVM / Module Signing", size=11, fill="#fff", min_w=200)
    b_c4, _, _ = textbox(870, 530, "Апаратний корінь\nTPM / TrustZone", size=11, fill="#fef2f2", stroke="#dc2626", min_w=190)
    f.extend([b_c1, b_c2, b_c3, b_c4])

    render(os.path.join(OUT, 'kernel-keyring.svg'), W, H, *f)


if __name__ == "__main__":
    fig_kernel_keyring_arch()

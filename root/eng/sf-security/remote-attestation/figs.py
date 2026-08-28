# -*- coding: utf-8 -*-
import sys
import os

SCRIPTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../scripts'))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)
if os.path.abspath('scripts') not in sys.path:
    sys.path.insert(0, os.path.abspath('scripts'))

from svgkit import render, rect, text, textbox, fitbox, arrow, line, circle, INK, POS, NEG, FIELD, MUTED

def fig_attestation_protocol():
    out = []
    out.append(rect(0, 0, 800, 520, fill="#ffffff", stroke="#ffffff", rx=0))
    out.append(text(400, 30, "Протокол виклику-відповіді віддаленої атестації TPM 2.0", size=18, bold=True, anchor="middle"))

    v_box, _, _ = textbox(120, 70, "Верифікатор\n(Віддалений сервер)", size=13, pad=8, fill="#e8f5e9", stroke="#2e7d32", bold=True)
    h_box, _, _ = textbox(400, 70, "Хост / Клієнтський агент\n(Операційна система)", size=13, pad=8, fill="#e3f2fd", stroke="#1565c0", bold=True)
    t_box, _, _ = textbox(680, 70, "Апаратний TPM 2.0\n(Кремнієвий якір)", size=13, pad=8, fill="#fff3e0", stroke="#e65100", bold=True)
    out.append(v_box)
    out.append(h_box)
    out.append(t_box)

    # Lifelines - broken around textboxes to prevent line-text collisions
    out.append(line(120, 105, 120, 355, color="#90a4ae", sw=1.5, dash="4,4"))
    out.append(line(120, 460, 120, 495, color="#90a4ae", sw=1.5, dash="4,4"))

    out.append(line(400, 105, 400, 495, color="#90a4ae", sw=1.5, dash="4,4"))

    out.append(line(680, 105, 680, 195, color="#90a4ae", sw=1.5, dash="4,4"))
    out.append(line(680, 265, 680, 495, color="#90a4ae", sw=1.5, dash="4,4"))

    # Step 1: Challenge
    out.append(arrow(120, 140, 395, 140, color="#2e7d32", sw=1.6))
    out.append(text(260, 130, "1. Challenge (Nonce + PCR Selection)", size=11, bold=True, color="#1b5e20", anchor="middle"))

    # Step 2: Forward to TPM
    out.append(arrow(400, 180, 675, 180, color="#1565c0", sw=1.6))
    out.append(text(540, 170, "2. TPM2_Quote(AK_handle, Nonce, PCRs)", size=11, bold=True, color="#0d47a1", anchor="middle"))

    # Internal TPM Action
    tpm_action, _, _ = textbox(680, 230, "TPM формує TPMS_ATTEST\nгешує вибрані PCR\nпідписує приватним AK", size=10, pad=6, fill="#ffe0b2", stroke="#fb8c00")
    out.append(tpm_action)

    # Step 3: TPM response
    out.append(arrow(680, 280, 405, 280, color="#e65100", sw=1.6))
    out.append(text(540, 270, "3. TPM2B_ATTEST + TPMT_SIGNATURE", size=11, bold=True, color="#bf360c", anchor="middle"))

    # Step 4: Host to Verifier
    out.append(arrow(400, 340, 125, 340, color="#1565c0", sw=1.6))
    out.append(text(260, 330, "4. Quote + TCG Event Log", size=11, bold=True, color="#0d47a1", anchor="middle"))

    # Verifier Action
    ver_action, _, _ = textbox(120, 410, "Верифікація:\n1. Перевірка підпису AK\n2. Перевірка Nonce\n3. Відтворення Event Log\n4. Звірка з еталоном RIM", size=10, pad=6, fill="#c8e6c9", stroke="#388e3c")
    out.append(ver_action)

    # Step 5: Trust Decision
    out.append(arrow(120, 475, 395, 475, color="#2e7d32", sw=1.6))
    out.append(text(260, 465, "5. Рішення про довіру (mTLS / Сесійний токен)", size=11, bold=True, color="#1b5e20", anchor="middle"))

    return "\n".join(out)

def fig_pcr_extend():
    out = []
    out.append(rect(0, 0, 820, 480, fill="#ffffff", stroke="#ffffff", rx=0))
    out.append(text(410, 30, "Формування регістра PCR та верифікація через TCG Event Log", size=18, bold=True, anchor="middle"))

    out.append(rect(30, 60, 360, 395, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    out.append(text(210, 85, "Апаратне вимірювання на пристрої", size=14, bold=True, color="#0f172a", anchor="middle"))

    b1, _, _ = textbox(210, 130, "Stage 0: CRTM / UEFI Firmware ROM\nВимірює завантажувач: Digest D0", size=11, pad=6, fill="#e2e8f0", stroke="#64748b")
    b2, _, _ = textbox(210, 210, "Stage 1: GRUB / Shim Bootloader\nВимірює ядро та UKI: Digest D1", size=11, pad=6, fill="#e2e8f0", stroke="#64748b")
    b3, _, _ = textbox(210, 290, "Stage 2: Linux Kernel & Initrd\nВимірює модулі й IMA: Digest D2", size=11, pad=6, fill="#e2e8f0", stroke="#64748b")
    out.append(b1)
    out.append(b2)
    out.append(b3)

    out.append(arrow(210, 155, 210, 185, color="#475569", sw=1.4))
    out.append(arrow(210, 235, 210, 265, color="#475569", sw=1.4))

    op_box, _, _ = textbox(210, 385, "Операція в чипі: PCR_new = SHA256(PCR_old || Dn)\nНеможливо стерти чи повернути стан назад", size=10, pad=8, fill="#fee2e2", stroke="#dc2626", bold=True)
    out.append(op_box)
    out.append(arrow(210, 320, 210, 355, color="#dc2626", sw=1.4))

    out.append(rect(430, 60, 360, 395, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    out.append(text(610, 85, "Відтворення журналу верифікатором (Replay)", size=14, bold=True, color="#14532d", anchor="middle"))

    v1, _, _ = textbox(610, 130, "TCG Event Log: Подія 0 (Firmware)\nХеш: D0 → PCR_exp = SHA256(00..00 || D0)", size=10, pad=6, fill="#dcfce7", stroke="#22c55e")
    v2, _, _ = textbox(610, 210, "TCG Event Log: Подія 1 (Bootloader)\nХеш: D1 → PCR_exp = SHA256(PCR_exp || D1)", size=10, pad=6, fill="#dcfce7", stroke="#22c55e")
    v3, _, _ = textbox(610, 290, "TCG Event Log: Подія 2 (Kernel & Config)\nХеш: D2 → PCR_exp = SHA256(PCR_exp || D2)", size=10, pad=6, fill="#dcfce7", stroke="#22c55e")
    out.append(v1)
    out.append(v2)
    out.append(v3)

    out.append(arrow(610, 155, 610, 185, color="#16a34a", sw=1.4))
    out.append(arrow(610, 235, 610, 265, color="#16a34a", sw=1.4))

    cmp_box, _, _ = textbox(610, 385, "Порівняння: PCR_expected == Quoted_PCR_digest\nЗвірка кожної події з базою еталонів RIM", size=10, pad=8, fill="#bbf7d0", stroke="#15803d", bold=True)
    out.append(cmp_box)
    out.append(arrow(610, 320, 610, 355, color="#15803d", sw=1.4))

    return "\n".join(out)

def fig_credential_activation():
    out = []
    out.append(rect(0, 0, 820, 480, fill="#ffffff", stroke="#ffffff", rx=0))
    out.append(text(410, 30, "Двофазна процедура активації облікових даних (Credential Activation)", size=18, bold=True, anchor="middle"))

    out.append(rect(30, 60, 360, 395, fill="#fdf4ff", stroke="#f0abfc", sw=1.5, rx=8))
    out.append(text(210, 85, "Фаза 1: Верифікатор (TPM2_MakeCredential)", size=13, bold=True, color="#701a75", anchor="middle"))

    m1, _, _ = textbox(210, 130, "Вхідні дані:\n• Сертифікат EK-Cert (Публічний EK_pub)\n• Згенерований клієнтом публічний AK_pub\n• Обчислене ім'я Name(AK) = SHA256(AK_pub)", size=10, pad=6, fill="#fae8ff", stroke="#d946ef")
    m2, _, _ = textbox(210, 220, "Генерація симетричного секрету K\nта зашифрування під захистом Name(AK):\nФормування TPM2B_ID_OBJECT", size=10, pad=6, fill="#fae8ff", stroke="#d946ef")
    m3, _, _ = textbox(210, 310, "Асиметричне шифрування ключа K\nна публічному ключі EK_pub:\nФормування TPM2B_ENCRYPTED_SECRET", size=10, pad=6, fill="#fae8ff", stroke="#d946ef")
    m4, _, _ = textbox(210, 400, "Вихід: Пакет {ID_Object, Encrypted_Secret}\nПередається клієнту через мережу", size=10, pad=6, fill="#e879f9", stroke="#a21caf", bold=True)
    
    out.append(m1)
    out.append(m2)
    out.append(m3)
    out.append(m4)
    out.append(arrow(210, 175, 210, 195, color="#a21caf", sw=1.4))
    out.append(arrow(210, 260, 210, 285, color="#a21caf", sw=1.4))
    out.append(arrow(210, 350, 210, 375, color="#a21caf", sw=1.4))

    out.append(rect(430, 60, 360, 395, fill="#fffbeb", stroke="#fde68a", sw=1.5, rx=8))
    out.append(text(610, 85, "Фаза 2: Чип TPM (TPM2_ActivateCredential)", size=13, bold=True, color="#78350f", anchor="middle"))

    a1, _, _ = textbox(610, 130, "Прийом пакетів усередину чипа:\nКлієнт передає сесійні дескриптори\nHandle(AK) та Handle(EK)", size=10, pad=6, fill="#fef3c7", stroke="#f59e0b")
    a2, _, _ = textbox(610, 220, "Розшифрування ключа K:\nЧип використовує апаратний приватний EK_priv\nдля зняття асиметричного шару", size=10, pad=6, fill="#fef3c7", stroke="#f59e0b")
    a3, _, _ = textbox(610, 310, "Перевірка прив'язки до AK:\nЧип розшифровує ID_Object лише якщо\nім'я завантаженого AK тотожне Name(AK)", size=10, pad=6, fill="#fef3c7", stroke="#f59e0b")
    a4, _, _ = textbox(610, 400, "Результат: Відновлений секрет K\nКлієнт повертає K верифікатору як доказ,\nщо AK створено саме на цьому чипі", size=10, pad=6, fill="#fcd34d", stroke="#d97706", bold=True)

    out.append(a1)
    out.append(a2)
    out.append(a3)
    out.append(a4)
    out.append(arrow(610, 170, 610, 195, color="#d97706", sw=1.4))
    out.append(arrow(610, 260, 610, 285, color="#d97706", sw=1.4))
    out.append(arrow(610, 355, 610, 375, color="#d97706", sw=1.4))

    return "\n".join(out)

if __name__ == "__main__":
    IMG = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(IMG, exist_ok=True)
    render(os.path.join(IMG, 'attestation-protocol-flow.svg'), 800, 520, fig_attestation_protocol())
    render(os.path.join(IMG, 'pcr-extend-and-eventlog.svg'), 820, 480, fig_pcr_extend())
    render(os.path.join(IMG, 'tpm2-credential-activation.svg'), 820, 480, fig_credential_activation())

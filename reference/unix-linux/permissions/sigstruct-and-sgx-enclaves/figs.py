import os
import sys

# Path to scripts directory at repo root
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
scripts_dir = os.path.join(repo_root, "scripts")
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

from svgkit import render, rect, text, line, arrow, fitbox, FILL, BG, INK, LINE, MUTED, POS, FIELD

def build_sgx_arch_fig(filename):
    w, h = 820, 460
    frags = []

    # Title
    frags.append(text(410, 25, "Апаратна межа захисту Intel SGX: MEE, EPC та EPCM", size=16, bold=True, color=INK))

    # Untrusted Domain (OS/Hypervisor)
    frags.append(rect(20, 55, 370, 385, fill="#fdf2f2", stroke=POS, sw=2, rx=8))
    frags.append(text(205, 80, "Недовірена зона (Ring 0 / ОС / Гіпервізор)", size=13, bold=True, color=POS))

    # OS Page Tables
    frags.append(fitbox(35, 105, 340, 75, "Таблиці сторінок ОС (Page Tables)\nФізична адресація сторінок EPC у RAM", size=12, fill="#ffffff", stroke="#d9534f", color=INK))

    # RAM Direct Access Blocked
    frags.append(fitbox(35, 195, 340, 80, "Спроба прямого доступу ОС до EPC\nБлокується апаратно → повертає 0xFF...FF", size=12, fill="#f9ebe8", stroke=POS, color=POS, bold=True))

    # System DRAM (PRM & EPC)
    frags.append(fitbox(35, 290, 340, 135, "Системна оперативна пам'ять DRAM\n\n• Звичайна пам'ять (відкрита для ОС)\n• PRM (Processor Reserved Memory)\n  └─ EPC (Enclave Page Cache)\n     [Шифрований вміст в RAM]", size=11, fill="#ffffff", stroke=LINE, color=INK))

    # Hardware Trusted CPU Boundary
    frags.append(rect(430, 55, 370, 385, fill="#edf7ed", stroke=FIELD, sw=2, rx=8))
    frags.append(text(615, 80, "Довірена апаратна межа CPU (Hardware TCB)", size=13, bold=True, color=FIELD))

    # CPU Core & Enclave Exec Mode
    frags.append(fitbox(445, 105, 340, 75, "Ядра CPU (Enclave Mode)\nВиконання інструкцій ENCLU (EENTER/EEXIT)", size=12, fill="#ffffff", stroke=FIELD, color=INK))

    # EPCM Table
    frags.append(fitbox(445, 195, 340, 115, "EPCM (Enclave Page Cache Map)\n\n• Перевірка належності сторінки енклаву\n• Збіг віртуальної адреси (ELRANGE)\n• Права доступу (R, W, X) та тип (SECS/TCS/REG)", size=11, fill="#e8f5e9", stroke=FIELD, color=INK))

    # MEE
    frags.append(fitbox(445, 325, 340, 100, "MEE (Memory Encryption Engine)\n\n• AES-CTR шифрування трафіку до DRAM\n• Дерево Меркла для захисту цілісності\n• Ключі шифрування не покидають процесор", size=11, fill="#ffffff", stroke=FIELD, color=INK))

    # Connectors
    frags.append(arrow(375, 142, 445, 142, color=LINE, sw=1.8))
    frags.append(line(445, 375, 375, 375, color=FIELD, sw=1.8, dash="4,4"))

    render(filename, w, h, *frags)

def build_sigstruct_flow_fig(filename):
    w, h = 820, 440
    frags = []

    # Title
    frags.append(text(410, 25, "Алгоритм криптографічної верифікації SIGSTRUCT в інструкції EINIT", size=16, bold=True, color=INK))

    # Step 1: RSA Signature Verification
    frags.append(fitbox(30, 60, 360, 100, "1. Перевірка RSA-3072 підпису\n\nПеревірка SIGNATURE за допомогою\nMODULUS та EXPONENT із SIGSTRUCT", size=12, fill="#f4f6f8", stroke=LINE, color=INK))

    # Step 2: MRSIGNER & Launch Control
    frags.append(fitbox(430, 60, 360, 100, "2. Перевірка MRSIGNER та FLC\n\nSHA-256(MODULUS) == MRSIGNER\nЗбіг з MSR IA32_SGXLEPUBKEYHASH", size=12, fill="#f4f6f8", stroke=LINE, color=INK))

    # Arrow 1 -> 2
    frags.append(arrow(390, 110, 430, 110, color=LINE, sw=1.8))

    # Step 3: MRENCLAVE match
    frags.append(fitbox(30, 205, 360, 110, "3. Зіставлення вимірювань коду\n\nОбчислений при EADD/EEXTEND хеш MRENCLAVE\n== SIGSTRUCT.ENCLAVEHASH", size=12, fill="#f4f6f8", stroke=LINE, color=INK))

    # Arrow 2 -> 3
    frags.append(line(610, 160, 610, 185, color=LINE, sw=1.8))
    frags.append(line(610, 185, 210, 185, color=LINE, sw=1.8))
    frags.append(arrow(210, 185, 210, 205, color=LINE, sw=1.8))

    # Step 4: SVN & Attributes
    frags.append(fitbox(430, 205, 360, 110, "4. Перевірка версії та атрибутів\n\nISVSVN >= мінімальний SVN обладнання\nЗбіг ATTRIBUTES (DEBUG / KSS прапори)", size=12, fill="#f4f6f8", stroke=LINE, color=INK))

    # Arrow 3 -> 4
    frags.append(arrow(390, 260, 430, 260, color=LINE, sw=1.8))

    # Final Outcome: Initialization Success
    frags.append(fitbox(180, 345, 460, 75, "ІНІЦІАЛІЗАЦІЯ ЕНКЛАВА УСПІШНА\n\nSECS.VALID = 1 → Активація виконання через EENTER", size=13, fill="#edf7ed", stroke=FIELD, color=FIELD, bold=True))

    # Arrow 4 -> Final
    frags.append(line(610, 315, 610, 330, color=FIELD, sw=1.8))
    frags.append(line(610, 330, 410, 330, color=FIELD, sw=1.8))
    frags.append(arrow(410, 330, 410, 345, color=FIELD, sw=1.8))

    render(filename, w, h, *frags)

def generate_all():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)

    fig1 = os.path.join(img_dir, "sgx-architecture-epc.svg")
    fig2 = os.path.join(img_dir, "sigstruct-verification-flow.svg")

    build_sgx_arch_fig(fig1)
    build_sigstruct_flow_fig(fig2)
    print("SVGs successfully generated!")

if __name__ == "__main__":
    generate_all()

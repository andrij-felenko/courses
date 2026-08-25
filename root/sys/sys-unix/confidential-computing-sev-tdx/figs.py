# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE   = "#eaf0fd"
GREEN  = "#eaf6ef"
WARM   = "#fff6e5"
RED    = "#fdecea"
GREY   = "#eceff1"
PURPLE = "#f3e8ff"

def fig_sev_snp_vs_tdx_architecture():
    W, H = 1200, 720
    p = []

    # Title
    f_hdr, _, _ = textbox(W / 2, 40, ["Архітектурне порівняння захисту пам'яті: AMD SEV-SNP проти Intel TDX"], size=16, bold=True, fill=WARM, stroke=LINE)
    p.append(f_hdr)

    # Column 1: AMD SEV-SNP (Left)
    cx_amd = 320
    f_amd_hdr, _, _ = textbox(cx_amd, 110, ["AMD SEV-SNP (Secure Nested Paging)", "Апаратний захист цілісності та шифрування"], size=14, bold=True, fill=GREEN, stroke=LINE)
    p.append(f_amd_hdr)

    f_amd_vm, _, _ = textbox(cx_amd, 210, ["Конфіденційна ВМ (Guest VM)", "Зашифрована пам'ять (AES-128/256)", "Захищений стан CPU (VMSA) & VMPL 0..3"], size=13, fill=BLUE, stroke=LINE)
    p.append(f_amd_vm)

    f_amd_rmp, _, _ = textbox(cx_amd, 340, ["Reverse Map Table (RMP)", "Апаратна таблиця цілісності пам'яті", "Запобігання aliasing та remapping атак"], size=13, fill=PURPLE, stroke=LINE)
    p.append(f_amd_rmp)

    f_amd_asp, _, _ = textbox(cx_amd, 470, ["AMD Secure Processor (ASP / PSP)", "Криптографічний співпроцесор (ARM Cortex-A5)", "Управління ключами та віддалена атестація"], size=13, fill=WARM, stroke=LINE)
    p.append(f_amd_asp)

    f_amd_host, _, _ = textbox(cx_amd, 600, ["Недовірений гіпервізор (KVM / QEMU)", "Управління ресурсами без доступу до даних", "Обмін через незашифровані буфери GHCB"], size=13, fill=RED, stroke=LINE)
    p.append(f_amd_host)

    # Arrows AMD
    p.append(arrow(cx_amd, 135, cx_amd, 185))
    p.append(arrow(cx_amd, 235, cx_amd, 315))
    p.append(arrow(cx_amd, 365, cx_amd, 445))
    p.append(arrow(cx_amd, 495, cx_amd, 575))

    # Column 2: Intel TDX (Right)
    cx_intel = 880
    f_intel_hdr, _, _ = textbox(cx_intel, 110, ["Intel TDX (Trust Domain Extensions)", "Ізоляція віртуальних машин через SEAM"], size=14, bold=True, fill=GREEN, stroke=LINE)
    p.append(f_intel_hdr)

    f_intel_td, _, _ = textbox(cx_intel, 210, ["Trust Domain (TD Guest VM)", "Шифрування пам'яті MKTME (KeyID)", "Захищений стан регістрів (TDVPS)"], size=13, fill=BLUE, stroke=LINE)
    p.append(f_intel_td)

    f_intel_mod, _, _ = textbox(cx_intel, 340, ["Intel TDX Module (SEAM Mode)", "Підписана мікропрограма Intel у захищеному режимі", "Обробка перемикань контексту та S-EPT"], size=13, fill=PURPLE, stroke=LINE)
    p.append(f_intel_mod)

    f_intel_mktme, _, _ = textbox(cx_intel, 470, ["Контролер пам'яті MKTME / AES-XTS", "Апаратний криптографічний рушій DRAM", "Апаратний захист цілісності та ключів"], size=13, fill=WARM, stroke=LINE)
    p.append(f_intel_mktme)

    f_intel_host, _, _ = textbox(cx_intel, 600, ["Недовірений гіпервізор (KVM / QEMU)", "Виклики SEAMCALL для управління ВМ", "Відсутність прямого доступу до сторінок TD"], size=13, fill=RED, stroke=LINE)
    p.append(f_intel_host)

    # Arrows Intel
    p.append(arrow(cx_intel, 135, cx_intel, 185))
    p.append(arrow(cx_intel, 235, cx_intel, 315))
    p.append(arrow(cx_intel, 365, cx_intel, 445))
    p.append(arrow(cx_intel, 495, cx_intel, 575))

    out_path = os.path.join(IMG, 'sev-snp-vs-tdx-architecture.svg')
    render(out_path, W, H, *p)
    print(f"Generated {out_path}")

def fig_attestation_chain_flow():
    W, H = 1150, 680
    p = []

    # Title
    f_hdr, _, _ = textbox(W / 2, 40, ["Процес віддаленої атестації та передачі секретів (Remote Attestation Flow)"], size=16, bold=True, fill=WARM, stroke=LINE)
    p.append(f_hdr)

    # Participant boxes across top
    f_p1, _, _ = textbox(150, 110, ["Гостьова ОС", "(/dev/sev-guest або /dev/tdx-guest)"], size=13, bold=True, fill=BLUE, stroke=LINE)
    p.append(f_p1)

    f_p2, _, _ = textbox(480, 110, ["Апаратне забезпечення", "(ASP / Intel TDX Module)"], size=13, bold=True, fill=GREEN, stroke=LINE)
    p.append(f_p2)

    f_p3, _, _ = textbox(820, 110, ["Сервер атестації", "(Relying Party / KMS)"], size=13, bold=True, fill=PURPLE, stroke=LINE)
    p.append(f_p3)

    # Sequence steps (vertical Y)
    # Step 1: Request report
    f_s1, _, _ = textbox(315, 200, ["1. ioctl(GET_REPORT, nonce)", "Запит атестаційного звіту з виміром ВМ"], size=12, fill=FILL, stroke=LINE)
    p.append(f_s1)
    p.append(arrow(150, 135, 150, 200))
    p.append(arrow(150, 200, 480, 200))

    # Step 2: Hardware generates signed report
    f_s2, _, _ = textbox(480, 290, ["2. Підписання виміру (Launch Digest)", "Підпис апаратним ключем (VCEK / PCK)"], size=12, fill=WARM, stroke=LINE)
    p.append(f_s2)
    p.append(arrow(480, 225, 480, 265))

    # Step 3: Return report to guest
    f_s3, _, _ = textbox(315, 370, ["3. Повернення Attestation Report / Quote", "Передача підписаного блоку гостю"], size=12, fill=FILL, stroke=LINE)
    p.append(f_s3)
    p.append(arrow(480, 315, 480, 370))
    p.append(arrow(480, 370, 150, 370))

    # Step 4: Guest sends quote to relying party
    f_s4, _, _ = textbox(480, 460, ["4. Надсилання Quote по мережі (TLS)", "Передача звіту та nonce до KMS"], size=12, fill=FILL, stroke=LINE)
    p.append(f_s4)
    p.append(arrow(150, 395, 150, 460))
    p.append(arrow(150, 460, 820, 460))

    # Step 5: Relying party verifies signature & injects secret
    f_s5, _, _ = textbox(820, 540, ["5. Перевірка підпису через CA AMD/Intel", "Звірення виміру та надання ключів LUKS/TLS"], size=12, fill=GREEN, stroke=LINE)
    p.append(f_s5)
    p.append(arrow(820, 485, 820, 515))

    # Step 6: Secret Injection back
    f_s6, _, _ = textbox(485, 620, ["6. Передача секретів у захищений тунель ВМ", "Розблокування дисків та запуск служб"], size=12, fill=BLUE, stroke=LINE)
    p.append(f_s6)
    p.append(arrow(820, 565, 820, 620))
    p.append(arrow(820, 620, 150, 620))

    out_path = os.path.join(IMG, 'attestation-chain-flow.svg')
    render(out_path, W, H, *p)
    print(f"Generated {out_path}")

if __name__ == '__main__':
    fig_sev_snp_vs_tdx_architecture()
    fig_attestation_chain_flow()

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
import svgkit

def fig_ima_arch():
    out = []
    # Background
    out.append(svgkit.rect(0, 0, 800, 420, fill="#ffffff", stroke="none"))
    
    # Title / Boundary Box: Userspace
    out.append(svgkit.rect(20, 20, 760, 60, fill="#f8f9fa", stroke="#ced4da", rx=6))
    out.append(svgkit.text(400, 42, "User Space (Ппростір користувача)", bold=True, size=15))
    out.append(svgkit.text(400, 60, "Процеси (execve / open), udev, evmctl, keyctl", size=12, color="#495057"))
    
    # Boundary Box: Kernel Space
    out.append(svgkit.rect(20, 95, 760, 215, fill="#f1f3f5", stroke="#adb5bd", rx=6))
    out.append(svgkit.text(400, 115, "Kernel Space (Ядро Linux & VFS)", bold=True, size=15))
    
    # VFS Box
    out.append(svgkit.rect(40, 135, 140, 60, fill="#ffffff", stroke="#495057", rx=5))
    out.append(svgkit.text(110, 160, "VFS Hooks", bold=True, size=13))
    out.append(svgkit.text(110, 178, "sys_execve / open", size=11, color="#6c757d"))
    
    # LSM Box
    out.append(svgkit.rect(210, 135, 120, 60, fill="#e7f5ff", stroke="#1c7ed6", rx=5))
    out.append(svgkit.text(270, 160, "LSM Framework", bold=True, size=12, color="#1864ab"))
    out.append(svgkit.text(270, 178, "SELinux / AppArmor", size=10, color="#1c7ed6"))

    # IMA Box
    out.append(svgkit.rect(350, 135, 190, 160, fill="#e6fcf5", stroke="#0ca678", sw=2, rx=5))
    out.append(svgkit.text(445, 155, "IMA Subsystem", bold=True, size=14, color="#099268"))
    out.append(svgkit.rect(365, 170, 160, 32, fill="#ffffff", stroke="#20c997", rx=3))
    out.append(svgkit.text(445, 190, "Measurement (PCR 10)", size=11))
    out.append(svgkit.rect(365, 210, 160, 32, fill="#ffffff", stroke="#20c997", rx=3))
    out.append(svgkit.text(445, 230, "Appraisal (security.ima)", size=11))
    out.append(svgkit.rect(365, 250, 160, 32, fill="#ffffff", stroke="#20c997", rx=3))
    out.append(svgkit.text(445, 270, "Audit (audit.log)", size=11))
    
    # EVM Box
    out.append(svgkit.rect(560, 135, 200, 160, fill="#fff9db", stroke="#f59f00", sw=2, rx=5))
    out.append(svgkit.text(660, 155, "EVM Subsystem", bold=True, size=14, color="#d9480f"))
    out.append(svgkit.text(660, 180, "Захист xattrs:", size=11, bold=True))
    out.append(svgkit.text(660, 200, "security.ima, selinux,", size=10))
    out.append(svgkit.text(660, 215, "capability, SMACK64", size=10))
    out.append(svgkit.text(660, 240, "+ i_ino, i_generation,", size=10))
    out.append(svgkit.text(660, 255, "i_uid, i_gid, i_mode", size=10))
    out.append(svgkit.text(660, 275, "HMAC / Digital Sig", size=11, bold=True, color="#e65c00"))

    # Boundary Box: Hardware & Keyrings
    out.append(svgkit.rect(20, 320, 760, 80, fill="#f8f0fc", stroke="#ae3ec9", rx=6))
    
    # TPM Box
    out.append(svgkit.rect(40, 335, 340, 50, fill="#ffffff", stroke="#ae3ec9", sw=2, rx=5))
    out.append(svgkit.text(210, 357, "TPM 2.0 (Hardware Root of Trust)", bold=True, size=13, color="#862e9c"))
    out.append(svgkit.text(210, 373, "PCR 10 (IMA) + Sealed Storage Key (EVM HMAC)", size=11, color="#495057"))

    # Keyrings Box
    out.append(svgkit.rect(410, 335, 350, 50, fill="#ffffff", stroke="#7048e8", sw=2, rx=5))
    out.append(svgkit.text(585, 357, "Kernel Keyrings (.ima / .evm)", bold=True, size=13, color="#5f3dc4"))
    out.append(svgkit.text(585, 373, "X.509 Сертифікати / Публічні ключі RSA/ECDSA", size=11, color="#495057"))

    # Connections / Arrows
    out.append(svgkit.arrow(180, 165, 210, 165)) # VFS to LSM
    out.append(svgkit.arrow(330, 165, 350, 165)) # LSM to IMA
    out.append(svgkit.arrow(540, 190, 560, 190)) # IMA to EVM
    out.append(svgkit.arrow(445, 295, 210, 335)) # IMA to TPM PCR
    out.append(svgkit.arrow(660, 295, 585, 335)) # EVM to Keyring

    return out

def fig_ima_evm_flow():
    out = []
    out.append(svgkit.rect(0, 0, 800, 300, fill="#ffffff", stroke="none"))
    out.append(svgkit.text(400, 25, "Конвеєр перевірки цілісності при відкритті файлу VFS", bold=True, size=15))

    # Step 1: Open call
    out.append(svgkit.rect(30, 60, 120, 70, fill="#e7f5ff", stroke="#1c7ed6", rx=5))
    out.append(svgkit.text(90, 85, "1. VFS Open", bold=True, size=12))
    out.append(svgkit.text(90, 105, "sys_open / execve", size=10))

    # Step 2: EVM verify
    out.append(svgkit.rect(180, 60, 140, 70, fill="#fff9db", stroke="#f59f00", rx=5))
    out.append(svgkit.text(250, 85, "2. EVM Verify", bold=True, size=12))
    out.append(svgkit.text(250, 105, "evm_verifyxattr()", size=10))
    out.append(svgkit.text(250, 118, "Перевірка security.evm", size=9, color="#d9480f"))

    # Step 3: IMA Appraisal
    out.append(svgkit.rect(350, 60, 140, 70, fill="#e6fcf5", stroke="#0ca678", rx=5))
    out.append(svgkit.text(420, 85, "3. IMA Appraisal", bold=True, size=12))
    out.append(svgkit.text(420, 105, "ima_appraise()", size=10))
    out.append(svgkit.text(420, 118, "Хеш вмісту vs security.ima", size=9, color="#099268"))

    # Step 4: IMA Measure
    out.append(svgkit.rect(520, 60, 130, 70, fill="#f3d9fa", stroke="#ae3ec9", rx=5))
    out.append(svgkit.text(585, 85, "4. IMA Measure", bold=True, size=12))
    out.append(svgkit.text(585, 105, "TPM PCR 10 Extend", size=10))
    out.append(svgkit.text(585, 118, "+ ascii_measurements", size=9, color="#862e9c"))

    # Step 5: Decision
    out.append(svgkit.rect(680, 60, 90, 70, fill="#d3f9d8", stroke="#2b8a3e", rx=5))
    out.append(svgkit.text(725, 95, "5. Доступ", bold=True, size=12, color="#2b8a3e"))
    out.append(svgkit.text(725, 112, "Дозволено", size=10))

    # Flow arrows
    out.append(svgkit.arrow(150, 95, 180, 95))
    out.append(svgkit.arrow(320, 95, 350, 95))
    out.append(svgkit.arrow(490, 95, 520, 95))
    out.append(svgkit.arrow(650, 95, 680, 95))

    # Error path box below
    out.append(svgkit.rect(180, 180, 470, 70, fill="#ffe3e3", stroke="#e03131", rx=5))
    out.append(svgkit.text(415, 205, "Помилка цілісності (Невідповідність HMAC / підпису / хешу)", bold=True, size=12, color="#c92a2a"))
    out.append(svgkit.text(415, 225, "Блокування виклику: повернення -EACCES / -EPERM + Запис в audit.log", size=11, color="#a51d24"))

    # Error arrows down
    out.append(svgkit.arrow(250, 130, 250, 180, color="#e03131"))
    out.append(svgkit.arrow(420, 130, 420, 180, color="#e03131"))

    return out

def render():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    
    frags_arch = fig_ima_arch()
    out_arch = os.path.join(img_dir, "ima-arch.svg")
    svgkit.render(out_arch, 800, 420, *frags_arch)

    frags_flow = fig_ima_evm_flow()
    out_flow = os.path.join(img_dir, "ima-evm-flow.svg")
    svgkit.render(out_flow, 800, 300, *frags_flow)

if __name__ == "__main__":
    render()

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
import svgkit

def draw_arch():
    out = []
    w_canvas = 680
    h_canvas = 650

    # Background
    out.append(svgkit.rect(0, 0, w_canvas, h_canvas, fill="#ffffff", stroke="none"))

    # Title
    out.append(svgkit.text(340, 30, "Підсистема HWRNG та Entropy Pool у Linux", bold=True, size=18, anchor="middle"))

    # 1. Hardware layer box
    out.append(svgkit.rect(30, 55, 620, 105, fill="#f8f9fa", stroke="#6c757d", sw=1.5, rx=8))
    out.append(svgkit.text(50, 85, "Апаратний рівень (Hardware)", bold=True, size=13, anchor="start", color="#495057"))

    t1, _, _ = svgkit.textbox(130, 120, "CPU RNG\n(RDRAND / RDSEED)", size=12, pad=6, fill="#e3f2fd", stroke="#1565c0", rx=5)
    out.append(t1)

    t2, _, _ = svgkit.textbox(340, 120, "Апаратний TRNG\n(SoC / TPM 2.0)", size=12, pad=6, fill="#e3f2fd", stroke="#1565c0", rx=5)
    out.append(t2)

    t3, _, _ = svgkit.textbox(550, 120, "Джерела шуму\n(IRQ / Jitter)", size=12, pad=6, fill="#e3f2fd", stroke="#1565c0", rx=5)
    out.append(t3)

    # 2. Kernel Space box
    out.append(svgkit.rect(30, 180, 620, 270, fill="#fff8e1", stroke="#ffa000", sw=1.5, rx=8))
    out.append(svgkit.text(50, 212, "Рівень Ядра (Kernel Space)", bold=True, size=13, anchor="start", color="#e65100"))

    t4, _, _ = svgkit.textbox(340, 240, "hwrng core framework\n(/dev/hwrng driver interface)", size=12, pad=8, fill="#ffe0b2", stroke="#f57c00", rx=5)
    out.append(t4)

    t5, _, _ = svgkit.textbox(440, 315, "add_hwgenerator_randomness()\nBLAKE2s Entropy Mixer", size=12, pad=8, fill="#d1c4e9", stroke="#512da8", rx=5)
    out.append(t5)

    t6, _, _ = svgkit.textbox(220, 390, "Entropy Pool (crng state)\n256-bit Entropy Pool", size=12, pad=8, fill="#c8e6c9", stroke="#2e7d32", bold=True, rx=5)
    out.append(t6)

    t7, _, _ = svgkit.textbox(510, 390, "ChaCha20 CSPRNG\n(crng_reseed 5 min)", size=12, pad=8, fill="#a5d6a7", stroke="#1b5e20", rx=5)
    out.append(t7)

    # 3. User Space box
    out.append(svgkit.rect(30, 470, 620, 150, fill="#f3e5f5", stroke="#8e24aa", sw=1.5, rx=8))
    out.append(svgkit.text(50, 502, "Простір Користувача (User Space)", bold=True, size=13, anchor="start", color="#4a148c"))

    t8, _, _ = svgkit.textbox(140, 550, "rngd (rng-tools)\nFIPS 140-2 Validation", size=12, pad=8, fill="#e1bee7", stroke="#7b1fa2", rx=5)
    out.append(t8)

    t9, _, _ = svgkit.textbox(470, 550, "Криптографічні застосунки\ngetrandom() / /dev/urandom", size=12, pad=8, fill="#e1bee7", stroke="#7b1fa2", rx=5)
    out.append(t9)

    # Arrows
    out.append(svgkit.arrow(130, 140, 130, 350, color="#1565c0"))
    out.append(svgkit.arrow(130, 350, 140, 360, color="#1565c0"))

    out.append(svgkit.arrow(340, 140, 340, 205, color="#1565c0"))

    out.append(svgkit.arrow(550, 140, 550, 275, color="#1565c0"))
    out.append(svgkit.arrow(550, 275, 530, 285, color="#1565c0"))

    out.append(svgkit.arrow(340, 255, 390, 280, color="#e65100"))

    out.append(svgkit.arrow(220, 230, 20, 230, color="#e65100"))
    out.append(svgkit.arrow(20, 230, 20, 550, color="#e65100"))
    out.append(svgkit.arrow(20, 550, 80, 550, color="#e65100"))

    out.append(svgkit.arrow(440, 330, 310, 360, color="#512da8"))

    out.append(svgkit.arrow(190, 520, 210, 410, color="#7b1fa2"))

    out.append(svgkit.arrow(300, 380, 430, 380, color="#2e7d32"))

    out.append(svgkit.arrow(510, 405, 510, 525, color="#2e7d32"))

    return out

def render():
    frags = draw_arch()
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    out_path = os.path.join(img_dir, "hwrng-architecture.svg")
    svgkit.render(out_path, 680, 650, *frags)

if __name__ == "__main__":
    render()

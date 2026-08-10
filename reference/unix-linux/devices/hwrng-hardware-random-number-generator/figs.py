import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
import svgkit

def draw_arch():
    out = []
    # Background
    out.append(svgkit.rect(0, 0, 500, 600, fill="#ffffff", stroke="none"))
    
    # Titles
    out.append(svgkit.text(250, 30, "Архітектура RNG у Linux", bold=True, size=18, anchor="middle"))
    
    # Hardware layer
    out.append(svgkit.rect(50, 70, 400, 80, fill="#eeeeee", stroke="#999999", sw=2))
    out.append(svgkit.text(250, 95, "Апаратний рівень (Hardware)", bold=True, size=14, anchor="middle"))
    
    out.append(svgkit.rect(70, 110, 150, 30, fill="#e1f5fe", stroke="#0288d1", sw=2))
    out.append(svgkit.text(145, 130, "CPU RNG (RDRAND)", size=12, anchor="middle"))
    
    out.append(svgkit.rect(280, 110, 150, 30, fill="#e1f5fe", stroke="#0288d1", sw=2))
    out.append(svgkit.text(355, 130, "TPM / HW RNG", size=12, anchor="middle"))
    
    # Kernel layer
    out.append(svgkit.rect(50, 190, 400, 250, fill="#fff3e0", stroke="#ff9800", sw=2))
    out.append(svgkit.text(250, 215, "Рівень Ядра (Kernel Space)", bold=True, size=14, anchor="middle"))
    
    out.append(svgkit.rect(280, 235, 150, 30, fill="#ffe0b2", stroke="#f57c00", sw=2))
    out.append(svgkit.text(355, 255, "hwrng core", size=12, anchor="middle"))
    
    out.append(svgkit.rect(70, 270, 150, 30, fill="#dcedc8", stroke="#689f38", sw=2))
    out.append(svgkit.text(145, 290, "Jitter / IRQ Events", size=12, anchor="middle"))
    
    out.append(svgkit.rect(175, 340, 150, 40, fill="#c8e6c9", stroke="#388e3c", sw=2))
    out.append(svgkit.text(250, 365, "Entropy Pool (crng)", bold=True, size=14, anchor="middle"))
    
    out.append(svgkit.rect(175, 400, 150, 30, fill="#f8bbd0", stroke="#c2185b", sw=2))
    out.append(svgkit.text(250, 420, "ChaCha20 CSPRNG", size=12, anchor="middle"))
    
    # User space layer
    out.append(svgkit.rect(50, 480, 400, 100, fill="#f3e5f5", stroke="#8e24aa", sw=2))
    out.append(svgkit.text(250, 505, "Простір Користувача (User Space)", bold=True, size=14, anchor="middle"))
    
    out.append(svgkit.rect(70, 530, 150, 30, fill="#ce93d8", stroke="#7b1fa2", sw=2))
    out.append(svgkit.text(145, 550, "rng-tools (rngd)", size=12, anchor="middle"))
    
    out.append(svgkit.rect(280, 530, 150, 30, fill="#ce93d8", stroke="#7b1fa2", sw=2))
    out.append(svgkit.text(355, 550, "/dev/random & urandom", size=12, anchor="middle"))
    
    # Arrows
    out.append(svgkit.arrow(355, 140, 355, 235))
    out.append(svgkit.arrow(145, 300, 145, 340))
    out.append(svgkit.arrow(250, 380, 250, 400))
    out.append(svgkit.arrow(250, 430, 250, 530))
    
    return out

def render():
    frags = draw_arch()
    out_path = os.path.join(os.path.dirname(__file__), "hwrng_architecture.svg")
    svgkit.render(out_path, 500, 600, *frags)

if __name__ == "__main__":
    render()

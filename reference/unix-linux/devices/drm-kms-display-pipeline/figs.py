# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def generate_kms_pipeline():
    w, h = 860, 360
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">',
           f'<rect width="{w}" height="{h}" fill="{BG}"/>']
    
    out.append('''<defs>
      <marker id="arrow" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#333333"/>
      </marker>
    </defs>''')

    out.append(text(w/2, 28, "Дисплейний конвеєр Kernel Mode Setting (KMS)", size=18, bold=True))

    out.append(rect(20, 60, 160, 260, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    out.append(text(100, 84, "Пам'ять (GEM / dma-buf)", size=13, color=MUTED, bold=True))
    
    fb1, _, _ = textbox(100, 130, "Primary FB\n3840×2160 ARGB", size=12, fill="#e0f2fe", stroke="#0284c7")
    fb2, _, _ = textbox(100, 200, "Overlay FB\n1920×1080 NV12", size=12, fill="#fef3c7", stroke="#d97706")
    fb3, _, _ = textbox(100, 270, "Cursor FB\n64×64 ARGB8888", size=12, fill="#f3e8ff", stroke="#9333ea")
    out.extend([fb1, fb2, fb3])

    out.append(rect(210, 60, 160, 260, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    out.append(text(290, 84, "Площини (Planes)", size=13, color=MUTED, bold=True))
    
    p1, _, _ = textbox(290, 130, "Primary Plane\nZ-Index: 0", size=12, fill="#bae6fd", stroke="#0284c7")
    p2, _, _ = textbox(290, 200, "Overlay Plane\nZ-Index: 1 (CSC)", size=12, fill="#fde68a", stroke="#d97706")
    p3, _, _ = textbox(290, 270, "Cursor Plane\nZ-Index: 2", size=12, fill="#e9d5ff", stroke="#9333ea")
    out.extend([p1, p2, p3])

    out.append(arrow(170, 130, 220, 130, color="#0284c7"))
    out.append(arrow(170, 200, 220, 200, color="#d97706"))
    out.append(arrow(170, 270, 220, 270, color="#9333ea"))

    crtc_box, _, _ = textbox(470, 200, "CRTC (Display Engine)\n• Змішування (Blending)\n• Колірна гама (LUT)\n• Хронометраж (VBlank/HSync)\n• Сканування: 3840×2160 @ 60Hz", size=13, fill="#dcfce7", stroke="#16a34a", pad=12, min_w=200)
    out.append(crtc_box)

    out.append(arrow(360, 130, 410, 175, color="#0284c7"))
    out.append(arrow(360, 200, 410, 200, color="#d97706"))
    out.append(arrow(360, 270, 410, 225, color="#9333ea"))

    enc_box, _, _ = textbox(635, 200, "Encoder\nTMDS / DP PHY\nСеріалізатор", size=12, fill="#ffedd5", stroke="#ea580c", pad=10, min_w=100)
    out.append(enc_box)
    out.append(arrow(570, 200, 585, 200, color="#16a34a"))

    conn_box, _, _ = textbox(770, 200, "Connector\nHDMI-A-1 / DP-1\nEDID + Hotplug", size=12, fill="#fee2e2", stroke="#dc2626", pad=10, min_w=110)
    out.append(conn_box)
    out.append(arrow(685, 200, 715, 200, color="#ea580c"))

    out.append("</svg>")
    return "\n".join(out)

def generate_atomic_commit_flow():
    w, h = 860, 320
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">',
           f'<rect width="{w}" height="{h}" fill="{BG}"/>']

    out.append('''<defs>
      <marker id="arrow" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#333333"/>
      </marker>
    </defs>''')

    out.append(text(w/2, 28, "Транзакційний процес Atomic KMS Commit (Two-Phase)", size=18, bold=True))

    b1, _, _ = textbox(110, 110, "1. Збірка стану\n`drmModeAtomicAlloc`\n`drmModeAtomicAddProperty`", size=12, fill="#e0f2fe", stroke="#0284c7", min_w=170)
    out.append(b1)

    b2, _, _ = textbox(320, 110, "2. Перевірка (Validation)\n`DRM_MODE_ATOMIC_\nTEST_ONLY`", size=12, fill="#fef3c7", stroke="#d97706", min_w=170)
    out.append(b2)
    out.append(arrow(195, 110, 235, 110))

    out.append(line(405, 110, 445, 110, sw=1.8))
    out.append(arrow(445, 110, 445, 180, color="#dc2626"))
    out.append(arrow(405, 110, 485, 110, color="#16a34a"))

    b_fail, _, _ = textbox(445, 230, "Невдача (EINVAL / EBUSY)\nFallback на SW Blending\nбез апаратних змін", size=11, fill="#fee2e2", stroke="#dc2626", min_w=170)
    out.append(b_fail)

    b3, _, _ = textbox(575, 110, "3. Атомарний коміт\n`DRM_MODE_ATOMIC_\nNONBLOCK`", size=12, fill="#dcfce7", stroke="#16a34a", min_w=160)
    out.append(b3)

    b4, _, _ = textbox(770, 110, "4. VBlank перемикання\nЗапис у регістри GPU\nПодія PAGE_FLIP_EVENT", size=11, fill="#f3e8ff", stroke="#9333ea", min_w=150)
    out.append(b4)
    out.append(arrow(655, 110, 695, 110))

    out.append(line(770, 160, 770, 280, color="#9333ea", sw=1.5, dash="4,4"))
    out.append(line(770, 280, 110, 280, color="#9333ea", sw=1.5, dash="4,4"))
    out.append(arrow(110, 280, 110, 165, color="#9333ea", sw=1.5))
    out.append(text(440, 295, "Сигнал VBlank від DRM FD -> композитор готує наступний кадр", size=11, color="#9333ea", italic=True))

    out.append("</svg>")
    return "\n".join(out)

def generate_prime_dmabuf_flow():
    w, h = 860, 320
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">',
           f'<rect width="{w}" height="{h}" fill="{BG}"/>']

    out.append('''<defs>
      <marker id="arrow" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#333333"/>
      </marker>
    </defs>''')

    out.append(text(w/2, 28, "Передача буферів PRIME dma-buf між GPU (Offloading)", size=18, bold=True))

    out.append(rect(30, 60, 240, 230, fill="#fef2f2", stroke="#ef4444", sw=1.5, rx=8))
    out.append(text(150, 84, "Дискретний GPU (dGPU)", size=14, color="#b91c1c", bold=True))
    b_dgpu_render, _, _ = textbox(150, 135, "Рендеринг кадру\n(Vulkan / OpenGL)", size=12, fill="#ffffff", stroke="#ef4444")
    b_prime_export, _, _ = textbox(150, 215, "PRIME Export\n`HANDLE_TO_FD`\n(Створення dma-buf fd)", size=11, fill="#fee2e2", stroke="#dc2626")
    out.extend([b_dgpu_render, b_prime_export])
    out.append(arrow(150, 168, 150, 187, color="#dc2626"))

    b_fd, _, _ = textbox(430, 215, "dma-buf File Descriptor (fd)\nZero-Copy handle в ядрі", size=12, fill="#fef3c7", stroke="#d97706", min_w=200)
    out.append(b_fd)
    out.append(arrow(245, 215, 330, 215, color="#dc2626"))

    out.append(rect(590, 60, 240, 230, fill="#f0fdf4", stroke="#22c55e", sw=1.5, rx=8))
    out.append(text(710, 84, "Інтегрований GPU (iGPU)", size=14, color="#15803d", bold=True))
    b_prime_import, _, _ = textbox(710, 215, "PRIME Import\n`FD_TO_HANDLE`\n(GEM handle в iGPU)", size=11, fill="#dcfce7", stroke="#16a34a")
    b_igpu_scanout, _, _ = textbox(710, 135, "Scanout на дисплей\nKMS Plane -> CRTC\nHDMI / DisplayPort", size=12, fill="#ffffff", stroke="#22c55e")
    out.extend([b_prime_import, b_igpu_scanout])
    out.append(arrow(530, 215, 630, 215, color="#16a34a"))
    out.append(arrow(710, 187, 710, 168, color="#16a34a"))

    out.append("</svg>")
    return "\n".join(out)

def render():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    
    with open(os.path.join(img_dir, "kms-pipeline.svg"), "w", encoding="utf-8") as f:
        f.write(generate_kms_pipeline())
        
    with open(os.path.join(img_dir, "atomic-commit-flow.svg"), "w", encoding="utf-8") as f:
        f.write(generate_atomic_commit_flow())

    with open(os.path.join(img_dir, "prime-dmabuf-offload.svg"), "w", encoding="utf-8") as f:
        f.write(generate_prime_dmabuf_flow())

    print("SVG figures generated successfully.")

if __name__ == "__main__":
    render()

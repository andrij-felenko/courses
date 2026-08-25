import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import fitbox, rect, text, line, arrow, render, FILL, FIELD, NEG, POS, MUTED

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

def fig_architecture():
    """Загальна архітектура підсистеми DRM Accel та її зв'язок із простором користувача."""
    W, H = 900, 480
    f = []

    # Title label at top
    f.append(text(W / 2, 25, "Архітектура підсистеми DRM Accel (Linux 6.3+)", size=16, bold=True))

    # --- User Space Section ---
    y_us = 50
    f.append(rect(40, y_us, 820, 105, fill="#f4f8fb", stroke="#2b7de9", rx=6, sw=1.5))
    f.append(text(60, y_us + 22, "Простір користувача (User Space)", size=14, bold=True, color="#1565c0", anchor="start"))

    f.append(fitbox(80, y_us + 40, 230, 48, "High-Level Frameworks\n(PyTorch, TensorFlow, OpenVINO)", size=12, fill="#ffffff", stroke="#2b7de9"))
    f.append(fitbox(345, y_us + 40, 230, 48, "User Mode Driver (UMD)\n(Vendor Machine Code Gen)", size=12, fill="#ffffff", stroke="#2b7de9"))
    f.append(fitbox(610, y_us + 40, 220, 48, "libdrm (Accel Surface)\n/dev/accel/accelX IOCTLs", size=12, fill="#ffffff", stroke="#2b7de9"))

    # Interface arrow User Space -> Kernel Space
    y_arrow1 = y_us + 105
    y_ks = 205
    f.append(arrow(460, y_arrow1 + 5, 460, y_ks - 5, color="#c0392b", sw=2))
    f.append(fitbox(340, y_arrow1 + 12, 240, 28, "UAPI: /dev/accel/accelX (Major 261)", size=12, bold=True, fill="#fdecea", stroke="#c0392b"))

    # --- Kernel Space Section ---
    f.append(rect(40, y_ks, 820, 150, fill="#f3f9f4", stroke="#2e7d32", rx=6, sw=1.5))
    f.append(text(60, y_ks + 22, "Ядро Linux (Kernel Space: drivers/accel/)", size=14, bold=True, color="#2e7d32", anchor="start"))

    f.append(fitbox(60, y_ks + 40, 230, 48, "DRM Core (Accel Subsystem)\nDRIVER_COMPUTE_ACCEL", size=12, fill="#ffffff", stroke="#2e7d32"))
    f.append(fitbox(310, y_ks + 40, 260, 48, "Менеджер пам'яті (GEM) та DMA-BUF\nMemory Pinning & Allocation", size=12, fill="#ffffff", stroke="#2e7d32"))
    f.append(fitbox(590, y_ks + 40, 240, 48, "Планувальник drm_sched\n& dma_fence Sync", size=12, fill="#ffffff", stroke="#2e7d32"))

    # KMD drivers
    f.append(fitbox(60, y_ks + 98, 770, 38, "Kernel Mode Drivers (KMD): Intel ivpu (VPU/NPU) | Habana habanalabs (Gaudi) | Qualcomm qaic | AMD amdxdna", size=12, fill="#e8f5e9", stroke="#2e7d32"))

    # Arrow Kernel -> Hardware
    y_arrow2 = y_ks + 150
    y_hw = 395
    f.append(arrow(460, y_arrow2 + 5, 460, y_hw - 5, color="#e65100", sw=2))
    f.append(text(475, y_arrow2 + 22, "PCIe / Platform MMIO & DMA Commands", size=11, color="#e65100", anchor="start"))

    # --- Hardware Section ---
    f.append(rect(40, y_hw, 820, 60, fill="#fff8e1", stroke="#fb8c00", rx=6, sw=1.5))
    f.append(text(W / 2, y_hw + 35, "Апаратне забезпечення: NPU / TPU / AI Accelerators (без дисплейних блоків KMS)", size=14, bold=True, color="#e65100"))

    render(os.path.join(IMG, 'drm-accel-architecture.svg'), W, H, *f, title="Архітектура підсистеми DRM Accel")

def fig_pipeline():
    """Конвеєр безкопійного обміну та синхронізації між V4L2, DRM Accel та DRM Render Node."""
    W, H = 880, 360
    f = []

    f.append(text(W / 2, 25, "Конвеєр Zero-Copy обробки даних між підсистемами ядра", size=16, bold=True))

    # Three subsystem boxes
    f.append(fitbox(40, 60, 240, 90, "1. Відеозахоплення\nV4L2 (/dev/video0)\nЗахоплення кадру з камери", size=13, fill="#e3f2fd", stroke="#1565c0"))
    f.append(fitbox(320, 60, 240, 90, "2. AI-Інференс\nDRM Accel (/dev/accel/accel0)\nОбробка NPU / ШІ-модель", size=13, fill="#f3f9f4", stroke="#2e7d32"))
    f.append(fitbox(600, 60, 240, 90, "3. Візуалізація / Рендеринг\nDRM GPU (/dev/dri/renderD128)\nНакладання графіки GPU", size=13, fill="#e65100", stroke="#e65100"))

    # Data flow: DMA-BUF
    f.append(arrow(280, 90, 320, 90, color="#1565c0", sw=2))
    f.append(text(300, 78, "DMA-BUF fd", size=11, bold=True, color="#1565c0"))

    f.append(arrow(560, 90, 600, 90, color="#2e7d32", sw=2))
    f.append(text(580, 78, "DMA-BUF fd", size=11, bold=True, color="#2e7d32"))

    # Lower box: Memory & Fence Backbone
    f.append(rect(40, 180, 800, 140, fill="#f5f5f5", stroke="#616161", rx=6, sw=1.5))
    f.append(text(60, 205, "Спільні примітиви синхронізації та управління пам'яттю", size=14, bold=True, color="#424242", anchor="start"))

    f.append(fitbox(60, 225, 360, 75, "DMA-BUF Allocator & GEM\nЄдиний фізичний буфер у пам'яті (RAM / VRAM)\nБез копіювання через CPU", size=12, fill="#ffffff", stroke="#757575"))
    f.append(fitbox(460, 225, 360, 75, "dma_fence & syncobj Pipeline\nАпаратне очікування між пристроями\nCPU не блокується під час інференсу", size=12, fill="#ffffff", stroke="#757575"))

    # Vertical connections to lower box
    f.append(line(160, 150, 160, 225, color="#1565c0", sw=1.5, dash="4,4"))
    f.append(line(440, 150, 440, 225, color="#2e7d32", sw=1.5, dash="4,4"))
    f.append(line(720, 150, 720, 225, color="#e65100", sw=1.5, dash="4,4"))

    render(os.path.join(IMG, 'drm-accel-pipeline.svg'), W, H, *f, title="Конвеєр Zero-Copy обробки даних")

if __name__ == "__main__":
    fig_architecture()
    fig_pipeline()

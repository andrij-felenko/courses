import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import render, textbox, rect, line, arrow, text

def draw_dma_buf_heaps_arch():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    out_path = os.path.join(img_dir, 'dma-buf-heaps-arch.svg')

    frags = []

    # 1. User Space container
    frags.append(rect(20, 40, 760, 140, fill='#e0f7fa', stroke='#006064', rx=8))
    frags.append(text(400, 65, "User Space (Простір користувача)", size=15, bold=True, color='#006064'))

    tb_app, _, _ = textbox(140, 125, "V4L2 Application\n(Камера / Ввід)", size=12, fill='#ffffff', stroke='#00838f')
    tb_alloc, _, _ = textbox(400, 125, "Allocator Process\nopen(/dev/dma_heap/system)\nioctl(DMA_HEAP_IOC_ALLOC)", size=11, fill='#ffffff', stroke='#00838f')
    tb_drm, _, _ = textbox(660, 125, "DRM / KMS Composer\n(Дисплей / Вивід)", size=12, fill='#ffffff', stroke='#00838f')
    frags.extend([tb_app, tb_alloc, tb_drm])

    # Arrow from Allocator to User Space fds
    frags.append(arrow(280, 125, 230, 125, color='#00838f'))
    frags.append(arrow(520, 125, 570, 125, color='#00838f'))
    frags.append(text(255, 115, "dma-buf fd", size=10, color='#006064'))
    frags.append(text(545, 115, "dma-buf fd", size=10, color='#006064'))

    # 2. Character Device Interface Layer
    frags.append(rect(20, 205, 760, 45, fill='#fff3e0', stroke='#e65100', rx=6))
    frags.append(text(400, 232, "Системний інтерфейс: /dev/dma_heap/* (character devices)", size=13, bold=True, color='#e65100'))
    frags.append(arrow(400, 160, 400, 205, color='#e65100'))

    # 3. Kernel Space container
    frags.append(rect(20, 275, 760, 140, fill='#fff8e1', stroke='#ff8f00', rx=8))
    frags.append(text(400, 300, "Kernel Space (Ядро Linux)", size=15, bold=True, color='#ff8f00'))

    tb_v4l2_drv, _, _ = textbox(140, 355, "V4L2 Driver\nv4l2_buffer\n(V4L2_MEMORY_DMABUF)", size=11, fill='#ffffff', stroke='#e65100')
    tb_heap_fw, _, _ = textbox(400, 355, "dma-buf heaps Framework\nstruct dma_heap_ops\ndma_buf_export()", size=11, fill='#ffffff', stroke='#e65100')
    tb_drm_drv, _, _ = textbox(660, 355, "DRM Driver\nDRM_IOCTL_PRIME_FD_TO_HANDLE\n(GEM handle)", size=11, fill='#ffffff', stroke='#e65100')
    frags.extend([tb_v4l2_drv, tb_heap_fw, tb_drm_drv])

    frags.append(arrow(400, 250, 400, 320, color='#e65100'))
    frags.append(arrow(140, 160, 140, 320, color='#00838f'))
    frags.append(arrow(660, 160, 660, 320, color='#00838f'))

    # Shared dma-buf backing struct link
    frags.append(line(220, 355, 310, 355, color='#27ae60', sw=2, dash='4,4'))
    frags.append(line(490, 355, 570, 355, color='#27ae60', sw=2, dash='4,4'))

    # 4. Physical Memory Layer container
    frags.append(rect(20, 440, 760, 90, fill='#e8f5e9', stroke='#2e7d32', rx=8))
    frags.append(text(400, 462, "Фізична оперативна пам'ять (RAM)", size=14, bold=True, color='#2e7d32'))
    
    tb_sys_mem, _, _ = textbox(240, 498, "Buddy Allocator (System Heap)\nФізично розривні сторінки", size=11, fill='#ffffff', stroke='#27ae60')
    tb_cma_mem, _, _ = textbox(560, 498, "CMA Pool (Contiguous Memory)\nФізично неперервний блок", size=11, fill='#ffffff', stroke='#27ae60')
    frags.extend([tb_sys_mem, tb_cma_mem])

    frags.append(arrow(350, 395, 270, 470, color='#27ae60'))
    frags.append(arrow(450, 395, 530, 470, color='#27ae60'))

    render(out_path, 800, 550, *frags)

def main():
    draw_dma_buf_heaps_arch()

if __name__ == '__main__':
    main()

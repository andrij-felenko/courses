import os
import sys

# Add scripts directory to sys.path for svgkit import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

def render():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    # 1. ublk-arch.svg
    svg_arch = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 520">']
    svg_arch.append('<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#333333"/></marker></defs>')
    svg_arch.append(rect(0, 0, 820, 520, fill="#ffffff", stroke="none"))
    
    # Boundary: Userspace
    svg_arch.append(rect(20, 20, 780, 210, fill="#f4f8ff", stroke="#2457d6", sw=1.5, rx=8))
    svg_arch.append(text(410, 45, "Простір користувача (Userspace)", size=16, color="#2457d6", bold=True))
    
    # App and ublksrv boxes
    b_app, _, _ = textbox(160, 130, "Користувацький застосунок\n(FS / DB / Ввід-вивід)", size=13, pad=12, fill="#ffffff", stroke="#2457d6")
    svg_arch.append(b_app)
    
    b_srv, _, _ = textbox(620, 130, "Демон ublksrv\n(Target Logic / libublksrv)", size=13, pad=12, fill="#e8f0fe", stroke="#1a73e8", bold=True)
    svg_arch.append(b_srv)
    
    # SQ/CQ ring box inside userspace
    b_ring, _, _ = textbox(400, 130, "io_uring Кільця\n(SQ / CQ Buffers)", size=12, pad=10, fill="#e6f4ea", stroke="#27ae60")
    svg_arch.append(b_ring)

    # Boundary: Kernel Space
    svg_arch.append(rect(20, 270, 780, 220, fill="#f9fbe7", stroke="#27ae60", sw=1.5, rx=8))
    svg_arch.append(text(410, 295, "Простір ядра (Kernel Space)", size=16, color="#27ae60", bold=True))

    # Kernel components
    b_blk, _, _ = textbox(160, 390, "Блоковий шар Linux\n/dev/ublkbN", size=13, pad=12, fill="#ffffff", stroke="#27ae60")
    svg_arch.append(b_blk)

    b_drv, _, _ = textbox(620, 390, "Модуль ublk_drv\n/dev/ublkcN", size=13, pad=12, fill="#e6f4ea", stroke="#1e7e34", bold=True)
    svg_arch.append(b_drv)

    # Connections
    svg_arch.append(arrow(160, 185, 160, 335, color="#1a1a1a", sw=1.8))
    svg_arch.append(text(175, 260, "I/O запит", size=11, color="#6b7280", anchor="start"))

    svg_arch.append(arrow(260, 390, 520, 390, color="#1a1a1a", sw=1.8))
    svg_arch.append(text(390, 380, "struct request", size=11, color="#6b7280"))

    # io_uring passthrough connection
    svg_arch.append(arrow(620, 335, 620, 185, color="#c0392b", sw=2.0))
    svg_arch.append(arrow(600, 185, 600, 335, color="#2457d6", sw=2.0))
    
    svg_arch.append(text(630, 250, "CQE: метадані запиту", size=11, color="#c0392b", anchor="start"))
    svg_arch.append(text(590, 270, "SQE: FETCH_REQ / COMMIT", size=11, color="#2457d6", anchor="end"))

    svg_arch.append("</svg>")

    with open(os.path.join(img_dir, "ublk-arch.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(svg_arch))

    # 2. zero-copy.svg
    svg_zc = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 480">']
    svg_zc.append('<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#333333"/></marker></defs>')
    svg_zc.append(rect(0, 0, 820, 480, fill="#ffffff", stroke="none"))

    svg_zc.append(text(410, 35, "Передача даних Zero-Copy у фреймворку ublk", size=16, color="#1a1a1a", bold=True))

    # Stages: App Buffer -> Page Pinning -> Userspace Target -> NVMe Storage
    b_app_buf, _, _ = textbox(130, 140, "Буфер застосунку\n(User Virtual Memory)", size=13, pad=12, fill="#f4f8ff", stroke="#2457d6")
    svg_zc.append(b_app_buf)

    b_pages, _, _ = textbox(390, 140, "Фізичні сторінки ядра\n(struct page / bio_vec)", size=13, pad=12, fill="#f9fbe7", stroke="#27ae60")
    svg_zc.append(b_pages)

    b_target_buf, _, _ = textbox(670, 140, "Буфери демона ublksrv\n(io_uring registered bvec)", size=13, pad=12, fill="#e8f0fe", stroke="#1a73e8")
    svg_zc.append(b_target_buf)

    b_storage, _, _ = textbox(390, 360, "Апаратний накопичувач\n(NVMe SSD / Мережеве сховище)", size=14, pad=14, fill="#f4f6f8", stroke="#333333", bold=True)
    svg_zc.append(b_storage)

    # Direct data paths
    svg_zc.append(arrow(220, 140, 300, 140, color="#1a1a1a", sw=1.8))
    svg_zc.append(text(260, 125, "GUP / Pinning", size=11, color="#6b7280"))

    svg_zc.append(arrow(480, 140, 560, 140, color="#27ae60", sw=2.0))
    svg_zc.append(text(520, 125, "Zero-Copy", size=11, color="#27ae60", bold=True))

    # DMA arrow from pages straight to hardware
    svg_zc.append(arrow(390, 195, 390, 305, color="#c0392b", sw=2.2))
    svg_zc.append(text(400, 250, "Трансфер бекенду (без копії CPU)", size=12, color="#c0392b", bold=True, anchor="start"))

    # Target control line
    svg_zc.append(line(670, 195, 670, 360, color="#1a73e8", sw=1.5, dash="4,4"))
    svg_zc.append(arrow(670, 360, 510, 360, color="#1a73e8", sw=1.5))
    svg_zc.append(text(620, 345, "Асинхронний контроль io_uring", size=11, color="#1a73e8"))

    svg_zc.append("</svg>")

    with open(os.path.join(img_dir, "zero-copy.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(svg_zc))

if __name__ == "__main__":
    render()

import os
import sys

# Add scripts directory to path (4 levels up from topic dir)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def render_all():
    topic_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(topic_dir, "img")
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. ZFS Encryption Tree SVG
    frags1 = []
    frags1.append(text(400, 25, "Ієрархія коренів шифрування та успадкування ключів у ZFS", size=15, bold=True, color="#1a1a1a"))
    
    t1, w1, h1 = textbox(400, 75, "pool (корінь пулу, unencrypted)\nБез власних ключів", size=13, fill="#e2e8f0", stroke="#475569", bold=True)
    frags1.append(t1)
    
    t2, w2, h2 = textbox(230, 180, "pool/data (Encryption Root)\nМайстер-ключ A (AES-256-GCM)\nКлюч завантажено в пам'ять", size=12, fill="#fde8e8", stroke="#c0392b", color="#900c3f", bold=True)
    frags1.append(t2)
    
    t3, w3, h3 = textbox(570, 180, "pool/public (unencrypted)\nУспадковує відсутність шифрування", size=12, fill="#f4f6f8", stroke="#7f8c8d", color="#2c3e50")
    frags1.append(t3)
    
    t4, w4, h4 = textbox(130, 295, "pool/data/home\nУспадковує Майстер-ключ A\n(спільне криптодерево)", size=11, fill="#fef2f2", stroke="#e74c3c", color="#991b1b")
    frags1.append(t4)
    
    t5, w5, h5 = textbox(360, 295, "pool/data/secret (Encryption Root)\nОкремий Майстер-ключ B\n(новий корінь шифрування)", size=11, fill="#fde8e8", stroke="#c0392b", color="#900c3f", bold=True)
    frags1.append(t5)
    
    frags1.append(line(330, 98, 260, 142, color="#475569", sw=1.5))
    frags1.append(line(470, 98, 540, 142, color="#7f8c8d", sw=1.5, dash="3,3"))
    
    frags1.append(line(180, 218, 140, 258, color="#c0392b", sw=1.5))
    frags1.append(line(280, 218, 330, 258, color="#c0392b", sw=1.5, dash="3,3"))
    
    render(os.path.join(out_dir, "zfs-encryption-tree.svg"), 800, 360, *frags1)
    
    # 2. DDT Structure SVG
    frags2 = []
    frags2.append(text(400, 25, "Структура таблиці дедуплікації (DDT) та адресація у ZFS", size=15, bold=True, color="#1a1a1a"))
    
    frags2.append(rect(30, 45, 740, 180, fill="#f8fafc", stroke="#3b82f6", sw=1.5, rx=8))
    frags2.append(text(50, 60, "Оперативна пам'ять (RAM / ARC)", size=12, bold=True, color="#1d4ed8", anchor="start"))
    
    ddt_str = "Deduplication Table (DDT in ARC)\nХеш блоку (SHA256/SHA512/SKEIN)  |  RefCount  |  DVA (Physical Address)\n0x8F3A...E910 (256 bit)                 |     Count=2    |  DVA: pool/dev0:offset 0x4000\n0x11B2...90AC (256 bit)                 |     Count=1    |  DVA: pool/dev0:offset 0x8000"
    t_ddt, _, _ = textbox(400, 138, ddt_str, size=11, fill="#f3e8ff", stroke="#7e22ce", color="#581c87")
    frags2.append(t_ddt)
    
    frags2.append(rect(30, 240, 740, 160, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=8))
    frags2.append(text(50, 254, "Дискове сховище (Zpool Storage)", size=12, bold=True, color="#15803d", anchor="start"))
    
    t_fa, _, _ = textbox(150, 315, "Файл A (Block Pointer 1)\nВказує на 0x8F3A...", size=11, fill="#e0f2fe", stroke="#0284c7", color="#0369a1")
    frags2.append(t_fa)
    
    t_fb, _, _ = textbox(650, 315, "Файл B (Block Pointer 3)\nВказує на 0x8F3A...", size=11, fill="#e0f2fe", stroke="#0284c7", color="#0369a1")
    frags2.append(t_fb)
    
    t_dva, _, _ = textbox(400, 365, "Фізичний блок на диску (DVA1)\nЗбережений єдиний примірник даних", size=11, fill="#dcfce7", stroke="#16a34a", color="#14532d", bold=True)
    frags2.append(t_dva)
    
    frags2.append(line(150, 290, 270, 192, color="#0284c7", sw=1.5, dash="4,4"))
    frags2.append(line(650, 290, 530, 192, color="#0284c7", sw=1.5, dash="4,4"))
    frags2.append(arrow(400, 192, 400, 342, color="#7e22ce", sw=2))
    
    render(os.path.join(out_dir, "zfs-ddt-structure.svg"), 800, 420, *frags2)

if __name__ == "__main__":
    render_all()

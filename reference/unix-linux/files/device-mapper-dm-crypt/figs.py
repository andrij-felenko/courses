import sys
import os

# Add path to scripts/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../scripts')))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

def render_figs():
    # 1. Device Mapper Architecture
    # Canvas 820 x 420
    frags1 = [
        # User space group
        rect(30, 20, 760, 110, fill="#f8f9fa", stroke="#6c757d", sw=1.5, rx=8),
        text(120, 45, "Простір користувача (User Space)", size=15, bold=True, color="#495057"),
        
        fitbox(50, 65, 160, 48, "LVM2 (lvm)\nPV / VG / LV", size=13, fill="#e7f5ff", stroke="#1c7ed6"),
        fitbox(230, 65, 170, 48, "cryptsetup\nУправління LUKS", size=13, fill="#e7f5ff", stroke="#1c7ed6"),
        fitbox(420, 65, 150, 48, "dmsetup\nПряме керування", size=13, fill="#e7f5ff", stroke="#1c7ed6"),
        fitbox(590, 65, 180, 48, "Системний утиліт\nmount / fsck", size=13, fill="#e7f5ff", stroke="#1c7ed6"),

        # Control interface ioctl node
        fitbox(280, 160, 260, 44, "/dev/mapper/control\n(ioctl виклики)", size=13, fill="#fff9db", stroke="#f59f00", bold=True),

        # Kernel space group
        rect(30, 230, 760, 160, fill="#f1f3f5", stroke="#495057", sw=1.5, rx=8),
        text(140, 255, "Ядро Linux: Device Mapper (dm-mod)", size=15, bold=True, color="#212529"),

        fitbox(50, 275, 160, 50, "Target: linear\nСклеювання блоків", size=13, fill="#d3f9d8", stroke="#2b8a3e"),
        fitbox(230, 275, 170, 50, "Target: crypt\nAES-XTS шифрування", size=13, fill="#ffe3e3", stroke="#e03131", bold=True),
        fitbox(420, 275, 160, 50, "Target: snapshot\nCopy-on-Write", size=13, fill="#d3f9d8", stroke="#2b8a3e"),
        fitbox(600, 275, 170, 50, "Target: striped\nRAID0 смугування", size=13, fill="#d3f9d8", stroke="#2b8a3e"),

        # Virtual Device Layer
        fitbox(210, 340, 400, 36, "Віртуальні пристрої (/dev/mapper/* або /dev/dm-N)", size=13, fill="#eebefa", stroke="#9c36b5"),

        # Connecting arrows
        arrow(130, 113, 350, 160, color="#1c7ed6"),
        arrow(315, 113, 390, 160, color="#1c7ed6"),
        arrow(495, 113, 430, 160, color="#1c7ed6"),
        arrow(410, 204, 410, 230, color="#f59f00")
    ]
    render(os.path.join(IMG, 'dm-architecture.svg'), 820, 420, *frags1)

    # 2. LUKS Header Structure
    # Canvas 820 x 420
    frags2 = [
        rect(30, 30, 760, 360, fill="#f8f9fa", stroke="#495057", sw=1.5, rx=8),
        text(410, 55, "Структура дискового блокового пристрою з LUKS2", size=15, bold=True, anchor="middle"),

        # LUKS Header container
        rect(50, 80, 340, 290, fill="#fff5f5", stroke="#e03131", sw=1.5, rx=6),
        text(220, 105, "Заголовок LUKS (LUKS Header)", size=14, bold=True, color="#c92a2a"),

        fitbox(70, 120, 300, 36, "Magic: LUKS\\xba\\xbe (Версія 1 або 2)", size=12, fill="#ffe3e3", stroke="#e03131"),
        fitbox(70, 165, 300, 36, "Метадані JSON: UUID, Алгоритм (AES-XTS)", size=12, fill="#ffe3e3", stroke="#e03131"),
        fitbox(70, 210, 300, 40, "Параметри KDF: Argon2id / PBKDF2\n(Сіль, ітерації, пам'ять)", size=12, fill="#ffe3e3", stroke="#e03131"),
        fitbox(70, 260, 300, 95, "Key Slots 0 .. 7\n- Зашифрований Master Key (VK)\n- AF-Split розмічування матеріалу\n- Парольна фраза розшифровує KEK", size=12, fill="#fff0f6", stroke="#d6336c"),

        # Master key relation box
        fitbox(410, 180, 110, 80, "Master Key\n(Volume Key)\n🔑", size=13, fill="#fff9db", stroke="#f59f00", bold=True),

        # Payload container
        rect(540, 80, 230, 290, fill="#e6fcf5", stroke="#0ca678", sw=1.5, rx=6),
        text(655, 110, "Зашифрований Payload", size=14, bold=True, color="#099268"),
        mtext(655, 150, "Сектори 0 .. N\n(Шифрування AES-XTS)\n\nМістить файлову\nсистему або LVM PV", size=13, anchor="middle", color="#2b8a3e"),

        # Key transformation arrows
        arrow(370, 300, 410, 240, color="#d6336c"),
        text(390, 285, "KEK", size=11, color="#d6336c", bold=True),
        arrow(520, 220, 540, 220, color="#f59f00"),
        text(530, 205, "Розшифровує", size=11, color="#f59f00", bold=True)
    ]
    render(os.path.join(IMG, 'luks-structure.svg'), 820, 420, *frags2)

    # 3. DM-Crypt I/O Request Flow
    # Canvas 820 x 360
    frags3 = [
        rect(30, 20, 760, 320, fill="#f8f9fa", stroke="#495057", sw=1.5, rx=8),
        text(410, 45, "Конвеєр обробки I/O запиту в dm-crypt", size=15, bold=True, anchor="middle"),

        fitbox(50, 75, 200, 60, "Запит bio від ФС\n(наприклад /dev/mapper/sec)\nСектор S, розмір LEN", size=12, fill="#e7f5ff", stroke="#1c7ed6"),

        arrow(250, 105, 300, 105, color="#1c7ed6"),

        fitbox(300, 75, 220, 60, "Target dm-crypt\n1. Перераховує сектор IV\n2. Клонує структуру bio", size=12, fill="#fff9db", stroke="#f59f00", bold=True),

        arrow(410, 135, 410, 180, color="#f59f00"),

        fitbox(300, 180, 220, 60, "Kernel Crypto API / AES-NI\nШифрування/розшифрування\nблока (AES-256-XTS)", size=12, fill="#ffe3e3", stroke="#e03131", bold=True),

        arrow(410, 240, 410, 280, color="#e03131"),

        fitbox(300, 280, 220, 45, "Черга робочих потоків\nkcryptd", size=12, fill="#f3d9fa", stroke="#ae3ec9"),

        arrow(520, 302, 570, 302, color="#ae3ec9"),

        fitbox(570, 275, 200, 55, "Фізичний драйвер\nNVMe / SATA / SCSI\n/dev/nvme0n1p2", size=12, fill="#e6fcf5", stroke="#0ca678")
    ]
    render(os.path.join(IMG, 'dm-mapping-flow.svg'), 820, 360, *frags3)

if __name__ == '__main__':
    render_figs()

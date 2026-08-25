import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

def render_arch():
    path = os.path.join(IMG, "crypto-arch.svg")
    
    frags = [
        # Outer Frame
        rect(10, 10, 840, 560, fill="#f8f9fa", stroke="#cfd8dc", sw=2, rx=8),
        
        # User Space Layer
        rect(30, 30, 800, 110, fill="#e1f5fe", stroke="#0277bd", sw=2, rx=6),
        text(50, 55, "User Space (Простір користувача)", size=16, bold=True, color="#01579b", anchor="start"),
        
        fitbox(50, 68, 230, 55, "Програми та утиліти\n(OpenSSL, GnuTLS, libgcrypt)", size=12, fill="#ffffff", stroke="#0288d1"),
        fitbox(300, 68, 240, 55, "Сокети AF_ALG\n(bind, setsockopt, accept)", size=12, fill="#ffffff", stroke="#0288d1"),
        fitbox(560, 68, 250, 55, "Межа привілеїв & LSM\n(Seccomp, Capabilities, SELinux)", size=12, fill="#e3f2fd", stroke="#1565c0"),
        
        # System Call / Socket Interface Arrow
        arrow(420, 140, 420, 175, color="#0277bd", sw=2),
        text(430, 160, "socket(AF_ALG) / splice()", size=11, color="#0277bd", bold=True, anchor="start"),

        # Kernel Space Container
        rect(30, 180, 800, 250, fill="#e8f5e9", stroke="#2e7d32", sw=2, rx=6),
        text(50, 205, "Kernel Space (Ядро Linux — Kernel Crypto API)", size=16, bold=True, color="#1b5e20", anchor="start"),
        
        # Consumers Box
        rect(50, 220, 220, 190, fill="#ffffff", stroke="#388e3c", rx=4),
        text(160, 243, "Споживачі в ядрі", size=14, bold=True, color="#2e7d32"),
        fitbox(60, 255, 200, 30, "dm-crypt / LUKS (шифрування дисків)", size=11, fill="#f1f8e9", stroke="#7cb342"),
        fitbox(60, 293, 200, 30, "IPsec (xfrm) & mac80211 / Wi-Fi", size=11, fill="#f1f8e9", stroke="#7cb342"),
        fitbox(60, 331, 200, 30, "IMA / EVM (цілісність файлів)", size=11, fill="#f1f8e9", stroke="#7cb342"),
        fitbox(60, 369, 200, 30, "Kernel Keyring (підписи & асиметрія)", size=11, fill="#f1f8e9", stroke="#7cb342"),
        
        # Crypto Core Box
        rect(290, 220, 260, 190, fill="#ffffff", stroke="#388e3c", rx=4),
        text(420, 243, "Crypto Core (Ядро Crypto API)", size=14, bold=True, color="#2e7d32"),
        fitbox(305, 255, 230, 42, "Реєстр алгоритмів (struct crypto_alg)\nДиспетчер пріоритетів (cra_priority)", size=11, fill="#dedede", stroke="#9e9e9e"),
        fitbox(305, 305, 230, 42, "Об'єкти трансформацій (TFM)\n(skcipher, ahash, aead, cipher)", size=11, fill="#dedede", stroke="#9e9e9e"),
        fitbox(305, 355, 230, 42, "Інтерфейс діагностики\n/proc/crypto", size=11, fill="#e8eaf6", stroke="#3f51b5"),

        # Driver Implementations Box
        rect(570, 220, 240, 190, fill="#ffffff", stroke="#388e3c", rx=4),
        text(690, 243, "Реалізації алгоритмів", size=14, bold=True, color="#2e7d32"),
        fitbox(580, 255, 220, 42, "Програмні C-версії\n(aes-generic, sha256-generic)", size=11, fill="#fff9c4", stroke="#fbc02d"),
        fitbox(580, 305, 220, 42, "Процесорні інструкції\n(aes-ni, arm64-ce-aes, avx2)", size=11, fill="#fff9c4", stroke="#fbc02d"),
        fitbox(580, 355, 220, 42, "Драйвери прискорювачів\n(intel-qat, amd-ccp)", size=11, fill="#ffe0b2", stroke="#f57c00"),

        # Arrows inside Kernel
        arrow(270, 315, 290, 315, color="#2e7d32", sw=2),
        arrow(550, 315, 570, 315, color="#2e7d32", sw=2),
        
        # Hardware Layer
        rect(30, 450, 800, 100, fill="#fff3e0", stroke="#e65100", sw=2, rx=6),
        text(50, 475, "Hardware Layer (Апаратне забезпечення)", size=16, bold=True, color="#e65100", anchor="start"),
        
        fitbox(60, 488, 230, 48, "ЦП з інструкціями\nAES-NI / ARM CE / SHA-NI", size=12, fill="#ffffff", stroke="#f57c00"),
        fitbox(310, 488, 230, 48, "PCIe Апаратні Прискорювачі\n(Intel QAT, AMD CCP)", size=12, fill="#ffffff", stroke="#f57c00"),
        fitbox(560, 488, 250, 48, "Криптомодулі HSM & TPM\n(асиметричні ключі & виміри)", size=12, fill="#ffffff", stroke="#f57c00"),

        # Arrow Kernel to Hardware
        arrow(690, 410, 690, 450, color="#e65100", sw=2)
    ]
    
    render(path, 860, 580, *frags, title="Архітектура Linux Kernel Crypto API")
    print("Generated crypto-arch.svg")


def render_async_req():
    path = os.path.join(IMG, "async-req-lifecycle.svg")
    
    frags = [
        # Frame
        rect(10, 10, 840, 520, fill="#ffffff", stroke="#cfd8dc", sw=2, rx=8),
        text(430, 35, "Життєвий цикл асинхронного криптографічного запиту в ядрі", size=16, bold=True, color="#263238"),
        
        # Actor Columns / Swimlanes
        rect(30, 55, 240, 365, fill="#f3f4f6", stroke="#90a4ae", rx=6),
        text(150, 78, "Клієнт ядра (dm-crypt/IPsec)", size=13, bold=True, color="#37474f"),

        rect(300, 55, 260, 365, fill="#e8f5e9", stroke="#81c784", rx=6),
        text(430, 78, "Crypto Core & Driver Queue", size=13, bold=True, color="#2e7d32"),

        rect(590, 55, 230, 365, fill="#fff3e0", stroke="#ffb74d", rx=6),
        text(705, 78, "Апаратний прискорювач (QAT)", size=13, bold=True, color="#e65100"),

        # Step 1: Alloc & Fill req
        fitbox(45, 95, 210, 45, "1. Виділення skcipher_req\nЗаповнення SG-list та callback", size=11, fill="#ffffff", stroke="#78909c"),

        # Arrow 1 -> 2
        arrow(255, 118, 300, 118, color="#1976d2", sw=2),
        text(278, 110, "encrypt()", size=10, color="#1976d2", bold=True),

        # Step 2: Queue req
        fitbox(300, 95, 260, 45, "2. Постановка в чергу драйвера\ncrypto_enqueue_request()", size=11, fill="#ffffff", stroke="#4caf50"),

        # Arrow 2 -> 1 (EINPROGRESS)
        arrow(300, 155, 255, 155, color="#d32f2f", sw=2),
        text(278, 147, "-EINPROGRESS", size=10, color="#d32f2f", bold=True),

        # Step 3: Non-blocking continuation
        fitbox(45, 145, 210, 45, "3. Клієнт НЕ блокується\nВиконує інші I/O операції", size=11, fill="#e3f2fd", stroke="#1e88e5"),

        # Step 4: Hardware DMA trigger
        fitbox(300, 200, 260, 45, "4. Передача фізичних сторінок\nчерез DMA у PCIe пристрої", size=11, fill="#ffffff", stroke="#4caf50"),

        # Arrow 4 -> Hardware
        arrow(560, 222, 590, 222, color="#e65100", sw=2),
        text(575, 212, "DMA", size=10, color="#e65100", bold=True),

        # Step 5: Silicon calculation
        fitbox(590, 200, 230, 50, "5. Апаратне шифрування\nбез участі ЦП", size=11, fill="#ffffff", stroke="#fb8c00"),

        # Step 6: Hardware Interrupt
        arrow(590, 280, 560, 280, color="#e65100", sw=2),
        text(575, 270, "IRQ", size=10, color="#e65100", bold=True),

        # Step 7: Interrupt Handler & Tasklet
        fitbox(300, 265, 260, 50, "6. Обробник переривання ЦП\nВитягує результат з DMA ring", size=11, fill="#ffffff", stroke="#4caf50"),

        # Arrow 7 -> Callback
        arrow(300, 345, 255, 345, color="#388e3c", sw=2),
        text(278, 337, "Callback", size=10, color="#388e3c", bold=True),

        # Step 8: Completion Callback executed
        fitbox(45, 325, 210, 50, "7. Виклик req->complete()\nОбробка шифрованих даних", size=11, fill="#e8f5e9", stroke="#388e3c"),

        # Summary footer box
        fitbox(30, 435, 790, 65, "Перевага: ЦП звільняється від математичних обчислень під час обробки тисяч I/O запитів;\nПам'ять передається безкопіювально через Scatterlists без проміжних буферів.", size=11, fill="#f5f5f5", stroke="#b0bec5", color="#455a64")
    ]
    
    render(path, 860, 540, *frags, title="Життєвий цикл асинхронного криптографічного запиту")
    print("Generated async-req-lifecycle.svg")


if __name__ == '__main__':
    render_arch()
    render_async_req()

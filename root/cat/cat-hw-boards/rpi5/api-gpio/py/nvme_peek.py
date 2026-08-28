# nvme_peek.py — читаємо перші 16 байтів NVMe-диска як звичайного файлу
# запуск:  sudo python3 nvme_peek.py   (сирий диск читає лише root)

DISK = "/dev/nvme0n1"   # весь диск; розділ був би nvme0n1p1

# "rb" — тільки читаємо, у двійковому режимі; писати в сирий диск наосліп
# НЕБЕЗПЕЧНО. with сам закриє файл на виході.
with open(DISK, "rb") as f:
    buf = f.read(16)    # читаємо з початку диска

print(f"перші {len(buf)} байтів {DISK}:")
print(" ".join(f"{b:02X}" for b in buf))

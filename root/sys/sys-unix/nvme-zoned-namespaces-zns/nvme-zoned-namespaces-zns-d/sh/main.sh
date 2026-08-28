# 1. Перегляд геологічних атрибутів ZNS простору імен
nvme zns id-ns /dev/nvme0n1

# 2. Отримання звіту про стан зон (Zone Report)
nvme zns report-zones /dev/nvme0n1

# 3. Виконання дій над зонами (Zone Management Send)
# Відкрити зону (ZSA = 3)
nvme zns zone-mgmt-send /dev/nvme0n1 --slba=0x0 --zsa=3

# Закрити зону (ZSA = 1)
nvme zns zone-mgmt-send /dev/nvme0n1 --slba=0x0 --zsa=1

# Завершити зону (ZSA = 2)
nvme zns zone-mgmt-send /dev/nvme0n1 --slba=0x0 --zsa=2

# Скинути зону (ZSA = 4)
nvme zns zone-mgmt-send /dev/nvme0n1 --slba=0x0 --zsa=4

# Скинути ВСІ зони накопичувача однією командою
nvme zns zone-mgmt-send /dev/nvme0n1 --zsa=4 --select-all

# 1. Завантаження потрібних модулів ядра
sudo modprobe nvmet
sudo modprobe nvmet-tcp

# 2. Створення підсистеми NVMe Target
sudo mkdir /sys/kernel/config/nvmet/subsystems/nqn.2026-08.com.example:nvme-storage01
cd /sys/kernel/config/nvmet/subsystems/nqn.2026-08.com.example:nvme-storage01

# 3. Дозвіл підключення будь-яким хостам (без обмеження ACL)
echo 1 | sudo tee attr_allow_any_host

# 4. Створення Namespace 1 та прив'язка блочного пристрою
sudo mkdir namespaces/1
echo -n "/dev/sdb" | sudo tee namespaces/1/device_path
echo 1 | sudo tee namespaces/1/enable

# 5. Створення мережевого порту NVMe/TCP (порт 4420)
sudo mkdir /sys/kernel/config/nvmet/ports/1
cd /sys/kernel/config/nvmet/ports/1
echo "tcp" | sudo tee addr_trtype
echo "ipv4" | sudo tee addr_adrfam
echo "192.168.122.10" | sudo tee addr_traddr
echo "4420" | sudo tee addr_trsvcid

# 6. Зв'язування підсистеми з портом
sudo ln -s /sys/kernel/config/nvmet/subsystems/nqn.2026-08.com.example:nvme-storage01 \
  /sys/kernel/config/nvmet/ports/1/subsystems/

# 1. Створення підсистеми
mkdir /sys/kernel/config/nvmet/subsystems/nqn.2026-08.com.example:nvme-pool1
cd /sys/kernel/config/nvmet/subsystems/nqn.2026-08.com.example:nvme-pool1

# Дозвіл підключення будь-якому хосту
echo 1 > attr_allow_any_host

# 2. Створення простору імен Namespace 1 на базі LVM-тому
mkdir namespaces/1
cd namespaces/1
echo -n "/dev/vg_nvme/lv_storage" > device_path
echo 1 > enable

# 3. Створення мережевого порту TCP на порту 4420
mkdir /sys/kernel/config/nvmet/ports/1
cd /sys/kernel/config/nvmet/ports/1
echo "tcp" > addr_trtype
echo "192.168.1.100" > addr_traddr
echo "4420" > addr_trsvcid
echo "ipv4" > addr_adrfam

# 4. Прив'язка підсистеми до порту через symlink
ln -s /sys/kernel/config/nvmet/subsystems/nqn.2026-08.com.example:nvme-pool1 \
      /sys/kernel/config/nvmet/ports/1/subsystems/nqn.2026-08.com.example:nvme-pool1

# Налаштування NVMe Target (nvmet) у Linux

У Linux ядро містить підсистему `nvmet`, яка дозволяє серверу експортувати пристрої через NVMe-oF. Конфігурація здійснюється через інтерфейс `configfs`.

```bash
# Монтуємо configfs, якщо вона ще не змонтована
mount -t configfs none /sys/kernel/config
modprobe nvmet
modprobe nvmet-tcp

# 1. Створюємо підсистему (Target)
mkdir /sys/kernel/config/nvmet/subsystems/nqn.2024-01.com.example:test-target
cd /sys/kernel/config/nvmet/subsystems/nqn.2024-01.com.example:test-target

# Дозволяємо підключення будь-якому ініціатору
echo 1 > attr_allow_any_host

# 2. Створюємо простір імен (Namespace) і прив'язуємо блоковий пристрій
mkdir namespaces/1
echo -n /dev/nvme0n1 > namespaces/1/device_path
echo 1 > namespaces/1/enable

# 3. Створюємо порт і прив'язуємо до нього підсистему
mkdir /sys/kernel/config/nvmet/ports/1
cd /sys/kernel/config/nvmet/ports/1
echo "ipv4" > addr_adrfam
echo "tcp" > addr_trtype
echo "4420" > addr_trsvcid
echo "192.168.1.100" > addr_traddr

# Робимо підсистему доступною на цьому порту
ln -s /sys/kernel/config/nvmet/subsystems/nqn.2024-01.com.example:test-target \
      /sys/kernel/config/nvmet/ports/1/subsystems/
```

Після цього ініціатори зможуть виявити цю підсистему за IP 192.168.1.100 на порту 4420.

# Монтування configfs, якщо ще не змонтовано
sudo mount -t configfs none /sys/kernel/config 2>/dev/null || true

# Створення нового екземпляра nullb1
sudo mkdir /sys/kernel/config/nullb/nullb1
cd /sys/kernel/config/nullb/nullb1

# Налаштування параметрів черг
echo 8 | sudo tee submit_queues      # 8 апаратних черг
echo 128 | sudo tee hw_queue_depth   # Глибина 128
echo 1 | sudo tee power              # Активація пристрою /dev/nullb1

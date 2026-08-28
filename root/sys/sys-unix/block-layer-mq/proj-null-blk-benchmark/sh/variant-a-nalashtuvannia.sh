# Перевірка та видалення раніше завантаженого модуля
sudo rmmod null_blk 2>/dev/null || true

# Завантаження null_blk у режимі 4 апаратних черг
sudo modprobe null_blk \
    gb=10 \
    submit_queues=4 \
    hw_queue_depth=64 \
    queue_mode=2 \
    irqmode=1 \
    completion_nsec=0

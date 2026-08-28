# Порівняльний тест: 1 апаратна черга (N:1 mapping) проти 4 апаратних черг (1:1 mapping)

# 1. Завантаження з 1 апаратною чергою
sudo rmmod null_blk 2>/dev/null || true
sudo modprobe null_blk submit_queues=1 hw_queue_depth=64 queue_mode=2
./bench_blk_mq /dev/nullb0 4

# 2. Завантаження з 4 апаратними чергами
sudo rmmod null_blk 2>/dev/null || true
sudo modprobe null_blk submit_queues=4 hw_queue_depth=64 queue_mode=2
./bench_blk_mq /dev/nullb0 4

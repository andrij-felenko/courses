# Створення нової підгрупи
mkdir /sys/fs/cgroup/worker1

# Дозволяємо кореню роздати контролери дітям — саме після цього у worker1 з'являться cpu.max, memory.max тощо
echo "+cpu +memory +io +pids" > /sys/fs/cgroup/cgroup.subtree_control

# Встановлення ліміту CPU на 50% одного ядра
echo "50000 100000" > /sys/fs/cgroup/worker1/cpu.max

# Обмеження пам'яті до 500 МіБ
echo "524288000" > /sys/fs/cgroup/worker1/memory.max

# Обмеження на 100 процесів
echo "100" > /sys/fs/cgroup/worker1/pids.max

# Додавання поточного процесу (shell) до групи
echo $$ > /sys/fs/cgroup/worker1/cgroup.procs

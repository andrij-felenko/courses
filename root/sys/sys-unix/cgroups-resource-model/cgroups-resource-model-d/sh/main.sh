# нова група для збірки
mkdir /sys/fs/cgroup/build

# корінь має роздавати дітям процесор і пам'ять
echo "+cpu +memory" > /sys/fs/cgroup/cgroup.subtree_control

# правила для групи
echo 4G              > /sys/fs/cgroup/build/memory.max
echo "200000 100000" > /sys/fs/cgroup/build/cpu.max

# переводимо саму оболонку — усі її нащадки народяться вже тут
echo $$ > /sys/fs/cgroup/build/cgroup.procs
make -j16

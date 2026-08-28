echo "+cpu +memory" > /sys/fs/cgroup/cgroup.subtree_control
mkdir /sys/fs/cgroup/build

cat /sys/fs/cgroup/build/cgroup.controllers
# cpu memory

ls /sys/fs/cgroup/build/ | grep -E '^(cpu|memory|io)\.'
# cpu.idle cpu.max cpu.max.burst cpu.pressure cpu.stat cpu.weight cpu.weight.nice
# memory.current memory.events memory.high memory.low memory.max memory.min …
# io.pressure                    ← лише файл тиску: контролер io ніхто не роздавав

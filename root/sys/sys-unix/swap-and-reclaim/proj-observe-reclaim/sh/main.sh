# cgroup v2 типово змонтовано в /sys/fs/cgroup
sudo mkdir -p /sys/fs/cgroup/probe
echo '+memory' | sudo tee /sys/fs/cgroup/cgroup.subtree_control

# межа вдвічі менша за ділянку, яку проситиме програма
echo 128M | sudo tee /sys/fs/cgroup/probe/memory.max
echo max  | sudo tee /sys/fs/cgroup/probe/memory.swap.max

# загнати поточну оболонку — програма успадкує групу
echo $$ | sudo tee /sys/fs/cgroup/probe/cgroup.procs
./swapprobe 256

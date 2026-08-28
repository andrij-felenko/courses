$ sudo mkdir /sys/fs/cgroup/lab
$ echo 1G | sudo tee /sys/fs/cgroup/lab/memory.max
$ echo 0  | sudo tee /sys/fs/cgroup/lab/memory.swap.max
$ sudo sh -c 'echo $$ > /sys/fs/cgroup/lab/cgroup.procs; exec ./promise wall --size 8'
Killed
$ cat /sys/fs/cgroup/lab/memory.events
low 0
high 0
max 47
oom 1
oom_kill 1

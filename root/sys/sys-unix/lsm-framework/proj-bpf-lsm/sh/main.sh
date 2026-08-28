$ cat /sys/kernel/security/lsm
capability,landlock,lockdown,yama,apparmor,bpf

$ sudo mkdir /sys/fs/cgroup/caged
$ sudo ./deny-net /sys/fs/cgroup/caged &
правило діє для cgroup 5342; Ctrl-C знімає

$ echo $$ | sudo tee /sys/fs/cgroup/caged/cgroup.procs > /dev/null
$ python3 -c 'import socket; socket.socket()'
Traceback (most recent call last):
  ...
PermissionError: [Errno 1] Operation not permitted

$ python3 -c 'import socket; socket.socket(socket.AF_UNIX)'
$ cat /etc/hostname
lab

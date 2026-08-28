$ make
$ sudo insmod tinyfs.ko
$ grep tinyfs /proc/filesystems
nodev	tinyfs

$ sudo mkdir -p /mnt/tiny
$ sudo mount -t tinyfs none /mnt/tiny
$ ls -la /mnt/tiny
total 0
dr-xr-xr-x 2 root root   0 сер  7 10:12 .
drwxr-xr-x 4 root root  80 сер  7 10:11 ..
-r--r--r-- 1 user user   0 сер  7 10:12 status

$ cat /mnt/tiny/status
uptime  91274 s
opens   1
magic   0x54494e59

$ cat /mnt/tiny/nope
cat: /mnt/tiny/nope: No such file or directory
$ touch /mnt/tiny/x
touch: cannot touch '/mnt/tiny/x': Permission denied

$ stat -f -c 'тип=%T довжина_імені=%l блок=%s' /mnt/tiny
тип=UNKNOWN довжина_імені=255 блок=4096

$ sudo umount /mnt/tiny
$ sudo rmmod tinyfs

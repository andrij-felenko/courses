DEV=$(lsblk -dno MAJ:MIN /dev/nvme0n1)      # 259:0
cd /sys/fs/cgroup
echo "+io" > cgroup.subtree_control
mkdir -p backup

echo "$DEV rbps=52428800" > backup/io.max   # 50 МіБ/с на читання
echo $$ > backup/cgroup.procs               # оболонка й усі її нащадки — у групі

dd if=/dev/nvme0n1 of=/dev/null bs=1M count=512 iflag=direct
cat backup/io.stat

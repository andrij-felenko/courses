# 1. Копія образу віртуальної машини на 40 ГіБ
$ cp --reflink=always vm.img clone.img
cp: failed to clone 'clone.img' from 'vm.img': Operation not supported   # ext4
$ cp --reflink=always vm.img clone.img                                   # XFS, Btrfs
$                                                                        # готово, миттєво

# 2. Місце нібито є
$ df -h /srv
/dev/sdb1       500G  372G  128G  75% /srv
$ touch /srv/probe
touch: cannot touch '/srv/probe': No space left on device                 # Btrfs

# 3. Розділ треба зменшити
$ resize2fs /dev/sda2 200G          # ext4: працює (на відмонтованій)
$ # XFS: такої операції не існує взагалі — тільки зростання

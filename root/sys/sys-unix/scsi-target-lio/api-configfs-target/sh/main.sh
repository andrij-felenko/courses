T=/sys/kernel/config/target
IQN=iqn.2026-08.org.example:store
CLI=iqn.2026-08.org.example:client

mkdir -p $T/core/fileio_0/disk1
echo "fd_dev_name=/srv/disk1.img,fd_dev_size=1073741824" > $T/core/fileio_0/disk1/control
echo 1 > $T/core/fileio_0/disk1/enable

mkdir -p $T/iscsi/$IQN/tpgt_1/np/0.0.0.0:3260
cd $T/iscsi/$IQN/tpgt_1

mkdir lun/lun_0 &&        ln -s $T/core/fileio_0/disk1 lun/lun_0/backing
mkdir -p acls/$CLI/lun_0 && ln -s $PWD/lun/lun_0      acls/$CLI/lun_0/mapped
echo 1 > enable

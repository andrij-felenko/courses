IQN=iqn.2026-08.org.example:store
mkdir -p $CFG/iscsi/$IQN/tpgt_1/np/0.0.0.0:3260
cd $CFG/iscsi/$IQN/tpgt_1

mkdir lun/lun_0
ln -s $CFG/core/fileio_0/disk1 lun/lun_0/store

INIT=$(sed -n 's/^InitiatorName=//p' /etc/iscsi/initiatorname.iscsi)
mkdir -p acls/$INIT/lun_0
ln -s $CFG/iscsi/$IQN/tpgt_1/lun/lun_0 acls/$INIT/lun_0/mapped

echo 0 > attrib/authentication
echo 1 > enable

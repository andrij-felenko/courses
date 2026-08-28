umount /mnt/t
iscsiadm -m node -T $IQN -p 127.0.0.1:3260 --logout
iscsiadm -m node -T $IQN -p 127.0.0.1:3260 -o delete
echo NULL > $CFG/loopback/$WWN/tpgt_0/nexus
rm $CFG/loopback/$WWN/tpgt_0/lun/lun_0/store
rmdir $CFG/loopback/$WWN/tpgt_0/lun/lun_0 $CFG/loopback/$WWN/tpgt_0 $CFG/loopback/$WWN

cd $CFG/iscsi/$IQN/tpgt_1 && echo 0 > enable
rm acls/$INIT/lun_0/mapped lun/lun_0/store
rmdir acls/$INIT/lun_0 acls/$INIT lun/lun_0 np/0.0.0.0:3260
cd $CFG && rmdir iscsi/$IQN/tpgt_1 iscsi/$IQN core/fileio_0/disk1 core/fileio_0

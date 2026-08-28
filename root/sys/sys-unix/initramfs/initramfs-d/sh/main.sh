# 2. перенести вже підняті службові монтування в новий корінь
mount --move /dev  /sysroot/dev
mount --move /proc /sysroot/proc
mount --move /sys  /sysroot/sys
# 3. стати в новий корінь і зробити його коренем дерева
cd /sysroot
mount --move . /
# 4. перевести точку відліку процесу й віддати керування
chroot .
exec /sbin/init

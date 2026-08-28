/* 1. Переведення кореневого монтування в приватний режим */
mount(NULL, "/", NULL, MS_REC | MS_PRIVATE, NULL);

/* 2. Перетворення цільового каталогу rootfs на самостійну точку монтування */
mount(rootfs_path, rootfs_path, "bind", MS_BIND | MS_REC, NULL);

/* 3. Атомарний поворот кореня */
syscall(SYS_pivot_root, rootfs_path, old_root_path);

/* 4. Від'єднання старого хостового кореня */
chdir("/");
umount2("/.old_root", MNT_DETACH);
rmdir("/.old_root");

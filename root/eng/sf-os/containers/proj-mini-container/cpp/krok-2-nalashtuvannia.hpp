/* 1. Переведення кореневого монтування в приватний режим */
::mount(nullptr, "/", nullptr, MS_REC | MS_PRIVATE, nullptr);

/* 2. Перетворення цільового каталогу rootfs на самостійну точку монтування */
::mount(rootfs_path.c_str(), rootfs_path.c_str(), "bind", MS_BIND | MS_REC, nullptr);

/* 3. Атомарний поворот кореня */
::syscall(SYS_pivot_root, rootfs_path.c_str(), old_root_path.c_str());

/* 4. Від'єднання старого хостового кореня */
::chdir("/");
::umount2("/.old_root", MNT_DETACH);
::fs::remove("/.old_root", ec);

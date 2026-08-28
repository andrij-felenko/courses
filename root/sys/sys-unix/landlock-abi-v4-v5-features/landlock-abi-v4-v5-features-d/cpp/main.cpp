landlock_ruleset_attr attr{};

// ABI v1: базові файлові операції
attr.handled_access_fs = LANDLOCK_ACCESS_FS_READ_FILE | 
                         LANDLOCK_ACCESS_FS_READ_DIR | 
                         LANDLOCK_ACCESS_FS_EXECUTE;

// ABI v5: додаємо контроль ioctl пристроїв
if (abi >= 5) {
    attr.handled_access_fs |= LANDLOCK_ACCESS_FS_IOCTL_DEV;
}

// ABI v4: додаємо мережевий контроль
if (abi >= 4) {
    attr.handled_access_net = LANDLOCK_ACCESS_NET_BIND_TCP | 
                              LANDLOCK_ACCESS_NET_CONNECT_TCP;
}

int ruleset_fd = landlock_create_ruleset(&attr, sizeof(attr), 0);

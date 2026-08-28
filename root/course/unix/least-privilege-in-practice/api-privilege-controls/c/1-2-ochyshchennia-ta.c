/* 1. Повне очищення списку додаткових груп */
if (setgroups(0, NULL) != 0) {
    perror("FATAL: setgroups(0, NULL) failed");
    abort();
}

/* 2. АБО завантаження груп виділеного облікового запису з бази /etc/group */
if (initgroups("daemon_user", target_gid) != 0) {
    perror("FATAL: initgroups failed");
    abort();
}

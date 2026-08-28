// Безпечний варіант функції робітника мовою C
void safe_worker_iteration(int dirfd, const char* filename) {
    // 1. Атомарне відкриття файлу без слідування за симлінками
    int fd = openat(dirfd, filename, O_WRONLY | O_NOFOLLOW | O_CLOEXEC);
    if (fd < 0) {
        // Якщо це був симлінк, openat поверне -1, а errno буде ELOOP
        if (errno == ELOOP) {
            // Атаку підміни виявлено та знешкоджено ядром на етапі відкриття
            return;
        }
        // Файл не існує або немає доступу
        return;
    }

    // 2. Додаткова валідація вже зафіксованого інода через fstat
    struct stat st;
    if (fstat(fd, &st) == 0) {
        if (S_ISREG(st.st_mode)) {
            const char msg[] = "SAFE_DATA_WRITE\n";
            write(fd, msg, sizeof(msg) - 1);
        }
    }

    close(fd);
}

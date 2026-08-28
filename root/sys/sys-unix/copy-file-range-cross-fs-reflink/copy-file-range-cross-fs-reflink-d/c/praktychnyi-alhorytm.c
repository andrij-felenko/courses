// Стратегія надійного клонування файлів мовою C
bool copy_file_cascading(int fd_in, int fd_out, size_t file_size) {
    // 1. Спроба Reflink (FICLONE)
    if (ioctl(fd_out, FICLONE, fd_in) == 0) {
        return true; // Миттєво, 0 байт I/O
    }

    // 2. Спроба copy_file_range (Offload / Cross-FS)
    loff_t off_in = 0, off_out = 0;
    size_t remaining = file_size;

    while (remaining > 0) {
        ssize_t ret = copy_file_range(fd_in, &off_in, fd_out, &off_out, remaining, 0);
        if (ret > 0) {
            remaining -= (size_t)ret;
            continue;
        }
        if (ret == 0) break; // EOF
        if (errno == EINTR) continue;

        // При EXDEV, EOPNOTSUPP або EINVAL каскадно переходимо на splice або read/write
        if (errno == EXDEV || errno == EOPNOTSUPP || errno == ENOSYS || errno == EINVAL) {
            break;
        }
        return false; // Непоправна помилка
    }

    if (remaining == 0) return true;

    // 3. Фолбек на послідовний POSIX read/write або splice
    // (Повна реалізація наведена у проєктній вставці)
    // Зміщення передаємо явно: частину файлу могло вже перенести copy_file_range
    return fallback_read_write_loop(fd_in, &off_in, fd_out, &off_out, remaining);
}

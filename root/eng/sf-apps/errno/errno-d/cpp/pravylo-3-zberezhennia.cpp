int fd = ::open(filename, O_RDONLY);
if (fd == -1) {
    int saved_errno = errno; // Фіксуємо початковий стан

    if (temp_fd != -1) {
        ::close(temp_fd); // Не боїмося перезапису errno
    }

    // Працюємо виключно зі збереженим кодом
    log_error("Failed to open", filename, saved_errno);
    return -1;
}

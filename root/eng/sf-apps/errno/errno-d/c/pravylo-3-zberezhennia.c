int fd = open(filename, O_RDONLY);
if (fd == -1) {
    int saved_errno = errno; /* Зберегли початкову причину */

    /* Прибирання за собою: закриваємо тимчасові файли, якщо вони були */
    if (temp_fd != -1) {
        close(temp_fd); /* Цей виклик може перезаписати errno, але нам байдуже */
    }

    /* Логуємо саме збережений код */
    fprintf(stderr, "Failed to open %s: %s\n", filename, strerror(saved_errno));
    return -1;
}

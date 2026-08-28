void *buffer = NULL;
size_t mem_align = stx.stx_dio_mem_align;
size_t buffer_bytes = 65536; /* 64 КБ */

/* Якщо ядро не надало вирівнювання, беремо стандартний розмір сторінки */
if ((stx.stx_mask & STATX_DIOALIGN) == 0 || mem_align == 0) {
    mem_align = sysconf(_SC_PAGESIZE);
}

/* Виділення пам'яті з точним вирівнюванням під апаратний сектор диска */
if (posix_memalign(&buffer, mem_align, buffer_bytes) != 0) {
    perror("Помилка виділення вирівняної пам'яті через posix_memalign");
    return;
}

/* Пряме читання з файлу з гарантією відсутності помилки EINVAL */
ssize_t bytes_read = pread(fd, buffer, buffer_bytes, aligned_offset);

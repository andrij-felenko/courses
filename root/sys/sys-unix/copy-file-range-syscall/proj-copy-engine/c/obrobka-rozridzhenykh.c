off_t data_off = lseek(fd_in, current_off, SEEK_DATA);
if (data_off != (off_t)-1) {
    off_t hole_off = lseek(fd_in, data_off, SEEK_HOLE);
    if (hole_off != (off_t)-1) {
        /* Окремі змінні: ядро посуває КОЖНЕ зміщення на скопійований обсяг,
           один вказівник на обидва аргументи посунув би його двічі */
        loff_t in_off = data_off, out_off = data_off;
        size_t remaining = (size_t)(hole_off - data_off);
        while (remaining > 0) {
            /* Копіюємо лише реальні блоки даних через copy_file_range */
            ssize_t n = copy_file_range(fd_in, &in_off, fd_out, &out_off, remaining, 0);
            if (n < 0) { if (errno == EINTR) continue; break; }
            if (n == 0) break;
            remaining -= (size_t)n;
        }
        current_off = hole_off;
    }
}

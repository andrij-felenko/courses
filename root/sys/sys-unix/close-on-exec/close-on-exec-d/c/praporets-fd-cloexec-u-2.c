/* Внутрішня функція ядра Linux (простір ядра) */
static void do_close_on_exec(struct files_struct *files)
{
    unsigned int j;
    struct fdtable *fdt = files_fdtable(files);

    /* Ітерація по машинних словах бітової маски */
    for (j = 0; j < fdt->max_fds; j += BITS_PER_LONG) {
        unsigned long set = fdt->close_on_exec[j / BITS_PER_LONG];
        if (!set)
            continue;
        fdt->close_on_exec[j / BITS_PER_LONG] = 0;
        for (unsigned int fd = j; set; fd++, set >>= 1) {
            if (set & 1) {
                struct file *file = fdt->fd[fd];
                if (file) {
                    rcu_assign_pointer(fdt->fd[fd], NULL);
                    __clear_open_fd(fd, fdt);
                    filp_close(file, files);
                }
            }
        }
    }
}

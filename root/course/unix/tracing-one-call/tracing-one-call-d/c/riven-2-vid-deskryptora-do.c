/* Логіка перетворення fd -> struct file (спрощено) */
struct fd fdget_pos(int fd)
{
    struct files_struct *files = current->files;
    struct file *file = NULL;

    if (fd < files->fdt->max_fds)
        file = files->fdt->fd[fd]; /* для fd=1 беремо елемент із індексом 1 */

    if (!file)
        return (struct fd){ NULL, 0 };

    /* Якщо файловий дескриптор використовується кількома потоками,
     * блокуємо f_pos_lock для запобігання гонитви за позицію у файлі */
    if (file->f_mode & FMODE_ATOMIC_POS)
        mutex_lock(&file->f_pos_lock);

    return (struct fd){ file, flags };
}

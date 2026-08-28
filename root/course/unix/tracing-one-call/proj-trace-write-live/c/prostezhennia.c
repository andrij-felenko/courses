/* Спрощена логіка fdget_pos у ядрі */
static inline struct fd fdget_pos(int fd)
{
    struct fd f = fdget(fd);
    if (f.file && (f.file->f_mode & FMODE_ATOMIC_POS)) {
        if (file_count(f.file) > 1) {
            mutex_lock(&f.file->f_pos_lock);
            f.flags |= FDPUT_POS_UNLOCK;
        }
    }
    return f;
}

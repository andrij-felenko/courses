static struct slot *map_log(const char *path, int *fd_out)
{
    int fd = open(path, O_RDWR);
    if (fd < 0) { perror("open"); return NULL; }

    void *base = mmap(NULL, (size_t)SLOT * SLOTS, PROT_READ | PROT_WRITE,
                      MAP_SHARED_VALIDATE | MAP_SYNC, fd, 0);
    if (base != MAP_FAILED) { *fd_out = fd; return base; }

    switch (errno) {
    case EOPNOTSUPP:
        fprintf(stderr, "файл не тягне MAP_SYNC: прямого звертання для нього немає\n");
        break;
    case EINVAL:
        fprintf(stderr, "ядро не знає MAP_SHARED_VALIDATE — старіше за 4.15\n");
        break;
    default:
        perror("mmap");
    }
    close(fd);
    return NULL;              /* продовжити без гарантій — гірше, ніж не запуститися */
}

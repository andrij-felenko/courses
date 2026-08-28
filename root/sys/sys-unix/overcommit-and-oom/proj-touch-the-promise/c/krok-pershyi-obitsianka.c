enum how { H_MALLOC, H_CALLOC, H_NORESERVE };

static void *promise(size_t bytes, enum how how)
{
    void *p;
    if (how == H_NORESERVE)
        p = mmap(NULL, bytes, PROT_READ | PROT_WRITE,
                 MAP_PRIVATE | MAP_ANONYMOUS | MAP_NORESERVE, -1, 0);
    else
        p = (how == H_CALLOC) ? calloc(1, bytes) : malloc(bytes);

    if (!p || p == MAP_FAILED) {
        printf("обіцянка НЕ вдалася: %s\n", strerror(errno));
        return NULL;
    }
    printf("обіцянка = %p\n", p);
    return p;
}

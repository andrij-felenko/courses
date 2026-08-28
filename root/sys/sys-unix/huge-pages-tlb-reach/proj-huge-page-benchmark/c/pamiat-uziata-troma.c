/* Ділянка, початок якої вирівняний на align (степінь двійки, кратна PAGE). */
static char *mmap_aligned(size_t len, size_t align)
{
        size_t total = len + align;
        char *raw = mmap(NULL, total, PROT_READ | PROT_WRITE,
                         MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
        if (raw == MAP_FAILED)
                return MAP_FAILED;

        uintptr_t start = ((uintptr_t)raw + align - 1) & ~(uintptr_t)(align - 1);
        size_t head = start - (uintptr_t)raw;
        if (head)
                munmap(raw, head);
        if (total - head - len)
                munmap((char *)start + len, total - head - len);
        return (char *)start;
}

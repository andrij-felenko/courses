static void flush(const void *addr, size_t len)
{
    const char *p   = (const char *)((uintptr_t)addr & ~(uintptr_t)(LINE - 1));
    const char *end = (const char *)addr + len;
    for (; p < end; p += LINE)
        _mm_clwb((void *)p);
}

static void fence(void)
{
    __atomic_signal_fence(__ATOMIC_SEQ_CST);   /* компіляторові: нічого не переставляй */
    _mm_sfence();                              /* процесорові: дочекайся виштовхувань */
}

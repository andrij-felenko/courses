static inline unsigned int rdpkru(void)
{
    unsigned int pkru;
    __asm__ volatile(".byte 0x0f,0x01,0xee" : "=a"(pkru) : "c"(0) : "edx");
    return pkru;
}

static inline void wrpkru(unsigned int value)
{
    __asm__ volatile(".byte 0x0f,0x01,0xef"
                     :: "a"(value), "c"(0), "d"(0) : "memory");
}

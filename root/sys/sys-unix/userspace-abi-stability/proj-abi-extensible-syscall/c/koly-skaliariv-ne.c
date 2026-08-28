struct pacer_attr {
        __u16 len;    /* довжина РАЗОМ із цим заголовком, без заповнювача */
        __u16 type;
};

#define PACER_ATTR_ALIGNTO   4
#define PACER_ATTR_ALIGN(n)  (((n) + PACER_ATTR_ALIGNTO - 1) & ~(PACER_ATTR_ALIGNTO - 1))
#define PACER_ATTR_HDRLEN    PACER_ATTR_ALIGN(sizeof(struct pacer_attr))

enum {
        PACER_A_UNSPEC = 0,
        PACER_A_EXEMPT_PATH,   /* рядок */
        PACER_A_EXEMPT_INO,    /* __u64 */
        __PACER_A_MAX,
};
#define PACER_ATTR_MAX      (__PACER_A_MAX - 1)
#define PACER_ATTRS_KNOWN   (BIT_ULL(PACER_A_EXEMPT_PATH) | BIT_ULL(PACER_A_EXEMPT_INO))
#define PACER_ATTRS_MAX_LEN 4096   /* стеля на весь хвіст */

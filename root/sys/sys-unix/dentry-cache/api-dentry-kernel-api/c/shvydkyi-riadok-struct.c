struct qstr {
    union {
        struct {
            u32 hash;
            u32 len;
        };
        u64 hashlen;
    };
    const unsigned char *name;
};

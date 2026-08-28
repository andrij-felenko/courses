struct hwrng {
    const char *name;
    int (*init)(struct hwrng *rng);
    void (*cleanup)(struct hwrng *rng);
    int (*data_present)(struct hwrng *rng, int wait);
    int (*data_read)(struct hwrng *rng, u32 *data);
    int (*read)(struct hwrng *rng, void *data, size_t max, bool wait);
    unsigned short quality;
    unsigned long priv;
};

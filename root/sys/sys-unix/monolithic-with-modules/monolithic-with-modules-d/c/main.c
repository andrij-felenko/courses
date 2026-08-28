/* ядро версії A */
struct some_kernel_struct {
    int  flags;
    void *priv;
};

/* ядро версії B — додано поле посередині */
struct some_kernel_struct {
    int  flags;
    void *stats;        /* усі наступні поля переїхали */
    void *priv;
};

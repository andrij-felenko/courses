struct crypto_alg {
    struct list_head    cra_list;
    struct list_head    cra_users;
    
    u32                 cra_flags;
    unsigned int        cra_blocksize;
    unsigned int        cra_ctxsize;
    unsigned int        cra_alignmask;
    
    int                 cra_priority;
    refcount_t          cra_refcnt;
    
    char                cra_name[CRYPTO_MAX_ALG_NAME];
    char                cra_driver_name[CRYPTO_MAX_ALG_NAME];
    
    const struct crypto_type *cra_type;
    struct module       *cra_module;
};

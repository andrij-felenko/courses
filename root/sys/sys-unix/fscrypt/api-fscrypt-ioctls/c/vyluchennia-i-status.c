struct fscrypt_remove_key_arg {
        struct fscrypt_key_specifier key_spec;
        __u32 removal_status_flags;   /* вихід */
        __u32 __reserved[5];
};

struct fscrypt_get_key_status_arg {
        struct fscrypt_key_specifier key_spec;   /* вхід */
        __u32 __reserved[6];
        __u32 status;                            /* вихід: 1 / 2 / 3 */
        __u32 status_flags;                      /* 0x1 = ADDED_BY_SELF */
        __u32 user_count;                        /* скільки заявок на ключ */
        __u32 __out_reserved[13];
};

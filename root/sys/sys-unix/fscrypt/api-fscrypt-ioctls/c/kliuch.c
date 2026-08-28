struct fscrypt_key_specifier {
        __u32 type;             /* 1 = DESCRIPTOR (v1), 2 = IDENTIFIER (v2) */
        __u32 __reserved;
        union {
                __u8 __reserved[32];
                __u8 descriptor[8];     /* FSCRYPT_KEY_DESCRIPTOR_SIZE */
                __u8 identifier[16];    /* FSCRYPT_KEY_IDENTIFIER_SIZE */
        } u;
};

struct fscrypt_add_key_arg {
        struct fscrypt_key_specifier key_spec;  /* вхід; для v2 identifier — ВИХІД */
        __u32 raw_size;                         /* 16..64, або 0 при key_id != 0 */
        __u32 key_id;                           /* 0 або ключ зі зв'язки ядра */
        __u32 flags;                            /* 0x1 = FSCRYPT_ADD_KEY_FLAG_HW_WRAPPED */
        __u32 __reserved[7];                    /* нулі */
        __u8  raw[];                            /* сам секрет */
};

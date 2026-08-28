struct fsverity_enable_arg {
        __u32 version;          /* має бути 1 */
        __u32 hash_algorithm;   /* 1 = SHA-256, 2 = SHA-512 */
        __u32 block_size;       /* у байтах, степінь двійки */
        __u32 salt_size;        /* 0..32 */
        __u64 salt_ptr;         /* адреса солі в просторі користувача */
        __u32 sig_size;         /* 0, якщо вбудованого підпису немає */
        __u32 __reserved1;      /* нуль */
        __u64 sig_ptr;          /* адреса підпису PKCS#7 */
        __u64 __reserved2[11];  /* нулі */
};                              /* 128 байтів */

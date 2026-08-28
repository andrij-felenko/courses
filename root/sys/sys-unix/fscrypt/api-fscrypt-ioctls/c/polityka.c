#define FSCRYPT_POLICY_V1  0            /* так, нуль */
#define FSCRYPT_POLICY_V2  2

struct fscrypt_policy_v2 {
        __u8 version;                   /* 2 */
        __u8 contents_encryption_mode;
        __u8 filenames_encryption_mode;
        __u8 flags;
        __u8 log2_data_unit_size;       /* 0 — блок файлової системи */
        __u8 __reserved[3];             /* нулі */
        __u8 master_key_identifier[16]; /* FSCRYPT_KEY_IDENTIFIER_SIZE */
};

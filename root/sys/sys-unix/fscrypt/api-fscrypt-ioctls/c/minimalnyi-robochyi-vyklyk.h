struct {
        struct fscrypt_add_key_arg arg;
        __u8 raw[32];
} k = { 0 };                       /* обнулення обов'язкове: є резервні поля */

k.arg.key_spec.type = FSCRYPT_KEY_SPEC_TYPE_IDENTIFIER;
k.arg.raw_size      = 32;
memcpy(k.raw, master_key, 32);     /* 32 байти з /dev/urandom */

int mnt = open("/data", O_RDONLY | O_DIRECTORY);
if (ioctl(mnt, FS_IOC_ADD_ENCRYPTION_KEY, &k.arg) != 0)
        perror("FS_IOC_ADD_ENCRYPTION_KEY");
/* ядро вписало 16 байтів у k.arg.key_spec.u.identifier */

struct fscrypt_policy_v2 pol = {
        .version                   = FSCRYPT_POLICY_V2,
        .contents_encryption_mode  = FSCRYPT_MODE_AES_256_XTS,
        .filenames_encryption_mode = FSCRYPT_MODE_AES_256_CTS,
        .flags                     = FSCRYPT_POLICY_FLAGS_PAD_32,
};
memcpy(pol.master_key_identifier, k.arg.key_spec.u.identifier, 16);

int dir = open("/data/oksana", O_RDONLY | O_DIRECTORY);   /* каталог порожній */
if (ioctl(dir, FS_IOC_SET_ENCRYPTION_POLICY, &pol) != 0)
        perror("FS_IOC_SET_ENCRYPTION_POLICY");

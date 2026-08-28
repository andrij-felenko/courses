#include <linux/fscrypt.h>   /* окремий uapi-заголовок — з ядра 5.4 */

#define FS_IOC_SET_ENCRYPTION_POLICY     _IOR('f', 19, struct fscrypt_policy_v1)
#define FS_IOC_GET_ENCRYPTION_PWSALT     _IOW('f', 20, __u8[16])
#define FS_IOC_GET_ENCRYPTION_POLICY     _IOW('f', 21, struct fscrypt_policy_v1)
#define FS_IOC_GET_ENCRYPTION_POLICY_EX  _IOWR('f', 22, __u8[9])
#define FS_IOC_ADD_ENCRYPTION_KEY        _IOWR('f', 23, struct fscrypt_add_key_arg)
#define FS_IOC_REMOVE_ENCRYPTION_KEY     _IOWR('f', 24, struct fscrypt_remove_key_arg)
#define FS_IOC_REMOVE_ENCRYPTION_KEY_ALL_USERS \
                                         _IOWR('f', 25, struct fscrypt_remove_key_arg)
#define FS_IOC_GET_ENCRYPTION_KEY_STATUS _IOWR('f', 26, struct fscrypt_get_key_status_arg)
#define FS_IOC_GET_ENCRYPTION_NONCE      _IOR('f', 27, __u8[16])

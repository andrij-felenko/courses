#include <sys/types.h>
#include <sys/stat.h>
#include <errno.h>

/* Імітація алгоритму перевірки прав VFS ядра Linux */
int check_dac_permission(uid_t current_fsuid, gid_t current_fsgid,
                         uid_t inode_uid, gid_t inode_gid,
                         mode_t inode_mode, int requested_mask)
{
    /* 1. Якщо процес є власником інода, перевіряються біти власника (0700) */
    if (current_fsuid == inode_uid) {
        if ((inode_mode & (requested_mask << 6)) == (requested_mask << 6))
            return 0;
        return -EACCES;
    }

    /* 2. Якщо процес входить до групи інода, перевіряються біти групи (0070) */
    if (current_fsgid == inode_gid) {
        if ((inode_mode & (requested_mask << 3)) == (requested_mask << 3))
            return 0;
        return -EACCES;
    }

    /* 3. Для всіх інших користувачів перевіряються біти others (0007) */
    if ((inode_mode & requested_mask) == (mode_t)requested_mask)
        return 0;

    return -EACCES;
}

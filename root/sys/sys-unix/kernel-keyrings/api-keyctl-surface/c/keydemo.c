/* збірка: cc -o keydemo keydemo.c -lkeyutils */
#include <keyutils.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>

int main(void)
{
    /* 1. покласти секрет так, щоб назад його не забрав ніхто */
    key_serial_t k = add_key("logon", "myfs:vol0", "s3cret", 6,
                             KEY_SPEC_SESSION_KEYRING);
    if (k == -1) { perror("add_key"); return 1; }
    printf("serial = %d (0x%08x)\n", k, k);

    /* 2. знайти той самий ключ пошуком — так само робить ядро */
    key_serial_t f = keyctl_search(KEY_SPEC_SESSION_KEYRING,
                                   "logon", "myfs:vol0", 0);
    printf("search -> %d\n", f);

    /* 3. тип не віддає вміст навіть тому, хто його поклав */
    char buf[64];
    if (keyctl_read(k, buf, sizeof buf) == -1)
        printf("read -> %s\n", strerror(errno));   /* Operation not supported */

    /* 4. усе тримачеві, собі — лише право бачити */
    keyctl_setperm(k, KEY_POS_ALL | KEY_USR_VIEW);

    /* 5. хай згине сам через п'ять хвилин */
    keyctl_set_timeout(k, 300);
    return 0;
}

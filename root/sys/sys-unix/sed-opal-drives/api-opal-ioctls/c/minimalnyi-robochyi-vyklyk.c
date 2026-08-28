#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>
#include <linux/sed-opal.h>

int main(void)
{
        int fd = open("/dev/nvme0n1", O_RDONLY);   /* цілий носій, не розділ */
        struct opal_status st = {0};
        const char *pin = "correct horse battery";

        if (ioctl(fd, IOC_OPAL_GET_STATUS, &st) < 0) { perror("GET_STATUS"); return 1; }
        printf("flags=0x%08x locked=%d mbr=%d\n", st.flags,
               !!(st.flags & OPAL_FL_LOCKED), !!(st.flags & OPAL_FL_MBR_ENABLED));

        struct opal_lock_unlock lu = {
                .session = {
                        .who = OPAL_ADMIN1,
                        .sum = 0,
                        .opal_key = { .lr = 1, .key_type = OPAL_INCLUDED },
                },
                .l_state = OPAL_RW,
        };
        lu.session.opal_key.key_len = strlen(pin);
        memcpy(lu.session.opal_key.key, pin, lu.session.opal_key.key_len);

        if (ioctl(fd, IOC_OPAL_LOCK_UNLOCK, &lu) < 0) { perror("UNLOCK"); return 1; }

        lu.flags = OPAL_SAVE_FOR_LOCK;             /* дозволити замикання без пароля */
        if (ioctl(fd, IOC_OPAL_SAVE, &lu) < 0) { perror("SAVE"); return 1; }

        return 0;
}

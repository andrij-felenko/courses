/* demo-handler.c — cc -Wall -O2 demo-handler.c -o demo-handler -lkeyutils
   кладеться в /usr/local/sbin; запускає його request-key від імені root */
#include <keyutils.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char *argv[])
{
    if (argc != 5) {
        fprintf(stderr, "usage: %s <key> <desc> <callout> <ring>\n", argv[0]);
        return 2;
    }
    key_serial_t key  = (key_serial_t)strtol(argv[1], NULL, 10);
    const char  *desc = argv[2];
    key_serial_t ring = (key_serial_t)strtol(argv[4], NULL, 10);

    /* повноваження рівно на цей один ключ; без них ядро відповість EPERM */
    if (keyctl_assume_authority(key) < 0) { perror("assume_authority"); return 1; }

    if (strstr(desc, "forbidden")) {           /* добувати нема чого */
        keyctl_reject(key, 60, ENOKEY, ring);  /* від'ємне наповнення на 60 с */
        return 0;
    }

    char payload[128];
    int n = snprintf(payload, sizeof payload, "material:%s", desc);
    if (n < 0 || n >= (int)sizeof payload) return 1;

    if (keyctl_instantiate(key, payload, n, ring) < 0) { perror("instantiate"); return 1; }
    return 0;
}

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/mman.h>

int main(void)
{
    long ps = sysconf(_SC_PAGESIZE);
    char *secret = aligned_alloc(ps, ps);
    if (!secret)
        return 1;
    strcpy(secret, "приватний ключ");

    int pkey = pkey_alloc(0, PKEY_DISABLE_ACCESS);
    if (pkey < 0) {
        perror("pkey_alloc");          /* ENOSPC — ключів немає або їх не підтримано */
        return 1;
    }
    if (pkey_mprotect(secret, ps, PROT_READ | PROT_WRITE, pkey) < 0) {
        perror("pkey_mprotect");
        return 1;
    }

    /* тут будь-яке звернення до secret дає SIGSEGV */

    pkey_set(pkey, 0);                     /* відчинили: одна команда WRPKRU */
    size_t n = strlen(secret);             /* коротка робота з секретом      */
    pkey_set(pkey, PKEY_DISABLE_ACCESS);   /* зачинили                       */

    printf("довжина секрету: %zu\n", n);
    return 0;
}

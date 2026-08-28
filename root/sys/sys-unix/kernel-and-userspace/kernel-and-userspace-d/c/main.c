#include <unistd.h>
#include <errno.h>
#include <stdio.h>

int main(void) {
    char *bad = (char *)0x10;          /* адреси 0x10 у процесі немає */
    ssize_t n = write(1, bad, 16);     /* дескриптор 1 веде в термінал */
    printf("n=%zd errno=%d (EFAULT=%d)\n", n, errno, EFAULT);
    return 0;                          /* n=-1 errno=14 (EFAULT=14) */
}

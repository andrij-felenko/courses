#include <unistd.h>
#include <sys/syscall.h>
#include <errno.h>
#include <stdio.h>

int main(void)
{
    static const char msg[] = "Привіт із загальних дверей\n";

    long r = syscall(SYS_write, 1, msg, sizeof msg - 1);
    if (r == -1)
        fprintf(stderr, "не вийшло: errno=%d\n", errno);
    return 0;
}

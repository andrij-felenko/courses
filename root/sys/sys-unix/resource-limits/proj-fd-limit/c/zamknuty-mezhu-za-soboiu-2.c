#include <stdio.h>
#include <sys/resource.h>

int main(void)
{
    struct rlimit rl;

    getrlimit(RLIMIT_NOFILE, &rl);
    printf("дали: м'який %llu, жорсткий %llu\n",
           (unsigned long long)rl.rlim_cur, (unsigned long long)rl.rlim_max);

    rl.rlim_cur = rl.rlim_max = 4096;
    if (setrlimit(RLIMIT_NOFILE, &rl) != 0)
        perror("спроба підняти назад");
    return 0;
}

#define _GNU_SOURCE
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/resource.h>

int main(void)
{
        size_t len = 1024 * 1024;
        void *p = mmap(NULL, len, PROT_READ | PROT_WRITE,
                       MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
        if (p == MAP_FAILED) { perror("mmap"); return 1; }

        struct rlimit rl;
        getrlimit(RLIMIT_MEMLOCK, &rl);
        printf("м'яка межа: %llu Б\n", (unsigned long long) rl.rlim_cur);

        if (mlock(p, len) != 0) { perror("mlock"); return 1; }
        memset(p, 0, len);      /* сторінки вже в пам'яті — жодного збою */

        char line[256];
        FILE *f = fopen("/proc/self/status", "r");
        while (fgets(line, sizeof line, f))
                if (strncmp(line, "VmLck:", 6) == 0)
                        fputs(line, stdout);
        fclose(f);

        munlock(p, len);
        munmap(p, len);
        return 0;
}

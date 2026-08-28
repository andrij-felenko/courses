#include <sys/resource.h>
#include <stdio.h>
#include <stdlib.h>

/* Sets strict virtual memory limit for logspace execution */
int set_logspace_memory_limit(size_t limit_bytes) {
    struct rlimit rl;
    
    rl.rlim_cur = limit_bytes; /* Soft limit */
    rl.rlim_max = limit_bytes; /* Hard limit */

    if (setrlimit(RLIMIT_AS, &rl) != 0) {
        perror("Failed to set RLIMIT_AS memory limit");
        return -1;
    }
    
    return 0;
}

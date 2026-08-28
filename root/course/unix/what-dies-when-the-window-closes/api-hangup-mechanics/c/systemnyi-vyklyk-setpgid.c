#include <unistd.h>
#include <stdio.h>
#include <errno.h>

int assign_process_group(pid_t pid, pid_t pgid) {
    if (setpgid(pid, pgid) < 0) {
        perror("setpgid");
        return -1;
    }
    return 0;
}

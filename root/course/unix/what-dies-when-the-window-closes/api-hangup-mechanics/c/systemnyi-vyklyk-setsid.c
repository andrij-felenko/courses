#include <unistd.h>
#include <stdio.h>
#include <errno.h>

pid_t create_isolated_session(void) {
    pid_t sid = setsid();
    if (sid < 0) {
        perror("setsid");
        return -1;
    }
    return sid;
}

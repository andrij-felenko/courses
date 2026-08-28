#include <linux/ptp_clock.h>
#include <time.h>

#define CLOCKFD 3
#define FD_TO_CLOCKID(fd) ((~(clockid_t)(fd) << 3) | CLOCKFD)

// Зчитування поточного апаратного часу:
struct timespec64 ts;
clockid_t clkid = FD_TO_CLOCKID(ptp_fd);
clock_gettime(clkid, (struct timespec *)&ts);

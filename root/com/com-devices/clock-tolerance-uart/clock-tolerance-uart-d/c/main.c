#include <sys/ioctl.h>
#include <linux/serial.h>
#include <stdbool.h>

bool check_framing_errors_c(int fd) {
    struct serial_icounter_struct icounter;
    if (ioctl(fd, TIOCGICOUNT, &icounter) == 0) {
        return (icounter.frame > 0);
    }
    return false;
}

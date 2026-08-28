#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/serial.h>

int set_low_latency(int fd) {
    struct serial_struct serial;
    if (ioctl(fd, TIOCGSERIAL, &serial) < 0) {
        return -1;
    }
    serial.flags |= ASYNC_LOW_LATENCY;
    if (ioctl(fd, TIOCSSERIAL, &serial) < 0) {
        return -1;
    }
    return 0;
}

#include <termios.h>
#include <unistd.h>

int configure_frame(int fd, speed_t baud_rate) {
    struct termios options;
    if (tcgetattr(fd, &options) != 0) {
        return -1;
    }
    cfsetispeed(&options, baud_rate);
    cfsetospeed(&options, baud_rate);
    
    options.c_cflag &= ~PARENB;
    options.c_cflag &= ~CSTOPB;
    options.c_cflag &= ~CSIZE;
    options.c_cflag |= CS8;
    options.c_cflag |= (CLOCAL | CREAD);
    
    options.c_lflag &= ~(ICANON | ECHO | ECHOE | ISIG);
    options.c_iflag &= ~(IXON | IXOFF | IXANY);
    options.c_oflag &= ~OPOST;
    
    return tcsetattr(fd, TCSANOW, &options);
}

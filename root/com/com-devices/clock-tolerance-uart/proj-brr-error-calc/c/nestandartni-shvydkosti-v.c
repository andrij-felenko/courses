#include <asm/termbits.h>
#include <sys/ioctl.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdbool.h>

bool set_custom_baudrate_c(int fd, unsigned int custom_baud) {
    struct termios2 tio;
    if (ioctl(fd, TCGETS2, &tio) < 0) {
        return false;
    }
    
    /* Скидаємо маску стандартної швидкості та встановлюємо довільну */
    tio.c_cflag &= ~CBAUD;
    tio.c_cflag |= BOTHER;
    tio.c_ispeed = custom_baud;
    tio.c_ospeed = custom_baud;
    
    return (ioctl(fd, TCSETS2, &tio) >= 0);
}

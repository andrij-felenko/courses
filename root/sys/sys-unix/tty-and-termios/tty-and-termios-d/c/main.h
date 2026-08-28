int fd = open("/dev/ttyUSB0", O_RDWR | O_NOCTTY | O_NONBLOCK);  /* не чекати несучої */
if (fd < 0)
    return -1;

struct termios tio;
if (tcgetattr(fd, &tio) < 0)          /* прочитали, як є */
    return -1;

cfmakeraw(&tio);                      /* зняли ICANON, ECHO, ISIG, перетворення */
cfsetispeed(&tio, B115200);
cfsetospeed(&tio, B115200);
tio.c_cflag |= CLOCAL | CREAD;        /* модемних ліній тут немає */
tio.c_cflag &= ~CRTSCTS;              /* апаратного керування потоком теж */
tio.c_cc[VMIN]  = 1;                  /* повернутися, щойно прийде байт; */
tio.c_cc[VTIME] = 1;                  /* таймер стартує лише з першим із них */

if (tcsetattr(fd, TCSAFLUSH, &tio) < 0)
    return -1;

/* CLOCAL уже в силі — тепер блокуючий read() може чесно спати */
fcntl(fd, F_SETFL, fcntl(fd, F_GETFL) & ~O_NONBLOCK);

struct termios check;                 /* tcsetattr каже «успіх», */
tcgetattr(fd, &check);                /* якщо застосував ХОЧ ЩОСЬ */
if ((check.c_cflag & (CSIZE | PARENB | CSTOPB | CRTSCTS))
        != (tio.c_cflag & (CSIZE | PARENB | CSTOPB | CRTSCTS))
    || check.c_lflag != tio.c_lflag
    || cfgetospeed(&check) != cfgetospeed(&tio))
    return -1;                        /* драйвер узяв не все — це помилка */

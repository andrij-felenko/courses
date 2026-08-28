struct termios want, got;
if (tcgetattr(fd, &want) < 0) return -1;
/* … правимо потрібні біти в want … */
if (tcsetattr(fd, TCSAFLUSH, &want) < 0) return -1;

if (tcgetattr(fd, &got) < 0) return -1;
if ((got.c_cflag & (CSIZE | PARENB | CSTOPB | CRTSCTS))
        != (want.c_cflag & (CSIZE | PARENB | CSTOPB | CRTSCTS))
    || cfgetospeed(&got) != cfgetospeed(&want)
    || got.c_lflag != want.c_lflag) {
    errno = EINVAL;              /* драйвер узяв не все */
    return -1;
}

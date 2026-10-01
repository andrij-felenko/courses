#if defined(_WIN32)
#include <windows.h>

void ch340_enter_bootloader(HANDLE hComm) {
    // Утримання GPIO0 у низькому рівні (RTS) та формування імпульсу RESET (DTR)
    EscapeCommFunction(hComm, SETRTS);
    EscapeCommFunction(hComm, SETDTR);
    Sleep(100);
    EscapeCommFunction(hComm, CLRDTR);
    Sleep(50);
    EscapeCommFunction(hComm, CLRRTS);
}
#else
#include <sys/ioctl.h>
#include <unistd.h>

void ch340_enter_bootloader(int fd) {
    int rts_mask = TIOCM_RTS;
    int dtr_mask = TIOCM_DTR;

    // Встановлення RTS та DTR для переведення мікроконтролера у режим прошивки
    ioctl(fd, TIOCMBIS, &rts_mask);
    ioctl(fd, TIOCMBIS, &dtr_mask);
    usleep(100000);
    ioctl(fd, TIOCMBIC, &dtr_mask);
    usleep(50000);
    ioctl(fd, TIOCMBIC, &rts_mask);
}
#endif

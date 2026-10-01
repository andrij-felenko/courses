#if defined(_WIN32)
#include <windows.h>
#include <chrono>
#include <thread>

void ch340EnterBootloader(HANDLE hComm) {
    // Апаратне скидання мікроконтролера з фіксацією режиму bootloader
    EscapeCommFunction(hComm, SETRTS);
    EscapeCommFunction(hComm, SETDTR);
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    EscapeCommFunction(hComm, CLRDTR);
    std::this_thread::sleep_for(std::chrono::milliseconds(50));
    EscapeCommFunction(hComm, CLRRTS);
}
#else
#include <sys/ioctl.h>
#include <termios.h>
#include <chrono>
#include <thread>

void ch340EnterBootloader(int fd) {
    int rtsMask = TIOCM_RTS;
    int dtrMask = TIOCM_DTR;

    // Перемикання прапорів TIOCMBIS та TIOCMBIC через ioctl
    ioctl(fd, TIOCMBIS, &rtsMask);
    ioctl(fd, TIOCMBIS, &dtrMask);
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    ioctl(fd, TIOCMBIC, &dtrMask);
    std::this_thread::sleep_for(std::chrono::milliseconds(50));
    ioctl(fd, TIOCMBIC, &rtsMask);
}
#endif

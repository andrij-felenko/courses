#include <windows.h>
#include <stdio.h>

HANDLE open_ch340_port_win32(const char *port_name) {
    HANDLE hComm = CreateFileA(
        port_name,
        GENERIC_READ | GENERIC_WRITE,
        0,
        NULL,
        OPEN_EXISTING,
        0,
        NULL
    );

    if (hComm == INVALID_HANDLE_VALUE) {
        perror("Помилка відкриття Virtual COM Port CH340 у Windows");
        return INVALID_HANDLE_VALUE;
    }

    COMMTIMEOUTS timeouts = {0};
    timeouts.ReadIntervalTimeout = 50;
    timeouts.ReadTotalTimeoutConstant = 1000;
    timeouts.ReadTotalTimeoutMultiplier = 10;
    timeouts.WriteTotalTimeoutConstant = 1000;
    timeouts.WriteTotalTimeoutMultiplier = 10;

    if (!SetCommTimeouts(hComm, &timeouts)) {
        CloseHandle(hComm);
        return INVALID_HANDLE_VALUE;
    }

    return hComm;
}

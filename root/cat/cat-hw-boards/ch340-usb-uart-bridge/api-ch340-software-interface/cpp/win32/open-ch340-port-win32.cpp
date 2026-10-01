#include <windows.h>
#include <system_error>
#include <string>

HANDLE open_ch340_port_win32(const std::string &port_name) {
    HANDLE hComm = ::CreateFileA(
        port_name.c_str(),
        GENERIC_READ | GENERIC_WRITE,
        0,
        nullptr,
        OPEN_EXISTING,
        0,
        nullptr
    );

    if (hComm == INVALID_HANDLE_VALUE) {
        throw std::system_error(
            static_cast<int>(::GetLastError()),
            std::system_category(),
            "Не вдалося відкрити Virtual COM Port CH340 у Windows"
        );
    }

    COMMTIMEOUTS timeouts{};
    timeouts.ReadIntervalTimeout = 50;
    timeouts.ReadTotalTimeoutConstant = 1000;
    timeouts.ReadTotalTimeoutMultiplier = 10;
    timeouts.WriteTotalTimeoutConstant = 1000;
    timeouts.WriteTotalTimeoutMultiplier = 10;

    if (!::SetCommTimeouts(hComm, &timeouts)) {
        ::CloseHandle(hComm);
        throw std::system_error(
            static_cast<int>(::GetLastError()),
            std::system_category(),
            "Не вдалося налаштувати таймаути порту CH340"
        );
    }

    return hComm;
}

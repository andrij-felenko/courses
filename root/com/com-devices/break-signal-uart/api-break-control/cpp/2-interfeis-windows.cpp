// Керування послідовним портом через Win32 API на мові C++
#include <windows.h>
#include <stdexcept>
#include <chrono>
#include <thread>

class Win32SerialBreak {
public:
    static void send_break(HANDLE handle, std::chrono::milliseconds duration) {
        if (!::SetCommBreak(handle)) {
            throw std::runtime_error("SetCommBreak failed");
        }
        std::this_thread::sleep_for(duration);
        if (!::ClearCommBreak(handle)) {
            throw std::runtime_error("ClearCommBreak failed");
        }
    }
};

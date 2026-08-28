#include <windows.h>
#include <system_error>

void flush_windows_handle(HANDLE handle) {
    if (!::FlushFileBuffers(handle)) {
        throw std::system_error(static_cast<int>(::GetLastError()),
                                std::system_category(),
                                "FlushFileBuffers failed");
    }
}

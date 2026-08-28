#ifdef _WIN32
#include <windows.h>

// Трейт для дескрипторів файлів Windows
struct Win32FileHandleTraits {
    using HandleType = HANDLE;
    static HandleType invalid() noexcept { return INVALID_HANDLE_VALUE; }
    static void close(HandleType h) noexcept {
        if (h != INVALID_HANDLE_VALUE && h != NULL) {
            ::CloseHandle(h);
        }
    }
};

using UniqueWin32File = UniqueHandle<Win32FileHandleTraits>;
#endif

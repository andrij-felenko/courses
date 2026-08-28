#ifdef _WIN32
#include <windows.h>

typedef struct {
    HANDLE handle;
} UniqueWin32FileC;

static inline void win32_close(UniqueWin32FileC* h) {
    if (h && h->handle != INVALID_HANDLE_VALUE && h->handle != NULL) {
        CloseHandle(h->handle);
        h->handle = INVALID_HANDLE_VALUE;
    }
}
#endif

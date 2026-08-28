#include <windows.h>

std::expected<HANDLE, DWORD> win32_create_file(const wchar_t* filename) {
    HANDLE h = CreateFileW(filename, GENERIC_READ, FILE_SHARE_READ, NULL, 
                           OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (h == INVALID_HANDLE_VALUE) {
        return std::unexpected(GetLastError());
    }
    return h;
}

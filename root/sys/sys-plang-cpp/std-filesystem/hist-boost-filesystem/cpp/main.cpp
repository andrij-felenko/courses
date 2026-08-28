// Win32 C++: Отримання розміру файлу та часу модифікації
#include <windows.h>
#include <iostream>

long long get_win32_file_size(const wchar_t* path) {
    WIN32_FILE_ATTRIBUTE_DATA data;
    if (GetFileAttributesExW(path, GetFileExInfoStandard, &data)) {
        LARGE_INTEGER size;
        size.HighPart = data.nFileSizeHigh;
        size.LowPart = data.nFileSizeLow;
        return size.QuadPart;
    }
    return -1;
}

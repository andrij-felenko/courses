// Win32 C++: Перевірка існування файлу та створення каталогу
#include <windows.h>

bool ensure_directory_win32(const wchar_t* path) {
    DWORD attr = GetFileAttributesW(path);
    if (attr == INVALID_FILE_ATTRIBUTES) {
        return CreateDirectoryW(path, NULL) != 0; // Win32 приймає структуру безпеки
    }
    return (attr & FILE_ATTRIBUTE_DIRECTORY) != 0;
}

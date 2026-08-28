/* win32_longpath.c — безпечне відкриття файлу за довгим шляхом у C */
#include <windows.h>
#include <stdio.h>
#include <wchar.h>

HANDLE open_file_extended(const wchar_t* path, DWORD access_mode) {
    wchar_t extended_buffer[32768];
    const wchar_t* final_path = path;

    /* Якщо шлях довгий (> 240) і ще не має префікса \\?\ — додаємо його */
    if (wcslen(path) > 240 && wcsncmp(path, L"\\\\?\\", 4) != 0) {
        /* Обробка мережевих UNC шляхів: \\server\share -> \\?\UNC\server\share */
        if (wcsncmp(path, L"\\\\", 2) == 0) {
            swprintf(extended_buffer, 32768, L"\\\\?\\UNC\\%ls", path + 2);
        } else {
            swprintf(extended_buffer, 32768, L"\\\\?\\%ls", path);
        }
        final_path = extended_buffer;
    }

    return CreateFileW(
        final_path,
        access_mode,
        FILE_SHARE_READ,
        NULL,
        OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL,
        NULL
    );
}

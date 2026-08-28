#include <windows.h>

/* 1. Відкриття файлу з контролем спільного доступу */
HANDLE create_file_writer(LPCWSTR path) {
    return CreateFileW(
        path,
        GENERIC_READ | GENERIC_WRITE,
        FILE_SHARE_READ,                 /* Заборона іншим процесам писати у файл */
        NULL,
        CREATE_ALWAYS,
        FILE_ATTRIBUTE_NORMAL,
        NULL
    );
}

/* 2. Скидання системного буфера на фізичний диск */
BOOL sync_windows_buffers(HANDLE hFile) {
    return FlushFileBuffers(hFile);
}

/* 3. Атомарна заміна цільового файлу */
BOOL replace_file_atomic(LPCWSTR target_path, LPCWSTR temp_path) {
    return ReplaceFileW(
        target_path,
        temp_path,
        NULL,
        REPLACEFILE_IGNORE_MERGE_ERRORS,
        NULL,
        NULL
    );
}

/* 4. Ексклюзивне блокування діапазону байтів */
BOOL lock_windows_file(HANDLE hFile) {
    OVERLAPPED ov = {0};
    return LockFileEx(
        hFile,
        LOCKFILE_EXCLUSIVE_LOCK | LOCKFILE_FAIL_IMMEDIATELY,
        0,
        MAXDWORD,
        MAXDWORD,
        &ov
    );
}

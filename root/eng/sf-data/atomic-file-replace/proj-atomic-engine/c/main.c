#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <stdint.h>

#if defined(_WIN32)
#include <windows.h>
#include <io.h>
#else
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <libgen.h>
#endif

// Результат виконання операції: 0 — успіх, ненульове — код помилки
int atomic_write_file(const char *target_path, const void *data, size_t size) {
    if (!target_path || (!data && size > 0)) {
        return EINVAL;
    }

#if defined(_WIN32)
    // --- Реалізація для Windows ---
    wchar_t w_target[MAX_PATH];
    wchar_t w_temp[MAX_PATH];
    wchar_t w_dir[MAX_PATH];

    if (MultiByteToWideChar(CP_UTF8, 0, target_path, -1, w_target, MAX_PATH) == 0) {
        return (int)GetLastError();
    }

    // Виділяємо каталог цільового файлу
    wcscpy_s(w_dir, MAX_PATH, w_target);
    wchar_t *last_slash = wcsrchr(w_dir, L'\\');
    if (!last_slash) last_slash = wcsrchr(w_dir, L'/');
    if (last_slash) {
        *last_slash = L'\0';
    } else {
        wcscpy_s(w_dir, MAX_PATH, L".");
    }

    // Створюємо унікальний тимчасовий файл у тому ж каталозі
    if (GetTempFileNameW(w_dir, L"atm", 0, w_temp) == 0) {
        return (int)GetLastError();
    }

    HANDLE h_file = CreateFileW(w_temp, GENERIC_WRITE, 0, NULL, CREATE_ALWAYS,
                                FILE_ATTRIBUTE_NORMAL, NULL);
    if (h_file == INVALID_HANDLE_VALUE) {
        DWORD err = GetLastError();
        DeleteFileW(w_temp);
        return (int)err;
    }

    // Запис корисного навантаження
    DWORD bytes_written = 0;
    BOOL write_ok = WriteFile(h_file, data, (DWORD)size, &bytes_written, NULL);
    if (!write_ok || bytes_written != (DWORD)size) {
        DWORD err = GetLastError();
        CloseHandle(h_file);
        DeleteFileW(w_temp);
        return (int)(err ? err : ERROR_WRITE_FAULT);
    }

    // Примусове виштовхування буферів на диск
    if (!FlushFileBuffers(h_file)) {
        DWORD err = GetLastError();
        CloseHandle(h_file);
        DeleteFileW(w_temp);
        return (int)err;
    }
    CloseHandle(h_file);

    // Спроба атомарної заміни через ReplaceFileW (якщо файл уже існував)
    if (!ReplaceFileW(w_target, w_temp, NULL, REPLACEFILE_IGNORE_MERGE_ERRORS, NULL, NULL)) {
        DWORD err = GetLastError();
        // Якщо цільового файлу ще не існувало — використовуємо MoveFileExW
        if (err == ERROR_FILE_NOT_FOUND) {
            if (!MoveFileExW(w_temp, w_target, MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH)) {
                err = GetLastError();
                DeleteFileW(w_temp);
                return (int)err;
            }
        } else {
            DeleteFileW(w_temp);
            return (int)err;
        }
    }
    return 0;

#else
    // --- Реалізація для POSIX (Linux / macOS / BSD) ---
    mode_t target_mode = 0644;
    struct stat st;
    if (stat(target_path, &st) == 0) {
        target_mode = st.st_mode & 0777; // Зберігаємо вихідні права
    }

    // Формуємо шаблон тимчасового файлу поруч із цільовим
    char tmp_template[4096];
    int written = snprintf(tmp_template, sizeof(tmp_template), "%s.tmp_XXXXXX", target_path);
    if (written < 0 || (size_t)written >= sizeof(tmp_template)) {
        return ENAMETOOLONG;
    }

    // Створюємо безпечний тимчасовий файл
    int fd = mkstemp(tmp_template);
    if (fd < 0) {
        return errno;
    }

    // Встановлюємо збережені права доступу
    if (fchmod(fd, target_mode) != 0) {
        int err = errno;
        close(fd);
        unlink(tmp_template);
        return err;
    }

    // Записуємо всі байти з обробкою неповних записів та переривань
    const uint8_t *ptr = (const uint8_t *)data;
    size_t remaining = size;
    while (remaining > 0) {
        ssize_t n = write(fd, ptr, remaining);
        if (n < 0) {
            if (errno == EINTR) continue; // Переривання сигналом
            int err = errno;
            close(fd);
            unlink(tmp_template);
            return err;
        }
        ptr += n;
        remaining -= (size_t)n;
    }

    // Скидаємо брудні сторінки та інод на фізичний носій
    if (fsync(fd) != 0) {
        int err = errno;
        close(fd);
        unlink(tmp_template);
        return err;
    }

    if (close(fd) != 0) {
        int err = errno;
        unlink(tmp_template);
        return err;
    }

    // Атомарна підміна імені в просторі імен каталогу
    if (rename(tmp_template, target_path) != 0) {
        int err = errno;
        unlink(tmp_template);
        return err;
    }

    // Синхронізація запису батьківського каталогу
    char path_copy[4096];
    strncpy(path_copy, target_path, sizeof(path_copy) - 1);
    path_copy[sizeof(path_copy) - 1] = '\0';
    char *dir_name = dirname(path_copy);

    int dir_fd = open(dir_name, O_RDONLY | O_DIRECTORY);
    if (dir_fd >= 0) {
        fsync(dir_fd); // Помилку каталогу фіксуємо, але не відкочуємо файл
        close(dir_fd);
    }

    return 0;
#endif
}

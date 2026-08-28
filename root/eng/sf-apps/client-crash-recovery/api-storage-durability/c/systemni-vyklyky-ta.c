#include <fcntl.h>
#include <unistd.h>
#include <sys/file.h>
#include <stdio.h>
#include <errno.h>

#if defined(__APPLE__)
#include <sys/fcntl.h>
#endif

/* 1. Створення унікального тимчасового файлу в тому ж каталозі */
int open_temporary_atomic(const char *path) {
    return open(path, O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC, 0644);
}

/* 2. Примусове скидання брудних сторінок сторінкового кешу на фізичний диск */
int sync_file_to_disk(int fd) {
#if defined(__APPLE__)
    /* На macOS звичайний fsync скидає лише в кеш накопичувача, F_FULLFSYNC — у флешкомірки */
    return fcntl(fd, F_FULLFSYNC);
#else
    return fsync(fd);
#endif
}

/* 3. Атомарна підміна запису в таблиці каталогу */
int atomic_replace_file(const char *temp_path, const char *target_path) {
    return rename(temp_path, target_path);
}

/* 4. Ексклюзивне блокування файлу від інших процесів */
int acquire_file_lease(int fd) {
    return flock(fd, LOCK_EX | LOCK_NB);
}

#include <fcntl.h>
#include <unistd.h>

// Записати й дочекатися, поки дані справді підуть на носій.
bool store(const char* path, const uint8_t* d, size_t n) {
    int fd = ::open(path, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) return false;
    for (size_t off = 0; off < n; ) {
        ssize_t w = ::write(fd, d + off, n - off);
        if (w <= 0) { ::close(fd); return false; }
        off += size_t(w);
    }
    bool ok = (::fsync(fd) == 0);       // без цього дані ще в кеші сторінок
    return (::close(fd) == 0) && ok;
}

// Геш ІЗ ФАЙЛА, а не з буфера, що лишився в пам'яті.
uint64_t hash_stored(const char* path) {
    int fd = ::open(path, O_RDONLY);
    if (fd < 0) return 0;
    ::posix_fadvise(fd, 0, 0, POSIX_FADV_DONTNEED);   // спробувати викинути кеш
    Fnv1a h;
    std::vector<uint8_t> buf(1 << 16);
    for (;;) {
        ssize_t got = ::read(fd, buf.data(), buf.size());
        if (got <= 0) break;
        h.feed(buf.data(), size_t(got));
    }
    ::close(fd);
    return h.h;
}

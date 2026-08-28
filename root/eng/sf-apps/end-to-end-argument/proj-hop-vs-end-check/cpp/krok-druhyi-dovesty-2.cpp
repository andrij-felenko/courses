// Модель тихого псування на носії.
bool rot(const char* path, off_t a, off_t b) {
    int fd = ::open(path, O_RDWR);
    if (fd < 0) return false;
    uint8_t x = 0, y = 0;
    ::pread(fd, &x, 1, a);
    ::pread(fd, &y, 1, b);
    ::pwrite(fd, &y, 1, a);
    ::pwrite(fd, &x, 1, b);
    ::fsync(fd);
    ::close(fd);
    return true;
}

class DualDevice {
    int fd1_;
    int fd2_;
public:
    DualDevice() {
        fd1_ = ::open("/dev/dev1", O_RDWR); // Успішно відкрито
        fd2_ = ::open("/dev/dev2", O_RDWR); // Помилка! Викидаємо виняток
        if (fd2_ < 0) throw std::runtime_error("Device 2 failed");
    }

    ~DualDevice() {
        if (fd1_ >= 0) ::close(fd1_);
        if (fd2_ >= 0) ::close(fd2_);
    }
};

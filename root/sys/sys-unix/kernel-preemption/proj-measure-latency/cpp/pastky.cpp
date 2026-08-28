// RAII-обгортка для керування станами сну в C++
class DmaLatencyGuard {
    int fd_ = -1;
public:
    explicit DmaLatencyGuard(std::int32_t target_us = 0) {
        fd_ = ::open("/dev/cpu_dma_latency", O_RDWR);
        if (fd_ >= 0) {
            ::write(fd_, &target_us, sizeof(target_us));
        }
    }
    ~DmaLatencyGuard() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }
    DmaLatencyGuard(const DmaLatencyGuard&) = delete;
    DmaLatencyGuard& operator=(const DmaLatencyGuard&) = delete;
};

// Використання:
{
    DmaLatencyGuard latency_guard(0); // заборона глибокого сну на час життя об'єкта
    // …увесь вимір…
} // об'єкт знищується, дескриптор автоматично закривається

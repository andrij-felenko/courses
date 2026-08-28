// RAII блокування переходів CPU в C-states
class CpuDmaLatencyLock {
public:
    explicit CpuDmaLatencyLock(int32_t latency_us = 0) {
        fd_ = ::open("/dev/cpu_dma_latency", O_RDWR | O_CLOEXEC);
        if (fd_ >= 0) {
            ::write(fd_, &latency_us, sizeof(latency_us));
        }
    }
    ~CpuDmaLatencyLock() {
        if (fd_ >= 0) ::close(fd_);
    }
private:
    int fd_{-1};
};

namespace driver {

struct TaskNotifier {
    void* task_handle;
    void notify_from_isr(Status status) const noexcept;
    [[nodiscard]] Status wait(uint32_t timeout_ms) const noexcept;
};

// RAII блокування м'ютекса шини
class BusLock {
public:
    explicit BusLock(void* mutex) noexcept : mutex_(mutex) {
        // xSemaphoreTake(mutex_, portMAX_DELAY);
    }
    ~BusLock() noexcept {
        // xSemaphoreGive(mutex_);
    }
    BusLock(const BusLock&) = delete;
    BusLock& operator=(const BusLock&) = delete;

private:
    void* mutex_;
};

} // namespace driver

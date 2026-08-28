template<ptrdiff_t MaxVal>
class SemaphoreGuard {
public:
    explicit SemaphoreGuard(std::counting_semaphore<MaxVal>& sem)
        : sem_(sem), acquired_(true) {
        sem_.acquire();
    }
    ~SemaphoreGuard() {
        if (acquired_) sem_.release();
    }
    SemaphoreGuard(const SemaphoreGuard&) = delete;
    SemaphoreGuard& operator=(const SemaphoreGuard&) = delete;
private:
    std::counting_semaphore<MaxVal>& sem_;
    bool acquired_;
};

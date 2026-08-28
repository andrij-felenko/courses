namespace driver {

class CriticalSectionGuard {
public:
    CriticalSectionGuard() noexcept : primask_(__get_PRIMASK()) {
        __disable_irq();
    }
    ~CriticalSectionGuard() noexcept {
        __set_PRIMASK(primask_);
    }
    CriticalSectionGuard(const CriticalSectionGuard&) = delete;
    CriticalSectionGuard& operator=(const CriticalSectionGuard&) = delete;

private:
    uint32_t primask_;
};

} // namespace driver

namespace rtos {

/* C++ RAII вартовий для гарантованого перемикання контексту */
class ScopedIsrYield {
public:
    ScopedIsrYield() noexcept : woken_(pdFALSE) {}
    ~ScopedIsrYield() noexcept {
        portYIELD_FROM_ISR(woken_);
    }

    [[nodiscard]] BaseType_t* flag() noexcept { return &woken_; }
    [[nodiscard]] bool is_woken() const noexcept { return woken_ == pdTRUE; }

private:
    BaseType_t woken_;
};

} // namespace rtos

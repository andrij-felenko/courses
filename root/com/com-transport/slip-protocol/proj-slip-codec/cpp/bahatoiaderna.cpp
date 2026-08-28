// C++ RAII обгортка критичної секції ESP-IDF
class EspSpinLock {
public:
    EspSpinLock() noexcept { portENTER_CRITICAL(&mux_); }
    ~EspSpinLock() noexcept { portEXIT_CRITICAL(&mux_); }
    EspSpinLock(const EspSpinLock &) = delete;
    EspSpinLock &operator=(const EspSpinLock &) = delete;

private:
    static inline portMUX_TYPE mux_ = portMUX_INITIALIZER_UNLOCKED;
};

void safe_slip_feed(SlipDecoder &decoder, uint8_t byte) {
    EspSpinLock lock;
    decoder.feed(byte);
}

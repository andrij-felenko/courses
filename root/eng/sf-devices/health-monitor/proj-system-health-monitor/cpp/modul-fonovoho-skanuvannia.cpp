namespace Health {

class FlashScrubber {
public:
    constexpr FlashScrubber(uintptr_t start_addr, uintptr_t end_addr) noexcept
        : start_address_(start_addr), end_address_(end_addr), current_address_(start_addr) {}

    void step(size_t words_to_read) noexcept {
        if (start_address_ >= end_address_) return;

        auto ptr = reinterpret_cast<volatile const uint32_t*>(current_address_);
        for (size_t i = 0; i < words_to_read; ++i) {
            volatile uint32_t dummy = *ptr++;
            (void)dummy;

            current_address_ += sizeof(uint32_t);
            if (current_address_ >= end_address_) {
                current_address_ = start_address_;
                break;
            }
        }
    }

    [[nodiscard]] uintptr_t current_address() const noexcept { return current_address_; }

private:
    uintptr_t start_address_{0};
    uintptr_t end_address_{0};
    uintptr_t current_address_{0};
};

} // namespace Health

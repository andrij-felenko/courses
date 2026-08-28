// C++20: Безпечне оновлення бітового поля за допомогою constexpr масок
template <BusTransport Transport>
Status AccelerometerDriver<Transport>::setOdr(std::uint8_t odr_code) noexcept {
    if (!is_initialized_) return Status::NotInit;

    constexpr std::uint8_t OdrMask = 0xF0U;
    constexpr std::uint8_t OdrShift = 4U;

    const auto new_val = static_cast<std::uint8_t>(
        (shadow_ctrl1_ & ~OdrMask) | ((odr_code << OdrShift) & OdrMask)
    );

    std::array<const std::uint8_t, 1> tx{new_val};
    if (auto res = transport_.write(RegCtrl1, tx); res != Status::Ok) {
        return res;
    }

    shadow_ctrl1_ = new_val;
    return Status::Ok;
}

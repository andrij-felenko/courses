// C++20: Опитування готовності з детермінованим тайм-аутом
template <BusTransport Transport>
Status AccelerometerDriver<Transport>::waitDataReady(std::uint32_t timeout_ms) noexcept {
    std::uint32_t elapsed = 0;
    constexpr std::uint32_t PollIntervalMs = 1;

    while (elapsed < timeout_ms) {
        std::array<std::uint8_t, 1> status{0};
        if (transport_.read(RegStatus, status) == Status::Ok) {
            if ((status[0] & 0x08U) != 0) {
                return Status::Ok;
            }
        }
        transport_.delay_ms(PollIntervalMs);
        elapsed += PollIntervalMs;
    }
    return Status::Timeout;
}

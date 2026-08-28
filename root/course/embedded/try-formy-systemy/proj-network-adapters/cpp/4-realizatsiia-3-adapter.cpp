class P2PLinkAdapter final : public INetAdapter {
public:
    static constexpr uint32_t FailSafeTimeoutMs = 1500;

    P2PLinkAdapter() = default;

    bool init() noexcept override {
        state_ = NetState::Connecting;
        last_rx_timestamp_ms_ = 0;
        tx_sequence_ = 0;
        rx_sequence_ = 0;
        packets_lost_ = 0;
        failsafe_triggered_ = false;
        return true;
    }

    void poll(uint32_t now_ms) noexcept override {
        if (state_ == NetState::Online) {
            if (now_ms - last_rx_timestamp_ms_ >= FailSafeTimeoutMs) {
                state_ = NetState::Error;
                failsafe_triggered_ = true;
                // Сповіщення підсистеми польотного контролера
            }
        }
    }

    std::expected<void, NetError> send(const NetPacket& pkt) noexcept override {
        tx_sequence_++;
        // Пряме відправлення кадру через радіотрансивер
        return {};
    }

    void on_raw_frame_received(std::span<const uint8_t> frame, uint16_t seq, uint32_t now_ms) noexcept {
        last_rx_timestamp_ms_ = now_ms;
        state_ = NetState::Online;
        failsafe_triggered_ = false;

        if (seq > rx_sequence_ + 1) {
            packets_lost_ += (seq - rx_sequence_ - 1);
        }
        rx_sequence_ = seq;

        if (rx_callback_ && frame.size() >= 2) {
            NetPacket pkt{};
            pkt.msg_id = static_cast<uint16_t>((frame[0] << 8) | frame[1]);
            pkt.len = static_cast<uint8_t>(std::min(frame.size(), size_t{64}));
            std::copy_n(frame.data(), pkt.len, pkt.payload.begin());
            pkt.priority = NetPriority::Critical;
            rx_callback_(pkt);
        }
    }

    [[nodiscard]] NetState state() const noexcept override {
        return state_;
    }

    [[nodiscard]] bool is_failsafe_active() const noexcept {
        return failsafe_triggered_;
    }

    [[nodiscard]] uint32_t lost_packets_count() const noexcept {
        return packets_lost_;
    }

    void set_rx_callback(RxCallback cb) noexcept override {
        rx_callback_ = std::move(cb);
    }

private:
    NetState state_{NetState::Offline};
    uint32_t last_rx_timestamp_ms_{0};
    uint16_t tx_sequence_{0};
    uint16_t rx_sequence_{0};
    uint32_t packets_lost_{0};
    bool failsafe_triggered_{false};
    RxCallback rx_callback_{};
};

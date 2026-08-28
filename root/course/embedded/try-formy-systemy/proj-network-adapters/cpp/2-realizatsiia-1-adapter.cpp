class HomeNodeAdapter final : public INetAdapter {
public:
    HomeNodeAdapter() = default;

    bool init() noexcept override {
        state_ = NetState::Online;
        last_heartbeat_ms_ = 0;
        return true;
    }

    void poll(uint32_t now_ms) noexcept override {
        if (now_ms - last_heartbeat_ms_ >= 30'000) {
            last_heartbeat_ms_ = now_ms;
            NetPacket hb{};
            hb.msg_id = 0x0001; // ID: Node Heartbeat
            hb.payload[0] = 0x01; // Status OK
            hb.len = 1;
            hb.priority = NetPriority::Low;
            (void)send(hb);
        }
    }

    std::expected<void, NetError> send(const NetPacket& pkt) noexcept override {
        if (state_ != NetState::Online) {
            return std::unexpected(NetError::LinkDown);
        }
        // Пряма відправка кадру через локальний радіотрансивер
        return {};
    }

    NetState state() const noexcept override {
        return state_;
    }

    void set_rx_callback(RxCallback cb) noexcept override {
        rx_callback_ = std::move(cb);
    }

    void on_raw_frame_received(const NetPacket& pkt) noexcept {
        if (rx_callback_) {
            rx_callback_(pkt);
        }
    }

private:
    NetState state_{NetState::Offline};
    uint32_t last_heartbeat_ms_{0};
    RxCallback rx_callback_{};
};

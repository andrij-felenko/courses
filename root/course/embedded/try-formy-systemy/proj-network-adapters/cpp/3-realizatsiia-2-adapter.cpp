struct TrackerRecord {
    uint32_t timestamp{0};
    int32_t  lat_e7{0};
    int32_t  lon_e7{0};
    uint8_t  battery_pct{0};
};

class FleetTrackerAdapter final : public INetAdapter {
public:
    static constexpr size_t BufferCapacity = 32;

    FleetTrackerAdapter() = default;

    bool init() noexcept override {
        state_ = NetState::Sleeping;
        fsm_ = FsmState::Sleeping;
        head_ = 0;
        tail_ = 0;
        count_ = 0;
        timer_ms_ = 0;
        return true;
    }

    void poll(uint32_t now_ms) noexcept override {
        switch (fsm_) {
        case FsmState::Sleeping:
            if (count_ >= 5 || (now_ms - timer_ms_ >= 3'600'000 && count_ > 0)) {
                fsm_ = FsmState::PowerUpModem;
                timer_ms_ = now_ms;
                state_ = NetState::Connecting;
            }
            break;

        case FsmState::PowerUpModem:
            if (now_ms - timer_ms_ >= 500) {
                fsm_ = FsmState::Registering;
                timer_ms_ = now_ms;
            }
            break;

        case FsmState::Registering:
            if (now_ms - timer_ms_ >= 4'000) {
                fsm_ = FsmState::TransmittingBatch;
                state_ = NetState::Online;
            }
            break;

        case FsmState::TransmittingBatch:
            // Пакетне вивантаження точок через CoAP/UDP
            count_ = 0;
            tail_ = head_;
            fsm_ = FsmState::ShutdownModem;
            timer_ms_ = now_ms;
            break;

        case FsmState::ShutdownModem:
            state_ = NetState::Sleeping;
            fsm_ = FsmState::Sleeping;
            break;
        }
    }

    std::expected<void, NetError> send(const NetPacket& pkt) noexcept override {
        if (pkt.len < sizeof(TrackerRecord)) {
            return std::unexpected(NetError::InvalidPayload);
        }
        TrackerRecord rec;
        std::memcpy(&rec, pkt.payload.data(), sizeof(TrackerRecord));

        if (count_ >= BufferCapacity) {
            tail_ = (tail_ + 1) % BufferCapacity;
            count_--;
        }
        buffer_[head_] = rec;
        head_ = (head_ + 1) % BufferCapacity;
        count_++;
        return {};
    }

    NetState state() const noexcept override {
        return state_;
    }

    void set_rx_callback(RxCallback cb) noexcept override {
        rx_callback_ = std::move(cb);
    }

private:
    enum class FsmState {
        Sleeping,
        PowerUpModem,
        Registering,
        TransmittingBatch,
        ShutdownModem
    };

    NetState state_{NetState::Sleeping};
    FsmState fsm_{FsmState::Sleeping};
    std::array<TrackerRecord, BufferCapacity> buffer_{};
    size_t head_{0};
    size_t tail_{0};
    size_t count_{0};
    uint32_t timer_ms_{0};
    RxCallback rx_callback_{};
};

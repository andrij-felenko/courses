#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <optional>
#include <expected>
#include <functional>

enum class CorrStatus : uint8_t {
    Ok = 0,
    Timeout,
    RemoteError,
    Busy,
    InvalidArg
};

struct Response {
    uint16_t trans_id{0};
    CorrStatus status{CorrStatus::Ok};
    std::span<const uint8_t> payload{};
};

using ResponseCallback = std::function<void(const Response&)>;

template <size_t MaxPending = 8>
class AsyncCorrelator {
public:
    constexpr AsyncCorrelator() = default;

    // Реєстрація запиту з неблокуючим зворотним викликом
    std::expected<uint16_t, CorrStatus> registerRequest(
        uint32_t timeout_ms,
        ResponseCallback callback) 
    {
        if (!callback || timeout_ms == 0) {
            return std::unexpected(CorrStatus::InvalidArg);
        }

        for (auto& slot : slots_) {
            if (!slot.is_active) {
                uint16_t id = generateUniqueId();
                if (id == 0) {
                    return std::unexpected(CorrStatus::Busy);
                }

                slot.is_active = true;
                slot.trans_id = id;
                slot.timeout_remaining_ms = timeout_ms;
                slot.callback = std::move(callback);

                return id;
            }
        }
        return std::unexpected(CorrStatus::Busy);
    }

    // Маршрутизація вхідної відповіді
    bool dispatchResponse(uint16_t trans_id, CorrStatus status, std::span<const uint8_t> payload) {
        if (trans_id == 0) return false;

        for (auto& slot : slots_) {
            if (slot.is_active && slot.trans_id == trans_id) {
                Response resp{trans_id, status, payload};
                auto cb = std::move(slot.callback);
                slot.is_active = false;

                if (cb) {
                    cb(resp);
                }
                return true;
            }
        }
        return false;
    }

    // Періодичне обслуговування таймерів дедлайнів
    void tick(uint32_t elapsed_ms) {
        if (elapsed_ms == 0) return;

        for (auto& slot : slots_) {
            if (slot.is_active) {
                if (slot.timeout_remaining_ms <= elapsed_ms) {
                    Response timeout_resp{slot.trans_id, CorrStatus::Timeout, {}};
                    auto cb = std::move(slot.callback);
                    slot.is_active = false;

                    if (cb) {
                        cb(timeout_resp);
                    }
                } else {
                    slot.timeout_remaining_ms -= elapsed_ms;
                }
            }
        }
    }

private:
    uint16_t generateUniqueId() {
        for (size_t attempt = 0; attempt < 65535; ++attempt) {
            uint16_t candidate = next_id_++;
            if (next_id_ == 0) next_id_ = 1;

            bool in_use = false;
            for (const auto& slot : slots_) {
                if (slot.is_active && slot.trans_id == candidate) {
                    in_use = true;
                    break;
                }
            }

            if (!in_use) {
                return candidate;
            }
        }
        return 0;
    }

    struct Slot {
        bool is_active{false};
        uint16_t trans_id{0};
        uint32_t timeout_remaining_ms{0};
        ResponseCallback callback{};
    };

    std::array<Slot, MaxPending> slots_{};
    uint16_t next_id_{1};
};

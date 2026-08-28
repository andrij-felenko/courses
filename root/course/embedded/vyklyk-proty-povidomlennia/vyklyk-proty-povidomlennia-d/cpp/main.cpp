#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <optional>
#include <expected>
#include <functional>

enum class RpcStatus : uint8_t {
    Success = 0,
    Timeout,
    RemoteError,
    NoFreeSlots
};

struct RpcResult {
    uint16_t trans_id{0};
    RpcStatus status{RpcStatus::Success};
    std::span<const uint8_t> payload{};
};

using RpcCompletionHandler = std::function<void(const RpcResult&)>;

template <size_t MaxPending = 4>
class AsyncRpcCorrelator {
public:
    AsyncRpcCorrelator() = default;

    // Реєстрація неблокуючого виклику
    std::expected<uint16_t, RpcStatus> sendRequestAsync(
        uint32_t timeout_ms,
        RpcCompletionHandler handler) 
    {
        if (!handler) {
            return std::unexpected(RpcStatus::RemoteError);
        }

        for (auto& slot : pool_) {
            if (!slot.active) {
                uint16_t tid = next_id_++;
                if (next_id_ == 0) next_id_ = 1;

                slot.active = true;
                slot.trans_id = tid;
                slot.timeout_ms = timeout_ms;
                slot.handler = std::move(handler);

                return tid;
            }
        }
        return std::unexpected(RpcStatus::NoFreeSlots);
    }

    // Обробка вхідного пакету відповіді
    void onResponseReceived(uint16_t trans_id, std::span<const uint8_t> payload) {
        if (trans_id == 0) return;

        for (auto& slot : pool_) {
            if (slot.active && slot.trans_id == trans_id) {
                RpcResult result{trans_id, RpcStatus::Success, payload};
                auto cb = std::move(slot.handler);
                slot.active = false;

                if (cb) {
                    cb(result);
                }
                return;
            }
        }
    }

    // Обслуговування таймаутів
    void pollTimeouts(uint32_t elapsed_ms) {
        for (auto& slot : pool_) {
            if (slot.active) {
                if (slot.timeout_ms <= elapsed_ms) {
                    RpcResult timeout_res{slot.trans_id, RpcStatus::Timeout, {}};
                    auto cb = std::move(slot.handler);
                    slot.active = false;

                    if (cb) {
                        cb(timeout_res);
                    }
                } else {
                    slot.timeout_ms -= elapsed_ms;
                }
            }
        }
    }

private:
    struct PendingSlot {
        bool active{false};
        uint16_t trans_id{0};
        uint32_t timeout_ms{0};
        RpcCompletionHandler handler{};
    };

    std::array<PendingSlot, MaxPending> pool_{};
    uint16_t next_id_{1};
};

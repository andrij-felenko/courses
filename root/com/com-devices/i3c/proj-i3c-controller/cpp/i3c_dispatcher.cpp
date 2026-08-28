// i3c_dispatcher.cpp - Обробка подій та реєстрація переривань цілей на C++20
#include "i3c_controller.hpp"
#include <iostream>
#include <functional>
#include <unordered_map>

namespace mipi::i3c {

using IbiCallback = std::function<void(uint8_t dynamic_addr, uint8_t mdb)>;

class IbiEventDispatcher {
public:
    explicit IbiEventDispatcher(BusController& bus) noexcept : bus_(bus) {}

    void register_handler(uint8_t dynamic_address, IbiCallback callback) {
        callbacks_[dynamic_address] = std::move(callback);
    }

    [[nodiscard]] std::expected<void, Status> process_pending_ibi() noexcept {
        uint8_t winning_addr = 0;
        uint8_t mdb_value = 0;

        // Виклик низькорівневого захоплення IBI на шині
        if (auto res = capture_ibi_event(winning_addr, mdb_value); !res) {
            return std::unexpected(res.error());
        }

        if (auto it = callbacks_.find(winning_addr); it != callbacks_.end()) {
            it->second(winning_addr, mdb_value);
        }

        return {};
    }

private:
    [[nodiscard]] std::expected<void, Status> capture_ibi_event(
        uint8_t& out_addr, uint8_t& out_mdb) noexcept 
    {
        // Імітація захоплення апаратного переривання шини
        out_addr = 0x08;
        out_mdb = 0x01; // Data Ready флаг акселерометра
        return {};
    }

    BusController& bus_;
    std::unordered_map<uint8_t, IbiCallback> callbacks_;
};

} // namespace mipi::i3c

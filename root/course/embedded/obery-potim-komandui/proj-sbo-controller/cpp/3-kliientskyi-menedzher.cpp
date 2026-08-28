// gcs_focus_manager.hpp — C++20 менеджер вибору цілі для наземної станції
#include <string>
#include <string_view>
#include <chrono>
#include <optional>
#include <expected>

namespace gcs {

class FocusManager {
public:
    using TimePoint = std::chrono::steady_clock::time_point;

    void select_vehicle(sbo::NodeId id, std::string_view name) noexcept {
        focused_id_ = id;
        target_name_ = name;
        armed_ = false;
        token_ = sbo::Token{0};
    }

    void on_select_ack(sbo::NodeId from_id, sbo::Token token, std::chrono::milliseconds window, TimePoint now) noexcept {
        if (from_id == focused_id_) {
            armed_ = true;
            token_ = token;
            deadline_ = now + window;
        }
    }

    [[nodiscard]] std::optional<sbo::Packet> build_operate_packet(sbo::CommandCode cmd, TimePoint now) noexcept {
        if (!armed_ || now >= deadline_) {
            armed_ = false;
            return std::nullopt;
        }

        sbo::Packet pkt{};
        pkt.magic = 0x5B;
        pkt.type = sbo::MessageType::OperateReq;
        pkt.source = sbo::NodeId{0xFE};
        pkt.target = focused_id_;
        pkt.token = token_;
        pkt.command = cmd;

        armed_ = false; // Одноразовий клік
        return pkt;
    }

    [[nodiscard]] bool is_armed(TimePoint now) const noexcept {
        return armed_ && (now < deadline_);
    }

    [[nodiscard]] std::string_view target_name() const noexcept {
        return target_name_;
    }

    [[nodiscard]] sbo::NodeId target_id() const noexcept {
        return focused_id_;
    }

private:
    sbo::NodeId focused_id_{0};
    std::string target_name_{"NONE"};
    bool armed_{false};
    sbo::Token token_{0};
    TimePoint deadline_{};
};

} // namespace gcs

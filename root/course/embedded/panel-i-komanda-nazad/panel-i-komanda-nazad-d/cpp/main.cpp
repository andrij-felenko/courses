#include <array>
#include <cstdint>
#include <format>
#include <iostream>
#include <string>
#include <string_view>

enum class ActuatorState {
    Idle,
    Busy,
    Error
};

struct DedupEntry {
    std::string cmd_id;
    uint32_t seen_time_sec{0};
};

class DedupFilter {
public:
    static constexpr size_t Capacity = 16;

    [[nodiscard]] bool check(std::string_view cmd_id) const noexcept {
        for (size_t i = 0; i < count_; ++i) {
            if (records_[i].cmd_id == cmd_id) {
                return true;
            }
        }
        return false;
    }

    void insert(std::string_view cmd_id, uint32_t now_sec) {
        records_[head_] = DedupEntry{std::string(cmd_id), now_sec};
        head_ = (head_ + 1) % Capacity;
        if (count_ < Capacity) {
            ++count_;
        }
    }

private:
    std::array<DedupEntry, Capacity> records_{};
    size_t head_{0};
    size_t count_{0};
};

class ServoController {
public:
    void handleDownlink(std::string_view cmd_id, int target_pos,
                        uint32_t issued_at, uint16_t ttl_sec,
                        uint32_t now_sec, uint32_t now_ms) {
        if (now_sec > issued_at + ttl_sec) {
            sendExecStatus(cmd_id, "EXPIRED", 0, currentAngleDeg_, 104);
            return;
        }

        if (dedup_.check(cmd_id)) {
            sendAck(cmd_id, "ACK_DUPLICATE");
            sendExecStatus(cmd_id, "COMPLETED", 100, currentAngleDeg_, 0);
            return;
        }

        if (state_ == ActuatorState::Busy) {
            sendAck(cmd_id, "ACK_REJECTED");
            sendExecStatus(cmd_id, "FAILED", 0, currentAngleDeg_, 201);
            return;
        }

        dedup_.insert(cmd_id, now_sec);
        sendAck(cmd_id, "ACK_RECEIVED");

        activeCmdId_ = cmd_id;
        targetAngleDeg_ = target_pos;
        startTickMs_ = now_ms;
        state_ = ActuatorState::Busy;

        sendExecStatus(activeCmdId_, "STARTED", 0, currentAngleDeg_, 0);
    }

    void poll(uint32_t now_ms) {
        if (state_ != ActuatorState::Busy) {
            return;
        }

        uint32_t elapsed = now_ms - startTickMs_;
        if (elapsed >= DurationMs) {
            currentAngleDeg_ = targetAngleDeg_;
            state_ = ActuatorState::Idle;
            sendExecStatus(activeCmdId_, "COMPLETED", 100, currentAngleDeg_, 0);
        } else if (now_ms - lastReportMs_ >= 500) {
            lastReportMs_ = now_ms;
            int progress = static_cast<int>((elapsed * 100) / DurationMs);
            sendExecStatus(activeCmdId_, "IN_PROGRESS", progress, currentAngleDeg_, 0);
        }
    }

private:
    static constexpr uint32_t DurationMs = 2500;

    void sendAck(std::string_view cmd_id, std::string_view status) const {
        std::cout << std::format("--> [PUB devices/gate/cmd/ack] {{\"cmd_id\":\"{}\",\"status\":\"{}\"}}\n",
                                 cmd_id, status);
    }

    void sendExecStatus(std::string_view cmd_id, std::string_view state,
                        int progress, int pos, int err) const {
        std::cout << std::format("--> [PUB devices/gate/cmd/status] {{\"cmd_id\":\"{}\",\"state\":\"{}\","
                                 "\"progress_pct\":{},\"pos\":{},\"err\":{}}}\n",
                                 cmd_id, state, progress, pos, err);
    }

    DedupFilter dedup_;
    ActuatorState state_{ActuatorState::Idle};
    std::string activeCmdId_;
    int targetAngleDeg_{0};
    int currentAngleDeg_{0};
    uint32_t startTickMs_{0};
    uint32_t lastReportMs_{0};
};

#include <array>
#include <chrono>
#include <cstdint>
#include <format>
#include <iostream>
#include <string>
#include <string_view>
#include <vector>

enum class CmdState {
    Idle,
    Received,
    Executing,
    Completed,
    Failed,
    Expired
};

struct DedupEntry {
    std::string cmd_id;
    uint32_t timestamp_sec{0};
};

class DedupFilter {
public:
    static constexpr size_t Capacity = 16;

    [[nodiscard]] bool isDuplicate(std::string_view cmd_id) const noexcept {
        for (size_t i = 0; i < count_; ++i) {
            if (history_[i].cmd_id == cmd_id) {
                return true;
            }
        }
        return false;
    }

    void record(std::string_view cmd_id, uint32_t now_sec) {
        history_[head_] = DedupEntry{std::string(cmd_id), now_sec};
        head_ = (head_ + 1) % Capacity;
        if (count_ < Capacity) {
            ++count_;
        }
    }

private:
    std::array<DedupEntry, Capacity> history_{};
    size_t head_{0};
    size_t count_{0};
};

class ActuatorController {
public:
    void handleDownlink(std::string_view cmd_id, int target_pos,
                        uint32_t issued_at, uint16_t ttl_sec,
                        uint32_t now_sec, uint32_t now_ms) {
        if (now_sec > issued_at + ttl_sec) {
            publishExecStatus(cmd_id, "EXPIRED", 0, currentValue_, 104);
            return;
        }

        if (dedup_.isDuplicate(cmd_id)) {
            publishAck(cmd_id, "ACK_DUPLICATE");
            publishExecStatus(cmd_id, "COMPLETED", 100, currentValue_, 0);
            return;
        }

        dedup_.record(cmd_id, now_sec);
        publishAck(cmd_id, "ACK_RECEIVED");

        activeCmdId_ = cmd_id;
        targetValue_ = target_pos;
        startTimeMs_ = now_ms;
        state_ = CmdState::Executing;

        publishExecStatus(activeCmdId_, "STARTED", 0, currentValue_, 0);
    }

    void poll(uint32_t now_ms) {
        if (state_ != CmdState::Executing) {
            return;
        }

        uint32_t elapsed = now_ms - startTimeMs_;
        if (elapsed >= DurationMs) {
            currentValue_ = targetValue_;
            state_ = CmdState::Completed;
            publishExecStatus(activeCmdId_, "COMPLETED", 100, currentValue_, 0);
        } else if (now_ms - lastProgressReportMs_ >= 500) {
            lastProgressReportMs_ = now_ms;
            int progress = static_cast<int>((elapsed * 100) / DurationMs);
            publishExecStatus(activeCmdId_, "IN_PROGRESS", progress, currentValue_, 0);
        }
    }

private:
    static constexpr uint32_t DurationMs = 3000;

    void publishAck(std::string_view cmd_id, std::string_view status) const {
        std::cout << std::format("[MQTT OUT -> devices/zone1/cmd/ack] {{\"cmd_id\":\"{}\",\"status\":\"{}\"}}\n",
                                 cmd_id, status);
    }

    void publishExecStatus(std::string_view cmd_id, std::string_view state,
                           int progress, int val, int err) const {
        std::cout << std::format("[MQTT OUT -> devices/zone1/cmd/status] {{\"cmd_id\":\"{}\",\"state\":\"{}\","
                                 "\"progress_pct\":{},\"val\":{},\"err\":{}}}\n",
                                 cmd_id, state, progress, val, err);
    }

    DedupFilter dedup_;
    CmdState state_{CmdState::Idle};
    std::string activeCmdId_;
    int targetValue_{0};
    int currentValue_{0};
    uint32_t startTimeMs_{0};
    uint32_t lastProgressReportMs_{0};
};

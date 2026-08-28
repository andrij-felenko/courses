#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <string_view>
#include <unordered_map>
#include <queue>
#include <cstdint>
#include <span>
#include <memory>
#include <functional>
#include <format>
#include <cstring>

enum class ULogMsgType : uint8_t {
    Format       = 'F',
    Info         = 'I',
    Parameter    = 'P',
    AddLoggedMsg = 'A',
    Data         = 'D',
    Dropout      = 'S'
};

struct ULogFormat {
    std::string name;
    std::string fields;
};

struct ULogSubscription {
    uint16_t msg_id{0};
    uint8_t multi_id{0};
    std::string format_name;
};

struct ReplayFrame {
    uint64_t timestamp_us{0};
    uint16_t msg_id{0};
    uint8_t multi_id{0};
    std::string name;
    std::vector<uint8_t> payload;

    // Min-Heap компаратор за міткою часу
    bool operator>(const ReplayFrame& other) const noexcept {
        return timestamp_us > other.timestamp_us;
    }
};

using DispatchCallback = std::function<void(uint64_t t_sim, std::string_view topic, 
                                            uint8_t instance, std::span<const uint8_t> payload)>;

class ULogReplayEngineCpp {
public:
    explicit ULogReplayEngineCpp(std::string_view filepath, DispatchCallback callback)
        : callback_(std::move(callback)) {
        file_.open(std::string(filepath), std::ios::binary);
        if (!file_.is_open()) {
            throw std::runtime_error(std::format("Не вдалося відкрити ULog файл: {}", filepath));
        }
        validateHeader();
    }

    void runReplay() {
        while (file_ && !file_.eof()) {
            uint16_t msg_size = 0;
            uint8_t msg_type = 0;

            if (!file_.read(reinterpret_cast<char*>(&msg_size), 2)) break;
            if (!file_.read(reinterpret_cast<char*>(&msg_type), 1)) break;

            std::vector<uint8_t> payload(msg_size);
            if (!file_.read(reinterpret_cast<char*>(payload.data()), msg_size)) break;

            handleMessage(static_cast<ULogMsgType>(msg_type), payload);
        }

        // Очищення черги пріоритетів
        while (!priority_queue_.empty()) {
            ReplayFrame frame = std::move(const_cast<ReplayFrame&>(priority_queue_.top()));
            priority_queue_.pop();
            dispatchFrame(frame);
        }

        std::cout << std::format("[ULog C++20 Engine] Завершено. Оброблено: {} кадрів даних, {} дропаутів.\n",
                                 total_data_messages_, total_dropouts_);
    }

private:
    std::ifstream file_;
    DispatchCallback callback_;
    uint64_t start_time_us_{0};
    uint64_t current_sim_time_us_{0};
    
    std::unordered_map<std::string, ULogFormat> formats_;
    std::unordered_map<uint16_t, ULogSubscription> subscriptions_;
    std::priority_queue<ReplayFrame, std::vector<ReplayFrame>, std::greater<ReplayFrame>> priority_queue_;

    uint64_t total_data_messages_{0};
    uint64_t total_dropouts_{0};

    void validateHeader() {
        std::vector<uint8_t> header(16);
        if (!file_.read(reinterpret_cast<char*>(header.data()), 16)) {
            throw std::runtime_error("Файл занадто короткий для ULog заголовка");
        }
        const uint8_t magic[7] = {0x55, 0x4C, 0x6F, 0x67, 0x01, 0x12, 0x35};
        if (std::memcmp(header.data(), magic, 7) != 0) {
            throw std::runtime_error("Невірна магічна сигнатура ULog заголовка");
        }
        std::memcpy(&start_time_us_, &header[7], sizeof(uint64_t));
        current_sim_time_us_ = start_time_us_;
        std::cout << std::format("[ULog C++20 Engine] Час старту: {} мкс\n", start_time_us_);
    }

    void handleMessage(ULogMsgType type, std::span<const uint8_t> payload) {
        switch (type) {
            case ULogMsgType::Format: {
                std::string text(reinterpret_cast<const char*>(payload.data()), payload.size());
                auto colon = text.find(':');
                if (colon != std::string::npos) {
                    std::string name = text.substr(0, colon);
                    std::string fields = text.substr(colon + 1);
                    formats_[name] = ULogFormat{name, fields};
                }
                break;
            }
            case ULogMsgType::AddLoggedMsg: {
                if (payload.size() < 4) return;
                uint8_t multi_id = payload[0];
                uint16_t msg_id = payload[1] | (static_cast<uint16_t>(payload[2]) << 8);
                std::string name(reinterpret_cast<const char*>(&payload[3]), payload.size() - 3);
                subscriptions_[msg_id] = ULogSubscription{msg_id, multi_id, name};
                break;
            }
            case ULogMsgType::Data: {
                if (payload.size() < 10) return;
                uint16_t msg_id = payload[0] | (static_cast<uint16_t>(payload[1]) << 8);
                auto it = subscriptions_.find(msg_id);
                if (it == subscriptions_.end()) return;

                uint64_t timestamp = 0;
                std::memcpy(&timestamp, &payload[2], sizeof(uint64_t));

                ReplayFrame frame;
                frame.timestamp_us = timestamp;
                frame.msg_id = msg_id;
                frame.multi_id = it->second.multi_id;
                frame.name = it->second.format_name;
                frame.payload.assign(payload.begin() + 2, payload.end());

                priority_queue_.push(std::move(frame));
                total_data_messages_++;

                // Якщо черга накопичила > 512 кадрів, вивантажуємо найстаріший
                if (priority_queue_.size() > 512) {
                    ReplayFrame oldest = std::move(const_cast<ReplayFrame&>(priority_queue_.top()));
                    priority_queue_.pop();
                    dispatchFrame(oldest);
                }
                break;
            }
            case ULogMsgType::Dropout: {
                total_dropouts_++;
                break;
            }
            default:
                break;
        }
    }

    void dispatchFrame(const ReplayFrame& frame) {
        current_sim_time_us_ = frame.timestamp_us;
        if (callback_) {
            callback_(current_sim_time_us_, frame.name, frame.multi_id, frame.payload);
        }
    }
};

#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <chrono>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <optional>
#include <fstream>
#include <filesystem>
#include <cstdint>
#include <cstring>

namespace p2p {

using namespace std::chrono_literals;

enum class MessageState : uint8_t {
    Empty = 0,
    Ready,
    InFlight,
    Acked
};

enum class WalOp : uint8_t {
    Enqueue = 1,
    Acquire = 2,
    Ack     = 3,
    Nack    = 4
};

#pragma pack(push, 1)
struct WalHeader {
    uint32_t magic{0x51554555};
    uint32_t crc32{0};
    uint64_t msg_id{0};
    WalOp    op_type{WalOp::Enqueue};
    uint32_t payload_len{0};
};
#pragma pack(pop)

struct QueueItem {
    uint64_t id{0};
    MessageState state{MessageState::Empty};
    std::chrono::steady_clock::time_point lease_deadline{};
    uint32_t attempts{0};
    std::string payload;
};

class DurableQueue {
public:
    explicit DurableQueue(std::filesystem::path wal_path, size_t capacity = 1024)
        : wal_path_(std::move(wal_path)), items_(capacity), running_(true) {
        open_and_replay_wal();
        reclaim_thread_ = std::jthread([this](std::stop_token st) {
            reclaim_loop(st);
        });
    }

    ~DurableQueue() {
        stop();
    }

    uint64_t publish(std::string_view payload) {
        std::unique_lock lock(mutex_);
        uint64_t msg_id = next_id_++;
        size_t slot = msg_id % items_.size();

        items_[slot].id = msg_id;
        items_[slot].state = MessageState::Ready;
        items_[slot].attempts = 0;
        items_[slot].payload = std::string(payload);

        append_wal(WalOp::Enqueue, msg_id, payload);

        cv_ready_.notify_one();
        return msg_id;
    }

    struct AcquiredTask {
        uint64_t id;
        std::string payload;
    };

    std::optional<AcquiredTask> acquire(std::chrono::milliseconds lease_duration) {
        std::unique_lock lock(mutex_);

        while (running_) {
            auto now = std::chrono::steady_clock::now();
            for (auto &item : items_) {
                if (item.state == MessageState::Ready) {
                    item.state = MessageState::InFlight;
                    item.lease_deadline = now + lease_duration;
                    item.attempts++;

                    append_wal(WalOp::Acquire, item.id, {});
                    return AcquiredTask{item.id, item.payload};
                }
            }

            cv_ready_.wait_for(lock, 200ms);
        }
        return std::nullopt;
    }

    void ack(uint64_t msg_id) {
        std::unique_lock lock(mutex_);
        size_t slot = msg_id % items_.size();
        if (items_[slot].id == msg_id && items_[slot].state == MessageState::InFlight) {
            items_[slot].state = MessageState::Acked;
            append_wal(WalOp::Ack, msg_id, {});
        }
    }

    void nack(uint64_t msg_id) {
        std::unique_lock lock(mutex_);
        size_t slot = msg_id % items_.size();
        if (items_[slot].id == msg_id && items_[slot].state == MessageState::InFlight) {
            items_[slot].state = MessageState::Ready;
            append_wal(WalOp::Nack, msg_id, {});
            cv_ready_.notify_one();
        }
    }

    void stop() {
        {
            std::unique_lock lock(mutex_);
            running_ = false;
        }
        cv_ready_.notify_all();
        if (wal_file_.is_open()) {
            wal_file_.flush();
            wal_file_.close();
        }
    }

private:
    static uint32_t calc_crc(std::string_view data) {
        uint32_t crc = 0xFFFFFFFF;
        for (unsigned char b : data) {
            crc ^= b;
            for (int j = 0; j < 8; ++j) {
                crc = (crc >> 1) ^ (0xEDB88320 & -(crc & 1));
            }
        }
        return ~crc;
    }

    void append_wal(WalOp op, uint64_t msg_id, std::string_view payload) {
        if (!wal_file_.is_open()) return;

        WalHeader hdr;
        hdr.msg_id = msg_id;
        hdr.op_type = op;
        hdr.payload_len = static_cast<uint32_t>(payload.size());
        hdr.crc32 = calc_crc(payload);

        wal_file_.write(reinterpret_cast<const char*>(&hdr), sizeof(hdr));
        if (!payload.empty()) {
            wal_file_.write(payload.data(), payload.size());
        }
        wal_file_.flush();
    }

    void open_and_replay_wal() {
        if (std::filesystem::exists(wal_path_)) {
            std::ifstream in(wal_path_, std::ios::binary);
            WalHeader hdr;
            while (in.read(reinterpret_cast<char*>(&hdr), sizeof(hdr))) {
                if (hdr.magic != 0x51554555) break;

                std::string payload(hdr.payload_len, '\0');
                if (hdr.payload_len > 0) {
                    in.read(payload.data(), hdr.payload_len);
                }

                size_t slot = hdr.msg_id % items_.size();
                if (hdr.op_type == WalOp::Enqueue) {
                    items_[slot].id = hdr.msg_id;
                    items_[slot].state = MessageState::Ready;
                    items_[slot].payload = std::move(payload);
                    if (hdr.msg_id >= next_id_) {
                        next_id_ = hdr.msg_id + 1;
                    }
                } else if (hdr.op_type == WalOp::Ack) {
                    items_[slot].state = MessageState::Acked;
                } else if (hdr.op_type == WalOp::Nack) {
                    items_[slot].state = MessageState::Ready;
                }
            }
        }
        wal_file_.open(wal_path_, std::ios::binary | std::ios::app);
    }

    void reclaim_loop(std::stop_token st) {
        while (!st.stop_requested() && running_) {
            std::this_thread::sleep_for(100ms);
            std::unique_lock lock(mutex_);
            auto now = std::chrono::steady_clock::now();
            bool awakened = false;

            for (auto &item : items_) {
                if (item.state == MessageState::InFlight && now >= item.lease_deadline) {
                    std::cout << "[Брокер C++] Таймаут оренди задачі #" << item.id
                              << ". Повертаємо в чергу READY.\n";
                    item.state = MessageState::Ready;
                    awakened = true;
                }
            }

            if (awakened) {
                cv_ready_.notify_all();
            }
        }
    }

    std::filesystem::path wal_path_;
    std::ofstream wal_file_;
    std::vector<QueueItem> items_;
    uint64_t next_id_{1};
    mutable std::mutex mutex_;
    std::condition_variable cv_ready_;
    bool running_{false};
    std::jthread reclaim_thread_;
};

} // namespace p2p

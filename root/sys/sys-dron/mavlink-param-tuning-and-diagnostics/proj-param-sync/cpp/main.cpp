#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <unordered_map>
#include <chrono>
#include <array>
#include <algorithm>
#include <cstring>
#include <bit>
#include <optional>
#include <functional>

/* Системні константи протоколу MAVLink */
constexpr size_t MAVLINK_PARAM_ID_LEN = 16;
constexpr auto STREAM_TIMEOUT = std::chrono::milliseconds(600);
constexpr auto REQUEST_TIMEOUT = std::chrono::milliseconds(1500);
constexpr size_t MAX_BATCH_MISSING = 8;
constexpr int MAX_RETRIES = 3;

enum class SyncState {
    Idle,
    RequestingAll,
    ReceivingStream,
    RequestingMissing,
    Synced,
    Error
};

struct ParamRecord {
    std::string name;
    float raw_value{0.0f};
    uint8_t type{0};
    uint16_t index{0};

    [[nodiscard]] int32_t as_int32() const noexcept {
        return std::bit_cast<int32_t>(raw_value);
    }
    [[nodiscard]] uint32_t as_uint32() const noexcept {
        return std::bit_cast<uint32_t>(raw_value);
    }
    [[nodiscard]] float as_float() const noexcept {
        return raw_value;
    }
};

struct PendingWrite {
    std::string name;
    float raw_value{0.0f};
    uint8_t type{0};
    int retries{0};
    std::chrono::steady_clock::time_point last_sent;
};

class ParamSyncEngine {
public:
    using SendCallback = std::function<void(const uint8_t* buffer, size_t length)>;

    ParamSyncEngine(uint8_t sys_id, uint8_t comp_id,
                    uint8_t target_sys, uint8_t target_comp)
        : sys_id_(sys_id), comp_id_(comp_id),
          target_sys_(target_sys), target_comp_(target_comp) {}

    void set_send_callback(SendCallback cb) {
        send_cb_ = std::move(cb);
    }

    void start_sync() {
        state_ = SyncState::RequestingAll;
        total_count_ = 0;
        received_count_ = 0;
        received_mask_.clear();
        params_by_index_.clear();
        params_by_name_.clear();
        last_packet_time_ = std::chrono::steady_clock::now();
        retries_count_ = 0;

        send_param_request_list();
    }

    void handle_param_value(const char raw_id[16], float value, uint8_t type,
                            uint16_t count, uint16_t index) {
        auto now = std::chrono::steady_clock::now();
        last_packet_time_ = now;

        std::string name = extract_safe_name(raw_id);

        /* Якщо це перше повідомлення — ініціалізуємо бітову маску */
        if (state_ == SyncState::RequestingAll || total_count_ == 0) {
            total_count_ = count;
            received_mask_.assign(total_count_, false);
            params_by_index_.resize(total_count_);
            state_ = SyncState::ReceivingStream;
        }

        /* Перевірка валідності індексу */
        if (index < total_count_) {
            if (!received_mask_[index]) {
                received_mask_[index] = true;
                ++received_count_;

                ParamRecord rec{
                    .name = name,
                    .raw_value = value,
                    .type = type,
                    .index = index
                };
                params_by_index_[index] = rec;
                params_by_name_[name] = rec;
            }
        }

        /* Перевірка черги запису (чи це луна від нашого PARAM_SET) */
        if (!write_queue_.empty()) {
            auto &current_write = write_queue_.front();
            if (current_write.name == name) {
                write_queue_.erase(write_queue_.begin());
                if (!write_queue_.empty()) {
                    send_param_set(write_queue_.front());
                }
            }
        }

        /* Якщо всі параметри отримано */
        if (received_count_ == total_count_ && total_count_ > 0) {
            state_ = SyncState::Synced;
        }
    }

    void update() {
        auto now = std::chrono::steady_clock::now();

        switch (state_) {
        case SyncState::RequestingAll:
            if (now - last_packet_time_ > REQUEST_TIMEOUT) {
                if (++retries_count_ > MAX_RETRIES) {
                    state_ = SyncState::Error;
                } else {
                    last_packet_time_ = now;
                    send_param_request_list();
                }
            }
            break;

        case SyncState::ReceivingStream:
            if (now - last_packet_time_ > STREAM_TIMEOUT) {
                state_ = SyncState::RequestingMissing;
                missing_sweep_index_ = 0;
                last_packet_time_ = now;
            }
            break;

        case SyncState::RequestingMissing:
            if (now - last_packet_time_ > STREAM_TIMEOUT) {
                request_next_missing_batch();
                last_packet_time_ = now;
            }
            break;

        case SyncState::Synced:
        case SyncState::Idle:
        case SyncState::Error:
            break;
        }

        /* Обробка таймаутів запису */
        if (!write_queue_.empty()) {
            auto &current_write = write_queue_.front();
            if (now - current_write.last_sent > REQUEST_TIMEOUT) {
                if (++current_write.retries > MAX_RETRIES) {
                    write_queue_.erase(write_queue_.begin());
                } else {
                    send_param_set(current_write);
                }
            }
        }
    }

    void set_parameter(std::string_view name, float val, uint8_t type) {
        PendingWrite write_op{
            .name = std::string(name),
            .raw_value = val,
            .type = type,
            .retries = 0,
            .last_sent = std::chrono::steady_clock::now()
        };
        write_queue_.push_back(write_op);
        if (write_queue_.size() == 1) {
            send_param_set(write_queue_.front());
        }
    }

    [[nodiscard]] SyncState state() const noexcept { return state_; }
    [[nodiscard]] uint16_t total_count() const noexcept { return total_count_; }
    [[nodiscard]] uint16_t received_count() const noexcept { return received_count_; }

    [[nodiscard]] std::optional<ParamRecord> get_param(std::string_view name) const {
        auto it = params_by_name_.find(std::string(name));
        if (it != params_by_name_.end()) {
            return it->second;
        }
        return std::nullopt;
    }

private:
    static std::string extract_safe_name(const char raw_id[16]) {
        size_t len = 0;
        while (len < 16 && raw_id[len] != '\0') {
            ++len;
        }
        return std::string(raw_id, len);
    }

    void send_param_request_list() {
        uint8_t dummy_buf[16] = {0};
        if (send_cb_) {
            send_cb_(dummy_buf, sizeof(dummy_buf));
        }
    }

    void send_param_set(PendingWrite &op) {
        op.last_sent = std::chrono::steady_clock::now();
        uint8_t dummy_buf[32] = {0};
        if (send_cb_) {
            send_cb_(dummy_buf, sizeof(dummy_buf));
        }
    }

    void request_next_missing_batch() {
        size_t requested_in_batch = 0;
        while (missing_sweep_index_ < total_count_ && requested_in_batch < MAX_BATCH_MISSING) {
            if (!received_mask_[missing_sweep_index_]) {
                send_param_request_read_index(static_cast<int16_t>(missing_sweep_index_));
                ++requested_in_batch;
            }
            ++missing_sweep_index_;
        }

        /* Якщо дійшли кінця списку, а прогалини ще лишилися — повертаємося на початок */
        if (missing_sweep_index_ >= total_count_) {
            missing_sweep_index_ = 0;
            if (received_count_ == total_count_) {
                state_ = SyncState::Synced;
            }
        }
    }

    void send_param_request_read_index(int16_t index) {
        uint8_t dummy_buf[24] = {0};
        if (send_cb_) {
            send_cb_(dummy_buf, sizeof(dummy_buf));
        }
    }

    uint8_t sys_id_{255};
    uint8_t comp_id_{190};
    uint8_t target_sys_{1};
    uint8_t target_comp_{1};

    SyncState state_{SyncState::Idle};
    uint16_t total_count_{0};
    uint16_t received_count_{0};
    std::vector<bool> received_mask_;
    std::vector<ParamRecord> params_by_index_;
    std::unordered_map<std::string, ParamRecord> params_by_name_;

    std::chrono::steady_clock::time_point last_packet_time_;
    int retries_count_{0};
    size_t missing_sweep_index_{0};

    std::vector<PendingWrite> write_queue_;
    SendCallback send_cb_;
};

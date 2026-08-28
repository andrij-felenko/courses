#include <cstdint>
#include <cstddef>
#include <string_view>
#include <array>
#include <span>
#include <functional>
#include <optional>
#include <cstring>

enum class AtStatus : uint8_t {
    Ok = 0,
    Error,
    Timeout,
    Aborted
};

struct AtCommandDescriptor {
    std::string_view cmd_text;
    std::string_view expect_prefix;
    uint32_t         timeout_ms{1000};
    uint8_t          max_retries{0};
    uint8_t          current_retry{0};
    std::function<void(AtStatus, std::string_view)> callback{};
};

struct UrcRegistration {
    std::string_view prefix;
    std::function<void(std::string_view)> handler;
};

template <size_t RxSize = 512, size_t QueueCapacity = 8, size_t MaxUrc = 8>
class AtCommandEngine {
public:
    using TxFunction = std::function<void(std::span<const uint8_t>)>;
    using TickFunction = std::function<uint32_t()>;

    AtCommandEngine(TxFunction tx, TickFunction tick) 
        : tx_fn_{std::move(tx)}, tick_fn_{std::move(tick)} {}

    [[nodiscard]] uint8_t* rx_buffer() noexcept { return rx_buffer_.data(); }
    [[nodiscard]] static constexpr size_t rx_capacity() noexcept { return RxSize; }

    bool register_urc(std::string_view prefix, std::function<void(std::string_view)> handler) noexcept {
        if (urc_count_ >= MaxUrc) return false;
        urc_table_[urc_count_++] = {prefix, std::move(handler)};
        return true;
    }

    bool enqueue_command(AtCommandDescriptor cmd) noexcept {
        if (queue_count_ >= QueueCapacity) return false;
        queue_[queue_head_] = std::move(cmd);
        queue_head_ = (queue_head_ + 1U) % QueueCapacity;
        ++queue_count_;
        return true;
    }

    void poll(uint16_t dma_cndtr) noexcept {
        const uint32_t now = tick_fn_();
        char line_buf[128];

        // 1. Потокова екстракція рядків та розпізнавання URC
        while (extract_line(dma_cndtr, line_buf, sizeof(line_buf))) {
            const std::string_view line{line_buf};
            bool is_urc = false;

            for (size_t i = 0; i < urc_count_; ++i) {
                if (line.starts_with(urc_table_[i].prefix)) {
                    if (urc_table_[i].handler) {
                        urc_table_[i].handler(line);
                    }
                    is_urc = true;
                    break;
                }
            }

            if (is_urc) continue;

            if (state_ == State::WaitResponse && active_cmd_) {
                if (!active_cmd_->expect_prefix.empty() && line.starts_with(active_cmd_->expect_prefix)) {
                    last_data_line_ = line;
                } else if (line == "OK") {
                    if (active_cmd_->callback) {
                        active_cmd_->callback(AtStatus::Ok, last_data_line_);
                    }
                    state_ = State::Idle;
                    active_cmd_.reset();
                } else if (line == "ERROR" || line.starts_with("+CME ERROR:")) {
                    handle_failure(now, AtStatus::Error, line);
                }
            }
        }

        // 2. FSM черги
        switch (state_) {
            case State::Idle:
                if (queue_count_ > 0) {
                    active_cmd_ = queue_[queue_tail_];
                    queue_tail_ = (queue_tail_ + 1U) % QueueCapacity;
                    --queue_count_;
                    last_data_line_ = {};
                    state_ = State::Send;
                }
                break;

            case State::Send:
                if (active_cmd_) {
                    auto span_data = std::as_bytes(std::span{active_cmd_->cmd_text.data(), active_cmd_->cmd_text.size()});
                    tx_fn_(std::span<const uint8_t>{reinterpret_cast<const uint8_t*>(span_data.data()), span_data.size()});
                    timer_start_ms_ = now;
                    state_ = State::WaitResponse;
                }
                break;

            case State::WaitResponse:
                if (active_cmd_ && (now - timer_start_ms_) >= active_cmd_->timeout_ms) {
                    handle_failure(now, AtStatus::Timeout, {});
                }
                break;

            case State::RetryDelay:
                if ((now - timer_start_ms_) >= 100U) {
                    state_ = State::Send;
                }
                break;
        }
    }

private:
    enum class State : uint8_t {
        Idle,
        Send,
        WaitResponse,
        RetryDelay
    };

    void handle_failure(uint32_t now, AtStatus status, std::string_view err_msg) noexcept {
        if (active_cmd_->current_retry < active_cmd_->max_retries) {
            ++active_cmd_->current_retry;
            timer_start_ms_ = now;
            state_ = State::RetryDelay;
        } else {
            if (active_cmd_->callback) {
                active_cmd_->callback(status, err_msg);
            }
            state_ = State::Idle;
            active_cmd_.reset();
        }
    }

    bool extract_line(uint16_t dma_cndtr, char* out, size_t max_len) noexcept {
        const uint16_t head = static_cast<uint16_t>(RxSize - dma_cndtr);
        if (head == rx_tail_) return false;

        uint16_t scan = rx_tail_;
        bool found = false;
        while (scan != head) {
            if (rx_buffer_[scan] == '\n') {
                found = true;
                break;
            }
            scan = (scan + 1U) % RxSize;
        }
        if (!found) return false;

        size_t written = 0;
        while (rx_tail_ != scan) {
            const char c = static_cast<char>(rx_buffer_[rx_tail_]);
            if (c != '\r' && c != '\n' && written < max_len - 1U) {
                out[written++] = c;
            }
            rx_tail_ = (rx_tail_ + 1U) % RxSize;
        }
        rx_tail_ = (rx_tail_ + 1U) % RxSize; // skip '\n'
        out[written] = '\0';
        return (written > 0);
    }

    TxFunction tx_fn_;
    TickFunction tick_fn_;

    std::array<uint8_t, RxSize> rx_buffer_{};
    uint16_t rx_tail_{0};

    std::array<AtCommandDescriptor, QueueCapacity> queue_{};
    size_t queue_head_{0};
    size_t queue_tail_{0};
    size_t queue_count_{0};

    std::array<UrcRegistration, MaxUrc> urc_table_{};
    size_t urc_count_{0};

    State state_{State::Idle};
    std::optional<AtCommandDescriptor> active_cmd_{std::nullopt};
    uint32_t timer_start_ms_{0};
    std::string_view last_data_line_{};
};

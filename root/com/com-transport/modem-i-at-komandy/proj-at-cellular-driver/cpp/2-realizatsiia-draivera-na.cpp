#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <functional>
#include <optional>
#include <span>
#include <chrono>
#include <cstring>

enum class AtResponseCode {
    Ok = 0,
    Error,
    Timeout,
    Busy
};

using UrcHandler = std::function<void(std::string_view line)>;

class CellularAtDriver {
public:
    using WriteFn = std::function<void(std::span<const uint8_t>)>;
    using TickFn = std::function<uint32_t()>;

    explicit CellularAtDriver(WriteFn write_fn, TickFn tick_fn)
        : write_uart_(std::move(write_fn)), get_tick_ms_(std::move(tick_fn)) {}

    void register_urc(std::string_view prefix, UrcHandler handler) {
        urc_registry_.emplace_back(std::string(prefix), std::move(handler));
    }

    void feed_rx_isr(uint8_t byte) noexcept {
        size_t next_head = (rx_head_ + 1) % kRingBufferSize;
        if (next_head != rx_tail_) {
            ring_buffer_[rx_head_] = byte;
            rx_head_ = next_head;
        }
    }

    void process() {
        if (transaction_ && transaction_->active) {
            uint32_t now = get_tick_ms_();
            if (now - transaction_->start_time_ms >= transaction_->timeout_ms) {
                transaction_->result = AtResponseCode::Timeout;
                transaction_->completed = true;
                transaction_->active = false;
            }
        }

        while (rx_head_ != rx_tail_) {
            uint8_t ch = ring_buffer_[rx_tail_];
            rx_tail_ = (rx_tail_ + 1) % kRingBufferSize;

            if (ch == ' ' && line_acc_.size() == 1 && line_acc_[0] == '>') {
                prompt_detected_ = true;
                line_acc_.clear();
                continue;
            }

            if (ch == '\r' || ch == '\n') {
                if (!line_acc_.empty()) {
                    dispatch_line(line_acc_);
                    line_acc_.clear();
                }
            } else {
                if (line_acc_.size() < kMaxLineLength) {
                    line_acc_.push_back(static_cast<char>(ch));
                } else {
                    line_acc_.clear();
                }
            }
        }
    }

    std::optional<std::string> send_command(std::string_view cmd,
                                            std::chrono::milliseconds timeout = std::chrono::milliseconds(3000)) {
        if (transaction_ && transaction_->active) {
            return std::nullopt;
        }

        transaction_ = Transaction{
            .response_body = "",
            .timeout_ms = static_cast<uint32_t>(timeout.count()),
            .start_time_ms = get_tick_ms_(),
            .result = AtResponseCode::Timeout,
            .completed = false,
            .active = true
        };

        std::string full_cmd(cmd);
        full_cmd += "\r\n";
        write_uart_(std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(full_cmd.data()), full_cmd.size()));

        while (!transaction_->completed) {
            process();
        }

        if (transaction_->result == AtResponseCode::Ok) {
            return transaction_->response_body;
        }
        return std::nullopt;
    }

private:
    struct Transaction {
        std::string response_body;
        uint32_t timeout_ms{3000};
        uint32_t start_time_ms{0};
        AtResponseCode result{AtResponseCode::Timeout};
        bool completed{false};
        bool active{false};
    };

    struct UrcEntry {
        std::string prefix;
        UrcHandler handler;
    };

    static constexpr size_t kRingBufferSize = 1024;
    static constexpr size_t kMaxLineLength = 256;

    WriteFn write_uart_;
    TickFn get_tick_ms_;

    uint8_t ring_buffer_[kRingBufferSize]{};
    volatile size_t rx_head_{0};
    volatile size_t rx_tail_{0};

    std::string line_acc_;
    std::vector<UrcEntry> urc_registry_;
    std::optional<Transaction> transaction_;
    bool prompt_detected_{false};

    void dispatch_line(std::string_view line) {
        for (const auto& [prefix, handler] : urc_registry_) {
            if (line.starts_with(prefix)) {
                handler(line);
                return;
            }
        }

        if (!transaction_ || !transaction_->active) {
            return;
        }

        if (line == "OK" || line.starts_with("CONNECT")) {
            transaction_->result = AtResponseCode::Ok;
            transaction_->completed = true;
            transaction_->active = false;
            return;
        }

        if (line == "ERROR" || line.starts_with("+CME ERROR:") ||
            line.starts_with("+CMS ERROR:") || line == "NO CARRIER" || line == "BUSY") {
            transaction_->result = AtResponseCode::Error;
            transaction_->completed = true;
            transaction_->active = false;
            return;
        }

        if (!transaction_->response_body.empty()) {
            transaction_->response_body += "\n";
        }
        transaction_->response_body += line;
    }
};

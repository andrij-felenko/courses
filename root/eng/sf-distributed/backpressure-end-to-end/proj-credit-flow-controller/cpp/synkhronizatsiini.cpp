#include <iostream>
#include <vector>
#include <memory>
#include <mutex>
#include <condition_variable>
#include <optional>
#include <span>
#include <cstdint>

struct Message {
    uint32_t id{0};
    uint32_t payload_size{0};
};

class FlowController {
public:
    static constexpr size_t kCapacity = 100;
    static constexpr size_t kHighWatermark = 80;
    static constexpr size_t kLowWatermark = 30;

    explicit FlowController() = default;
    ~FlowController() = default;

    FlowController(const FlowController&) = delete;
    FlowController& operator=(const FlowController&) = delete;

    // Вхідний мережевий виклик від event-loop сокета
    [[nodiscard]] bool push_ingress(Message msg) {
        std::unique_lock<std::mutex> lock(mutex_);

        if (count_ >= kCapacity) {
            return false; // Захист від збійного клієнта
        }

        ring_buffer_[tail_] = msg;
        tail_ = (tail_ + 1) % kCapacity;
        ++count_;

        if (active_credits_ > 0) {
            --active_credits_;
        }

        if (count_ >= kHighWatermark && !socket_paused_) {
            socket_paused_ = true;
            update_epoll_registration(false);
        }

        cv_not_empty_.notify_one();
        return true;
    }

    // Вибірка повідомлення воркером бізнес-обробки
    [[nodiscard]] Message pop_worker() {
        std::unique_lock<std::mutex> lock(mutex_);

        cv_not_empty_.wait(lock, [this] { return count_ > 0; });

        Message msg = ring_buffer_[head_];
        head_ = (head_ + 1) % kCapacity;
        --count_;

        if (count_ <= kLowWatermark && socket_paused_) {
            socket_paused_ = false;
            update_epoll_registration(true);

            auto grant = static_cast<int32_t>(kCapacity - count_);
            active_credits_ += grant;
            std::cout << "[CREDIT] Видано новий кредит: +" << grant 
                      << " (активний ліміт: " << active_credits_ << ")\n";
        }

        cv_not_full_.notify_one();
        return msg;
    }

    [[nodiscard]] size_t current_depth() const noexcept {
        std::lock_guard<std::mutex> lock(mutex_);
        return count_;
    }

private:
    void update_epoll_registration(bool enable_read) const noexcept {
        if (enable_read) {
            std::cout << "[EPOLL] Увімкнено EPOLLIN (відновлення TCP Window)\n";
        } else {
            std::cout << "[EPOLL] Вимкнено EPOLLIN (активація TCP ZeroWindow)\n";
        }
    }

    mutable std::mutex mutex_;
    std::condition_variable cv_not_empty_;
    std::condition_variable cv_not_full_;

    std::vector<Message> ring_buffer_{std::vector<Message>(kCapacity)};
    size_t head_{0};
    size_t tail_{0};
    size_t count_{0};

    int32_t active_credits_{0};
    bool socket_paused_{false};
};

#include <iostream>
#include <vector>
#include <queue>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <atomic>
#include <memory>
#include <variant>
#include <functional>
#include <chrono>

enum class MessageType { Ping, Pong, Stop };

struct Message {
    MessageType type;
    int payload;
    uint32_t sender_id;
};

class ActorSystem;

class Actor {
public:
    using Behavior = std::function<void(Actor& self, const Message& msg)>;

    Actor(uint32_t id, Behavior init_behavior, ActorSystem& system)
        : id_(id), behavior_(std::move(init_behavior)), system_(system) {}

    uint32_t id() const noexcept { return id_; }
    bool is_active() const noexcept { return is_active_.load(std::memory_order_relaxed); }
    void stop() noexcept { is_active_.store(false, std::memory_order_relaxed); }

    void become(Behavior new_behavior) {
        behavior_ = std::move(new_behavior);
    }

    void enqueue(Message msg);
    void process_batch(size_t max_messages);
    ActorSystem& system() noexcept { return system_; }

private:
    uint32_t id_;
    Behavior behavior_;
    ActorSystem& system_;
    std::queue<Message> mailbox_;
    std::mutex mailbox_mutex_;
    std::atomic<bool> is_active_{true};
    std::atomic<bool> is_scheduled_{false};
};

class ActorSystem {
public:
    explicit ActorSystem(size_t thread_count = std::thread::hardware_concurrency())
        : stop_requested_(false) {
        workers_.reserve(thread_count);
        for (size_t i = 0; i < thread_count; ++i) {
            workers_.emplace_back([this] { worker_loop(); });
        }
    }

    ~ActorSystem() {
        shutdown();
    }

    uint32_t spawn(Actor::Behavior behavior) {
        std::lock_guard<std::mutex> lock(actors_mutex_);
        auto id = static_cast<uint32_t>(actors_.size());
        actors_.push_back(std::make_unique<Actor>(id, std::move(behavior), *this));
        return id;
    }

    void send(uint32_t target_id, Message msg) {
        std::lock_guard<std::mutex> lock(actors_mutex_);
        if (target_id < actors_.size()) {
            actors_[target_id]->enqueue(std::move(msg));
        }
    }

    void schedule(Actor* actor) {
        {
            std::lock_guard<std::mutex> lock(ready_mutex_);
            ready_queue_.push(actor);
        }
        ready_cv_.notify_one();
    }

    void shutdown() {
        {
            std::lock_guard<std::mutex> lock(ready_mutex_);
            stop_requested_ = true;
        }
        ready_cv_.notify_all();
        for (auto& worker : workers_) {
            if (worker.joinable()) {
                worker.join();
            }
        }
    }

private:
    void worker_loop() {
        constexpr size_t quota = 4;
        while (true) {
            Actor* actor = nullptr;
            {
                std::unique_lock<std::mutex> lock(ready_mutex_);
                ready_cv_.wait(lock, [this] {
                    return stop_requested_ || !ready_queue_.empty();
                });

                if (stop_requested_ && ready_queue_.empty()) {
                    return;
                }

                actor = ready_queue_.front();
                ready_queue_.pop();
            }

            if (actor) {
                actor->process_batch(quota);
            }
        }
    }

    std::vector<std::unique_ptr<Actor>> actors_;
    std::mutex actors_mutex_;
    std::queue<Actor*> ready_queue_;
    std::mutex ready_mutex_;
    std::condition_variable ready_cv_;
    std::vector<std::thread> workers_;
    bool stop_requested_;
};

void Actor::enqueue(Message msg) {
    if (!is_active()) return;

    bool was_empty = false;
    {
        std::lock_guard<std::mutex> lock(mailbox_mutex_);
        was_empty = mailbox_.empty();
        mailbox_.push(std::move(msg));
    }

    bool expected = false;
    if (is_scheduled_.compare_exchange_strong(expected, true)) {
        system_.schedule(this);
    }
}

void Actor::process_batch(size_t max_messages) {
    size_t processed = 0;
    while (processed < max_messages) {
        Message msg;
        {
            std::lock_guard<std::mutex> lock(mailbox_mutex_);
            if (mailbox_.empty()) break;
            msg = std::move(mailbox_.front());
            mailbox_.pop();
        }

        if (is_active_ && behavior_) {
            behavior_(*this, msg);
        }
        ++processed;
    }

    std::lock_guard<std::mutex> lock(mailbox_mutex_);
    if (!mailbox_.empty() && is_active_) {
        system_.schedule(this);
    } else {
        is_scheduled_.store(false, std::memory_order_release);
    }
}

int main() {
    std::cout << "Ініціалізація C++ рантайму акторів...\n";
    ActorSystem system(2);

    uint32_t ping_pid = 0;
    uint32_t pong_pid = 0;

    ping_pid = system.spawn([&system](Actor& self, const Message& msg) {
        if (msg.type == MessageType::Pong) {
            std::cout << "[C++ Ping " << self.id() << "] Отримано PONG (раунд " << msg.payload << ")\n";
            if (msg.payload >= 5) {
                std::cout << "[C++ Ping] Завершення обміну.\n";
                system.send(msg.sender_id, Message{MessageType::Stop, 0, self.id()});
                self.stop();
            } else {
                std::this_thread::sleep_for(std::chrono::milliseconds(100));
                system.send(msg.sender_id, Message{MessageType::Ping, msg.payload + 1, self.id()});
            }
        }
    });

    pong_pid = system.spawn([&system](Actor& self, const Message& msg) {
        if (msg.type == MessageType::Ping) {
            std::cout << "[C++ Pong " << self.id() << "] Отримано PING (" << msg.payload << "), відповідаю PONG\n";
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
            system.send(msg.sender_id, Message{MessageType::Pong, msg.payload, self.id()});
        } else if (msg.type == MessageType::Stop) {
            std::cout << "[C++ Pong] Отримано STOP. Зупинка.\n";
            self.stop();
        }
    });

    // Запуск обміну
    system.send(pong_pid, Message{MessageType::Ping, 1, ping_pid});

    std::this_thread::sleep_for(std::chrono::seconds(2));
    system.shutdown();
    std::cout << "C++ систему акторів зупинено успішно.\n";
    return 0;
}

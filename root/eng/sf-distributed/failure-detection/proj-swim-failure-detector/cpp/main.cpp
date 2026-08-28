#include <iostream>
#include <vector>
#include <unordered_map>
#include <optional>
#include <chrono>
#include <random>
#include <algorithm>

enum class MemberStatus {
    Alive,
    Suspect,
    Dead
};

struct Member {
    uint32_t id;
    MemberStatus status{MemberStatus::Alive};
    uint32_t incarnation{0};
    std::chrono::steady_clock::time_point state_change_time;
};

class SwimFailureDetector {
public:
    using Milliseconds = std::chrono::milliseconds;

    SwimFailureDetector(uint32_t self_id, 
                        Milliseconds ping_timeout = Milliseconds(200),
                        Milliseconds suspect_timeout = Milliseconds(1000),
                        size_t k_helpers = 3)
        : self_id_(self_id),
          ping_timeout_(ping_timeout),
          suspect_timeout_(suspect_timeout),
          k_helpers_(k_helpers),
          rng_(std::random_device{}()) {}

    void add_member(uint32_t id, std::chrono::steady_clock::time_point now) {
        if (id == self_id_ || members_.contains(id)) {
            return;
        }
        members_.emplace(id, Member{
            .id = id,
            .status = MemberStatus::Alive,
            .incarnation = 0,
            .state_change_time = now
        });
    }

    void apply_update(uint32_t id, MemberStatus new_status, uint32_t inc, 
                      std::chrono::steady_clock::time_point now) {
        // Якщо надійшла підозра про нас самих — спростовуємо її новою інкарнацією
        if (id == self_id_) {
            if (new_status == MemberStatus::Suspect && inc >= self_incarnation_) {
                self_incarnation_ = inc + 1;
                std::cout << "[Node " << self_id_ 
                          << "] Спростування підозри! Нова інкарнація: " 
                          << self_incarnation_ << "\n";
            }
            return;
        }

        auto it = members_.find(id);
        if (it == members_.end()) {
            return;
        }
        Member& m = it->second;

        if (inc > m.incarnation) {
            m.incarnation = inc;
            m.status = new_status;
            m.state_change_time = now;
        } else if (inc == m.incarnation) {
            if (m.status == MemberStatus::Alive && new_status == MemberStatus::Suspect) {
                m.status = MemberStatus::Suspect;
                m.state_change_time = now;
            } else if (new_status == MemberStatus::Dead) {
                m.status = MemberStatus::Dead;
                m.state_change_time = now;
            }
        }
    }

    void start_probe_round(std::chrono::steady_clock::time_point now) {
        if (members_.empty() || active_probe_.has_value()) {
            return;
        }

        std::vector<uint32_t> eligible;
        for (const auto& [id, m] : members_) {
            if (m.status != MemberStatus::Dead) {
                eligible.push_back(id);
            }
        }
        if (eligible.empty()) {
            return;
        }

        std::uniform_int_distribution<size_t> dist(0, eligible.size() - 1);
        uint32_t target_id = eligible[dist(rng_)];

        active_probe_ = ProbeState{
            .target_id = target_id,
            .start_time = now,
            .ping_req_sent = false
        };

        std::cout << "[Node " << self_id_ << "] Старт прямого Ping до вузла " 
                  << target_id << "\n";
    }

    void on_ack_received(uint32_t from_id, uint32_t inc, 
                         std::chrono::steady_clock::time_point now) {
        if (active_probe_.has_value() && active_probe_->target_id == from_id) {
            active_probe_.reset();
            apply_update(from_id, MemberStatus::Alive, inc, now);
            std::cout << "[Node " << self_id_ << "] Отримано успішний Ack від " 
                      << from_id << "\n";
        }
    }

    void tick(std::chrono::steady_clock::time_point now) {
        // 1. Перевірка таймерів підозри
        for (auto& [id, m] : members_) {
            if (m.status == MemberStatus::Suspect) {
                if (now - m.state_change_time >= suspect_timeout_) {
                    m.status = MemberStatus::Dead;
                    m.state_change_time = now;
                    std::cout << "[Node " << self_id_ << "] Вузол " << id 
                              << " не спростував підозру -> СТАТУС DEAD\n";
                }
            }
        }

        // 2. Перевірка активного зонда
        if (active_probe_.has_value()) {
            auto elapsed = now - active_probe_->start_time;
            if (!active_probe_->ping_req_sent && elapsed >= ping_timeout_) {
                active_probe_->ping_req_sent = true;
                std::cout << "[Node " << self_id_ << "] Прямий таймаут до " 
                          << active_probe_->target_id << " -> Запуск непрямого Ping-Req\n";
            } else if (active_probe_->ping_req_sent && elapsed >= (ping_timeout_ * 2)) {
                uint32_t target_id = active_probe_->target_id;
                uint32_t inc = members_.at(target_id).incarnation;
                apply_update(target_id, MemberStatus::Suspect, inc, now);
                std::cout << "[Node " << self_id_ << "] Непрямий таймаут -> Вузол " 
                          << target_id << " переведено у стан SUSPECT\n";
                active_probe_.reset();
            }
        }
    }

private:
    struct ProbeState {
        uint32_t target_id;
        std::chrono::steady_clock::time_point start_time;
        bool ping_req_sent{false};
    };

    uint32_t self_id_;
    uint32_t self_incarnation_{0};
    Milliseconds ping_timeout_;
    Milliseconds suspect_timeout_;
    size_t k_helpers_;
    
    std::unordered_map<uint32_t, Member> members_;
    std::optional<ProbeState> active_probe_;
    std::mt19937 rng_;
};

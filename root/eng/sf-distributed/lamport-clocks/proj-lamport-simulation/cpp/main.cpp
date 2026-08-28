#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <algorithm>
#include <cstdint>
#include <cassert>
#include <memory>
#include <format>

enum class EventType {
    Local,
    Send,
    Recv
};

struct EventRecord {
    uint64_t logical_time;
    uint32_t process_id;
    uint32_t event_id;
    EventType type;
    uint32_t related_msg_id;
    std::string description;

    auto operator<=>(const EventRecord& other) const = default;
};

struct NetworkMessage {
    uint32_t msg_id;
    uint32_t sender_pid;
    uint32_t receiver_pid;
    uint64_t send_timestamp;
    std::string payload;
};

class Node {
public:
    explicit Node(uint32_t pid, std::vector<EventRecord>& global_log, uint32_t& msg_seq)
        : pid_(pid), clock_(0), event_counter_(0), log_(global_log), msg_sequence_(msg_seq) {}

    void execute_local(std::string_view action) {
        ++clock_;
        log_event(EventType::Local, 0, std::string(action));
    }

    NetworkMessage send_message(uint32_t receiver_pid, std::string_view payload) {
        ++clock_;
        NetworkMessage msg{
            .msg_id = ++msg_sequence_,
            .sender_pid = pid_,
            .receiver_pid = receiver_pid,
            .send_timestamp = clock_,
            .payload = std::string(payload)
        };

        log_event(EventType::Send, msg.msg_id,
                  std::format("Send msg#{} to Node {}", msg.msg_id, receiver_pid));
        return msg;
    }

    void receive_message(const NetworkMessage& msg) {
        assert(msg.receiver_pid == pid_);
        uint64_t old_clock = clock_;
        clock_ = std::max(old_clock, msg.send_timestamp) + 1;

        log_event(EventType::Recv, msg.msg_id,
                  std::format("Recv msg#{} from Node {} (prev={}, msg_ts={})",
                              msg.msg_id, msg.sender_pid, old_clock, msg.send_timestamp));
    }

    [[nodiscard]] uint32_t pid() const noexcept { return pid_; }
    [[nodiscard]] uint64_t clock() const noexcept { return clock_; }

private:
    void log_event(EventType type, uint32_t msg_id, std::string desc) {
        log_.push_back(EventRecord{
            .logical_time = clock_,
            .process_id = pid_,
            .event_id = ++event_counter_,
            .type = type,
            .related_msg_id = msg_id,
            .description = std::move(desc)
        });
    }

    uint32_t pid_;
    uint64_t clock_;
    uint32_t event_counter_;
    std::vector<EventRecord>& log_;
    uint32_t& msg_sequence_;
};

void verify_causality(const std::vector<EventRecord>& log) {
    std::cout << "=== Перевірка причинних інваріантів Лампорта (C++) ===\n";
    for (const auto& recv_ev : log) {
        if (recv_ev.type != EventType::Recv) continue;

        auto it = std::find_if(log.begin(), log.end(), [&](const EventRecord& send_ev) {
            return send_ev.type == EventType::Send && send_ev.related_msg_id == recv_ev.related_msg_id;
        });

        assert(it != log.end() && "Подія відправлення обов'язково присутня");
        assert(recv_ev.logical_time > it->logical_time && "L(recv) > L(send)");
        std::cout << std::format("[OK] Msg #{}: Send (L={}) -> Recv (L={})\n",
                                 recv_ev.related_msg_id, it->logical_time, recv_ev.logical_time);
    }
}

int main() {
    std::vector<EventRecord> global_log;
    uint32_t msg_sequence = 0;

    Node node_a(1, global_log, msg_sequence);
    Node node_b(2, global_log, msg_sequence);
    Node node_c(3, global_log, msg_sequence);

    // 1. Вузол A робить дію та надсилає повідомлення B
    node_a.execute_local("A: ініціалізація транзакції");
    NetworkMessage msg1 = node_a.send_message(2, "Запит на списання");

    // 2. Вузол B виконує власну паралельну дію
    node_b.execute_local("B: фонове оновлення індексу");

    // 3. Вузол B отримує повідомлення від A
    node_b.receive_message(msg1);

    // 4. Вузол B надсилає повідомлення до C
    NetworkMessage msg2 = node_b.send_message(3, "Підтвердження переказу");

    // 5. Вузол C опрацьовує ланцюжок дій
    node_c.execute_local("C: підготовка буфера");
    node_c.execute_local("C: перевірка сертифіката");
    node_c.receive_message(msg2);
    node_c.execute_local("C: фіксація в журналі");

    // Перевірка інваріантів
    verify_causality(global_log);

    // Сортування у тотальний порядок за (logical_time, process_id, event_id)
    std::sort(global_log.begin(), global_log.end(), [](const EventRecord& a, const EventRecord& b) {
        if (a.logical_time != b.logical_time) return a.logical_time < b.logical_time;
        if (a.process_id != b.process_id) return a.process_id < b.process_id;
        return a.event_id < b.event_id;
    });

    std::cout << "\n=== Глобальний журнал подій (Тотальний порядок за (L, PID)) ===\n";
    for (size_t i = 0; i < global_log.size(); ++i) {
        const auto& r = global_log[i];
        std::cout << std::format("Крок {:2}: (L={:2}, PID={}) -> {}\n",
                                 i + 1, r.logical_time, r.process_id, r.description);
    }
    return 0;
}

#include <iostream>
#include <vector>
#include <queue>
#include <array>
#include <memory>
#include <cassert>

constexpr std::size_t NodeCount = 3;

enum class MessageType {
    Transfer,
    Marker
};

struct Message {
    MessageType type{MessageType::Transfer};
    std::size_t from{0};
    std::size_t to{0};
    int amount{0};
};

class Node {
public:
    explicit Node(std::size_t id, int initial_balance)
        : id_(id), balance_(initial_balance) {
        channel_recording_.fill(false);
        marker_received_.fill(false);
        recorded_channels_.fill(0);
    }

    [[nodiscard]] std::size_t id() const noexcept { return id_; }
    [[nodiscard]] int balance() const noexcept { return balance_; }
    [[nodiscard]] bool snapshot_taken() const noexcept { return snapshot_taken_; }
    [[nodiscard]] int recorded_balance() const noexcept { return recorded_balance_; }
    [[nodiscard]] int recorded_channel(std::size_t from) const noexcept { return recorded_channels_[from]; }

    void deduct(int amount) {
        assert(balance_ >= amount);
        balance_ -= amount;
    }

    void add(int amount) {
        balance_ += amount;
    }

    void initiate_snapshot(std::vector<Message>& outgoing_markers) {
        snapshot_taken_ = true;
        recorded_balance_ = balance_;

        for (std::size_t src = 0; src < NodeCount; ++src) {
            if (src != id_) {
                channel_recording_[src] = true;
                marker_received_[src] = false;
            }
        }
        create_markers(outgoing_markers);
    }

    void handle_marker(std::size_t from, std::vector<Message>& outgoing_markers) {
        if (!snapshot_taken_) {
            snapshot_taken_ = true;
            recorded_balance_ = balance_;
            marker_received_[from] = true;
            channel_recording_[from] = false;
            recorded_channels_[from] = 0;

            for (std::size_t src = 0; src < NodeCount; ++src) {
                if (src != id_ && src != from) {
                    channel_recording_[src] = true;
                    marker_received_[src] = false;
                }
            }
            create_markers(outgoing_markers);
        } else {
            marker_received_[from] = true;
            channel_recording_[from] = false;
        }
    }

    void handle_transfer(std::size_t from, int amount) {
        balance_ += amount;
        if (channel_recording_[from]) {
            recorded_channels_[from] += amount;
        }
    }

private:
    void create_markers(std::vector<Message>& out) {
        for (std::size_t dst = 0; dst < NodeCount; ++dst) {
            if (dst != id_) {
                out.push_back({MessageType::Marker, id_, dst, 0});
            }
        }
    }

    std::size_t id_;
    int balance_;
    bool snapshot_taken_{false};
    int recorded_balance_{0};
    std::array<bool, NodeCount> channel_recording_{};
    std::array<bool, NodeCount> marker_received_{};
    std::array<int, NodeCount> recorded_channels_{};
};

class DistributedSystem {
public:
    explicit DistributedSystem(const std::array<int, NodeCount>& initial_balances) {
        for (std::size_t i = 0; i < NodeCount; ++i) {
            nodes_.push_back(std::make_unique<Node>(i, initial_balances[i]));
        }
    }

    void send_money(std::size_t from, std::size_t to, int amount) {
        nodes_[from]->deduct(amount);
        channels_[from][to].push({MessageType::Transfer, from, to, amount});
    }

    void start_snapshot(std::size_t initiator) {
        std::vector<Message> markers;
        nodes_[initiator]->initiate_snapshot(markers);
        for (const auto& m : markers) {
            channels_[m.from][m.to].push(m);
        }
    }

    void step(std::size_t from, std::size_t to) {
        if (channels_[from][to].empty()) return;
        auto msg = channels_[from][to].front();
        channels_[from][to].pop();

        if (msg.type == MessageType::Marker) {
            std::vector<Message> markers;
            nodes_[to]->handle_marker(from, markers);
            for (const auto& m : markers) {
                channels_[m.from][m.to].push(m);
            }
        } else {
            nodes_[to]->handle_transfer(from, msg.amount);
        }
    }

    void print_snapshot_report() const {
        int node_total = 0;
        int channel_total = 0;

        std::cout << "\n=== Звіт узгодженого знімка (C++) ===\n";
        for (std::size_t i = 0; i < NodeCount; ++i) {
            std::cout << "Вузол P" << i << ": стан = " << nodes_[i]->recorded_balance() << " грн\n";
            node_total += nodes_[i]->recorded_balance();

            for (std::size_t j = 0; j < NodeCount; ++j) {
                if (i != j && nodes_[i]->recorded_channel(j) > 0) {
                    std::cout << "  Канал C_" << j << i << " (в польоті) = " 
                              << nodes_[i]->recorded_channel(j) << " грн\n";
                    channel_total += nodes_[i]->recorded_channel(j);
                }
            }
        }

        int total = node_total + channel_total;
        std::cout << "Сума станів вузлів: " << node_total << " грн\n";
        std::cout << "Сума станів каналів: " << channel_total << " грн\n";
        std::cout << "Загальна сума знімка: " << total << " грн\n";
        std::cout << "Інваріант збереження: " << (total == 1000 ? "ЗБЕРЕЖЕНО" : "ПОРУШЕНО") << "\n";
    }

private:
    std::vector<std::unique_ptr<Node>> nodes_;
    std::array<std::array<std::queue<Message>, NodeCount>, NodeCount> channels_;
};

int main() {
    DistributedSystem system({500, 300, 200});

    system.send_money(0, 1, 100);
    system.start_snapshot(0);
    system.send_money(0, 1, 50);

    system.step(0, 1); // 100 грн отримано P1
    system.step(0, 1); // Маркер від P0 отримано P1
    system.step(0, 2); // Маркер від P0 отримано P2
    system.step(1, 2); // Маркер від P1 отримано P2
    system.step(1, 0); // Маркер від P1 отримано P0
    system.step(2, 0); // Маркер від P2 отримано P0
    system.step(2, 1); // Маркер від P2 отримано P1
    system.step(0, 1); // 50 грн отримано P1 після знімка

    system.print_snapshot_report();
    return 0;
}

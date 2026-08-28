#include <iostream>
#include <vector>
#include <queue>
#include <random>
#include <optional>
#include <algorithm>

enum class MsgType {
    Propose,
    Ratify
};

struct Message {
    int from;
    int to;
    int round;
    MsgType type;
    std::optional<int> value; // nullopt відповідає невизначеності '?'
    int deliver_tick;
};

struct MessageComparator {
    bool operator()(const Message& a, const Message& b) const {
        return a.deliver_tick > b.deliver_tick; // Мін-куча за часом доставки
    }
};

class Node {
public:
    int id;
    int current_round = 1;
    int preference;
    std::optional<int> decided_value = std::nullopt;
    bool is_crashed = false;

    int propose_votes[2] = {0, 0};
    int propose_count = 0;
    int ratify_votes[2] = {0, 0};
    int ratify_count = 0;
    bool phase1_done = false;

    Node(int node_id, int initial_pref, bool crashed = false)
        : id(node_id), preference(initial_pref), is_crashed(crashed) {}

    bool has_decided() const {
        return decided_value.has_value();
    }

    void reset_round_buffers() {
        propose_votes[0] = propose_votes[1] = 0;
        propose_count = 0;
        ratify_votes[0] = ratify_votes[1] = 0;
        ratify_count = 0;
        phase1_done = false;
    }
};

class NetworkSimulator {
public:
    int total_nodes;
    int max_faults;
    int quorum_size;
    std::vector<Node> nodes;
    std::priority_queue<Message, std::vector<Message>, MessageComparator> message_queue;
    std::mt19937 rng{std::random_device{}()};

    NetworkSimulator(int n, int f)
        : total_nodes(n), max_faults(f), quorum_size(n - f) {
        for (int i = 0; i < n; ++i) {
            nodes.emplace_back(i, i % 2, i == 0 /* Вузол 0 зламаний */);
        }
    }

    void broadcast(int from, int round, MsgType type, std::optional<int> val, int current_tick) {
        std::uniform_int_distribution<int> delay_dist(1, 5);
        for (int dest = 0; dest < total_nodes; ++dest) {
            message_queue.push(Message{
                from,
                dest,
                round,
                type,
                val,
                current_tick + delay_dist(rng)
            });
        }
    }

    void run() {
        int tick = 0;
        // Початковий раунд
        for (const auto& node : nodes) {
            if (!node.is_crashed) {
                broadcast(node.id, 1, MsgType::Propose, node.preference, tick);
            }
        }

        std::uniform_int_distribution<int> coin_dist(0, 1);

        while (tick < 1000 && !all_working_decided()) {
            tick++;
            while (!message_queue.empty() && message_queue.top().deliver_tick <= tick) {
                Message msg = message_queue.top();
                message_queue.pop();

                Node& node = nodes[msg.to];
                if (node.is_crashed || msg.round != node.current_round) {
                    continue;
                }

                if (msg.type == MsgType::Propose && !node.phase1_done) {
                    if (msg.value.has_value()) {
                        node.propose_votes[*msg.value]++;
                    }
                    node.propose_count++;

                    if (node.propose_count >= quorum_size) {
                        node.phase1_done = true;
                        std::optional<int> ratify_val = std::nullopt;
                        if (node.propose_votes[0] > total_nodes / 2) {
                            ratify_val = 0;
                        } else if (node.propose_votes[1] > total_nodes / 2) {
                            ratify_val = 1;
                        }
                        broadcast(node.id, node.current_round, MsgType::Ratify, ratify_val, tick);
                    }
                } else if (msg.type == MsgType::Ratify && node.phase1_done) {
                    if (msg.value.has_value()) {
                        node.ratify_votes[*msg.value]++;
                    }
                    node.ratify_count++;

                    if (node.ratify_count >= quorum_size) {
                        if (node.ratify_votes[0] >= max_faults + 1) {
                            node.decided_value = 0;
                            node.preference = 0;
                        } else if (node.ratify_votes[1] >= max_faults + 1) {
                            node.decided_value = 1;
                            node.preference = 1;
                        } else if (node.ratify_votes[0] > 0) {
                            node.preference = 0;
                        } else if (node.ratify_votes[1] > 0) {
                            node.preference = 1;
                        } else {
                            // Підкидання монети (Coin Toss)
                            node.preference = coin_dist(rng);
                        }

                        node.current_round++;
                        node.reset_round_buffers();
                        broadcast(node.id, node.current_round, MsgType::Propose, node.preference, tick);
                    }
                }
            }
        }

        print_results(tick);
    }

    bool all_working_decided() const {
        return std::all_of(nodes.begin(), nodes.end(), [](const Node& node) {
            return node.is_crashed || node.has_decided();
        });
    }

    void print_results(int total_ticks) const {
        std::cout << "Результати C++ симуляції консенсусу Бена-Ора (тактів: " << total_ticks << "):\n";
        for (const auto& node : nodes) {
            if (node.is_crashed) {
                std::cout << "  Вузол " << node.id << ": [ЗБІЙ/CRASHED]\n";
            } else {
                std::cout << "  Вузол " << node.id << ": Рішення = "
                          << (node.decided_value ? std::to_string(*node.decided_value) : "немає")
                          << " (Раунд = " << node.current_round << ")\n";
            }
        }
    }
};

int main() {
    NetworkSimulator sim(5, 2);
    sim.run();
    return 0;
}

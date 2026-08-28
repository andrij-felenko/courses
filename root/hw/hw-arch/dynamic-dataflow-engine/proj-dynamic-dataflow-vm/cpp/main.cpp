#include <iostream>
#include <vector>
#include <array>
#include <queue>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <atomic>
#include <optional>
#include <span>
#include <memory>
#include <chrono>

namespace dataflow {

using FrameId = uint32_t;
using NodeId  = uint16_t;
using Port    = uint8_t;

/* ── 1. Тип токена ── */
struct Token {
    FrameId frame_id{0};
    NodeId  node_id{0};
    Port    port{0};
    int64_t value{0};
};

/* ── 2. Опис вузлів графа ── */
enum class Opcode : uint8_t {
    Add,
    Sub,
    Mul,
    Output
};

struct Arc {
    NodeId dest_node{0};
    Port   dest_port{0};
};

struct Node {
    Opcode           opcode{Opcode::Add};
    bool             is_binary{true};
    uint8_t          slot_index{0};
    std::vector<Arc> successors;
};

/* ── 3. Explicit Token Store (ETS) Кадр ── */
struct EtsSlot {
    std::atomic<bool> has_value{false};
    int64_t           value{0};
};

class ActivationFrame {
public:
    static constexpr size_t kMaxSlots = 16;

    ActivationFrame() = default;

    void reset() noexcept {
        for (auto& s : slots_) {
            s.has_value.store(false, std::memory_order_relaxed);
            s.value = 0;
        }
    }

    /* Атомарне зіставлення токена в слоті */
    std::optional<std::pair<int64_t, int64_t>> match(uint8_t slot_idx, Port port, int64_t incoming_val) noexcept {
        auto& slot = slots_[slot_idx];
        bool expected = false;

        /* Перший операнд: захоплення слота через CAS */
        if (slot.has_value.compare_exchange_strong(expected, true, std::memory_order_acq_rel)) {
            slot.value = incoming_val;
            return std::nullopt;
        }

        /* Другий операнд: читання значення та атомарне звільнення слота */
        int64_t stored_val = slot.value;
        slot.has_value.store(false, std::memory_order_release);

        int64_t left  = (port == 0) ? incoming_val : stored_val;
        int64_t right = (port == 0) ? stored_val   : incoming_val;
        return std::make_pair(left, right);
    }

private:
    std::array<EtsSlot, kMaxSlots> slots_{};
};

/* ── 4. Потокобезпечна черга токенів ── */
class TokenQueue {
public:
    void push(Token tok) {
        {
            std::lock_guard lock(mtx_);
            queue_.push(tok);
        }
        cv_.notify_one();
    }

    bool pop(Token& out_tok) {
        std::unique_lock lock(mtx_);
        cv_.wait(lock, [this]() { return !queue_.empty() || shutdown_; });

        if (queue_.empty() && shutdown_) {
            return false;
        }

        out_tok = queue_.front();
        queue_.pop();
        return true;
    }

    void shutdown() noexcept {
        {
            std::lock_guard lock(mtx_);
            shutdown_ = true;
        }
        cv_.notify_all();
    }

private:
    std::queue<Token>       queue_;
    std::mutex              mtx_;
    std::condition_variable cv_;
    bool                    shutdown_{false};
};

/* ── 5. Рушій Dataflow ── */
class Engine {
public:
    explicit Engine(std::vector<Node> graph, size_t num_workers = 4)
        : graph_(std::move(graph)) {
        frames_.resize(128);
        for (size_t i = 0; i < num_workers; ++i) {
            workers_.emplace_back([this]() { worker_loop(); });
        }
    }

    ~Engine() {
        queue_.shutdown();
        for (auto& w : workers_) {
            if (w.joinable()) {
                w.join();
            }
        }
    }

    Engine(const Engine&) = delete;
    Engine& operator=(const Engine&) = delete;

    FrameId allocate_frame() noexcept {
        size_t id = next_frame_id_.fetch_add(1, std::memory_order_relaxed);
        frames_[id % frames_.size()].reset();
        return static_cast<FrameId>(id);
    }

    void emit(Token tok) {
        queue_.push(tok);
    }

    [[nodiscard]] int64_t result() const noexcept {
        return total_sum_.load(std::memory_order_relaxed);
    }

private:
    void execute(FrameId fid, const Node& node, int64_t v1, int64_t v2) {
        int64_t res = 0;
        switch (node.opcode) {
            case Opcode::Add: res = v1 + v2; break;
            case Opcode::Sub: res = v1 - v2; break;
            case Opcode::Mul: res = v1 * v2; break;
            case Opcode::Output:
                total_sum_.fetch_add(v1, std::memory_order_relaxed);
                std::cout << "[C++ Dataflow] Результат кадру " << fid << " = " << v1 << "\n";
                return;
        }

        for (const auto& arc : node.successors) {
            queue_.push(Token{fid, arc.dest_node, arc.dest_port, res});
        }
    }

    void worker_loop() {
        Token tok;
        while (queue_.pop(tok)) {
            const auto& node = graph_[tok.node_id];

            if (!node.is_binary) {
                execute(tok.frame_id, node, tok.value, 0);
            } else {
                auto& frame = frames_[tok.frame_id % frames_.size()];
                if (auto operands = frame.match(node.slot_index, tok.port, tok.value)) {
                    execute(tok.frame_id, node, operands->first, operands->second);
                }
            }
        }
    }

    std::vector<Node>            graph_;
    std::vector<ActivationFrame> frames_;
    TokenQueue                   queue_;
    std::vector<std::thread>     workers_;
    std::atomic<size_t>          next_frame_id_{0};
    std::atomic<int64_t>         total_sum_{0};
};

} // namespace dataflow

int main() {
    using namespace dataflow;

    /* Побудова графа виразу: (a + b) * (c - d) */
    std::vector<Node> graph{
        /* Вузол 0: ADD (слот 0) -> відправляє у Вузол 2, Порт 0 */
        Node{Opcode::Add, true, 0, {{2, 0}}},
        /* Вузол 1: SUB (слот 1) -> відправляє у Вузол 2, Порт 1 */
        Node{Opcode::Sub, true, 1, {{2, 1}}},
        /* Вузол 2: MUL (слот 2) -> відправляє у Вузол 3, Порт 0 */
        Node{Opcode::Mul, true, 2, {{3, 0}}},
        /* Вузол 3: OUTPUT (термінальний вузол) */
        Node{Opcode::Output, false, 0, {}}
    };

    Engine engine(std::move(graph), 4);

    /* Екземпляр 1: (10 + 20) * (50 - 15) = 30 * 35 = 1050 */
    auto frame1 = engine.allocate_frame();
    engine.emit(Token{frame1, 0, 0, 10});
    engine.emit(Token{frame1, 0, 1, 20});
    engine.emit(Token{frame1, 1, 0, 50});
    engine.emit(Token{frame1, 1, 1, 15});

    /* Екземпляр 2: (100 + 200) * (40 - 30) = 300 * 10 = 3000 */
    auto frame2 = engine.allocate_frame();
    engine.emit(Token{frame2, 0, 0, 100});
    engine.emit(Token{frame2, 0, 1, 200});
    engine.emit(Token{frame2, 1, 0, 40});
    engine.emit(Token{frame2, 1, 1, 30});

    std::this_thread::sleep_for(std::chrono::milliseconds(100));

    std::cout << "Сумарний результат усіх паралельних графів: " << engine.result() << "\n";
    return 0;
}

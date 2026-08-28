#include <atomic>

struct NodeBase { virtual ~NodeBase() = default; };
struct WorkerNode : NodeBase { int worker_id{0}; };

std::atomic<NodeBase*> global_head{nullptr};

void process_worker() {
    // 1. Атомарне завантаження з бар'єром пам'яті acquire
    NodeBase* raw_ptr = global_head.load(std::memory_order_acquire);

    // 2. Безпечне приведення після атомарного читання
    if (auto* worker = dynamic_cast<WorkerNode*>(raw_ptr)) {
        // Робота з WorkerNode
    }
}

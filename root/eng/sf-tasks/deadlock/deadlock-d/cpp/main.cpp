#include <mutex>
#include <utility>

struct Node {
    int value{0};
    mutable std::mutex mtx;
};

// БЕЗПЕЧНО: C++17 std::scoped_lock гарантує відсутність дедлоку для будь-якої кількості замків
void swap_nodes_safe(Node& a, Node& b) {
    if (&a == &b) {
        return; // Самовтягнення не потребує блокувань
    }

    // std::scoped_lock автоматично впорядковує захоплення замків
    // та звільняє їх у деструкторі за принципом RAII
    std::scoped_lock lock(a.mtx, b.mtx);

    std::swap(a.value, b.value);
}

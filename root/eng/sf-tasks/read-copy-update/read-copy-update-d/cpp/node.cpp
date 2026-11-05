#include <atomic>
#include <memory>
#include <string>

struct Node {
    int id;
    std::string name;
};

class RcuContainer {
private:
    std::atomic<Node*> global_node_{nullptr};

public:
    void update_node(int new_id, const std::string& new_name) {
        // 1. Read: зчитуємо актуальний вказівник
        Node* old_node = global_node_.load(std::memory_order_relaxed);

        // 2. Copy: створюємо нову копію об'єкта
        Node* new_node = new Node();
        if (old_node) {
            *new_node = *old_node;
        }

        // 3. Update: безпечно змінюємо копію
        new_node->id = new_id;
        new_node->name = new_name;

        // 4. Publish (Atomic Swap): атомарно підміняємо вказівник із семантикою release
        global_node_.store(new_node, std::memory_order_release);

        // КРИТИЧНИЙ МОМЕНТ: Вивільнення пам'яті (delete old_node) НЕМОЖЛИВЕ негайно!
        // Активні читачі все ще опрацьовують old_node у своїх секціях.
        // Очищення вимагає витримування періоду відстрочки (grace period).
    }
};

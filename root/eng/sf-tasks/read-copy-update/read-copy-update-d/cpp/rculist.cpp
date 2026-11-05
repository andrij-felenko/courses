#include <iostream>
#include <atomic>
#include <memory>
#include <thread>
#include <vector>

// Ідіоматична реалізація RCU-списку для C++11/17/20
template <typename T>
class RcuList {
private:
    struct Node {
        T data;
        std::atomic<Node*> next{nullptr};

        Node(const T& val) : data(val) {}
    };

    std::atomic<Node*> head_{nullptr};

public:
    ~RcuList() {
        Node* curr = head_.load(std::memory_order_relaxed);
        while (curr) {
            Node* next = curr->next.load(std::memory_order_relaxed);
            delete curr;
            curr = next;
        }
    }

    // Безблокове читання списку із семантикою memory_order_acquire
    template <typename Predicate>
    bool find(Predicate pred, T& result) const {
        Node* curr = head_.load(std::memory_order_acquire); // RCU dereference
        while (curr != nullptr) {
            if (pred(curr->data)) {
                result = curr->data;
                return true;
            }
            curr = curr->next.load(std::memory_order_acquire);
        }
        return false;
    }

    // Атомарна публікація нового вузла
    void insert(const T& val) {
        auto* new_node = new Node(val);
        Node* old_head = head_.load(std::memory_order_relaxed);
        do {
            new_node->next.store(old_head, std::memory_order_relaxed);
        } while (!head_.compare_exchange_weak(
                    old_head, new_node,
                    std::memory_order_release, // RCU assign pointer
                    std::memory_order_relaxed));
    }

    // Синхронне видалення з імітацією періоду відстрочки
    bool remove(const T& val) {
        std::atomic<Node*>* pred = &head_;
        Node* curr = head_.load(std::memory_order_relaxed);

        while (curr != nullptr) {
            if (curr->data == val) {
                Node* next_node = curr->next.load(std::memory_order_relaxed);
                // Всі читачі бачать від'єднання атомарно
                pred->store(next_node, std::memory_order_release);

                // Очікування завершення періоду відстрочки (симуляція synchronize_rcu)
                std::this_thread::yield();

                // Безпечне вивільнення від'єднаного вузла
                delete curr;
                return true;
            }
            pred = &(curr->next);
            curr = curr->next.load(std::memory_order_relaxed);
        }
        return false;
    }
};

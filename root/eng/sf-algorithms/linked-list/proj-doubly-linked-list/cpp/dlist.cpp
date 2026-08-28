// dlist.cpp — Ідіоматичний RAII-шаблон двохзв'язаного списка C++20
#include <iostream>
#include <memory>
#include <utility>
#include <cstddef>
#include <string>

template <typename T>
class DoublyLinkedList {
private:
    struct Node {
        T data;
        Node* prev{nullptr};
        Node* next{nullptr};

        template <typename... Args>
        explicit Node(Args&&... args) 
            : data(std::forward<Args>(args)...) {}
    };

    Node sentinel_;
    std::size_t size_{0};

    void insert_between(Node* new_node, Node* prev_node, Node* next_node) noexcept {
        new_node->prev = prev_node;
        new_node->next = next_node;
        prev_node->next = new_node;
        next_node->prev = new_node;
    }

    void unlink(Node* node) noexcept {
        node->prev->next = node->next;
        node->next->prev = node->prev;
    }

public:
    DoublyLinkedList() noexcept {
        sentinel_.next = &sentinel_;
        sentinel_.prev = &sentinel_;
    }

    ~DoublyLinkedList() noexcept {
        clear();
    }

    // Заборона копіювання для простоти управління ресурсами
    DoublyLinkedList(const DoublyLinkedList&) = delete;
    DoublyLinkedList& operator=(const DoublyLinkedList&) = delete;

    // Переміщення списку
    DoublyLinkedList(DoublyLinkedList&& other) noexcept : DoublyLinkedList() {
        if (!other.empty()) {
            sentinel_.next = other.sentinel_.next;
            sentinel_.prev = other.sentinel_.prev;
            sentinel_.next->prev = &sentinel_;
            sentinel_.prev->next = &sentinel_;
            size_ = std::exchange(other.size_, 0);
            other.sentinel_.next = &other.sentinel_;
            other.sentinel_.prev = &other.sentinel_;
        }
    }

    [[nodiscard]] bool empty() const noexcept {
        return sentinel_.next == &sentinel_;
    }

    [[nodiscard]] std::size_t size() const noexcept {
        return size_;
    }

    template <typename... Args>
    void emplace_back(Args&&... args) {
        auto* new_node = new Node(std::forward<Args>(args)...);
        insert_between(new_node, sentinel_.prev, &sentinel_);
        ++size_;
    }

    void push_back(const T& value) { emplace_back(value); }
    void push_back(T&& value) { emplace_back(std::move(value)); }

    bool pop_front(T& out_value) {
        if (empty()) return false;
        Node* first = sentinel_.next;
        out_value = std::move(first->data);
        unlink(first);
        delete first;
        --size_;
        return true;
    }

    void clear() noexcept {
        Node* current = sentinel_.next;
        while (current != &sentinel_) {
            Node* next_node = current->next;
            delete current;
            current = next_node;
        }
        sentinel_.next = &sentinel_;
        sentinel_.prev = &sentinel_;
        size_ = 0;
    }
};

int main() {
    DoublyLinkedList<std::string> list;
    list.push_back("Комірка 1");
    list.push_back("Комірка 2");
    list.emplace_back("Комірка 3");

    std::cout << "Розмір: " << list.size() << "\n";

    std::string item;
    while (list.pop_front(item)) {
        std::cout << "Отримано: " << item << "\n";
    }

    return 0;
}

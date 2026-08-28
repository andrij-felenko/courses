#include <memory>
#include <utility>

template <typename T>
struct Node {
    T value;
    std::unique_ptr<Node<T>> next;

    explicit Node(T val) : value(std::move(val)), next(nullptr) {}
};

/* Ідіоматичне безпечне сортування зв'язного списку з керуванням пам'яттю через RAII */
template <typename T>
std::unique_ptr<Node<T>> sort_linked_list(std::unique_ptr<Node<T>> head) {
    if (!head || !head->next) {
        return head;
    }

    std::unique_ptr<Node<T>> sorted_head = nullptr;

    while (head) {
        /* Відокремлюємо поточний вузол від несортованого списку */
        std::unique_ptr<Node<T>> current = std::move(head);
        head = std::move(current->next);

        /* Вставка на початок відсортованого списку */
        if (!sorted_head || current->value < sorted_head->value) {
            current->next = std::move(sorted_head);
            sorted_head = std::move(current);
        } else {
            /* Пошук точки вставки всередині списку */
            Node<T>* prev = sorted_head.get();
            while (prev->next && !(current->value < prev->next->value)) {
                prev = prev->next.get();
            }
            current->next = std::move(prev->next);
            prev->next = std::move(current);
        }
    }

    return sorted_head;
}

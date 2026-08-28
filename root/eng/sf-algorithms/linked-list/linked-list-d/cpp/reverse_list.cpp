// reverse_list.cpp — Перевертання однозв'язаного списка C++
#include <iostream>
#include <memory>

struct Node {
    int data;
    Node* next{nullptr};
    explicit Node(int val) : data(val) {}
};

Node* reverse_list(Node* head) noexcept {
    Node* prev = nullptr;
    Node* curr = head;

    while (curr != nullptr) {
        Node* next_node = curr->next;
        curr->next = prev;
        prev = curr;
        curr = next_node;
    }

    return prev;
}

#include <iostream>
#include <memory>
#include <utility>

template <typename T>
struct ForwardNode {
    T val;
    std::unique_ptr<ForwardNode<T>> next;

    explicit ForwardNode(T value) : val(std::move(value)), next(nullptr) {}
};

template <typename T>
class ForwardListSort {
public:
    using NodePtr = std::unique_ptr<ForwardNode<T>>;

    static NodePtr sort(NodePtr head) {
        if (!head || !head->next) {
            return head;
        }

        NodePtr mid = split(head);
        NodePtr left = sort(std::move(head));
        NodePtr right = sort(std::move(mid));

        return merge(std::move(left), std::move(right));
    }

private:
    static NodePtr split(NodePtr& head) {
        if (!head || !head->next) {
            return nullptr;
        }

        ForwardNode<T>* slow = head.get();
        ForwardNode<T>* fast = head->next.get();

        while (fast && fast->next) {
            slow = slow->next.get();
            fast = fast->next->next.get();
        }

        NodePtr mid = std::move(slow->next);
        slow->next = nullptr;
        return mid;
    }

    static NodePtr merge(NodePtr l1, NodePtr l2) {
        NodePtr dummy = std::make_unique<ForwardNode<T>>(T{});
        ForwardNode<T>* tail = dummy.get();

        while (l1 && l2) {
            if (l1->val <= l2->val) {
                NodePtr next_l1 = std::move(l1->next);
                tail->next = std::move(l1);
                l1 = std::move(next_l1);
            } else {
                NodePtr next_l2 = std::move(l2->next);
                tail->next = std::move(l2);
                l2 = std::move(next_l2);
            }
            tail = tail->next.get();
        }

        tail->next = l1 ? std::move(l1) : std::move(l2);
        return std::move(dummy->next);
    }
};

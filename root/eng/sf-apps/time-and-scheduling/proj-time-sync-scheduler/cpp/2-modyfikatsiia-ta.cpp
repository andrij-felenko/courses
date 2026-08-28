/* БЕЗПЕЧНИЙ ІНВАРІАНТ: */
Node* curr = slot.head;
slot.head = nullptr; /* Слот миттєво стає порожнім */

while (curr != nullptr) {
    Node* next = curr->next;
    curr->next = nullptr;
    curr->prev = nullptr;
    curr->is_active = false;

    if (curr->callback) {
        curr->callback();
    }
    curr = next;
}

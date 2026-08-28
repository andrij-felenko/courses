/* БЕЗПЕЧНИЙ ІНВАРІАНТ: */
timer_node_t *curr = slot->head;
slot->head = NULL; /* Слот миттєво стає порожнім */

while (curr != NULL) {
    timer_node_t *next = curr->next;
    curr->next = NULL;
    curr->prev = NULL;
    curr->is_active = false;

    curr->callback(curr, curr->user_data);
    curr = next;
}

/* C: повна перевірка інваріантів списку */
bool skiplist_validate(const SkipList* list) {
    if (!list || !list->head) return false;
    size_t count = 0;
    SkipNode* curr = list->head->forward[0];
    int prev_key = -2147483648; /* INT_MIN */

    /* Перевірка нульового рівня */
    while (curr != NULL) {
        if (count > 0 && curr->key <= prev_key) return false;
        prev_key = curr->key;
        count++;
        curr = curr->forward[0];
    }
    if (count != list->size) return false;

    /* Перевірка вищих рівнів */
    for (int i = 1; i < list->level; i++) {
        curr = list->head->forward[i];
        while (curr != NULL) {
            if (curr->level <= i) return false;
            if (curr->forward[i] != NULL && curr->forward[i]->key <= curr->key) return false;
            curr = curr->forward[i];
        }
    }
    return true;
}

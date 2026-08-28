// C++: метод валідації інваріантів у класі SkipList
bool validate() const {
    if (!head_) return false;
    size_t count = 0;
    Node* curr = head_->forward[0];

    while (curr != nullptr) {
        if (curr->forward[0] != nullptr && !comp_(curr->key, curr->forward[0]->key)) {
            return false;
        }
        count++;
        curr = curr->forward[0];
    }
    if (count != element_count_) return false;

    for (size_t i = 1; i < current_level_; ++i) {
        curr = head_->forward[i];
        while (curr != nullptr) {
            if (curr->forward[i] != nullptr && !comp_(curr->key, curr->forward[i]->key)) {
                return false;
            }
            curr = curr->forward[i];
        }
    }
    return true;
}

template <typename T, typename Compare>
void TimSort<T, Compare>::merge_collapse(std::span<T> data) {
    while (stack_size_ > 1) {
        size_t n = stack_size_ - 2;

        if ((n >= 1 && stack_[n - 1].len <= stack_[n].len + stack_[n + 1].len) ||
            (n >= 2 && stack_[n - 2].len <= stack_[n - 1].len + stack_[n].len)) {
            if (stack_[n - 1].len < stack_[n + 1].len) {
                n--;
            }
            merge_at(data, n);
        } else if (stack_[n].len <= stack_[n + 1].len) {
            merge_at(data, n);
        } else {
            break;
        }
    }
}

template <typename T, typename Compare>
void TimSort<T, Compare>::merge_force_collapse(std::span<T> data) {
    while (stack_size_ > 1) {
        size_t n = stack_size_ - 2;
        if (n > 0 && stack_[n - 1].len < stack_[n + 1].len) {
            n--;
        }
        merge_at(data, n);
    }
}

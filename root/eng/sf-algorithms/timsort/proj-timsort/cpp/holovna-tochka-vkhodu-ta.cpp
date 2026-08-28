template <typename T, typename Compare>
void TimSort<T, Compare>::sort(std::span<T> data) {
    const size_t n = data.size();
    if (n < 2) return;

    size_t minrun = calculate_minrun_impl<T, Compare>(n);
    stack_size_ = 0;
    min_gallop_ = MIN_GALLOP_DEFAULT;

    size_t start = 0;
    while (start < n) {
        size_t run_len = count_and_reverse_run_impl(data, start, comp_);

        if (run_len < minrun) {
            size_t force = std::min(minrun, n - start);
            binary_insertion_sort_impl(data, start, force, run_len, comp_);
            run_len = force;
        }

        stack_[stack_size_++] = Run{ start, run_len };
        merge_collapse(data);
        start += run_len;
    }

    merge_force_collapse(data);
}

struct Item {
    int key;
    int original_index;
};

int main() {
    std::vector<Item> items = {
        {5, 0}, {2, 1}, {8, 2}, {5, 3}, {1, 4}, {5, 5}, {2, 6}, {9, 7}
    };

    TimSort<Item, decltype([](const Item &a, const Item &b) { return a.key < b.key; })> sorter;
    sorter.sort(items);

    std::cout << "Відсортований масив (key, orig_index):\n";
    for (const auto &it : items) {
        std::cout << "{" << it.key << ", " << it.original_index << "} ";
    }
    std::cout << "\n";

    bool stable = true;
    for (size_t i = 1; i < items.size(); ++i) {
        if (items[i].key < items[i - 1].key) {
            std::cerr << "Помилка порядку ключів!\n";
            return 1;
        }
        if (items[i].key == items[i - 1].key && items[i].original_index < items[i - 1].original_index) {
            stable = false;
        }
    }

    std::cout << "Стійкість сортування: " << (stable ? "ЗБЕРЕЖЕНО (OK)" : "ПОРУШЕНО (ПОМИЛКА)") << "\n";
    return 0;
}

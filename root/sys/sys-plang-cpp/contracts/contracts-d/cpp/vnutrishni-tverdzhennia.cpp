void binary_search_step(std::span<const int> sorted_data, int target) {
    std::size_t low = 0;
    std::size_t high = sorted_data.size();

    while (low < high) {
        std::size_t mid = low + (high - low) / 2;

        contract_assert [valid_midpoint]: mid >= low && mid < high;

        if (sorted_data[mid] < target) {
            low = mid + 1;
        } else {
            high = mid;
        }
    }
}

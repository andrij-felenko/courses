#include <iostream>
#include <vector>
#include <span>
#include <algorithm>
#include <utility>
#include <functional>
#include <cstddef>
#include <memory>

template <typename T, typename Compare = std::less<T>>
class TimSort {
public:
    static constexpr size_t MIN_GALLOP_DEFAULT = 7;
    static constexpr size_t MAX_STACK_SIZE = 85;

    struct Run {
        size_t start;
        size_t len;
    };

    explicit TimSort(Compare comp = Compare()) 
        : comp_(comp), min_gallop_(MIN_GALLOP_DEFAULT), stack_size_(0) {}

    void sort(std::span<T> data);

private:
    Compare comp_;
    size_t min_gallop_;
    std::vector<T> temp_buf_;
    Run stack_[MAX_STACK_SIZE];
    size_t stack_size_;

    void merge_collapse(std::span<T> data);
    void merge_force_collapse(std::span<T> data);
    void merge_at(std::span<T> data, size_t i);
    void merge_lo(std::span<T> data, size_t base_a, size_t len_a, size_t base_b, size_t len_b);
    void merge_hi(std::span<T> data, size_t base_a, size_t len_a, size_t base_b, size_t len_b);
};

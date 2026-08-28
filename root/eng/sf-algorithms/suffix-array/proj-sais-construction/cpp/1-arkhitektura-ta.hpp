#pragma once
#include <string>
#include <string_view>
#include <vector>
#include <span>
#include <cstdint>
#include <algorithm>

struct SearchResult {
    int left{-1};
    int right{-1};
    int count{0};

    [[nodiscard]] bool found() const noexcept { return count > 0; }
};

class SuffixIndex {
public:
    explicit SuffixIndex(std::string_view text);

    // Заборона небезпечного копіювання масивних буферів, дозволено переміщення (RAII)
    SuffixIndex(const SuffixIndex&) = delete;
    SuffixIndex& operator=(const SuffixIndex&) = delete;
    SuffixIndex(SuffixIndex&&) noexcept = default;
    SuffixIndex& operator=(SuffixIndex&&) noexcept = default;
    ~SuffixIndex() = default;

    [[nodiscard]] SearchResult search(std::string_view pattern) const noexcept;
    [[nodiscard]] int query_lcp(int sa_a, int sa_b) const noexcept;
    [[nodiscard]] std::string_view longest_repeated_substring() const noexcept;
    [[nodiscard]] int64_t count_distinct_substrings() const noexcept;

    [[nodiscard]] std::span<const int> get_sa() const noexcept { return sa_; }
    [[nodiscard]] std::span<const int> get_lcp() const noexcept { return lcp_; }
    [[nodiscard]] std::string_view get_text() const noexcept { return text_; }
    [[nodiscard]] int size() const noexcept { return n_; }

private:
    void build_sa();
    void build_lcp();
    void build_sparse_table();

    std::string text_;
    int n_{0};
    std::vector<int> sa_;
    std::vector<int> rank_;
    std::vector<int> lcp_;
    std::vector<std::vector<int>> st_;
};

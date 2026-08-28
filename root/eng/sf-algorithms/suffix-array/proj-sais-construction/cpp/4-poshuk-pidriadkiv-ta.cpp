SuffixIndex::SuffixIndex(std::string_view text)
    : text_(text), n_(static_cast<int>(text.size())) {
    if (n_ == 0) return;
    sa_.resize(n_);
    rank_.resize(n_);
    lcp_.resize(n_, 0);

    build_sa();
    build_lcp();
    build_sparse_table();
}

SearchResult SuffixIndex::search(std::string_view pattern) const noexcept {
    SearchResult res;
    if (pattern.empty() || n_ == 0) return res;

    int m = static_cast<int>(pattern.size());

    // 1. Нижня межа
    int low = 0, high = n_ - 1;
    int first = -1;
    while (low <= high) {
        int mid = low + (high - low) / 2;
        std::string_view suffix(text_.data() + sa_[mid], std::min(m, n_ - sa_[mid]));
        if (suffix >= pattern) {
            first = mid;
            high = mid - 1;
        } else {
            low = mid + 1;
        }
    }

    if (first == -1) return res;

    std::string_view found_suffix(text_.data() + sa_[first], std::min(m, n_ - sa_[first]));
    if (!found_suffix.starts_with(pattern)) {
        return res;
    }

    // 2. Верхня межа
    low = first;
    high = n_ - 1;
    int last = first;
    while (low <= high) {
        int mid = low + (high - low) / 2;
        std::string_view suffix(text_.data() + sa_[mid], std::min(m, n_ - sa_[mid]));
        if (suffix.starts_with(pattern)) {
            last = mid;
            low = mid + 1;
        } else if (suffix < pattern) {
            low = mid + 1;
        } else {
            high = mid - 1;
        }
    }

    res.left = first;
    res.right = last;
    res.count = last - first + 1;
    return res;
}

std::string_view SuffixIndex::longest_repeated_substring() const noexcept {
    if (n_ <= 1) return {};

    int max_len = 0;
    int best_pos = -1;

    for (int i = 1; i < n_; ++i) {
        if (lcp_[i] > max_len) {
            max_len = lcp_[i];
            best_pos = sa_[i];
        }
    }

    if (best_pos == -1 || max_len == 0) return {};
    return std::string_view(text_.data() + best_pos, max_len);
}

int64_t SuffixIndex::count_distinct_substrings() const noexcept {
    int64_t total = 0;
    for (int i = 0; i < n_; ++i) {
        total += (n_ - sa_[i]) - lcp_[i];
    }
    return total;
}

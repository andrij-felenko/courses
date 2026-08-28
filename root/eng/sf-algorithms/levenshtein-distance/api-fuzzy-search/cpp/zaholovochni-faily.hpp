#pragma once

#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <functional>
#include <expected>

namespace fuzzy {

enum class Status {
    Ok = 0,
    InvalidArg,
    NoMemory,
    NotFound
};

struct SearchOptions {
    int max_distance = 2;
    size_t prefix_freeze_len = 0;
    bool allow_transposition = false;
    size_t max_results = 50;
};

template <typename T = void*>
struct MatchResult {
    std::string word;
    int distance = 0;
    T user_data{};
};

template <typename T = void*>
class FuzzyMatcher {
public:
    FuzzyMatcher();
    ~FuzzyMatcher();

    FuzzyMatcher(const FuzzyMatcher&) = delete;
    FuzzyMatcher& operator=(const FuzzyMatcher&) = delete;
    FuzzyMatcher(FuzzyMatcher&&) noexcept;
    FuzzyMatcher& operator=(FuzzyMatcher&&) noexcept;

    std::expected<void, Status> insert(std::string_view word, T user_data = T{});
    
    [[nodiscard]] std::vector<MatchResult<T>> search(
        std::string_view query, 
        const SearchOptions& options = {}
    ) const;

    [[nodiscard]] size_t size() const noexcept;
    void clear() noexcept;

private:
    struct Impl;
    std::unique_ptr<Impl> pimpl_;
};

} // namespace fuzzy

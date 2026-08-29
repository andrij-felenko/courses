#include "at/urc_table.hpp"

#include <utility>

namespace at {

bool UrcTable::add(std::string_view prefix, UrcHandler handler) noexcept
{
    if (prefix.empty() || !handler || count_ == entry_.size()) {
        return false;
    }
    StaticString<config::kMaxPrefix> stored{prefix};
    if (stored.truncated()) {
        return false;   // обрізаний префікс ловив би не те, що просили
    }

    entry_[count_].prefix = stored;
    entry_[count_].handler = std::move(handler);
    entry_[count_].hits = 0;
    ++count_;
    return true;
}

bool UrcTable::dispatch(std::string_view line) noexcept
{
    Entry* best = nullptr;
    std::size_t best_len = 0;

    for (std::size_t i = 0; i < count_; ++i) {
        const std::string_view prefix = entry_[i].prefix.view();
        if (prefix.size() > best_len && line.starts_with(prefix)) {
            best = &entry_[i];
            best_len = prefix.size();
        }
    }

    if (best == nullptr) {
        return false;
    }

    ++best->hits;
    best->handler(line);
    return true;
}

}  // namespace at

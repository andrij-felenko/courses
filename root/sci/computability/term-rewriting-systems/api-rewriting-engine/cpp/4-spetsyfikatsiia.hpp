#pragma once

#include <string_view>
#include <span>
#include <memory>
#include <optional>
#include <vector>

namespace trs::ffi {

class MemoryArena {
public:
    explicit MemoryArena(size_t initial_bytes = 1024 * 1024);
    ~MemoryArena();

    MemoryArena(const MemoryArena&) = delete;
    MemoryArena& operator=(const MemoryArena&) = delete;
    MemoryArena(MemoryArena&&) noexcept = default;
    MemoryArena& operator=(MemoryArena&&) noexcept = default;

    void reset() noexcept;
    void* allocate(size_t bytes, size_t alignment = alignof(std::max_align_t));
};

struct TermHandle {
    const void* internal_repr{nullptr};
    bool is_valid() const noexcept { return internal_repr != nullptr; }
};

class RewritingEngine {
public:
    explicit RewritingEngine(std::shared_ptr<MemoryArena> arena);

    TermHandle make_var(std::string_view name);
    TermHandle make_fn(std::string_view name, std::span<const TermHandle> args);

    bool equals(TermHandle a, TermHandle b) const noexcept;
    bool contains_var(TermHandle term, std::string_view var) const noexcept;

    std::optional<TermHandle> unify_and_substitute(TermHandle s, TermHandle t);
    TermHandle normalize(TermHandle term);
    int run_knuth_bendix(size_t max_steps);

private:
    std::shared_ptr<MemoryArena> arena_;
};

} // namespace trs::ffi

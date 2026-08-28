#include <cstdint>
#include <vector>
#include <optional>
#include <span>
#include <iostream>
#include <random>
#include <algorithm>

enum class PageState : uint8_t {
    Free = 0,
    Valid = 1,
    Invalid = 2
};

struct FlashBlock {
    uint32_t erase_count{0};
    uint32_t valid_count{0};
    uint32_t invalid_count{0};
    uint32_t free_page_idx{0};
    std::vector<PageState> page_states;
    std::vector<uint32_t> page_lba;

    explicit FlashBlock(size_t pages_per_block)
        : page_states(pages_per_block, PageState::Free),
          page_lba(pages_per_block, UINT32_MAX) {}

    void erase() noexcept {
        ++erase_count;
        valid_count = 0;
        invalid_count = 0;
        free_page_idx = 0;
        std::fill(page_states.begin(), page_states.end(), PageState::Free);
        std::fill(page_lba.begin(), page_lba.end(), UINT32_MAX);
    }

    [[nodiscard]] bool is_clean() const noexcept {
        return free_page_idx == 0 && valid_count == 0;
    }
};

class FtlSimulator {
public:
    FtlSimulator(size_num_blocks, size_t pages_per_block, size_t logical_pages, size_t gc_threshold)
        : pages_per_block_{pages_per_block},
          logical_pages_{logical_pages},
          gc_threshold_{gc_threshold},
          l2p_table_(logical_pages, std::nullopt),
          active_block_id_{0} {
        blocks_.reserve(num_blocks);
        for (size_t i = 0; i < num_blocks; ++i) {
            blocks_.emplace_back(pages_per_block);
        }
    }

    bool write(uint32_t lba) {
        if (lba >= logical_pages_) return false;

        // Перевірка потреби запуску GC при дефіциті вільних блоків
        if (count_free_blocks() < gc_threshold_ &&
            blocks_[active_block_id_].free_page_idx == pages_per_block_) {
            run_gc();
        }

        // Якщо активний блок повністю записаний, відкриваємо новий чистий блок
        if (blocks_[active_block_id_].free_page_idx == pages_per_block_) {
            auto free_b = find_free_block();
            if (!free_b) {
                if (!run_gc()) return false;
                free_b = find_free_block();
                if (!free_b) return false;
            }
            active_block_id_ = *free_b;
        }

        // Інвалідація попередньої фізичної сторінки
        if (l2p_table_[lba].has_value()) {
            uint32_t old_pba = *l2p_table_[lba];
            uint32_t old_b = old_pba / static_cast<uint32_t>(pages_per_block_);
            uint32_t old_p = old_pba % static_cast<uint32_t>(pages_per_block_);
            blocks_[old_b].page_states[old_p] = PageState::Invalid;
            --blocks_[old_b].valid_count;
            ++blocks_[old_b].invalid_count;
        }

        // Програмування нової сторінки
        auto &active = blocks_[active_block_id_];
        uint32_t new_p = active.free_page_idx++;
        active.page_states[new_p] = PageState::Valid;
        active.page_lba[new_p] = lba;
        ++active.valid_count;

        l2p_table_[lba] = (static_cast<uint32_t>(active_block_id_) * static_cast<uint32_t>(pages_per_block_)) + new_p;
        ++host_writes_;
        ++flash_writes_;
        return true;
    }

    [[nodiscard]] double calculate_waf() const noexcept {
        return host_writes_ > 0 ? static_cast<double>(flash_writes_) / static_cast<double>(host_writes_) : 1.0;
    }

    [[nodiscard]] uint64_t host_writes() const noexcept { return host_writes_; }
    [[nodiscard]] uint64_t flash_writes() const noexcept { return flash_writes_; }

private:
    [[nodiscard]] size_t count_free_blocks() const noexcept {
        size_t count = 0;
        for (size_t b = 0; b < blocks_.size(); ++b) {
            if (b != active_block_id_ && blocks_[b].is_clean()) ++count;
        }
        return count;
    }

    [[nodiscard]] std::optional<size_t> find_free_block() const noexcept {
        for (size_t b = 0; b < blocks_.size(); ++b) {
            if (b != active_block_id_ && blocks_[b].is_clean()) return b;
        }
        return std::nullopt;
    }

    bool run_gc() {
        std::optional<size_t> victim_idx;
        uint32_t max_invalid = 0;

        // Пошук блоку з найбільшою кількістю сміття
        for (size_t b = 0; b < blocks_.size(); ++b) {
            if (b == active_block_id_) continue;
            if (blocks_[b].free_page_idx == pages_per_block_ && blocks_[b].invalid_count > max_invalid) {
                max_invalid = blocks_[b].invalid_count;
                victim_idx = b;
            }
        }

        if (!victim_idx) return false;

        auto &victim = blocks_[*victim_idx];
        for (size_t p = 0; p < pages_per_block_; ++p) {
            if (victim.page_states[p] == PageState::Valid) {
                uint32_t lba = victim.page_lba[p];

                if (blocks_[active_block_id_].free_page_idx == pages_per_block_) {
                    auto next_b = find_free_block();
                    if (!next_b) return false;
                    active_block_id_ = *next_b;
                }

                auto &active = blocks_[active_block_id_];
                uint32_t new_p = active.free_page_idx++;
                active.page_states[new_p] = PageState::Valid;
                active.page_lba[new_p] = lba;
                ++active.valid_count;

                l2p_table_[lba] = (static_cast<uint32_t>(active_block_id_) * static_cast<uint32_t>(pages_per_block_)) + new_p;
                ++flash_writes_;
            }
        }

        victim.erase();
        return true;
    }

    size_t pages_per_block_;
    size_t logical_pages_;
    size_t gc_threshold_;
    std::vector<std::optional<uint32_t>> l2p_table_;
    std::vector<FlashBlock> blocks_;
    size_t active_block_id_{0};
    uint64_t host_writes_{0};
    uint64_t flash_writes_{0};
};

int main() {
    constexpr size_t kBlocks = 8;
    constexpr size_t kPagesPerBlock = 8;
    constexpr size_t kLogicalPages = 32;
    constexpr size_t kGcThreshold = 2;

    FtlSimulator sim(kBlocks, kPagesPerBlock, kLogicalPages, kGcThreshold);

    std::mt19937 gen(42);
    std::uniform_int_distribution<uint32_t> dist(0, kLogicalPages - 1);

    for (int i = 0; i < 300; ++i) {
        sim.write(dist(gen));
    }

    std::cout << "Результати симуляції FTL (C++20):\n"
              << "  Хост-записів:     " << sim.host_writes() << "\n"
              << "  Флеш-записів:     " << sim.flash_writes() << "\n"
              << "  Розрахований WAF: " << sim.calculate_waf() << "\n";

    return 0;
}

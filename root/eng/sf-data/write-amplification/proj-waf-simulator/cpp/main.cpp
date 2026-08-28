#include <iostream>
#include <vector>
#include <random>
#include <numeric>
#include <iomanip>
#include <cstdint>

enum class PageState {
    Free,
    Valid,
    Invalid
};

struct PhysicalPage {
    PageState state{PageState::Free};
    std::uint32_t lba{0};
};

class EraseBlock {
public:
    static constexpr std::size_t PagesPerBlock = 16;
    
    EraseBlock() : pages_(PagesPerBlock) {}

    [[nodiscard]] bool is_full() const noexcept { return free_count_ == 0; }
    [[nodiscard]] std::size_t valid_count() const noexcept { return valid_count_; }
    [[nodiscard]] std::size_t invalid_count() const noexcept { return invalid_count_; }
    [[nodiscard]] std::size_t free_count() const noexcept { return free_count_; }

    PhysicalPage& page(std::size_t idx) { return pages_.at(idx); }
    const PhysicalPage& page(std::size_t idx) const { return pages_.at(idx); }

    void invalidate_page(std::size_t idx) {
        if (pages_.at(idx).state == PageState::Valid) {
            pages_.at(idx).state = PageState::Invalid;
            --valid_count_;
            ++invalid_count_;
        }
    }

    void write_page(std::size_t idx, std::uint32_t lba) {
        pages_.at(idx).state = PageState::Valid;
        pages_.at(idx).lba = lba;
        --free_count_;
        ++valid_count_;
    }

    void erase() {
        for (auto& p : pages_) {
            p.state = PageState::Free;
            p.lba = 0;
        }
        valid_count_ = 0;
        invalid_count_ = 0;
        free_count_ = PagesPerBlock;
    }

private:
    std::vector<PhysicalPage> pages_;
    std::size_t valid_count_{0};
    std::size_t invalid_count_{0};
    std::size_t free_count_{PagesPerBlock};
};

class FTLSimulator {
public:
    FTLSimulator(std::size_t user_pages, std::size_t total_blocks)
        : user_pages_(user_pages),
          blocks_(total_blocks),
          lba_table_(user_pages, -1) {}

    void write(std::uint32_t lba) {
        if (lba >= user_pages_) return;

        if (active_page_idx_ >= EraseBlock::PagesPerBlock || blocks_[active_block_].is_full()) {
            run_garbage_collection();
        }

        // Івалідувати попередній запис
        if (int32_t old_phys = lba_table_[lba]; old_phys >= 0) {
            std::size_t old_block = old_phys / EraseBlock::PagesPerBlock;
            std::size_t old_page = old_phys % EraseBlock::PagesPerBlock;
            blocks_[old_block].invalidate_page(old_page);
        }

        // Записати у поточний активний блок
        auto& ablock = blocks_[active_block_];
        std::size_t pidx = active_page_idx_++;
        ablock.write_page(pidx, lba);

        lba_table_[lba] = static_cast<std::int32_t>(active_block_ * EraseBlock::PagesPerBlock + pidx);
        ++host_writes_;
    }

    [[nodiscard]] double calculate_waf() const noexcept {
        if (host_writes_ == 0) return 1.0;
        return static_cast<double>(host_writes_ + gc_page_copies_) / static_cast<double>(host_writes_);
    }

    void print_stats() const {
        std::cout << "=== Статистика FTL Симулятора (C++) ===\n"
                  << "Записи від хоста:       " << host_writes_ << " сторінок\n"
                  << "Перенесення GC:         " << gc_page_copies_ << " сторінок\n"
                  << "Стирання блоків:        " << block_erases_ << "\n"
                  << std::fixed << std::setprecision(3)
                  << "Розрахований WAF:       " << calculate_waf() << "\n";
    }

private:
    void run_garbage_collection() {
        int victim = -1;
        std::size_t max_invalid = 0;
        for (std::size_t b = 0; b < blocks_.size(); ++b) {
            if (b == active_block_) continue;
            if (blocks_[b].invalid_count() > max_invalid) {
                max_invalid = blocks_[b].invalid_count();
                victim = static_cast<int>(b);
            }
        }

        if (victim < 0) return;

        auto& vblock = blocks_[victim];
        for (std::size_t p = 0; p < EraseBlock::PagesPerBlock; ++p) {
            if (vblock.page(p).state == PageState::Valid) {
                std::uint32_t lba = vblock.page(p).lba;
                
                if (active_page_idx_ >= EraseBlock::PagesPerBlock) {
                    for (std::size_t b = 0; b < blocks_.size(); ++b) {
                        if (static_cast<int>(b) != victim && blocks_[b].free_count() == EraseBlock::PagesPerBlock) {
                            active_block_ = b;
                            active_page_idx_ = 0;
                            break;
                        }
                    }
                }

                auto& ablock = blocks_[active_block_];
                std::size_t pidx = active_page_idx_++;
                ablock.write_page(pidx, lba);

                lba_table_[lba] = static_cast<std::int32_t>(active_block_ * EraseBlock::PagesPerBlock + pidx);
                ++gc_page_copies_;
            }
        }

        vblock.erase();
        ++block_erases_;
    }

    std::size_t user_pages_;
    std::vector<EraseBlock> blocks_;
    std::vector<std::int32_t> lba_table_;
    std::size_t active_block_{0};
    std::size_t active_page_idx_{0};
    std::uint64_t host_writes_{0};
    std::uint64_t gc_page_copies_{0};
    std::uint64_t block_erases_{0};
};

int main() {
    constexpr std::size_t UserPages = 64;
    constexpr std::size_t TotalBlocks = 6; // OP ~ 50%
    
    FTLSimulator sim(UserPages, TotalBlocks);
    
    std::mt19937 rng(42);
    std::uniform_int_distribution<std::uint32_t> dist(0, UserPages - 1);

    for (int i = 0; i < 1000; ++i) {
        sim.write(dist(rng));
    }

    sim.print_stats();
    return 0;
}

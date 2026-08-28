// gc_sim.cpp — Ідіоматичний симулятор Garbage Collection мовою C++17
#include <iostream>
#include <vector>
#include <optional>
#include <numeric>
#include <algorithm>
#include <random>
#include <iomanip>
#include <cstdint>

constexpr size_t PAGES_PER_BLOCK = 64;
constexpr size_t TOTAL_BLOCKS = 128;
constexpr size_t TOTAL_PAGES = TOTAL_BLOCKS * PAGES_PER_BLOCK;
constexpr size_t HOST_LOGICAL_PAGES = static_cast<size_t>(TOTAL_PAGES * 0.80);

enum class GCPolicy {
    Greedy,
    CostBenefit
};

struct BlockMetadata {
    size_t valid_count{0};
    size_t invalid_count{0};
    size_t free_count{PAGES_PER_BLOCK};
    uint64_t last_write_time{0};
    uint32_t erase_count{0};
};

class FlashSimulator {
public:
    explicit FlashSimulator(GCPolicy policy) : policy_(policy) {
        l2p_.resize(HOST_LOGICAL_PAGES, std::nullopt);
        p2l_.resize(TOTAL_PAGES, std::nullopt);
        is_invalid_.resize(TOTAL_PAGES, false);
        blocks_.resize(TOTAL_BLOCKS);
    }

    void write(size_t lba) {
        current_time_++;
        host_writes_++;

        if (blocks_[active_block_].free_count == 0) {
            if (count_free_blocks() < 3) {
                run_gc();
            }
            if (auto next = get_next_free_block()) {
                active_block_ = *next;
                active_page_offset_ = 0;
            } else {
                run_gc();
                active_block_ = get_next_free_block().value_or(0);
                active_page_offset_ = 0;
            }
        }

        // Оновлення застарілості попередньої версії LBA
        if (auto old_ppn = l2p_[lba]) {
            is_invalid_[*old_ppn] = true;
            size_t old_b = *old_ppn / PAGES_PER_BLOCK;
            if (blocks_[old_b].valid_count > 0) blocks_[old_b].valid_count--;
            blocks_[old_b].invalid_count++;
        }

        // Запис нової сторінки
        size_t ppn = active_block_ * PAGES_PER_BLOCK + active_page_offset_;
        l2p_[lba] = ppn;
        p2l_[ppn] = lba;
        is_invalid_[ppn] = false;

        blocks_[active_block_].valid_count++;
        blocks_[active_block_].free_count--;
        blocks_[active_block_].last_write_time = current_time_;
        active_page_offset_++;
        nand_writes_++;
    }

    [[nodiscard]] double get_write_amplification() const noexcept {
        return static_cast<double>(nand_writes_) / static_cast<double>(host_writes_);
    }

    void print_stats(std::string_view policy_name) const {
        std::cout << "--- Політика: " << policy_name << " ---\n"
                  << "  Хостових записів:    " << host_writes_ << "\n"
                  << "  Фізичних записів:    " << nand_writes_ << "\n"
                  << "  Перенесено сторінок: " << gc_copied_pages_ << "\n"
                  << "  Всього стирань:      " << total_erases_ << "\n"
                  << "  Write Amplification: " << std::fixed << std::setprecision(3) 
                  << get_write_amplification() << "\n\n";
    }

private:
    [[nodiscard]] size_t count_free_blocks() const noexcept {
        return std::count_if(blocks_.begin(), blocks_.end(), [](const auto& b) {
            return b.free_count == PAGES_PER_BLOCK;
        });
    }

    [[nodiscard]] std::optional<size_t> get_next_free_block() const noexcept {
        for (size_t b = 0; b < TOTAL_BLOCKS; ++b) {
            if (b != active_block_ && blocks_[b].free_count == PAGES_PER_BLOCK) {
                return b;
            }
        }
        return std::nullopt;
    }

    [[nodiscard]] std::optional<size_t> select_victim_block() const noexcept {
        std::optional<size_t> victim;
        double best_score = -1.0;

        for (size_t b = 0; b < TOTAL_BLOCKS; ++b) {
            if (b == active_block_ || blocks_[b].free_count == PAGES_PER_BLOCK) continue;

            const auto& bm = blocks_[b];
            double score = 0.0;

            if (policy_ == GCPolicy::Greedy) {
                score = static_cast<double>(bm.invalid_count);
            } else {
                double u = static_cast<double>(bm.valid_count) / static_cast<double>(PAGES_PER_BLOCK);
                u = std::max(u, 0.001);
                double age = static_cast<double>(current_time_ - bm.last_write_time + 1);
                score = ((1.0 - u) / (2.0 * u)) * age;
            }

            if (score > best_score) {
                best_score = score;
                victim = b;
            }
        }
        return victim;
    }

    void run_gc() {
        auto victim = select_victim_block();
        auto target_block = get_next_free_block();
        if (!victim || !target_block) return;

        size_t v_idx = *victim;
        size_t t_idx = *target_block;
        size_t start_ppn = v_idx * PAGES_PER_BLOCK;
        size_t target_ppn_start = t_idx * PAGES_PER_BLOCK;
        size_t target_offset = 0;

        // 1. Евакуація чинних сторінок
        for (size_t i = 0; i < PAGES_PER_BLOCK; ++i) {
            size_t ppn = start_ppn + i;
            if (auto lba = p2l_[ppn]) {
                if (l2p_[*lba] == ppn && !is_invalid_[ppn]) {
                    size_t new_ppn = target_ppn_start + target_offset++;
                    l2p_[*lba] = new_ppn;
                    p2l_[new_ppn] = *lba;
                    is_invalid_[new_ppn] = false;
                    is_invalid_[ppn] = true;

                    nand_writes_++;
                    gc_copied_pages_++;
                    blocks_[t_idx].valid_count++;
                    blocks_[t_idx].free_count--;
                }
            }
        }

        blocks_[t_idx].last_write_time = current_time_;

        // 2. Стирання блоку-жертви
        for (size_t i = 0; i < PAGES_PER_BLOCK; ++i) {
            size_t ppn = start_ppn + i;
            p2l_[ppn] = std::nullopt;
            is_invalid_[ppn] = false;
        }

        blocks_[v_idx].valid_count = 0;
        blocks_[v_idx].invalid_count = 0;
        blocks_[v_idx].free_count = PAGES_PER_BLOCK;
        blocks_[v_idx].erase_count++;
        total_erases_++;
    }

    GCPolicy policy_;
    std::vector<std::optional<size_t>> l2p_;
    std::vector<std::optional<size_t>> p2l_;
    std::vector<bool> is_invalid_;
    std::vector<BlockMetadata> blocks_;

    size_t active_block_{0};
    size_t active_page_offset_{0};

    uint64_t current_time_{0};
    uint64_t host_writes_{0};
    uint64_t nand_writes_{0};
    uint64_t gc_copied_pages_{0};
    uint64_t total_erases_{0};
};

int main() {
    std::cout << "=== C++17 Симуляція Garbage Collection у Flash ===\n\n";

    std::mt19937 rng(42);
    std::discrete_distribution<size_t> dist({80, 20}); // 80% гарячі, 20% холодні

    for (auto policy : {GCPolicy::Greedy, GCPolicy::CostBenefit}) {
        FlashSimulator sim(policy);

        for (size_t i = 0; i < 100000; ++i) {
            size_t lba = 0;
            if (dist(rng) == 0) {
                lba = rng() % (HOST_LOGICAL_PAGES / 5);
            } else {
                lba = (HOST_LOGICAL_PAGES / 5) + (rng() % (HOST_LOGICAL_PAGES - HOST_LOGICAL_PAGES / 5));
            }
            sim.write(lba);
        }

        sim.print_stats(policy == GCPolicy::Greedy ? "Greedy (Жадібна)" : "Cost-Benefit (Вартість/Вигода)");
    }
    return 0;
}

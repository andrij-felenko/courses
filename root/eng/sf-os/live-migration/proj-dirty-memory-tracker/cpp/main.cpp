#include <iostream>
#include <vector>
#include <array>
#include <atomic>
#include <thread>
#include <mutex>
#include <chrono>
#include <random>
#include <cstring>
#include <span>
#include <memory>
#include <bit>
#include <algorithm>

namespace migration {

inline constexpr size_t kPageSize = 4096;
inline constexpr size_t kTotalPages = 16384; // 64 МБ
inline constexpr size_t kTotalBytes = kTotalPages * kPageSize;
inline constexpr size_t kBitmapWords = kTotalPages / 64;
inline constexpr size_t kDowntimeThresholdPages = 64;

struct VirtualDeviceState {
    uint64_t vcpu_rip{0x1000};
    uint64_t vcpu_rsp{0x7FFF0000};
    uint64_t vcpu_cr3{0x200000};
    uint32_t apic_timer_count{0};
    uint64_t tsc_offset{0};
};

class VMSimulator {
public:
    VMSimulator()
        : source_ram_(std::make_unique<uint8_t[]>(kTotalBytes)),
          target_ram_(std::make_unique<uint8_t[]>(kTotalBytes)) {
        for (auto& word : dirty_bitmap_) {
            word.store(0ULL, std::memory_order_relaxed);
        }
        // Ініціалізація вихідного стану пам'яті
        for (size_t i = 0; i < kTotalPages; ++i) {
            std::memset(source_ram_.get() + i * kPageSize, static_cast<int>(i & 0xFF), kPageSize);
        }
    }

    void mark_page_dirty(size_t page_idx) noexcept {
        size_t word_idx = page_idx / 64;
        uint64_t bit_mask = 1ULL << (page_idx % 64);
        dirty_bitmap_[word_idx].fetch_or(bit_mask, std::memory_order_relaxed);
    }

    size_t harvest_dirty_bitmap(std::span<uint64_t, kBitmapWords> local_copy) noexcept {
        size_t dirty_count = 0;
        for (size_t i = 0; i < kBitmapWords; ++i) {
            local_copy[i] = dirty_bitmap_[i].exchange(0ULL, std::memory_order_acq_rel);
            if (local_copy[i] != 0) {
                dirty_count += static_cast<size_t>(std::popcount(local_copy[i]));
            }
        }
        return dirty_count;
    }

    void run_migration() {
        std::array<uint64_t, kBitmapWords> local_bitmap{};
        size_t round = 0;
        size_t total_transferred_pages = 0;
        size_t prev_dirty_count = kTotalPages;

        std::cout << "[MIGRATION] === Старт C++20 ітеративної живої міграції (RAM: "
                  << kTotalBytes / (1024 * 1024) << " МБ) ===\n";
        auto start_time = std::chrono::steady_clock::now();

        // Ітерація 0: Повний дамп усієї оперативної пам'яті
        std::cout << "[MIGRATION] Раунд 0: Початковий повний дамп " << kTotalPages << " сторінок...\n";
        auto r0_start = std::chrono::steady_clock::now();
        std::memcpy(target_ram_.get(), source_ram_.get(), kTotalBytes);
        total_transferred_pages += kTotalPages;
        auto r0_dur = std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - r0_start);
        std::cout << "[MIGRATION] Раунд 0 завершено за " << r0_dur.count() << " мс.\n";

        // Цикл попереднього копіювання брудної пам'яті
        while (true) {
            round++;
            auto round_start = std::chrono::steady_clock::now();

            size_t dirty_count = harvest_dirty_bitmap(local_bitmap);
            double dirty_mb = static_cast<double>(dirty_count * kPageSize) / (1024.0 * 1024.0);
            std::cout << "[MIGRATION] Раунд " << round << ": виявлено "
                      << dirty_count << " брудних сторінок (" << dirty_mb << " МБ)...\n";

            if (dirty_count <= kDowntimeThresholdPages) {
                std::cout << "[MIGRATION] >>> Збіжність досягнута! Залишок " << dirty_count
                          << " <= порогу " << kDowntimeThresholdPages << " <<<\n";
                break;
            }

            if (dirty_count >= static_cast<size_t>(prev_dirty_count * 0.90)) {
                int cur_th = cpu_throttle_percent_.load(std::memory_order_relaxed);
                int new_th = std::min(cur_th + 20, 90);
                cpu_throttle_percent_.store(new_th, std::memory_order_relaxed);
                std::cout << "[AUTO-CONVERGE] Стагнація! Тротлінг vCPU підвищено до " << new_th << "%\n";
            }
            prev_dirty_count = dirty_count;

            transfer_pages(local_bitmap);
            total_transferred_pages += dirty_count;

            auto round_dur = std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - round_start);
            std::cout << "[MIGRATION] Раунд " << round << " завершено за " << round_dur.count() << " мс.\n";
        }

        // Фаза Stop-and-Copy: Зупинка vCPU та фінальна синхронізація
        std::cout << "[STOP-AND-COPY] Зупинка vCPU гостя (початок Downtime)...\n";
        auto downtime_start = std::chrono::steady_clock::now();

        {
            std::lock_guard<std::mutex> lock(vcpu_mutex_);
            vm_running_.store(false, std::memory_order_relaxed);

            size_t final_dirty = harvest_dirty_bitmap(local_bitmap);
            transfer_pages(local_bitmap);
            total_transferred_pages += final_dirty;

            // Серіалізація стану віртуальних пристроїв
            target_dev_state_ = dev_state_;
            target_dev_state_.tsc_offset += 1000;
        }

        auto downtime_dur = std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - downtime_start);
        std::cout << "[STOP-AND-COPY] >>> Реальний час простою гостя: " << downtime_dur.count() << " мс <<<\n";

        auto total_dur = std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - start_time);
        std::cout << "[MIGRATION] === Міграція успішно завершена за " << total_dur.count() << " мс ===\n";
        std::cout << "[MIGRATION] Сумарно передано: " << total_transferred_pages
                  << " сторінок (надлишковість: "
                  << static_cast<double>(total_transferred_pages) / static_cast<double>(kTotalPages) << " x)\n";
    }

    void start_guest_workload() {
        writer_thread_ = std::jthread([this](std::stop_token st) {
            std::mt19937 rng(42);
            std::uniform_int_distribution<size_t> dist_pct(0, 99);
            std::uniform_int_distribution<size_t> dist_hot(0, kTotalPages / 5 - 1);
            std::uniform_int_distribution<size_t> dist_all(0, kTotalPages - 1);
            std::uniform_int_distribution<size_t> dist_offset(0, kPageSize - 1);

            while (!st.stop_requested() && vm_running_.load(std::memory_order_relaxed)) {
                {
                    std::lock_guard<std::mutex> lock(vcpu_mutex_);
                    size_t page_idx = (dist_pct(rng) < 80) ? dist_hot(rng) : dist_all(rng);
                    size_t offset = page_idx * kPageSize + dist_offset(rng);
                    source_ram_[offset] = static_cast<uint8_t>(rng() & 0xFF);

                    mark_page_dirty(page_idx);
                    dev_state_.vcpu_rip += 4;
                    dev_state_.apic_timer_count++;
                }

                int throttle = cpu_throttle_percent_.load(std::memory_order_relaxed);
                if (throttle > 0) {
                    std::this_thread::sleep_for(std::chrono::microseconds(throttle * 5));
                } else {
                    std::this_thread::sleep_for(std::chrono::microseconds(20));
                }
            }
        });
    }

    [[nodiscard]] bool verify_integrity() const noexcept {
        return std::memcmp(source_ram_.get(), target_ram_.get(), kTotalBytes) == 0;
    }

    void stop_guest() {
        vm_running_.store(false, std::memory_order_relaxed);
        if (writer_thread_.joinable()) {
            writer_thread_.request_stop();
            writer_thread_.join();
        }
    }

private:
    void transfer_pages(std::span<const uint64_t, kBitmapWords> bitmap) {
        for (size_t w = 0; w < kBitmapWords; ++w) {
            uint64_t word = bitmap[w];
            while (word != 0) {
                int bit = std::countr_zero(word);
                size_t page_idx = w * 64 + static_cast<size_t>(bit);

                std::memcpy(target_ram_.get() + page_idx * kPageSize,
                            source_ram_.get() + page_idx * kPageSize,
                            kPageSize);

                // Емуляція затримки передачі пакета по мережі
                std::this_thread::sleep_for(std::chrono::microseconds(3));
                word &= ~(1ULL << bit);
            }
        }
    }

    std::unique_ptr<uint8_t[]> source_ram_;
    std::unique_ptr<uint8_t[]> target_ram_;
    std::array<std::atomic<uint64_t>, kBitmapWords> dirty_bitmap_{};

    std::atomic<bool> vm_running_{true};
    std::atomic<int>  cpu_throttle_percent_{0};

    std::mutex vcpu_mutex_;
    VirtualDeviceState dev_state_{};
    VirtualDeviceState target_dev_state_{};
    std::jthread writer_thread_;
};

} // namespace migration

int main() {
    migration::VMSimulator vm;
    vm.start_guest_workload();

    // Даємо гостю попрацювати 50 мс перед стартом міграції
    std::this_thread::sleep_for(std::chrono::milliseconds(50));

    vm.run_migration();
    vm.stop_guest();

    std::cout << "[VERIFICATION] Перевірка цілісності оперативної пам'яті...\n";
    if (vm.verify_integrity()) {
        std::cout << "[VERIFICATION] УСПІХ: Пам'ять цільового вузла 100% ідентична джерелу!\n";
    } else {
        std::cout << "[VERIFICATION] ПОМИЛКА: Виявлено розходження вмісту сторінок!\n";
        return 1;
    }
    return 0;
}

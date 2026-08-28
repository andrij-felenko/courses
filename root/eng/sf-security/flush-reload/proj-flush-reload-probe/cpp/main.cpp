#include <iostream>
#include <array>
#include <span>
#include <vector>
#include <numeric>
#include <algorithm>
#include <cstdint>
#include <cstring>
#include <sched.h>
#include <immintrin.h>
#include <x86intrin.h>

namespace sidechannel {

constexpr std::size_t PageSize = 4096;
constexpr std::size_t ProbeEntries = 256;
constexpr std::size_t CalibrationRounds = 2000;

class FlushReloadProbe {
public:
    FlushReloadProbe() {
        /* Прив'язка до ядра для мінімізації між'ядерного шуму */
        cpu_set_t cpuset;
        CPU_ZERO(&cpuset);
        CPU_SET(0, &cpuset);
        sched_setaffinity(0, sizeof(cpu_set_t), &cpuset);

        /* Примусова ініціалізація пам'яті для виділення фізичних сторінок */
        probe_storage_.fill(0x55);
        calibrate();
    }

    /* Витіснення лінії пам'яті за заданим індексом зонда */
    void flush_entry(std::size_t index) noexcept {
        _mm_clflush(get_entry_address(index));
    }

    /* Очищення всього вимірювального масиву */
    void flush_all() noexcept {
        for (std::size_t i = 0; i < ProbeEntries; ++i) {
            flush_entry(i);
        }
        _mm_mfence();
    }

    /* Вимірювання затримки доступу до конкретної зони зонда */
    [[nodiscard]] std::uint64_t reload_entry(std::size_t index) const noexcept {
        const volatile void* addr = get_entry_address(index);
        std::uint32_t aux = 0;

        _mm_lfence();
        const std::uint64_t start = __rdtscp(&aux);
        _mm_lfence();

        (void)*static_cast<const volatile std::uint8_t*>(addr);

        _mm_lfence();
        const std::uint64_t end = __rdtscp(&aux);
        _mm_lfence();

        return end - start;
    }

    /* Повний цикл виявлення найшвидшої кеш-лінії */
    [[nodiscard]] std::pair<int, std::uint64_t> detect_hit() const noexcept {
        int best_index = -1;
        std::uint64_t min_latency = std::numeric_limits<std::uint64_t>::max();

        for (std::size_t i = 0; i < ProbeEntries; ++i) {
            const std::uint64_t latency = reload_entry(i);
            if (latency < threshold_ && latency < min_latency) {
                min_latency = latency;
                best_index = static_cast<int>(i);
            }
        }
        return {best_index, min_latency};
    }

    /* Отримання покажчика на конкретну сторінку зонда (для жертви) */
    [[nodiscard]] volatile std::uint8_t* entry_ptr(std::size_t index) noexcept {
        return &probe_storage_[index * PageSize];
    }

    [[nodiscard]] std::uint64_t threshold() const noexcept { return threshold_; }

private:
    [[nodiscard]] const volatile void* get_entry_address(std::size_t index) const noexcept {
        return &probe_storage_[index * PageSize];
    }

    void calibrate() {
        std::uint64_t hit_total = 0;
        std::uint64_t miss_total = 0;
        volatile auto* test_addr = &probe_storage_[0];

        *test_addr = 0xAA;

        for (std::size_t i = 0; i < CalibrationRounds; ++i) {
            (void)*test_addr;
            _mm_lfence();
            hit_total += reload_entry(0);

            flush_entry(0);
            _mm_mfence();
            miss_total += reload_entry(0);
        }

        const std::uint64_t hit_avg = hit_total / CalibrationRounds;
        const std::uint64_t miss_avg = miss_total / CalibrationRounds;
        threshold_ = (hit_avg + miss_avg) / 2;

        std::cout << "[Калібрування C++] Середній Hit: " << hit_avg
                  << " тактів, Miss: " << miss_avg
                  << " тактів. Поріг: " << threshold_ << " тактів.\n";
    }

    alignas(PageSize) std::array<std::uint8_t, ProbeEntries * PageSize> probe_storage_{};
    std::uint64_t threshold_{140};
};

} // namespace sidechannel

int main() {
    sidechannel::FlushReloadProbe probe;

    /* 1. Фаза FLUSH */
    probe.flush_all();

    /* 2. Дія жертви */
    constexpr std::uint8_t secret = 204;
    *probe.entry_ptr(secret) = 0xFF; // звернення жертви
    _mm_mfence();

    /* 3. Фаза RELOAD */
    const auto [recovered, latency] = probe.detect_hit();

    if (recovered >= 0) {
        std::cout << "[Успіх C++] Відновлено секретний байт: " << recovered
                  << " (час читання: " << latency << " тактів)\n";
    } else {
        std::cerr << "[Помилка C++] Секрет не виявлено в кеші.\n";
    }

    return 0;
}

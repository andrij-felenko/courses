#include <iostream>
#include <vector>
#include <atomic>
#include <thread>
#include <cstdint>
#include <bit>
#include <optional>

class ScalableBitmap {
public:
    static constexpr size_t BITS_PER_WORD = 64;

    explicit ScalableBitmap(size_t num_words)
        : words_(num_words), total_depth_(num_words * BITS_PER_WORD) {
        for (auto& w : words_) {
            w.store(0, std::memory_order_relaxed);
        }
    }

    /* Безблокова алокація тегу із записом нової підказки */
    [[nodiscard]] std::optional<unsigned int> allocate_tag(unsigned int& hint) noexcept {
        const size_t num_words = words_.size();
        size_t start_word = (hint / BITS_PER_WORD) % num_words;

        for (size_t i = 0; i < num_words; ++i) {
            size_t w_idx = (start_word + i) % num_words;
            auto& word_atom = words_[w_idx];

            uint64_t val = word_atom.load(std::memory_order_relaxed);
            while (val != ~0ULL) {
                int bit = std::countr_zero(~val);
                if (bit >= static_cast<int>(BITS_PER_WORD)) break;

                uint64_t mask = 1ULL << bit;
                if (!(val & mask)) {
                    if (word_atom.compare_exchange_weak(val, val | mask,
                                                        std::memory_order_acquire,
                                                        std::memory_order_relaxed)) {
                        unsigned int tag = static_cast<unsigned int>(w_idx * BITS_PER_WORD + bit);
                        hint = tag + 1;
                        return tag;
                    }
                }
            }
        }
        return std::nullopt;
    }

    /* Повернення тегу з гарантією впорядкування пам'яті */
    void release_tag(unsigned int tag) noexcept {
        size_t w_idx = tag / BITS_PER_WORD;
        unsigned int bit = tag % BITS_PER_WORD;
        uint64_t mask = ~(1ULL << bit);

        words_[w_idx].fetch_and(mask, std::memory_order_release);
    }

    [[nodiscard]] size_t total_depth() const noexcept { return total_depth_; }

private:
    std::vector<std::atomic<uint64_t>> words_;
    size_t total_depth_;
};

int main() {
    constexpr size_t NUM_WORDS = 4;
    constexpr int NUM_THREADS = 4;
    constexpr int OPS_PER_THREAD = 100000;

    ScalableBitmap sbitmap(NUM_WORDS);
    std::cout << "Запуск C++ sbitmap симулятора (" << sbitmap.total_depth() 
              << " тегів, " << NUM_THREADS << " потоків)...\n";

    std::vector<std::thread> workers;
    workers.reserve(NUM_THREADS);

    for (int t = 0; t < NUM_THREADS; ++t) {
        workers.emplace_back([&sbitmap, t]() {
            unsigned int hint = static_cast<unsigned int>(t * 16);
            size_t allocated = 0;

            for (int i = 0; i < OPS_PER_THREAD; ++i) {
                if (auto tag = sbitmap.allocate_tag(hint)) {
                    ++allocated;
                    sbitmap.release_tag(*tag);
                }
            }
            std::cout << "Потік C++ [" << t << "] обробив " << allocated << " операцій.\n";
        });
    }

    for (auto& th : workers) {
        th.join();
    }

    std::cout << "Тестування C++ sbitmap завершено успішно.\n";
    return 0;
}

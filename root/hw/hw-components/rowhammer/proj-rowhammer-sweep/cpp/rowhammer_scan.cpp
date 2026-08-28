// rowhammer_scan.cpp — Ідіоматичний об'єктно-орієнтований сканер Rowhammer на C++20
#include <iostream>
#include <vector>
#include <span>
#include <memory>
#include <chrono>
#include <format>
#include <expected>
#include <cstdint>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include <x86intrin.h>

namespace rowhammer {

// RAII-обгортка для безпечного виділення неперервної анонімної пам'яті
class MappedBuffer {
public:
    explicit MappedBuffer(std::size_t size) : size_(size) {
        void* ptr = ::mmap(nullptr, size_,
                           PROT_READ | PROT_WRITE,
                           MAP_PRIVATE | MAP_ANONYMOUS | MAP_POPULATE,
                           -1, 0);
        if (ptr == MAP_FAILED) {
            throw std::runtime_error("Не вдалося виділити пам'ять через mmap");
        }
        data_ = static_cast<std::byte*>(ptr);
    }

    ~MappedBuffer() noexcept {
        if (data_ != nullptr) {
            ::munmap(data_, size_);
        }
    }

    MappedBuffer(const MappedBuffer&) = delete;
    MappedBuffer& operator=(const MappedBuffer&) = delete;

    MappedBuffer(MappedBuffer&& other) noexcept : data_(other.data_), size_(other.size_) {
        other.data_ = nullptr;
        other.size_ = 0;
    }

    MappedBuffer& operator=(MappedBuffer&& other) noexcept {
        if (this != &other) {
            if (data_ != nullptr) {
                ::munmap(data_, size_);
            }
            data_ = other.data_;
            size_ = other.size_;
            other.data_ = nullptr;
            other.size_ = 0;
        }
        return *this;
    }

    [[nodiscard]] std::span<std::byte> as_span() noexcept {
        return {data_, size_};
    }

    [[nodiscard]] std::size_t size() const noexcept { return size_; }

private:
    std::byte* data_{nullptr};
    std::size_t size_{0};
};

struct BitFlipDescriptor {
    std::size_t rowIndex;
    std::size_t byteOffset;
    int bitOffset;
    bool expectedVal;
    bool actualVal;
};

class MemoryHammerEngine {
public:
    static constexpr std::size_t RowSizeBytes = 8 * 1024; // 8 КБ на рядок
    static constexpr std::size_t DefaultActivations = 200'000;

    static void executeDoubleSided(volatile std::byte* rowA1, volatile std::byte* rowA2, std::size_t count) noexcept {
        for (std::size_t i = 0; i < count; ++i) {
            // Читання зі скиданням першого рядка-агресора
            (void)*rowA1;
            _mm_clflush(const_cast<const void*>(static_cast<volatile void*>(rowA1)));

            // Читання зі скиданням другого рядка-агресора
            (void)*rowA2;
            _mm_clflush(const_cast<const void*>(static_cast<volatile void*>(rowA2)));

            // Серіалізація конвеєра інструкцій
            _mm_mfence();
        }
    }

    static std::vector<BitFlipDescriptor> inspectVictimRow(
        std::span<const std::byte> victimData,
        std::byte expectedPattern,
        std::size_t rowIndex)
    {
        std::vector<BitFlipDescriptor> detectedFlips;

        for (std::size_t byteIdx = 0; byteIdx < victimData.size(); ++byteIdx) {
            std::byte actual = victimData[byteIdx];
            if (actual != expectedPattern) {
                auto diff = static_cast<std::uint8_t>(actual ^ expectedPattern);
                for (int bit = 0; bit < 8; ++bit) {
                    if (diff & (1 << bit)) {
                        bool exp = (static_cast<std::uint8_t>(expectedPattern) >> bit) & 1;
                        bool act = (static_cast<std::uint8_t>(actual) >> bit) & 1;
                        detectedFlips.push_back({rowIndex, byteIdx, bit, exp, act});
                    }
                }
            }
        }
        return detectedFlips;
    }
};

} // namespace rowhammer

int main() {
    std::cout << "[*] Запуск модульного сканера Rowhammer (C++20)\n";

    constexpr std::size_t TotalMemorySize = 4 * 1024 * 1024; // 4 МБ
    constexpr std::byte Pattern{0xAA};

    try {
        rowhammer::MappedBuffer buffer(TotalMemorySize);
        auto memorySpan = buffer.as_span();

        // Ініціалізація пам'яті еталонним шаблоном
        std::fill(memorySpan.begin(), memorySpan.end(), Pattern);

        const std::size_t totalRows = TotalMemorySize / rowhammer::MemoryHammerEngine::RowSizeBytes;
        std::cout << std::format("[*] Виділено {} рядків по {} байтів\n",
                                 totalRows, rowhammer::MemoryHammerEngine::RowSizeBytes);

        std::size_t totalFlipsCount = 0;
        auto startTime = std::chrono::steady_clock::now();

        // Прохід по всіх можливих трійках рядків масиву
        for (std::size_t r = 1; r < totalRows - 1; ++r) {
            auto* agg1 = &memorySpan[(r - 1) * rowhammer::MemoryHammerEngine::RowSizeBytes];
            auto* victim = &memorySpan[r * rowhammer::MemoryHammerEngine::RowSizeBytes];
            auto* agg2 = &memorySpan[(r + 1) * rowhammer::MemoryHammerEngine::RowSizeBytes];

            // Запуск циклу атаки подвійним молотом
            rowhammer::MemoryHammerEngine::executeDoubleSided(
                agg1, agg2, rowhammer::MemoryHammerEngine::DefaultActivations);

            // Перевірка результату в рядку-жертві
            std::span<const std::byte> victimSpan(victim, rowhammer::MemoryHammerEngine::RowSizeBytes);
            auto flips = rowhammer::MemoryHammerEngine::inspectVictimRow(victimSpan, Pattern, r);

            for (const auto& flip : flips) {
                std::cout << std::format("[!] ЗБІЙ: Рядок {}, зміщення {}, біт {} інвертовано ({} -> {})\n",
                                         flip.rowIndex, flip.byteOffset, flip.bitOffset,
                                         flip.expectedVal, flip.actualVal);
            }

            totalFlipsCount += flips.size();

            // Відновлення початкового стану у разі збою
            if (!flips.empty()) {
                std::fill_n(victim, rowhammer::MemoryHammerEngine::RowSizeBytes, Pattern);
            }
        }

        auto endTime = std::chrono::steady_clock::now();
        auto durationMs = std::chrono::duration_cast<std::chrono::milliseconds>(endTime - startTime).count();

        std::cout << std::format("[+] Сканування завершено за {} мс. Знайдено збоїв: {}\n",
                                 durationMs, totalFlipsCount);

    } catch (const std::exception& ex) {
        std::cerr << std::format("[-] Критична помилка: {}\n", ex.what());
        return EXIT_FAILURE;
    }

    return 0;
}

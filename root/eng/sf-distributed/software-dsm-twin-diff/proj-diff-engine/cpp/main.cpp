#include <cstdint>
#include <cstddef>
#include <cstring>
#include <span>
#include <vector>
#include <memory>
#include <expected>
#include <system_error>
#include <array>
#include <unistd.h>
#include <signal.h>
#include <sys/mman.h>

constexpr size_t PageSize = 4096;
constexpr size_t MaxPages = 16;

enum class PageStatus : uint8_t {
    Invalid,
    ReadOnly,
    DirtyTwinned
};

struct alignas(uint16_t) DiffHeader {
    uint16_t offset{0};
    uint16_t length{0};
};

struct DiffEntry {
    uint16_t offset{0};
    std::vector<std::byte> payload;
};

class DsmMemoryEngine {
public:
    DsmMemoryEngine() = default;
    ~DsmMemoryEngine() {
        if (m_sharedMemory != nullptr && m_sharedMemory != MAP_FAILED) {
            munmap(m_sharedMemory, m_pageCount * PageSize);
        }
    }

    DsmMemoryEngine(const DsmMemoryEngine&) = delete;
    DsmMemoryEngine& operator=(const DsmMemoryEngine&) = delete;

    std::expected<void, std::error_code> initialize(size_t pageCount) {
        if (pageCount == 0 || pageCount > MaxPages) {
            return std::unexpected(std::make_error_code(std::errc::invalid_argument));
        }

        m_pageCount = pageCount;
        const size_t totalBytes = m_pageCount * PageSize;

        void* rawMem = mmap(nullptr, totalBytes, PROT_READ,
                            MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
        if (rawMem == MAP_FAILED) {
            return std::unexpected(std::make_error_code(std::errc::not_enough_memory));
        }

        m_sharedMemory = static_cast<std::byte*>(rawMem);
        s_activeInstance = this;

        struct sigaction sa{};
        sa.sa_sigaction = &DsmMemoryEngine::signalTrampoline;
        sa.sa_flags = SA_SIGINFO | SA_NODEFER;
        sigemptyset(&sa.sa_mask);

        if (sigaction(SIGSEGV, &sa, nullptr) != 0) {
            munmap(m_sharedMemory, totalBytes);
            m_sharedMemory = nullptr;
            return std::unexpected(std::make_error_code(std::errc::permission_denied));
        }

        for (size_t i = 0; i < m_pageCount; ++i) {
            m_status[i] = PageStatus::ReadOnly;
            std::memset(m_twinPool[i].data(), 0, PageSize);
        }

        return {};
    }

    [[nodiscard]] std::span<std::byte> getPage(size_t index) noexcept {
        if (index >= m_pageCount || m_sharedMemory == nullptr) {
            return {};
        }
        return {m_sharedMemory + (index * PageSize), PageSize};
    }

    [[nodiscard]] std::vector<DiffEntry> computeDiff(size_t pageIndex) const {
        if (pageIndex >= m_pageCount || m_status[pageIndex] != PageStatus::DirtyTwinned) {
            return {};
        }

        std::vector<DiffEntry> diffs;
        const auto* pagePtr = reinterpret_cast<const uint64_t*>(m_sharedMemory + (pageIndex * PageSize));
        const auto* twinPtr = reinterpret_cast<const uint64_t*>(m_twinPool[pageIndex].data());
        constexpr size_t wordsPerPage = PageSize / sizeof(uint64_t);

        size_t w = 0;
        while (w < wordsPerPage) {
            if (pagePtr[w] == twinPtr[w]) {
                ++w;
                continue;
            }

            size_t startByte = w * sizeof(uint64_t);
            const auto* pageBytes = m_sharedMemory + (pageIndex * PageSize);
            const auto* twinBytes = m_twinPool[pageIndex].data();

            while (startByte < PageSize && pageBytes[startByte] == twinBytes[startByte]) {
                ++startByte;
            }

            size_t endByte = (w + 1) * sizeof(uint64_t);
            if (endByte > PageSize) endByte = PageSize;

            while (endByte < PageSize && pageBytes[endByte] != twinBytes[endByte]) {
                ++endByte;
            }

            DiffEntry entry;
            entry.offset = static_cast<uint16_t>(startByte);
            size_t len = endByte - startByte;
            entry.payload.resize(len);
            std::memcpy(entry.payload.data(), pageBytes + startByte, len);

            diffs.push_back(std::move(entry));
            w = (endByte / sizeof(uint64_t)) + 1;
        }

        return diffs;
    }

    void resetPageProtection(size_t pageIndex) noexcept {
        if (pageIndex < m_pageCount && m_status[pageIndex] == PageStatus::DirtyTwinned) {
            mprotect(m_sharedMemory + (pageIndex * PageSize), PageSize, PROT_READ);
            m_status[pageIndex] = PageStatus::ReadOnly;
        }
    }

    static void applyDiff(std::span<std::byte, PageSize> targetPage,
                          const std::vector<DiffEntry>& diffs) noexcept {
        for (const auto& entry : diffs) {
            if (entry.offset + entry.payload.size() <= PageSize) {
                std::memcpy(targetPage.data() + entry.offset,
                            entry.payload.data(),
                            entry.payload.size());
            }
        }
    }

private:
    static void signalTrampoline(int sig, siginfo_t* info, void* ctx) noexcept {
        if (s_activeInstance != nullptr) {
            s_activeInstance->handleFault(info->si_addr);
        }
    }

    void handleFault(void* faultAddr) noexcept {
        auto addr = reinterpret_cast<uintptr_t>(faultAddr);
        auto base = reinterpret_cast<uintptr_t>(m_sharedMemory);
        auto limit = base + (m_pageCount * PageSize);

        if (addr < base || addr >= limit) {
            const char msg[] = "SIGSEGV outside DSM bounds\n";
            write(STDERR_FILENO, msg, sizeof(msg) - 1);
            _exit(EXIT_FAILURE);
        }

        size_t pageIdx = (addr - base) / PageSize;
        if (m_status[pageIdx] == PageStatus::ReadOnly) {
            std::memcpy(m_twinPool[pageIdx].data(), m_sharedMemory + (pageIdx * PageSize), PageSize);
            if (mprotect(m_sharedMemory + (pageIdx * PageSize), PageSize, PROT_READ | PROT_WRITE) != 0) {
                const char err[] = "mprotect failed\n";
                write(STDERR_FILENO, err, sizeof(err) - 1);
                _exit(EXIT_FAILURE);
            }
            m_status[pageIdx] = PageStatus::DirtyTwinned;
        }
    }

    std::byte* m_sharedMemory{nullptr};
    size_t m_pageCount{0};
    PageStatus m_status[MaxPages]{};
    alignas(64) std::array<std::array<std::byte, PageSize>, MaxPages> m_twinPool{};
    static inline DsmMemoryEngine* s_activeInstance{nullptr};
};

#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <array>
#include <memory>
#include <chrono>
#include <expected>
#include <cstring>
#include <cstdint>

#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>

namespace wal {

constexpr uint32_t MagicHeader = 0x57414C31; // "WAL1"
constexpr size_t SectorSize = 4096;

#pragma pack(push, 1)
struct RecordHeader {
    uint32_t magic{MagicHeader};
    uint64_t lsn{0};
    uint32_t length{0};
    uint32_t crc32{0};
};
#pragma pack(pop)

// Обчислення контрольної суми CRC32 (IEEE 802.3)
uint32_t calculate_crc32(std::span<const uint8_t> data) noexcept {
    static const auto table = []() {
        std::array<uint32_t, 256> t{};
        for (uint32_t i = 0; i < 256; ++i) {
            uint32_t rem = i;
            for (int j = 0; j < 8; ++j) {
                rem = (rem & 1) ? ((rem >> 1) ^ 0xEDB88320) : (rem >> 1);
            }
            t[i] = rem;
        }
        return t;
    }();

    uint32_t crc = 0xFFFFFFFF;
    for (uint8_t byte : data) {
        crc = table[(crc ^ byte) & 0xFF] ^ (crc >> 8);
    }
    return crc ^ 0xFFFFFFFF;
}

// RAII обгортка для керування файловим дескриптором
class UniqueFd {
    int fd_{-1};
public:
    explicit UniqueFd(int fd = -1) noexcept : fd_(fd) {}
    ~UniqueFd() noexcept { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            reset();
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }
};

// RAII буфер, вирівняний під межу 4096 байтів для O_DIRECT
class AlignedBuffer {
    uint8_t* ptr_{nullptr};
    size_t size_{0};
public:
    explicit AlignedBuffer(size_t size, size_t alignment = SectorSize) : size_(size) {
        void* mem = nullptr;
        if (posix_memalign(&mem, alignment, size) != 0) {
            throw std::bad_alloc();
        }
        ptr_ = static_cast<uint8_t*>(mem);
        std::memset(ptr_, 0, size_);
    }

    ~AlignedBuffer() noexcept {
        std::free(ptr_);
    }

    AlignedBuffer(const AlignedBuffer&) = delete;
    AlignedBuffer& operator=(const AlignedBuffer&) = delete;

    AlignedBuffer(AlignedBuffer&& other) noexcept : ptr_(other.ptr_), size_(other.size_) {
        other.ptr_ = nullptr;
        other.size_ = 0;
    }

    [[nodiscard]] uint8_t* data() noexcept { return ptr_; }
    [[nodiscard]] const uint8_t* data() const noexcept { return ptr_; }
    [[nodiscard]] size_t size() const noexcept { return size_; }
    [[nodiscard]] std::span<uint8_t> as_span() noexcept { return {ptr_, size_}; }
};

enum class SyncMode {
    None,        // Буферизований запис без виклику sync
    Fdatasync,   // Буферизований запис + fdatasync
    DirectIo     // O_DIRECT + O_DSYNC на рівні дескриптора
};

struct BenchmarkResult {
    int total_tx{0};
    double elapsed_sec{0.0};
    double avg_latency_us{0.0};
    double tps{0.0};
};

// Запис транзакцій у журнал із вимірюванням затримок
std::expected<BenchmarkResult, std::string> run_benchmark(
    std::string_view filename, SyncMode mode, int total_tx) {

    int flags = O_CREAT | O_RDWR | O_TRUNC;
    if (mode == SyncMode::DirectIo) {
        flags |= O_DIRECT | O_DSYNC;
    }

    UniqueFd fd(::open(filename.data(), flags, 0644));
    if (!fd.valid()) {
        return std::unexpected("Не вдалося відкрити файл WAL: " + std::string(strerror(errno)));
    }

    AlignedBuffer buffer(SectorSize);
    uint64_t total_latency_us = 0;
    const auto start_total = std::chrono::steady_clock::now();

    for (int i = 1; i <= total_tx; ++i) {
        std::memset(buffer.data(), 0, buffer.size());
        auto* hdr = reinterpret_cast<RecordHeader*>(buffer.data());
        hdr->magic = MagicHeader;
        hdr->lsn = static_cast<uint64_t>(i);

        std::string payload = "TX=" + std::to_string(i) + ";ACTION=TRANSFER;AMOUNT=100.00;STATE=COMMITTED";
        hdr->length = static_cast<uint32_t>(payload.size());

        std::memcpy(buffer.data() + sizeof(RecordHeader), payload.data(), payload.size());
        hdr->crc32 = calculate_crc32({buffer.data() + sizeof(RecordHeader), hdr->length});

        const auto tx_start = std::chrono::steady_clock::now();

        if (mode == SyncMode::DirectIo) {
            if (::write(fd.get(), buffer.data(), SectorSize) != static_cast<ssize_t>(SectorSize)) {
                return std::unexpected("Помилка прямого запису: " + std::string(strerror(errno)));
            }
        } else {
            size_t record_len = sizeof(RecordHeader) + hdr->length;
            if (::write(fd.get(), buffer.data(), record_len) != static_cast<ssize_t>(record_len)) {
                return std::unexpected("Помилка буферизованого запису: " + std::string(strerror(errno)));
            }
            if (mode == SyncMode::Fdatasync) {
                if (::fdatasync(fd.get()) < 0) {
                    return std::unexpected("Помилка fdatasync: " + std::string(strerror(errno)));
                }
            }
        }

        const auto tx_end = std::chrono::steady_clock::now();
        total_latency_us += std::chrono::duration_cast<std::chrono::microseconds>(tx_end - tx_start).count();
    }

    const auto end_total = std::chrono::steady_clock::now();
    double elapsed = std::chrono::duration<double>(end_total - start_total).count();

    return BenchmarkResult{
        .total_tx = total_tx,
        .elapsed_sec = elapsed,
        .avg_latency_us = static_cast<double>(total_latency_us) / total_tx,
        .tps = static_cast<double>(total_tx) / elapsed
    };
}

// Сканування та валідація цілісності журналу
std::expected<uint64_t, std::string> recover_log(std::string_view filename) {
    UniqueFd fd(::open(filename.data(), O_RDONLY));
    if (!fd.valid()) {
        return std::unexpected("Не вдалося відкрити журнал для відновлення");
    }

    uint64_t valid_records = 0;
    std::vector<uint8_t> payload_buf(SectorSize);

    while (true) {
        RecordHeader hdr;
        ssize_t r = ::read(fd.get(), &hdr, sizeof(RecordHeader));
        if (r == 0) break; // Нормальний кінець файлу
        if (r < static_cast<ssize_t>(sizeof(RecordHeader))) {
            std::cout << "  [УВАГА] Неповний заголовок наприкінці. Обірваний запис.\n";
            break;
        }

        if (hdr.magic != MagicHeader) {
            std::cout << "  [ПОМИЛКА] Невідповідність Magic: пошкоджені дані.\n";
            break;
        }

        if (hdr.length > payload_buf.size()) {
            std::cout << "  [ПОМИЛКА] Недійсний розмір корисного навантаження.\n";
            break;
        }

        r = ::read(fd.get(), payload_buf.data(), hdr.length);
        if (r < static_cast<ssize_t>(hdr.length)) {
            std::cout << "  [УВАГА] Неповний блок даних транзакції. Зупинка відновлення.\n";
            break;
        }

        uint32_t actual_crc = calculate_crc32({payload_buf.data(), hdr.length});
        if (actual_crc != hdr.crc32) {
            std::cout << "  [ПОМИЛКА] Збій CRC32: дані пошкоджено на носії!\n";
            break;
        }

        valid_records++;
    }

    return valid_records;
}

} // namespace wal

int main() {
    constexpr int NumTx = 500;
    std::cout << "=== ДОСЛІДЖЕННЯ ДОВГОВІЧНОСТІ ЖУРНАЛУ (C++20) ===\n\n";

    // 1. Buffered
    std::cout << "1. Режим Buffered (без синхронізації):\n";
    if (auto res = wal::run_benchmark("wal_cpp_none.log", wal::SyncMode::None, NumTx); res) {
        std::cout << "  Транзакцій: " << res->total_tx << " | Загальний час: " << res->elapsed_sec
                  << " с | Затримка: " << res->avg_latency_us << " мкс | Продуктивність: " << res->tps << " TPS\n";
        auto rec = wal::recover_log("wal_cpp_none.log");
        std::cout << "  Відновлено валідних транзакцій: " << rec.value_or(0) << "\n\n";
    }

    // 2. Fdatasync
    std::cout << "2. Режим fdatasync (гарантована довговічність):\n";
    if (auto res = wal::run_benchmark("wal_cpp_sync.log", wal::SyncMode::Fdatasync, NumTx); res) {
        std::cout << "  Транзакцій: " << res->total_tx << " | Загальний час: " << res->elapsed_sec
                  << " с | Затримка: " << res->avg_latency_us << " мкс | Продуктивність: " << res->tps << " TPS\n";
        auto rec = wal::recover_log("wal_cpp_sync.log");
        std::cout << "  Відновлено валідних транзакцій: " << rec.value_or(0) << "\n\n";
    }

    // 3. Direct I/O
    std::cout << "3. Режим O_DIRECT + O_DSYNC (обхід кешу ядра):\n";
    if (auto res = wal::run_benchmark("wal_cpp_direct.log", wal::SyncMode::DirectIo, NumTx); res) {
        std::cout << "  Транзакцій: " << res->total_tx << " | Загальний час: " << res->elapsed_sec
                  << " с | Затримка: " << res->avg_latency_us << " мкс | Продуктивність: " << res->tps << " TPS\n";
        auto rec = wal::recover_log("wal_cpp_direct.log");
        std::cout << "  Відновлено валідних транзакцій: " << rec.value_or(0) << "\n\n";
    }

    ::unlink("wal_cpp_none.log");
    ::unlink("wal_cpp_sync.log");
    ::unlink("wal_cpp_direct.log");

    return 0;
}

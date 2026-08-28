#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <span>
#include <memory>
#include <expected>
#include <system_error>
#include <chrono>
#include <cmath>
#include <array>
#include <concepts>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <sys/prctl.h>
#include <linux/fs.h>
#include <linux/i2c-dev.h>
#include <linux/nvme_ioctl.h>

namespace sanitizer {

enum class ErrorCode {
    InvalidParameter = 1,
    MemoryLockFailed,
    DeviceIoError,
    SecureElementFailure,
    TpmFailure,
    VerificationMismatch
};

struct SanitizerErrorCategory : std::error_category {
    [[nodiscard]] const char* name() const noexcept override { return "SanitizerCategory"; }
    [[nodiscard]] std::string message(int ev) const override {
        switch (static_cast<ErrorCode>(ev)) {
            case ErrorCode::InvalidParameter: return "Некоректні вхідні параметри";
            case ErrorCode::MemoryLockFailed: return "Неможливо заблокувати пам'ять у RAM";
            case ErrorCode::DeviceIoError: return "Помилка вводу/виводу блокового пристрою";
            case ErrorCode::SecureElementFailure: return "Помилка скидання Secure Element";
            case ErrorCode::TpmFailure: return "Помилка виконання команди TPM2_Clear";
            case ErrorCode::VerificationMismatch: return "Невідповідність верифікації санітизації";
            default: return "Невідома помилка санітизації";
        }
    }
};

const SanitizerErrorCategory& sanitizer_category() noexcept {
    static SanitizerErrorCategory instance;
    return instance;
}

std::error_code make_error_code(ErrorCode e) {
    return {static_cast<int>(e), sanitizer_category()};
}

/* Безпечний алокатор пам'яті, захищений від вивантаження у swap та скидання у дамп */
template <typename T>
class SecureLockedAllocator {
public:
    using value_type = T;

    SecureLockedAllocator() noexcept = default;
    template <typename U> SecureLockedAllocator(const SecureLockedAllocator<U>&) noexcept {}

    T* allocate(std::size_t n) {
        std::size_t bytes = n * sizeof(T);
        void* ptr = ::mmap(nullptr, bytes, PROT_READ | PROT_WRITE,
                           MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
        if (ptr == MAP_FAILED) {
            throw std::bad_alloc();
        }

        if (::mlock(ptr, bytes) != 0) {
            ::munmap(ptr, bytes);
            throw std::bad_alloc();
        }

        if (::madvise(ptr, bytes, MADV_DONTDUMP) != 0) {
            ::munlock(ptr, bytes);
            ::munmap(ptr, bytes);
            throw std::bad_alloc();
        }

        ::prctl(PR_SET_DUMPABLE, 0);
        return static_cast<T*>(ptr);
    }

    void deallocate(T* p, std::size_t n) noexcept {
        if (!p) return;
        std::size_t bytes = n * sizeof(T);
        
        volatile auto* vptr = reinterpret_cast<volatile std::byte*>(p);
        for (std::size_t i = 0; i < bytes; ++i) {
            vptr[i] = std::byte{0};
        }
        #if defined(__GNUC__) || defined(__clang__)
        asm volatile("" : : "r"(p) : "memory");
        #endif

        ::munlock(p, bytes);
        ::munmap(p, bytes);
    }
};

using SecureByteBuffer = std::vector<std::byte, SecureLockedAllocator<std::byte>>;

/* Інтерфейс для апаратних контролерів накопичувачів */
class IStorageTarget {
public:
    virtual ~IStorageTarget() = default;
    [[nodiscard]] virtual std::expected<void, std::error_code> purge_media() = 0;
    [[nodiscard]] virtual std::expected<SecureByteBuffer, std::error_code> read_sample_block(std::size_t size) = 0;
    [[nodiscard]] virtual std::string_view path() const noexcept = 0;
};

/* Реалізація для контролера NVMe */
class NvmeStorageTarget final : public IStorageTarget {
public:
    explicit NvmeStorageTarget(std::string device_path) : path_(std::move(device_path)) {}

    [[nodiscard]] std::expected<void, std::error_code> purge_media() override {
        int fd = ::open(path_.c_str(), O_RDWR | O_NONBLOCK);
        if (fd < 0) {
            return std::unexpected(make_error_code(ErrorCode::DeviceIoError));
        }

        struct nvme_admin_cmd cmd{};
        cmd.opcode = 0x84; /* NVMe Admin Sanitize */
        cmd.cdw10 = 0x04;   /* Crypto Erase */

        if (::ioctl(fd, NVME_IOCTL_ADMIN_CMD, &cmd) < 0) {
            ::close(fd);
            return std::unexpected(make_error_code(ErrorCode::DeviceIoError));
        }

        ::close(fd);
        return {};
    }

    [[nodiscard]] std::expected<SecureByteBuffer, std::error_code> read_sample_block(std::size_t size) override {
        int fd = ::open(path_.c_str(), O_RDONLY | O_DIRECT);
        if (fd < 0) {
            fd = ::open(path_.c_str(), O_RDONLY);
            if (fd < 0) return std::unexpected(make_error_code(ErrorCode::DeviceIoError));
        }

        SecureByteBuffer buffer(size);
        ssize_t read_bytes = ::read(fd, buffer.data(), size);
        ::close(fd);

        if (read_bytes < 0) {
            return std::unexpected(make_error_code(ErrorCode::DeviceIoError));
        }

        buffer.resize(static_cast<std::size_t>(read_bytes));
        return buffer;
    }

    [[nodiscard]] std::string_view path() const noexcept override { return path_; }

private:
    std::string path_;
};

/* Структура сертифіката санітизації */
struct CertificateOfSanitization {
    std::string device_uuid;
    std::string target_media;
    std::chrono::system_clock::time_point timestamp;
    double measured_entropy;
    bool crypto_shredded;
    bool verification_passed;
};

/* Оцінювач ентропії за формулою Шеннона */
class EntropyEvaluator {
public:
    [[nodiscard]] static double evaluate(std::span<const std::byte> data) noexcept {
        if (data.empty()) return 0.0;
        std::array<std::size_t, 256> counts{};
        for (auto b : data) {
            counts[static_cast<uint8_t>(b)]++;
        }

        double entropy = 0.0;
        double total = static_cast<double>(data.size());
        for (auto c : counts) {
            if (c > 0) {
                double p = static_cast<double>(c) / total;
                entropy -= p * std::log2(p);
            }
        }
        return entropy;
    }
};

/* Головний сервіс санітизації */
class SanitizationEngine {
public:
    explicit SanitizationEngine(std::unique_ptr<IStorageTarget> target) 
        : target_(std::move(target)) {}

    [[nodiscard]] std::expected<CertificateOfSanitization, std::error_code> execute() {
        if (!target_) {
            return std::unexpected(make_error_code(ErrorCode::InvalidParameter));
        }

        CertificateOfSanitization cert{
            .device_uuid = "HW-SRV-984210",
            .target_media = std::string(target_->path()),
            .timestamp = std::chrono::system_clock::now(),
            .measured_entropy = 0.0,
            .crypto_shredded = false,
            .verification_passed = false
        };

        // 1. Виконання апаратного криптостирання
        auto purge_res = target_->purge_media();
        if (!purge_res) {
            return std::unexpected(purge_res.error());
        }
        cert.crypto_shredded = true;

        // 2. Верифікаційний прохід
        auto sample_res = target_->read_sample_block(1024 * 1024);
        if (!sample_res) {
            return std::unexpected(sample_res.error());
        }

        cert.measured_entropy = EntropyEvaluator::evaluate(*sample_res);

        // Перевірка: чи є вміст ідеальним шумом (~8.0) або чистими нулями (<0.01)
        if (cert.measured_entropy > 7.99 || cert.measured_entropy < 0.01) {
            cert.verification_passed = true;
            return cert;
        }

        return std::unexpected(make_error_code(ErrorCode::VerificationMismatch));
    }

private:
    std::unique_ptr<IStorageTarget> target_;
};

} // namespace sanitizer

int main() {
    auto nvme = std::make_unique<sanitizer::NvmeStorageTarget>("/dev/nvme0n1");
    sanitizer::SanitizationEngine engine(std::move(nvme));

    auto result = engine.execute();
    if (result) {
        std::cout << "[SUCCESS] Санітизація успішна. Ентропія: " 
                  << result->measured_entropy << std::endl;
    } else {
        std::cerr << "[FAIL] Помилка: " << result.error().message() << std::endl;
        return 1;
    }
    return 0;
}

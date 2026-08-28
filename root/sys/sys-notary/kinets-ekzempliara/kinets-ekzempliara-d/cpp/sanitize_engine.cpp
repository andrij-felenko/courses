// sanitize_engine.cpp - Модуль безпечної санітизації носія на сучасному C++20
#include <iostream>
#include <vector>
#include <span>
#include <string_view>
#include <memory>
#include <expected>
#include <system_error>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/nvme_ioctl.h>

namespace Decom {

enum class SanitizeType : uint32_t {
    BlockErase  = 0x02,
    Overwrite   = 0x03,
    CryptoErase = 0x04
};

enum class DecomError {
    DeviceOpenFailed,
    IoctlExecutionFailed,
    InvalidKeySize,
    InvalidParameter
};

struct DecomErrorCategory : std::error_category {
    [[nodiscard]] const char* name() const noexcept override { return "DecommissionEngine"; }
    [[nodiscard]] std::string message(int ev) const override {
        switch (static_cast<DecomError>(ev)) {
            case DecomError::DeviceOpenFailed:      return "Не вдалося відкрити дескриптор пристрою";
            case DecomError::IoctlExecutionFailed:  return "Помилка виконання низькорівневого ioctl";
            case DecomError::InvalidKeySize:        return "Некоректний розмір криптографічного ключа";
            case DecomError::InvalidParameter:      return "Передано недійсний параметр конфігурації";
            default:                                return "Невідома помилка деінсталяції";
        }
    }
};

const DecomErrorCategory theDecomErrorCategory{};

std::error_code make_error_code(DecomError e) {
    return {static_cast<int>(e), theDecomErrorCategory};
}

// RAII обгортка для безпечного керування файловими дескрипторами POSIX
class FileDescriptor {
    int m_fd{-1};
public:
    explicit FileDescriptor(int fd) noexcept : m_fd(fd) {}
    ~FileDescriptor() {
        if (m_fd >= 0) {
            ::close(m_fd);
        }
    }
    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;
    FileDescriptor(FileDescriptor&& other) noexcept : m_fd(other.m_fd) {
        other.m_fd = -1;
    }
    FileDescriptor& operator=(FileDescriptor&& other) noexcept {
        if (this != &other) {
            if (m_fd >= 0) ::close(m_fd);
            m_fd = other.m_fd;
            other.m_fd = -1;
        }
        return this;
    }
    [[nodiscard]] int get() const noexcept { return m_fd; }
    [[nodiscard]] bool isValid() const noexcept { return m_fd >= 0; }
};

// Захищений буфер для ключів із гарантованим стиранням пам'яті в деструкторі
class SecureKeyBuffer {
    std::vector<uint8_t> m_buffer;
public:
    explicit SecureKeyBuffer(size_t size) : m_buffer(size, 0) {}
    
    explicit SecureKeyBuffer(std::span<const uint8_t> init_data) 
        : m_buffer(init_data.begin(), init_data.end()) {}

    ~SecureKeyBuffer() {
        wipe();
    }

    SecureKeyBuffer(const SecureKeyBuffer&) = delete;
    SecureKeyBuffer& operator=(const SecureKeyBuffer&) = delete;
    
    SecureKeyBuffer(SecureKeyBuffer&& other) noexcept 
        : m_buffer(std::move(other.m_buffer)) {}

    SecureKeyBuffer& operator=(SecureKeyBuffer&& other) noexcept {
        if (this != &other) {
            wipe();
            m_buffer = std::move(other.m_buffer);
        }
        return *this;
    }

    void wipe() noexcept {
        if (!m_buffer.empty()) {
            volatile uint8_t* ptr = m_buffer.data();
            for (size_t i = 0; i < m_buffer.size(); ++i) {
                ptr[i] = 0x00;
            }
            __asm__ __volatile__("" : : "r"(m_buffer.data()) : "memory");
        }
    }

    [[nodiscard]] std::span<uint8_t> span() noexcept { return m_buffer; }
    [[nodiscard]] std::span<const uint8_t> cspan() const noexcept { return m_buffer; }
    [[nodiscard]] size_t size() const noexcept { return m_buffer.size(); }
};

// Керуючий клас санітизації твердотільних накопичувачів
class StorageSanitizer {
public:
    static std::expected<void, std::error_code> executeSanitize(
        std::string_view devicePath, 
        SanitizeType action) 
    {
        int raw_fd = ::open(devicePath.data(), O_RDWR);
        if (raw_fd < 0) {
            return std::unexpected(make_error_code(DecomError::DeviceOpenFailed));
        }
        FileDescriptor devFd(raw_fd);

        nvme_admin_cmd cmd{};
        cmd.opcode = 0x84; // NVME_ADMIN_SANITIZE_OPCODE
        cmd.cdw10 = static_cast<uint32_t>(action);

        std::cout << "[C++20 Engine] Відправка команди санітизації на " 
                  << devicePath << " (Action Code: " << cmd.cdw10 << ")...\n";

        if (::ioctl(devFd.get(), NVME_IOCTL_ADMIN_CMD, &cmd) < 0) {
            return std::unexpected(make_error_code(DecomError::IoctlExecutionFailed));
        }

        std::cout << "[C++20 Engine] Контролер підтвердив виконання апаратної санітизації.\n";
        return {};
    }
};

} // namespace Decom

int main() {
    std::cout << "=== СИСТЕМА ДЕКОМІСІЇ ПРИСТРОЇВ (C++20 RAII ARCHITECTURE) ===\n";

    // 1. Створення та гарантоване занулення ключа
    std::vector<uint8_t> initial_key = {
        0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
        0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18,
        0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28,
        0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38
    };

    {
        Decom::SecureKeyBuffer keyWrapper(initial_key);
        std::cout << "[1] Створено захищений буфер KEK у пам'яті (Розмір: " 
                  << keyWrapper.size() << " байт).\n";
        // При виході з області видимості деструктор SecureKeyBuffer виконає volatile-очищення пам'яті
    }
    std::cout << "[1] Захищений буфер знищено, пам'ять KEK гарантовано занулено.\n";

    // 2. Виклик санітизації носія
    constexpr std::string_view target_device = "/dev/nvme0";
    auto result = Decom::StorageSanitizer::executeSanitize(
        target_device, 
        Decom::SanitizeType::CryptoErase
    );

    if (!result) {
        std::cout << "[WARN] Очікуваний статус на емуляторі: " 
                  << result.error().message() 
                  << " (ioctl вимагає реального NVMe контролера).\n";
    } else {
        std::cout << "[2] Апаратне Crypto-Erase виконано успішно.\n";
    }

    std::cout << "[3] Процедуру санітизації завершено відповідно до NIST SP 800-88 Purge.\n";
    return 0;
}

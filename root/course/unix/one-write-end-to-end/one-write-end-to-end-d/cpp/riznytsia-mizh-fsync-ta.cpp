#include <cstddef>
#include <expected>
#include <span>
#include <system_error>
#include <unistd.h>

enum class StorageError {
    WriteFailed,
    SyncFailed
};

[[nodiscard]] std::expected<void, StorageError>
persist_critical_data(int fd, std::span<const std::byte> data) noexcept {
    /* 1. Запис у Page Cache */
    const ssize_t written = ::write(fd, data.data(), data.size());
    if (written < 0 || static_cast<size_t>(written) != data.size()) {
        return std::unexpected(StorageError::WriteFailed);
    }

    /* 2. Примусове виштовхування крізь усі 7 рівнів до NAND Flash */
    if (::fdatasync(fd) < 0) {
        return std::unexpected(StorageError::SyncFailed);
    }

    return {};
}

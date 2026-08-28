#include <memory_resource>
#include <expected>

// Тип контейнера, що використовує локальну арену пам'яті
using PmrString = std::pmr::string;

std::expected<PmrString, SystemError> fast_read_config(std::pmr::memory_resource* arena) {
    PmrString buffer(arena);
    buffer.reserve(512);
    
    if (!read_into_buffer(buffer)) {
        return std::unexpected(SystemError::ReadFailed);
    }
    return buffer; // Повертає рядок, створений у виділеній арені пам'яті
}

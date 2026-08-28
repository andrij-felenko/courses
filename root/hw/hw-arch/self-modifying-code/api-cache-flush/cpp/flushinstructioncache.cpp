#include <windows.h>
#include <processthreadsapi.h>
#include <span>
#include <expected>
#include <system_error>

inline std::expected<void, DWORD> flush_instruction_cache(
    HANDLE process_handle, std::span<const uint8_t> memory_range) noexcept {
    BOOL ok = FlushInstructionCache(process_handle, memory_range.data(), memory_range.size());
    if (!ok) {
        return std::unexpected(GetLastError());
    }
    return {};
}

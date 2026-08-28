#include <cstdint>
#include <span>

enum class LogLevel : uint8_t {
    Trace = 0,
    Debug = 1,
    Info  = 2,
    Warn  = 3,
    Error = 4,
    Fatal = 5
};

inline constexpr LogLevel CompileLogLevel = LogLevel::Info;
inline LogLevel RuntimeLogLevel = LogLevel::Info;

template <LogLevel Level>
inline void logEmit(uint8_t moduleId, uint32_t tokenId, std::span<const uint8_t> payload = {}) {
    if constexpr (Level >= CompileLogLevel) {
        if (Level >= RuntimeLogLevel) {
            logBackendWrite(static_cast<uint8_t>(Level), moduleId, tokenId, payload.data(), static_cast<uint8_t>(payload.size()));
        }
    }
}

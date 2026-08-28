#include <cstdint>
#include <span>

/* Типізована C++20 структура діагностичного дампу пам'яті */
struct alignas(4) CrashDump {
    static constexpr uint32_t MagicHeader = 0xDEADBEEF;

    uint32_t magicHeader{0};
    uint32_t resetFlags{0};
    uint16_t lastTimerTicks{0};
    uint16_t lastHeartbeat{0};
    uint8_t  activeTaskId{0};
    uint8_t  lastErrorCode{0};
    uint32_t crc32{0};

    [[nodiscard]] bool isValid() const noexcept {
        return magicHeader == MagicHeader;
    }
};

// Розміщення в спеціальній секції пам'яті без ініціалізації нулями
[[gnu::section(".noinit")]] volatile CrashDump g_crashDump;

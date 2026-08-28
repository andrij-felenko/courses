#include <iostream>
#include <chrono>
#include <compare>
#include <cstdint>

struct TelemetryPacket {
    std::chrono::system_clock::time_point timestamp;
    uint32_t sequence_id{0};
    uint8_t  priority{0};

    // 1. Рівність за унікальним послідовним номером
    bool operator==(const TelemetryPacket& o) const noexcept {
        return sequence_id == o.sequence_id && timestamp == o.timestamp;
    }

    // 2. Впорядкування за хронологією та пріоритетом
    std::strong_ordering operator<=>(const TelemetryPacket& o) const noexcept {
        // Хронологічний порядок часу (раніші пакети йдуть попереду)
        if (auto cmp = timestamp <=> o.timestamp; cmp != 0) {
            return cmp;
        }
        // Вищий пріоритет іде попереду (сортування за спаданням через перестановку операндів)
        if (auto cmp = o.priority <=> priority; cmp != 0) {
            return cmp;
        }
        return sequence_id <=> o.sequence_id;
    }
};

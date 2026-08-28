// dispatch-bench.cpp — c++17
//   g++ -O2 -std=c++17 dispatch-bench.cpp -o dispatch-bench
#include <array>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <utility>
#include <vector>

constexpr uint32_t MSG_HEARTBEAT    = 0;
constexpr uint32_t MSG_RADIO_STATUS = 109;

// Розкладка поле-в-поле збігається з mavlink_message_t — отже, і вага.
struct Message {
    uint16_t checksum;
    uint8_t  magic, len, incompat_flags, compat_flags, seq, sysid, compid;
    uint32_t msgid : 24;
    uint64_t payload64[(255 + 2 + 7) / 8];
    uint8_t  ck[2];
    uint8_t  signature[13];
};
static_assert(sizeof(Message) == 296, "розкладка розійшлася з mavlink_message_t");

struct Vehicle {
    int         sysid              = 0;
    int         defaultComponentId = 1;      // MAV_COMP_ID_AUTOPILOT1
    const void *link               = nullptr;
    uint64_t    accepted           = 0;

    bool usesLink(const void *l) const { return l == link; }

    void onMessage(const void *l, const Message &m) {
        // Перший рівень: чи взагалі мій номер системи.
        if (m.sysid != sysid && m.sysid != 0) {
            if (!(m.msgid == MSG_RADIO_STATUS && usesLink(l))) {
                return;
            }
        }
        // Другий рівень: чи це автопілот, а не підвіс під тим самим номером.
        // У застосунку ця перевірка стоїть у кожному обробнику окремо.
        if (m.compid != defaultComponentId) {
            return;
        }
        accepted += m.len;                   // «робота» замість справжнього тіла
    }
};

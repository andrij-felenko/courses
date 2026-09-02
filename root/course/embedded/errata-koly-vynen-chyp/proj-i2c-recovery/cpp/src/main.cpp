#include "bus_recovery.hpp"
#include "i2c1.hpp"
#include "timing.hpp"

#include <cstdint>
#include <optional>

namespace {

constexpr std::uint8_t kSensorAddr = 0x68U;   /* давач на шині зв'язкового модуля */
constexpr std::uint8_t kWhoAmI = 0x75U;       /* регістр-візитівка: значення відоме наперед */
constexpr std::uint32_t kBusSpeedHz = 100'000U;

/* Лічильники навмисно volatile: о другій ночі єдиний спосіб побачити картину —
   спинити налагоджувач і подивитися, скільки разів шину довелося рятувати. */
struct Stats {
    std::uint32_t reads_ok;
    std::uint32_t nacks;
    std::uint32_t recoveries;
    std::uint32_t recovery_pulses;
    std::uint32_t fatal;
    std::uint8_t last_who_am_i;
};

volatile Stats g_stats{};

/* Драйвер живе в optional саме заради відновлення: перед ручним тактуванням
   об'єкт знищується (деструктор гасить передавач), після — створюється заново. */
void bring_bus_up(std::optional<hw::I2c1>& bus) noexcept {
    bus.reset();
    g_stats.recoveries = g_stats.recoveries + 1U;

    const auto report = hw::recover_i2c1_bus();
    if (!report) {
        /* Модуль лишився у скиданні. Далі має йти людина з осцилографом:
           програмно з короткого замикання шину не витягнути. */
        g_stats.fatal = g_stats.fatal + 1U;
        return;
    }

    g_stats.recovery_pulses = g_stats.recovery_pulses + report->pulses;
    bus.emplace(kBusSpeedHz);
}

} // namespace

int main() {
    bsp::init_timing();

    std::optional<hw::I2c1> bus;

    /* Починаємо з відновлення, ще не спробувавши жодної транзакції: скидання від
       сторожового таймера посеред читання байта лишає ведений чип із притиснутою
       SDA, і перше ж звертання стане в BUSY. */
    bring_bus_up(bus);

    for (;;) {
        if (!bus) {
            /* Шина не піднялася — пробуємо ще раз, повільно, без штурму */
            bsp::delay(1'000'000us);
            bring_bus_up(bus);
            continue;
        }

        const auto value = bus->read_register(kSensorAddr, kWhoAmI);
        if (value) {
            g_stats.reads_ok = g_stats.reads_ok + 1U;
            g_stats.last_who_am_i = *value;
        } else if (value.error() == hw::I2cError::Nack) {
            /* Шина жива, просто ніхто не озвався на цю адресу — рятувати нічого */
            g_stats.nacks = g_stats.nacks + 1U;
        } else {
            bring_bus_up(bus);
        }

        bsp::delay(100'000us);   /* 100 мс між опитуваннями */
    }
}

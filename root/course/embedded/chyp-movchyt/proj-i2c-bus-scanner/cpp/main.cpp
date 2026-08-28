/* Обслуговування шини I2C: сучасний C++20 з RAII та концептами */
#include <cstdint>
#include <cstdio>
#include <concepts>
#include <span>
#include <vector>
#include <optional>

/* Концепт для низькорівневих апаратних маніпуляцій лініями */
template <typename T>
concept I2CPinDriver = requires(T io, bool level, uint32_t us) {
    { io.set_scl_output() } -> std::same_as<void>;
    { io.set_scl_level(level) } -> std::same_as<void>;
    { io.read_sda_level() } -> std::same_as<bool>;
    { io.set_sda_output() } -> std::same_as<void>;
    { io.set_sda_level(level) } -> std::same_as<void>;
    { io.restore_peripheral() } -> std::same_as<void>;
    { io.delay_us(us) } -> std::same_as<void>;
};

/* Клас діагностики та обслуговування I2C шини */
template <I2CPinDriver Driver>
class I2CBusDiagnostics {
public:
    explicit I2CBusDiagnostics(Driver& driver) : driver_(driver) {}

    /* Виведення шини із зависання через 9 тактів SCL */
    [[nodiscard]] bool recover_bus() {
        if (driver_.read_sda_level()) {
            return true; /* Лінія вільна */
        }

        driver_.set_scl_output();
        driver_.set_scl_level(true);
        driver_.delay_us(5);

        bool sda_cleared = false;
        for (std::size_t i = 0; i < 9; ++i) {
            driver_.set_scl_level(false);
            driver_.delay_us(5);
            driver_.set_scl_level(true);
            driver_.delay_us(5);

            if (driver_.read_sda_level()) {
                sda_cleared = true;
                break;
            }
        }

        if (!sda_cleared) {
            driver_.restore_peripheral();
            return false; /* Апаратна несправність: SDA замкнена на GND */
        }

        /* Формування аварійного STOP сигналу */
        driver_.set_sda_output();
        driver_.set_sda_level(false);
        driver_.delay_us(5);
        driver_.set_scl_level(true);
        driver_.delay_us(5);
        driver_.set_sda_level(true);
        driver_.delay_us(5);

        driver_.restore_peripheral();
        return true;
    }

    /* Сканування простору 7-бітних адрес */
    template <typename PingCallable>
    requires std::predicate<PingCallable, std::uint8_t>
    [[nodiscard]] std::vector<std::uint8_t> scan_bus(PingCallable&& ping) {
        std::vector<std::uint8_t> found_devices;
        found_devices.reserve(8);

        std::printf("I2C Scanner: початок перебору 0x08..0x77\r\n");

        for (std::uint8_t addr = 0x08; addr <= 0x77; ++addr) {
            if (ping(addr)) {
                found_devices.push_back(addr);
                std::printf(" -> Пристрій відповідає: 7-біт: 0x%02X | 8-біт WR: 0x%02X\r\n",
                            addr, static_cast<std::uint8_t>(addr << 1));
            }
        }

        std::printf("Знайдено активних вузлів: %zu\r\n", found_devices.size());
        return found_devices;
    }

private:
    Driver& driver_;
};

#include <cstdint>
#include <array>
#include <expected>
#include <span>

enum class BringupError : uint8_t {
    BusFaultAllOnes,          // 0xFF: Обрив ліній, немає живлення, лінія в підтяжці
    BusFaultAllZeros,         // 0x00: Коротке замикання на GND, зависла шина I2C
    SpiModeMismatch,          // Зсув бітів: невідповідність CPOL / CPHA
    UnexpectedDeviceModel,    // Невідповідний ID ревізії чи підробка
    ScratchpadLoopbackFailed, // Помилка читання-запису конфігураційного регістра
    CommunicationTimeout      // Тайм-аут фізичного рівня шини
};

struct DeviceDescriptor {
    uint8_t who_am_i_reg;
    uint8_t expected_id;
    uint8_t scratchpad_reg;
};

struct ValidationSuccess {
    uint8_t validated_id;
    bool    scratchpad_passed;
};

// Абстрактний інтерфейс периферійної шини (RAII / C++ Concept)
class IBusInterface {
public:
    virtual ~IBusInterface() = default;
    [[nodiscard]] virtual bool read_register(uint8_t reg, uint8_t& out_val) noexcept = 0;
    [[nodiscard]] virtual bool write_register(uint8_t reg, uint8_t val) noexcept = 0;
    virtual void delay_ms(uint32_t ms) noexcept = 0;
};

class ChipBringupValidator {
public:
    [[nodiscard]] static std::expected<ValidationSuccess, BringupError> 
    validate(IBusInterface& bus, const DeviceDescriptor& desc) noexcept {
        // 1. Апаратна пауза на час наростання живлення (t_POR)
        bus.delay_ms(15);

        // 2. Зчитування WHO_AM_I з фільтром короткочасних збоїв
        uint8_t received_id = 0;
        bool is_read_ok = false;
        
        for (uint32_t attempt = 0; attempt < 5; ++attempt) {
            if (bus.read_register(desc.who_am_i_reg, received_id)) {
                is_read_ok = true;
                break;
            }
            bus.delay_ms(2);
        }

        if (!is_read_ok) {
            return std::unexpected(BringupError::CommunicationTimeout);
        }

        // 3. Аналіз апаратних аварійних кодів шини
        if (received_id == 0xFF) {
            return std::unexpected(BringupError::BusFaultAllOnes);
        }
        if (received_id == 0x00) {
            return std::unexpected(BringupError::BusFaultAllZeros);
        }

        // 4. Перевірка помилки полярності та фази тактування SPI
        const uint8_t shifted_left  = static_cast<uint8_t>(desc.expected_id << 1);
        const uint8_t shifted_right = static_cast<uint8_t>(desc.expected_id >> 1);
        if (received_id == shifted_left || received_id == shifted_right) {
            return std::unexpected(BringupError::SpiModeMismatch);
        }

        // 5. Перевірка точного збігу ідентифікатора
        if (received_id != desc.expected_id) {
            return std::unexpected(BringupError::UnexpectedDeviceModel);
        }

        // 6. Повнодуплексна валідація тригерів комірки Scratchpad
        constexpr std::array<uint8_t, 4> TestPatterns = {0x55, 0xAA, 0x00, 0xFF};
        uint8_t backup_val = 0;
        bus.read_register(desc.scratchpad_reg, backup_val);

        for (uint8_t pattern : TestPatterns) {
            uint8_t readback = 0;
            bus.write_register(desc.scratchpad_reg, pattern);
            bus.read_register(desc.scratchpad_reg, readback);

            if (readback != pattern) {
                // Відновлюємо початковий стан перед звітуванням про помилку
                bus.write_register(desc.scratchpad_reg, backup_val);
                return std::unexpected(BringupError::ScratchpadLoopbackFailed);
            }
        }

        // Відновлюємо конфігурацію після успішного тесту
        bus.write_register(desc.scratchpad_reg, backup_val);

        return ValidationSuccess{
            .validated_id = received_id,
            .scratchpad_passed = true
        };
    }
};

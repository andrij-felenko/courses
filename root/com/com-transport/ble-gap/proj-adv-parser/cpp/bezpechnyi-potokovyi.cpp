#include <cstdint>
#include <cstddef>
#include <string_view>
#include <span>
#include <optional>
#include <functional>

enum class BleAdType : uint8_t {
    Flags                = 0x01,
    Uuid16Incomplete     = 0x02,
    Uuid16Complete       = 0x03,
    Uuid32Incomplete     = 0x04,
    Uuid32Complete       = 0x05,
    Uuid128Incomplete    = 0x06,
    Uuid128Complete      = 0x07,
    ShortLocalName       = 0x08,
    CompleteLocalName    = 0x09,
    TxPowerLevel         = 0x0A,
    SlaveConnInterval    = 0x12,
    ServiceData16        = 0x16,
    Appearance           = 0x19,
    AdvInterval          = 0x1A,
    ManufacturerSpecific = 0xFF
};

struct BleAdElement {
    BleAdType                   type;
    std::span<const uint8_t>    data;

    [[nodiscard]] std::string_view as_string_view() const noexcept {
        return {reinterpret_cast<const char*>(data.data()), data.size()};
    }
};

class BleAdParser {
public:
    using ElementVisitor = std::function<bool(const BleAdElement&)>;

    /**
     * @brief Безпечний розбір сирого масиву рекламних даних через std::span.
     * @param payload Діапазон байтів рекламного кадру.
     * @param visitor Функція-обробник. Повертає false для зупинки.
     * @return Кількість валідних елементів.
     */
    static size_t for_each(std::span<const uint8_t> payload, const ElementVisitor& visitor) {
        if (payload.empty()) {
            return 0;
        }

        size_t offset = 0;
        size_t parsed_count = 0;

        while (offset < payload.size()) {
            const uint8_t length = payload[offset];

            if (length == 0) {
                break; // Досягнуто нульового заповнювача
            }

            // Перевірка цілісності: чи вміщується задекларований блок у залишок пам'яті
            if (offset + 1 + length > payload.size()) {
                break; // Захист від зловмисних чи пошкоджених пакетів
            }

            BleAdElement element{
                .type = static_cast<BleAdType>(payload[offset + 1]),
                .data = payload.subspan(offset + 2, length - 1)
            };

            parsed_count++;

            if (!visitor(element)) {
                break;
            }

            offset += (1 + length);
        }

        return parsed_count;
    }
};

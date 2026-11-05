#include <cstdint>
#include <array>

// Шаблонний клас драйвера 74HC165 для вбудованих систем C++
template <std::size_t NumChips>
class ShiftRegister165 {
public:
    // Структура для передачі покажчиків на апаратні периферійні функції
    struct HardwareInterface {
        void (*setPL)(bool high);
        void (*setCP)(bool high);
        bool (*readQ7)();
        void (*delayUs)(uint32_t us);
    };

    explicit ShiftRegister165(const HardwareInterface& hw) : m_hw(hw) {}

    // Ініціалізація вихідного стану керуючих ліній
    void init() const {
        m_hw.setPL(true);
        m_hw.setCP(false);
    }

    // Зчитування повного стану всіх каскадованих регістрів
    std::array<uint8_t, NumChips> readAll() const {
        std::array<uint8_t, NumChips> resultData{};

        // Засув паралельних входів асинхронним імпульсом PL
        latchInputs();

        // Прохід по всіх мікросхемах каскаду
        for (std::size_t i = 0; i < NumChips; ++i) {
            // Зберігаємо дані від останньої мікросхеми до першої
            std::size_t chipIndex = NumChips - 1 - i;
            resultData[chipIndex] = readSingleByte();
        }

        return resultData;
    }

    // Зчитування конкретного біта за його глобальним індексом (0 .. NumChips*8 - 1)
    bool getBitState(const std::array<uint8_t, NumChips>& data, std::size_t globalBitIndex) const {
        if (globalBitIndex >= NumChips * 8) {
            return false;
        }
        std::size_t chipIdx = globalBitIndex / 8;
        std::size_t bitIdx = globalBitIndex % 8;
        return (data[chipIdx] & (1U << bitIdx)) != 0;
    }

private:
    HardwareInterface m_hw;

    void latchInputs() const {
        m_hw.setPL(false);
        m_hw.delayUs(1);
        m_hw.setPL(true);
        m_hw.delayUs(1);
    }

    uint8_t readSingleByte() const {
        uint8_t value = 0;
        for (uint8_t bit = 0; bit < 8; ++bit) {
            value <<= 1;
            if (m_hw.readQ7()) {
                value |= 0x01;
            }
            m_hw.setCP(true);
            m_hw.delayUs(1);
            m_hw.setCP(false);
            m_hw.delayUs(1);
        }
        return value;
    }
};

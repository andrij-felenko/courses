#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <expected>
#include <algorithm>

/* Перелік статусів помилок драйвера */
enum class DaisyError {
    InvalidParameter,
    BusBusy,
    LoopbackFault,
    HardwareTimeout
};

/* Апаратний інтерфейс низького рівня (HAL Concept / Interface) */
class ISpiHal {
public:
    virtual ~ISpiHal() = default;
    virtual void setCs(bool active) = 0;
    virtual void delayNs(std::uint32_t ns) = 0;
    virtual bool transfer(std::span<const std::uint8_t> tx, std::span<std::uint8_t> rx) = 0;
};

/* Шаблонний драйвер каскаду з фіксованою кількістю пристроїв */
template <std::size_t NumDevices, typename WordType = std::uint16_t>
class DaisyChainDriver {
    static_assert(NumDevices > 0 && NumDevices <= 32, "Кількість пристроїв має бути від 1 до 32");
    static_assert(sizeof(WordType) == 2, "Підтримуються 16-бітні слова даних");

public:
    static constexpr std::size_t ByteCount = NumDevices * sizeof(WordType);

    explicit DaisyChainDriver(ISpiHal& hal) : m_hal(hal) {
        m_shadowTx.fill(0);
        m_shadowRx.fill(0);
        m_hal.setCs(false);
    }

    /* Встановлення значення виходу конкретної мікросхеми в тіньовому буфері */
    void setDeviceValue(std::size_t index, WordType value) noexcept {
        if (index < NumDevices) {
            m_shadowTx[index] = value;
        }
    }

    /* Зчитування останнього отриманого стану конкретної мікросхеми */
    [[nodiscard]] WordType getDeviceFeedback(std::size_t index) const noexcept {
        return (index < NumDevices) ? m_shadowRx[index] : WordType{0};
    }

    /* Виконання синхронного обміну кадру крізь увесь каскад */
    std::expected<void, DaisyError> syncTransaction() noexcept {
        // Формування реверсного апаратного буфера передачі (IC_N передається першим)
        for (std::size_t i = 0; i < NumDevices; ++i) {
            std::size_t revIdx = (NumDevices - 1) - i;
            WordType word = m_shadowTx[revIdx];
            m_rawTx[i * 2 + 0] = static_cast<std::uint8_t>(word >> 8);
            m_rawTx[i * 2 + 1] = static_cast<std::uint8_t>(word & 0xFF);
        }

        // Апаратний фреймінг: активуємо лінію CS (Active Low)
        m_hal.setCs(true);
        m_hal.delayNs(50); // t_setup(CS)

        bool ok = m_hal.transfer(std::span<const std::uint8_t>(m_rawTx),
                                 std::span<std::uint8_t>(m_rawRx));
        if (!ok) {
            m_hal.setCs(false);
            return std::unexpected(DaisyError::BusBusy);
        }

        // Завершення кадру: фіксація даних вихідними засувками мікросхем (Latch)
        m_hal.delayNs(50); // t_hold(CS)
        m_hal.setCs(false);
        m_hal.delayNs(100); // t_pulse(CS_High)

        // Розпакування зчитаних слів зворотного потоку
        for (std::size_t i = 0; i < NumDevices; ++i) {
            std::size_t revIdx = (NumDevices - 1) - i;
            auto hi = static_cast<WordType>(m_rawRx[i * 2 + 0]);
            auto lo = static_cast<WordType>(m_rawRx[i * 2 + 1]);
            m_shadowRx[revIdx] = static_cast<WordType>((hi << 8) | lo);
        }

        return {};
    }

    /* Комплексна перевірка цілісності ланцюга та локалізація обриву */
    std::expected<void, std::size_t> runDiagnosticLoopback() noexcept {
        constexpr WordType MagicBase = 0x5AA5;
        auto savedTx = m_shadowTx;

        // Завантаження унікального сигнатурного шаблону в каскад
        for (std::size_t i = 0; i < NumDevices; ++i) {
            m_shadowTx[i] = static_cast<WordType>(MagicBase + i);
        }

        // Дві транзакції: запис та наступне виштовхування даних у MISO
        if (!syncTransaction()) return std::unexpected(0);
        if (!syncTransaction()) return std::unexpected(0);

        // Перевірка повернення сигнатур
        for (std::size_t i = 0; i < NumDevices; ++i) {
            auto expected = static_cast<WordType>(MagicBase + i);
            if (m_shadowRx[i] != expected) {
                m_shadowTx = savedTx;
                syncTransaction();
                return std::unexpected(i); // Повертаємо індекс першого збійного чіпа
            }
        }

        m_shadowTx = savedTx;
        syncTransaction();
        return {};
    }

private:
    ISpiHal& m_hal;
    std::array<WordType, NumDevices> m_shadowTx{};
    std::array<WordType, NumDevices> m_shadowRx{};
    std::array<std::uint8_t, ByteCount> m_rawTx{};
    std::array<std::uint8_t, ByteCount> m_rawRx{};
};

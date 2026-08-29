// Публічний контракт драйвера: повний життєвий цикл акселерометра.
//
// Тип транспорту — параметр шаблона, тож ані віртуальних викликів, ані
// вказівників на функції в гарячому шляху немає: компілятор бачить
// реалізацію шини наскрізь. Динамічної пам'яті драйвер не торкається
// взагалі; обʼєкт розміщує викликач — статично, у пулі чи на стеку.
#pragma once

#include <array>
#include <atomic>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>
#include <utility>

#include "registers.hpp"
#include "status.hpp"
#include "transport.hpp"

namespace chip {

/// Значення = біти FS у CTRL_REG4, тож перекодовувати нічого не треба.
enum class Range : std::uint8_t { G2 = 0, G4 = 1, G8 = 2, G16 = 3 };

/// Значення = нібл ODR у CTRL_REG1.
enum class Odr : std::uint8_t {
    Hz1 = 1, Hz10 = 2, Hz25 = 3, Hz50 = 4, Hz100 = 5, Hz200 = 6, Hz400 = 7
};

/// Ціна молодшого розряду у високому роздільному режимі (12 біт), мg.
[[nodiscard]] constexpr float mgPerLsb(Range range) noexcept
{
    switch (range) {
    case Range::G2:  return 1.0F;
    case Range::G4:  return 2.0F;
    case Range::G8:  return 4.0F;
    case Range::G16: return 12.0F;
    }
    return 1.0F;
}

/// Прискорення в одиницях SI, м/с². Ціну розряду за даташитом прикладний
/// код не рахує ніколи — це робота драйвера.
struct Vector3 {
    float x{0.0F};
    float y{0.0F};
    float z{0.0F};
};

inline constexpr std::size_t kFifoDepth   = 32;
inline constexpr std::size_t kSampleBytes = 6;
inline constexpr std::size_t kFifoBytes   = kFifoDepth * kSampleBytes;

using FifoScratch = DmaBuffer<kFifoBytes>;

struct FifoBatch {
    std::span<Vector3> samples;      ///< дійсна частина переданого out[]
    bool overrun{false};             ///< чергу переповнено, відліки втрачено
    bool watermark{false};           ///< досягнуто порогу FTH
};

template <BusTransport Transport>
class Sensor {
public:
    /// Помилку несе тип, а не код повернення: проігнорувати її мовчки
    /// не вийде — [[nodiscard]] на кожному методі.
    using Result = std::expected<void, Status>;

    explicit Sensor(Transport transport) noexcept : bus_{std::move(transport)} {}

    Sensor(const Sensor&) = delete;
    Sensor& operator=(const Sensor&) = delete;

    /// Впізнає мікросхему, піднімає коефіцієнти з NVM і виставляє відомий
    /// режим: 100 Гц, високий роздільний, BDU, ±2 g.
    [[nodiscard]] Result init();

    /// Скидає в заводський стан; після цього потрібен повторний init().
    [[nodiscard]] Result softReset();

    /// Перепідняття NVM із перевіркою, що воно справді відбулося.
    [[nodiscard]] Result reloadTrim();

    [[nodiscard]] Result setRange(Range range);
    [[nodiscard]] Result setOdr(Odr odr);

    /// Один відлік. Не блокує: якщо ZYXDA скинутий — Status::DataNotReady.
    [[nodiscard]] std::expected<Vector3, Status> readAcceleration();

    [[nodiscard]] Result enableFifo(bool enable);

    /// Вичитує чергу однією пакетною транзакцією через scratch і розкладає
    /// відліки в out у SI. Повертає ту частину out, що заповнена.
    [[nodiscard]] std::expected<FifoBatch, Status> readFifo(FifoScratch& scratch,
                                                            std::span<Vector3> out);

    /// Збуджує масу електростатично й перевіряє, що відгук по кожній осі
    /// влучає в паспортне вікно 17…360 мg. Блокує на ~1 с.
    [[nodiscard]] Result selfTest();

    [[nodiscard]] Result shutdown();

    /// Єдине, що можна кликати з обробника переривання лінії DRDY:
    /// ані шини, ані затримок — сама лише позначка.
    void drdyFromIsr() noexcept { sample_pending_.store(true, std::memory_order_release); }

    [[nodiscard]] bool samplePending() const noexcept
    {
        return sample_pending_.load(std::memory_order_acquire);
    }

    [[nodiscard]] bool initialized() const noexcept { return initialized_; }

private:
    [[nodiscard]] Result readRegs(std::uint8_t reg, std::span<std::byte> dst);
    [[nodiscard]] std::expected<std::uint8_t, Status> readReg(reg::Reg r);
    [[nodiscard]] Result writeReg(reg::Reg r, std::uint8_t value);
    /// Запис керувального регістру через тінь: нове значення рахуємо з копії
    /// в обʼєкті, а не з читання шини.
    [[nodiscard]] Result writeCtrl(reg::Reg r, std::uint8_t value);
    [[nodiscard]] Result bootAndWait();
    [[nodiscard]] Result waitDataReady();
    [[nodiscard]] std::expected<std::array<std::int32_t, 3>, Status> averageRaw(unsigned count);

    Transport bus_;
    float lsb_to_ms2_{0.0F};
    Range range_{Range::G2};
    std::uint8_t shadow_ctrl1_{0};
    std::uint8_t shadow_ctrl4_{0};
    std::uint8_t shadow_ctrl5_{0};
    bool initialized_{false};
    std::atomic<bool> sample_pending_{false};
};

// Прапорець виставляє ISR, читає задача: без lock-free атомарності це були б
// перегони, а мʼютекса в драйвері немає за контрактом.
static_assert(std::atomic<bool>::is_always_lock_free,
              "прапорець DRDY мусить лишатися lock-free для контексту переривання");

} // namespace chip

#include "sensor.inl"

// crash_report.hpp — журнал причин рестарту в пам'яті, що переживає скидання.
//
// Виріб ніколи не перезавантажується мовчки. Різниця з варіантом на C —
// не в оздобленні: журнал віддається як std::expected, і виклична сторона
// фізично не може прочитати поля, не розібравшись спершу, чи він цілий.
#pragma once

#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>
#include <string_view>
#include <type_traits>

namespace diag {

enum class ResetCause : std::uint8_t {
    unknown,
    power_on,            // холодний старт: живлення щойно подано
    pin,                 // зовнішній NRST — кнопка або програматор
    brown_out,           // просідання живлення нижче порога BOR
    software,            // нас перезапустила сама прошивка
    independent_watchdog, // логіка зависла
    window_watchdog,
    low_power            // збій виходу зі standby
};

enum class PanicReason : std::uint8_t {
    none,
    hard_fault,     // апаратний виняток ядра
    assertion,      // порушений інваріант прошивки
    sensor_timeout, // давач не відповів у відведений час
    bus_stuck,      // шина не звільнилася після відновлення
    loop_too_fast,  // цикл крутиться швидше за вікно сторожа
    brown_out       // монітор живлення побачив просідання
};

// Контекст місця падіння: те, що сервісний інженер шукає в дампі найперше.
struct FaultContext {
    std::uint32_t pc;
    std::uint32_t lr;
    std::uint32_t sp;
    std::uint32_t cfsr;
};

// Тип навмисно тривіальний: жодних ініціалізаторів членів і жодного
// конструктора. Об'єкт лежить у секції .noinit, і будь-яка ініціалізація
// затерла б рівно ті дані, заради яких журнал існує.
struct CrashReport {
    std::uint32_t magic;
    std::uint32_t boot_count;
    std::uint32_t fault_count;
    std::uint32_t safe_state_entries;
    std::uint32_t raw_reset_flags;
    std::uint32_t uptime_ms;
    FaultContext fault;
    ResetCause cause;
    PanicReason panic;
    std::uint16_t crc;

    static constexpr std::uint32_t magic_value = 0x5052'4F44U; // 'PROD'

    // Байти, які беруть участь у контрольній сумі: усе, крім самої суми.
    [[nodiscard]] std::span<const std::byte> payload() const noexcept;
    [[nodiscard]] std::uint16_t checksum() const noexcept;
    [[nodiscard]] bool intact() const noexcept;
};

static_assert(std::is_trivial_v<CrashReport>,
              "журнал у .noinit не має права мати конструктора");

enum class JournalError : std::uint8_t {
    uninitialised,     // магії немає: пам'ять уперше побачила живлення
    checksum_mismatch  // просідання живлення зіпсувало вміст
};

// Єдиний власник примірника в .noinit. Статичний фасад, а не об'єкт:
// журнал у системі рівно один, і другого бути не може за побудовою.
class Journal {
public:
    Journal() = delete;

    // Виконати на самому початку старту, до ініціалізації периферії.
    static ResetCause begin_boot() noexcept;

    static void record(PanicReason reason, const FaultContext& context) noexcept;
    static void note_safe_state() noexcept;
    static void note_uptime(std::uint32_t ms) noexcept;

    // Копія журналу — лише якщо він пройшов перевірку цілісності.
    [[nodiscard]] static std::expected<CrashReport, JournalError> load() noexcept;
};

[[nodiscard]] std::string_view to_string(ResetCause cause) noexcept;
[[nodiscard]] std::string_view to_string(PanicReason reason) noexcept;
[[nodiscard]] std::string_view to_string(JournalError error) noexcept;

} // namespace diag

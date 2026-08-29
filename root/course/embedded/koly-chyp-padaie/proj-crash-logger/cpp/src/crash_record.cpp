#include "crash_record.hpp"

#include <algorithm>
#include <cstring>

#include "stm32f4xx.h"

namespace crash {
namespace {

constexpr std::uint32_t kMagic = 0xDEADBEEF;
constexpr std::uint32_t kCounterKey = 0xC0FFEE01;

// Секція .noinit (NOLOAD): стартовий код її не обнуляє, тож вміст переживає
// і NVIC_SystemReset(), і скидання сторожовим таймером.
[[gnu::section(".noinit")]] Record g_record;
[[gnu::section(".noinit")]] std::uint32_t g_counter;
[[gnu::section(".noinit")]] std::uint32_t g_counter_key;

// Рахуємо все, крім самого поля crc, — тому воно й стоїть останнім.
[[nodiscard]] std::span<const std::byte> hashed_part(const Record& record) noexcept
{
    return {reinterpret_cast<const std::byte*>(&record), offsetof(Record, crc)};
}

} // namespace

std::uint32_t crc32(std::span<const std::byte> data) noexcept
{
    std::uint32_t crc = 0xFFFFFFFF;
    for (std::byte b : data) {
        crc ^= std::to_integer<std::uint32_t>(b);
        for (int bit = 0; bit < 8; ++bit) {
            crc = (crc & 1u) ? ((crc >> 1) ^ 0xEDB88320u) : (crc >> 1);
        }
    }
    return ~crc;
}

std::uint32_t bump_counter() noexcept
{
    if (g_counter_key != kCounterKey) {
        // Перший старт після подачі живлення: у RAM випадкове сміття.
        g_counter_key = kCounterKey;
        g_counter = 0;
    }
    return ++g_counter;
}

void store(const CortexFrame* frame,
           std::uint32_t exc_return,
           FpuFrame fpu,
           std::span<const std::uint32_t> fpu_block) noexcept
{
    // Пишемо просто в .noinit, без проміжної копії: якщо аварія сталася через
    // переповнення стека, зайвих ста двадцяти байтів там немає.
    std::memset(&g_record, 0, sizeof(g_record));

    g_record.magic = kMagic;
    g_record.crash_count = bump_counter();
    g_record.exc_return = exc_return;
    g_record.fpu = fpu;

    // Причини винятку в кадрі немає — вона в регістрах стану ядра.
    g_record.hfsr = SCB->HFSR;
    g_record.cfsr = SCB->CFSR;
    g_record.mmfar = SCB->MMFAR;
    g_record.bfar = SCB->BFAR;
    g_record.shcsr = SCB->SHCSR;

    // Обидва регістри — write-1-to-clear. Не погасивши їх, наступного разу
    // побачимо суміш старих і свіжих бітів.
    SCB->HFSR = g_record.hfsr;
    SCB->CFSR = g_record.cfsr;

    if (frame != nullptr) {
        g_record.frame = *frame;
    }

    if (fpu == FpuFrame::Saved && fpu_block.size() >= 17) {
        std::copy_n(fpu_block.begin(), g_record.s.size(), g_record.s.begin());
        g_record.fpscr = fpu_block[16];
    }

    g_record.crc = crc32(hashed_part(g_record));
}

std::optional<Record> take() noexcept
{
    if (g_record.magic != kMagic) {
        return std::nullopt;
    }
    if (crc32(hashed_part(g_record)) != g_record.crc) {
        // Сигнатура є, CRC немає: RAM устигла зіпсуватися, і числа в дампі брехливі.
        g_record.magic = 0;
        return std::nullopt;
    }

    Record copy = g_record;
    g_record.magic = 0;
    return copy;
}

std::uint32_t consecutive() noexcept
{
    return (g_counter_key == kCounterKey) ? g_counter : 0;
}

void clear_counter() noexcept
{
    g_counter_key = kCounterKey;
    g_counter = 0;
}

} // namespace crash

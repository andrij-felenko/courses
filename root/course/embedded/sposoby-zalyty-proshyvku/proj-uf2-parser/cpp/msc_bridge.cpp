/*
 * Міст між стеком TinyUSB і сеансом завантаження: обробник SCSI WRITE (10)
 * плюс порт Flash для RP2040. Тут вирішується, що відповісти хосту, — і тут
 * ховається найгрубіша помилка завантажувача: сказати «збій носія» на
 * службовий сектор файлової системи.
 */
#include "download_session.hpp"

#include <algorithm>
#include <array>
#include <optional>

extern "C" {
#include "tusb.h"
#include "RP2040.h"                   // CMSIS кристала: NVIC_SystemReset()
#include "hardware/flash.h"           // flash_range_erase / flash_range_program
#include "hardware/sync.h"            // save_and_disable_interrupts
#include "hardware/regs/addressmap.h" // XIP_BASE
#include "pico/time.h"
}

namespace {

constexpr std::uint32_t FamilyRp2040 = 0xE48BFF56U; // значення з uf2families.json

// Перші 256 КіБ Flash займає сам завантажувач — туди писати нема чого.
constexpr uf2::FlashRegion AppRegion{.start = XIP_BASE + 256U * 1024U,
                                     .size  = 1792U * 1024U};

// Пауза, щоб стек устиг віддати хосту статус останнього запису.
constexpr std::uint64_t RebootDelayUs = 50'000;

uf2::DownloadSession g_session{FamilyRp2040, AppRegion};
std::optional<std::uint64_t> g_rebootAtUs;

// Вимкнені переривання на час операції з Flash — і ввімкнені назад у будь-якому
// разі: XIP вимкнено, будь-яке звернення до коду у Flash зависло б.
class InterruptGuard {
public:
    InterruptGuard() noexcept : saved_{save_and_disable_interrupts()} {}
    ~InterruptGuard() { restore_interrupts(saved_); }
    InterruptGuard(const InterruptGuard&) = delete;
    InterruptGuard& operator=(const InterruptGuard&) = delete;

private:
    std::uint32_t saved_;
};

} // namespace

namespace uf2::port {

// pico-sdk працює зі зсувами від XIP_BASE, а не з абсолютними адресами.
bool eraseSector(std::uint32_t address) noexcept
{
    const InterruptGuard guard;
    flash_range_erase(address - XIP_BASE, FlashSectorSize);
    return true;
}

bool program(std::uint32_t address, std::span<const std::uint8_t> data) noexcept
{
    // Програмувати можна лише цілими сторінками по 256 байтів, тож короткий
    // хвіст образу доводимо до сторінки байтами 0xFF — такими вони й лишаються
    // у стертій Flash, тобто поза корисними байтами нічого не міняється.
    if (data.size() > FLASH_PAGE_SIZE || (address % FLASH_PAGE_SIZE) != 0) {
        return false;
    }
    static std::array<std::uint8_t, FLASH_PAGE_SIZE> page{};
    page.fill(0xFF);
    std::copy(data.begin(), data.end(), page.begin());

    const InterruptGuard guard;
    flash_range_program(address - XIP_BASE, page.data(), page.size());
    return true;
}

} // namespace uf2::port

extern "C" {

// Хост записує; емульований диск завжди приймає запис.
bool tud_msc_is_writable_cb(std::uint8_t lun)
{
    (void)lun;
    return true;
}

/*
 * Повертається кількість прийнятих байтів; від'ємне значення означає
 * CHECK CONDITION, тобто «носій зламався» на боці хоста.
 */
std::int32_t tud_msc_write10_cb(std::uint8_t lun, std::uint32_t lba, std::uint32_t offset,
                                std::uint8_t* buffer, std::uint32_t bufsize)
{
    (void)lba;

    // CFG_TUD_MSC_EP_BUFSIZE == 512, тож сектор приходить цілим. Якщо стек усе ж
    // розрізав його на частини — мовчки приймаємо байти: зібрати їх ніде,
    // а помилку хосту віддавати не можна.
    if (offset != 0 || bufsize < uf2::BlockSize) {
        return static_cast<std::int32_t>(bufsize);
    }

    const std::span sector{static_cast<const std::uint8_t*>(buffer), bufsize};
    const auto result = g_session.accept(sector);

    if (!result) {
        if (uf2::isForeignSector(result.error())) {
            // Це не блок UF2, а запис каталогу, таблиці FAT чи .DS_Store.
            // Кажемо GOOD і нічого не робимо: CHECK CONDITION тут перерве
            // копіювання файлу й покаже користувачу «диск пошкоджено».
            return static_cast<std::int32_t>(bufsize);
        }
        // А це вже справжня біда: чуже сімейство, адреса поза межами, збій
        // Flash. Тут мовчати не можна — хай копіювання зупиниться.
        const std::string_view reason = uf2::describe(result.error());
        TU_LOG1("UF2: %.*s\r\n", static_cast<int>(reason.size()), reason.data());
        tud_msc_set_sense(lun, SCSI_SENSE_MEDIUM_ERROR, 0x03, 0x00);
        return -1;
    }

    if (result->complete && !g_rebootAtUs.has_value()) {
        g_rebootAtUs = time_us_64() + RebootDelayUs;
    }
    return static_cast<std::int32_t>(bufsize);
}

} // extern "C"

/*
 * Викликається з головного циклу поруч із tud_task(). Перезавантаження робиться
 * саме тут, а не всередині callback: скинути ядро до того, як стек віддав хосту
 * CSW останнього запису, — це «пристрій зник» і помилка копіювання на екрані.
 */
void uf2MscTask()
{
    if (!g_rebootAtUs.has_value() || time_us_64() < *g_rebootAtUs) {
        return;
    }
    tud_disconnect(); // коректний USB disconnect, щоб хост прибрав том
    sleep_ms(10);
    NVIC_SystemReset();
}

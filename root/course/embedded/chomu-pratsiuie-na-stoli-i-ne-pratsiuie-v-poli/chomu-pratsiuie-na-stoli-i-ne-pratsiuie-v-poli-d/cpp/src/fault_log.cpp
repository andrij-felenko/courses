// fault_log.cpp — розкладка резервного домену й розшифровка причини старту.
//
// Подія пакується в 32 біти:
//   31..29 причина · 28..21 температура+64 · 20..13 напруга/16 · 12..0 секунди
// Кожне поле обрізане свідомо: точність тут не потрібна, потрібна історія
// останніх шістнадцяти аварій у пам'яті, якої всього двадцять слів.

#include "field/fault_log.hpp"

#include <algorithm>

#include "field/platform.hpp"

namespace field {
namespace {

constexpr std::uint8_t kWordHeader = 0;
constexpr std::uint8_t kWordCountersA = 1;
constexpr std::uint8_t kWordCountersB = 2;
constexpr std::uint8_t kWordHardFault = 3;
constexpr std::uint8_t kWordEvents = 4;

constexpr std::uint16_t kMagic = 0xF1E1;
constexpr std::uint32_t kHardFaultMark = 0xFA;

// Прапори RCC_CSR. Тримаємо їх тут, а не в порті: розшифровка — це політика.
constexpr std::uint32_t kCsrLowPower = 1u << 31;
constexpr std::uint32_t kCsrWwdg = 1u << 30;
constexpr std::uint32_t kCsrIwdg = 1u << 29;
constexpr std::uint32_t kCsrSoftware = 1u << 28;
constexpr std::uint32_t kCsrPowerOn = 1u << 27;
constexpr std::uint32_t kCsrPin = 1u << 26;
constexpr std::uint32_t kCsrBrownout = 1u << 25;

std::uint32_t readWord(std::uint8_t index) noexcept {
    return plat::bkpRead(index).value_or(0);
}

std::uint16_t headerCount(std::uint32_t header) noexcept {
    return static_cast<std::uint16_t>((header >> 8) & 0xFFu);
}

std::uint8_t headerHead(std::uint32_t header) noexcept {
    return static_cast<std::uint8_t>(header & 0xFFu);
}

void storeHeader(std::uint8_t count, std::uint8_t head) noexcept {
    static_cast<void>(plat::bkpWrite(
        kWordHeader, (static_cast<std::uint32_t>(kMagic) << 16) |
                         (static_cast<std::uint32_t>(count) << 8) | head));
}

bool domainValid(std::uint32_t header) noexcept { return (header >> 16) == kMagic; }

void wipeDomain() noexcept {
    for (std::uint8_t i = 0; i < plat::kBkpWords; ++i) {
        static_cast<void>(plat::bkpWrite(i, 0));
    }
    storeHeader(0, 0);
}

Counters loadCounters() noexcept {
    const std::uint32_t a = readWord(kWordCountersA);
    const std::uint32_t b = readWord(kWordCountersB);
    return Counters{static_cast<std::uint16_t>(a >> 16),
                    static_cast<std::uint16_t>(a & 0xFFFFu),
                    static_cast<std::uint16_t>(b >> 16),
                    static_cast<std::uint16_t>(b & 0xFFFFu)};
}

void storeCounters(const Counters& c) noexcept {
    static_cast<void>(plat::bkpWrite(
        kWordCountersA, (static_cast<std::uint32_t>(c.boots) << 16) | c.brownouts));
    static_cast<void>(plat::bkpWrite(
        kWordCountersB, (static_cast<std::uint32_t>(c.watchdogs) << 16) | c.busRecoveries));
}

// Лічильники впираються в стелю замість переповнення: «65535 Brownout» —
// це вирок конструкції, і скинути його в нуль означало б збрехати.
std::uint16_t bump(std::uint16_t value) noexcept {
    return (value == 0xFFFF) ? value : static_cast<std::uint16_t>(value + 1);
}

std::uint32_t packEvent(ResetCause cause, std::int16_t temperatureC, std::uint16_t voltageMv,
                        std::uint32_t uptimeS) noexcept {
    const auto t = static_cast<std::uint32_t>(std::clamp(temperatureC + 64, 0, 255));
    const std::uint32_t mv = std::min<std::uint32_t>(voltageMv / 16u, 255);
    const std::uint32_t up = std::min<std::uint32_t>(uptimeS, 8191);

    return ((static_cast<std::uint32_t>(cause) & 7u) << 29) | (t << 21) | (mv << 13) | up;
}

Event unpackEvent(std::uint32_t word) noexcept {
    return Event{static_cast<ResetCause>((word >> 29) & 7u),
                 static_cast<std::int16_t>(static_cast<int>((word >> 21) & 0xFFu) - 64),
                 static_cast<std::uint16_t>(((word >> 13) & 0xFFu) * 16u),
                 std::chrono::seconds{word & 0x1FFFu}};
}

ResetCause decodeFlags(std::uint32_t csr) noexcept {
    // Порядок перевірок — це порядок важливості, а не порядок бітів. Залізо
    // часто піднімає кілька прапорів одразу: після Brownout стоїть і PINRST,
    // бо просадка тягне лінію NRST. Питання «що нас убило» має рівно одну
    // відповідь, і це найгірший із піднятих прапорів.
    if ((csr & kCsrBrownout) != 0) return ResetCause::Brownout;
    if ((csr & (kCsrIwdg | kCsrWwdg)) != 0) return ResetCause::Watchdog;
    if ((csr & kCsrLowPower) != 0) return ResetCause::LowPower;
    if ((csr & kCsrSoftware) != 0) return ResetCause::Software;
    if ((csr & kCsrPin) != 0) return ResetCause::Pin;
    if ((csr & kCsrPowerOn) != 0) return ResetCause::PowerOn;
    return ResetCause::Unknown;
}

}  // namespace

std::string_view name(ResetCause cause) noexcept {
    using enum ResetCause;
    switch (cause) {
        case PowerOn: return "power-on";
        case Pin: return "nrst";
        case Brownout: return "brownout";
        case Watchdog: return "watchdog";
        case HardFault: return "hardfault";
        case Software: return "software";
        case LowPower: return "low-power";
        case Unknown: break;
    }
    return "unknown";
}

BootReport FaultLog::open() {
    BootReport report{};

    const std::uint32_t header = readWord(kWordHeader);
    report.historyLost = !domainValid(header);
    if (report.historyLost) {
        // Перший старт, знята батарейка резервного домену або зіпсовані
        // слова. Розмічаємо наново — і кажемо про це вголос.
        wipeDomain();
    }

    report.cause = decodeFlags(plat::resetFlagsRaw());

    // Слід HardFault важить більше за прапор заліза: після скидання з
    // обробника винятку RCC_CSR покаже лише SFTRST, тобто «нас перезапустила
    // програма» — правду знає тільки цей запис.
    if (const std::uint32_t mark = readWord(kWordHardFault); (mark >> 24) == kHardFaultMark) {
        report.cause = ResetCause::HardFault;
        report.faultPc = mark & 0x00FF'FFFFu;
        static_cast<void>(plat::bkpWrite(kWordHardFault, 0));  // слід прочитано
    }

    report.counters = loadCounters();
    report.counters.boots = bump(report.counters.boots);
    if (report.cause == ResetCause::Brownout) {
        report.counters.brownouts = bump(report.counters.brownouts);
    } else if (report.cause == ResetCause::Watchdog) {
        report.counters.watchdogs = bump(report.counters.watchdogs);
    }
    storeCounters(report.counters);

    return report;
}

void FaultLog::append(ResetCause cause, std::int16_t temperatureC, std::uint16_t voltageMv,
                      std::chrono::milliseconds uptime) {
    std::uint32_t header = readWord(kWordHeader);
    if (!domainValid(header)) {
        wipeDomain();  // домен зіпсувався в роботі: краще порожній, ніж брехливий
        header = readWord(kWordHeader);
    }

    std::uint8_t head = headerHead(header) % kSlots;
    std::uint16_t count = headerCount(header);

    const auto seconds =
        static_cast<std::uint32_t>(std::chrono::duration_cast<std::chrono::seconds>(uptime).count());
    static_cast<void>(plat::bkpWrite(static_cast<std::uint8_t>(kWordEvents + head),
                                     packEvent(cause, temperatureC, voltageMv, seconds)));

    head = static_cast<std::uint8_t>((head + 1) % kSlots);
    if (count < kSlots) {
        ++count;
    }
    storeHeader(static_cast<std::uint8_t>(count), head);
}

std::size_t FaultLog::readRecent(std::span<Event> out) const {
    const std::uint32_t header = readWord(kWordHeader);
    if (out.empty() || !domainValid(header)) {
        return 0;
    }

    const std::size_t stored = std::min<std::size_t>(headerCount(header), kSlots);
    const std::size_t take = std::min(out.size(), stored);

    std::uint8_t head = headerHead(header) % kSlots;
    for (std::size_t i = 0; i < take; ++i) {
        // Ідемо назад від голови: найсвіжіша подія лежить перед нею.
        head = static_cast<std::uint8_t>((head + kSlots - 1) % kSlots);
        out[i] = unpackEvent(readWord(static_cast<std::uint8_t>(kWordEvents + head)));
    }
    return take;
}

void FaultLog::noteBusRecovery() {
    Counters c = loadCounters();
    c.busRecoveries = bump(c.busRecoveries);
    storeCounters(c);
}

}  // namespace field

// Кадр, який залізо поклало на стек: r0 r1 r2 r3 r12 lr pc psr. Нас цікавить
// pc — адреса інструкції, на якій усе розвалилося.
extern "C" [[noreturn]] void fieldRecordHardFault(const std::uint32_t* frame) {
    static_cast<void>(field::plat::bkpWrite(
        field::kWordHardFault, (field::kHardFaultMark << 24) | (frame[6] & 0x00FF'FFFFu)));
    field::plat::systemReset();
}

// Обробник голий: жодного прологу, бо пролог зіпсував би регістри до того,
// як ми дізнаємось, на якому стеку лежить кадр винятку. Біт 2 у LR каже,
// звідки прийшли — з головного стека чи з процесного.
extern "C" __attribute__((naked)) void HardFault_Handler() {
    __asm volatile(
        "tst lr, #4                \n"
        "ite eq                    \n"
        "mrseq r0, msp             \n"
        "mrsne r0, psp             \n"
        "b fieldRecordHardFault    \n");
}

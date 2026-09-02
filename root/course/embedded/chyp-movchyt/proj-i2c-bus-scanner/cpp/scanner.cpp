#include "scanner.hpp"

#include <algorithm>
#include <bit>
#include <string_view>

namespace {

std::string_view advice(Verdict verdict) noexcept {
    switch (verdict) {
    case Verdict::device_as_expected:
        return "Шина справна, вузол відповідає за очікуваною адресою.\n"
               "  Далі має сенс читати регістр ідентифікації (WHO_AM_I).";
    case Verdict::address_mismatch:
        return "Пристрій на шині є, але не за тією адресою, яку обіцяв даташит.\n"
               "  Перевір потенціал на виводі AD0 / ADDR: підтяжка до живлення замість землі\n"
               "  або взагалі непідключений вивід, що ловить потенціал сусідньої доріжки.";
    case Verdict::phantom_all_ack:
        return "Відповіли всі адреси діапазону — стільки мікросхем на платі немає.\n"
               "  SDA притиснута до землі: коротке замикання, пробитий захисний діод\n"
               "  або зависла мікросхема, яку не витягли дев'ять тактів відновлення.";
    case Verdict::silent_but_healthy:
        return "Лінії електрично здорові (підтяжки є, такти проходять), але не відповів ніхто.\n"
               "  Перевір V_DD на веденому чіпі, рівень на nRST (він active-low)\n"
               "  і чи не переплутані SDA та SCL між мікроконтролером і модулем.";
    case Verdict::lines_broken:
        return "Транзакції не починаються взагалі: лінії не виходять у високий рівень.\n"
               "  Найімовірніше немає резисторів підтяжки (типово 4.7 кОм до V_DD)\n"
               "  або на шину не подано живлення.";
    }
    return "невідомий вердикт";
}

} // namespace

Verdict classify(const ScanReport& report, std::uint8_t expected_addr) noexcept {
    /* Сто дванадцять "пристроїв" — це не сто дванадцять мікросхем, а нуль на SDA:
       ведучий читає притиснуту лінію на дев'ятому такті як ACK. */
    if (report.found.size() >= addr_space) {
        return Verdict::phantom_all_ack;
    }
    if (report.found.empty()) {
        return report.errors > 0 ? Verdict::lines_broken : Verdict::silent_but_healthy;
    }
    if (std::ranges::find(report.found, expected_addr) != report.found.end()) {
        return Verdict::device_as_expected;
    }
    return Verdict::address_mismatch;
}

void print_report(const ScanReport& report, std::uint8_t expected_addr, Verdict verdict) {
    if (report.last_error) {
        std::println("Остання помилка шини: {}", describe(*report.last_error));
    }
    std::println("Вердикт:\n  {}", advice(verdict));

    if (verdict == Verdict::address_mismatch) {
        for (const std::uint8_t addr : report.found) {
            const auto diff = static_cast<std::uint8_t>(addr ^ expected_addr);

            /* Один-два різні біти в молодшій частині — це майже завжди
               адресні перемички AD0/AD1, а не інша мікросхема. */
            if (std::popcount(diff) <= 2 && diff < 0x08) {
                std::println("  0x{:02X} відрізняється від очікуваної 0x{:02X} лише молодшими бітами"
                             " — дивись адресні перемички.",
                             addr, expected_addr);
            }
        }
    }
}

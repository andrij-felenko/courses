// ============================================================================
// ФАЙЛ: test_harness.cpp (C++20) — демонстраційний тестовий сценарій
// ============================================================================
#include "hal_driver_core.hpp"
#include <iostream>
#include <array>

int main()
{
    std::cout << "=== СТАРТ ТЕСТУВАННЯ ФРЕЙМВОРКУ СЛАБКИХ СИМВОЛІВ (C++20) ===\n\n";

    hal::core::initialize();

    std::cout << "\n--- ТЕСТ 1: Сильний UART обробник ---\n";
    const std::array<std::byte, 5> uart_data{
        std::byte{'W'}, std::byte{'O'}, std::byte{'R'}, std::byte{'L'}, std::byte{'D'}
    };
    hal::core::dispatch_interrupt(hal::PeripheralId::Uart1, hal::EventKind::RxReady, uart_data);

    std::cout << "\n--- ТЕСТ 2: Сильний GPIO обробник ---\n";
    hal::core::dispatch_interrupt(hal::PeripheralId::Gpio, hal::EventKind::PinEdge, {});

    std::cout << "\n--- ТЕСТ 3: Неперекритий SPI обробник (Default Stub) ---\n";
    const std::array<std::byte, 2> spi_data{std::byte{0xDE}, std::byte{0xAD}};
    hal::core::dispatch_interrupt(hal::PeripheralId::Spi1, hal::EventKind::TransferDone, spi_data);
    std::cout << "SPI успішно пройшов крізь заглушку за замовчуванням.\n";

    std::cout << "\n--- ТЕСТ 4: Неперекритий Таймер ---\n";
    hal::core::dispatch_interrupt(hal::PeripheralId::Timer, hal::EventKind::PeriodElapsed, {});
    std::cout << "Таймер відпрацював без помилок.\n";

    std::cout << "\n=== ТЕСТУВАННЯ C++20 ЗАВЕРШЕНО УСПІШНО ===\n";
    return 0;
}

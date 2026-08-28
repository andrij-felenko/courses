#include <cassert>

void run_clock_manager_tests_cpp() {
    using namespace std::string_literals;

    // 1. Початковий стан
    assert(!modern_clock_manager::is_active(periph_tag::usart1));
    assert(!modern_clock_manager::is_active(periph_tag::gpioa));
    assert(modern_clock_manager::bus_active_count(bus_domain_tag::apb2) == 0);

    // 2. Тестування RAII області видимості
    {
        peripheral_clock_guard<periph_tag::usart1> usart_guard;
        assert(usart_guard.is_valid());
        assert(modern_clock_manager::is_active(periph_tag::usart1));
        assert(modern_clock_manager::is_active(periph_tag::gpioa)); // Авто-залежність
        assert(modern_clock_manager::bus_active_count(bus_domain_tag::apb2) == 1);
        assert(modern_clock_manager::bus_active_count(bus_domain_tag::ahb1) == 1);

        {
            // Вкладена область видимості: інший драйвер захоплює SPI1
            peripheral_clock_guard<periph_tag::spi1> spi_guard;
            assert(spi_guard.is_valid());
            assert(modern_clock_manager::is_active(periph_tag::spi1));
            assert(modern_clock_manager::is_active(periph_tag::dma2)); // Залежність SPI1
            assert(modern_clock_manager::bus_active_count(bus_domain_tag::ahb1) == 2); // GPIOA + DMA2
        } // spi_guard знищується: SPI1 та DMA2 вимикаються, GPIOA лишається для USART1

        assert(!modern_clock_manager::is_active(periph_tag::spi1));
        assert(!modern_clock_manager::is_active(periph_tag::dma2));
        assert(modern_clock_manager::is_active(periph_tag::usart1));
        assert(modern_clock_manager::is_active(periph_tag::gpioa));
    } // usart_guard знищується: USART1 та GPIOA повністю вимикаються

    assert(!modern_clock_manager::is_active(periph_tag::usart1));
    assert(!modern_clock_manager::is_active(periph_tag::gpioa));
    assert(modern_clock_manager::bus_active_count(bus_domain_tag::apb2) == 0);
    assert(modern_clock_manager::bus_active_count(bus_domain_tag::ahb1) == 0);
}

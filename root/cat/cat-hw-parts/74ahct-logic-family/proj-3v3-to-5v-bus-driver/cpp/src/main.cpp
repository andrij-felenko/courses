#include "AhctBusDriver.hpp"
#include <array>
#include <span>
#include <cstdio>

int main() {
    // Буфер для SPI трансляції (наприклад, для 4 пікселів: 4 пікселі * 3 байти * 8 біт = 96 байт SPI)
    std::array<uint8_t, 96> spiBuffer{};
    
    // Вихідні дані піксеів (GRB)
    std::array<Pixel, 4> pixels = {
        Pixel{255, 0, 0},     // Зелений
        Pixel{0, 255, 0},     // Червоний
        Pixel{0, 0, 255},     // Синій
        Pixel{255, 255, 255}  // Білий
    };

    // Використання RAII для захисту шини 74AHCT245 під час передачі
    {
        AhctBusGuard guard(AhctBusGuard::Direction::Output);
        
        Ws2812SpiDriver driver(spiBuffer);
        size_t encodedBytes = driver.encodePixels(pixels);
        
        std::printf("Encoded %zu bytes for SPI transmission through 74AHCT level shifter.\n", encodedBytes);
        
        // Тут відбувався б старт SPI+DMA передачі на апаратному рівні:
        // HAL_SPI_Transmit_DMA(&hspi1, spiBuffer.data(), encodedBytes);
    } // При виході з блоку спрацьовує деструктор guard, безпечно переводячи шину в Z-стан

    std::printf("Bus guard released safely. System stable.\n");
    return 0;
}

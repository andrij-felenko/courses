#pragma once

#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <utility>

/// RAII-обгортка для керування життєвим циклом активної транзакції SPI DMA.
/// Гарантує коректне утримання лінії CS (Chip Select), синхронізацію завершення
/// передачі перед виходом з області видимості та запобігає перегонам за спільний буфер.
template <typename SpiDriver>
class [[nodiscard]] DmaTransactionGuard {
public:
    explicit DmaTransactionGuard(SpiDriver& driver, const uint16_t* buffer, size_t count_pixels) noexcept
        : driver_(&driver), active_(true) {
        // Запуск передачі: контролер бере на себе володіння шиною на час трансляції
        driver_->start_dma_tx(buffer, count_pixels);
    }

    ~DmaTransactionGuard() noexcept {
        wait();
    }

    // Заборона копіювання: транзакція DMA є унікальним апаратним ресурсом
    DmaTransactionGuard(const DmaTransactionGuard&) = delete;
    DmaTransactionGuard& operator=(const DmaTransactionGuard&) = delete;

    // Дозвіл переміщення для передачі володіння між контекстами
    DmaTransactionGuard(DmaTransactionGuard&& other) noexcept
        : driver_(other.driver_), active_(other.active_) {
        other.active_ = false;
        other.driver_ = nullptr;
    }

    DmaTransactionGuard& operator=(DmaTransactionGuard&& other) noexcept {
        if (this != &other) {
            wait();
            driver_ = other.driver_;
            active_ = other.active_;
            other.active_ = false;
            other.driver_ = nullptr;
        }
        return *this;
    }

    /// Очікування фізичного завершення передачі блоку даних контролером DMA
    void wait() noexcept {
        if (active_ && driver_ != nullptr) {
            driver_->wait_dma_complete();
            active_ = false;
        }
    }

    /// Перевірка активності трансляції без блокування процесора
    [[nodiscard]] bool is_busy() const noexcept {
        return active_ && driver_ != nullptr && driver_->is_dma_busy();
    }

private:
    SpiDriver* driver_{nullptr};
    bool active_{false};
};

/// Дескриптор подвійного лінійного буфера для конвеєрного рендерингу (Ping-Pong).
/// Дозволяє процесору заповнювати один рядок пікселів, поки контролер DMA
/// автономно передає інший рядок по шині SPI.
template <size_t LineLength = 240>
struct PingPongBuffers {
    alignas(4) std::array<uint16_t, LineLength> line_a{};
    alignas(4) std::array<uint16_t, LineLength> line_b{};
    uint8_t write_index{0};

    /// Отримати робочий буфер для генерації поточного рядка процесором
    [[nodiscard]] std::span<uint16_t, LineLength> render_buffer() noexcept {
        return (write_index == 0) ? std::span<uint16_t, LineLength>(line_a)
                                  : std::span<uint16_t, LineLength>(line_b);
    }

    /// Отримати покажчик на заповнений буфер, готовий до відправки через DMA
    [[nodiscard]] const uint16_t* dma_buffer() const noexcept {
        return (write_index == 0) ? line_b.data() : line_a.data();
    }

    /// Атомарна зміна активного та передавального буферів
    void swap() noexcept {
        write_index ^= 1;
    }
};

/// Шаблонний драйвер дисплея ST7789 з нульовими накладними витратами.
/// Параметризований типами апаратного бекенду SPI DMA, лініями GPIO та сервісом затримок.
template <typename SpiDmaBackend, typename PinCs, typename PinDc, typename PinRst, typename DelayPolicy>
class ST7789 {
public:
    static constexpr uint16_t WIDTH = 240;
    static constexpr uint16_t HEIGHT = 240;

    /// Команди керування згідно зі специфікацією контролера Sitronix ST7789VW
    enum class Command : uint8_t {
        SWRESET = 0x01, // Програмне скидання регістрів у початковий стан
        SLPOUT  = 0x11, // Вихід із режиму сну генератора
        NORON   = 0x13, // Нормальний режим відображення (без часткового оновлення)
        INVOFF  = 0x20, // Вимкнення інверсії
        INVON   = 0x21, // Увімкнення інверсії (критично для правильних кольорів IPS)
        DISPOFF = 0x28, // Вимкнення драйвера панелі
        DISPON  = 0x29, // Увімкнення виведення зображення
        CASET   = 0x2A, // Встановлення діапазону стовпчиків (X-координати)
        RASET   = 0x2B, // Встановлення діапазону рядків (Y-координати)
        RAMWR   = 0x2C, // Початок передачі піксельних даних у відеопам'ять
        MADCTL  = 0x36, // Керування адресацією та порядком кольорів
        COLMOD  = 0x3A  // Формат кольору пікселів інтерфейсу
    };

    explicit ST7789(SpiDmaBackend& spi_dma) noexcept : spi_dma_(spi_dma) {}

    /// Повна апаратна та регістрова ініціалізація матриці
    void init() noexcept {
        // Апаратний імпульс скидання (Hardware Reset Pulse)
        PinRst::set_high();
        DelayPolicy::delay_ms(5);
        PinRst::set_low();
        DelayPolicy::delay_ms(20);
        PinRst::set_high();
        DelayPolicy::delay_ms(120);

        // Програмний скид контролера
        write_command(Command::SWRESET);
        DelayPolicy::delay_ms(150);

        // Пробудження тактового генератора та аналогових підсилювачів
        write_command(Command::SLPOUT);
        DelayPolicy::delay_ms(120);

        // Конфігурація 16-бітного кольору (RGB565: 5 біт R, 6 біт G, 5 біт B)
        write_command(Command::COLMOD);
        write_data(0x55);
        DelayPolicy::delay_ms(10);

        // Напрямок розгортки: портретна орієнтація, порядок RGB
        write_command(Command::MADCTL);
        write_data(0x00);

        // Для панелей IPS з нормально чорними пікселями інверсія мусить бути увімкнена
        write_command(Command::INVON);
        DelayPolicy::delay_ms(10);

        // Звичайний режим відображення
        write_command(Command::NORON);
        DelayPolicy::delay_ms(10);

        // Запуск виведення матриці
        write_command(Command::DISPON);
        DelayPolicy::delay_ms(120);
    }

    /// Налаштування активного прямокутного вікна малювання в пам'яті дисплея
    void set_address_window(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1) noexcept {
        write_command(Command::CASET);
        write_data(static_cast<uint8_t>(x0 >> 8));
        write_data(static_cast<uint8_t>(x0 & 0xFF));
        write_data(static_cast<uint8_t>(x1 >> 8));
        write_data(static_cast<uint8_t>(x1 & 0xFF));

        write_command(Command::RASET);
        write_data(static_cast<uint8_t>(y0 >> 8));
        write_data(static_cast<uint8_t>(y0 & 0xFF));
        write_data(static_cast<uint8_t>(y1 >> 8));
        write_data(static_cast<uint8_t>(y1 & 0xFF));
    }

    /// Переведення контролера в режим прийому потоку кольорів пікселів
    void prepare_ram_write() noexcept {
        write_command(Command::RAMWR);
    }

    /// Запуск асинхронної трансляції рядкового буфера в пам'ять дисплея через DMA.
    /// Повертає об'єкт RAII-захисника, який гарантує синхронізацію завершення передачі.
    [[nodiscard]] auto transmit_scanline_async(const uint16_t* line_pixels, size_t count = WIDTH) noexcept {
        PinDc::set_high(); // Режим даних
        PinCs::set_low();  // Активація веденого пристрою на шині SPI
        return DmaTransactionGuard<SpiDmaBackend>(spi_dma_, line_pixels, count);
    }

    /// Запис байта команди (лінія DC низька)
    void write_command(Command cmd) noexcept {
        PinDc::set_low();
        PinCs::set_low();
        spi_dma_.send_byte_blocking(static_cast<uint8_t>(cmd));
        PinCs::set_high();
    }

    /// Запис байта даних (лінія DC висока)
    void write_data(uint8_t data) noexcept {
        PinDc::set_high();
        PinCs::set_low();
        spi_dma_.send_byte_blocking(data);
        PinCs::set_high();
    }

private:
    SpiDmaBackend& spi_dma_;
};

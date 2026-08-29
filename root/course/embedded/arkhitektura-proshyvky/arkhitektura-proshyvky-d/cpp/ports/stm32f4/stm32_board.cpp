// ports/stm32f4/stm32_board.cpp — збірка плати на STM32F401.
// Системний час, критична секція, сон ядра, передавач телеметрії й
// board::init(), що зшиває це все в структуру board::Board.
#include "app/config.hpp"
#include "board.hpp"
#include "hal/clock.hpp"
#include "hal/critical_section.hpp"
#include "ports/stm32f4/stm32_peripherals.hpp"

#include <array>

namespace {

constexpr std::uint8_t  kLedPin      = 0;        // PB0
constexpr std::uint32_t kUartBaud    = 115200;
constexpr std::uint32_t kApb1ClockHz = 42'000'000;

volatile std::uint32_t g_tick_ms       = 0;
volatile std::uint32_t g_next_event_ms = 0;
app::IEventSink*       g_sink          = nullptr;

port::Stm32I2cBus        g_bus{I2C1};
port::Stm32GpioPort      g_port_b{GPIOB};
port::UartTelemetrySink  g_telemetry;

} // namespace

// --- hal/clock.hpp ---

namespace hal {

Millis now() noexcept
{
    return Millis{g_tick_ms};
}

void cpu_sleep() noexcept
{
    // Ядро спиняється до найближчого переривання. Струм падає з десятків
    // міліампер до одиниць — заради цього рядка вся подійна архітектура
    // й будувалася.
    __asm volatile("wfi");
}

void delay(Millis duration) noexcept
{
    const auto started = g_tick_ms;
    while ((g_tick_ms - started) < static_cast<std::uint32_t>(duration.count())) {
        __asm volatile("nop");
    }
}

std::uint32_t critical_enter() noexcept
{
    std::uint32_t primask = 0;
    __asm volatile("mrs %0, primask" : "=r"(primask));
    __asm volatile("cpsid i" ::: "memory");
    return primask;
}

void critical_exit(std::uint32_t saved_state) noexcept
{
    // Вмикаємо переривання лише якщо вони були ввімкнені до входу: інакше
    // вкладена секція відкрила б їх передчасно.
    if ((saved_state & 1U) == 0) {
        __asm volatile("cpsie i" ::: "memory");
    }
}

} // namespace hal

// --- Системний таймер ---

extern "C" void SysTick_Handler()
{
    ++g_tick_ms;

    // Тік застосунку рідший за такт таймера: подія раз на сто мілісекунд,
    // а не тисяча подій на секунду, яких ніхто не встигне розібрати.
    if (static_cast<std::int32_t>(g_tick_ms - g_next_event_ms) >= 0) {
        g_next_event_ms = g_tick_ms + static_cast<std::uint32_t>(config::kTickPeriod.count());

        if (app::IEventSink* sink = g_sink; sink != nullptr) {
            static_cast<void>(sink->post(app::SystemEvent{
                .id = app::EventId::Tick,
                .timestamp = hal::Millis{g_tick_ms},
            }));
        }
    }
}

namespace port {

void UartTelemetrySink::put_char(char c)
{
    while ((USART2->SR & USART_SR_TXE) == 0) {
    }
    USART2->DR = static_cast<std::uint32_t>(static_cast<std::uint8_t>(c));
}

void UartTelemetrySink::put_text(std::string_view text)
{
    for (const char c : text) {
        put_char(c);
    }
}

void UartTelemetrySink::put_uint(std::uint32_t value)
{
    if (value == 0) {
        put_char('0');
        return;
    }
    std::array<char, 10> digits{};
    std::size_t count = 0;
    while (value != 0 && count < digits.size()) {
        digits[count++] = static_cast<char>('0' + (value % 10));
        value /= 10;
    }
    while (count-- > 0) {
        put_char(digits[count]);
    }
}

// Друк числа з двома знаками після коми без printf: повний форматувальник
// з підтримкою float тягне у прошивку кілька десятків кілобайтів.
void UartTelemetrySink::put_fixed2(float value)
{
    if (value < 0.0F) {
        put_char('-');
        value = -value;
    }
    const auto scaled = static_cast<std::uint32_t>(value * 100.0F + 0.5F);
    put_uint(scaled / 100);
    put_char('.');
    const std::uint32_t frac = scaled % 100;
    if (frac < 10) {
        put_char('0');
    }
    put_uint(frac);
}

void UartTelemetrySink::init()
{
    RCC->APB1ENR |= RCC_APB1ENR_USART2EN;
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;

    // PA2 — вихід передавача, альтернативна функція 7.
    GPIOA->MODER  &= ~(3U << 4);
    GPIOA->MODER  |=  (2U << 4);
    GPIOA->AFR[0] &= ~(0xFU << 8);
    GPIOA->AFR[0] |=  (7U << 8);

    USART2->BRR = kApb1ClockHz / kUartBaud;
    USART2->CR1 = USART_CR1_TE | USART_CR1_UE;
}

void UartTelemetrySink::publish(const app::TelemetryRecord& record)
{
    put_text("T=");
    put_fixed2(record.temp_avg_c);
    put_text("C H=");
    put_fixed2(record.humidity_avg_rh);
    put_text("% P=");
    put_fixed2(record.pressure_avg_hpa);
    put_text("hPa VIB=");
    put_fixed2(record.vibration_rms_g);
    put_text("g PEAK=");
    put_fixed2(record.vibration_peak_g);
    put_text("g N=");
    put_uint(record.sample_count);
    put_text(" ERR=");
    put_uint(record.fault_count);
    put_text("\r\n");
}

} // namespace port

// --- board.hpp ---

namespace board {

void bind_event_sink(app::IEventSink* sink)
{
    const hal::CriticalSection guard;
    g_sink = sink;
}

app::IEventSink* event_sink() noexcept
{
    return g_sink;
}

Board* init()
{
    SystemCoreClockUpdate();

    SysTick->LOAD = (SystemCoreClock / 1000U) - 1U;
    SysTick->VAL  = 0;
    SysTick->CTRL = SysTick_CTRL_CLKSOURCE_Msk | SysTick_CTRL_TICKINT_Msk |
                    SysTick_CTRL_ENABLE_Msk;
    g_next_event_ms = static_cast<std::uint32_t>(config::kTickPeriod.count());

    g_telemetry.init();
    g_bus.init();
    port::button_exti_init();

    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOBEN;

    // Обидві мікросхеми сидять на одній шині — це видно тут, у порті,
    // і більше ніде в проєкті.
    static Board board{
        .env_bus    = g_bus,
        .accel_bus  = g_bus,
        .status_led = hal::OutputPin{g_port_b, kLedPin, false},
        .telemetry  = g_telemetry,
    };
    return &board;
}

} // namespace board

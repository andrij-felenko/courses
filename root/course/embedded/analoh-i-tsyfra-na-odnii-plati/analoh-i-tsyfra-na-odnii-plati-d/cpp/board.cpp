#include "board.hpp"

#include "stm32f4xx_hal.h"

// Об'єкти й функції ініціалізації породжує CubeMX — ми ними користуємося.
extern "C" {
extern SPI_HandleTypeDef hspi1;
extern UART_HandleTypeDef huart2;

void SystemClock_Config();
void MX_GPIO_Init();
void MX_SPI1_Init();
void MX_USART2_UART_Init();
}

namespace board {
namespace {

// Розведення за правилами статті: чип АЦП стоїть на межі зон, лінії SPI і
// DRDY йдуть у цифровий бік і ніде не заходять в аналоговий сектор.
constexpr GPIO_TypeDef* cs_port = GPIOA;
constexpr std::uint16_t cs_pin = GPIO_PIN_4;
constexpr GPIO_TypeDef* drdy_port = GPIOA;
constexpr std::uint16_t drdy_pin = GPIO_PIN_3;

constexpr std::uint32_t spi_timeout_ms = 50;
constexpr std::uint32_t uart_timeout_ms = 100;

}  // namespace

void init()
{
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_SPI1_Init();
    MX_USART2_UART_Init();

    // CS відпускаємо явно: після скидання вивід міг лишитися в нулі.
    HAL_GPIO_WritePin(cs_port, cs_pin, GPIO_PIN_SET);
}

bool data_ready() noexcept
{
    return HAL_GPIO_ReadPin(drdy_port, drdy_pin) == GPIO_PIN_RESET;
}

std::chrono::milliseconds uptime() noexcept
{
    return std::chrono::milliseconds{HAL_GetTick()};
}

void sleep(std::chrono::milliseconds delay) noexcept
{
    HAL_Delay(static_cast<std::uint32_t>(delay.count()));
}

void write_line(std::string_view text) noexcept
{
    if (!text.empty()) {
        HAL_UART_Transmit(&huart2,
                          reinterpret_cast<std::uint8_t*>(const_cast<char*>(text.data())),
                          static_cast<std::uint16_t>(text.size()),
                          uart_timeout_ms);
    }

    static constexpr char eol[] = "\r\n";
    HAL_UART_Transmit(&huart2,
                      reinterpret_cast<std::uint8_t*>(const_cast<char*>(eol)),
                      2,
                      uart_timeout_ms);
}

SpiBus::Selection::Selection(SpiBus& bus) noexcept : bus_{bus}
{
    bus_.assert_cs();
}

SpiBus::Selection::~Selection() noexcept
{
    bus_.release_cs();
}

void SpiBus::assert_cs() noexcept
{
    HAL_GPIO_WritePin(cs_port, cs_pin, GPIO_PIN_RESET);
}

void SpiBus::release_cs() noexcept
{
    HAL_GPIO_WritePin(cs_port, cs_pin, GPIO_PIN_SET);
}

bool SpiBus::transfer(std::span<const std::uint8_t> tx, std::span<std::uint8_t> rx) noexcept
{
    if (tx.empty() || tx.size() != rx.size() || tx.size() > UINT16_MAX) {
        return false;
    }

    // HAL приймає буфер передавання без const; вміст лишається недоторканим.
    const auto status = HAL_SPI_TransmitReceive(
        &hspi1,
        const_cast<std::uint8_t*>(tx.data()),
        rx.data(),
        static_cast<std::uint16_t>(tx.size()),
        spi_timeout_ms);

    return status == HAL_OK;
}

}  // namespace board

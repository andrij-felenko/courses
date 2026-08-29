#include "isr/i2c_relay.hpp"

#include "FreeRTOS.h"
#include "task.h"

#include "stm32f4xx.h"
#include "stm32f4xx_ll_i2c.h"
#include "stm32f4xx_ll_usart.h"

#include "isr/spsc_ring.hpp"

#include <array>
#include <atomic>

namespace isr {
namespace {

constexpr std::uint8_t kSensorAddr7 = 0x48;
constexpr TickType_t kI2cTimeout = pdMS_TO_TICKS(20);
constexpr std::uint32_t kRelayStackWords = 256;

SpscRing<std::uint8_t, 256> g_relay_ring{};
TaskHandle_t g_relay_task = nullptr;
StaticTask_t g_relay_tcb;
std::array<StackType_t, kRelayStackWords> g_relay_stack;

std::atomic<std::uint32_t> g_dropped{0};
std::atomic<std::uint32_t> g_failures{0};

// STOP мусить піти на КОЖНОМУ виході з розпочатої транзакції — і на
// успішному, і на будь-якому помилковому. У C це пишуть як goto out
// із міткою в кінці функції; тут за це відповідає час життя об'єкта,
// і забути гілку неможливо — навіть ту, яку допишуть через рік.
class StopOnExit {
public:
    StopOnExit() = default;

    ~StopOnExit() noexcept { LL_I2C_GenerateStopCondition(I2C1); }

    StopOnExit(const StopOnExit &) = delete;
    StopOnExit &operator=(const StopOnExit &) = delete;
};

} // namespace

// ===========================================================================
// ТАК РОБИТИ НЕ МОЖНА.
//
// Функція навмисно не називається USART2_IRQHandler і нікуди не підключена:
// вона тут як експонат. Досить одному давачеві затиснути SDA до землі —
// і ядро назавжди залишиться всередині while, з погашеними перериваннями
// свого й нижчих рівнів. Аварійна лінія в такій системі більше не спрацює.
// ===========================================================================
extern "C" void usart2_isr_trap_never_link()
{
    if (LL_USART_IsActiveFlag_RXNE(USART2)) {
        const auto data = static_cast<std::uint8_t>(LL_USART_ReceiveData8(USART2));

        while (!LL_I2C_IsActiveFlag_TXE(I2C1)) {
            // Умова виходу залежить від чужого дроту. Обробник не має права
            // ставити свою тривалість у таку залежність.
        }
        LL_I2C_TransmitData8(I2C1, data);
    }
}

// ===========================================================================
// ТАК ТРЕБА.
// ===========================================================================
void I2cRelay::handle_irq() noexcept
{
    BaseType_t higher_priority_woken = pdFALSE;

    if (LL_USART_IsActiveFlag_ORE(USART2)) {
        LL_USART_ClearFlag_ORE(USART2);
    }

    while (LL_USART_IsActiveFlag_RXNE(USART2)) {
        const auto data = static_cast<std::uint8_t>(LL_USART_ReceiveData8(USART2));
        if (!g_relay_ring.push_from_isr(data)) {
            g_dropped.fetch_add(1, std::memory_order_relaxed);
        }
    }

    if (g_relay_task != nullptr) {
        vTaskNotifyGiveFromISR(g_relay_task, &higher_priority_woken);
    }
    portYIELD_FROM_ISR(higher_priority_woken);
}

std::expected<void, I2cError> I2cRelay::write(std::uint8_t addr7, std::uint8_t data) noexcept
{
    const TickType_t deadline = xTaskGetTickCount() + kI2cTimeout;

    // Те саме очікування прапорця, що й у пастці вище, — але з кінцевим
    // терміном і з поверненням керування планувальнику. У контексті
    // завдання це законно: поки ми чекаємо, система живе далі.
    const auto wait_for = [deadline](auto &&ready) noexcept -> std::expected<void, I2cError> {
        while (!ready()) {
            if (LL_I2C_IsActiveFlag_BERR(I2C1)) {
                LL_I2C_ClearFlag_BERR(I2C1);
                return std::unexpected(I2cError::BusError);
            }
            if (LL_I2C_IsActiveFlag_AF(I2C1)) {
                LL_I2C_ClearFlag_AF(I2C1);
                return std::unexpected(I2cError::Nack);
            }
            if (xTaskGetTickCount() > deadline) {
                return std::unexpected(I2cError::Timeout);
            }
            taskYIELD();
        }
        return {};
    };

    // Поки транзакції немає, STOP видавати нема за що — тому вартовий
    // з'являється рівно після START і жодним раннім виходом не обходиться.
    if (auto r = wait_for([] { return !LL_I2C_IsActiveFlag_BUSY(I2C1); }); !r) {
        return r;
    }

    LL_I2C_GenerateStartCondition(I2C1);
    const StopOnExit stop;
    if (auto r = wait_for([] { return LL_I2C_IsActiveFlag_SB(I2C1) != 0; }); !r) {
        return r;
    }

    LL_I2C_TransmitData8(I2C1, static_cast<std::uint8_t>(addr7 << 1)); // біт 0 = 0: запис
    if (auto r = wait_for([] { return LL_I2C_IsActiveFlag_ADDR(I2C1) != 0; }); !r) {
        return r;
    }
    LL_I2C_ClearFlag_ADDR(I2C1);

    if (auto r = wait_for([] { return LL_I2C_IsActiveFlag_TXE(I2C1) != 0; }); !r) {
        return r;
    }
    LL_I2C_TransmitData8(I2C1, data);

    if (auto r = wait_for([] { return LL_I2C_IsActiveFlag_BTF(I2C1) != 0; }); !r) {
        return r;
    }

    return {}; // STOP видасть деструктор stop — на цьому шляху так само, як на решті
}

void I2cRelay::relay_entry(void *arg) noexcept
{
    static_cast<void>(arg);

    std::array<std::uint8_t, 32> batch{};

    for (;;) {
        static_cast<void>(ulTaskNotifyTake(pdTRUE, portMAX_DELAY));

        bool bus_broken = false;
        while (!bus_broken) {
            const std::span<std::uint8_t> chunk = g_relay_ring.drain(batch);
            if (chunk.empty()) {
                break;
            }
            for (const std::uint8_t byte : chunk) {
                if (!write(kSensorAddr7, byte)) {
                    // Шину заклинило. У контексті завдання це просто помилка;
                    // всередині обробника та сама ситуація зупинила б пристрій.
                    g_failures.fetch_add(1, std::memory_order_relaxed);
                    bus_broken = true;
                    break;
                }
            }
        }

        if (bus_broken) {
            // Скидаємо ВСЮ решту черги — байти, які нікуди віддати,
            // краще загубити явно й порахувати, ніж тримати вічно.
            for (;;) {
                const auto rest = g_relay_ring.drain(batch);
                if (rest.empty()) {
                    break;
                }
                g_dropped.fetch_add(static_cast<std::uint32_t>(rest.size()),
                                    std::memory_order_relaxed);
            }
            vTaskDelay(pdMS_TO_TICKS(50)); // дати периферії видихнути
        }
    }
}

void I2cRelay::start()
{
    g_relay_task = xTaskCreateStatic(&I2cRelay::relay_entry,
                                     "i2c-relay",
                                     kRelayStackWords,
                                     nullptr,
                                     configMAX_PRIORITIES - 3,
                                     g_relay_stack.data(),
                                     &g_relay_tcb);
    configASSERT(g_relay_task != nullptr);
}

std::uint32_t I2cRelay::dropped() noexcept
{
    return g_dropped.load(std::memory_order_relaxed);
}

std::uint32_t I2cRelay::failures() noexcept
{
    return g_failures.load(std::memory_order_relaxed);
}

} // namespace isr

extern "C" void USART2_IRQHandler()
{
    isr::I2cRelay::handle_irq();
}

#include "board/g0_board.hpp"
#include "pipeline/signal_pipeline.hpp"

#include "stm32g0xx.h" // __WFI із ядрового заголовка CMSIS

#include <cstdint>

namespace {

using pipeline::Millivolts;
namespace fp = pipeline::fp;

/// Уставка: тримаємо на вході половину опори.
constexpr Millivolts kSetpoint{1650};

/// Коефіцієнти задані десятковим записом, але у прошивку їдуть цілими:
/// from_double обчислюється лише під час збирання, і вихід за межі Q8.8
/// був би помилкою компіляції, а не тихим переповненням у польоті.
constexpr pipeline::Gains kGains{
    .kp = fp::from_double(2.5),
    .ki = fp::from_double(0.1),
    .kd = fp::from_double(1.2),
};

constexpr pipeline::Limits kLimits{
    .min = 0,
    .max = pipeline::kPwmMaxDuty,
};

/// Уся пам'ять конвеєра — один статичний об'єкт із alpha = 1/8.
/// constinit гарантує, що він побудований ще під час збирання: жодного
/// коду ініціалізації на старті, жодного порядку статичних об'єктів.
constinit pipeline::SignalPipeline<3> g_pipeline{kGains, kLimits};

/// Лічильник для фонового циклу. Пише його переривання, читає main.
volatile std::uint32_t g_ticks = 0;

} // namespace

/// Викликається з переривання DMA кожні 10 мс. Тут не має бути нічого,
/// крім самого конвеєра: увесь прохід — близько сімдесяти тактів, і саме
/// тому період квантування лишається незмінним.
void board::on_sample(std::uint16_t raw_code) noexcept
{
    board::set_duty(g_pipeline.step(raw_code, kSetpoint));
    ++g_ticks;
}

int main()
{
    if (auto result = board::init(); !result) {
        board::panic(result.error());
    }

    for (;;) {
        // Регулювання цілком живе в перериванні. Фоновому циклу лишається
        // зв'язок, журнал, сторожовий таймер — тут просто спимо до
        // наступного відліку й не палимо струм даремно.
        __WFI();
    }
}

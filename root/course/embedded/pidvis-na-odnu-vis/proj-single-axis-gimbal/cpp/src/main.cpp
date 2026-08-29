// main.cpp — стендовий стабілізатор горизонту на одну вісь.
//
// Плата: ATmega328P @ 16 МГц. MPU-6050 на TWI (PC4/PC5), серво на OC1A (PB1)
// від окремого BEC зі спільною землею, телеметрія на USART0.
//
// Такт контуру задає Timer2 (200 Гц). Головний цикл лише чекає прапорець:
// уся робота — читання IMU, фільтр, ПІД, вихід — робиться поза перериванням,
// щоб довгий обмін по I2C не блокував систему переривань.

#include <avr/interrupt.h>
#include <avr/io.h>
#include <util/delay.h>

#include "mpu6050.hpp"
#include "servo.hpp"
#include "stabilizer.hpp"
#include "telemetry.hpp"
#include "twi.hpp"

using namespace gimbal;

namespace {

constexpr std::uint8_t  kLedBit       = PB5;   // світлодіод плати
constexpr std::uint16_t kCalSamples   = 500;   // 500 вибірок на 200 Гц = 2.5 с
constexpr std::uint8_t  kCalAttempts  = 5;
constexpr std::uint8_t  kImuFailLimit = 5;     // збоїв підряд до визволення шини

// Стан такту. Пише переривання — тому volatile, читаємо атомарно.
volatile bool          g_tick    = false;
volatile bool          g_overrun = false;
volatile std::uint32_t g_time_ms = 0;

// Timer2 у режимі CTC: 16 МГц / 1024 = 15625 Гц, поділити на 78 → 200.3 Гц.
void tick_begin() noexcept {
    TCCR2A = (1 << WGM21);
    TCCR2B = (1 << CS22) | (1 << CS21) | (1 << CS20);
    OCR2A  = 77;
    TIMSK2 = (1 << OCIE2A);
}

// Чекає такт і повертає true, якщо попередній не встиг добігти.
bool wait_tick() noexcept {
    while (true) {
        cli();
        if (g_tick) {
            g_tick = false;
            const bool overrun = g_overrun;
            g_overrun = false;
            sei();
            return overrun;
        }
        sei();
    }
}

std::uint32_t now_ms() noexcept {
    cli();
    const std::uint32_t t = g_time_ms;
    sei();
    return t;
}

void led(bool on) noexcept {
    if (on) {
        PORTB |= static_cast<std::uint8_t>(1u << kLedBit);
    } else {
        PORTB &= static_cast<std::uint8_t>(~(1u << kLedBit));
    }
}

// Аварійний режим: вал у нейтраль, світлодіод блимає, стенд не рухається.
// Виходу звідси немає — оператор має вимкнути живлення й розібратися.
[[noreturn]] void fatal(RcServo& servo, std::string_view why) noexcept {
    servo.write(RcServo::kMid);
    telemetry::write("FATAL ");
    telemetry::write(why);
    telemetry::write("\r\n");

    while (true) {
        led(true);
        _delay_ms(120);
        led(false);
        _delay_ms(120);
    }
}

// Підняти давач: якщо шина мовчить — визволити її й спробувати ще.
bool bring_up_imu(Twi& bus, Mpu6050& imu) noexcept {
    for (std::uint8_t attempt = 0; attempt < 3; ++attempt) {
        if (imu.begin()) {
            return true;
        }
        telemetry::write("# IMU init failed, recovering bus\r\n");
        bus.recover_bus();
        _delay_ms(50);
    }
    return false;
}

// Калібрування нуля гіроскопа з перевіркою нерухомості платформи.
bool calibrate(Twi& bus, Mpu6050& imu, Stabilizer& stab) noexcept {
    for (std::uint8_t attempt = 0; attempt < kCalAttempts; ++attempt) {
        GyroCalibrator cal;
        cal.reset();

        bool bus_ok = true;
        led(true);  // горить рівно — «не чіпай, калібрую»

        for (std::uint16_t i = 0; i < kCalSamples; ++i) {
            static_cast<void>(wait_tick());

            auto sample = imu.read();
            if (!sample) {
                bus_ok = false;
                break;
            }
            cal.push(sample.value().gyro_x_dps);

            // Остання вибірка дає ще й початковий кут — стенд може стояти
            // під нахилом, і фільтру не треба повзти до істини секунду.
            if (i + 1 == kCalSamples) {
                stab.seed_angle(sample.value().accel_y_g, sample.value().accel_z_g);
            }
        }

        led(false);

        if (!bus_ok) {
            telemetry::write("# CAL bus error\r\n");
            bus.recover_bus();
            if (!bring_up_imu(bus, imu)) {
                return false;
            }
            continue;
        }

        if (const auto bias = cal.finish(kCalSamples); bias.has_value()) {
            stab.set_bias(*bias);

            telemetry::write("# CAL ok bias_mdps=");
            telemetry::write(static_cast<std::int32_t>(*bias * 1000.0f));
            telemetry::write("\r\n");
            return true;
        }

        // Дисперсія завелика: хтось тримав стенд або він хитався.
        telemetry::write("# CAL rejected: platform moving\r\n");
        _delay_ms(500);
    }

    return false;
}

}  // namespace

ISR(TIMER2_COMPA_vect) {
    if (g_tick) {
        // Головний цикл не встиг за 5 мс. Мовчки з'їсти це не можна:
        // фільтр і ПІД рахують на сталому dt, а він щойно поплив.
        g_overrun = true;
    }
    g_tick = true;
    g_time_ms += 5;
}

int main() {
    DDRB |= static_cast<std::uint8_t>(1u << kLedBit);

    telemetry::begin(115200);

    Twi bus;
    bus.begin();

    RcServo servo;
    servo.begin();

    tick_begin();
    sei();

    telemetry::write("\r\n# single-axis gimbal, 200 Hz\r\n");
    telemetry::write("# t_ms,angle_mdeg,rate_mdps,integ_mdeg,pulse_us,flags\r\n");

    Mpu6050 imu{bus};
    if (!bring_up_imu(bus, imu)) {
        fatal(servo, "IMU not responding");
    }

    // Коефіцієнти зі стенда: Kp тримає, Kd демпфує, Ki добирає статику.
    Pid::Config pid_cfg;
    pid_cfg.kp           = 2.0f;
    pid_cfg.ki           = 0.5f;
    pid_cfg.kd           = 0.08f;
    pid_cfg.d_cutoff_hz  = 25.0f;
    pid_cfg.deadband_deg = 0.3f;

    Stabilizer stab{0.98f, pid_cfg};

    if (!calibrate(bus, imu, stab)) {
        fatal(servo, "gyro calibration");
    }

    std::uint8_t imu_fails = 0;

    while (true) {
        const bool overrun = wait_tick();

        auto sample = imu.read();
        if (!sample) {
            if (++imu_fails >= kImuFailLimit) {
                // Шина злягла. Тримати вал під останньою командою, поки
                // платформа їде, гірше, ніж відпустити його в нейтраль.
                servo.write(RcServo::kMid);
                stab.reset_control();

                bus.recover_bus();
                static_cast<void>(bring_up_imu(bus, imu));
                imu_fails = 0;

                telemetry::write("# bus recovered\r\n");
            }
            continue;
        }
        imu_fails = 0;

        const ImuSample s = sample.value();
        const ControlOutput out = stab.step(s.gyro_x_dps, s.accel_y_g, s.accel_z_g);

        servo.write(out.pulse);

        // Цілими в тисячних градуса: printf із float на AVR тягне кілька
        // кілобайтів коду й сотні мікросекунд на кожен рядок.
        telemetry::write(static_cast<std::int32_t>(now_ms()));            telemetry::write(",");
        telemetry::write(static_cast<std::int32_t>(out.angle_deg * 1000.0f));  telemetry::write(",");
        telemetry::write(static_cast<std::int32_t>(out.rate_dps * 1000.0f));   telemetry::write(",");
        telemetry::write(static_cast<std::int32_t>(out.integrator * 1000.0f)); telemetry::write(",");
        telemetry::write(static_cast<std::int32_t>(out.pulse.value));      telemetry::write(",");
        telemetry::write(static_cast<std::int32_t>(overrun ? 1 : 0));
        telemetry::write("\r\n");
    }
}

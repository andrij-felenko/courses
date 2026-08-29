// Координатор вузла: один неблокуючий цикл подій на чотири чипи.
//
// Секундний меандр DS3231 будить ядро зі Stop 2 і кладе в чергу подію
// вимірювання; BME280 міряє свої десять мілісекунд, поки цикл займається
// іншим; повні сторінки записів лягають у W25Q128 автоматом, який ніде не
// чекає в while; кадри Modbus RTU приходять і йдуть через переривання
// USART, а лінію DE знімає обробник TC. Ніде немає ані delay(), ані
// очікування прапорця без тайм-ауту.

#include "mcu.hpp"
#include "modbus_slave.hpp"
#include "ring_log.hpp"
#include "sensors.hpp"
#include "spi_flash.hpp"
#include "telemetry.hpp"

namespace node {

class Coordinator {
public:
    void run() noexcept {
        setup();

        for (;;) {
            mcu::Watchdog::kick();
            log_.poll();

            while (auto event = events_.pop()) {
                dispatch(*event);
            }

            pollSensor();

            // Аварійний ритм: секундна мітка від DS3231 зникла. Спати тепер
            // не можна — прокидатися немає від чого; такт відміряє SysTick,
            // а годинник пробуємо підняти на кожному зрізі.
            if (!rtcAlive_) {
                if (!sampling_ && mcu::time::elapsed(lastSampleMs_, 1000)) {
                    startSample();
                }
                continue;
            }

            // Спати можна лише коли не лишилося ані події в черзі, ані
            // незавершеної роботи в жодного з чотирьох чипів.
            if (events_.empty() && !sampling_ && log_.idle() &&
                !modbus_.txBusy() && !modbus_.frameWaiting()) {
                mcu::enterStop2();
            }
        }
    }

    void onRtcTick() noexcept { events_.push(Event::RtcTick); }
    void onUartIrq() noexcept { modbus_.handleIrq(); }

private:
    void setup() noexcept {
        mcu::clock::configure();
        mcu::time::init(mcu::clock::kSysClkHz);
        mcu::Watchdog::start();

        bus_.begin();
        flash_.begin();
        modbus_.begin(mcu::clock::kHsi16Hz);
        setupRtcTickInput();

        sensorAlive_ = bme_.begin().has_value();
        rtcAlive_ = rtc_.begin().has_value();

        if (auto mounted = log_.mount()) {
            if (mounted->has_value()) {
                // Нумерацію продовжуємо з останнього запису в кільці, щоб
                // ведучий не побачив після перезавантаження стрибок назад.
                last_ = **mounted;
                sequence_ = last_.sequenceId;
            }
        }
    }

    static void setupRtcTickInput() noexcept {
        RCC->AHB2ENR |= RCC_AHB2ENR_GPIOAEN;
        RCC->APB2ENR |= RCC_APB2ENR_SYSCFGEN;

        const mcu::Pin tick{GPIOA, 0};
        tick.mode(mcu::Pin::Mode::Input);
        tick.pull(mcu::Pin::Pull::Up);   // вихід чипа з відкритим стоком

        SYSCFG->EXTICR[0] &= ~SYSCFG_EXTICR1_EXTI0;   // лінія EXTI0 з порту A
        EXTI->FTSR1 |= EXTI_FTSR1_FT0;                // спадний фронт меандра 1 Гц
        EXTI->RTSR1 &= ~EXTI_RTSR1_RT0;
        EXTI->IMR1  |= EXTI_IMR1_IM0;

        NVIC_SetPriority(EXTI0_IRQn, 1u);
        NVIC_EnableIRQ(EXTI0_IRQn);
    }

    void dispatch(Event event) noexcept {
        switch (event) {
        case Event::RtcTick:
            startSample();
            break;
        case Event::Rs485Frame:
            modbus_.service(last_);
            break;
        case Event::Rs485Sent:
        case Event::FlashIdle:
            break;   // автомати вже все зробили
        }
    }

    void startSample() noexcept {
        if (sampling_) return;   // попереднє ще не забрали

        if (!bme_.startMeasurement()) {
            // Шина мовчить — найімовірніше завис ведений. Розблоковуємо й
            // піднімаємо датчик наново; не вийде — запишемо зріз без нього.
            bus_.recoverBus();
            sensorAlive_ = bme_.begin() && bme_.startMeasurement();
        } else {
            sensorAlive_ = true;
        }

        sampling_ = true;
        sampleStartedMs_ = mcu::time::millis();
        lastSampleMs_ = sampleStartedMs_;
    }

    void pollSensor() noexcept {
        if (!sampling_) return;

        if (!sensorAlive_) {
            finishSample(std::nullopt);
            return;
        }

        const auto ready = bme_.ready();
        if (ready && *ready) {
            const auto sample = bme_.read();
            finishSample(sample ? std::optional{*sample} : std::nullopt);
        } else if (mcu::time::elapsed(sampleStartedMs_, kSampleLimitMs)) {
            // Датчик не звільнив прапорець measuring за вчетверо довший час,
            // ніж обіцяє паспорт: пишемо зріз без нього.
            sensorAlive_ = false;
            finishSample(std::nullopt);
        }
    }

    void finishSample(std::optional<Bme280::Sample> sample) noexcept {
        Record rec{};
        Status flags = Status::None;

        if (sample) {
            rec.temperature = sample->temperatureC100;
            rec.pressure    = sample->pressurePa100;
            rec.humidity    = sample->humidityRh1024;
            flags |= Status::SensorBmeOk;
        }

        if (const auto time = rtc_.now()) {
            rtcAlive_ = true;
            rec.timestamp = time->unix;
            if (time->oscillatorValid) flags |= Status::RtcSyncOk;
        } else {
            // Годинник не відповів: мітку рахуємо від попередньої. Запис від
            // цього не зникає — зникає лише довіра до його часу. Чип піднімаємо
            // наново: разом із налаштуваннями могла зникнути й секундна мітка
            // на INT/SQW, а без неї вузол більше не прокинеться.
            rtcAlive_ = false;
            rec.timestamp = last_.timestamp + 1u;
            bus_.recoverBus();
            rtcAlive_ = rtc_.begin().has_value();
        }

        if (log_.lastWriteOk())      flags |= Status::FlashLogOk;   // стан ОСТАННЬОЇ сторінки
        if (modbus_.masterActive())  flags |= Status::Rs485Active;

        rec.sequenceId = ++sequence_;
        rec.status = flags;
        rec.crc = computeCrc(rec);

        last_ = rec;
        (void)log_.append(rec);
        sampling_ = false;
    }

    static constexpr std::uint32_t kSampleLimitMs = 50;   // BME280 на ×1 міряє ~10 мс

    EventQueue<16> events_{};
    I2cMaster      bus_{};
    SpiFlash       flash_{};
    Bme280         bme_{bus_};
    Ds3231         rtc_{bus_};
    RingLog        log_{flash_, events_};
    ModbusSlave    modbus_{events_};

    Record        last_{};
    std::uint16_t sequence_{0};
    std::uint32_t sampleStartedMs_{0};
    std::uint32_t lastSampleMs_{0};
    bool          sampling_{false};
    bool          sensorAlive_{false};
    bool          rtcAlive_{false};   // меандр 1 Гц живий — інакше не прокинемось
};

// Єдиний екземпляр із локальною статикою: до нього дотягуються обробники
// переривань, і жодного глобального конструктора до входу в main.
Coordinator& coordinator() noexcept {
    static Coordinator instance;
    return instance;
}

}  // namespace node

extern "C" {

void SysTick_Handler(void) {
    ++mcu::time::g_ms;
}

void EXTI0_IRQHandler(void) {
    EXTI->PR1 = EXTI_PR1_PIF0;
    node::coordinator().onRtcTick();
}

void USART1_IRQHandler(void) {
    node::coordinator().onUartIrq();
}

}  // extern "C"

int main() {
    node::coordinator().run();
}

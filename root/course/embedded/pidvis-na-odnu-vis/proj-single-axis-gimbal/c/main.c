/* main.c — стендовий стабілізатор горизонту на одну вісь.
 *
 * Плата: ATmega328P @ 16 МГц. Давач MPU-6050 на TWI (PC4/PC5), серво на
 * OC1A (PB1) від окремого BEC зі спільною землею, телеметрія на USART0.
 *
 * Такт контуру задає Timer2 (200 Гц). Головний цикл лише чекає прапорець:
 * уся робота — читання IMU, фільтр, ПІД, вихід — робиться поза
 * перериванням, щоб довгий обмін по I2C не блокував систему переривань. */

#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/delay.h>

#include "gimbal_controller.h"
#include "i2c.h"
#include "mpu6050.h"
#include "servo.h"
#include "uart.h"

#define LED_BIT PB5                 /* Світлодіод плати: стан стенда */

#define CAL_SAMPLES     500u        /* 500 вибірок на 200 Гц = 2.5 с спокою */
#define CAL_ATTEMPTS    5u          /* Скільки разів пробувати перекалібрувати */
#define IMU_FAIL_LIMIT  5u          /* Підряд збоїв шини до її відновлення */

/* Прапорець такту й лічильник часу. Обидва пише переривання —
 * тому volatile, і читаємо їх із вимкненими перериваннями. */
static volatile uint8_t  g_tick;
static volatile uint8_t  g_overrun;   /* Такт настав, а попередній ще не добіг */
static volatile uint32_t g_time_ms;

ISR(TIMER2_COMPA_vect)
{
    if (g_tick) {
        /* Головний цикл не встиг за 5 мс. Мовчки з'їсти це не можна:
         * дискретний фільтр і ПІД рахують на сталому dt, а він щойно
         * поплив. Прапорець доїде в телеметрію. */
        g_overrun = 1;
    }
    g_tick = 1;
    g_time_ms += 5;
}

/* Timer2 у режимі CTC: 16 МГц / 1024 = 15625 Гц, поділити на 78 → 200.3 Гц. */
static void tick_init(void)
{
    TCCR2A = (1 << WGM21);
    TCCR2B = (1 << CS22) | (1 << CS21) | (1 << CS20);
    OCR2A  = 77;
    TIMSK2 = (1 << OCIE2A);
}

/* Чекає наступного такту й забирає прапорець. */
static uint8_t wait_tick(void)
{
    uint8_t overrun;

    while (1) {
        cli();
        if (g_tick) {
            g_tick   = 0;
            overrun  = g_overrun;
            g_overrun = 0;
            sei();
            return overrun;
        }
        sei();
        /* Спати не йдемо: прокидання зі сну коштує тактів,
         * а робити на цьому стенді все одно нічого. */
    }
}

static uint32_t now_ms(void)
{
    uint32_t t;
    cli();
    t = g_time_ms;
    sei();
    return t;
}

static void led_set(uint8_t on)
{
    if (on) PORTB |=  (1 << LED_BIT);
    else    PORTB &= (uint8_t)~(1 << LED_BIT);
}

/* Аварійний режим: серво в нейтраль, світлодіод блимає, стенд не рухається.
 * Виходу звідси немає — оператор має вимкнути живлення й розібратися. */
static void fatal(const char *why)
{
    servo_write_us(1500);
    uart_write("FATAL ");
    uart_write(why);
    uart_write("\r\n");

    while (1) {
        led_set(1);
        _delay_ms(120);
        led_set(0);
        _delay_ms(120);
    }
}

/* Підняти давач: якщо шина мовчить — визволити її й спробувати ще. */
static uint8_t bring_up_imu(void)
{
    for (uint8_t attempt = 0; attempt < 3; ++attempt) {
        if (mpu6050_init() == I2C_OK) {
            return 1;
        }
        uart_write("IMU init failed, recovering bus\r\n");
        i2c_bus_recover();
        _delay_ms(50);
    }
    return 0;
}

/* Калібрування нуля гіроскопа. Повертає 0, якщо стенд так і не завмер:
 * стартувати з невідомим зсувом не можна — кут поїде за хвилину. */
static uint8_t calibrate(SingleAxisGimbal *g)
{
    for (uint8_t attempt = 0; attempt < CAL_ATTEMPTS; ++attempt) {
        GyroCal cal;
        gyro_cal_reset(&cal);

        imu_sample_t s;
        uint8_t      bus_ok = 1;

        led_set(1);   /* Горить рівно — «не чіпай, калібрую» */

        for (uint16_t i = 0; i < CAL_SAMPLES; ++i) {
            (void)wait_tick();

            if (mpu6050_read(&s) != I2C_OK) {
                bus_ok = 0;
                break;
            }
            gyro_cal_push(&cal, s.gyro_x_dps);

            /* Останню вибірку беремо ще й для початкового кута:
             * стенд може стояти під нахилом, і фільтру не треба
             * повзти до істини від нуля цілу секунду. */
            if (i + 1u == CAL_SAMPLES) {
                gimbal_seed_angle(g, s.accel_y_g, s.accel_z_g);
            }
        }

        led_set(0);

        if (!bus_ok) {
            uart_write("CAL bus error\r\n");
            i2c_bus_recover();
            if (!bring_up_imu()) {
                return 0;
            }
            continue;
        }

        float bias = 0.0f;
        if (gyro_cal_finish(&cal, CAL_SAMPLES, &bias)) {
            gimbal_set_bias(g, bias);

            uart_write("CAL ok bias_mdps=");
            uart_write_i32((int32_t)(bias * 1000.0f));
            uart_write("\r\n");
            return 1;
        }

        /* Дисперсія завелика: хтось тримав стенд або він хитався. */
        uart_write("CAL rejected: platform moving\r\n");
        _delay_ms(500);
    }

    return 0;
}

int main(void)
{
    DDRB |= (1 << LED_BIT);

    uart_init(115200);
    i2c_init();
    servo_init();
    tick_init();
    sei();

    uart_write("\r\n# single-axis gimbal, 200 Hz\r\n");
    uart_write("# t_ms,angle_mdeg,rate_mdps,integ_mdeg,pulse_us,flags\r\n");

    if (!bring_up_imu()) {
        fatal("IMU not responding");
    }

    /* Коефіцієнти зі стенда: Kp тримає, Kd демпфує, Ki добирає статику.
     * Зріз похідної 25 Гц — вище смуги контуру, нижче вібрації мотора. */
    const GimbalConfig cfg = {
        .alpha        = 0.98f,
        .kp           = 2.0f,
        .ki           = 0.5f,
        .kd           = 0.08f,
        .d_cutoff_hz  = 25.0f,
        .deadband_deg = 0.3f
    };

    SingleAxisGimbal gimbal;
    gimbal_init(&gimbal, &cfg);

    if (!calibrate(&gimbal)) {
        fatal("gyro calibration");
    }

    uint8_t imu_fails = 0;

    while (1) {
        const uint8_t overrun = wait_tick();

        imu_sample_t sample;
        if (mpu6050_read(&sample) != I2C_OK) {
            imu_fails++;

            if (imu_fails >= IMU_FAIL_LIMIT) {
                /* Шина злягла. Тримати вал під останньою командою, поки
                 * платформа їде, — гірше, ніж відпустити його в нейтраль. */
                servo_write_us(1500);
                gimbal_reset_control(&gimbal);

                i2c_bus_recover();
                (void)bring_up_imu();
                imu_fails = 0;

                uart_write("# bus recovered\r\n");
            }
            continue;
        }
        imu_fails = 0;

        GimbalOutput out;
        gimbal_step(&gimbal, sample.gyro_x_dps, sample.accel_y_g, sample.accel_z_g, &out);

        servo_write_us(out.pulse_us);

        /* Телеметрія цілими в тисячних градуса: printf із float на AVR
         * тягне за собою кілька кілобайтів коду й сотні мікросекунд. */
        uart_write_i32((int32_t)now_ms());          uart_write(",");
        uart_write_i32((int32_t)(out.angle_deg  * 1000.0f)); uart_write(",");
        uart_write_i32((int32_t)(out.rate_dps   * 1000.0f)); uart_write(",");
        uart_write_i32((int32_t)(out.integrator * 1000.0f)); uart_write(",");
        uart_write_i32((int32_t)out.pulse_us);      uart_write(",");
        uart_write_i32(overrun ? 1 : 0);
        uart_write("\r\n");
    }
}

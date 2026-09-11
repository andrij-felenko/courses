#ifndef XPT8871_H
#define XPT8871_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include "stm32f4xx_hal.h"

/*
 * Драйвер монофонічного звукового підсилювача потужності XPT8871 (клас AB/D, до 5 Вт).
 * 
 * Особливості керування:
 * - Лінія SHDN (Shutdown, пін 1):
 *   Логічна '1' (VDD) вмикає вихідні каскади, логічний '0' (GND) переводить мікросхему
 *   в енергоощадний режим сну зі струмом споживання менше 1 мкА.
 * - Захист від пускових клацань (Pop-and-Click):
 *   Внутрішнє джерело опорної напруги VDD/2 заряджає зовнішній фільтрувальний конденсатор
 *   на виводі BYPASS. Подача динамічного аудіосигналу дозволяється лише після стабілізації
 *   робочої точки (затримка t_wakeup близько 50 мс).
 * - Автоматичний сон під час простою:
 *   Коли кільцевий буфер вичерпується, вихідний сигнал утримується на рівні зміщення тиші,
 *   а після вичерпання таймауту простою підсилювач вимикається лінією SHDN. Це повністю
 *   усуває фонове шипіння та наведення в паузах.
 */

/* Розмір кільцевого буфера аудіосемплів (степінь двійки для швидкої маски) */
#define XPT8871_BUFFER_SIZE         512U
#define XPT8871_BUFFER_MASK         (XPT8871_BUFFER_SIZE - 1U)

/* Рівень зміщення (тиші) для 8-бітного ЦАП: VDD / 2 = 128 */
#define XPT8871_SAMPLE_BIAS         128U

/* Час стабілізації напруги BYPASS при пробудженні (мс) */
#define XPT8871_WAKEUP_DELAY_MS     50U

/* Таймаут бездіяльності перед автоматичним переходом у режим сну (мс) */
#define XPT8871_IDLE_TIMEOUT_MS     100U

/* Стан кінцевого автомата драйвера */
typedef enum {
    XPT8871_STATE_SLEEP = 0,        /* Підсилювач вимкнено (SHDN = LOW, споживання < 1 мкА) */
    XPT8871_STATE_WAKING,           /* SHDN = HIGH, триває заряд конденсатора BYPASS */
    XPT8871_STATE_PLAYING,          /* Активне потокове відтворення аудіосемплів */
    XPT8871_STATE_IDLE_DRAIN        /* Буфер спорожнів: утримання зміщення перед сном */
} xpt8871_state_t;

/* Конфігурація апаратних виводів та периферії мікроконтролера */
typedef struct {
    GPIO_TypeDef       *shdn_port;   /* Порт лінії SHDN (наприклад, GPIOB) */
    uint16_t            shdn_pin;    /* Пін лінії SHDN (наприклад, GPIO_PIN_0) */
    DAC_HandleTypeDef  *hdac;        /* Дескриптор апаратного ЦАП */
    uint32_t            dac_channel; /* Канал ЦАП (наприклад, DAC_CHANNEL_1 / PA4) */
    TIM_HandleTypeDef  *htim;        /* Дескриптор таймера дискретизації */
} xpt8871_hw_config_t;

/* Безпечний кільцевий буфер семплів SPSC (Single Producer, Single Consumer) */
typedef struct {
    uint8_t             data[XPT8871_BUFFER_SIZE];
    volatile uint16_t   head;        /* Індекс запису (головний потік) */
    volatile uint16_t   tail;        /* Індекс читання (таймерне переривання) */
} xpt8871_ring_buffer_t;

/* Контекст драйвера XPT8871 */
typedef struct {
    xpt8871_hw_config_t   config;
    xpt8871_ring_buffer_t buffer;
    volatile xpt8871_state_t state;

    uint32_t              sample_rate_hz;
    volatile uint32_t     wakeup_ticks_remaining;
    volatile uint32_t     idle_ticks_remaining;
} xpt8871_t;

/* Ініціалізація драйвера та переведення підсилювача в безпечний початковий стан сну */
bool xpt8871_init(xpt8871_t *dev, const xpt8871_hw_config_t *config, uint32_t sample_rate_hz);

/* Деініціалізація драйвера та зупинка периферії */
void xpt8871_deinit(xpt8871_t *dev);

/*
 * Неблокувальний запис блоку аудіосемплів у кільцевий буфер.
 * Якщо підсилювач спав, функція автоматично запускає апаратне пробудження.
 * Повертає кількість реально записаних семплів.
 */
size_t xpt8871_write(xpt8871_t *dev, const uint8_t *samples, size_t count);

/* Запис одного семпла в кільцевий буфер */
bool xpt8871_write_sample(xpt8871_t *dev, uint8_t sample);

/* Отримання кількості вільних байтів у буфері */
size_t xpt8871_get_free_space(const xpt8871_t *dev);

/* Перевірка, чи активне відтворення звуку або живлення підсилювача */
bool xpt8871_is_playing(const xpt8871_t *dev);

/* Примусова зупинка відтворення та негайний перехід у сплячий режим */
void xpt8871_stop(xpt8871_t *dev);

/*
 * Обробник таймерних переривань частоти дискретизації.
 * Викликається з обробника переривань апаратного таймера (наприклад, TIM6_DAC_IRQHandler).
 */
void xpt8871_timer_isr(xpt8871_t *dev);

#endif /* XPT8871_H */

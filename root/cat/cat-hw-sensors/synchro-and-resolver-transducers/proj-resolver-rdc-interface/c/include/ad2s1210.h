#ifndef AD2S1210_H
#define AD2S1210_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @file ad2s1210.h
 * @brief Модульний C-драйвер перетворювача резольвер-код AD2S1210 (Analog Devices).
 *
 * Забезпечує керування режимами роботи (A0, A1), стробуванням SAMPLE,
 * обміном даними через SPI, зчитуванням кутового положення та швидкості,
 * конфігурацією роздільної здатності та частоти збудження, а також розширеною
 * діагностикою апаратних помилок індуктивного зв'язку (LOT, DOS, LOS).
 */

/* Математичні константи */
#ifndef M_PI
#define M_PI 3.14159265358979323846f
#endif

/**
 * @brief Перелічення режимів роботи мікросхеми AD2S1210 (керування лініями A0, A1).
 */
typedef enum {
    AD2S1210_MODE_POSITION = 0, /**< A0 = 0, A1 = 0: Вибірка кутового положення (Position mode) */
    AD2S1210_MODE_VELOCITY = 1, /**< A0 = 0, A1 = 1: Вибірка кутової швидкості (Velocity mode) */
    AD2S1210_MODE_RESERVED = 2, /**< A0 = 1, A1 = 0: Зарезервований режим */
    AD2S1210_MODE_CONFIG   = 3  /**< A0 = 1, A1 = 1: Конфігураційний режим (доступ до регістрів) */
} ad2s1210_mode_t;

/**
 * @brief Перелічення роздільної здатності следящого перетворювача (Tracking RDC).
 */
typedef enum {
    AD2S1210_RES_10BIT = 10, /**< 10 біт (0..1023, макс. швидкість ~2500 RPS) */
    AD2S1210_RES_12BIT = 12, /**< 12 біт (0..4095, макс. швидкість ~1000 RPS) */
    AD2S1210_RES_14BIT = 14, /**< 14 біт (0..16383, макс. швидкість ~500 RPS) */
    AD2S1210_RES_16BIT = 16  /**< 16 біт (0..65535, макс. швидкість ~125 RPS) */
} ad2s1210_resolution_t;

/**
 * @brief Ідентифікатори апаратних виводів керування та діагностики AD2S1210.
 */
typedef enum {
    AD2S1210_PIN_SAMPLE = 0, /**< Вхід стробування latch (активний низький) */
    AD2S1210_PIN_A0,         /**< Вивід селектора режиму A0 */
    AD2S1210_PIN_A1,         /**< Вивід селектора режиму A1 */
    AD2S1210_PIN_RESET,      /**< Вхід апаратного скидання (активний низький) */
    AD2S1210_PIN_CS,         /**< Вхід вибору веденого SPI Chip Select (активний низький) */
    AD2S1210_PIN_LOT,        /**< Вхід діагностики Loss of Tracking (активний низький) */
    AD2S1210_PIN_DOS         /**< Вхід діагностики Degradation / Loss of Signal (активний низький) */
} ad2s1210_pin_t;

/**
 * @brief Логічний стан цифрового виводу GPIO.
 */
typedef enum {
    AD2S1210_PIN_LOW = 0,
    AD2S1210_PIN_HIGH = 1
} ad2s1210_pin_state_t;

/**
 * @brief Бітові прапорці регістра апаратних помилок AD2S1210 (Fault Register 0xFF).
 *
 * У внутрішньому регістрі мікросхеми біти помилок є активними низькими (0 = помилка),
 * але у даній структурі прапорці нормалізовані до активних високих (true = помилку виявлено).
 */
typedef union {
    struct {
        uint8_t parity_error       : 1; /**< Біт 0: Помилка парності кадру SPI */
        uint8_t config_change      : 1; /**< Біт 1: Динамічна зміна конфігурації під час роботи */
        uint8_t los_lot_combined   : 1; /**< Біт 2: Одночасна втрата сигналу та трекінгу (LOS + LOT) */
        uint8_t dos_phase_err      : 1; /**< Біт 3: Помилка фази синусно-косинусного сигналу (DOS Phase) */
        uint8_t dos_mismatch       : 1; /**< Біт 4: Невідповідність амплітуд Sin/Cos (DOS Mismatch) */
        uint8_t lot_fault          : 1; /**< Біт 5: Перевищення допустимої швидкості/втрата стеження (LOT) */
        uint8_t dos_los_fault      : 1; /**< Біт 6: Повна втрата вхідного сигналу резольвера (DOS/LOS) */
        uint8_t dos_clipping       : 1; /**< Біт 7: Перевантаження / кліпінг вхідного сигналу (DOS Clipping) */
    } bits;
    uint8_t raw_byte;                   /**< Сирий байт регістра помилок */
} ad2s1210_fault_flags_t;

/**
 * @brief Структура виміряних параметрів резольвера (повна телеметрія).
 */
typedef struct {
    uint16_t raw_position;     /**< Сировий 16-бітний код кута (0..2^N - 1) */
    int16_t  raw_velocity;     /**< Сировий 16-бітний підписаний код швидкості */
    float    angle_degrees;    /**< Обчислений кут у градусах [0.0 .. 360.0) */
    float    angle_radians;    /**< Обчислений кут у радіанах [0.0 .. 2*PI) */
    float    velocity_rps;     /**< Кутова швидкість в обертах за секунду (RPS) */
    float    velocity_rpm;     /**< Кутова швидкість в обертах за хвилину (RPM) */
    float    velocity_rads;    /**< Кутова швидкість у радіанах за секунду (рад/с) */
    ad2s1210_fault_flags_t fault_flags; /**< Декодовані прапорці апаратних помилок */
    bool     lot_pin_active;   /**< Стан виводу LOT (true = виявлено помилку стеження) */
    bool     dos_pin_active;   /**< Стан виводу DOS (true = виявлено помилку сигналу) */
} ad2s1210_data_t;

/**
 * @brief Прототипи функцій зворотного виклику для апаратного рівня абстракції (HAL).
 */
typedef void (*ad2s1210_gpio_write_fn)(void *user_ctx, ad2s1210_pin_t pin, ad2s1210_pin_state_t state);
typedef ad2s1210_pin_state_t (*ad2s1210_gpio_read_fn)(void *user_ctx, ad2s1210_pin_t pin);
typedef void (*ad2s1210_delay_us_fn)(uint32_t microseconds);
typedef bool (*ad2s1210_spi_transfer_fn)(void *user_ctx, const uint8_t *tx_buf, uint8_t *rx_buf, size_t length);

/**
 * @brief Конфігураційна структура для ініціалізації драйвера AD2S1210.
 */
typedef struct {
    uint32_t clk_in_hz;                /**< Частота тактування CLKIN (наприклад, 8192000 Гц) */
    uint32_t excitation_freq_hz;       /**< Бажана частота збудження резольвера (2000..20000 Гц) */
    ad2s1210_resolution_t resolution;  /**< Початкова роздільна здатність (10, 12, 14, 16 біт) */
    bool enable_hysteresis;            /**< Увімкнення гістерезису для усунення тремтіння молодших бітів */
    bool enable_encoder_outputs;       /**< Увімкнення виходів енкодера (A, B, NM) */

    /* Zворотні виклики периферії HAL */
    ad2s1210_gpio_write_fn gpio_write;
    ad2s1210_gpio_read_fn  gpio_read;
    ad2s1210_delay_us_fn   delay_us;
    ad2s1210_spi_transfer_fn spi_transfer;
    void *user_ctx;                    /**< Вказівник на контекст користувача (SPI handle / GPIO port) */
} ad2s1210_config_t;

/**
 * @brief Головний контекст драйвера пристрою AD2S1210.
 */
typedef struct {
    ad2s1210_config_t config;          /**< Налаштування драйвера */
    ad2s1210_mode_t current_mode;      /**< Поточний встановлений апаратний режим (A0, A1) */
    bool is_initialized;               /**< Прапорець успішного завершення ініціалізації */
    uint8_t control_reg_shadow;        /**< Тіньова копія контрольного регістра 0x92 */
} ad2s1210_dev_t;

/**
 * @brief Статусні коди завершення функцій драйвера.
 */
typedef enum {
    AD2S1210_OK = 0,                   /**< Успішне виконання операції */
    AD2S1210_ERR_INVALID_ARG,          /**< Передано некоректний аргумент */
    AD2S1210_ERR_HAL_NULL,             /**< Відсутні обов'язкові callback-функції HAL */
    AD2S1210_ERR_SPI_FAIL,             /**< Збій передачі даних по SPI */
    AD2S1210_ERR_HARDWARE_FAULT,       /**< Виявлено апаратну помилку індуктивного зв'язку */
    AD2S1210_ERR_TIMEOUT,              /**< Перевищено час очікування відповіді */
    AD2S1210_ERR_NOT_INITIALIZED       /**< Драйвер не був ініціалізований */
} ad2s1210_status_t;

/* Прототипи публічних функцій */

/**
 * @brief Ініціалізація мікросхеми AD2S1210 та конфігурування первинних режимів.
 * @param dev Вказівник на контекст пристрою.
 * @param config Вказівник на конфігураційну структуру.
 * @return AD2S1210_OK у разі успіху, або відповідний код помилки.
 */
ad2s1210_status_t ad2s1210_init(ad2s1210_dev_t *dev, const ad2s1210_config_t *config);

/**
 * @brief Апаратне скидання мікросхеми через подачу імпульсу на лінію RESET.
 * @param dev Вказівник на контекст пристрою.
 * @return AD2S1210_OK або код помилки.
 */
ad2s1210_status_t ad2s1210_hardware_reset(ad2s1210_dev_t *dev);

/**
 * @brief Перемикання режиму роботи мікросхеми за допомогою ліній A0 та A1.
 * @param dev Вказівник на контекст пристрою.
 * @param mode Бажаний режим (POSITION, VELOCITY, CONFIG).
 * @return AD2S1210_OK або код помилки.
 */
ad2s1210_status_t ad2s1210_set_mode(ad2s1210_dev_t *dev, ad2s1210_mode_t mode);

/**
 * @brief Генерація стробуючого імпульсу SAMPLE для фіксації поточного кута та швидкості.
 * @param dev Вказівник на контекст пристрою.
 * @return AD2S1210_OK або код помилки.
 */
ad2s1210_status_t ad2s1210_trigger_sample(ad2s1210_dev_t *dev);

/**
 * @brief Зчитування сирого коду кутового положення через SPI.
 * @param dev Вказівник на контекст пристрою.
 * @param raw_pos Вказівник для збереження 16-бітного коду.
 * @return AD2S1210_OK або код помилки.
 */
ad2s1210_status_t ad2s1210_read_position_raw(ad2s1210_dev_t *dev, uint16_t *raw_pos);

/**
 * @brief Зчитування сирого коду кутової швидкості через SPI.
 * @param dev Вказівник на контекст пристрою.
 * @param raw_vel Вказівник для збереження 16-бітного підписаного коду.
 * @return AD2S1210_OK або код помилки.
 */
ad2s1210_status_t ad2s1210_read_velocity_raw(ad2s1210_dev_t *dev, int16_t *raw_vel);

/**
 * @brief Повний вибір параметрів резольвера (кут, швидкість, обробка помилок) в один кадр.
 * @param dev Вказівник на контекст пристрою.
 * @param data Вказівник на структуру телеметрії.
 * @return AD2S1210_OK або код помилки.
 */
ad2s1210_status_t ad2s1210_read_all(ad2s1210_dev_t *dev, ad2s1210_data_t *data);

/**
 * @brief Зчитування внутрішнього регістра апаратних помилок (Fault Register 0xFF).
 * @param dev Вказівник на контекст пристрою.
 * @param flags Вказівник на структуру прапорців помилок.
 * @return AD2S1210_OK або код помилки.
 */
ad2s1210_status_t ad2s1210_read_fault_register(ad2s1210_dev_t *dev, ad2s1210_fault_flags_t *flags);

/**
 * @brief Скидання прапорців помилок у регістрі AD2S1210.
 * @param dev Вказівник на контекст пристрою.
 * @return AD2S1210_OK або код помилки.
 */
ad2s1210_status_t ad2s1210_clear_faults(ad2s1210_dev_t *dev);

/**
 * @brief Зміна роздільної здатності следящого перетворювача (10, 12, 14, 16 біт).
 * @param dev Вказівник на контекст пристрою.
 * @param res Нова значення роздільної здатності.
 * @return AD2S1210_OK або код помилки.
 */
ad2s1210_status_t ad2s1210_set_resolution(ad2s1210_dev_t *dev, ad2s1210_resolution_t res);

/**
 * @brief Програмування частоти збудження первинної обмотки резольвера.
 * @param dev Вказівник на контекст пристрою.
 * @param freq_hz Бажана частота у Гц (від 2000 до 20000).
 * @return AD2S1210_OK або код помилки.
 */
ad2s1210_status_t ad2s1210_set_excitation_frequency(ad2s1210_dev_t *dev, uint32_t freq_hz);

/**
 * @brief Перетворення статусного коду помилки драйвера у текстовий рядок.
 * @param status Код помилки.
 * @return Символьний рядок опису.
 */
const char* ad2s1210_status_to_string(ad2s1210_status_t status);

#ifdef __cplusplus
}
#endif

#endif /* AD2S1210_H */

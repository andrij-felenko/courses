#include <stdint.h>
#include <stdbool.h>

/* Переліки для типобезпечної конфігурації пінів */
typedef enum {
    PIN_PORT_A = 0,
    PIN_PORT_B = 1,
    PIN_PORT_C = 2,
    PIN_PORT_D = 3,
    PIN_PORT_MAX
} pin_port_t;

typedef enum {
    PIN_MODE_INPUT     = 0x00,
    PIN_MODE_OUTPUT_PP = 0x01,
    PIN_MODE_OUTPUT_OD = 0x11,
    PIN_MODE_AF_PP     = 0x02,
    PIN_MODE_AF_OD     = 0x12,
    PIN_MODE_ANALOG    = 0x03
} pin_mode_t;

typedef enum {
    PIN_PULL_NONE = 0x00,
    PIN_PULL_UP   = 0x01,
    PIN_PULL_DOWN = 0x02
} pin_pull_t;

typedef enum {
    PIN_SPEED_LOW    = 0x00,
    PIN_SPEED_MEDIUM = 0x01,
    PIN_SPEED_HIGH   = 0x02,
    PIN_SPEED_VHIGH  = 0x03
} pin_speed_t;

typedef enum {
    AF_NONE = 0,
    AF1_TIM1_TIM2 = 1,
    AF4_I2C1_I2C3 = 4,
    AF5_SPI1_SPI2 = 5,
    AF7_USART1_2  = 7
} pin_af_t;

/* Структура дескриптора одного виводу */
typedef struct {
    pin_port_t  port;
    uint8_t     pin_num;     /* 0..15 */
    pin_mode_t  mode;
    pin_pull_t  pull;
    pin_speed_t speed;
    pin_af_t    af;
    const char* label;       /* Семантичне ім'я для налагодження */
} pin_descriptor_t;

/* Єдине джерело правди: Маніфест плати в пам'яті Flash (ROM) */
static const pin_descriptor_t BOARD_PINOUT_SSOT[] = {
    { PIN_PORT_A, 9,  PIN_MODE_AF_PP,     PIN_PULL_NONE, PIN_SPEED_VHIGH, AF7_USART1_2,  "DEBUG_UART_TX" },
    { PIN_PORT_A, 10, PIN_MODE_AF_PP,     PIN_PULL_UP,   PIN_SPEED_VHIGH, AF7_USART1_2,  "DEBUG_UART_RX" },
    { PIN_PORT_A, 5,  PIN_MODE_AF_PP,     PIN_PULL_NONE, PIN_SPEED_HIGH,  AF5_SPI1_SPI2,  "FLASH_SPI_SCK" },
    { PIN_PORT_A, 6,  PIN_MODE_AF_PP,     PIN_PULL_NONE, PIN_SPEED_HIGH,  AF5_SPI1_SPI2,  "FLASH_SPI_MISO"},
    { PIN_PORT_A, 7,  PIN_MODE_AF_PP,     PIN_PULL_NONE, PIN_SPEED_HIGH,  AF5_SPI1_SPI2,  "FLASH_SPI_MOSI"},
    { PIN_PORT_B, 6,  PIN_MODE_AF_OD,     PIN_PULL_UP,   PIN_SPEED_HIGH,  AF4_I2C1_I2C3,  "SENSORS_I2C_SCL"},
    { PIN_PORT_B, 7,  PIN_MODE_AF_OD,     PIN_PULL_UP,   PIN_SPEED_HIGH,  AF4_I2C1_I2C3,  "SENSORS_I2C_SDA"},
    { PIN_PORT_C, 13, PIN_MODE_INPUT,     PIN_PULL_UP,   PIN_SPEED_LOW,   AF_NONE,        "USER_BUTTON" },
    { PIN_PORT_A, 8,  PIN_MODE_OUTPUT_PP, PIN_PULL_NONE, PIN_SPEED_LOW,   AF_NONE,        "STATUS_LED" }
};

#define BOARD_PIN_COUNT (sizeof(BOARD_PINOUT_SSOT) / sizeof(BOARD_PINOUT_SSOT[0]))

/* Імітація регістрів порту GPIO для тестування без прив'язки до заліза */
typedef struct {
    volatile uint32_t MODER;
    volatile uint32_t OTYPER;
    volatile uint32_t OSPEEDR;
    volatile uint32_t PUPDR;
    volatile uint32_t IDR;
    volatile uint32_t ODR;
    volatile uint32_t BSRR;
    volatile uint32_t LCKR;
    volatile uint32_t AFR[2];
} mock_gpio_typedef_t;

static mock_gpio_typedef_t MOCK_PORTS[PIN_PORT_MAX];

/* Уніфікована функція конфігурації виводу за дескриптором */
bool pin_apply_configuration(const pin_descriptor_t* desc) {
    if (!desc || desc->port >= PIN_PORT_MAX || desc->pin_num > 15) {
        return false;
    }

    mock_gpio_typedef_t* port = &MOCK_PORTS[desc->port];
    uint32_t pin = desc->pin_num;

    /* 1. Налаштування базового режиму MODER (2 біти на пін) */
    uint32_t raw_mode = desc->mode & 0x03;
    port->MODER &= ~(0x03u << (pin * 2));
    port->MODER |= (raw_mode << (pin * 2));

    /* 2. Налаштування типу виходу OTYPER (1 біт на пін) */
    uint32_t is_open_drain = (desc->mode >> 4) & 0x01;
    if (is_open_drain) {
        port->OTYPER |= (1u << pin);
    } else {
        port->OTYPER &= ~(1u << pin);
    }

    /* 3. Налаштування швидкості наростання OSPEEDR (2 біти на пін) */
    port->OSPEEDR &= ~(0x03u << (pin * 2));
    port->OSPEEDR |= ((uint32_t)desc->speed << (pin * 2));

    /* 4. Налаштування підтяжок PUPDR (2 біти на пін) */
    port->PUPDR &= ~(0x03u << (pin * 2));
    port->PUPDR |= ((uint32_t)desc->pull << (pin * 2));

    /* 5. Налаштування альтернативної функції AFR (4 біти на пін) */
    if (raw_mode == 0x02) { /* AF Mode */
        uint32_t afr_idx = pin >> 3;         /* 0 для 0..7, 1 для 8..15 */
        uint32_t afr_shift = (pin & 0x07) * 4;
        port->AFR[afr_idx] &= ~(0x0Fu << afr_shift);
        port->AFR[afr_idx] |= ((uint32_t)desc->af << afr_shift);
    }

    return true;
}

/* Централізована ініціалізація всіх виводів системи */
bool board_pins_init(void) {
    for (size_t i = 0; i < BOARD_PIN_COUNT; ++i) {
        if (!pin_apply_configuration(&BOARD_PINOUT_SSOT[i])) {
            return false;
        }
    }
    return true;
}

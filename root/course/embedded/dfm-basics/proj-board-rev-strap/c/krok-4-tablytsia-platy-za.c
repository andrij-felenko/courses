// Що саме відрізняє ревізії одна від одної.
typedef enum { BARO_BMP280, BARO_DPS310 } baro_type_t;

typedef struct {
    baro_type_t   baro;        // який барометр напаяний на цій ревізії
    GPIO_TypeDef *servo_port;  // порт піна керма
    uint16_t      servo_pin;   // сам пін керма
    const char   *name;        // людська назва — для журналу
} board_config_t;

// Таблиця ВСІХ ревізій: індекс = номер, прочитаний зі страпів.
static const board_config_t BOARD_TABLE[] = {
    // rev 0 — дослідна: хай поводиться як rev 1 (безпечний резерв)
    [0] = { BARO_BMP280, GPIOA, GPIO_PIN_0, "rev0 (proto)"  },
    [1] = { BARO_BMP280, GPIOA, GPIO_PIN_0, "rev1"          },
    [2] = { BARO_DPS310, GPIOA, GPIO_PIN_1, "rev2"          },
    // rev 3…7 — ще не існують; заповняться, коли з'являться
};

#define BOARD_TABLE_LEN  (sizeof(BOARD_TABLE) / sizeof(BOARD_TABLE[0]))

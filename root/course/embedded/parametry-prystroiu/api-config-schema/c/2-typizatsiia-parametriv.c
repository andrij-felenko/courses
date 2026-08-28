#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define CONFIG_MAGIC 0x43464731UL /* "CFG1" в ASCII */

typedef enum {
    CONFIG_TYPE_BOOL   = 0x01, /* 1 байт: 0 або 1 */
    CONFIG_TYPE_INT32  = 0x02, /* 4 байти: знакове ціле */
    CONFIG_TYPE_UINT32 = 0x03, /* 4 байти: беззнакове ціле */
    CONFIG_TYPE_FLOAT  = 0x04, /* 4 байти: число з рухомою комою IEEE 754 */
    CONFIG_TYPE_STRING = 0x05, /* Фіксований масив char із нуль-термінатором */
    CONFIG_TYPE_BLOB   = 0x06  /* Бінарний масив довільних байтів */
} cfg_type_t;

typedef enum {
    CFG_FLAG_NONE         = 0x0000,
    CFG_FLAG_READ_ONLY    = 0x0001, /* Заборона модифікації користувачем (заводські дані) */
    CFG_FLAG_REBOOT_REQ   = 0x0002, /* Зміна набуває чинності лише після повного рестарту */
    CFG_FLAG_CONFIDENTIAL = 0x0004, /* Чутливий ключ/пароль: маскувати під час виводу в лог */
    CFG_FLAG_VOLATILE     = 0x0008, /* Тимчасовий параметр: тримати в RAM, не писати у Flash */
    CFG_FLAG_TRIAL_CRIT   = 0x0010  /* Критичний мережевий параметр: вимагає Trial Run */
} cfg_param_flags_t;

typedef enum {
    CFG_OK                   =  0, /* Успішне виконання */
    CFG_ERR_INVALID_MAGIC    = -1, /* Помилка магічних байтів сектора */
    CFG_ERR_CRC_MISMATCH     = -2, /* Порушення контрольної суми даних */
    CFG_ERR_VERSION_GAP      = -3, /* Несумісна версія схеми без функції міграції */
    CFG_ERR_OUT_OF_RANGE     = -4, /* Значення параметра виходить за межі [min, max] */
    CFG_ERR_READ_ONLY        = -5, /* Спроба запису в параметр із прапорцем READ_ONLY */
    CFG_ERR_NOT_FOUND        = -6, /* Запитаний Key ID відсутній у словнику дескрипторів */
    CFG_ERR_BUFFER_TOO_SMALL = -7, /* Буфер приймача замалий для рядка чи блоба */
    CFG_ERR_FLASH_WRITE      = -8, /* Апаратна помилка шини SPI / контролера Flash */
    CFG_ERR_TRIAL_ACTIVE     = -9, /* Спроба запустити нове випробування під час активного Trial */
    CFG_ERR_DEPENDENCY       = -10 /* Порушення крос-параметричних правил узгодженості */
} cfg_status_t;

typedef struct {
    uint32_t magic;
    uint16_t schema_version;
    uint16_t flags;
    uint32_t sequence_number;
    uint16_t payload_len;
    uint16_t reserved;
    uint32_t crc32;
} __attribute__((packed)) cfg_header_t;

typedef struct {
    uint16_t key_id;                      /* Унікальний числовий ідентифікатор параметра */
    const char *key_name;                 /* Текстове ім'я для CLI та зовнішніх протоколів */
    cfg_type_t type;                      /* Фізичний тип даних */
    uint16_t offset_in_struct;            /* Зсув поля від початку структури корисного навантаження */
    uint16_t size_bytes;                  /* Розмір поля у байтах */
    uint16_t flags;                       /* Бітова маска прав доступу та поведінки */
    int64_t  min_int;                     /* Мінімальна допустима межа цілого числа */
    int64_t  max_int;                     /* Максимальна допустима межа цілого числа */
    float    min_float;                   /* Нижня межа для чисел із рухомою комою */
    float    max_float;                   /* Верхня межа для чисел із рухомою комою */
    const void *default_value_ptr;        /* Вказівник на типове заводське значення у ROM */
    cfg_status_t (*custom_validator)(const void *val_ptr); /* Додатковий функціональний валідатор */
} cfg_descriptor_t;

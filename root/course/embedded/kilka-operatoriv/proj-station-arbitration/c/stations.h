/* Реєстр наземних станцій: хто на звʼязку і які ролі за ним записано.
 * Таблиця фіксована й статична — жодного malloc, як вимагає інваріант 1. */
#ifndef ARB_STATIONS_H
#define ARB_STATIONS_H

#include <stdbool.h>
#include <stdint.h>

#define ARB_MAX_STATIONS 8u

/* Скільки станція лежить у таблиці без жодного heartbeat, перш ніж слот звільниться.
 * Це НЕ оренда токена (та коротка, 1 с) — це прибирання давно зниклих пультів. */
#define ARB_STATION_TTL_MS 30000u

typedef enum {
    ROLE_NONE      = 0x00,
    ROLE_MONITOR   = 0x01, /* лише дивиться телеметрію */
    ROLE_PILOT     = 0x02, /* може претендувати на токен пілота */
    ROLE_PAYLOAD   = 0x04, /* камера, підвіс, скидання */
    ROLE_COMMANDER = 0x08  /* аварійне перехоплення */
} role_flag_t;

typedef struct {
    uint8_t  id;
    uint8_t  roles;        /* побітова сума role_flag_t */
    uint32_t last_seen_ms;
    bool     used;
} station_t;

typedef struct {
    station_t slot[ARB_MAX_STATIONS];
} station_table_t;

void station_table_init(station_table_t *t);

/* Записати станцію або оновити її час і ролі. NULL — таблиця забита. */
station_t *station_touch(station_table_t *t, uint8_t id, uint8_t roles, uint32_t now_ms);

const station_t *station_find(const station_table_t *t, uint8_t id);

/* Станція «жива», якщо її останній heartbeat не старший за lease_ms.
 * Порівняння через різницю — воно переживає переповнення 32-бітного лічильника мс
 * (а воно настає на 49-й день безперервної роботи борта). */
bool station_is_alive(const station_table_t *t, uint8_t id, uint32_t now_ms, uint32_t lease_ms);

/* Жива станція І має вказану роль. Саме ця перевірка стоїть на вході кожної
 * привілейованої операції: без неї «командирський» пакет міг би надіслати будь-хто. */
bool station_has_role(const station_table_t *t, uint8_t id, uint8_t role,
                      uint32_t now_ms, uint32_t lease_ms);

/* Звільнити слоти станцій, які мовчать довше за ARB_STATION_TTL_MS. */
void station_expire(station_table_t *t, uint32_t now_ms);

#endif /* ARB_STATIONS_H */

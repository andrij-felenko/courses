#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <string.h>
#include <limits.h>

enum {
    TELEM_MAGIC = 0xA5C3,
    TELEM_VER   = 1,

    OFF_MAGIC = 0,
    OFF_VER   = OFF_MAGIC + 2,
    OFF_FLAGS = OFF_VER   + 1,
    OFF_LEN   = OFF_FLAGS + 1,
    OFF_RSV   = OFF_LEN   + 2,
    OFF_TIME  = OFF_RSV   + 2,
    OFF_LAT   = OFF_TIME  + 8,
    OFF_LON   = OFF_LAT   + 4,
    OFF_ALT   = OFF_LON   + 4,
    OFF_MV    = OFF_ALT   + 4,
    OFF_CRC   = OFF_MV    + 2,
    TELEM_SIZE = OFF_CRC  + 2
};

/* Таблиця формату як перевірка, а не як коментар. */
_Static_assert(OFF_LEN  ==  4, "len стоїть на зсуві 4");
_Static_assert(OFF_TIME ==  8, "time_us стоїть на зсуві 8");
_Static_assert(OFF_LAT  == 16, "lat_e7 стоїть на зсуві 16");
_Static_assert(OFF_CRC  == 30, "контрольна сума — два останні байти");
_Static_assert(TELEM_SIZE == 32, "повідомлення — рівно 32 байти");

/* Природне вирівнювання: кожне поле на зсуві, кратному своєму розміру. */
_Static_assert(OFF_TIME % 8 == 0, "64-бітне поле — на кратному 8");
_Static_assert(OFF_LAT % 4 == 0 && OFF_LON % 4 == 0 && OFF_ALT % 4 == 0,
               "32-бітні поля — на кратних 4");
_Static_assert(OFF_MV % 2 == 0 && OFF_CRC % 2 == 0,
               "16-бітні поля — на кратних 2");

/* Припущення кодека про платформу. */
_Static_assert(CHAR_BIT == 8, "кодек припускає восьмибітний байт");
_Static_assert(sizeof(float) == 4, "f32 має бути чотирибайтним");

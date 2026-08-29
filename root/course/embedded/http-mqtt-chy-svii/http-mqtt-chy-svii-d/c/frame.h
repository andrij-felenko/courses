/* frame.h — формат кадру телеметрії: 16 байтів на дроті, без вирівнювання.
 *
 * Кадр навмисно описаний упакованою структурою: покажчик на неї йде просто
 * в sendto(), без серіалізатора, без malloc, без форматерів рядків. */
#ifndef FRAME_H
#define FRAME_H

#include <stddef.h>
#include <stdint.h>

/* Порядок байтів у кадрі фіксований — little-endian. Обидва кінці (Cortex-M
 * і x86-шлюз) зберігають числа так само, тож структура кладеться в датаграму
 * як є. На big-endian платформі знадобилися б перестановки, тому — стоп. */
#if defined(__BYTE_ORDER__) && (__BYTE_ORDER__ != __ORDER_LITTLE_ENDIAN__)
#error "frame.h: формат кадру little-endian, потрібні перестановки байтів"
#endif

#define FRAME_MAGIC     0xA5u  /* магічний байт початку кадру */
#define MSG_TELEMETRY   0x01u
#define MSG_ACK         0x02u

#define TELEMETRY_SIZE  16u
#define ACK_SIZE         4u

#pragma pack(push, 1)
typedef struct {
    uint8_t  magic;       /* 0xA5 — відсіює чужі датаграми на порті */
    uint8_t  msg_type;    /* 0x01 — телеметрія */
    uint16_t seq_num;     /* лічильник кадру: втрати й дублікати видно серверу */
    uint32_t timestamp;   /* час вимірювання, Unix time */
    int16_t  temperature; /* °C * 100: від -327.68 до +327.67 */
    uint16_t humidity;    /* % * 100: 0..10000 */
    uint16_t vbat_mv;     /* напруга батареї, мВ */
    uint16_t crc16;       /* CRC-16-CCITT по перших 14 байтах */
} sensor_packet_t;
#pragma pack(pop)

/* Якщо компілятор проігнорує pragma pack — кадр роз'їдеться, і краще про це
 * дізнатися під час збірки, а не по сміттю в базі шлюзу. */
_Static_assert(sizeof(sensor_packet_t) == TELEMETRY_SIZE,
               "кадр телеметрії мусить бути рівно 16 байтів");

/* Вимір у «людських» одиницях зберігання: те, що прошивка отримала з давача. */
typedef struct {
    uint32_t timestamp;
    int16_t  temperature;
    uint16_t humidity;
    uint16_t vbat_mv;
} sensor_sample_t;

enum {
    FRAME_OK      =  0,
    FRAME_E_SHORT = -1,  /* датаграма коротша за кадр */
    FRAME_E_MAGIC = -2,  /* не наш протокол */
    FRAME_E_TYPE  = -3,  /* не той тип повідомлення */
    FRAME_E_CRC   = -4,  /* кадр побився в дорозі */
    FRAME_E_SPACE = -5   /* буфер замалий */
};

uint16_t frame_crc16(const uint8_t *data, size_t len);

/* Повертає довжину складеного кадру або від'ємний код помилки. */
int frame_pack_telemetry(const sensor_sample_t *sample, uint16_t seq,
                         uint8_t *buf, size_t cap);

/* Перевіряє магію, тип і CRC; при успіху копіює поля в *out. */
int frame_parse_telemetry(const uint8_t *buf, size_t len, sensor_packet_t *out);

int frame_pack_ack(uint16_t seq, uint8_t *buf, size_t cap);
int frame_parse_ack(const uint8_t *buf, size_t len, uint16_t *seq_out);

const char *frame_strerror(int code);

#endif /* FRAME_H */

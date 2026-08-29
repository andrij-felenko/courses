// Спільний формат телеметрії вузла та три способи запакувати його в мережу (C99).
#ifndef TELEMETRY_H
#define TELEMETRY_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Власний бінарний протокол: синхробайт і тип повідомлення.
#define FRAME_MAGIC      0xAAu
#define FRAME_TYPE_TELEM 0x01u

// Те, що вузол справді виміряв. Жодного float: усе цілими у фіксованій точці,
// бо перетворення в текст із комою — найдорожча операція в усьому ланцюжку.
typedef struct {
    uint32_t timestamp_s;   // Unix-час або uptime, секунди
    int16_t  temp_centi_c;  // 2450 = 24.50 °C (може бути відʼємним)
    uint16_t humidity_pct;  // 6020 = 60.20 %
    uint16_t vbat_mv;       // 3280 = 3.280 В
} telemetry_sample_t;

// Кадр у тому вигляді, в якому він летить у радіоканал.
// #pragma pack прибирає вирівнювальні проміжки: без нього між magic і
// timestamp_s компілятор непомітно вставить три байти сміття, і CRC на
// приймачі не зійдеться (у приймача сміття буде інше).
#pragma pack(push, 1)
typedef struct {
    uint8_t  magic;       // FRAME_MAGIC
    uint8_t  msg_type;    // FRAME_TYPE_TELEM
    uint16_t seq_num;     // лічильник кадрів — ловить утрати, дублі й повтори
    uint32_t timestamp_s;
    int16_t  temp_c;
    uint16_t hum_pct;
    uint16_t vbat_mv;
    uint16_t crc16;       // CRC-16-CCITT по всіх попередніх 14 байтах
} custom_frame_t;
#pragma pack(pop)

#define CUSTOM_FRAME_SIZE    16u
#define CUSTOM_FRAME_CRC_LEN (CUSTOM_FRAME_SIZE - sizeof(uint16_t))

// Розмір кадру — частина специфікації протоколу, а не наслідок налаштувань
// компілятора. Якщо #pragma pack не спрацювала (чужий компілятор, забутий
// pop), збірка мусить упасти тут, а не мовчки видати 20-байтові кадри в ефір.
typedef char custom_frame_is_16_bytes[(sizeof(custom_frame_t) == CUSTOM_FRAME_SIZE) ? 1 : -1];

// Порядок байтів у кадрі зафіксовано little-endian — саме так лягає структура
// на Cortex-M, ESP32 та RISC-V, і саме так її читає сервер. Прямий memcpy
// структури працює лише за цієї умови, тож перевіряємо її на етапі збірки.
#if defined(__BYTE_ORDER__) && (__BYTE_ORDER__ != __ORDER_LITTLE_ENDIAN__)
#error "Кадр зафіксовано little-endian; на big-endian платформі поля треба писати побайтово"
#endif

// CRC-16-CCITT (поліном 0x1021, початкове значення 0xFFFF, без відображення).
uint16_t crc16_ccitt(const uint8_t *data, size_t len);

// Три способи пакування. Усі повертають довжину готового буфера
// або 0, якщо зібрати кадр не вдалося (мало місця, кривий аргумент).

// HTTP/1.1 POST із JSON-тілом, заголовком Bearer і Content-Length.
size_t build_http_post_request(const telemetry_sample_t *s,
                               const char *host,
                               const char *token,
                               char *out_buf,
                               size_t max_len);

// MQTT 3.1.1 PUBLISH, QoS 1: фіксований заголовок, Remaining Length зі
// змінним кодуванням, тема, Packet Identifier, JSON-payload.
size_t build_mqtt_publish_qos1(const telemetry_sample_t *s,
                               const char *topic,
                               uint16_t packet_id,
                               uint8_t *out_buf,
                               size_t max_len);

// Власний бінарний кадр: 16 байтів, з них 10 корисних.
size_t build_custom_binary_frame(const telemetry_sample_t *s,
                                 uint16_t seq,
                                 uint8_t *out_buf,
                                 size_t max_len);

#endif // TELEMETRY_H

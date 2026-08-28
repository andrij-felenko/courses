#include <stdint.h>
#include <stdbool.h>
#include <string.h>   // memcpy

// ── Каркас UBX ────────────────────────────────────────────────────────────
#define UBX_SYNC1   0xB5      // перший сигнатурний байт
#define UBX_SYNC2   0x62      // другий сигнатурний байт

// Класи повідомлень
#define UBX_CLS_NAV  0x01     // навігаційні рішення
#define UBX_CLS_ACK  0x05     // підтвердження
#define UBX_CLS_CFG  0x06     // конфігурація
#define UBX_CLS_MON  0x0A     // моніторинг (версія тощо)

// ID у своїх класах
#define UBX_NAV_PVT     0x07  // Position-Velocity-Time
#define UBX_ACK_ACK     0x01  // команду прийнято
#define UBX_ACK_NAK     0x00  // команду відкинуто
#define UBX_MON_VER     0x04  // версія прошивки/заліза
#define UBX_CFG_VALSET  0x8A  // задати конфіг (Gen9+: M9/M10)
#define UBX_CFG_PRT     0x00  // порт (легасі, M8)
#define UBX_CFG_MSG     0x01  // темп повідомлення (легасі)
#define UBX_CFG_RATE    0x08  // темп навігації (легасі)
#define UBX_CFG_GNSS    0x3E  // вибір сузір'їв (легасі)
#define UBX_CFG_CFG     0x09  // зберегти/завантажити конфіг (легасі)

// Зсуви ключових полів у payload NAV-PVT (payload = 92 байти).
// Саме ці зсуви — з офіційного інтерфейс-опису; переплутати = читати сміття.
#define PVT_iTOW      0   // u32, мс GPS-тижня
#define PVT_year      4   // u16 — ДВА байти, не один!
#define PVT_fixType  20   // u8  0=нема, 2=2D, 3=3D
#define PVT_flags    21   // u8  біт0 gnssFixOK, біти6-7 carrSoln
#define PVT_numSV    23   // u8  супутників у розв'язку
#define PVT_lon      24   // i32 × 1e-7 градуса
#define PVT_lat      28   // i32 × 1e-7 градуса
#define PVT_height   32   // i32 мм над еліпсоїдом
#define PVT_hMSL     36   // i32 мм над рівнем моря
#define PVT_hAcc     40   // u32 мм, оцінка горизонтальної похибки
#define PVT_gSpeed   60   // i32 мм/с, модуль горизонтальної швидкості
#define PVT_headMot  64   // i32 × 1e-5 градуса, курс руху
#define PVT_pDOP     76   // u16 × 0.01, геометричне розмивання

#define PVT_PAYLOAD_LEN  92
#define UBX_BUF_MAX     128   // стеля буфера payload — більше не буває в потрібних нам повідомленнях

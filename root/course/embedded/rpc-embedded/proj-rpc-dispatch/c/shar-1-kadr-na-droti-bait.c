#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define RPC_START   0x7Eu      // байт-початок кадру

// Кадр запиту на дроті. packed → жодних невидимих байтів-вирівнювачів,
// розкладка в памʼяті ТОЧНО збігається з порядком байтів на лінії.
typedef struct __attribute__((packed)) {
    uint8_t  id;               // номер запиту (повтори/звʼязка)
    uint8_t  func;             // номер функції — ІНДЕКС у таблицю
    int32_t  arg;              // аргумент (little-endian на дроті)
    uint16_t crc;             // CRC-16/CCITT над {id, func, arg}
} rpc_req_t;

// Кадр відповіді: той самий ID, код результату, повернуте значення.
typedef struct __attribute__((packed)) {
    uint8_t  id;               // ID запиту, на який це відповідь
    uint8_t  status;           // 0 = OK, інакше код помилки (нижче)
    int32_t  value;            // результат функції (значуще лише при OK)
    uint16_t crc;
} rpc_resp_t;

// Коди результату у відповіді.
enum {
    RPC_OK          = 0,       // виконано, value дійсне
    RPC_ERR_BADFUNC = 1,       // номер функції за межами таблиці
    RPC_ERR_BADCRC  = 2,       // (сервер не шле — клієнт сам відсіює)
    RPC_ERR_BUSY    = 3,       // обробник тимчасово не може виконати
};

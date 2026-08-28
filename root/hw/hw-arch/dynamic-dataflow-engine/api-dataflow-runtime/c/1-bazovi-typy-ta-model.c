#include <stdint.h>
#include <stdbool.h>

typedef uint32_t df_frame_id_t;  /* Унікальний числовий дескриптор кадру активації ETS */
typedef uint16_t df_node_id_t;   /* Індекс інструкції всередині статичного графа */
typedef uint8_t  df_port_t;      /* Номер цільового вхідного порту: 0 (лівий), 1 (правий) */

typedef struct {
    df_frame_id_t frame_id;      /* Базовий контекст кадру активації */
    df_node_id_t  node_id;       /* Адреса цільового оператора в Node Store */
    df_port_t     port;          /* Вхідний порт операнда */
    uint8_t       flags;         /* Прапорці керування (EOF, Ack, Trap) */
    uint64_t      value;         /* 64-бітне значення операнда (IEEE 754 або ціле) */
} df_token_t;

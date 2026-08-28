#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define MAVFTP_MAX_DATA_LEN 239
#define MAVFTP_HEADER_LEN   12
#define MAVFTP_PAYLOAD_LEN  251

/* Опкоди MAVFTP */
typedef enum {
    MAVFTP_OP_NONE              = 0,
    MAVFTP_OP_TERMINATE_SESSION = 1,
    MAVFTP_OP_RESET_SESSIONS    = 2,
    MAVFTP_OP_LIST_DIRECTORY    = 3,
    MAVFTP_OP_OPEN_FILE_RO      = 4,
    MAVFTP_OP_READ_FILE         = 5,
    MAVFTP_OP_CREATE_FILE       = 6,
    MAVFTP_OP_WRITE_FILE        = 7,
    MAVFTP_OP_REMOVE_FILE       = 8,
    MAVFTP_OP_CREATE_DIRECTORY  = 9,
    MAVFTP_OP_REMOVE_DIRECTORY  = 10,
    MAVFTP_OP_OPEN_FILE_WO      = 11,
    MAVFTP_OP_TRUNCATE_FILE     = 12,
    MAVFTP_OP_RENAME            = 13,
    MAVFTP_OP_CALC_FILE_CRC32   = 14,
    MAVFTP_OP_BURST_READ_FILE   = 15,
    MAVFTP_OP_ACK               = 128,
    MAVFTP_OP_NAK               = 129
} mavftp_op_t;

/* Коди помилок NAK */
typedef enum {
    MAVFTP_ERR_NONE             = 0,
    MAVFTP_ERR_FAIL             = 1,
    MAVFTP_ERR_FAIL_ERRNO       = 2,
    MAVFTP_ERR_INVALID_SIZE     = 3,
    MAVFTP_ERR_INVALID_SESSION  = 4,
    MAVFTP_ERR_NO_SESSIONS      = 5,
    MAVFTP_ERR_EOF              = 6,
    MAVFTP_ERR_UNKNOWN_CMD      = 7,
    MAVFTP_ERR_FILE_EXISTS      = 8,
    MAVFTP_ERR_FILE_PROTECTED   = 9,
    MAVFTP_ERR_FILE_NOT_FOUND   = 10
} mavftp_err_t;

#pragma pack(push, 1)
typedef struct {
    uint16_t seq_number;       /* Номер послідовності (LE) */
    uint8_t  session;          /* ID сесії */
    uint8_t  opcode;           /* Опкод операції / відповіді */
    uint8_t  size;             /* Кількість значущих байтів у data */
    uint8_t  req_opcode;       /* Опкод запиту для ACK/NAK */
    uint8_t  burst_complete;   /* 1 якщо останній пакет burst */
    uint8_t  padding;          /* Зарезервовано (0) */
    uint32_t offset;           /* Зсув у файлі (LE) */
    uint8_t  data[MAVFTP_MAX_DATA_LEN]; /* Тіло фрагмента */
} mavftp_pkt_t;
#pragma pack(pop)

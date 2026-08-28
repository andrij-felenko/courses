#include <stdint.h>
#include <string.h>

#define MAVFTP_MAX_DATA_LEN 239

/* Опкоди операцій MAVFTP */
typedef enum {
    MAVFTP_CMD_NONE              = 0,
    MAVFTP_CMD_TERMINATE_SESSION = 1,
    MAVFTP_CMD_RESET_SESSIONS    = 2,
    MAVFTP_CMD_LIST_DIRECTORY    = 3,
    MAVFTP_CMD_OPEN_FILE_RO      = 4,
    MAVFTP_CMD_READ_FILE         = 5,
    MAVFTP_CMD_CREATE_FILE       = 6,
    MAVFTP_CMD_WRITE_FILE        = 7,
    MAVFTP_CMD_REMOVE_FILE       = 8,
    MAVFTP_CMD_CREATE_DIRECTORY  = 9,
    MAVFTP_CMD_REMOVE_DIRECTORY  = 10,
    MAVFTP_CMD_OPEN_FILE_WO      = 11,
    MAVFTP_CMD_TRUNCATE_FILE     = 12,
    MAVFTP_CMD_RENAME            = 13,
    MAVFTP_CMD_CALC_FILE_CRC32   = 14,
    MAVFTP_CMD_BURST_READ_FILE   = 15,
    MAVFTP_RSP_ACK               = 128,
    MAVFTP_RSP_NAK               = 129
} mavftp_opcode_t;

/* Коди помилок NAK */
typedef enum {
    MAVFTP_ERR_NONE                 = 0,
    MAVFTP_ERR_FAIL                 = 1,
    MAVFTP_ERR_FAIL_ERRNO           = 2,
    MAVFTP_ERR_INVALID_DATA_SIZE    = 3,
    MAVFTP_ERR_INVALID_SESSION      = 4,
    MAVFTP_ERR_NO_SESSIONS_AVAIL    = 5,
    MAVFTP_ERR_EOF                  = 6,
    MAVFTP_ERR_UNKNOWN_COMMAND      = 7,
    MAVFTP_ERR_FILE_EXISTS          = 8,
    MAVFTP_ERR_FILE_PROTECTED       = 9,
    MAVFTP_ERR_FILE_NOT_FOUND       = 10
} mavftp_error_t;

/* Упакований заголовок PayloadHeader (12 байтів) та масив data (239 байтів) */
#pragma pack(push, 1)
typedef struct {
    uint16_t seq_number;       /* Номер пакета (little-endian) */
    uint8_t  session;          /* ID сесії */
    uint8_t  opcode;           /* Опкод (mavftp_opcode_t) */
    uint8_t  size;             /* Кількість байтів у data */
    uint8_t  req_opcode;       /* Опкод запиту для відповідей ACK/NAK */
    uint8_t  burst_complete;   /* 1 якщо фініш burst потоку */
    uint8_t  padding;          /* Резерв (0) */
    uint32_t offset;           /* Зсув у файлі (little-endian) */
    uint8_t  data[MAVFTP_MAX_DATA_LEN]; /* Дані операції */
} mavftp_payload_t;
#pragma pack(pop)

/* Допоміжна функція складання запиту OpenFileRO */
static inline void mavftp_init_open_ro(mavftp_payload_t *msg, uint16_t seq, const char *path) {
    memset(msg, 0, sizeof(*msg));
    msg->seq_number = seq;
    msg->opcode = MAVFTP_CMD_OPEN_FILE_RO;
    size_t path_len = strlen(path) + 1;
    if (path_len > MAVFTP_MAX_DATA_LEN) {
        path_len = MAVFTP_MAX_DATA_LEN;
    }
    msg->size = (uint8_t)path_len;
    memcpy(msg->data, path, path_len);
    msg->data[MAVFTP_MAX_DATA_LEN - 1] = '\0';
}

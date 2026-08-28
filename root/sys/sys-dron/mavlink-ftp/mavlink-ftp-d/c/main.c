#include <stdint.h>
#include <string.h>

#define MAVFTP_DATA_SIZE 239

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
    MAVFTP_CMD_BURST_READ_FILE   = 15,
    MAVFTP_RSP_ACK               = 128,
    MAVFTP_RSP_NAK               = 129
} mavftp_cmd_t;

/* Заголовок PayloadHeader (12 байтів) та масив даних (239 байтів) */
#pragma pack(push, 1)
typedef struct {
    uint16_t seq_number;       /* Номер пакета (little-endian) */
    uint8_t  session;          /* Номер сесії */
    uint8_t  opcode;           /* Код операції (mavftp_cmd_t) */
    uint8_t  size;             /* Кількість значущих байтів у data */
    uint8_t  req_opcode;       /* Опкод запиту для відповідей ACK/NAK */
    uint8_t  burst_complete;   /* 1 якщо останній пакет burst */
    uint8_t  padding;          /* Резервний байт (0) */
    uint32_t offset;           /* Зсув у файлі (little-endian) */
    uint8_t  data[MAVFTP_DATA_SIZE]; /* Буфер корисного навантаження */
} mavftp_payload_header_t;
#pragma pack(pop)

/* Складання запиту на відкриття файлу для читання */
void make_open_ro_request(mavftp_payload_header_t *hdr, uint16_t seq, const char *filepath) {
    memset(hdr, 0, sizeof(*hdr));
    hdr->seq_number = seq;
    hdr->opcode = MAVFTP_CMD_OPEN_FILE_RO;
    size_t len = strlen(filepath) + 1;
    if (len > MAVFTP_DATA_SIZE) len = MAVFTP_DATA_SIZE;
    hdr->size = (uint8_t)len;
    memcpy(hdr->data, filepath, len);
    hdr->data[MAVFTP_DATA_SIZE - 1] = '\0';
}

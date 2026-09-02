/* Бінарний дескриптор заголовка LUKS2 та читання копії метаданих з носія.
 *
 * Розкладка полів — дисковий формат LUKS2 (cryptsetup, lib/luks2/luks2.h).
 * Усі багатобайтові числа на диску лежать у Big-Endian.
 */
#ifndef LUKS2_HDR_H
#define LUKS2_HDR_H

#include <stddef.h>
#include <stdint.h>

#define LUKS2_MAGIC_1             "LUKS\xba\xbe"
#define LUKS2_MAGIC_2             "SKUL\xba\xbe"
#define LUKS2_MAGIC_SIZE          6
#define LUKS2_LABEL_SIZE          48
#define LUKS2_CHECKSUM_ALG_SIZE   32
#define LUKS2_SALT_SIZE           64
#define LUKS2_UUID_SIZE           44
#define LUKS2_SUBSYSTEM_SIZE      48
#define LUKS2_PADDING_SIZE        180
#define LUKS2_CHECKSUM_SIZE       64
#define LUKS2_HDR_PAD_SIZE        3584
#define LUKS2_HDR_TOTAL_SIZE      4096

/* Поле csum лежить за зсувом 448 і зануляється перед розрахунком суми. */
#define LUKS2_CSUM_OFFSET         448
/* Службова зона однієї копії: від 16 КіБ до 4 МіБ, завжди степінь двійки. */
#define LUKS2_HDR_SIZE_MIN        16384ULL
#define LUKS2_HDR_SIZE_MAX        4194304ULL

#pragma pack(push, 1)
struct luks2_hdr_disk {
    char     magic[LUKS2_MAGIC_SIZE];             /* 0x0000: "LUKS\xba\xbe" або "SKUL\xba\xbe" */
    uint16_t version;                             /* 0x0006: 0x0002 (Big-Endian) */
    uint64_t hdr_size;                            /* 0x0008: розмір заголовка разом із JSON */
    uint64_t seqid;                               /* 0x0010: монотонний лічильник транзакцій */
    char     label[LUKS2_LABEL_SIZE];             /* 0x0018: текстова мітка тома */
    char     csum_alg[LUKS2_CHECKSUM_ALG_SIZE];   /* 0x0048: алгоритм контрольної суми */
    uint8_t  salt[LUKS2_SALT_SIZE];               /* 0x0068: сіль контрольної суми */
    char     uuid[LUKS2_UUID_SIZE];               /* 0x00A8: UUID тома */
    char     subsystem[LUKS2_SUBSYSTEM_SIZE];     /* 0x00D4: підсистема-власник */
    uint64_t hdr_offset;                          /* 0x0104: очікуваний зсув цієї копії */
    uint8_t  _padding[LUKS2_PADDING_SIZE];        /* 0x010C: резерв, нулі */
    uint8_t  csum[LUKS2_CHECKSUM_SIZE];           /* 0x01C0: контрольна сума блоку метаданих */
    uint8_t  _pad_to_4k[LUKS2_HDR_PAD_SIZE];      /* 0x0200: доповнення до 4096 байтів */
};
#pragma pack(pop)

_Static_assert(sizeof(struct luks2_hdr_disk) == LUKS2_HDR_TOTAL_SIZE,
               "дескриптор LUKS2 мусить займати рівно 4096 байтів");

enum luks2_rc {
    LUKS2_OK = 0,
    LUKS2_E_IO,          /* носій не дочитався */
    LUKS2_E_MEM,
    LUKS2_E_MAGIC,       /* тут узагалі не LUKS2 */
    LUKS2_E_WRITING,     /* "SKUL" — обірвана транзакція запису */
    LUKS2_E_VERSION,
    LUKS2_E_HDR_SIZE,
    LUKS2_E_HDR_OFFSET,  /* копію зсунули (типово — dd з неправильним skip) */
    LUKS2_E_CSUM_ALG,
    LUKS2_E_CSUM,
    LUKS2_E_JSON_TERM,   /* після документа немає нульового байта */
    LUKS2_E_JSON_PAD     /* хвіст після документа не занулено */
};

/* Прочитана й перевірена копія метаданих. Володіє буфером area. */
struct luks2_hdr {
    uint64_t       at_offset;   /* зсув, з якого копію прочитано */
    uint64_t       hdr_size;
    uint64_t       seqid;
    uint64_t       hdr_offset;  /* значення поля з диска */
    char           label[LUKS2_LABEL_SIZE + 1];
    char           csum_alg[LUKS2_CHECKSUM_ALG_SIZE + 1];
    char           uuid[LUKS2_UUID_SIZE + 1];
    char           subsystem[LUKS2_SUBSYSTEM_SIZE + 1];
    unsigned char *area;        /* увесь блок hdr_size байтів */
    const char    *json;        /* area + 4096 */
    size_t         json_len;    /* довжина тексту до першого 0x00 */
    size_t         json_size;   /* hdr_size - 4096 */
};

/* Стандартні зсуви копії заголовка — ними шукають вторинну, коли первинну вбито. */
extern const uint64_t luks2_hdr_offsets[];
extern const size_t   luks2_hdr_offsets_count;

int  luks2_hdr_read(int fd, uint64_t offset, struct luks2_hdr *out);
void luks2_hdr_free(struct luks2_hdr *hdr);
const char *luks2_strerror(int rc);

#endif /* LUKS2_HDR_H */

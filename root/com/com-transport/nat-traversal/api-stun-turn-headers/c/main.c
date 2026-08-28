#include <stdint.h>

/* Базовий 20-байтовий заголовок STUN / TURN */
#pragma pack(push, 1)
typedef struct {
    uint16_t msg_type;       /* 2 біти 00 + 2 біти Class + 12 бітів Method */
    uint16_t msg_length;     /* Довжина атрибутів у байтах (без 20 байтів заголовка) */
    uint32_t magic_cookie;   /* Фіксована константа 0x2112A442 */
    uint8_t  transaction_id[12]; /* 96-бітний ідентифікатор транзакції */
} StunHeader;

/* Заголовок атрибута TLV */
typedef struct {
    uint16_t type;           /* Тип атрибута (наприклад, 0x0020 для XOR-MAPPED-ADDRESS) */
    uint16_t length;         /* Довжина корисного навантаження атрибута в байтах */
} StunAttributeHeader;

/* Атрибут XOR-MAPPED-ADDRESS для IPv4 */
typedef struct {
    uint8_t  reserved;       /* Завжди 0x00 */
    uint8_t  family;         /* 0x01 для IPv4, 0x02 для IPv6 */
    uint16_t x_port;         /* Порт ^ 0x2112 */
    uint32_t x_address_ipv4; /* IPv4 ^ 0x2112A442 */
} StunXorMappedAddressIpv4;

/* Атрибут XOR-MAPPED-ADDRESS для IPv6 */
typedef struct {
    uint8_t  reserved;       /* Завжди 0x00 */
    uint8_t  family;         /* 0x02 для IPv6 */
    uint16_t x_port;         /* Порт ^ 0x2112 */
    uint8_t  x_address_ipv6[16]; /* IPv6 ^ (MagicCookie || TransactionID) */
} StunXorMappedAddressIpv6;

/* Заголовок фрейму ChannelData TURN (4 байти) */
typedef struct {
    uint16_t channel_number; /* 0x4000 .. 0x7FFE */
    uint16_t length;         /* Довжина навантаження в байтах */
} TurnChannelDataHeader;
#pragma pack(pop)

#include <stdint.h>
#include <string.h>

typedef struct {
    uint8_t bytes[16];
} rfc_uuid_t;

typedef struct {
    uint32_t Data1;
    uint16_t Data2;
    uint16_t Data3;
    uint8_t  Data4[8];
} win_guid_t;

/* Безпечна конвертація Windows GUID -> RFC 4122 Big-Endian байтовий масив */
void win_guid_to_rfc_uuid(const win_guid_t *src, rfc_uuid_t *dst) {
    /* Розпакування 32-бітного Data1 у 4 байти Big-Endian */
    dst->bytes[0] = (uint8_t)(src->Data1 >> 24);
    dst->bytes[1] = (uint8_t)(src->Data1 >> 16);
    dst->bytes[2] = (uint8_t)(src->Data1 >> 8);
    dst->bytes[3] = (uint8_t)(src->Data1);

    /* Розпакування 16-бітного Data2 у 2 байти Big-Endian */
    dst->bytes[4] = (uint8_t)(src->Data2 >> 8);
    dst->bytes[5] = (uint8_t)(src->Data2);

    /* Розпакування 16-бітного Data3 у 2 байти Big-Endian */
    dst->bytes[6] = (uint8_t)(src->Data3 >> 8);
    dst->bytes[7] = (uint8_t)(src->Data3);

    /* Поле Data4 копіюється як є (побайтний масив) */
    memcpy(&dst->bytes[8], src->Data4, 8);
}

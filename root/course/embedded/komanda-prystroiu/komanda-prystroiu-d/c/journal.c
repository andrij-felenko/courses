#include "journal.h"
#include "platform.h"
#include "cmd_proto.h"

#include <string.h>

/* Розкладка запису у FRAM:
 *   0  4  magic "JRN1"
 *   4  8  token
 *  12  1  type
 *  13  1  open (1 — транзакція відкрита)
 *  14  4  crc32 по байтах 0..13
 * Контрольна сума потрібна тому, що запис може обірватися на середині:
 * недописаний запис не має видаватися за дійсний. */

#define JRN_MAGIC 0x4A524E31u   /* "JRN1" */
#define JRN_LEN   18u

static void put_u32(uint8_t *p, uint32_t v) {
    p[0] = (uint8_t)(v); p[1] = (uint8_t)(v >> 8);
    p[2] = (uint8_t)(v >> 16); p[3] = (uint8_t)(v >> 24);
}

static uint32_t get_u32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
           ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

static void write_record(uint64_t token, uint8_t type, uint8_t open) {
    uint8_t nvm[PLAT_NVM_SIZE];
    memset(nvm, 0, sizeof(nvm));

    put_u32(nvm, JRN_MAGIC);
    put_u32(nvm + 4, (uint32_t)(token & 0xFFFFFFFFu));
    put_u32(nvm + 8, (uint32_t)(token >> 32));
    nvm[12] = type;
    nvm[13] = open;
    put_u32(nvm + 14, wire_crc32(nvm, 14));

    plat_nvm_write(nvm);
}

void journal_begin(uint64_t token, uint8_t type) {
    write_record(token, type, 1u);
}

void journal_commit(void) {
    write_record(0, 0, 0u);
}

bool journal_open_entry(uint64_t *token, uint8_t *type) {
    uint8_t nvm[PLAT_NVM_SIZE];
    plat_nvm_read(nvm);

    if (get_u32(nvm) != JRN_MAGIC)                 return false;
    if (wire_crc32(nvm, 14) != get_u32(nvm + 14))  return false;   /* обірваний запис */
    if (nvm[13] != 1u)                             return false;

    *token = (uint64_t)get_u32(nvm + 4) | ((uint64_t)get_u32(nvm + 8) << 32);
    *type  = nvm[12];
    return true;
}

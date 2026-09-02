#include "fs_storage.h"

#include <string.h>

uint32_t fs_crc32(const uint8_t *data, uint32_t len)
{
    uint32_t crc = 0xFFFFFFFFu;

    for (uint32_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (int b = 0; b < 8; ++b)
            crc = (crc >> 1) ^ (0xEDB88320u & (uint32_t)(-(int32_t)(crc & 1u)));
    }
    return crc ^ 0xFFFFFFFFu;
}

static void put_u16(uint8_t *p, uint16_t v) { p[0] = (uint8_t)v; p[1] = (uint8_t)(v >> 8); }
static void put_u32(uint8_t *p, uint32_t v)
{
    p[0] = (uint8_t)v;         p[1] = (uint8_t)(v >> 8);
    p[2] = (uint8_t)(v >> 16); p[3] = (uint8_t)(v >> 24);
}
static uint16_t get_u16(const uint8_t *p) { return (uint16_t)(p[0] | (p[1] << 8)); }
static uint32_t get_u32(const uint8_t *p)
{
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
           ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

static void put_f32(uint8_t *p, float f)
{
    uint32_t bits;
    memcpy(&bits, &f, sizeof bits);
    put_u32(p, bits);
}

static float get_f32(const uint8_t *p)
{
    uint32_t bits = get_u32(p);
    float f;
    memcpy(&f, &bits, sizeof f);
    return f;
}

/* NOR-пам'ять уміє лише гасити одиниці, тому запис поверх незстертого
 * сектора дав би побітове І — драйвер зобов'язаний це відсіювати. */
static void flash_erase(fs_flash_sector_t *sec)
{
    memset(sec->data, 0xFF, FS_SECTOR_SIZE);
}

static bool flash_program(fs_flash_sector_t *sec, const uint8_t *src, uint32_t len)
{
    if (len > FS_SECTOR_SIZE)
        return false;
    for (uint32_t i = 0; i < len; ++i)
        if (sec->data[i] != 0xFF)
            return false;
    memcpy(sec->data, src, len);
    return memcmp(sec->data, src, len) == 0;  /* верифікація зчитуванням */
}

void fs_store_init(fs_param_store_t *st)
{
    flash_erase(&st->bank[0]);
    flash_erase(&st->bank[1]);
    st->active = 0;
    st->last_seq = 0;
}

static uint32_t encode(const fs_param_block_t *b, uint8_t *buf)
{
    uint32_t off;

    put_u32(buf, FS_PARAM_MAGIC);
    put_u16(buf + 4, (uint16_t)FS_SCHEMA_VERSION);
    put_u16(buf + 6, (uint16_t)FS_PARAM_COUNT);
    /* seq заповнює викликач: він знає номер транзакції */
    off = FS_HDR_SIZE;
    for (int i = 0; i < FS_PARAM_COUNT; ++i, off += 4)
        put_f32(buf + off, fs_params_get(b, (fs_param_id_t)i));
    return off;
}

fs_store_status_t fs_store_decode(const fs_flash_sector_t *sec, fs_param_block_t *out,
                                  uint32_t *seq_out, int *migrated_out)
{
    uint32_t count, payload, stored_crc, real_crc, schema;
    int migrated = 0;

    if (migrated_out != NULL)
        *migrated_out = 0;

    /* Стертий сектор — не пошкодження, а чиста плата. */
    if (get_u32(sec->data) == 0xFFFFFFFFu)
        return FS_STORE_ERR_ERASED;
    if (get_u32(sec->data) != FS_PARAM_MAGIC)
        return FS_STORE_ERR_MAGIC;

    schema = get_u16(sec->data + 4);
    count  = get_u16(sec->data + 6);
    if (schema > FS_SCHEMA_VERSION || count > FS_PARAM_COUNT)
        return FS_STORE_ERR_VERSION;

    payload = FS_HDR_SIZE + count * 4u;
    if (payload + 4u > FS_SECTOR_SIZE)
        return FS_STORE_ERR_VERSION;

    stored_crc = get_u32(sec->data + payload);
    real_crc   = fs_crc32(sec->data, payload);
    if (stored_crc != real_crc)
        return FS_STORE_ERR_CRC;

    /* Міграція схеми: параметри, доданих у нових версіях, у секторі просто немає —
     * добираємо їх із заводських значень, старі калібрування лишаються цілими. */
    fs_params_load_defaults(out);
    for (uint32_t i = 0; i < count; ++i) {
        float v = get_f32(sec->data + FS_HDR_SIZE + i * 4u);
        if (fs_params_set(out, (fs_param_id_t)i, v) != FS_PARAM_OK) {
            /* Значення зі старої прошивки не лізе в новий діапазон — беремо дефолт. */
            fs_params_set(out, (fs_param_id_t)i, fs_param_desc[i].def);
            migrated = 1;
        }
    }
    if (count < FS_PARAM_COUNT || schema < FS_SCHEMA_VERSION)
        migrated = 1;

    if (seq_out != NULL)
        *seq_out = get_u32(sec->data + 8);
    if (migrated_out != NULL)
        *migrated_out = migrated;
    return FS_STORE_OK;
}

fs_store_status_t fs_store_load(fs_param_store_t *st, fs_param_block_t *out, int *bank_out)
{
    fs_param_block_t cand[2];
    uint32_t seq[2] = { 0, 0 };
    fs_store_status_t rc[2];
    int ok0, ok1, pick;

    rc[0] = fs_store_decode(&st->bank[0], &cand[0], &seq[0], NULL);
    rc[1] = fs_store_decode(&st->bank[1], &cand[1], &seq[1], NULL);
    ok0 = (rc[0] == FS_STORE_OK);
    ok1 = (rc[1] == FS_STORE_OK);

    if (!ok0 && !ok1) {
        /* Обидві копії загинули: злітати не даємо, але параметри мусять бути валідні. */
        fs_params_load_defaults(out);
        st->active = 0;
        st->last_seq = 0;
        if (bank_out != NULL)
            *bank_out = -1;
        return (rc[0] == FS_STORE_ERR_ERASED && rc[1] == FS_STORE_ERR_ERASED)
                   ? FS_STORE_ERR_ERASED
                   : FS_STORE_ERR_NO_BANK;
    }

    if (ok0 && ok1)
        pick = ((int32_t)(seq[0] - seq[1]) >= 0) ? 0 : 1;  /* стійко до переповнення */
    else
        pick = ok0 ? 0 : 1;

    *out = cand[pick];
    st->active = pick;
    st->last_seq = seq[pick];
    if (bank_out != NULL)
        *bank_out = pick;
    return FS_STORE_OK;
}

fs_store_status_t fs_store_save(fs_param_store_t *st, const fs_param_block_t *b)
{
    uint8_t buf[FS_SECTOR_SIZE];
    fs_param_block_t check;
    uint32_t len, seq;
    int target = 1 - st->active;

    memset(buf, 0xFF, sizeof buf);
    len = encode(b, buf);
    seq = st->last_seq + 1u;
    put_u32(buf + 8, seq);
    put_u32(buf + len, fs_crc32(buf, len));
    len += 4u;

    /* Транзакція: пишемо в резервний банк, і лише вдале перечитування
     * робить його активним. Зникло живлення посеред запису — активним
     * лишається старий банк із меншим seq. */
    flash_erase(&st->bank[target]);
    if (!flash_program(&st->bank[target], buf, len))
        return FS_STORE_ERR_FLASH;
    if (fs_store_decode(&st->bank[target], &check, NULL, NULL) != FS_STORE_OK)
        return FS_STORE_ERR_FLASH;

    st->active = target;
    st->last_seq = seq;
    return FS_STORE_OK;
}

void fs_store_flip_bit(fs_param_store_t *st, int bank, uint32_t byte_off, int bit)
{
    if (bank < 0 || bank > 1 || byte_off >= FS_SECTOR_SIZE)
        return;
    st->bank[bank].data[byte_off] ^= (uint8_t)(1u << (bit & 7));
}

const char *fs_store_status_str(fs_store_status_t s)
{
    switch (s) {
    case FS_STORE_OK:          return "OK";
    case FS_STORE_ERR_ERASED:  return "ERASED";
    case FS_STORE_ERR_MAGIC:   return "BAD_MAGIC";
    case FS_STORE_ERR_CRC:     return "BAD_CRC";
    case FS_STORE_ERR_VERSION: return "FUTURE_SCHEMA";
    case FS_STORE_ERR_FLASH:   return "FLASH_FAILURE";
    case FS_STORE_ERR_NO_BANK: return "NO_VALID_BANK";
    default:                   return "?";
    }
}

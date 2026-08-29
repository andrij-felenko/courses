#include "build_meta.h"
#include "crc32.h"

/* Усі три значення приходять із Makefile через -D. Якщо котрогось немає,
   образ вийшов би невідстежуваним — краще не зібратися взагалі. */
#ifndef SOURCE_DATE_EPOCH
#error "SOURCE_DATE_EPOCH не заданий: збірка не була б відтворюваною"
#endif
#ifndef FW_GIT_COMMIT
#error "FW_GIT_COMMIT не заданий: образ неможливо звести до коміту"
#endif
#ifndef FW_TOOLCHAIN_ID
#error "FW_TOOLCHAIN_ID не заданий: невідомо, чим це скомпільовано"
#endif

/* sizeof рядкового літерала враховує нульовий байт, тож 41 — це рівно
   40 hex-символів повного SHA-1. Скорочений хеш сюди не пролізе. */
_Static_assert(sizeof(FW_GIT_COMMIT) == 41,
               "FW_GIT_COMMIT має бути повним SHA-1 із 40 символів");
_Static_assert(sizeof(FW_TOOLCHAIN_ID) <= 33,
               "FW_TOOLCHAIN_ID не влазить у поле toolchain_id");
_Static_assert(sizeof(fw_meta_t) == FW_META_SIZE,
               "розкладка fw_meta_t розійшлася зі stamp_meta.py");

/* used — щоб --gc-sections не викинув структуру, на яку ніхто не посилається
   з коду: її читає зовнішній інструмент, а не прошивка. */
__attribute__((section(".meta"), used))
const fw_meta_t fw_meta = {
    .magic        = FW_META_MAGIC,
    .version      = (uint16_t)FW_META_VERSION,
    .size         = (uint16_t)sizeof(fw_meta_t),
    .build_epoch  = (uint32_t)(SOURCE_DATE_EPOCH),
    .image_size   = 0U,   /* обидва проставить stamp_meta.py: до компонування */
    .image_crc32  = 0U,   /* ні розміру, ні контрольної суми ще не існує */
    .git_commit   = FW_GIT_COMMIT,
    .toolchain_id = FW_TOOLCHAIN_ID
};

/* Початок секції .meta, який розставив компонувальник */
extern const uint8_t __meta_start[];

const fw_meta_t *fw_meta_current(void)
{
    return (const fw_meta_t *)(const void *)__meta_start;
}

fw_meta_status_t fw_meta_verify(const fw_meta_t *meta,
                                const uint8_t *image,
                                uint32_t image_len)
{
    if (meta == NULL || image == NULL) {
        return FW_META_ERR_ARG;
    }
    if (meta->magic != FW_META_MAGIC) {
        return FW_META_ERR_MAGIC;
    }
    if (meta->version != (uint16_t)FW_META_VERSION) {
        return FW_META_ERR_VERSION;
    }
    if (meta->size != (uint16_t)sizeof(fw_meta_t)) {
        return FW_META_ERR_SIZE;
    }
    if (meta->image_size == 0U) {
        return FW_META_ERR_UNSTAMPED;
    }
    if (meta->image_size > image_len) {
        return FW_META_ERR_RANGE;
    }

    /* Метадані мусять лежати всередині того самого образу — інакше зсув
       поля CRC порахувати нема від чого. */
    const uint8_t *self = (const uint8_t *)meta;
    if (self < image || (self + sizeof(*meta)) > (image + meta->image_size)) {
        return FW_META_ERR_RANGE;
    }

    const uint32_t crc_off =
        (uint32_t)(self - image) + (uint32_t)offsetof(fw_meta_t, image_crc32);
    const uint32_t tail = crc_off + 4U;
    if (tail > meta->image_size) {
        return FW_META_ERR_RANGE;
    }

    /* Рахуємо так само, як штампувальник: поле CRC на час підрахунку
       вважається нульовим, решта образу — як є. */
    static const uint8_t zeros[4] = { 0U, 0U, 0U, 0U };
    uint32_t crc = crc32_update(CRC32_INIT, image, crc_off);
    crc = crc32_update(crc, zeros, sizeof zeros);
    crc = crc32_update(crc, image + tail, meta->image_size - tail);
    crc = crc32_final(crc);

    return (crc == meta->image_crc32) ? FW_META_OK : FW_META_ERR_CRC;
}

const char *fw_meta_status_text(fw_meta_status_t status)
{
    switch (status) {
    case FW_META_OK:             return "ok";
    case FW_META_ERR_ARG:        return "bad-arg";
    case FW_META_ERR_MAGIC:      return "bad-magic";
    case FW_META_ERR_VERSION:    return "bad-version";
    case FW_META_ERR_SIZE:       return "bad-size";
    case FW_META_ERR_UNSTAMPED:  return "unstamped";
    case FW_META_ERR_RANGE:      return "bad-range";
    case FW_META_ERR_CRC:        return "bad-crc";
    default:                     return "unknown";
    }
}

/* Далі — дрібна ручна робота замість snprintf: прошивка зібрана
   з -nostdlib, і тягти сюди stdio заради одного рядка нема сенсу. */

static size_t append_raw(char *buf, size_t cap, size_t pos,
                         const char *src, size_t len)
{
    for (size_t i = 0U; i < len && pos < cap; ++i) {
        buf[pos++] = src[i];
    }
    return pos;
}

static size_t append_str(char *buf, size_t cap, size_t pos, const char *src)
{
    while (*src != '\0' && pos < cap) {
        buf[pos++] = *src++;
    }
    return pos;
}

static size_t append_u32(char *buf, size_t cap, size_t pos, uint32_t value)
{
    char digits[10];
    size_t n = 0U;
    do {
        digits[n++] = (char)('0' + (value % 10U));
        value /= 10U;
    } while (value != 0U);

    while (n > 0U && pos < cap) {
        buf[pos++] = digits[--n];
    }
    return pos;
}

static size_t append_hex32(char *buf, size_t cap, size_t pos, uint32_t value)
{
    static const char hex[] = "0123456789abcdef";
    for (int shift = 28; shift >= 0 && pos < cap; shift -= 4) {
        buf[pos++] = hex[(value >> shift) & 0x0FU];
    }
    return pos;
}

size_t fw_meta_report(char *buf, size_t cap, const fw_meta_t *meta)
{
    if (buf == NULL || cap == 0U) {
        return 0U;
    }
    if (meta == NULL) {
        buf[0] = '\0';
        return 0U;
    }

    /* Один байт лишаємо під нульовий термінатор */
    const size_t limit = cap - 1U;
    size_t pos = 0U;

    pos = append_str(buf, limit, pos, "git=");
    pos = append_raw(buf, limit, pos, meta->git_commit, sizeof meta->git_commit);

    pos = append_str(buf, limit, pos, " tc=");
    /* toolchain_id коротший за поле й добитий нулями — беремо до першого */
    size_t tc_len = 0U;
    while (tc_len < sizeof meta->toolchain_id && meta->toolchain_id[tc_len] != '\0') {
        ++tc_len;
    }
    pos = append_raw(buf, limit, pos, meta->toolchain_id, tc_len);

    pos = append_str(buf, limit, pos, " epoch=");
    pos = append_u32(buf, limit, pos, meta->build_epoch);

    pos = append_str(buf, limit, pos, " size=");
    pos = append_u32(buf, limit, pos, meta->image_size);

    pos = append_str(buf, limit, pos, " crc=0x");
    pos = append_hex32(buf, limit, pos, meta->image_crc32);

    buf[pos] = '\0';
    return pos;
}

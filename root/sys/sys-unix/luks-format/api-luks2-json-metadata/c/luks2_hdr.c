#define _GNU_SOURCE
#include "luks2_hdr.h"

#include <endian.h>
#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include <openssl/evp.h>

const uint64_t luks2_hdr_offsets[] = {
    16384, 32768, 65536, 131072, 262144, 524288, 1048576, 2097152, 4194304
};
const size_t luks2_hdr_offsets_count =
    sizeof(luks2_hdr_offsets) / sizeof(luks2_hdr_offsets[0]);

const char *luks2_strerror(int rc)
{
    switch (rc) {
    case LUKS2_OK:            return "гаразд";
    case LUKS2_E_IO:          return "помилка читання носія";
    case LUKS2_E_MEM:         return "бракує пам'яті";
    case LUKS2_E_MAGIC:       return "немає сигнатури LUKS2";
    case LUKS2_E_WRITING:     return "сигнатура SKUL — запис копії було обірвано";
    case LUKS2_E_VERSION:     return "версія формату не 2";
    case LUKS2_E_HDR_SIZE:    return "неприпустимий hdr_size";
    case LUKS2_E_HDR_OFFSET:  return "hdr_offset не збігається з фактичним зсувом";
    case LUKS2_E_CSUM_ALG:    return "невідомий алгоритм контрольної суми";
    case LUKS2_E_CSUM:        return "контрольна сума не збіглася";
    case LUKS2_E_JSON_TERM:   return "область JSON не має нульового термінатора";
    case LUKS2_E_JSON_PAD:    return "хвіст після документа JSON не занулено";
    default:                  return "невідома помилка";
    }
}

/* Носій має право віддати менше, ніж просили, — дочитуємо в циклі. */
static int read_exact(int fd, void *buf, size_t len, uint64_t offset)
{
    unsigned char *p = buf;

    while (len > 0) {
        ssize_t n = pread(fd, p, len, (off_t)offset);
        if (n < 0) {
            if (errno == EINTR)
                continue;
            return LUKS2_E_IO;
        }
        if (n == 0)
            return LUKS2_E_IO;      /* пристрій коротший за заявлений hdr_size */
        p += (size_t)n;
        len -= (size_t)n;
        offset += (uint64_t)n;
    }
    return LUKS2_OK;
}

/* Поля-рядки на диску не зобов'язані мати термінатор — доводимо до C-рядка самі. */
static void copy_field(char *dst, const char *src, size_t n)
{
    memcpy(dst, src, n);
    dst[n] = '\0';
}

/* Сума рахується над усім блоком hdr_size із тимчасово зануленим полем csum.
   Буфер наш, тож зануляємо просто на місці й повертаємо байти назад. */
static int verify_csum(unsigned char *area, size_t area_len, const char *alg)
{
    unsigned char stored[LUKS2_CHECKSUM_SIZE];
    unsigned char calc[EVP_MAX_MD_SIZE];
    unsigned int calc_len = 0;
    EVP_MD_CTX *ctx = NULL;
    const EVP_MD *md;
    int md_len;
    int rc = LUKS2_E_CSUM;

    md = EVP_get_digestbyname(alg);
    if (md == NULL)
        return LUKS2_E_CSUM_ALG;    /* напр. "crc32" — його в EVP немає */

    md_len = EVP_MD_size(md);
    if (md_len <= 0 || (size_t)md_len > LUKS2_CHECKSUM_SIZE)
        return LUKS2_E_CSUM_ALG;

    memcpy(stored, area + LUKS2_CSUM_OFFSET, LUKS2_CHECKSUM_SIZE);
    memset(area + LUKS2_CSUM_OFFSET, 0, LUKS2_CHECKSUM_SIZE);

    ctx = EVP_MD_CTX_new();
    if (ctx == NULL) {
        rc = LUKS2_E_MEM;
        goto out;
    }
    if (EVP_DigestInit_ex(ctx, md, NULL) != 1 ||
        EVP_DigestUpdate(ctx, area, area_len) != 1 ||
        EVP_DigestFinal_ex(ctx, calc, &calc_len) != 1)
        goto out;

    /* На диску значущі лише md_len байтів поля, решта — нулі. */
    if (calc_len == (unsigned int)md_len && memcmp(stored, calc, calc_len) == 0)
        rc = LUKS2_OK;
out:
    EVP_MD_CTX_free(ctx);
    memcpy(area + LUKS2_CSUM_OFFSET, stored, LUKS2_CHECKSUM_SIZE);
    return rc;
}

/* Текст починається за зсувом 4096; після нього до кінця зони — самі нулі. */
static int check_json_area(struct luks2_hdr *h)
{
    const unsigned char *p = h->area + LUKS2_HDR_TOTAL_SIZE;
    size_t n = (size_t)(h->hdr_size - LUKS2_HDR_TOTAL_SIZE);
    const unsigned char *nul = memchr(p, 0x00, n);
    size_t len, i;

    if (nul == NULL)
        return LUKS2_E_JSON_TERM;

    len = (size_t)(nul - p);
    for (i = len; i < n; i++)
        if (p[i] != 0x00)
            return LUKS2_E_JSON_PAD;

    h->json = (const char *)p;
    h->json_len = len;
    h->json_size = n;
    return LUKS2_OK;
}

int luks2_hdr_read(int fd, uint64_t offset, struct luks2_hdr *out)
{
    struct luks2_hdr_disk d;
    struct luks2_hdr h;
    uint64_t hdr_size;
    int rc;

    memset(out, 0, sizeof(*out));
    memset(&h, 0, sizeof(h));

    rc = read_exact(fd, &d, sizeof(d), offset);
    if (rc != LUKS2_OK)
        return rc;

    /* 1. Сигнатура. "SKUL" означає перервану транзакцію, а не сміття. */
    if (memcmp(d.magic, LUKS2_MAGIC_2, LUKS2_MAGIC_SIZE) == 0)
        return LUKS2_E_WRITING;
    if (memcmp(d.magic, LUKS2_MAGIC_1, LUKS2_MAGIC_SIZE) != 0)
        return LUKS2_E_MAGIC;

    /* 2. Версія. */
    if (be16toh(d.version) != 2)
        return LUKS2_E_VERSION;

    /* 3. Розмір зони: степінь двійки в межах 16 КіБ … 4 МіБ. */
    hdr_size = be64toh(d.hdr_size);
    if (hdr_size < LUKS2_HDR_SIZE_MIN || hdr_size > LUKS2_HDR_SIZE_MAX ||
        (hdr_size & (hdr_size - 1)) != 0)
        return LUKS2_E_HDR_SIZE;

    /* 4. Копія знає власний зсув — так ловлять образ, скопійований не туди. */
    h.hdr_offset = be64toh(d.hdr_offset);
    if (h.hdr_offset != offset)
        return LUKS2_E_HDR_OFFSET;

    h.hdr_size = hdr_size;
    h.area = malloc((size_t)hdr_size);
    if (h.area == NULL)
        return LUKS2_E_MEM;

    rc = read_exact(fd, h.area, (size_t)hdr_size, offset);
    if (rc != LUKS2_OK)
        goto fail;

    /* 5. Контрольна сума всього блоку. */
    copy_field(h.csum_alg, d.csum_alg, LUKS2_CHECKSUM_ALG_SIZE);
    rc = verify_csum(h.area, (size_t)hdr_size, h.csum_alg);
    if (rc != LUKS2_OK)
        goto fail;

    /* 6. Межі текстової області. */
    rc = check_json_area(&h);
    if (rc != LUKS2_OK)
        goto fail;

    copy_field(h.label, d.label, LUKS2_LABEL_SIZE);
    copy_field(h.uuid, d.uuid, LUKS2_UUID_SIZE);
    copy_field(h.subsystem, d.subsystem, LUKS2_SUBSYSTEM_SIZE);
    h.at_offset = offset;
    h.seqid = be64toh(d.seqid);

    *out = h;
    return LUKS2_OK;
fail:
    free(h.area);
    return rc;
}

void luks2_hdr_free(struct luks2_hdr *hdr)
{
    if (hdr == NULL)
        return;
    free(hdr->area);
    memset(hdr, 0, sizeof(*hdr));
}
